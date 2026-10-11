
# JC SRE NETPROBE

[![PyPI](https://img.shields.io/pypi/v/jc-sre-netprobe?cacheSeconds=300&v=2)](https://pypi.org/project/jc-sre-netprobe/)
[![Python](https://img.shields.io/pypi/pyversions/jc-sre-netprobe)](https://pypi.org/project/jc-sre-netprobe/)
[![CI](https://github.com/jacivaldocarvalho/jc-sre-netprobe/actions/workflows/ci.yml/badge.svg)](https://github.com/jacivaldocarvalho/jc-sre-netprobe/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/jacivaldocarvalho/jc-sre-netprobe)](LICENSE)

Network and service health checks for **Telecom infrastructure, Networking, DevOps and SRE**.

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
* YAML-based configuration for multiple checks
* Concurrent bulk execution with configurable workers
* Individual check results and aggregated health status
* Bulk check results in text and JSON formats

## Use Cases

`jc-sre-netprobe` provides network and service probes for troubleshooting,
automation and basic availability checks in IP-based infrastructures.

It is designed for Networking, DevOps and SRE workflows, with applicability
to telecommunications operators, internet service providers (ISPs),
enterprise networks and cloud environments.

### SRE and DevOps

The package can be used as a lightweight black-box probing tool to verify whether services are reachable and healthy from an external perspective.

Typical use cases include:

* Checking TCP service availability and connection latency
* Verifying DNS resolution
* Monitoring HTTP/HTTPS endpoint health
* Validating TLS certificates and expiration information
* Running multiple checks concurrently
* Using JSON output in scripts and automation workflows
* Using exit codes in CI/CD pipelines and operational scripts
* Applying configurable timeouts to control probe execution

Example:

```bash
jc-sre-netprobe http https://api.example.com
echo $?
```

The exit code can be consumed by automation:

* `0` — target is healthy
* `1` — target is unhealthy or unavailable
* `2` — invalid CLI usage, input or configuration

### Networking and Telecommunications Infrastructure

The project focuses on IP networking and service-level checks that
can support troubleshooting in enterprise networks, cloud environments
and telecommunications infrastructures.

It does not currently provide specialized optical, radio-frequency,
routing telemetry or carrier-grade performance measurements.

The probes support network troubleshooting by validating different components involved in service delivery:

```text
Application
├── HTTP/HTTPS ──> HTTP check
├── TLS ─────────> TLS certificate check
│
Transport
└── TCP ─────────> TCP connectivity check
│
Network Services
└── DNS ─────────> DNS resolution check
│
Addressing
└── IPv4/IPv6 ──> Network information
```

For example, when investigating an unavailable application:

```bash
jc-sre-netprobe dns api.example.com
jc-sre-netprobe tcp api.example.com 443
jc-sre-netprobe tls api.example.com
jc-sre-netprobe http https://api.example.com
```

Running these probes independently helps isolate whether a failure is related to name resolution, TCP connectivity, TLS certificate validation or the HTTP service itself.

### Automation

Structured output makes the package suitable as a building block for operational tools:

```bash
jc-sre-netprobe --json tls api.example.com
```

Multiple checks can also be defined in YAML and executed through a single command:

```bash
jc-sre-netprobe run checks.yaml --json
```

The combination of structured results, configurable timeouts, concurrent execution and operational exit codes allows integration into scripts, CI/CD workflows and monitoring processes.

## Installation

Requires Python 3.11+.

```bash
pip install jc-sre-netprobe
```

To install a specific version after its release:

```bash
pip install jc-sre-netprobe==0.3.0
```

Bulk execution is available starting with v0.3.0, published on PyPI.

## Usage

```bash
jc-sre-netprobe tcp HOST PORT [--timeout SECONDS]
jc-sre-netprobe dns HOSTNAME
jc-sre-netprobe http URL [--timeout SECONDS]
jc-sre-netprobe network CIDR
jc-sre-netprobe tls HOST [--port PORT] [--timeout SECONDS]
jc-sre-netprobe run CONFIG.yaml [--json]
```

Use `--help` to display available commands:

```bash
jc-sre-netprobe --help
jc-sre-netprobe run --help
```

### Examples

TCP connectivity check:

```bash
jc-sre-netprobe tcp github.com 443
```

DNS resolution:

```bash
jc-sre-netprobe dns github.com
```

HTTP endpoint health:

```bash
jc-sre-netprobe http https://github.com
```

TLS certificate check:

```bash
jc-sre-netprobe tls github.com
```

TLS check with a custom timeout:

```bash
jc-sre-netprobe tls github.com --timeout 3
```

IPv4 network information:

```bash
jc-sre-netprobe network 192.168.1.0/24
```

JSON output:

```bash
jc-sre-netprobe --json tls github.com
```

## Bulk Checks

Starting with v0.3.0, `jc-sre-netprobe` supports executing multiple network and service checks from a YAML configuration file.

The bulk runner uses concurrent execution to process independent checks and produces individual results with an aggregated health summary.

### YAML Configuration

Create a file named `checks.yaml`:

```yaml
max_workers: 5

checks:
  - name: github-tcp
    type: tcp
    host: github.com
    port: 443
    timeout: 3

  - name: github-http
    type: http
    url: https://github.com
    timeout: 5

  - name: github-dns
    type: dns
    host: github.com

  - name: github-tls
    type: tls
    host: github.com
    port: 443
    timeout: 5

  - name: private-network
    type: network
    cidr: 192.168.1.0/24
```

Supported check types:

| Type | Purpose | Required parameters |
| --- | --- | --- |
| `tcp` | TCP connectivity | `host`, `port` |
| `dns` | DNS resolution | `host` |
| `http` | HTTP/HTTPS health | `url` |
| `tls` | TLS certificate check | `host` |
| `network` | IPv4/IPv6 network information | `cidr` |

The `max_workers` parameter controls the maximum number of checks executed concurrently.

Each check must have a unique name.

Timeouts can be configured for supported check types.

### Running Multiple Checks

Execute the configuration:

```bash
jc-sre-netprobe run checks.yaml
```

Example output (illustrative):

```text
Bulk Check Results
------------------
[OK] github-tcp (tcp)
[OK] github-http (http)
[OK] github-dns (dns)
[OK] github-tls (tls)
[OK] private-network (network)

Total:   5
Healthy: 5
Failed:  0
```

If a check fails, it is reported individually without preventing the remaining checks from completing.

### JSON Output

Run checks with JSON output:

```bash
jc-sre-netprobe run checks.yaml --json
```

Alternatively, use the global JSON flag:

```bash
jc-sre-netprobe --json run checks.yaml
```

Illustrative JSON output:

```json
{
  "total": 2,
  "healthy": 1,
  "failed": 1,
  "results": [
    {
      "name": "service-tcp",
      "type": "tcp",
      "healthy": true,
      "details": {},
      "error": null
    },
    {
      "name": "unavailable-service",
      "type": "tcp",
      "healthy": false,
      "details": {},
      "error": "Connection refused"
    }
  ]
}
```

The `details` field contains probe-specific information. The output above is simplified to demonstrate the result structure.

### Bulk Exit Codes

| Code | Meaning |
| --- | --- |
| `0` | All checks are healthy |
| `1` | One or more checks are unhealthy |
| `2` | Invalid configuration or input |

Example:

```bash
jc-sre-netprobe run checks.yaml
echo $?
```

### Example Configuration

A sample YAML configuration is included in the repository:

```bash
jc-sre-netprobe run examples/checks.yaml
```

## Practical Examples

The following scenarios demonstrate how `jc-sre-netprobe` can be used in operational environments.

### 1. API Availability Checks

Scenario: An SRE team needs to verify DNS resolution, TCP connectivity, TLS and HTTP availability for a public API.

Create `api-checks.yaml`:

```yaml
max_workers: 4

checks:
  - name: api-dns
    type: dns
    host: api.github.com

  - name: api-tcp
    type: tcp
    host: api.github.com
    port: 443
    timeout: 3

  - name: api-tls
    type: tls
    host: api.github.com
    port: 443
    timeout: 5

  - name: api-http
    type: http
    url: https://api.github.com
    timeout: 5
```

Execute:

```bash
jc-sre-netprobe run api-checks.yaml
```

This allows the operator to distinguish between connectivity, DNS, TLS and application-layer failures.

The checks are independent and do not establish the root cause automatically.

### 2. Internal Infrastructure Checks

Scenario: A DevOps engineer needs to verify connectivity to services deployed in a private network.

Create `infrastructure-checks.yaml`:

```yaml
max_workers: 3

checks:
  - name: database-postgresql
    type: tcp
    host: 10.10.0.10
    port: 5432
    timeout: 3

  - name: redis-cache
    type: tcp
    host: 10.10.0.11
    port: 6379
    timeout: 3

  - name: internal-api
    type: http
    url: http://10.10.0.20:8080/health
    timeout: 5

  - name: internal-network
    type: network
    cidr: 10.10.0.0/24
```

Execute:

```bash
jc-sre-netprobe run infrastructure-checks.yaml
```

This configuration verifies service reachability from the machine running the probes.

The addresses are illustrative and must be replaced with actual infrastructure endpoints.

TCP connectivity confirms that a connection can be established; it does not validate database authentication or application transactions.

The network check returns addressing information rather than performing a subnet scan.

### 3. Telecom and ISP Troubleshooting

Scenario: A network operations team needs to investigate connectivity between infrastructure services and an external endpoint.

Create `telecom-checks.yaml`:

```yaml
max_workers: 4

checks:
  - name: public-dns
    type: dns
    host: cloudflare.com

  - name: external-https
    type: tcp
    host: cloudflare.com
    port: 443
    timeout: 3

  - name: external-tls
    type: tls
    host: cloudflare.com
    port: 443
    timeout: 5

  - name: internal-gateway-service
    type: tcp
    host: 192.168.1.1
    port: 443
    timeout: 3

  - name: local-subnet
    type: network
    cidr: 192.168.1.0/24
```

Execute:

```bash
jc-sre-netprobe run telecom-checks.yaml
```

The results provide a basic view of service connectivity and name resolution from the probe host.

This tool does not replace ICMP monitoring, routing analysis, SNMP telemetry or network performance monitoring systems.

### 4. CI/CD Deployment Validation

Scenario: A deployment pipeline must verify that an application endpoint is reachable before proceeding.

Create `deployment-checks.yaml`:

```yaml
max_workers: 2

checks:
  - name: application-http
    type: http
    url: https://example.com
    timeout: 5

  - name: application-tls
    type: tls
    host: example.com
    port: 443
    timeout: 5
```

Execute:

```bash
jc-sre-netprobe run deployment-checks.yaml
```

The command returns a nonzero exit code when one or more checks fail.

A simple shell validation:

```bash
if jc-sre-netprobe run deployment-checks.yaml; then
    echo "Health checks passed"
else
    echo "Health checks failed"
    exit 1
fi
```

Example GitHub Actions step:

```yaml
- name: Install NetProbe
  run: pip install jc-sre-netprobe

- name: Validate deployment
  run: jc-sre-netprobe run deployment-checks.yaml
```

For bulk execution functionality, ensure the pipeline installs jc-sre-netprobe version 0.3.0 or later.

### 5. JSON Integration with Automation

Scenario: An automation script needs to identify failed checks and generate a structured report.

Execute:

```bash
jc-sre-netprobe run checks.yaml --json > results.json
```

Inspect the results using `jq`:

```bash
jq '.failed' results.json
```

List failed checks:

```bash
jq '.results[] | select(.healthy == false) | .name' results.json
```

Generate a compact summary:

```bash
jq '{total, healthy, failed}' results.json
```

The JSON output can be consumed by external automation systems, dashboards and incident-processing workflows.

### 6. Python Automation

The YAML configuration and bulk runner can also be used programmatically:

```python
from jc_sre_netprobe.config import load_config
from jc_sre_netprobe.runner import run_checks

config = load_config("checks.yaml")
result = run_checks(config)

print(f"Total: {result.total}")
print(f"Healthy: {result.healthy}")
print(f"Failed: {result.failed}")

for check in result.results:
    print(check.name, check.healthy)
```

This provides a foundation for integrating network probes into custom operational applications.

## Exit Codes

The CLI uses exit codes designed for automation, monitoring and scripting:

| Code | Meaning |
| --- | --- |
| `0` | Check completed successfully / target is healthy |
| `1` | Target is unhealthy or unavailable |
| `2` | Invalid CLI usage, input or configuration |

For bulk execution, code `1` indicates that at least one check is unhealthy.

Example:

```bash
jc-sre-netprobe tcp github.com 443
echo $?
```

## Python API

TCP checks:

```python
from jc_sre_netprobe import tcp_check

result = tcp_check("github.com", 443)

print(result)
```

TLS checks:

```python
from jc_sre_netprobe import tls_check

result = tls_check("github.com")

print(result)
```

Bulk checks:

```python
from jc_sre_netprobe.config import load_config
from jc_sre_netprobe.runner import run_checks

config = load_config("checks.yaml")
result = run_checks(config)

print(result)
```

## Development

Clone the repository:

```bash
git clone https://github.com/jacivaldocarvalho/jc-sre-netprobe.git
cd jc-sre-netprobe
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install development dependencies:

```bash
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

Telecommunications Engineer | DevOps Engineer | SRE | Networking

[GitHub](https://github.com/jacivaldocarvalho) | [LinkedIn](https://www.linkedin.com/in/jacivaldocarvalho) | [Website](https://www.jacivaldocarvalho.com/)
