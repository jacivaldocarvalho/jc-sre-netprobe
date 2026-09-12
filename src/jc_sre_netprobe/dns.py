"""DNS resolution utilities."""

from __future__ import annotations

import socket
from dataclasses import dataclass


@dataclass(frozen=True)
class DNSCheckResult:
    """Represent the result of a DNS resolution."""

    hostname: str
    addresses: list[str]
    resolved: bool
    error: str | None = None


def dns_check(hostname: str) -> DNSCheckResult:
    """Resolve IPv4 and IPv6 addresses for a hostname."""

    try:
        results = socket.getaddrinfo(hostname, None)

        addresses: list[str] = sorted({
            str(result[4][0])
            for result in results
        })

        return DNSCheckResult(
            hostname=hostname,
            addresses=addresses,
            resolved=True,
        )

    except socket.gaierror as exc:
        return DNSCheckResult(
            hostname=hostname,
            addresses=[],
            resolved=False,
            error=str(exc),
        )
