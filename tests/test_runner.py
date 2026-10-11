
"""Tests for individual bulk runner check execution."""

import threading
import time
from unittest.mock import patch

import pytest

from jc_sre_netprobe.config import CheckConfig, RunnerConfig
from jc_sre_netprobe.dns import DNSCheckResult
from jc_sre_netprobe.http import HTTPCheckResult
from jc_sre_netprobe.network import NetworkInfo
from jc_sre_netprobe.runner import CheckResult, _execute_check, run_checks
from jc_sre_netprobe.tcp import TCPCheckResult
from jc_sre_netprobe.tls import TLSCheckResult


def test_execute_tcp_success() -> None:
    check = CheckConfig(
        name="tcp-test",
        type="tcp",
        host="127.0.0.1",
        port=443,
        timeout=3.0,
    )

    expected = TCPCheckResult(
        host="127.0.0.1",
        port=443,
        reachable=True,
        latency_ms=1.5,
    )

    with patch(
        "jc_sre_netprobe.runner.tcp_check",
        return_value=expected,
    ) as mock_probe:
        result = _execute_check(check)

    mock_probe.assert_called_once_with(
        "127.0.0.1",
        443,
        timeout=3.0,
    )
    assert result.healthy is True
    assert result.details["latency_ms"] == 1.5
    assert result.error is None


def test_execute_dns_failure() -> None:
    check = CheckConfig(
        name="dns-test",
        type="dns",
        host="invalid.example",
    )

    expected = DNSCheckResult(
        hostname="invalid.example",
        addresses=[],
        resolved=False,
        error="DNS resolution failed",
    )

    with patch(
        "jc_sre_netprobe.runner.dns_check",
        return_value=expected,
    ):
        result = _execute_check(check)

    assert result.healthy is False
    assert result.error == "DNS resolution failed"
    assert result.details["resolved"] is False


def test_execute_http_success() -> None:
    check = CheckConfig(
        name="http-test",
        type="http",
        url="https://example.com",
        timeout=5.0,
    )

    expected = HTTPCheckResult(
        url="https://example.com",
        status_code=200,
        healthy=True,
        latency_ms=10.0,
    )

    with patch(
        "jc_sre_netprobe.runner.http_check",
        return_value=expected,
    ) as mock_probe:
        result = _execute_check(check)

    mock_probe.assert_called_once_with(
        "https://example.com",
        timeout=5.0,
    )
    assert result.healthy is True
    assert result.details["status_code"] == 200


def test_execute_tls_success() -> None:
    check = CheckConfig(
        name="tls-test",
        type="tls",
        host="example.com",
        port=443,
        timeout=5.0,
    )

    expected = TLSCheckResult(
        host="example.com",
        port=443,
        valid=True,
        expires_at="2027-01-01T00:00:00+00:00",
        days_remaining=90,
        issuer="Example CA",
        subject="example.com",
    )

    with patch(
        "jc_sre_netprobe.runner.tls_check",
        return_value=expected,
    ) as mock_probe:
        result = _execute_check(check)

    mock_probe.assert_called_once_with(
        "example.com",
        port=443,
        timeout=5.0,
    )
    assert result.healthy is True
    assert result.details["valid"] is True


def test_execute_network_success() -> None:
    check = CheckConfig(
        name="network-test",
        type="network",
        cidr="192.168.1.0/24",
    )

    expected = NetworkInfo(
        network="192.168.1.0",
        prefix_length=24,
        netmask="255.255.255.0",
        broadcast="192.168.1.255",
        total_addresses=256,
        ip_version=4,
        is_private=True,
    )

    with patch(
        "jc_sre_netprobe.runner.network_info",
        return_value=expected,
    ):
        result = _execute_check(check)

    assert result.healthy is True
    assert result.details["total_addresses"] == 256
    assert result.error is None


def test_execute_check_isolates_exception() -> None:
    check = CheckConfig(
        name="tcp-error",
        type="tcp",
        host="localhost",
        port=443,
        timeout=3.0,
    )

    with patch(
        "jc_sre_netprobe.runner.tcp_check",
        side_effect=RuntimeError("Unexpected probe failure"),
    ):
        result = _execute_check(check)

    assert result.healthy is False
    assert result.details == {}
    assert result.error == "RuntimeError: Unexpected probe failure"


def test_execute_invalid_network() -> None:
    check = CheckConfig(
        name="invalid-network",
        type="network",
        cidr="invalid-cidr",
    )

    result = _execute_check(check)

    assert result.healthy is False
    assert result.error is not None
    assert "ValueError" in result.error


@pytest.mark.parametrize(
    "check",
    [
        CheckConfig(name="tcp", type="tcp"),
        CheckConfig(name="dns", type="dns"),
        CheckConfig(name="http", type="http"),
        CheckConfig(name="tls", type="tls"),
        CheckConfig(name="network", type="network"),
    ],
)
def test_execute_incomplete_config(check: CheckConfig) -> None:
    result = _execute_check(check)

    assert result.healthy is False
    assert result.error is not None
    assert "AssertionError" in result.error


def test_run_checks_aggregates_results() -> None:
    """Aggregate successful and failed checks correctly."""
    config = RunnerConfig(
        checks=(
            CheckConfig(name="first", type="network", cidr="10.0.0.0/8"),
            CheckConfig(name="second", type="network", cidr="invalid"),
            CheckConfig(name="third", type="network", cidr="192.168.1.0/24"),
        ),
        max_workers=2,
    )

    result = run_checks(config)

    assert result.total == 3
    assert result.healthy == 2
    assert result.failed == 1
    assert [item.name for item in result.results] == [
        "first",
        "second",
        "third",
    ]


def test_run_checks_preserves_order() -> None:
    """Preserve configuration order despite different completion times."""
    config = RunnerConfig(
        checks=tuple(
            CheckConfig(name=f"check-{i}", type="dns", host="example.com")
            for i in range(3)
        ),
        max_workers=3,
    )

    def fake_execute(check: CheckConfig) -> CheckResult:
        if check.name == "check-0":
            time.sleep(0.06)

        return CheckResult(
            name=check.name,
            type=check.type,
            healthy=True,
            details={},
        )

    with patch(
        "jc_sre_netprobe.runner._execute_check",
        side_effect=fake_execute,
    ):
        result = run_checks(config)

    assert [item.name for item in result.results] == [
        "check-0",
        "check-1",
        "check-2",
    ]


def test_run_checks_respects_max_workers() -> None:
    """Never execute more probes concurrently than max_workers."""
    config = RunnerConfig(
        checks=tuple(
            CheckConfig(name=f"check-{i}", type="dns", host="example.com")
            for i in range(6)
        ),
        max_workers=2,
    )

    lock = threading.Lock()
    active = 0
    peak = 0

    def fake_execute(check: CheckConfig) -> CheckResult:
        nonlocal active, peak

        with lock:
            active += 1
            peak = max(peak, active)

        try:
            time.sleep(0.03)
            return CheckResult(
                name=check.name,
                type=check.type,
                healthy=True,
                details={},
            )
        finally:
            with lock:
                active -= 1

    with patch(
        "jc_sre_netprobe.runner._execute_check",
        side_effect=fake_execute,
    ):
        result = run_checks(config)

    assert result.total == 6
    assert result.healthy == 6
    assert peak == 2


def test_run_checks_isolates_probe_failure() -> None:
    """A failing probe must not interrupt other checks."""
    config = RunnerConfig(
        checks=(
            CheckConfig(name="valid-1", type="network", cidr="10.0.0.0/8"),
            CheckConfig(name="invalid", type="network", cidr="invalid"),
            CheckConfig(name="valid-2", type="network", cidr="192.168.0.0/16"),
        ),
        max_workers=3,
    )

    result = run_checks(config)

    assert result.total == 3
    assert result.healthy == 2
    assert result.failed == 1
    assert result.results[1].healthy is False
    assert result.results[2].healthy is True


def test_run_checks_rejects_empty_checks() -> None:
    config = RunnerConfig(checks=())

    with pytest.raises(ValueError, match="at least one check"):
        run_checks(config)


@pytest.mark.parametrize("max_workers", [0, -1, True, 1.5, "2"])
def test_run_checks_rejects_invalid_workers(
    max_workers: object,
) -> None:
    config = RunnerConfig(
        checks=(
            CheckConfig(name="test", type="network", cidr="10.0.0.0/8"),
        ),
        max_workers=max_workers,  # type: ignore[arg-type]
    )

    with pytest.raises(ValueError, match="positive integer"):
        run_checks(config)

