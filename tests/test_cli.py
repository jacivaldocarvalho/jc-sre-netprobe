import json
import sys
from unittest.mock import MagicMock, patch

from pytest import CaptureFixture

from jc_sre_netprobe import TLSCheckResult
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
    )
