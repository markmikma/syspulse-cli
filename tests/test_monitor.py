import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from src import monitor


class MonitorTests(unittest.TestCase):
    def test_check_system_prints_resource_snapshot(self):
        memory = SimpleNamespace(total=8 * 1024**3, used=4 * 1024**3, percent=50.0)
        disk = SimpleNamespace(total=100 * 1024**3, percent=60.0)

        with (
            patch("src.monitor.psutil.cpu_percent", return_value=12.5),
            patch("src.monitor.psutil.virtual_memory", return_value=memory),
            patch("src.monitor.psutil.disk_usage", return_value=disk),
            redirect_stdout(io.StringIO()) as output,
        ):
            monitor.check_system()

        rendered = output.getvalue()
        self.assertIn("CPU Terhelés: 12.5%", rendered)
        self.assertIn("RAM Használt: 50.0%", rendered)
        self.assertIn("Lemez Használt: 60.0%", rendered)
