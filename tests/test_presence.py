"""
Unit tests for Rich Presence Builder & Profile Rotator
"""

import pytest
from core.telemetry import SystemMetrics
from core.presence import PresenceProfile, ProfileRotator


def test_presence_activity_interpolation():
    profile = PresenceProfile(
        name="Test Profile",
        details_template="CPU: {cpu} | RAM: {ram}",
        state_template="Up: {uptime} | Proc: {top_proc}",
        large_image="server_rack",
        large_text="Custom Server",
        buttons=[{"label": "Website", "url": "https://example.com"}],
    )

    metrics = SystemMetrics(
        cpu_percent=25.4,
        cpu_cores=16,
        ram_percent=60.0,
        ram_used_gb=9.6,
        ram_total_gb=16.0,
        uptime_seconds=3600,
        battery_percent=88,
        top_process_name="Code.exe",
    )

    activity = profile.build_activity(metrics, start_time=1700000000)

    assert activity["details"] == "CPU: 25.4% | RAM: 60.0%"
    assert activity["state"] == "Up: 1h 0m | Proc: Code.exe"
    assert activity["assets"]["large_image"] == "server_rack"
    assert len(activity["buttons"]) == 1
    assert activity["buttons"][0]["label"] == "Website"


def test_profile_rotator_cycling():
    p1 = PresenceProfile("P1", "d1", "s1")
    p2 = PresenceProfile("P2", "d2", "s2")

    rotator = ProfileRotator([p1, p2], rotation_seconds=0)  # instant rotation
    assert rotator.get_active_profile().name == "P1"
    # Calling again after elapsed time triggers rotation
    assert rotator.get_active_profile().name == "P2"
    assert rotator.get_active_profile().name == "P1"
