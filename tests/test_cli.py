import json
import sys
from unittest.mock import MagicMock, patch

from pytest import CaptureFixture

from jc_sre_netprobe import HTTPCheckResult, TLSCheckResult
from jc_sre_netprobe.cli import main
from jc_sre_netprobe.tcp import TCPCheckResult


def test_cli_tcp_json(capsys: CaptureFixture[str]) -> None:
    expected = TCPCheckResult(
        host="example.com",
        port=443,
        reachable=True,
        latency_ms=10.5,
    )

    with (
        patch(
            "jc_sre_netprobe.cli.tcp_check",
            return_value=expected,
        ),
        patch.object(
            sys,
            "argv",
            [
                "jc-sre-netprobe",
                "--json",
                "tcp",
                "example.com",
                "443",
            ],
        ),
    ):
        main()

    captured = capsys.readouterr()
    output = json.loads(captured.out)

    assert output["host"] == "example.com"
    assert output["port"] == 443
    assert output["reachable"] is True
    assert output["latency_ms"] == 10.5
    assert output["error"] is None

@patch("jc_sre_netprobe.cli.tls_check")
def test_cli_tls_json(
    mock_tls_check: MagicMock,
    capsys: CaptureFixture[str],
) -> None:
    expected = TLSCheckResult(
        host="example.com",
        port=443,
        valid=True,
        expires_at="2030-12-31T23:59:59+00:00",
        days_remaining=100,
        issuer="commonName=Example CA",
        subject="commonName=example.com",
    )

    mock_tls_check.return_value = expected

    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "--json",
            "tls",
            "example.com",
        ],
    ):
        main()

    output = json.loads(capsys.readouterr().out)

    assert output["host"] == "example.com"
    assert output["port"] == 443
    assert output["valid"] is True
    assert output["expires_at"] == "2030-12-31T23:59:59+00:00"
    assert output["issuer"] == "commonName=Example CA"
    assert output["subject"] == "commonName=example.com"
    assert output["error"] is None

    mock_tls_check.assert_called_once_with(
        "example.com",
        443,
        timeout=5.0,
    )

@patch("jc_sre_netprobe.cli.tcp_check")
def test_cli_tcp_custom_timeout(
    mock_tcp_check: MagicMock,
) -> None:
    mock_tcp_check.return_value = TCPCheckResult(
        host="example.com",
        port=443,
        reachable=True,
        latency_ms=10.0,
    )

    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "tcp",
            "example.com",
            "443",
            "--timeout",
            "2.5",
        ],
    ):
        main()

    mock_tcp_check.assert_called_once_with(
        "example.com",
        443,
        timeout=2.5,
    )


@patch("jc_sre_netprobe.cli.http_check")
def test_cli_http_custom_timeout(
    mock_http_check: MagicMock,
) -> None:

    mock_http_check.return_value = HTTPCheckResult(
        url="https://example.com",
        status_code=200,
        healthy=True,
        latency_ms=10.0,
    )

    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "http",
            "https://example.com",
            "--timeout",
            "3.5",
        ],
    ):
        main()

    mock_http_check.assert_called_once_with(
        "https://example.com",
        timeout=3.5,
    )


@patch("jc_sre_netprobe.cli.tls_check")
def test_cli_tls_custom_timeout(
    mock_tls_check: MagicMock,
) -> None:
    mock_tls_check.return_value = TLSCheckResult(
        host="example.com",
        port=443,
        valid=True,
        expires_at="2030-12-31T23:59:59+00:00",
        days_remaining=100,
        issuer="commonName=Example CA",
        subject="commonName=example.com",
    )

    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "tls",
            "example.com",
            "--timeout",
            "4.5",
        ],
    ):
        main()

    mock_tls_check.assert_called_once_with(
        "example.com",
        443,
        timeout=4.5,
    )

def test_cli_invalid_tcp_port() -> None:
    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "tcp",
            "example.com",
            "70000",
        ],
    ):
        try:
            main()
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError("Expected SystemExit")


def test_cli_invalid_tls_port() -> None:
    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "tls",
            "example.com",
            "--port",
            "0",
        ],
    ):
        try:
            main()
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError("Expected SystemExit")


def test_cli_invalid_tcp_timeout() -> None:
    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "tcp",
            "example.com",
            "443",
            "--timeout",
            "0",
        ],
    ):
        try:
            main()
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError("Expected SystemExit")


def test_cli_invalid_http_timeout() -> None:
    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "http",
            "https://example.com",
            "--timeout",
            "-1",
        ],
    ):
        try:
            main()
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError("Expected SystemExit")

def test_cli_invalid_cidr() -> None:
    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "network",
            "192.168.1.500/24",
        ],
    ):
        try:
            main()
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError("Expected SystemExit")

def test_cli_invalid_http_url() -> None:
    with patch(
        "sys.argv",
        [
            "jc-sre-netprobe",
            "http",
            "ftp://example.com",
        ],
    ):
        try:
            main()
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError("Expected SystemExit")
