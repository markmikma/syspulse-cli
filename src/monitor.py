"""Compatibility entry point. Prefer `syspulse snapshot`."""

from syspulse.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["snapshot"]))
