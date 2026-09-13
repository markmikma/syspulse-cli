import json
import tempfile
import unittest
from pathlib import Path

from syspulse.reporting import build_report


class ReportingTests(unittest.TestCase):
    def test_calculates_summary_and_skips_invalid_jsonl(self):
        records = [
            {"timestamp": "2026-01-01T00:00:00Z", "cpu_percent": 10, "memory_percent": 20, "disk_percent": 30, "alerts": {}},
            "not json",
            {"timestamp": "2026-01-01T00:05:00Z", "cpu_percent": 50, "memory_percent": 40, "disk_percent": 35, "alerts": {"cpu_percent": 50}},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "metrics.jsonl"
            path.write_text("\n".join(json.dumps(record) if isinstance(record, dict) else record for record in records), encoding="utf-8")
            report = build_report(path)

        self.assertEqual(report["snapshots"], 2)
        self.assertEqual(report["skipped_lines"], 1)
        self.assertEqual(report["snapshots_with_alerts"], 1)
        self.assertEqual(report["metrics"]["cpu_percent"]["average"], 30.0)
        self.assertEqual(report["metrics"]["cpu_percent"]["peak_timestamp"], "2026-01-01T00:05:00Z")
