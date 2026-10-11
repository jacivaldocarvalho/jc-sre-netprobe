
"""Concurrent execution models for bulk network checks."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from typing import Any

from jc_sre_netprobe.config import CheckConfig, CheckType, RunnerConfig
from jc_sre_netprobe.dns import dns_check
from jc_sre_netprobe.http import http_check
from jc_sre_netprobe.network import network_info
from jc_sre_netprobe.tcp import tcp_check
from jc_sre_netprobe.tls import tls_check


@dataclass(frozen=True)
class CheckResult:
    """Represent the normalized result of a single check."""

    name: str
    type: CheckType
    healthy: bool
    details: dict[str, Any]
    error: str | None = None


@dataclass(frozen=True)
class BulkResult:
    """Represent the aggregated result of multiple checks."""

    total: int
    healthy: int
    failed: int
    results: tuple[CheckResult, ...]



def _execute_check(check: CheckConfig) -> CheckResult:
    """Execute one check and normalize its result.

    Unexpected probe exceptions are isolated so that one failing
    check does not interrupt the remaining bulk execution.
    """
    try:
        if check.type == "tcp":
            assert check.host is not None
            assert check.port is not None
            assert check.timeout is not None

            tcp_result = tcp_check(
                check.host,
                check.port,
                timeout=check.timeout,
            )

            return CheckResult(
                name=check.name,
                type=check.type,
                healthy=tcp_result.reachable,
                details=asdict(tcp_result),
                error=tcp_result.error,
            )

        if check.type == "dns":
            assert check.host is not None

            dns_result = dns_check(check.host)

            return CheckResult(
                name=check.name,
                type=check.type,
                healthy=dns_result.resolved,
                details=asdict(dns_result),
                error=dns_result.error,
            )

        if check.type == "http":
            assert check.url is not None
            assert check.timeout is not None

            http_result = http_check(
                check.url,
                timeout=check.timeout,
            )

            return CheckResult(
                name=check.name,
                type=check.type,
                healthy=http_result.healthy,
                details=asdict(http_result),
                error=http_result.error,
            )

        if check.type == "tls":
            assert check.host is not None
            assert check.port is not None
            assert check.timeout is not None

            tls_result = tls_check(
                check.host,
                port=check.port,
                timeout=check.timeout,
            )

            return CheckResult(
                name=check.name,
                type=check.type,
                healthy=tls_result.valid,
                details=asdict(tls_result),
                error=tls_result.error,
            )

        if check.type == "network":
            assert check.cidr is not None

            network_result = network_info(check.cidr)

            return CheckResult(
                name=check.name,
                type=check.type,
                healthy=True,
                details=asdict(network_result),
            )

        raise ValueError(f"Unsupported check type: {check.type}")

    except Exception as exc:  # noqa: BLE001
        return CheckResult(
            name=check.name,
            type=check.type,
            healthy=False,
            details={},
            error=f"{type(exc).__name__}: {exc}",
        )


def run_checks(config: RunnerConfig) -> BulkResult:
    """Execute configured checks concurrently and aggregate results.

    Results preserve the original configuration order, regardless
    of the order in which individual checks complete.
    """
    if not config.checks:
        raise ValueError("RunnerConfig must contain at least one check.")

    if isinstance(config.max_workers, bool) or not isinstance(
        config.max_workers, int
    ) or config.max_workers <= 0:
        raise ValueError("max_workers must be a positive integer.")

    with ThreadPoolExecutor(
        max_workers=config.max_workers,
    ) as executor:
        results = tuple(
            executor.map(_execute_check, config.checks)
        )

    healthy = sum(result.healthy for result in results)
    total = len(results)

    return BulkResult(
        total=total,
        healthy=healthy,
        failed=total - healthy,
        results=results,
    )
