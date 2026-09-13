"""Process-level resource inspection."""

from __future__ import annotations

import time
from typing import Any

import psutil

VALID_SORTS = {"cpu_percent", "memory_percent"}


def top_processes(sort_by: str = "cpu_percent", limit: int = 10) -> list[dict[str, Any]]:
    """Return the highest resource-consuming visible processes.

    CPU percentages come from psutil's most recently available sample. A short
    interval is used before collecting so a standalone command is informative.
    """
    if sort_by not in VALID_SORTS:
        raise ValueError(f"sort_by must be one of: {', '.join(sorted(VALID_SORTS))}")
    if limit < 1:
        raise ValueError("limit must be at least 1")

    candidates = list(psutil.process_iter(["pid", "name", "memory_percent", "status"]))
    for process in candidates:
        try:
            process.cpu_percent(interval=None)
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
    time.sleep(0.1)

    processes: list[dict[str, Any]] = []
    for process in candidates:
        try:
            info = process.info
            processes.append(
                {
                    "pid": info["pid"],
                    "name": info["name"] or "<unknown>",
                    "status": info["status"] or "<unknown>",
                    "cpu_percent": round(process.cpu_percent(interval=None), 2),
                    "memory_percent": round(float(info["memory_percent"] or 0), 2),
                }
            )
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue

    return sorted(processes, key=lambda item: item[sort_by], reverse=True)[:limit]
