# JC SRE NETPROBE

[![PyPI](https://img.shields.io/pypi/v/jc-sre-netprobe)](https://pypi.org/project/jc-sre-netprobe/)
[![Python](https://img.shields.io/pypi/pyversions/jc-sre-netprobe)](https://pypi.org/project/jc-sre-netprobe/)
[![CI](https://github.com/jacivaldocarvalho/jc-sre-netprobe/actions/workflows/ci.yml/badge.svg)](https://github.com/jacivaldocarvalho/jc-sre-netprobe/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/jacivaldocarvalho/jc-sre-netprobe)](LICENSE)

Network health checks and utilities for **Telecom, Networking, DevOps and SRE**.

## Features

* TCP connectivity checks with latency measurement
* DNS resolution checks
* HTTP/HTTPS health checks
* IPv4 and IPv6 network information
* TLS certificate validation and expiration information
* Configurable timeouts for TCP, HTTP and TLS checks
* JSON output for automation and scripting
* CLI input validation
* Operational exit codes

## Use Cases

`jc-sre-netprobe` provides network and service probes that can be used for troubleshooting, automation and basic availability checks across Networking, Telecom, DevOps and SRE environments.

### SRE and DevOps

The package can be used as a lightweight black-box probing tool to verify whether services are reachable and healthy from an external perspective.

Typical use cases include:

* Checking TCP service availability and connection latency
* Verifying DNS resolution
* Monitoring HTTP/HTTPS endpoint health
* Validating TLS certificates and expiration information
* Using JSON output in scripts and automation workflows
* Using exit codes in CI/CD pipelines, health checks and operational scripts
* Applying configurable timeouts to control probe execution

Example:

```bash
jc-sre-netprobe http https://api.example.com
echo $?
```

The exit code can be consumed by automation:

* `0` — target is healthy
* `1` — target is unhealthy or unavailable
* `2` — invalid CLI usage or input

### Networking and Telecom

The probes can also support network troubleshooting by validating different components involved in service delivery:

```text
Application
├── HTTP/HTTPS ──> http check
├── TLS ─────────> TLS certificate check
│
Transport
└── TCP ─────────> TCP connectivity check
│
Network Services
└── DNS ─────────> DNS resolution check
│
Addressing
└── IPv4/IPv6 ──> network information
```

For example, when investigating an unavailable application:

```bash
jc-sre-netprobe dns api.example.com
jc-sre-netprobe tcp api.example.com 443
jc-sre-netprobe tls api.example.com
jc-sre-netprobe http https://api.example.com
```

Running the probes independently helps isolate whether a failure is related to name resolution, TCP connectivity, TLS certificate validation or the HTTP service itself.

### Automation

Structured output makes the package suitable as a building block for other operational tools:

```bash
jc-sre-netprobe --json tls api.example.com
```

The combination of structured results, JSON output, configurable timeouts and operational exit codes allows the probes to be integrated into scripts, CI/CD workflows and monitoring processes.


## Installation

Requires Python 3.11+.

```bash
pip install jc-sre-netprobe
```

## Usage

```bash
jc-sre-netprobe tcp HOST PORT [--timeout SECONDS]
jc-sre-netprobe dns HOSTNAME
jc-sre-netprobe http URL [--timeout SECONDS]
jc-sre-netprobe network CIDR
jc-sre-netprobe tls HOST [--port PORT] [--timeout SECONDS]
```

### Examples

TCP connectivity check:

```bash
jc-sre-netprobe tcp github.com 443
```

TLS certificate check:

```bash
jc-sre-netprobe tls github.com
```

TLS check with a custom timeout:

```bash
jc-sre-netprobe tls github.com --timeout 3
```

JSON output:

```bash
jc-sre-netprobe --json tls github.com
```

### Exit codes

The CLI uses exit codes designed for automation, monitoring and scripting:

| Code | Meaning                                          |
| ---- | ------------------------------------------------ |
| `0`  | Check completed successfully / target is healthy |
| `1`  | Target is unhealthy or unavailable               |
| `2`  | Invalid CLI usage or input                       |

Example:

```bash
jc-sre-netprobe tcp github.com 443
echo $?
```

## Python API

```python
from jc_sre_netprobe import tcp_check

result = tcp_check("github.com", 443)

print(result)
```

TLS checks are also available through the Python API:

```python
from jc_sre_netprobe import tls_check

result = tls_check("github.com")

print(result)
```

## Development

```bash
git clone https://github.com/jacivaldocarvalho/jc-sre-netprobe.git
cd jc-sre-netprobe

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
```

Quality checks:

```bash
ruff check .
mypy src tests
pytest --cov=jc_sre_netprobe
```

## CI/CD

GitHub Actions validates the project with Python 3.11, 3.12 and 3.13 using:

* Ruff
* Mypy
* Pytest
* Coverage
* Package build

Releases are published to PyPI using **GitHub Actions, OpenID Connect (OIDC) and PyPI Trusted Publishing**, without long-lived PyPI credentials.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

## Author

**Jacivaldo Carvalho**

Telecommunications Engineer | DevOps | SRE | Networking
