"""Dependency-free URL and TCP connectivity checks."""

from __future__ import annotations

import socket
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def check_url(url: str, timeout_seconds: float, max_latency_ms: float | None) -> dict[str, Any]:
    """Perform a GET request and return a script-friendly health result."""
    started = time.perf_counter()
    status_code: int | None = None
    error: str | None = None
    try:
        request = Request(url, method="GET", headers={"User-Agent": "SysPulse-CLI/0.1"})
        with urlopen(request, timeout=timeout_seconds) as response:
            status_code = response.status
    except HTTPError as exc:
        status_code = exc.code
        error = f"HTTP {exc.code}"
    except (URLError, ValueError, TimeoutError) as exc:
        error = str(exc.reason) if isinstance(exc, URLError) else str(exc)
    latency_ms = round((time.perf_counter() - started) * 1000, 2)
    latency_breached = max_latency_ms is not None and latency_ms > max_latency_ms
    available = error is None and status_code is not None and 200 <= status_code < 400 and not latency_breached
    return {"target": url, "kind": "url", "available": available, "status_code": status_code, "latency_ms": latency_ms, "max_latency_ms": max_latency_ms, "error": error or ("latency threshold exceeded" if latency_breached else None)}


def check_port(host: str, port: int, timeout_seconds: float) -> dict[str, Any]:
    """Test whether a TCP service accepts a connection."""
    started = time.perf_counter()
    error: str | None = None
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            pass
    except OSError as exc:
        error = str(exc)
    return {"target": f"{host}:{port}", "kind": "tcp", "available": error is None, "latency_ms": round((time.perf_counter() - started) * 1000, 2), "error": error}
