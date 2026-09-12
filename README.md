# jc-sre-netprobe

Network health checks and utilities for Telecom, DevOps and SRE.

## Features

- TCP connectivity checks
- DNS resolution
- HTTP/HTTPS health checks
- IPv4/IPv6 network information
- CLI with JSON output

## Installation

```bash
pip install jc-sre-netprobe

## Example

jc-sre-netprobe tcp github.com 443
jc-sre-netprobe dns github.com
jc-sre-netprobe http https://github.com
jc-sre-netprobe network 192.168.1.10/24
