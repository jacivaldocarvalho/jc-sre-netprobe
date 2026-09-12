# JC SRE NETPROBE

[![PyPI](https://img.shields.io/pypi/v/jc-sre-netprobe)](https://pypi.org/project/jc-sre-netprobe/)
[![Python](https://img.shields.io/pypi/pyversions/jc-sre-netprobe)](https://pypi.org/project/jc-sre-netprobe/)
[![CI](https://github.com/jacivaldocarvalho/jc-sre-netprobe/actions/workflows/ci.yml/badge.svg)](https://github.com/jacivaldocarvalho/jc-sre-netprobe/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/jacivaldocarvalho/jc-sre-netprobe)](LICENSE)

Network health checks and utilities for **Telecom, Networking, DevOps and SRE**.

## Features

* TCP connectivity checks
* DNS resolution
* HTTP/HTTPS health checks
* IPv4 and IPv6 network information
* CLI for network diagnostics
* JSON output for automation and integrations

## Installation

Requires Python 3.11+.

```bash
pip install jc-sre-netprobe
```

## Usage

```bash
jc-sre-netprobe tcp github.com 443
jc-sre-netprobe dns github.com
jc-sre-netprobe http https://github.com
jc-sre-netprobe network 192.168.1.10/24
```

JSON output:

```bash
jc-sre-netprobe --json tcp github.com 443
```

Python API:

```python
from jc_sre_netprobe import tcp_check

result = tcp_check("github.com", 443)
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
