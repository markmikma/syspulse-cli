# SysPulse CLI

> A small Python utility for quick system checks and first-pass log triage on Linux and WSL.

SysPulse CLI is an operations-support project. It reports CPU, memory, and disk usage, and it summarises `ERROR` and `WARNING` messages in a text log. It supports readable terminal output and JSON output for simple automation.

## What it does

- Displays current CPU, RAM, and disk utilisation through `psutil`.
- Counts `ERROR` and `WARNING` entries in a text log.
- Offers `status` and `logs` subcommands with optional `--json` output.
- Runs locally on Linux/WSL or in a Docker container.
- Includes automated checks for the monitoring and log-parser output.

## Requirements

- Python 3.10 or newer
- `pip`
- Optional: Docker

## Run locally

```bash
git clone https://github.com/markmikma/syspulse-cli.git
cd syspulse-cli
python -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt

# Basic system snapshot
python src/syspulse.py status

# Inspect a specific filesystem path
python src/syspulse.py status --path /var

# Summarise a log file
python src/syspulse.py logs sample.log

# Produce JSON for a script or pipeline
python src/syspulse.py status --json
```

## Run with Docker

```bash
docker build -t syspulse-cli .
docker run --rm syspulse-cli
```

## Run the checks

```bash
python -m unittest discover -s tests -t . -v
```

The GitHub Actions workflow runs these checks on every push and pull request.

## Project structure

```text
src/
  monitor.py     # CPU, memory, and disk snapshot
  parser.py      # ERROR/WARNING log summary
tests/           # automated checks
sample.log       # safe example input
```

## Operational limits

This is a lightweight snapshot tool, not a replacement for a monitoring platform. It does not retain metrics, send alerts, or interpret root cause; it helps an operator get an initial view of system pressure and log severity quickly.
