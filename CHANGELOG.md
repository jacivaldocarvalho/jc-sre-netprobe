# Changelog

All notable changes to this project will be documented in this file.

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