# SysPulse CLI

[![CI](https://github.com/markmikma/syspulse-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/markmikma/syspulse-cli/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

`syspulse` is a lightweight, scriptable system-health and log-analysis CLI for local machines, servers, containers, and CI jobs. It turns one-off checks into structured snapshots, threshold-aware exit codes, JSON output, and JSONL history.

> **Use case:** find resource pressure, identify expensive processes, validate service availability, and make the result usable by a scheduler or CI pipeline.

## Features

- Collect CPU, memory, and filesystem snapshots on Windows, Linux, macOS, and containers.
- Emit human-readable output for operators or JSON for scripts and pipelines.
- Apply resource thresholds; return exit code `2` when a threshold is breached.
- Run repeated checks and append each structured result to a JSONL history file.
- Summarize `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL` entries in text logs.
- Package as an installable Python command and run in Docker.

## Quick start

Requires Python 3.10+.

```bash
git clone https://github.com/markmikma/syspulse-cli.git
cd syspulse-cli
python -m venv .venv
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
# Linux/macOS
# source .venv/bin/activate
pip install -e .

syspulse snapshot
```

Example output:

```text
Timestamp: 2026-09-13T11:22:24+00:00
CPU:    11.4%
Memory: 50.5% (7.96/15.78 GiB)
Disk:   88.5% (210.20/237.58 GiB on C:\)
```

### Automation-friendly health check

The command below emits JSON and fails with status `2` if any configured limit is reached. That makes it suitable for schedulers and CI checks.

```bash
syspulse snapshot --format json --cpu-threshold 85 --memory-threshold 90 --disk-threshold 90 --fail-on-threshold
```

### Reusable configuration and safe webhook alerts

Copy [`syspulse.example.toml`](syspulse.example.toml) to `syspulse.toml`, then provide it explicitly:

```bash
syspulse --config syspulse.toml snapshot --fail-on-threshold
```

Configuration can store thresholds and the *name* of the environment variable that holds a webhook URL. The secret URL itself is never written to the repository:

```bash
# PowerShell
$env:SYSPULSE_WEBHOOK_URL = "https://your-webhook.example/..."
syspulse --config syspulse.toml snapshot --fail-on-threshold
```

When a configured threshold is breached, SysPulse sends a JSON event to the webhook and records a delivery error in its output if notification fails.

### Capture a short history

```bash
syspulse watch --count 12 --interval 5 --output metrics.jsonl
```

`metrics.jsonl` contains one JSON object per measurement and can be consumed by Python, `jq`, or a log pipeline.

### Analyze a log

```bash
syspulse analyze-logs sample.log
syspulse analyze-logs /var/log/app.log --format json
```

### Check an external service

```bash
syspulse check-url https://example.com/health --max-latency-ms 500
syspulse check-port database.internal 5432 --timeout 3
```

Both checks produce JSON on request and use exit code `2` for an unavailable service or a latency breach, so they can be used in CI and scheduled jobs.

### Investigate resource-heavy processes

```bash
syspulse processes --sort memory_percent --limit 10
```

### Turn captured history into a report

```bash
syspulse report metrics.jsonl
syspulse report metrics.jsonl --format json
```

The report calculates per-metric averages, minimums, maximums, peak timestamps, and the number of snapshots that triggered alerts. Malformed JSONL lines are reported and skipped instead of making the historical report unusable.

## Docker

```bash
docker build -t syspulse-cli .
docker run --rm syspulse-cli snapshot
docker run --rm -v /:/host:ro syspulse-cli snapshot --path /host --format json
```

The host mount example is useful on Linux hosts. Container disk and process metrics otherwise describe the container itself.

## Commands

| Command | Purpose |
| --- | --- |
| `syspulse snapshot` | One resource snapshot; supports JSON and thresholds. |
| `syspulse watch` | Repeated snapshots, optional JSONL output. |
| `syspulse analyze-logs FILE` | Severity count and example extraction from a text log. |
| `syspulse check-url URL` | Check HTTP availability and response latency. |
| `syspulse check-port HOST PORT` | Check TCP service connectivity. |
| `syspulse processes` | Inspect the highest CPU- or memory-consuming processes. |
| `syspulse report FILE` | Summarize the JSONL history written by `watch`. |

## Design

```text
CLI commands
    ├── metrics + threshold evaluation ──→ JSON / JSONL / exit code
    ├── process inspection
    ├── URL and TCP health checks
    ├── log analysis + historical reports
    └── optional webhook notification
```

The core uses the standard library wherever possible. `psutil` supplies cross-platform host metrics; TOML configuration, HTTP checks, and webhook delivery are deliberately kept small and dependency-light.

## Repository layout

```text
src/syspulse/       Core CLI and monitoring modules
tests/              Unit tests for parsing, configuration, metrics, reports, and health checks
.github/workflows/  Continuous integration
syspulse.example.toml  Safe configuration template
```

## Development

```bash
python -m unittest discover -v
```

GitHub Actions runs linting, strict type checks, a coverage report, a CLI smoke test, and a Docker build on Python 3.10–3.12.

## Portfolio talking points

- Designed a cross-platform CLI around an explicit automation contract: stable JSON output and meaningful exit codes.
- Separated metric collection, alert evaluation, log parsing, and presentation to keep the core independently testable.
- Included container execution and time-series-friendly JSONL output, reflecting a practical operations workflow.
- Added CI across three Python versions, so every push and pull request validates the package and a real CLI invocation.
