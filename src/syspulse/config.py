"""Safe loading of SysPulse TOML configuration files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


@dataclass(frozen=True)
class SysPulseConfig:
    cpu_threshold: float | None = None
    memory_threshold: float | None = None
    disk_threshold: float | None = None
    webhook_env: str | None = None


def _threshold(value: Any, name: str) -> float | None:
    if value is None:
        return None
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 100:
        raise ValueError(f"{name} must be a number between 0 and 100")
    return float(value)


def load_config(path: str | None) -> SysPulseConfig:
    """Load optional configuration, validating only the supported schema."""
    if path is None:
        return SysPulseConfig()
    with Path(path).open("rb") as stream:
        data = tomllib.load(stream)
    if not isinstance(data, dict):
        raise ValueError("configuration root must be a TOML table")

    thresholds = data.get("thresholds", {})
    alerts = data.get("alerts", {})
    if not isinstance(thresholds, dict) or not isinstance(alerts, dict):
        raise ValueError("[thresholds] and [alerts] must be TOML tables")
    webhook_env = alerts.get("webhook_env")
    if webhook_env is not None and (not isinstance(webhook_env, str) or not webhook_env):
        raise ValueError("alerts.webhook_env must be a non-empty environment variable name")
    return SysPulseConfig(
        cpu_threshold=_threshold(thresholds.get("cpu"), "thresholds.cpu"),
        memory_threshold=_threshold(thresholds.get("memory"), "thresholds.memory"),
        disk_threshold=_threshold(thresholds.get("disk"), "thresholds.disk"),
        webhook_env=webhook_env,
    )
