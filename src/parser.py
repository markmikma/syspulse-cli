"""Compatibility entry point. Prefer `syspulse analyze-logs FILE`."""

from syspulse.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["analyze-logs", "sample.log"]))
