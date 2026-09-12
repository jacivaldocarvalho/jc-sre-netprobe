"""Command-line interface for jc-sre-netprobe."""

from __future__ import annotations

import argparse

from jc_sre_netprobe import dns_check, http_check, network_info, tcp_check


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="jc-sre-netprobe",
        description="Network health checks for Telecom, DevOps and SRE.",
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

    args = parser.parse_args()

    if args.command == "tcp":
        print(tcp_check(args.host, args.port))
    elif args.command == "dns":
        print(dns_check(args.hostname))
    elif args.command == "http":
        print(http_check(args.url))
    elif args.command == "network":
        print(network_info(args.cidr))
