"""Lightweight, dependency-free analysis for text logs."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

SEVERITY_PATTERN = re.compile(r"\b(DEBUG|INFO|WARNING|ERROR|CRITICAL)\b", re.IGNORECASE)


def analyze_log(path: str | Path, example_limit: int = 3) -> dict[str, object]:
    """Count standard severity tokens and retain a few actionable log lines."""
    log_path = Path(path)
    counts: Counter[str] = Counter()
    examples: dict[str, list[str]] = defaultdict(list)
    total_lines = 0

    with log_path.open("r", encoding="utf-8", errors="replace") as stream:
        for line in stream:
            total_lines += 1
            match = SEVERITY_PATTERN.search(line)
            if not match:
                continue
            severity = match.group(1).upper()
            counts[severity] += 1
            if len(examples[severity]) < example_limit:
                examples[severity].append(line.rstrip())

    return {
        "file": str(log_path),
        "total_lines": total_lines,
        "severity_counts": {level: counts[level] for level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")},
        "examples": dict(examples),
    }
