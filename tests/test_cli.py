import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pytest import CaptureFixture

from jc_sre_netprobe import DNSCheckResult, HTTPCheckResult, NetworkInfo, TLSCheckResult
from jc_sre_netprobe.cli import main
from jc_sre_netprobe.tcp import TCPCheckResult


def test_cli_tcp_json(capsys: CaptureFixture[str]) -> None:
    expected = TCPCheckResult(
        host="example.com",
        port=443,
        reachable=True,
        latency_ms=10.5,
    )

    with (
        patch(
            "jc_sre_netprobe.cli.tcp_check",
            return_value=expected,
        ),
        patch.object(
            sys,
            "argv",
            [
                "jc-sre-netprobe",
                "--json",
                "tcp",
                "example.com",
                "443",
            ],
        ),
    ):
        main()

    captured = capsys.readouterr()
    output = json.loads(captured.out)

    assert output["host"] == "example.com"
    assert output["port"] == 443
    assert output["reachable"] is True
    assert output["latency_ms"] == 10.5
    assert output["error"] is None

@patch("jc_sre_netprobe.cli.tls_check")
def test_cli_tls_json(
    mock_tls_check: MagicMock,
    capsys: CaptureFixture[str],
) -> None:
    expected = TLSCheckResult(
        host="example.com",
        port=443,
        valid=True,
        expires_at="2030-12-31T23:59:59+00:00",
        days_remaining=100,
        issuer="commonName=Example CA",
        subject="commonName=example.com",
    )

    mock_tls_check.return_value = expected

    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "--json",
            "tls",
            "example.com",
        ],
    ):
        main()

    output = json.loads(capsys.readouterr().out)

    assert output["host"] == "example.com"
    assert output["port"] == 443
    assert output["valid"] is True
    assert output["expires_at"] == "2030-12-31T23:59:59+00:00"
    assert output["issuer"] == "commonName=Example CA"
    assert output["subject"] == "commonName=example.com"
    assert output["error"] is None

    mock_tls_check.assert_called_once_with(
        "example.com",
        443,
        timeout=5.0,
    )

@patch("jc_sre_netprobe.cli.tcp_check")
def test_cli_tcp_custom_timeout(
    mock_tcp_check: MagicMock,
) -> None:
    mock_tcp_check.return_value = TCPCheckResult(
        host="example.com",
        port=443,
        reachable=True,
        latency_ms=10.0,
    )

    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "tcp",
            "example.com",
            "443",
            "--timeout",
            "2.5",
        ],
    ):
        main()

    mock_tcp_check.assert_called_once_with(
        "example.com",
        443,
        timeout=2.5,
    )


@patch("jc_sre_netprobe.cli.http_check")
def test_cli_http_custom_timeout(
    mock_http_check: MagicMock,
) -> None:

    mock_http_check.return_value = HTTPCheckResult(
        url="https://example.com",
        status_code=200,
        healthy=True,
        latency_ms=10.0,
    )

    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "http",
            "https://example.com",
            "--timeout",
            "3.5",
        ],
    ):
        main()

    mock_http_check.assert_called_once_with(
        "https://example.com",
        timeout=3.5,
    )


@patch("jc_sre_netprobe.cli.tls_check")
def test_cli_tls_custom_timeout(
    mock_tls_check: MagicMock,
) -> None:
    mock_tls_check.return_value = TLSCheckResult(
        host="example.com",
        port=443,
        valid=True,
        expires_at="2030-12-31T23:59:59+00:00",
        days_remaining=100,
        issuer="commonName=Example CA",
        subject="commonName=example.com",
    )

    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "tls",
            "example.com",
            "--timeout",
            "4.5",
        ],
    ):
        main()

    mock_tls_check.assert_called_once_with(
        "example.com",
        443,
        timeout=4.5,
    )

def test_cli_invalid_tcp_port() -> None:
    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "tcp",
            "example.com",
            "70000",
        ],
    ):
        try:
            main()
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError("Expected SystemExit")


def test_cli_invalid_tls_port() -> None:
    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "tls",
            "example.com",
            "--port",
            "0",
        ],
    ):
        try:
            main()
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError("Expected SystemExit")


def test_cli_invalid_tcp_timeout() -> None:
    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "tcp",
            "example.com",
            "443",
            "--timeout",
            "0",
        ],
    ):
        try:
            main()
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError("Expected SystemExit")


def test_cli_invalid_http_timeout() -> None:
    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "http",
            "https://example.com",
            "--timeout",
            "-1",
        ],
    ):
        try:
            main()
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError("Expected SystemExit")

def test_cli_invalid_cidr() -> None:
    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "network",
            "192.168.1.500/24",
        ],
    ):
        try:
            main()
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError("Expected SystemExit")

def test_cli_invalid_http_url() -> None:
    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "http",
            "ftp://example.com",
        ],
    ):
        try:
            main()
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError("Expected SystemExit")

def test_cli_tcp_success_exit_code() -> None:
    result = TCPCheckResult(
        host="example.com",
        port=443,
        reachable=True,
        latency_ms=10.0,
        error=None,
    )

    with (
        patch(
            "sys.argv",
            ["jc-sre-netprobe", "tcp", "example.com", "443"],
        ),
        patch(
            "jc_sre_netprobe.cli.tcp_check",
            return_value=result,
        ),
    ):
        assert main() == 0


def test_cli_tcp_failure_exit_code() -> None:
    result = TCPCheckResult(
        host="example.com",
        port=443,
        reachable=False,
        latency_ms=None,
        error="Connection refused",
    )

    with (
        patch(
            "sys.argv",
            ["jc-sre-netprobe", "tcp", "example.com", "443"],
        ),
        patch(
            "jc_sre_netprobe.cli.tcp_check",
            return_value=result,
        ),
    ):
        assert main() == 1

def test_cli_dns_failure_exit_code() -> None:
    result = DNSCheckResult(
        hostname="invalid.example",
        addresses=[],
        resolved=False,
        error="Name resolution failed",
    )

    with (
        patch(
            "sys.argv",
            ["jc-sre-netprobe", "dns", "invalid.example"],
        ),
        patch(
            "jc_sre_netprobe.cli.dns_check",
            return_value=result,
        ),
    ):
        assert main() == 1


def test_cli_http_failure_exit_code() -> None:
    result = HTTPCheckResult(
        url="https://example.com",
        status_code=500,
        healthy=False,
        latency_ms=10.0,
        error=None,
    )

    with (
        patch(
            "sys.argv",
            ["jc-sre-netprobe", "http", "https://example.com"],
        ),
        patch(
            "jc_sre_netprobe.cli.http_check",
            return_value=result,
        ),
    ):
        assert main() == 1


def test_cli_tls_failure_exit_code() -> None:
    result = TLSCheckResult(
        host="example.com",
        port=443,
        valid=False,
        expires_at=None,
        days_remaining=None,
        issuer=None,
        subject=None,
        error="Certificate verification failed",
    )

    with (
        patch(
            "sys.argv",
            ["jc-sre-netprobe", "tls", "example.com"],
        ),
        patch(
            "jc_sre_netprobe.cli.tls_check",
            return_value=result,
        ),
    ):
        assert main() == 1

def test_cli_network_success_exit_code() -> None:
    result = NetworkInfo(
        network="192.168.1.0",
        prefix_length=24,
        netmask="255.255.255.0",
        broadcast="192.168.1.255",
        total_addresses=256,
        ip_version=4,
        is_private=True,
    )

    with (
        patch(
            "sys.argv",
            ["jc-sre-netprobe", "network", "192.168.1.0/24"],
        ),
        patch(
            "jc_sre_netprobe.cli.network_info",
            return_value=result,
        ),
    ):
        assert main() == 0

@pytest.mark.parametrize("json_position", ["none", "before", "after"])
def test_cli_run_success(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    json_position: str,
) -> None:
    config_path = tmp_path / "checks.yaml"
    config_path.write_text(
        "checks:\n"
        "  - name: local-network\n"
        "    type: network\n"
        "    cidr: 192.168.1.0/24\n",
        encoding="utf-8",
    )

    args = ["run", str(config_path)]

    if json_position == "before":
        args = ["--json", *args]
    elif json_position == "after":
        args.append("--json")

    monkeypatch.setattr(sys, "argv", ["jc-sre-netprobe", *args])

    assert main() == 0

    output = capsys.readouterr()

    if json_position == "none":
        assert "[OK] local-network (network)" in output.out
        assert "Healthy: 1" in output.out
    else:
        payload = json.loads(output.out)
        assert payload["total"] == 1
        assert payload["healthy"] == 1
        assert payload["failed"] == 0
        assert payload["results"][0]["name"] == "local-network"


def test_cli_run_failed_check(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "checks.yaml"
    config_path.write_text(
        "checks:\n"
        "  - name: invalid-http\n"
        "    type: http\n"
        "    url: https://example.com\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "jc_sre_netprobe.runner.http_check",
        lambda url, timeout: HTTPCheckResult(
            url=url,
            status_code=503,
            healthy=False,
            latency_ms=10.0,
            error=None,
        ),
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["jc-sre-netprobe", "run", str(config_path)],
    )

    assert main() == 1

    output = capsys.readouterr()
    assert "[FAIL] invalid-http (http)" in output.out
    assert "Failed:  1" in output.out


@pytest.mark.parametrize(
    "yaml_content",
    [
        "checks: []\n",
        "checks:\n  - name: invalid\n    type: unknown\n",
        "invalid: [\n",
    ],
)
def test_cli_run_invalid_config(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    yaml_content: str,
) -> None:
    config_path = tmp_path / "invalid.yaml"
    config_path.write_text(yaml_content, encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        ["jc-sre-netprobe", "run", str(config_path)],
    )

    assert main() == 2

    output = capsys.readouterr()
    assert "Configuration error:" in output.err


def test_cli_run_missing_file(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    missing_path = tmp_path / "missing.yaml"

    monkeypatch.setattr(
        sys,
        "argv",
        ["jc-sre-netprobe", "run", str(missing_path)],
    )

    assert main() == 2

    output = capsys.readouterr()
    assert "Configuration error:" in output.err