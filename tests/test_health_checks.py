import unittest
from unittest.mock import patch

from syspulse.health_checks import check_url


class FakeResponse:
    status = 204

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class HealthCheckTests(unittest.TestCase):
    @patch("syspulse.health_checks.urlopen", return_value=FakeResponse())
    def test_url_check_reports_success(self, mocked_urlopen):
        result = check_url("https://example.test/health", timeout_seconds=2, max_latency_ms=1000)
        self.assertTrue(result["available"])
        self.assertEqual(result["status_code"], 204)
        mocked_urlopen.assert_called_once()
