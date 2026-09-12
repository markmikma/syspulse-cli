from pathlib import Path


def parse_log_file(file_path):
    """Count common severity markers in a UTF-8 text log."""
    path = Path(file_path)
    error_count = 0
    warning_count = 0

    with path.open("r", encoding="utf-8") as log_file:
        for line in log_file:
            if "ERROR" in line:
                error_count += 1
            elif "WARNING" in line:
                warning_count += 1

    return {"file": str(path), "errors": error_count, "warnings": warning_count}


def format_log_summary(summary):
    return "\n".join(
        [
            f"=== Log summary: {summary['file']} ===",
            f"ERROR entries: {summary['errors']}",
            f"WARNING entries: {summary['warnings']}",
        ]
    )
