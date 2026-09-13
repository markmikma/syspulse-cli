"""Outbound alert delivery with secrets supplied only via environment variables."""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.request import Request, urlopen


def notify_webhook(webhook_env: str | None, event: dict[str, Any]) -> str | None:
    """Post a JSON alert when the configured environment variable is available."""
    if webhook_env is None:
        return None
    url = os.environ.get(webhook_env)
    if not url:
        return f"webhook environment variable {webhook_env!r} is not set"
    request = Request(url, data=json.dumps(event).encode("utf-8"), headers={"Content-Type": "application/json", "User-Agent": "SysPulse-CLI/0.1"}, method="POST")
    try:
        with urlopen(request, timeout=5) as response:
            if not 200 <= response.status < 300:
                return f"webhook returned HTTP {response.status}"
    except OSError as exc:
        return f"webhook delivery failed: {exc}"
    return None
