"""Command-line interface for jc-sre-netprobe."""

from __future__ import annotations

import argparse
import ipaddress
import json
from dataclasses import asdict
from urllib.parse import urlparse

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


def valid_port(value: str) -> int:
    """Validate a TCP port number."""

    port = int(value)

    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError(
            "port must be between 1 and 65535"
        )

    return port


def positive_timeout(value: str) -> float:
    """Validate a positive timeout value."""

    timeout = float(value)

    if timeout <= 0:
        raise argparse.ArgumentTypeError(
            "timeout must be greater than 0"
        )

    return timeout

def valid_cidr(value: str) -> str:
    """Validate an IPv4 or IPv6 network."""

    try:
        ipaddress.ip_network(value, strict=False)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "invalid IPv4 or IPv6 network"
        ) from exc

    return value

def valid_http_url(value: str) -> str:
    """Validate an HTTP or HTTPS URL."""

    parsed = urlparse(value)

    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise argparse.ArgumentTypeError(
            "URL must use http:// or https:// and include a host"
        )

    return value

def main() -> int:
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
    tcp_parser.add_argument("port", type=valid_port)

    tcp_parser.add_argument(
    "--timeout",
    type=positive_timeout,
    default=3.0,
    )

    dns_parser = subparsers.add_parser("dns")
    dns_parser.add_argument("hostname")

    http_parser = subparsers.add_parser("http")
    http_parser.add_argument(
        "url",
        type=valid_http_url,
    )

    http_parser.add_argument(
    "--timeout",
    type=positive_timeout,
    default=5.0,
    )

    network_parser = subparsers.add_parser("network")
    network_parser.add_argument(
        "cidr",
        type=valid_cidr,
    )

    tls_parser = subparsers.add_parser("tls")
    tls_parser.add_argument("host")
    tls_parser.add_argument(
        "--port",
        type=valid_port,
        default=443,
    )

    tls_parser.add_argument(
    "--timeout",
    type=positive_timeout,
    default=5.0,
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
        result = tcp_check(
            args.host,
            args.port,
            timeout=args.timeout,
        )
    elif args.command == "dns":
        result = dns_check(args.hostname)
    elif args.command == "http":
        result = http_check(
            args.url,
            timeout=args.timeout,
        )
    elif args.command == "network":
        result = network_info(args.cidr)
    else:
        result = tls_check(
            args.host,
            args.port,
            timeout=args.timeout,
        )

    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        print(result)

    if isinstance(result, TCPCheckResult):
        return 0 if result.reachable else 1

    if isinstance(result, DNSCheckResult):
        return 0 if result.resolved else 1

    if isinstance(result, HTTPCheckResult):
        return 0 if result.healthy else 1

    if isinstance(result, TLSCheckResult):
        return 0 if result.valid else 1

    return 0

def cli() -> None:
    """Run the command-line interface."""

    raise SystemExit(main())