"""Summaries for JSONL histories produced by `syspulse watch`."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import fmean
from typing import Any

METRICS = ("cpu_percent", "memory_percent", "disk_percent")


def build_report(path: str | Path) -> dict[str, Any]:
    """Build a compact report, skipping malformed or incomplete JSONL records."""
    history_path = Path(path)
    snapshots: list[dict[str, Any]] = []
    skipped_lines = 0

    with history_path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                if not isinstance(record, dict) or any(not isinstance(record.get(metric), (int, float)) for metric in METRICS):
                    raise ValueError("missing metric")
            except (json.JSONDecodeError, ValueError):
                skipped_lines += 1
                continue
            snapshots.append(record)

    if not snapshots:
        raise ValueError("no valid SysPulse snapshots found")

    metrics: dict[str, dict[str, Any]] = {}
    for metric in METRICS:
        values = [float(snapshot[metric]) for snapshot in snapshots]
        peak_index = max(range(len(values)), key=values.__getitem__)
        metrics[metric] = {
            "average": round(fmean(values), 2),
            "minimum": round(min(values), 2),
            "maximum": round(max(values), 2),
            "peak_timestamp": snapshots[peak_index].get("timestamp"),
        }

    alert_count = sum(1 for snapshot in snapshots if snapshot.get("alerts"))
    return {
        "file": str(history_path),
        "snapshots": len(snapshots),
        "skipped_lines": skipped_lines,
        "first_timestamp": snapshots[0].get("timestamp"),
        "last_timestamp": snapshots[-1].get("timestamp"),
        "snapshots_with_alerts": alert_count,
        "metrics": metrics,
    }
