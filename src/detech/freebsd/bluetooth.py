"""FreeBSD Bluetooth Management Adapter (hccontrol, bthost, bluetooth-config)."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


def is_bluetooth_stack_active(node: str = "ubt0hci") -> bool:
    """Check if the FreeBSD Bluetooth Netgraph stack is active and responding."""
    if not shutil.which("hccontrol"):
        return False
    try:
        proc = subprocess.run(
            ["hccontrol", "-n", node, "read_bd_addr"],
            capture_output=True,
            text=True,
            check=False,
            timeout=1.0,
        )
        return proc.returncode == 0
    except Exception:
        return False


def get_known_bluetooth_devices() -> list[dict[str, str]]:
    """Parse known devices from `/etc/bluetooth/hosts`."""
    hosts_file = Path("/etc/bluetooth/hosts")
    devices: list[dict[str, str]] = []
    if not hosts_file.is_file():
        return devices

    try:
        content = hosts_file.read_text(encoding="utf-8", errors="replace")
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split(None, 1)
            if len(parts) >= 2 and re.match(r"^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$", parts[0]):
                devices.append({
                    "bdaddr": parts[0],
                    "name": parts[1].strip(),
                })
    except Exception:
        pass

    return devices


def scan_bluetooth_devices(node: str = "ubt0hci") -> list[dict[str, str]]:
    """Perform a Bluetooth inquiry scan using FreeBSD `hccontrol`."""
    if not is_bluetooth_stack_active(node):
        return []

    discovered: list[dict[str, str]] = []
    try:
        proc = subprocess.run(
            ["hccontrol", "-n", node, "inquiry"],
            capture_output=True,
            text=True,
            check=False,
            timeout=8.0,
        )
        if proc.returncode != 0:
            return []

        bdaddrs = re.findall(r"BD_ADDR:\s+([0-9a-fA-F:]{17})", proc.stdout)
        for addr in bdaddrs:
            name = ""
            if shutil.which("bthost"):
                try:
                    b_proc = subprocess.run(
                        ["bthost", "-b", addr],
                        capture_output=True,
                        text=True,
                        check=False,
                        timeout=1.0,
                    )
                    name = b_proc.stdout.strip()
                except Exception:
                    pass

            discovered.append({
                "bdaddr": addr,
                "name": name if name else "Unknown Device",
            })
    except Exception:
        pass

    return discovered


def get_bluetooth_status(node: str = "ubt0hci") -> dict[str, Any]:
    """Query Bluetooth status for Waybar telemetry and menus."""
    active = is_bluetooth_stack_active(node)
    known = get_known_bluetooth_devices()

    if active:
        return {
            "active": True,
            "node": node,
            "text": "󰂯",
            "tooltip": f"FreeBSD Bluetooth ({node}): Active & Ready\nKnown devices: {len(known)}\nClick to open Bluetooth Manager",
            "class": "on",
        }

    # Stack not yet active
    return {
        "active": False,
        "node": node,
        "text": "󰂲",
        "tooltip": f"FreeBSD Bluetooth ({node}): Inactive\nClick to launch Bluetooth Manager & Setup",
        "class": "off",
    }
