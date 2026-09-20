"""Command-line interface for jc-sre-netprobe."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from jc_sre_netprobe import (
    DNSCheckResult,
    HTTPCheckResult,
    NetworkInfo,
    TCPCheckResult,
    TLSCheckResult,
    dns_check,
    http_check,
    network_info,
    tcp_check,
    tls_check,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="jc-sre-netprobe",
        description="Network health checks for Telecom, DevOps and SRE.",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Return output in JSON format.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    tcp_parser = subparsers.add_parser("tcp")
    tcp_parser.add_argument("host")
    tcp_parser.add_argument("port", type=int)

    dns_parser = subparsers.add_parser("dns")
    dns_parser.add_argument("hostname")

    http_parser = subparsers.add_parser("http")
    http_parser.add_argument("url")

    network_parser = subparsers.add_parser("network")
    network_parser.add_argument("cidr")

    tls_parser = subparsers.add_parser("tls")
    tls_parser.add_argument("host")
    tls_parser.add_argument(
        "--port",
        type=int,
        default=443,
    )

    args = parser.parse_args()

    result: (
    TCPCheckResult
    | DNSCheckResult
    | HTTPCheckResult
    | NetworkInfo
    | TLSCheckResult
    )

    if args.command == "tcp":
        result = tcp_check(args.host, args.port)
    elif args.command == "dns":
        result = dns_check(args.hostname)
    elif args.command == "http":
        result = http_check(args.url)
    elif args.command == "network":
        result = network_info(args.cidr)
    else:
        result = tls_check(args.host, args.port)

    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        print(result)