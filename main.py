"""
Discord-Status-Engine Runner
Author: loveslaw
"""

import argparse
import json
import os
import sys
import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.telemetry import collect_metrics
from core.presence import PresenceProfile, ProfileRotator
from core.ipc import DiscordIPCClient

console = Console()

BANNER = """[bold magenta]
  ███████╗████████╗ █████╗ ████████╗██╗   ██╗███████╗
  ██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██║   ██║██╔════╝
  ███████╗   ██║   ███████║   ██║   ██║   ██║███████╗
  ╚════██║   ██║   ██╔══██║   ██║   ██║   ██║╚════██║
  ███████║   ██║   ██║  ██║   ██║   ╚██████╔╝███████║
  ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝
[/bold magenta]
[dim cyan]  Real-Time Hardware Telemetry & Dynamic Rich Presence Synchronizer[/dim cyan]
[dim white]  Author: loveslaw | Version: 1.0.0[/dim white]
"""


def load_profiles(config_file: str = "config/profiles.json") -> tuple[str, int, list[PresenceProfile]]:
    if not os.path.exists(config_file):
        console.print(f"[bold red]Config file not found at {config_file}[/bold red]")
        sys.exit(1)

    with open(config_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    client_id = os.getenv("DISCORD_CLIENT_ID") or data.get("client_id", "1200000000000000000")
    rotation_sec = data.get("rotation_seconds", 15)

    profiles = []
    for p in data.get("profiles", []):
        profiles.append(
            PresenceProfile(
                name=p.get("name", "Custom"),
                details_template=p.get("details_template", "{cpu} | {ram}"),
                state_template=p.get("state_template", "Uptime: {uptime}"),
                large_image=p.get("large_image", "cpu_chip"),
                large_text=p.get("large_text", "Status Engine"),
                small_image=p.get("small_image"),
                small_text=p.get("small_text"),
                buttons=p.get("buttons", []),
            )
        )

    if not profiles:
        console.print("[bold red]No profiles defined in profiles.json![/bold red]")
        sys.exit(1)

    return client_id, rotation_sec, profiles


def main():
    console.print(BANNER)

    parser = argparse.ArgumentParser(description="Discord-Status-Engine - Live Telemetry RPC Daemon")
    parser.add_argument("--config", default="config/profiles.json", help="Path to profiles.json")
    parser.add_argument("--client-id", help="Discord Application Client ID override")
    parser.add_argument("--dry-run", action="store_true", help="Print presence telemetry locally without connecting to Discord")
    args = parser.parse_args()

    client_id, rotation_sec, profiles = load_profiles(args.config)
    if args.client_id:
        client_id = args.client_id

    rotator = ProfileRotator(profiles, rotation_seconds=rotation_sec)
    client = DiscordIPCClient(client_id)

    if not args.dry_run:
        console.print("[dim cyan]Connecting to local Discord Desktop IPC pipe...[/dim cyan]")
        connected = client.connect()
        if not connected:
            console.print("[bold yellow]⚠️ Could not connect to local Discord Desktop pipe (Discord not running).[/bold yellow]")
            console.print("[dim]Switching to Dry-Run Preview Mode...[/dim]\n")
            args.dry_run = True
        else:
            console.print("[bold green]✔ Successfully attached to Discord IPC pipe![/bold green]\n")

    start_time = int(time.time())

    try:
        while True:
            metrics = collect_metrics()
            active_profile = rotator.get_active_profile()
            activity = active_profile.build_activity(metrics, start_time=start_time)

            table = Table(title=f"Active Presence: {active_profile.name}", border_style="dim magenta", show_header=False)
            table.add_column("Key", style="bold cyan")
            table.add_column("Value", style="bold white")
            table.add_row("Details", activity.get("details", ""))
            table.add_row("State", activity.get("state", ""))
            table.add_row("CPU Load", f"{metrics.cpu_percent:.1f}% ({metrics.cpu_cores} Cores)")
            table.add_row("RAM Usage", f"{metrics.ram_percent:.1f}% ({metrics.ram_used_gb}/{metrics.ram_total_gb} GB)")
            table.add_row("Uptime", metrics.formatted_uptime)
            table.add_row("Top Process", metrics.top_process_name or "Idle")
            console.print(table)

            if not args.dry_run:
                client.set_activity(activity)

            time.sleep(5)
    except KeyboardInterrupt:
        console.print("\n[yellow]Disconnecting Discord-Status-Engine...[/yellow]")
        if not args.dry_run:
            client.clear_activity()
            client.close()
        console.print("[green]Daemon stopped cleanly.[/green]")


if __name__ == "__main__":
    main()
