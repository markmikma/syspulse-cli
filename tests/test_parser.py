import tempfile
import unittest
from pathlib import Path

from src import parser


class ParserTests(unittest.TestCase):
    def test_parse_log_file_counts_errors_and_warnings(self):
        with tempfile.TemporaryDirectory() as directory:
            log_file = Path(directory) / "service.log"
            log_file.write_text("INFO ready\nWARNING slow response\nERROR unavailable\nERROR retry failed\n")

            summary = parser.parse_log_file(log_file)

        self.assertEqual(2, summary["errors"])
        self.assertEqual(1, summary["warnings"])
