
"""YAML configuration models and validation for bulk network checks."""

from __future__ import annotations

import ipaddress
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, TypeAlias, cast
from urllib.parse import urlparse

import yaml

CheckType: TypeAlias = Literal["tcp", "dns", "http", "tls", "network"]


class ConfigError(ValueError):
    """Raised when a configuration file is invalid."""


@dataclass(frozen=True)
class CheckConfig:
    """Represent a validated network or service check."""

    name: str
    type: CheckType
    host: str | None = None
    port: int | None = None
    url: str | None = None
    cidr: str | None = None
    timeout: float | None = None


@dataclass(frozen=True)
class RunnerConfig:
    """Represent a validated bulk execution configuration."""

    checks: tuple[CheckConfig, ...]
    max_workers: int = 5


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader,
    node: yaml.MappingNode,
) -> dict[Any, Any]:
    """Construct a YAML mapping, rejecting duplicate keys."""
    mapping: dict[Any, Any] = {}

    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)

        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable mapping key",
                key_node.start_mark,
            ) from exc

        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate key: {key!r}",
                key_node.start_mark,
            )

        mapping[key] = loader.construct_object(value_node, deep=True)

    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML configuration file with basic structural validation."""
    config_path = Path(path)

    try:
        with config_path.open(encoding="utf-8") as file:
            data = yaml.load(file, Loader=UniqueKeyLoader)
    except OSError as exc:
        raise ConfigError(
            f"Unable to read configuration file '{config_path}': {exc}"
        ) from exc
    except (yaml.YAMLError, UnicodeError) as exc:
        raise ConfigError(
            f"Invalid YAML configuration '{config_path}': {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ConfigError("Configuration root must be a YAML mapping.")

    if not all(isinstance(key, str) for key in data):
        raise ConfigError("Configuration root keys must be strings.")

    return data


_CHECK_TYPES = {"tcp", "dns", "http", "tls", "network"}

_ALLOWED_FIELDS = {
    "tcp": {"name", "type", "host", "port", "timeout"},
    "dns": {"name", "type", "host"},
    "http": {"name", "type", "url", "timeout"},
    "tls": {"name", "type", "host", "port", "timeout"},
    "network": {"name", "type", "cidr"},
}

_REQUIRED_FIELDS = {
    "tcp": {"name", "type", "host", "port"},
    "dns": {"name", "type", "host"},
    "http": {"name", "type", "url"},
    "tls": {"name", "type", "host"},
    "network": {"name", "type", "cidr"},
}


def _positive_integer(value: object, field: str) -> int:
    if type(value) is not int or value <= 0:
        raise ConfigError(f"'{field}' must be a positive integer.")
    return value


def _port(value: object) -> int:
    port = _positive_integer(value, "port")
    if port > 65535:
        raise ConfigError("'port' must be between 1 and 65535.")
    return port

def _timeout(value: object) -> float:
    """Validate and normalize a positive finite timeout."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError("'timeout' must be a positive finite number.")

    try:
        timeout = float(value)
    except (OverflowError, ValueError) as exc:
        raise ConfigError(
            "'timeout' must be a positive finite number."
        ) from exc

    if not math.isfinite(timeout) or timeout <= 0:
        raise ConfigError("'timeout' must be a positive finite number.")

    return timeout

def _nonempty_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"'{field}' must be a nonempty string.")
    return value.strip()


def _validate_check(data: object, index: int) -> CheckConfig:
    if not isinstance(data, dict):
        raise ConfigError(f"Check #{index} must be a mapping.")

    if not all(isinstance(key, str) for key in data):
        raise ConfigError(f"Check #{index} has non-string field names.")

    name = _nonempty_string(data.get("name"), "name")
    check_type = _nonempty_string(data.get("type"), "type")

    if check_type not in _CHECK_TYPES:
        raise ConfigError(
            f"Check '{name}' has unsupported type '{check_type}'."
        )

    unknown = set(data) - _ALLOWED_FIELDS[check_type]
    if unknown:
        raise ConfigError(
            f"Check '{name}' has unknown fields: {sorted(unknown)}."
        )

    missing = _REQUIRED_FIELDS[check_type] - set(data)
    if missing:
        raise ConfigError(
            f"Check '{name}' is missing fields: {sorted(missing)}."
        )

    host = None
    port = None
    url = None
    cidr = None
    timeout = None

    if check_type in {"tcp", "dns", "tls"}:
        host = _nonempty_string(data["host"], "host")

    if check_type == "tcp":
        port = _port(data["port"])
    elif check_type == "tls":
        port = _port(data.get("port", 443))

    if check_type == "http":
        url = _nonempty_string(data["url"], "url")
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ConfigError(f"Check '{name}' has an invalid HTTP URL.")

    if check_type == "network":
        cidr = _nonempty_string(data["cidr"], "cidr")
        try:
            ipaddress.ip_network(cidr, strict=False)
        except ValueError as exc:
            raise ConfigError(
                f"Check '{name}' has an invalid CIDR."
            ) from exc

    if check_type in {"tcp", "http", "tls"}:
        default_timeout = 3.0 if check_type == "tcp" else 5.0
        timeout = _timeout(data.get("timeout", default_timeout))

    return CheckConfig(
        name=name,
        type=cast(CheckType, check_type),
        host=host,
        port=port,
        url=url,
        cidr=cidr,
        timeout=timeout,
    )


def validate_config(data: dict[str, object]) -> RunnerConfig:
    """Validate a parsed YAML configuration and normalize its checks."""
    unknown = set(data) - {"checks", "max_workers"}
    if unknown:
        raise ConfigError(f"Unknown root fields: {sorted(unknown)}.")

    max_workers = _positive_integer(
        data.get("max_workers", 5),
        "max_workers",
    )

    raw_checks = data.get("checks")
    if not isinstance(raw_checks, list) or not raw_checks:
        raise ConfigError("'checks' must be a nonempty list.")

    checks = []
    names: set[str] = set()

    for index, raw_check in enumerate(raw_checks, start=1):
        check = _validate_check(raw_check, index)

        if check.name in names:
            raise ConfigError(f"Duplicate check name: '{check.name}'.")

        names.add(check.name)
        checks.append(check)

    return RunnerConfig(
        checks=tuple(checks),
        max_workers=max_workers,
    )


def load_config(path: str | Path) -> RunnerConfig:
    """Load and validate a YAML configuration file."""
    return validate_config(load_yaml(path))
