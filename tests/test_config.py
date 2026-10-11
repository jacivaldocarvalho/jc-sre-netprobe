
"""Tests for YAML configuration loading and validation."""

from pathlib import Path

import pytest

from jc_sre_netprobe.config import ConfigError, load_config, load_yaml, validate_config


@pytest.fixture
def valid_checks() -> list[dict[str, object]]:
    return [
        {
            "name": "tcp-check",
            "type": "tcp",
            "host": "127.0.0.1",
            "port": 443,
        },
        {
            "name": "dns-check",
            "type": "dns",
            "host": "example.com",
        },
        {
            "name": "http-check",
            "type": "http",
            "url": "https://example.com",
        },
        {
            "name": "tls-check",
            "type": "tls",
            "host": "example.com",
        },
        {
            "name": "network-check",
            "type": "network",
            "cidr": "192.168.1.0/24",
        },
    ]


def test_valid_configuration(
    valid_checks: list[dict[str, object]],
) -> None:
    config = validate_config({"checks": valid_checks})

    assert config.max_workers == 5
    assert len(config.checks) == 5
    assert [check.type for check in config.checks] == [
        "tcp", "dns", "http", "tls", "network"
    ]

    assert config.checks[0].port == 443
    assert config.checks[0].timeout == 3.0
    assert config.checks[2].timeout == 5.0
    assert config.checks[3].port == 443


def test_custom_workers(
    valid_checks: list[dict[str, object]],
) -> None:
    config = validate_config({
        "max_workers": 3,
        "checks": valid_checks,
    })

    assert config.max_workers == 3


@pytest.mark.parametrize(
    "workers",
    [0, -1, True, False, 2.5, "5", None],
)
def test_invalid_workers(workers: object) -> None:
    with pytest.raises(ConfigError, match="max_workers"):
        validate_config({
            "max_workers": workers,
            "checks": [{"name": "dns", "type": "dns", "host": "example.com"}],
        })


@pytest.mark.parametrize(
    "checks",
    [None, [], {}, "invalid"],
)
def test_invalid_checks_root(checks: object) -> None:
    with pytest.raises(ConfigError, match="checks"):
        validate_config({"checks": checks})


def test_duplicate_names() -> None:
    with pytest.raises(ConfigError, match="Duplicate check name"):
        validate_config({
            "checks": [
                {"name": "same", "type": "dns", "host": "example.com"},
                {"name": "same", "type": "dns", "host": "example.org"},
            ]
        })


@pytest.mark.parametrize(
    "check",
    [
        {"name": "x", "type": "unknown"},
        {"name": "x", "type": "tcp", "host": "localhost"},
        {"name": "x", "type": "tcp", "host": "localhost", "port": 0},
        {"name": "x", "type": "tcp", "host": "localhost", "port": 65536},
        {"name": "x", "type": "tcp", "host": "localhost", "port": True},
        {"name": "x", "type": "dns", "host": ""},
        {"name": "x", "type": "http", "url": "ftp://example.com"},
        {"name": "x", "type": "http", "url": "invalid"},
        {"name": "x", "type": "tls", "host": "example.com", "timeout": 0},
        {"name": "x", "type": "tls", "host": "example.com", "timeout": True},
        {"name": "x", "type": "network", "cidr": "invalid"},
        {"name": "x", "type": "dns", "host": "example.com", "extra": 1},
    ],
)
def test_invalid_check(check: dict[str, object]) -> None:
    with pytest.raises(ConfigError):
        validate_config({"checks": [check]})


@pytest.mark.parametrize(
    "timeout",
    [-1, 0, True, False, float("nan"), float("inf"), "5"],
)
def test_invalid_timeout(timeout: object) -> None:
    with pytest.raises(ConfigError, match="timeout"):
        validate_config({
            "checks": [
                {
                    "name": "tcp",
                    "type": "tcp",
                    "host": "localhost",
                    "port": 443,
                    "timeout": timeout,
                }
            ]
        })


def test_unknown_root_field() -> None:
    with pytest.raises(ConfigError, match="Unknown root fields"):
        validate_config({
            "checks": [{"name": "dns", "type": "dns", "host": "example.com"}],
            "unexpected": True,
        })


def test_load_valid_yaml(tmp_path: Path) -> None:
    config_file = tmp_path / "checks.yaml"
    config_file.write_text(
        "max_workers: 2\n"
        "checks:\n"
        "  - name: dns-test\n"
        "    type: dns\n"
        "    host: example.com\n",
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert config.max_workers == 2
    assert config.checks[0].name == "dns-test"


def test_duplicate_yaml_keys(tmp_path: Path) -> None:
    config_file = tmp_path / "duplicate.yaml"
    config_file.write_text(
        "max_workers: 2\n"
        "max_workers: 5\n"
        "checks: []\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="duplicate key"):
        load_yaml(config_file)


def test_nested_duplicate_yaml_keys(tmp_path: Path) -> None:
    config_file = tmp_path / "nested.yaml"
    config_file.write_text(
        "checks:\n"
        "  - name: dns\n"
        "    type: dns\n"
        "    host: example.com\n"
        "    host: example.org\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="duplicate key"):
        load_yaml(config_file)


def test_invalid_yaml_syntax(tmp_path: Path) -> None:
    config_file = tmp_path / "invalid.yaml"
    config_file.write_text("checks: [\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="Invalid YAML"):
        load_yaml(config_file)


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="Unable to read"):
        load_yaml(tmp_path / "missing.yaml")


@pytest.mark.parametrize(
    "content",
    ["", "[]", "null", "42", "- item"],
)
def test_invalid_yaml_root(tmp_path: Path, content: str) -> None:
    config_file = tmp_path / "root.yaml"
    config_file.write_text(content, encoding="utf-8")

    with pytest.raises(ConfigError, match="root"):
        load_yaml(config_file)