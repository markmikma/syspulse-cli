import tempfile
import unittest
from pathlib import Path

from syspulse.log_analyzer import analyze_log


class LogAnalyzerTests(unittest.TestCase):
    def test_counts_all_supported_levels_case_insensitively(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "application.log"
            path.write_text("INFO ready\nwarning slow\nERROR failed\nERROR retry\nunknown\n", encoding="utf-8")
            result = analyze_log(path, example_limit=1)

        self.assertEqual(result["total_lines"], 5)
        self.assertEqual(result["severity_counts"]["INFO"], 1)
        self.assertEqual(result["severity_counts"]["WARNING"], 1)
        self.assertEqual(result["severity_counts"]["ERROR"], 2)
        self.assertEqual(result["severity_counts"]["CRITICAL"], 0)
        self.assertEqual(result["examples"]["ERROR"], ["ERROR failed"])
