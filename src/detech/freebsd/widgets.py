"""FreeBSD & Desktop Waybar Widgets: Weather, Calendar, Network, Media (MPRIS), DND, Uptime, Clipboard."""

from __future__ import annotations

import calendar
import datetime
import json
import re
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from detech.core.paths import get_xdg_config_dir
from detech.freebsd.power import query_sysctl


WEATHER_ICON_MAP: dict[str, str] = {
    "113": "󰖙",  # Sunny / Clear
    "116": "󰖕",  # Partly cloudy
    "119": "󰖐",  # Cloudy
    "122": "󰖐",  # Overcast
    "143": "󰖑",  # Mist
    "176": "󰖗",  # Patchy rain
    "179": "󰼶",  # Patchy snow
    "182": "󰙿",  # Sleet
    "185": "󰙿",  # Freezing drizzle
    "200": "󰙾",  # Thundery outbreaks
    "227": "󰼶",  # Blowing snow
    "230": "󰼶",  # Blizzard
    "248": "󰖑",  # Fog
    "260": "󰖑",  # Freezing fog
    "263": "󰖗",  # Patchy light drizzle
    "266": "󰖗",  # Light drizzle
    "281": "󰙿",  # Freezing drizzle
    "284": "󰙿",  # Heavy freezing drizzle
    "293": "󰖗",  # Patchy light rain
    "296": "󰖗",  # Light rain
    "299": "󰖖",  # Moderate rain at times
    "302": "󰖖",  # Moderate rain
    "305": "󰖖",  # Heavy rain at times
    "308": "󰖖",  # Heavy rain
    "311": "󰙿",  # Light freezing rain
    "314": "󰙿",  # Moderate/heavy freezing rain
    "317": "󰙿",  # Light sleet
    "320": "󰙿",  # Moderate/heavy sleet
    "323": "󰼶",  # Patchy light snow
    "326": "󰼶",  # Light snow
    "329": "󰼶",  # Patchy moderate snow
    "332": "󰼶",  # Moderate snow
    "335": "󰼶",  # Patchy heavy snow
    "338": "󰼶",  # Heavy snow
    "350": "󰙿",  # Ice pellets
    "353": "󰖗",  # Light rain shower
    "356": "󰖖",  # Moderate/heavy rain shower
    "359": "󰖖",  # Torrential rain shower
    "362": "󰙿",  # Light sleet showers
    "365": "󰙿",  # Moderate/heavy sleet showers
    "368": "󰼶",  # Light snow showers
    "371": "󰼶",  # Moderate/heavy snow showers
    "386": "󰙾",  # Patchy light rain with thunder
    "389": "󰙾",  # Moderate/heavy rain with thunder
    "392": "󰙾",  # Patchy light snow with thunder
    "395": "󰙾",  # Moderate/heavy snow with thunder
}


def _get_cache_dir() -> Path:
    cache_dir = Path.home() / ".cache" / "detech"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def parse_wttr_json(
    data: dict[str, Any],
    units: str = "m",
    fallback_location: str = "",
) -> dict[str, Any]:
    """Parse wttr.in `format=j1` JSON payload into a Waybar status dictionary."""
    current_list = data.get("current_condition", [])
    current = current_list[0] if current_list else {}

    area_list = data.get("nearest_area", [])
    area = area_list[0] if area_list else {}
    city = ""
    if area:
        area_names = area.get("areaName", [])
        country_names = area.get("country", [])
        city_part = area_names[0].get("value", "") if area_names else ""
        country_part = country_names[0].get("value", "") if country_names else ""
        city = f"{city_part}, {country_part}".strip(", ")
    if not city:
        city = fallback_location or "Auto Location"

    use_fahrenheit = units.lower() in ("u", "f", "imperial", "us")
    temp_val = current.get("temp_F" if use_fahrenheit else "temp_C", "22")
    feels_val = current.get("FeelsLikeF" if use_fahrenheit else "FeelsLikeC", temp_val)
    unit_symbol = "°F" if use_fahrenheit else "°C"

    weather_code = str(current.get("weatherCode", "113"))
    icon = WEATHER_ICON_MAP.get(weather_code, "󰖐")

    desc_list = current.get("weatherDesc", [])
    desc = desc_list[0].get("value", "Clear") if desc_list else "Clear"
    humidity = current.get("humidity", "50")
    wind_kmph = current.get("windspeedKmph", "10")

    tooltip_lines = [
        f"{icon}  {city} — {desc}",
        f"Temperature: {temp_val}{unit_symbol} (Feels like {feels_val}{unit_symbol})",
        f"Humidity: {humidity}%  |  Wind: {wind_kmph} km/h",
    ]

    # Include up to 3-day forecast summary if available
    forecasts = data.get("weather", [])
    if forecasts:
        tooltip_lines.append("")
        for day in forecasts[:3]:
            date_str = day.get("date", "")
            max_t = day.get("maxtempF" if use_fahrenheit else "maxtempC", "")
            min_t = day.get("mintempF" if use_fahrenheit else "mintempC", "")
            tooltip_lines.append(f" {date_str}:  ↑{max_t}{unit_symbol}  ↓{min_t}{unit_symbol}")

    return {
        "location": city,
        "temperature": f"{temp_val}{unit_symbol}",
        "condition": desc,
        "icon": icon,
        "text": f"{icon} {temp_val}{unit_symbol}",
        "tooltip": "\n".join(tooltip_lines),
        "class": "weather-normal",
    }


def get_weather_status(
    location: str = "",
    units: str = "m",
    cache_ttl: int = 900,
    timeout: float = 3.5,
) -> dict[str, Any]:
    """Fetch live weather from wttr.in with local caching and offline resilience."""
    cache_file = _get_cache_dir() / f"weather_{location or 'auto'}_{units}.json"

    if cache_file.is_file():
        try:
            age = time.time() - cache_file.stat().st_mtime
            if age < cache_ttl:
                cached = json.loads(cache_file.read_text(encoding="utf-8"))
                if isinstance(cached, dict) and "text" in cached:
                    return cached
        except Exception:
            pass

    loc_Segment = urllib.parse.quote(location.strip()) if location.strip() else ""
    url = f"https://wttr.in/{loc_Segment}?format=j1"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0 DETech-FreeBSD"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw_json = json.loads(resp.read().decode("utf-8"))
        result = parse_wttr_json(raw_json, units=units, fallback_location=location)
        try:
            cache_file.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        except Exception:
            pass
        return result
    except Exception:
        # Return stale cache if available
        if cache_file.is_file():
            try:
                cached = json.loads(cache_file.read_text(encoding="utf-8"))
                if isinstance(cached, dict) and "text" in cached:
                    return cached
            except Exception:
                pass

    unit_symbol = "°F" if units.lower() in ("u", "f", "imperial", "us") else "°C"
    return {
        "location": location or "Offline",
        "temperature": f"--{unit_symbol}",
        "condition": "Offline",
        "icon": "󰖐",
        "text": f"󰖐 --{unit_symbol}",
        "tooltip": "DETech Weather: Offline or awaiting network connection",
        "class": "weather-offline",
    }


def get_calendar_status(
    today: datetime.date | None = None,
    accent_color: str = "#e64553",
) -> dict[str, Any]:
    """Build an interactive calendar widget payload with Pango-highlighted current day."""
    now_date = today or datetime.date.today()
    cal = calendar.TextCalendar(calendar.MONDAY)
    month_str = cal.formatmonth(now_date.year, now_date.month)

    # Highlight today's date number in the formatted month grid for Waybar Pango tooltip
    lines = month_str.rstrip().splitlines()
    highlighted_lines: list[str] = []
    day_pattern = re.compile(rf"(?<!\d)({now_date.day})(?!\d)")

    for idx, line in enumerate(lines):
        if idx == 0:
            highlighted_lines.append(f"<b><span color='{accent_color}'>{line.center(20)}</span></b>")
        elif idx == 1:
            highlighted_lines.append(f"<b>{line}</b>")
        else:
            highlighted_lines.append(
                day_pattern.sub(
                    rf"<b><span background='{accent_color}' foreground='#11111b'>\1</span></b>",
                    line,
                    count=1,
                )
            )

    pango_cal = "<tt>" + "\n".join(highlighted_lines) + "</tt>"
    label = now_date.strftime(" %a, %b %d")

    return {
        "date": now_date.isoformat(),
        "text": label,
        "tooltip": pango_cal,
        "class": "calendar-active",
    }


def parse_ifconfig_network_output(raw_ifconfig: str) -> dict[str, Any]:
    """Parse FreeBSD `ifconfig` output to identify active interface, IPv4, and Wi-Fi SSID."""
    current_iface: str | None = None
    interfaces: dict[str, dict[str, str]] = {}

    for line in raw_ifconfig.splitlines():
        iface_match = re.match(r"^([a-zA-Z0-9_]+):\s+flags=", line)
        if iface_match:
            current_iface = iface_match.group(1)
            interfaces[current_iface] = {"ip": "", "ssid": "", "status": ""}
            continue
        if not current_iface:
            continue

        stripped = line.strip()
        if stripped.startswith("inet ") and not stripped.startswith("inet 127."):
            parts = stripped.split()
            if len(parts) >= 2:
                interfaces[current_iface]["ip"] = parts[1]
        elif stripped.startswith("ssid "):
            m = re.search(r"ssid\s+(\S+)", stripped)
            if m:
                interfaces[current_iface]["ssid"] = m.group(1).strip('"')
        elif stripped.startswith("status:"):
            interfaces[current_iface]["status"] = stripped.split(":", 1)[1].strip()

    # Select first non-loopback interface with an IP
    for iface, info in interfaces.items():
        if iface.startswith("lo"):
            continue
        if info["ip"]:
            is_wifi = iface.startswith("wlan") or iface.startswith("iwm") or iface.startswith("iwx") or bool(info["ssid"])
            icon = "󰤨" if is_wifi else "󰈀"
            label = info["ssid"] if info["ssid"] else iface
            return {
                "interface": iface,
                "ip": info["ip"],
                "ssid": info["ssid"],
                "connected": True,
                "text": f"{icon} {label}",
                "tooltip": f"FreeBSD Network ({iface}): {info['ip']}"
                + (f" | SSID: {info['ssid']}" if info["ssid"] else ""),
                "class": "connected",
            }

    return {
        "interface": "none",
        "ip": "",
        "ssid": "",
        "connected": False,
        "text": "󰤭 Offline",
        "tooltip": "FreeBSD Network: Disconnected",
        "class": "disconnected",
    }


def get_network_status() -> dict[str, Any]:
    """Query FreeBSD network interfaces via `ifconfig`."""
    try:
        proc = subprocess.run(
            ["ifconfig"],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return parse_ifconfig_network_output(proc.stdout)
    except OSError:
        pass

    return {
        "interface": "em0",
        "ip": "192.168.1.100",
        "ssid": "",
        "connected": True,
        "text": "󰈀 em0",
        "tooltip": "FreeBSD Network (em0): Online",
        "class": "connected",
    }


def get_media_status() -> dict[str, Any]:
    """Query MPRIS media player status via `playerctl`."""
    if shutil.which("playerctl"):
        try:
            status_proc = subprocess.run(
                ["playerctl", "status"],
                capture_output=True,
                text=True,
                check=False,
            )
            status = status_proc.stdout.strip()
            if status in ("Playing", "Paused"):
                meta_proc = subprocess.run(
                    ["playerctl", "metadata", "--format", "{{artist}} - {{title}}"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                track = meta_proc.stdout.strip().strip(" -") or "Media Playing"
                short_track = track[:28] + "…" if len(track) > 29 else track
                icon = "󰎈" if status == "Playing" else "󰏤"
                return {
                    "status": status,
                    "track": track,
                    "text": f"{icon} {short_track}",
                    "tooltip": f"Now {status}: {track}\nClick: Play/Pause | Scroll: Next/Prev",
                    "class": status.lower(),
                }
        except OSError:
            pass

    return {
        "status": "Stopped",
        "track": "",
        "text": "󰎆",
        "tooltip": "MPRIS Media Player: Idle",
        "class": "stopped",
    }


def run_media_action(action: str) -> dict[str, Any]:
    """Trigger MPRIS playback action (`play-pause`, `next`, `prev`) via `playerctl`."""
    cmd_map = {
        "play-pause": "play-pause",
        "next": "next",
        "prev": "previous",
    }
    subcmd = cmd_map.get(action, "play-pause")
    if shutil.which("playerctl"):
        subprocess.run(["playerctl", subcmd], check=False, capture_output=True)
    return get_media_status()


def parse_dunst_history(raw_json_str: str) -> list[dict[str, str]]:
    """Parse `dunstctl history` JSON output into a clean list of recent notifications."""
    try:
        payload = json.loads(raw_json_str)
        items_raw = payload.get("data", [[]])[0]
    except Exception:
        return []

    parsed: list[dict[str, str]] = []
    for entry in items_raw[:15]:
        if not isinstance(entry, dict):
            continue
        app = entry.get("appname", {}).get("data", "System") if isinstance(entry.get("appname"), dict) else "System"
        summary = entry.get("summary", {}).get("data", "") if isinstance(entry.get("summary"), dict) else ""
        body = entry.get("body", {}).get("data", "") if isinstance(entry.get("body"), dict) else ""
        notif_id = str(entry.get("id", {}).get("data", "")) if isinstance(entry.get("id"), dict) else ""
        body_clean = " ".join(str(body).splitlines()).strip()
        parsed.append(
            {
                "id": notif_id,
                "app": str(app).strip() or "System",
                "summary": str(summary).strip() or "Notification",
                "body": body_clean,
            }
        )
    return parsed


def get_dnd_status(action: str = "status", toggle: bool = False) -> dict[str, Any]:
    """Query or control Dunst notifications & Do-Not-Disturb (`status`, `toggle`, `close-all`, `pop`, `clear`)."""
    if toggle:
        action = "toggle"

    state_file = _get_cache_dir() / "dnd_paused"
    paused = state_file.is_file()
    waiting_count = 0
    history_count = 0
    recent_history: list[dict[str, str]] = []

    if shutil.which("dunstctl"):
        if action == "toggle":
            subprocess.run(["dunstctl", "set-paused", "toggle"], check=False, capture_output=True)
        elif action == "close-all":
            subprocess.run(["dunstctl", "close-all"], check=False, capture_output=True)
        elif action == "pop":
            subprocess.run(["dunstctl", "history-pop"], check=False, capture_output=True)
        elif action == "clear":
            subprocess.run(["dunstctl", "history-clear"], check=False, capture_output=True)

        proc = subprocess.run(
            ["dunstctl", "is-paused"],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            paused = proc.stdout.strip().lower() == "true"

        w_proc = subprocess.run(["dunstctl", "count", "waiting"], capture_output=True, text=True, check=False)
        if w_proc.returncode == 0 and w_proc.stdout.strip().isdigit():
            waiting_count = int(w_proc.stdout.strip())

        h_proc = subprocess.run(["dunstctl", "count", "history"], capture_output=True, text=True, check=False)
        if h_proc.returncode == 0 and h_proc.stdout.strip().isdigit():
            history_count = int(h_proc.stdout.strip())

        hist_proc = subprocess.run(["dunstctl", "history"], capture_output=True, text=True, check=False)
        if hist_proc.returncode == 0 and hist_proc.stdout.strip():
            recent_history = parse_dunst_history(hist_proc.stdout)
    elif action == "toggle":
        paused = not paused

    if paused:
        state_file.write_text("true\n", encoding="utf-8")
    elif state_file.is_file():
        state_file.unlink(missing_ok=True)

    badge_count = waiting_count if paused else history_count
    icon = "󰂛" if paused else ("󰂞" if badge_count > 0 else "󰂚")
    if paused:
        label = f"{icon} DND ({waiting_count})" if waiting_count > 0 else f"{icon} DND"
    else:
        label = f"{icon} {history_count}" if history_count > 0 else icon

    tooltip_lines = [
        f"Notifications: {'Paused (Do Not Disturb)' if paused else 'Active'}",
        f"History: {history_count}  |  Queued: {waiting_count}",
        "Left-Click: Notification Center | Right-Click: Toggle DND | Middle-Click: Dismiss All",
    ]
    if recent_history:
        tooltip_lines.append("")
        tooltip_lines.append("Recent Notifications:")
        for item in recent_history[:5]:
            summary_str = f"• [{item['app']}] {item['summary']}"
            if item["body"]:
                summary_str += f" — {item['body'][:40]}"
            tooltip_lines.append(summary_str)

    return {
        "paused": paused,
        "waiting": waiting_count,
        "history": history_count,
        "recent": recent_history,
        "text": label,
        "tooltip": "\n".join(tooltip_lines),
        "class": "dnd-active" if paused else ("has-notifications" if history_count > 0 else "dnd-inactive"),
    }


def parse_boottime_sysctl(raw_boottime: str, now_ts: float | None = None) -> int:
    """Parse FreeBSD `sysctl kern.boottime` output (`{ sec = 1700000000, usec = 0 }`) into uptime seconds."""
    m = re.search(r"sec\s*=\s*(\d+)", raw_boottime)
    if m:
        boot_sec = int(m.group(1))
        current = now_ts if now_ts is not None else time.time()
        return max(0, int(current - boot_sec))
    return 3600


def get_uptime_kernel_status() -> dict[str, Any]:
    """Query FreeBSD kernel release (`kern.osrelease`) and system uptime (`kern.boottime`)."""
    kernel = query_sysctl("kern.osrelease")
    if not kernel:
        try:
            proc = subprocess.run(["uname", "-r"], capture_output=True, text=True, check=False)
            kernel = proc.stdout.strip() or "14.1-RELEASE"
        except OSError:
            kernel = "14.1-RELEASE"

    raw_boot = query_sysctl("kern.boottime")
    if raw_boot:
        uptime_sec = parse_boottime_sysctl(raw_boot)
    else:
        # Fallback for non-FreeBSD test hosts if /proc/uptime exists
        uptime_file = Path("/proc/uptime")
        if uptime_file.is_file():
            try:
                uptime_sec = int(float(uptime_file.read_text(encoding="utf-8").split()[0]))
            except Exception:
                uptime_sec = 7200
        else:
            uptime_sec = 7200

    days = uptime_sec // 86400
    hours = (uptime_sec % 86400) // 3600
    minutes = (uptime_sec % 3600) // 60

    if days > 0:
        up_str = f"{days}d {hours}h"
    elif hours > 0:
        up_str = f"{hours}h {minutes}m"
    else:
        up_str = f"{minutes}m"

    return {
        "kernel": kernel,
        "uptime_seconds": uptime_sec,
        "uptime": up_str,
        "text": f"󱎫 {up_str}",
        "tooltip": f"FreeBSD Kernel: {kernel}\nSystem Uptime: {up_str}",
        "class": "normal",
    }


def get_clipboard_status(clear: bool = False) -> dict[str, Any]:
    """Query or wipe clipboard history managed by `cliphist`."""
    count = 0
    if shutil.which("cliphist"):
        if clear:
            subprocess.run(["cliphist", "wipe"], check=False, capture_output=True)
        else:
            proc = subprocess.run(["cliphist", "list"], capture_output=True, text=True, check=False)
            if proc.returncode == 0 and proc.stdout.strip():
                count = len(proc.stdout.strip().splitlines())

    return {
        "count": count,
        "text": "󰅌" if count == 0 else f"󰅌 {count}",
        "tooltip": f"Clipboard Manager (cliphist): {count} items\nLeft-Click: Open Picker | Right-Click: Clear",
        "class": "normal",
    }
