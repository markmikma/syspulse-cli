"""System metric collection and threshold evaluation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import psutil


@dataclass(frozen=True)
class SystemSnapshot:
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    disk_path: str

    def as_dict(self) -> dict[str, float | str]:
        return asdict(self)


def collect_snapshot(path: str = "/", cpu_interval: float | None = 0.2) -> SystemSnapshot:
    """Collect one consistent snapshot of CPU, memory, and disk usage."""
    disk_path = str(Path(path).resolve())
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(disk_path)
    gib = 1024**3
    return SystemSnapshot(
        timestamp=datetime.now(UTC).isoformat(),
        cpu_percent=psutil.cpu_percent(interval=cpu_interval),
        memory_percent=memory.percent,
        memory_used_gb=round(memory.used / gib, 2),
        memory_total_gb=round(memory.total / gib, 2),
        disk_percent=disk.percent,
        disk_used_gb=round(disk.used / gib, 2),
        disk_total_gb=round(disk.total / gib, 2),
        disk_path=disk_path,
    )


def breached_thresholds(
    snapshot: SystemSnapshot, *, cpu: float | None, memory: float | None, disk: float | None
) -> dict[str, float]:
    """Return metrics that are at or above their optional percentage threshold."""
    configured = {
        "cpu_percent": (snapshot.cpu_percent, cpu),
        "memory_percent": (snapshot.memory_percent, memory),
        "disk_percent": (snapshot.disk_percent, disk),
    }
    return {
        name: value
        for name, (value, threshold) in configured.items()
        if threshold is not None and value >= threshold
    }
