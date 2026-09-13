import tempfile
import unittest
from pathlib import Path

from syspulse.config import load_config


class ConfigTests(unittest.TestCase):
    def test_loads_thresholds_and_webhook_environment_name(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "syspulse.toml"
            path.write_text(
                "[thresholds]\ncpu = 80\nmemory = 90\n[alerts]\nwebhook_env = 'SYSPULSE_WEBHOOK_URL'\n",
                encoding="utf-8",
            )
            config = load_config(str(path))

        self.assertEqual(config.cpu_threshold, 80.0)
        self.assertEqual(config.memory_threshold, 90.0)
        self.assertEqual(config.disk_threshold, None)
        self.assertEqual(config.webhook_env, "SYSPULSE_WEBHOOK_URL")

    def test_rejects_invalid_percentage(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "syspulse.toml"
            path.write_text("[thresholds]\ncpu = 101\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "between 0 and 100"):
                load_config(str(path))
