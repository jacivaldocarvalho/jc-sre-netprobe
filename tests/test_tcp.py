from unittest.mock import MagicMock, patch

from jc_sre_netprobe import TCPCheckResult, tcp_check


def test_tcp_check_result() -> None:
    result = TCPCheckResult(
        host="127.0.0.1",
        port=443,
        reachable=True,
        latency_ms=1.5,
    )

    assert result.host == "127.0.0.1"
    assert result.port == 443
    assert result.reachable is True
    assert result.latency_ms == 1.5
    assert result.error is None


@patch("jc_sre_netprobe.tcp.socket.create_connection")
def test_tcp_check_success(mock_create_connection: MagicMock) -> None:
    result = tcp_check("192.0.2.10", 443)

    assert result.host == "192.0.2.10"
    assert result.port == 443
    assert result.reachable is True
    assert result.latency_ms is not None
    assert result.latency_ms >= 0
    assert result.error is None

    mock_create_connection.assert_called_once_with(
        ("192.0.2.10", 443),
        timeout=3.0,
    )


@patch(
    "jc_sre_netprobe.tcp.socket.create_connection",
    side_effect=TimeoutError("timed out"),
)
def test_tcp_check_timeout(mock_create_connection: MagicMock) -> None:
    result = tcp_check(
        "192.0.2.10",
        443,
        timeout=1.0,
    )

    assert result.host == "192.0.2.10"
    assert result.port == 443
    assert result.reachable is False
    assert result.latency_ms is None
    assert result.error == "timed out"

    mock_create_connection.assert_called_once_with(
        ("192.0.2.10", 443),
        timeout=1.0,
    )
