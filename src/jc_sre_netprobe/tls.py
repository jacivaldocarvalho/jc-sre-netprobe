"""TLS certificate check utilities."""

from __future__ import annotations

import socket
import ssl
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import cast

CertificateName = tuple[tuple[tuple[str, str], ...], ...]


@dataclass(frozen=True)
class TLSCheckResult:
    """Represent the result of a TLS certificate check."""

    host: str
    port: int
    valid: bool
    expires_at: str | None
    days_remaining: int | None
    issuer: str | None
    subject: str | None
    error: str | None = None


def _certificate_name(entries: CertificateName) -> str | None:
    """Convert certificate subject or issuer entries to a readable string."""

    values = [
        f"{key}={value}"
        for group in entries
        for key, value in group
    ]

    return ", ".join(values) if values else None


def tls_check(
    host: str,
    port: int = 443,
    timeout: float = 5.0,
) -> TLSCheckResult:
    """Check the TLS certificate presented by an endpoint."""

    try:
        context = ssl.create_default_context()

        with socket.create_connection(
            (host, port),
            timeout=timeout,
        ) as tcp_socket, context.wrap_socket(
            tcp_socket,
            server_hostname=host,
        ) as tls_socket:
            certificate = tls_socket.getpeercert()

        if certificate is None:
            raise ssl.SSLError("Peer certificate is unavailable.")

        not_after = certificate.get("notAfter")

        if not isinstance(not_after, str):
            raise ssl.SSLError(
                "Certificate expiration date is unavailable."
            )

        expires = datetime.fromtimestamp(
            ssl.cert_time_to_seconds(not_after),
            tz=UTC,
        )

        now = datetime.now(UTC)
        days_remaining = (expires - now).days

        subject_value = certificate.get("subject")
        issuer_value = certificate.get("issuer")

        subject = (
            _certificate_name(
                cast(CertificateName, subject_value)
            )
            if isinstance(subject_value, tuple)
            else None
        )

        issuer = (
            _certificate_name(
                cast(CertificateName, issuer_value)
            )
            if isinstance(issuer_value, tuple)
            else None
        )

        return TLSCheckResult(
            host=host,
            port=port,
            valid=True,
            expires_at=expires.isoformat(),
            days_remaining=days_remaining,
            issuer=issuer,
            subject=subject,
        )

    except (OSError, ssl.SSLError, ValueError) as exc:
        return TLSCheckResult(
            host=host,
            port=port,
            valid=False,
            expires_at=None,
            days_remaining=None,
            issuer=None,
            subject=None,
            error=str(exc),
        )