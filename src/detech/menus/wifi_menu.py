"""Interactive Rofi Wi-Fi Picker and Connection Manager for FreeBSD."""

from __future__ import annotations

import re
import shutil
import subprocess
from typing import Any

from detech.freebsd.wifi import (
    connect_wifi_network,
    detect_wifi_interface,
    disconnect_wifi,
    get_saved_networks,
    get_wifi_status,
    scan_wifi_networks,
)
from detech.menus.rofi_runner import run_rofi_dmenu

MINIMALIST_SEPARATOR = "────────────────────────────"


def open_wifi_menu() -> str | None:
    """Open interactive Rofi Wi-Fi network picker and manager."""
    iface = detect_wifi_interface()

    while True:
        status = get_wifi_status(iface)
        current_ssid = status.get("ssid", "")
        is_connected = bool(status.get("connected", False))
        ip_addr = status.get("ip", "")

        saved_nets = {item["ssid"]: item["id"] for item in get_saved_networks(iface)}
        scanned = scan_wifi_networks(iface)

        entries: list[str] = []

        if is_connected and current_ssid:
            status_line = f"󰤨  Connected: {current_ssid} ({ip_addr})" if ip_addr else f"󰤨  Connected: {current_ssid}"
            entries.append(status_line)
            entries.append(f"󰖩  Disconnect from {current_ssid}")
            entries.append("󰑐  Rescan Wi-Fi Networks")
            entries.append(MINIMALIST_SEPARATOR)
        else:
            entries.append("󰖩  Status: Disconnected")
            entries.append("󰑐  Rescan Wi-Fi Networks")
            entries.append(MINIMALIST_SEPARATOR)

        network_map: dict[str, dict[str, Any]] = {}
        for net in scanned:
            ssid = net["ssid"]
            network_map[ssid] = net
            icon = net["signal_icon"]
            lock = net["lock_icon"]
            pct = net["signal_pct"]

            if ssid == current_ssid and is_connected:
                label = f"{icon}  {lock}  {ssid}  [Active]"
            elif ssid in saved_nets:
                label = f"{icon}  {lock}  {ssid}  [Saved • {pct}%]"
            elif net["encrypted"]:
                label = f"{icon}  {lock}  {ssid}  [{net['security']} • {pct}%]"
            else:
                label = f"{icon}  {lock}  {ssid}  [Open • {pct}%]"

            entries.append(label)

        if not scanned:
            entries.append("(No Wi-Fi networks found)")

        mesg = (
            f"Interface: {iface} | Connected to {current_ssid} ({ip_addr})"
            if is_connected
            else f"Interface: {iface} | Disconnected"
        )

        choice = run_rofi_dmenu(
            entries,
            prompt="󰤨  Wi-Fi",
            mesg=mesg,
        )

        if not choice:
            return None

        if "Rescan" in choice:
            continue

        if "Disconnect" in choice:
            disconnect_wifi(iface)
            return "disconnected"

        if choice.startswith("󰤨  Connected:") or choice.startswith("󰖩  Status:") or choice.startswith("─"):
            continue

        if choice == "(No Wi-Fi networks found)":
            continue

        # Extract SSID from selected line
        # Format is "<icon>  <lock>  <SSID>  [...]"
        m = re.search(r"^\S+\s+\S+\s+(.*?)\s+\[", choice)
        selected_ssid = m.group(1).strip() if m else None

        if not selected_ssid:
            continue

        # If already connected to this SSID
        if selected_ssid == current_ssid and is_connected:
            action_choice = run_rofi_dmenu(
                [
                    f"󰖩  Disconnect from {selected_ssid}",
                    f"󰑐  Reconnect to {selected_ssid}",
                ],
                prompt=f"󰤨  {selected_ssid}",
                mesg=f"Currently active on {iface} with IP {ip_addr}",
            )
            if not action_choice:
                continue
            if "Disconnect" in action_choice:
                disconnect_wifi(iface)
                return "disconnected"
            if "Reconnect" in action_choice:
                connect_wifi_network(selected_ssid, iface=iface)
                return f"reconnected-{selected_ssid}"
            continue

        net_info = network_map.get(selected_ssid, {})
        is_encrypted = bool(net_info.get("encrypted", True))
        is_saved = selected_ssid in saved_nets

        password: str | None = None
        if is_encrypted and not is_saved:
            pass_choice = run_rofi_dmenu(
                [],
                prompt=f"󰌾  Password for {selected_ssid}",
                mesg=f"Enter WPA/WPA2 passphrase for network: {selected_ssid}",
                password=True,
            )
            if not pass_choice:
                continue  # User cancelled password entry
            password = pass_choice

        ok, msg = connect_wifi_network(selected_ssid, password=password, iface=iface)
        return f"connected-{selected_ssid}" if ok else f"error-{msg}"
