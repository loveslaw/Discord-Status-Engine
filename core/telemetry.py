"""
System Telemetry Collector
Harvests live CPU, RAM, battery, uptime, and top process performance metrics.
"""

import time
from dataclasses import dataclass
from typing import Optional
import psutil


@dataclass
class SystemMetrics:
    cpu_percent: float
    cpu_cores: int
    ram_percent: float
    ram_used_gb: float
    ram_total_gb: float
    uptime_seconds: int
    battery_percent: Optional[int] = None
    top_process_name: Optional[str] = None

    @property
    def formatted_uptime(self) -> str:
        hours = self.uptime_seconds // 3600
        minutes = (self.uptime_seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def collect_metrics() -> SystemMetrics:
    """Collects real-time snapshot of system hardware metrics."""
    cpu_pct = psutil.cpu_percent(interval=None)
    cpu_count = psutil.cpu_count(logical=True) or 1

    vm = psutil.virtual_memory()
    ram_pct = vm.percent
    ram_used = round(vm.used / (1024 ** 3), 2)
    ram_total = round(vm.total / (1024 ** 3), 2)

    boot_time = psutil.boot_time()
    uptime_sec = int(time.time() - boot_time)

    batt_pct = None
    if hasattr(psutil, "sensors_battery"):
        batt = psutil.sensors_battery()
        if batt:
            batt_pct = int(batt.percent)

    top_proc = None
    try:
        procs = sorted(
            psutil.process_iter(["name", "cpu_percent"]),
            key=lambda p: p.info["cpu_percent"] or 0,
            reverse=True,
        )
        if procs and procs[0].info["name"]:
            top_proc = procs[0].info["name"]
    except Exception:
        pass

    return SystemMetrics(
        cpu_percent=cpu_pct,
        cpu_cores=cpu_count,
        ram_percent=ram_pct,
        ram_used_gb=ram_used,
        ram_total_gb=ram_total,
        uptime_seconds=uptime_sec,
        battery_percent=batt_pct,
        top_process_name=top_proc,
    )
