"""Small command-line operations helper for system snapshots and log triage."""

import argparse
import json
from pathlib import Path

from monitor import collect_system_metrics, format_system_metrics
from parser import format_log_summary, parse_log_file


def build_parser():
    parser = argparse.ArgumentParser(description="SysPulse operations helper")
    subcommands = parser.add_subparsers(dest="command", required=True)

    status = subcommands.add_parser("status", help="show CPU, memory, and disk usage")
    status.add_argument("--path", default="/", help="filesystem path to inspect (default: /)")
    status.add_argument("--json", action="store_true", help="write machine-readable JSON")

    logs = subcommands.add_parser("logs", help="count ERROR and WARNING entries in a text log")
    logs.add_argument("file", type=Path, help="path to a UTF-8 text log")
    logs.add_argument("--json", action="store_true", help="write machine-readable JSON")
    return parser


def main():
    args = build_parser().parse_args()
    try:
        if args.command == "status":
            result = collect_system_metrics(args.path)
            output = json.dumps(result, indent=2) if args.json else format_system_metrics(result)
        else:
            result = parse_log_file(args.file)
            output = json.dumps(result, indent=2) if args.json else format_log_summary(result)
    except (FileNotFoundError, PermissionError, OSError) as error:
        raise SystemExit(f"SysPulse error: {error}") from error

    print(output)


if __name__ == "__main__":
    main()
