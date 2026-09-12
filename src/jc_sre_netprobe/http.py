"""HTTP health check utilities."""

from __future__ import annotations

import time
from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class HTTPCheckResult:
    """Represent the result of an HTTP health check."""

    url: str
    status_code: int | None
    healthy: bool
    latency_ms: float | None
    error: str | None = None


def http_check(
    url: str,
    timeout: float = 5.0,
) -> HTTPCheckResult:
    """Check HTTP endpoint availability and latency."""

    start_time = time.perf_counter()

    try:
        response = httpx.get(
            url,
            timeout=timeout,
            follow_redirects=True,
        )

        latency_ms = (time.perf_counter() - start_time) * 1000

        return HTTPCheckResult(
            url=url,
            status_code=response.status_code,
            healthy=200 <= response.status_code < 400,
            latency_ms=round(latency_ms, 2),
        )

    except httpx.RequestError as exc:
        return HTTPCheckResult(
            url=url,
            status_code=None,
            healthy=False,
            latency_ms=None,
            error=str(exc),
        )
