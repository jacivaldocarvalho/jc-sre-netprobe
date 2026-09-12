import json
import sys
from unittest.mock import patch

from pytest import CaptureFixture

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
