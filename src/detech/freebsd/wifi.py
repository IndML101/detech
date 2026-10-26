"""FreeBSD Wi-Fi Management Adapter (ifconfig wlan list scan & wpa_cli)."""

from __future__ import annotations

import re
import shutil
import subprocess
from typing import Any


def detect_wifi_interface() -> str:
    """Detect the active or primary wireless interface (e.g. wlan0) on FreeBSD."""
    try:
        proc = subprocess.run(
            ["ifconfig"],
            capture_output=True,
            text=True,
            check=False,
            timeout=1.0,
        )
        if proc.returncode == 0:
            # Check for cloned wlan interfaces first (e.g. wlan0, wlan1)
            for line in proc.stdout.splitlines():
                m = re.match(r"^(wlan\d+):", line)
                if m:
                    return m.group(1)
            # Check for interfaces with groups: wlan or 802.11
            current_iface = None
            for line in proc.stdout.splitlines():
                m_if = re.match(r"^([a-zA-Z0-9_]+):\s+flags=", line)
                if m_if:
                    current_iface = m_if.group(1)
                elif current_iface and ("groups: wlan" in line or "IEEE 802.11" in line):
                    return current_iface
    except Exception:
        pass

    return "wlan0"


def dbm_to_percentage(dbm: int) -> int:
    """Approximate Wi-Fi signal percentage from RSSI dBm (-100 dBm to -50 dBm)."""
    return max(0, min(100, int(2 * (dbm + 100))))


def get_signal_icon(pct: int) -> str:
    """Return appropriate Nerd Font Wi-Fi signal icon based on percentage."""
    if pct >= 75:
        return "󰤨"
    if pct >= 50:
        return "󰤥"
    if pct >= 25:
        return "󰤢"
    return "󰤟"


def get_wifi_status(iface: str | None = None) -> dict[str, Any]:
    """Query current Wi-Fi status on FreeBSD using `ifconfig` and `wpa_cli`."""
    interface = iface or detect_wifi_interface()
    info: dict[str, Any] = {
        "interface": interface,
        "connected": False,
        "ssid": "",
        "bssid": "",
        "ip": "",
        "channel": "",
        "signal_pct": 0,
        "status": "disconnected",
    }

    try:
        proc = subprocess.run(
            ["ifconfig", interface],
            capture_output=True,
            text=True,
            check=False,
            timeout=1.0,
        )
        if proc.returncode == 0:
            output = proc.stdout
            m_ip = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)", output)
            if m_ip:
                info["ip"] = m_ip.group(1)

            m_ssid = re.search(r"ssid\s+(\S+)", output)
            if m_ssid:
                info["ssid"] = m_ssid.group(1).strip('"')

            m_bssid = re.search(r"bssid\s+([0-9a-fA-F:]{17})", output)
            if m_bssid:
                info["bssid"] = m_bssid.group(1)

            m_chan = re.search(r"channel\s+(\d+)", output)
            if m_chan:
                info["channel"] = m_chan.group(1)

            m_status = re.search(r"status:\s+(\w+)", output)
            if m_status:
                info["status"] = m_status.group(1)
                if info["status"] == "associated" and info["ssid"]:
                    info["connected"] = True
    except Exception:
        pass

    return info


def scan_wifi_networks(iface: str | None = None) -> list[dict[str, Any]]:
    """Scan nearby Wi-Fi networks using FreeBSD `ifconfig <iface> list scan`."""
    interface = iface or detect_wifi_interface()
    networks: dict[str, dict[str, Any]] = {}

    try:
        proc = subprocess.run(
            ["ifconfig", interface, "list", "scan"],
            capture_output=True,
            text=True,
            check=False,
            timeout=8.0,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return []

        pattern = re.compile(
            r"^(.*?)\s+([0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5})\s+(\d+)\s+(\S+)\s+([-\d]+:[-\d]+)\s+(\d+)\s+(.*)$"
        )

        for line in proc.stdout.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("SSID/MESH"):
                continue

            m = pattern.match(line)
            if not m:
                continue

            ssid = m.group(1).strip()
            if not ssid:
                continue  # Hidden SSID

            bssid = m.group(2)
            chan = m.group(3)
            rate = m.group(4)
            sn_str = m.group(5)
            caps = m.group(7)

            try:
                sig_dbm = int(sn_str.split(":")[0])
            except ValueError:
                sig_dbm = -80

            pct = dbm_to_percentage(sig_dbm)
            encrypted = "RSN" in caps or "WPA" in caps
            security = "WPA2" if "RSN" in caps else ("WPA" if "WPA" in caps else "Open")

            # Deduplicate by SSID, keep highest signal
            if ssid not in networks or pct > networks[ssid]["signal_pct"]:
                networks[ssid] = {
                    "ssid": ssid,
                    "bssid": bssid,
                    "channel": chan,
                    "rate": rate,
                    "signal_dbm": sig_dbm,
                    "signal_pct": pct,
                    "signal_icon": get_signal_icon(pct),
                    "encrypted": encrypted,
                    "security": security,
                    "lock_icon": "󰌾" if encrypted else "󰌿",
                    "caps": caps,
                }
    except Exception:
        pass

    # Sort networks by signal strength descending
    sorted_nets = sorted(networks.values(), key=lambda n: n["signal_pct"], reverse=True)
    return sorted_nets


def get_saved_networks(iface: str | None = None) -> list[dict[str, str]]:
    """Query known networks from `wpa_cli list_networks`."""
    interface = iface or detect_wifi_interface()
    saved: list[dict[str, str]] = []
    if not shutil.which("wpa_cli"):
        return saved

    try:
        proc = subprocess.run(
            ["wpa_cli", "-i", interface, "list_networks"],
            input="",
            capture_output=True,
            text=True,
            check=False,
            timeout=2.0,
        )
        if proc.returncode == 0:
            for line in proc.stdout.splitlines():
                parts = line.split("\t")
                if len(parts) >= 2 and parts[0].strip().isdigit():
                    saved.append({
                        "id": parts[0].strip(),
                        "ssid": parts[1].strip(),
                        "flags": parts[3].strip() if len(parts) >= 4 else "",
                    })
    except Exception:
        pass

    return saved


def connect_wifi_network(
    ssid: str,
    password: str | None = None,
    iface: str | None = None,
) -> tuple[bool, str]:
    """Connect to a Wi-Fi network on FreeBSD using `wpa_cli`."""
    interface = iface or detect_wifi_interface()
    if not shutil.which("wpa_cli"):
        return False, "wpa_cli is not available"

    saved = get_saved_networks(interface)
    matching = next((item for item in saved if item["ssid"] == ssid), None)

    try:
        if matching:
            net_id = matching["id"]
        else:
            add_proc = subprocess.run(
                ["wpa_cli", "-i", interface, "add_network"],
                capture_output=True,
                text=True,
                check=False,
                timeout=2.0,
            )
            net_id = add_proc.stdout.strip()
            if not net_id.isdigit():
                return False, f"Failed to allocate network id: {net_id}"

            subprocess.run(
                ["wpa_cli", "-i", interface, "set_network", net_id, "ssid", f'"{ssid}"'],
                check=False,
                capture_output=True,
                timeout=2.0,
            )
            if password:
                subprocess.run(
                    ["wpa_cli", "-i", interface, "set_network", net_id, "psk", f'"{password}"'],
                    check=False,
                    capture_output=True,
                    timeout=2.0,
                )
            else:
                subprocess.run(
                    ["wpa_cli", "-i", interface, "set_network", net_id, "key_mgmt", "NONE"],
                    check=False,
                    capture_output=True,
                    timeout=2.0,
                )

        # Enable and select network
        subprocess.run(
            ["wpa_cli", "-i", interface, "enable_network", net_id],
            check=False,
            capture_output=True,
            timeout=2.0,
        )
        subprocess.run(
            ["wpa_cli", "-i", interface, "select_network", net_id],
            check=False,
            capture_output=True,
            timeout=2.0,
        )
        subprocess.run(
            ["wpa_cli", "-i", interface, "reassociate"],
            check=False,
            capture_output=True,
            timeout=2.0,
        )

        # Trigger desktop notification
        if shutil.which("notify-send"):
            try:
                subprocess.Popen(
                    [
                        "notify-send",
                        "-a",
                        "DETech Wi-Fi",
                        "-i",
                        "network-wireless",
                        f"Connecting to {ssid}...",
                        f"Interface {interface} associating",
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                pass

        return True, f"Connecting to {ssid} (Network #{net_id})"
    except Exception as e:
        return False, str(e)


def disconnect_wifi(iface: str | None = None) -> tuple[bool, str]:
    """Disconnect current Wi-Fi association on FreeBSD."""
    interface = iface or detect_wifi_interface()
    if not shutil.which("wpa_cli"):
        return False, "wpa_cli is not available"

    try:
        subprocess.run(
            ["wpa_cli", "-i", interface, "disconnect"],
            check=False,
            capture_output=True,
            timeout=2.0,
        )
        if shutil.which("notify-send"):
            try:
                subprocess.Popen(
                    [
                        "notify-send",
                        "-a",
                        "DETech Wi-Fi",
                        "-i",
                        "network-wireless-disconnected",
                        "Wi-Fi Disconnected",
                        f"Disconnected from {interface}",
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                pass
        return True, "Disconnected"
    except Exception as e:
        return False, str(e)
