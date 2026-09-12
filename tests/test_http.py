from unittest.mock import MagicMock, patch

import httpx

from jc_sre_netprobe import http_check


@patch("jc_sre_netprobe.http.httpx.get")
def test_http_check_success(mock_get: MagicMock) -> None:
    mock_get.return_value.status_code = 200

    result = http_check("https://example.com")

    assert result.url == "https://example.com"
    assert result.status_code == 200
    assert result.healthy is True
    assert result.latency_ms is not None
    assert result.error is None


@patch("jc_sre_netprobe.http.httpx.get")
def test_http_check_server_error(mock_get: MagicMock) -> None:
    mock_get.return_value.status_code = 500

    result = http_check("https://example.com")

    assert result.status_code == 500
    assert result.healthy is False


@patch(
    "jc_sre_netprobe.http.httpx.get",
    side_effect=httpx.ConnectError("connection failed"),
)
def test_http_check_connection_error(mock_get: MagicMock) -> None:
    result = http_check("https://example.com")

    assert result.status_code is None
    assert result.healthy is False
    assert result.latency_ms is None
    assert result.error == "connection failed"
