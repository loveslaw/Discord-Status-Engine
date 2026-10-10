"""
Unit tests for System Telemetry Collector
"""

import pytest
from core.telemetry import collect_metrics, SystemMetrics


def test_collect_metrics_validity():
    metrics = collect_metrics()
    assert isinstance(metrics, SystemMetrics)
    assert 0.0 <= metrics.cpu_percent <= 100.0
    assert metrics.cpu_cores >= 1
    assert 0.0 <= metrics.ram_percent <= 100.0
    assert metrics.ram_used_gb > 0
    assert metrics.ram_total_gb > 0
    assert metrics.uptime_seconds >= 0


def test_formatted_uptime_string():
    metrics = SystemMetrics(
        cpu_percent=12.5,
        cpu_cores=8,
        ram_percent=45.0,
        ram_used_gb=7.2,
        ram_total_gb=16.0,
        uptime_seconds=7320,  # 2 hours 2 minutes
    )
    assert metrics.formatted_uptime == "2h 2m"
