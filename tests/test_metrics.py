import unittest

from syspulse.metrics import SystemSnapshot, breached_thresholds


class MetricTests(unittest.TestCase):
    def test_only_configured_breaches_are_returned(self):
        snapshot = SystemSnapshot("now", 87.0, 72.0, 4.0, 8.0, 91.0, 9.1, 10.0, "/")
        alerts = breached_thresholds(snapshot, cpu=80, memory=80, disk=90)
        self.assertEqual(alerts, {"cpu_percent": 87.0, "disk_percent": 91.0})
