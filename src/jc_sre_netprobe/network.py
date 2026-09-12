"""IP network utilities."""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass


@dataclass(frozen=True)
class NetworkInfo:
    """Represent information about an IP network."""

    network: str
    prefix_length: int
    netmask: str
    broadcast: str | None
    total_addresses: int
    ip_version: int
    is_private: bool


def network_info(cidr: str) -> NetworkInfo:
    """Return information about an IPv4 or IPv6 network."""

    network = ipaddress.ip_network(cidr, strict=False)

    return NetworkInfo(
        network=str(network.network_address),
        prefix_length=network.prefixlen,
        netmask=str(network.netmask),
        broadcast=str(network.broadcast_address) if network.version == 4 else None,
        total_addresses=network.num_addresses,
        ip_version=network.version,
        is_private=network.is_private,
    )
