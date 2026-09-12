import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from src import parser


class ParserTests(unittest.TestCase):
    def test_parse_log_file_counts_errors_and_warnings(self):
        with tempfile.TemporaryDirectory() as directory:
            log_file = Path(directory) / "service.log"
            log_file.write_text("INFO ready\nWARNING slow response\nERROR unavailable\nERROR retry failed\n")

            with redirect_stdout(io.StringIO()) as output:
                parser.parse_log_file(log_file)

        rendered = output.getvalue()
        self.assertIn("Talált hibák (ERROR): 2", rendered)
        self.assertIn("Talált figyelmeztetések (WARNING): 1", rendered)
