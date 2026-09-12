import socket
from unittest.mock import MagicMock, patch

from jc_sre_netprobe import dns_check


@patch("jc_sre_netprobe.dns.socket.getaddrinfo")
def test_dns_check_success(mock_getaddrinfo: MagicMock) -> None:
    mock_getaddrinfo.return_value = [
        (
            socket.AF_INET,
            socket.SOCK_STREAM,
            6,
            "",
            ("192.0.2.10", 0),
        ),
        (
            socket.AF_INET6,
            socket.SOCK_STREAM,
            6,
            "",
            ("2001:db8::10", 0, 0, 0),
        ),
    ]

    result = dns_check("example.test")

    assert result.hostname == "example.test"
    assert result.resolved is True
    assert result.addresses == [
        "192.0.2.10",
        "2001:db8::10",
    ]
    assert result.error is None


@patch(
    "jc_sre_netprobe.dns.socket.getaddrinfo",
    side_effect=socket.gaierror("Name or service not known"),
)
def test_dns_check_failure(mock_getaddrinfo: MagicMock) -> None:
    result = dns_check("invalid.example")

    assert result.hostname == "invalid.example"
    assert result.resolved is False
    assert result.addresses == []
    assert result.error == "Name or service not known"
