"""Interactive Rofi Bluetooth Manager for FreeBSD."""

from __future__ import annotations

import re
import shutil
import subprocess

from detech.freebsd.bluetooth import (
    get_bluetooth_status,
    get_known_bluetooth_devices,
    is_bluetooth_stack_active,
    scan_bluetooth_devices,
)
from detech.menus.rofi_runner import run_rofi_dmenu

MINIMALIST_SEPARATOR = "────────────────────────────"


def launch_bluetooth_terminal_wizard() -> None:
    """Launch the FreeBSD interactive `bluetooth-config scan` wizard in a Kitty window."""
    terminal = shutil.which("kitty") or shutil.which("alacritty") or "xterm"
    shell_cmd = (
        "echo '=== FreeBSD Bluetooth Device Setup Wizard ==='; "
        "echo 'Starting bluetooth-config scan...'; "
        "sudo bluetooth-config scan || doas bluetooth-config scan || su -m root -c 'bluetooth-config scan'; "
        "echo; "
        "read -p 'Press Enter to close...' dummy"
    )

    if shutil.which("kitty"):
        subprocess.Popen(
            [
                "kitty",
                "--title",
                "DETech Bluetooth Setup",
                "-o",
                "initial_window_width=800",
                "-o",
                "initial_window_height=500",
                "sh",
                "-c",
                shell_cmd,
            ]
        )
    else:
        subprocess.Popen([terminal, "-e", "sh", "-c", shell_cmd])


def open_bluetooth_menu() -> str | None:
    """Open interactive Rofi Bluetooth menu."""
    while True:
        status = get_bluetooth_status()
        is_active = status["active"]
        known_devs = get_known_bluetooth_devices()

        entries: list[str] = []

        if is_active:
            entries.append("󰂯  Status: Bluetooth Controller Active (ubt0)")
            entries.append("󰂯  Pair New Device (Interactive Wizard)")
            entries.append("󰑐  Scan for Nearby Devices (Inquiry)")
            entries.append(MINIMALIST_SEPARATOR)
        else:
            entries.append("󰂲  Status: Bluetooth Inactive (Click to start & pair)")
            entries.append("󰂯  Start Bluetooth & Pair Devices (Setup Wizard)")
            entries.append(MINIMALIST_SEPARATOR)

        if known_devs:
            entries.append("── Known / Configured Devices ──")
            for dev in known_devs:
                entries.append(f"󰂱  {dev['name']} ({dev['bdaddr']})")
        else:
            entries.append("(No known devices configured)")

        mesg = (
            f"FreeBSD Bluetooth: {'Active' if is_active else 'Inactive'} | Known Devices: {len(known_devs)}"
        )

        choice = run_rofi_dmenu(
            entries,
            prompt="󰂯  Bluetooth",
            mesg=mesg,
        )

        if not choice or choice.startswith("──") or choice.startswith("󰂯  Status:") or choice.startswith("󰂲  Status:"):
            return None

        if "Pair" in choice or "Start Bluetooth" in choice:
            launch_bluetooth_terminal_wizard()
            return "launched-wizard"

        if "Scan for Nearby Devices" in choice:
            scanned = scan_bluetooth_devices()
            scan_entries = [f"󰂱  {d['name']} ({d['bdaddr']})" for d in scanned]
            if not scan_entries:
                scan_entries = ["(No nearby devices discovered)"]

            dev_choice = run_rofi_dmenu(
                scan_entries,
                prompt="󰑐  Discovered Devices",
                mesg="Nearby Bluetooth devices found via inquiry",
            )
            if dev_choice and not dev_choice.startswith("("):
                launch_bluetooth_terminal_wizard()
                return "pairing-discovered"
            continue

        # If user selected a known device
        m = re.search(r"\(([0-9a-fA-F:]{17})\)", choice)
        if m:
            bdaddr = m.group(1)
            action_choice = run_rofi_dmenu(
                [
                    f"󰈀  Ping Device (l2ping {bdaddr})",
                    "󰂯  Pair / Re-configure in Setup Wizard",
                ],
                prompt=f"󰂱  {bdaddr}",
                mesg=f"Manage device: {choice}",
            )
            if action_choice and "Ping" in action_choice and shutil.which("l2ping"):
                terminal = shutil.which("kitty") or "xterm"
                subprocess.Popen([
                    terminal,
                    "--title",
                    f"Ping {bdaddr}",
                    "-e",
                    "sh",
                    "-c",
                    f"l2ping -c 4 {bdaddr}; echo; read -p 'Press Enter to exit...' dummy",
                ])
                return f"pinged-{bdaddr}"
            if action_choice and "Pair" in action_choice:
                launch_bluetooth_terminal_wizard()
                return "reconfigure-device"
            continue

        return choice
