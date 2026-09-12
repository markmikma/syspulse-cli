import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src import monitor


class MonitorTests(unittest.TestCase):
    def test_collect_system_metrics_returns_resource_snapshot(self):
        memory = SimpleNamespace(total=8 * 1024**3, used=4 * 1024**3, percent=50.0)
        disk = SimpleNamespace(total=100 * 1024**3, percent=60.0)

        with (
            patch("src.monitor.psutil.cpu_percent", return_value=12.5),
            patch("src.monitor.psutil.virtual_memory", return_value=memory),
            patch("src.monitor.psutil.disk_usage", return_value=disk),
        ):
            metrics = monitor.collect_system_metrics()

        self.assertEqual(12.5, metrics["cpu_percent"])
        self.assertEqual(50.0, metrics["memory_percent"])
        self.assertEqual(60.0, metrics["disk_percent"])
