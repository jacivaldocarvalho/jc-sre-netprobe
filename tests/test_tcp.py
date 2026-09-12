from jc_sre_netprobe import TCPCheckResult


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
