"""
Rich Presence Payload Builder & Profile Rotation Engine
Formats dynamic system telemetry into Discord RPC activity structures.
"""

import time
from typing import Any, Dict, List, Optional
from core.telemetry import SystemMetrics


class PresenceProfile:
    def __init__(
        self,
        name: str,
        details_template: str,
        state_template: str,
        large_image: str = "cpu_chip",
        large_text: str = "Discord-Status-Engine",
        small_image: Optional[str] = "python_icon",
        small_text: Optional[str] = "Python 3.12 Engine",
        buttons: Optional[List[Dict[str, str]]] = None,
    ):
        self.name = name
        self.details_template = details_template
        self.state_template = state_template
        self.large_image = large_image
        self.large_text = large_text
        self.small_image = small_image
        self.small_text = small_text
        self.buttons = buttons or []

    def build_activity(self, metrics: SystemMetrics, start_time: Optional[int] = None) -> Dict[str, Any]:
        """Interpolates telemetry metrics into Discord activity payload."""
        variables = {
            "cpu": f"{metrics.cpu_percent:.1f}%",
            "cores": metrics.cpu_cores,
            "ram": f"{metrics.ram_percent:.1f}%",
            "ram_gb": f"{metrics.ram_used_gb} / {metrics.ram_total_gb} GB",
            "uptime": metrics.formatted_uptime,
            "top_proc": metrics.top_process_name or "System Idle",
            "battery": f"{metrics.battery_percent}%" if metrics.battery_percent is not None else "AC Power",
        }

        # Safe format substitution
        details = self.details_template
        state = self.state_template
        for k, v in variables.items():
            details = details.replace(f"{{{k}}}", str(v))
            state = state.replace(f"{{{k}}}", str(v))

        activity: Dict[str, Any] = {
            "details": details[:128],
            "state": state[:128],
            "timestamps": {"start": start_time or int(time.time() - metrics.uptime_seconds)},
            "assets": {
                "large_image": self.large_image,
                "large_text": self.large_text,
            },
        }

        if self.small_image:
            activity["assets"]["small_image"] = self.small_image
            activity["assets"]["small_text"] = self.small_text

        if self.buttons:
            # Discord limits RPC to 2 buttons
            valid_buttons = []
            for b in self.buttons[:2]:
                if "label" in b and "url" in b:
                    valid_buttons.append({"label": b["label"][:32], "url": b["url"]})
            if valid_buttons:
                activity["buttons"] = valid_buttons

        return activity


class ProfileRotator:
    def __init__(self, profiles: List[PresenceProfile], rotation_seconds: int = 20):
        if not profiles:
            raise ValueError("Must provide at least one PresenceProfile.")
        self.profiles = profiles
        self.rotation_seconds = rotation_seconds
        self.current_index = 0
        self.last_rotation = time.time()
        self._first_call = True

    def get_active_profile(self) -> PresenceProfile:
        now = time.time()
        if self._first_call:
            self._first_call = False
            self.last_rotation = now
            return self.profiles[self.current_index]

        if now - self.last_rotation >= self.rotation_seconds:
            self.current_index = (self.current_index + 1) % len(self.profiles)
            self.last_rotation = now
        return self.profiles[self.current_index]
