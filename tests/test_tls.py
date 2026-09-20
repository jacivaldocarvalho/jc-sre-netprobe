"""Tests for TLS certificate checks."""

from __future__ import annotations

import ssl
from unittest.mock import MagicMock, patch

from jc_sre_netprobe.tls import TLSCheckResult, tls_check


def _certificate() -> dict[str, object]:
    return {
        "notAfter": "Dec 31 23:59:59 2030 GMT",
        "subject": ((("commonName", "example.com"),),),
        "issuer": ((("commonName", "Example CA"),),),
    }


def test_tls_check_result() -> None:
    result = TLSCheckResult(
        host="example.com",
        port=443,
        valid=True,
        expires_at="2030-12-31T23:59:59+00:00",
        days_remaining=100,
        issuer="commonName=Example CA",
        subject="commonName=example.com",
    )

    assert result.host == "example.com"
    assert result.port == 443
    assert result.valid is True
    assert result.error is None


@patch("jc_sre_netprobe.tls.ssl.create_default_context")
@patch("jc_sre_netprobe.tls.socket.create_connection")
def test_tls_check_success(
    mock_create_connection: MagicMock,
    mock_create_default_context: MagicMock,
) -> None:
    tcp_socket = MagicMock()
    tls_socket = MagicMock()
    context = MagicMock()

    mock_create_connection.return_value.__enter__.return_value = tcp_socket
    mock_create_default_context.return_value = context
    context.wrap_socket.return_value.__enter__.return_value = tls_socket

    tls_socket.getpeercert.return_value = _certificate()

    result = tls_check("example.com", 443)

    assert result.host == "example.com"
    assert result.port == 443
    assert result.valid is True
    assert result.expires_at == "2030-12-31T23:59:59+00:00"
    assert result.issuer == "commonName=Example CA"
    assert result.subject == "commonName=example.com"
    assert result.days_remaining is not None
    assert result.error is None

    mock_create_connection.assert_called_once_with(
        ("example.com", 443),
        timeout=5.0,
    )

    context.wrap_socket.assert_called_once_with(
        tcp_socket,
        server_hostname="example.com",
    )


@patch("jc_sre_netprobe.tls.ssl.create_default_context")
@patch("jc_sre_netprobe.tls.socket.create_connection")
def test_tls_check_certificate_error(
    mock_create_connection: MagicMock,
    mock_create_default_context: MagicMock,
) -> None:
    tcp_socket = MagicMock()
    context = MagicMock()

    mock_create_connection.return_value.__enter__.return_value = tcp_socket
    mock_create_default_context.return_value = context

    context.wrap_socket.side_effect = ssl.SSLCertVerificationError(
        "certificate verify failed"
    )

    result = tls_check("example.com", 443)

    assert result.valid is False
    assert result.expires_at is None
    assert result.days_remaining is None
    assert result.issuer is None
    assert result.subject is None
    assert result.error is not None


@patch("jc_sre_netprobe.tls.socket.create_connection")
def test_tls_check_connection_error(
    mock_create_connection: MagicMock,
) -> None:
    mock_create_connection.side_effect = OSError("connection failed")

    result = tls_check("example.com", 443)

    assert result.valid is False
    assert result.error == "connection failed"


@patch("jc_sre_netprobe.tls.socket.create_connection")
def test_tls_check_timeout(
    mock_create_connection: MagicMock,
) -> None:
    mock_create_connection.side_effect = TimeoutError("timed out")

    result = tls_check(
        "example.com",
        443,
        timeout=2.0,
    )

    assert result.valid is False
    assert result.error == "timed out"

    mock_create_connection.assert_called_once_with(
        ("example.com", 443),
        timeout=2.0,
    )