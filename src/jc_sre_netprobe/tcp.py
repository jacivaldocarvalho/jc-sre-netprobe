"""TCP connectivity utilities."""

from __future__ import annotations

import socket
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class TCPCheckResult:
    """Represent the result of a TCP connectivity check."""

    host: str
    port: int
    reachable: bool
    latency_ms: float | None
    error: str | None = None


def tcp_check(
    host: str,
    port: int,
    timeout: float = 3.0,
) -> TCPCheckResult:
    """Check whether a TCP endpoint is reachable."""

    start_time = time.perf_counter()

    try:
        with socket.create_connection(
            (host, port),
            timeout=timeout,
        ):
            latency_ms = (time.perf_counter() - start_time) * 1000

            return TCPCheckResult(
                host=host,
                port=port,
                reachable=True,
                latency_ms=round(latency_ms, 2),
            )

    except OSError as exc:
        return TCPCheckResult(
            host=host,
            port=port,
            reachable=False,
            latency_ms=None,
            error=str(exc),
        )
