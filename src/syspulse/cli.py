"""Command-line interface for SysPulse."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from .config import load_config
from .health_checks import check_port, check_url
from .log_analyzer import analyze_log
from .metrics import breached_thresholds, collect_snapshot
from .notifications import notify_webhook
from .processes import top_processes
from .reporting import build_report


def _percentage(value: str) -> float:
    numeric = float(value)
    if not 0 <= numeric <= 100:
        raise argparse.ArgumentTypeError("threshold must be between 0 and 100")
    return numeric


def _positive_integer(value: str) -> int:
    numeric = int(value)
    if numeric < 1:
        raise argparse.ArgumentTypeError("value must be at least 1")
    return numeric


def _positive_float(value: str) -> float:
    numeric = float(value)
    if numeric <= 0:
        raise argparse.ArgumentTypeError("value must be greater than 0")
    return numeric


def _print(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False))
        return
    if "severity_counts" in payload:
        print(f"Log analysis: {payload['file']} ({payload['total_lines']} lines)")
        for severity, count in payload["severity_counts"].items():
            print(f"  {severity:<8} {count}")
        return
    if "processes" in payload:
        print(f"Top processes by {payload['sort_by']}:")
        print(f"  {'PID':>7}  {'CPU %':>7}  {'MEM %':>7}  {'STATUS':<10}  NAME")
        for process in payload["processes"]:
            print(f"  {process['pid']:>7}  {process['cpu_percent']:>7.2f}  {process['memory_percent']:>7.2f}  {process['status']:<10}  {process['name']}")
        return
    if "metrics" in payload:
        print(f"Report: {payload['file']} ({payload['snapshots']} snapshots; {payload['skipped_lines']} skipped)")
        print(f"Range: {payload['first_timestamp']} to {payload['last_timestamp']}")
        print(f"Snapshots with alerts: {payload['snapshots_with_alerts']}")
        for metric, summary in payload["metrics"].items():
            print(f"  {metric:<16} avg {summary['average']:>6.2f}%  min {summary['minimum']:>6.2f}%  max {summary['maximum']:>6.2f}%  peak {summary['peak_timestamp']}")
        return
    if "kind" in payload:
        status = "OK" if payload["available"] else "FAILED"
        print(f"{status}: {payload['kind']} {payload['target']} ({payload['latency_ms']:.2f} ms)")
        if payload.get("status_code") is not None:
            print(f"HTTP status: {payload['status_code']}")
        if payload.get("error"):
            print(f"Reason: {payload['error']}")
        return
    print(f"Timestamp: {payload['timestamp']}")
    print(f"CPU:    {payload['cpu_percent']:.1f}%")
    print(f"Memory: {payload['memory_percent']:.1f}% ({payload['memory_used_gb']:.2f}/{payload['memory_total_gb']:.2f} GiB)")
    print(f"Disk:   {payload['disk_percent']:.1f}% ({payload['disk_used_gb']:.2f}/{payload['disk_total_gb']:.2f} GiB on {payload['disk_path']})")
    if payload.get("alerts"):
        print("ALERT: " + ", ".join(f"{name}={value:.1f}%" for name, value in payload["alerts"].items()))
    if payload.get("notification_error"):
        print(f"Notification warning: {payload['notification_error']}")


def _snapshot_payload(args: argparse.Namespace) -> dict[str, Any]:
    snapshot = collect_snapshot(args.path, args.cpu_interval)
    payload: dict[str, Any] = snapshot.as_dict()
    payload["alerts"] = breached_thresholds(snapshot, cpu=args.cpu_threshold, memory=args.memory_threshold, disk=args.disk_threshold)
    if payload["alerts"]:
        notification_error = notify_webhook(args.webhook_env, {"event": "threshold_breached", "snapshot": payload})
        if notification_error:
            payload["notification_error"] = notification_error
    return payload


def _run_snapshot(args: argparse.Namespace) -> int:
    payload = _snapshot_payload(args)
    _print(payload, args.format)
    return 2 if args.fail_on_threshold and payload["alerts"] else 0


def _run_watch(args: argparse.Namespace) -> int:
    destination = Path(args.output) if args.output else None
    exit_code = 0
    for index in range(args.count):
        payload = _snapshot_payload(args)
        _print(payload, args.format)
        if destination:
            with destination.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(payload) + "\n")
        if args.fail_on_threshold and payload["alerts"]:
            exit_code = 2
        if index < args.count - 1:
            time.sleep(args.interval)
    return exit_code


def _run_analyze_logs(args: argparse.Namespace) -> int:
    try:
        payload = analyze_log(args.file, args.examples)
    except FileNotFoundError:
        print(f"error: log file not found: {args.file}", file=sys.stderr)
        return 1
    _print(payload, args.format)
    return 0


def _run_check_url(args: argparse.Namespace) -> int:
    payload = check_url(args.url, args.timeout, args.max_latency_ms)
    _print(payload, args.format)
    return 0 if payload["available"] else 2


def _run_check_port(args: argparse.Namespace) -> int:
    payload = check_port(args.host, args.port, args.timeout)
    _print(payload, args.format)
    return 0 if payload["available"] else 2


def _run_processes(args: argparse.Namespace) -> int:
    payload: dict[str, Any] = {"sort_by": args.sort, "processes": top_processes(args.sort, args.limit)}
    _print(payload, args.format)
    return 0


def _run_report(args: argparse.Namespace) -> int:
    try:
        payload = build_report(args.file)
    except FileNotFoundError:
        print(f"error: history file not found: {args.file}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    _print(payload, args.format)
    return 0


def _add_metric_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--path", default="/", help="filesystem path to measure (default: /)")
    parser.add_argument("--cpu-interval", type=float, default=0.2, help="CPU sample interval in seconds")
    parser.add_argument("--cpu-threshold", type=_percentage, help="alert at this CPU percentage")
    parser.add_argument("--memory-threshold", type=_percentage, help="alert at this memory percentage")
    parser.add_argument("--disk-threshold", type=_percentage, help="alert at this disk percentage")
    parser.add_argument("--webhook-env", help="environment variable containing an alert webhook URL")
    parser.add_argument("--fail-on-threshold", action="store_true", help="exit with code 2 when a threshold is breached")
    parser.add_argument("--format", choices=("text", "json"), default="text")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="syspulse", description="System health and log analysis from the command line.")
    parser.add_argument("--config", help="path to an optional SysPulse TOML configuration file")
    subcommands = parser.add_subparsers(dest="command", required=True)
    snapshot = subcommands.add_parser("snapshot", help="collect one system-health snapshot")
    _add_metric_options(snapshot)
    snapshot.set_defaults(handler=_run_snapshot)
    watch = subcommands.add_parser("watch", help="collect repeated snapshots")
    _add_metric_options(watch)
    watch.add_argument("--interval", type=float, default=5, help="seconds between snapshots")
    watch.add_argument("--count", type=_positive_integer, default=12, help="number of snapshots to collect")
    watch.add_argument("--output", help="append JSONL snapshots to this file")
    watch.set_defaults(handler=_run_watch)
    logs = subcommands.add_parser("analyze-logs", help="summarize severities in a text log")
    logs.add_argument("file", help="path to the log file")
    logs.add_argument("--examples", type=int, default=3, help="maximum example lines per severity")
    logs.add_argument("--format", choices=("text", "json"), default="text")
    logs.set_defaults(handler=_run_analyze_logs)
    check_url_command = subcommands.add_parser("check-url", help="check HTTP availability and response time")
    check_url_command.add_argument("url")
    check_url_command.add_argument("--timeout", type=_positive_float, default=5, help="request timeout in seconds")
    check_url_command.add_argument("--max-latency-ms", type=_positive_float, help="fail above this response time")
    check_url_command.add_argument("--format", choices=("text", "json"), default="text")
    check_url_command.set_defaults(handler=_run_check_url)
    check_port_command = subcommands.add_parser("check-port", help="check TCP connectivity")
    check_port_command.add_argument("host")
    check_port_command.add_argument("port", type=_positive_integer)
    check_port_command.add_argument("--timeout", type=_positive_float, default=5, help="connection timeout in seconds")
    check_port_command.add_argument("--format", choices=("text", "json"), default="text")
    check_port_command.set_defaults(handler=_run_check_port)
    processes = subcommands.add_parser("processes", help="show resource-heavy processes")
    processes.add_argument("--sort", choices=("cpu_percent", "memory_percent"), default="cpu_percent")
    processes.add_argument("--limit", type=_positive_integer, default=10, help="maximum process rows to return")
    processes.add_argument("--format", choices=("text", "json"), default="text")
    processes.set_defaults(handler=_run_processes)
    report = subcommands.add_parser("report", help="summarize JSONL history from `watch`")
    report.add_argument("file", help="JSONL history file created by `syspulse watch --output`")
    report.add_argument("--format", choices=("text", "json"), default="text")
    report.set_defaults(handler=_run_report)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
    except (FileNotFoundError, ValueError) as error:
        print(f"error: configuration error: {error}", file=sys.stderr)
        return 1
    if hasattr(args, "cpu_threshold"):
        args.cpu_threshold = args.cpu_threshold if args.cpu_threshold is not None else config.cpu_threshold
        args.memory_threshold = args.memory_threshold if args.memory_threshold is not None else config.memory_threshold
        args.disk_threshold = args.disk_threshold if args.disk_threshold is not None else config.disk_threshold
        args.webhook_env = args.webhook_env if args.webhook_env is not None else config.webhook_env
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
