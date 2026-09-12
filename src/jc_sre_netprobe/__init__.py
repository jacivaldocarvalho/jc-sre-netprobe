"""Network utilities for Telecom, DevOps and SRE."""

from jc_sre_netprobe.dns import DNSCheckResult, dns_check
from jc_sre_netprobe.tcp import TCPCheckResult, tcp_check

__all__ = [
    "DNSCheckResult",
    "TCPCheckResult",
    "dns_check",
    "tcp_check",
]
