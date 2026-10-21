"""FreeBSD ACPI Battery, Thermal, and Power Management (`sysctl hw.acpi`, `acpiconf`)."""

from __future__ import annotations

import json
import re
import subprocess
from typing import Any


def query_sysctl(oid: str) -> str:
    """Query a FreeBSD sysctl OID and return stripped stdout."""
    proc = subprocess.run(
        ["sysctl", "-n", oid],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.stdout.strip()


def get_battery_status() -> dict[str, Any]:
    """Query FreeBSD ACPI battery life and state via `sysctl hw.acpi.battery`."""
    life_raw = query_sysctl("hw.acpi.battery.life")
    state_raw = query_sysctl("hw.acpi.battery.state")

    try:
        capacity = int(life_raw)
    except ValueError:
        capacity = 100

    try:
        state_code = int(state_raw)
    except ValueError:
        state_code = 0

    # FreeBSD ACPI battery state bitmask: 0=AC/Full, 1=Discharging, 2=Charging, 4=Critical
    if state_code == 2:
        status = "Charging"
        icon = "󰂄"
    elif state_code & 4:
        status = "Critical"
        icon = "󰂃"
    elif state_code == 1:
        status = "Discharging"
        icon = "󰁹" if capacity > 80 else ("󰁾" if capacity > 40 else "󰁻")
    else:
        status = "Plugged"
        icon = "󰚥"

    return {
        "capacity": max(0, min(100, capacity)),
        "status": status,
        "icon": icon,
        "text": f"{icon} {capacity}%",
        "tooltip": f"FreeBSD ACPI Battery: {capacity}% ({status})",
        "class": status.lower(),
    }


def get_thermal_status(oid: str = "hw.acpi.thermal.tz0.temperature") -> dict[str, Any]:
    """Query FreeBSD CPU/ACPI temperature via sysctl."""
    raw = query_sysctl(oid)
    if not raw:
        raw = query_sysctl("dev.cpu.0.temperature")
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)", raw)
    temp_c = float(m.group(1)) if m else 42.0
    icon = "" if temp_c >= 75 else ("" if temp_c >= 55 else "")
    return {
        "temperature_c": temp_c,
        "text": f"{icon} {int(round(temp_c))}°C",
        "tooltip": f"FreeBSD Thermal Sensor ({oid}): {temp_c:.1f}°C",
        "class": "critical" if temp_c >= 80 else "normal",
    }


def build_power_command(action: str, privilege_cmd: str = "doas") -> list[str]:
    """Build FreeBSD power/session management command."""
    if action == "lock":
        return ["hyprlock"]
    if action == "suspend":
        return [privilege_cmd, "acpiconf", "-s", "3"]
    if action == "reboot":
        return [privilege_cmd, "shutdown", "-r", "now"]
    if action == "poweroff":
        return [privilege_cmd, "shutdown", "-p", "now"]
    if action == "logout":
        return ["hyprctl", "dispatch", "exit"]
    raise ValueError(f"Unsupported FreeBSD power action: {action!r}")


def format_waybar_json(payload: dict[str, Any]) -> str:
    """Serialize status dictionary as single-line JSON for Waybar custom modules."""
    return json.dumps(payload)
