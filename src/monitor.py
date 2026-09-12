import psutil


def collect_system_metrics(path="/"):
    """Return a compact system snapshot suitable for human or JSON output."""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(path)
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_total_gb": round(memory.total / (1024**3), 2),
        "memory_used_gb": round(memory.used / (1024**3), 2),
        "memory_percent": memory.percent,
        "disk_path": path,
        "disk_total_gb": round(disk.total / (1024**3), 2),
        "disk_percent": disk.percent,
    }


def format_system_metrics(metrics):
    return "\n".join(
        [
            "=== SysPulse system snapshot ===",
            f"CPU usage: {metrics['cpu_percent']}%",
            f"Memory: {metrics['memory_percent']}% ({metrics['memory_used_gb']} / {metrics['memory_total_gb']} GB)",
            f"Disk ({metrics['disk_path']}): {metrics['disk_percent']}% ({metrics['disk_total_gb']} GB total)",
        ]
    )
