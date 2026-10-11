
# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - Unreleased

### Added

- YAML-based configuration for defining multiple network and service checks.
- Configuration loading and validation through `config.py`.
- Support for TCP, DNS, HTTP, TLS and Network checks in YAML configurations.
- Validation of required fields, check types, ports, timeouts, URLs and CIDR networks.
- Detection of duplicate check names and YAML mapping keys.
- Rejection of unknown configuration properties.
- Concurrent bulk check execution using `ThreadPoolExecutor`.
- Configurable concurrency through the `max_workers` parameter.
- Individual check results and aggregated health summaries.
- Structured bulk execution results through `CheckResult` and `BulkResult`.
- New `run` CLI command for executing checks from YAML configuration files.
- Human-readable output for bulk execution.
- JSON output for bulk execution, supporting both global and command-level `--json` flags.
- Aggregated CLI exit codes:
  - `0` when all checks are healthy.
  - `1` when one or more checks are unhealthy.
  - `2` for invalid CLI usage or configuration.
- Example YAML configuration in `examples/checks.yaml`.
- Automated tests for YAML configuration, concurrent execution and CLI integration.
- PyYAML runtime dependency.

### Changed

- Extended the CLI with configuration-driven bulk execution while preserving existing commands.
- Added bounded concurrent execution of independent checks.
- Preserved configuration order in aggregated results.
- Isolated individual check failures to prevent interruption of other checks.
- Expanded README documentation with YAML configuration, bulk execution and operational examples.

### Quality

- 106 automated tests passing.
- 97% overall test coverage.
- Ruff and Mypy validation passing.
- GitHub Actions CI passing on Python 3.11, 3.12 and 3.13.

## [0.2.0] - 2026-09-20

### Added

- TLS certificate validation with expiration information.
- TLS certificate issuer and subject information.
- `tls` CLI command with configurable port and timeout.
- Configurable timeouts for TCP, HTTP and TLS CLI checks.
- CLI validation for TCP/TLS ports and timeout values.
- CLI validation for IPv4 and IPv6 CIDR networks.
- CLI validation for HTTP and HTTPS URLs.
- Operational CLI exit codes:
  - `0` for successful or healthy checks.
  - `1` for unhealthy or unavailable targets.
  - `2` for invalid CLI usage or input.
- Automated tests covering TLS checks, CLI validation and exit codes.

### Changed

- CLI entry point now propagates operational exit codes to the shell.
- README documentation expanded with TLS usage, timeouts and exit codes.

## [0.1.0]

### Added

- TCP connectivity checks with latency measurement.
- DNS resolution checks.
- HTTP/HTTPS health checks.
- IPv4 and IPv6 network information.
- JSON output for CLI automation.
- Python API for network health checks.
- Initial CLI interface.
- Ruff, Mypy, Pytest and coverage configuration.
- GitHub Actions CI for Python 3.11, 3.12 and 3.13.
- PyPI publishing through OIDC Trusted Publishing.
