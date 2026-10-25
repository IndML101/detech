"""Interactive Rofi Menus for Calendar, Weather, and Clipboard Widgets."""

from __future__ import annotations

import calendar
import datetime
import shutil
import subprocess

from detech.freebsd.widgets import get_dnd_status, get_weather_status
from detech.menus.glyph_emoji_menu import copy_to_wayland_clipboard
from detech.menus.rofi_runner import run_rofi_dmenu


MINIMALIST_SEPARATOR = "────────────"


def build_calendar_menu_entries(year: int | None = None, month: int | None = None) -> tuple[str, list[str]]:
    """Build formatted calendar header and navigable day/week entries for Rofi."""
    today = datetime.date.today()
    y = year or today.year
    m = month or today.month

    cal = calendar.TextCalendar(calendar.MONDAY)
    month_grid = cal.formatmonth(y, m).rstrip()
    entries = [
        f"  Today: {today.strftime('%A, %B %d, %Y')}",
        "◀  Previous Month",
        "▶  Next Month",
        MINIMALIST_SEPARATOR,
    ]
    for line in month_grid.splitlines()[1:]:
        entries.append(f"   {line}")
    return month_grid, entries


def open_calendar_menu(year: int | None = None, month: int | None = None) -> str | None:
    """Open interactive Rofi Calendar widget with month navigation."""
    today = datetime.date.today()
    y = year or today.year
    m = month or today.month

    while True:
        month_name = calendar.month_name[m]
        _, entries = build_calendar_menu_entries(y, m)
        choice = run_rofi_dmenu(
            entries,
            prompt=f"  {month_name} {y}",
            mesg=f"Today is {today.strftime('%A, %b %d, %Y')} — Select arrows to navigate months",
        )
        if not choice:
            return None
        if "Previous Month" in choice:
            if m == 1:
                m = 12
                y -= 1
            else:
                m -= 1
            continue
        if "Next Month" in choice:
            if m == 12:
                m = 1
                y += 1
            else:
                m += 1
            continue
        return choice


def open_clipboard_menu() -> str | None:
    """Open Rofi Clipboard History Picker backed by `cliphist` and `wl-copy`."""
    entries: list[str] = []
    if shutil.which("cliphist"):
        proc = subprocess.run(["cliphist", "list"], capture_output=True, text=True, check=False)
        if proc.returncode == 0 and proc.stdout.strip():
            entries = proc.stdout.strip().splitlines()

    if not entries:
        entries = ["(Clipboard history is empty)"]

    choice = run_rofi_dmenu(
        ["󰆴  Clear Clipboard History", *entries],
        prompt="󰅌  Clipboard",
        mesg="Select an item to copy to Wayland clipboard",
    )
    if not choice or choice == "(Clipboard history is empty)":
        return None

    if "Clear Clipboard History" in choice:
        if shutil.which("cliphist"):
            subprocess.run(["cliphist", "wipe"], check=False)
        return "cleared"

    if shutil.which("cliphist") and shutil.which("wl-copy"):
        decoded = subprocess.run(
            ["cliphist", "decode"],
            input=choice,
            capture_output=True,
            text=True,
            check=False,
        )
        if decoded.returncode == 0:
            copy_to_wayland_clipboard(decoded.stdout)
    else:
        copy_to_wayland_clipboard(choice)
    return choice


def open_weather_menu(location: str = "", units: str = "m") -> str | None:
    """Open Rofi Weather Forecast popup showing current conditions and 3-day outlook."""
    status = get_weather_status(location=location, units=units)
    lines = status.get("tooltip", "").splitlines()
    if not lines:
        lines = [status.get("text", "Weather unavailable")]
    return run_rofi_dmenu(
        lines,
        prompt="󰖐  Weather",
        mesg=f"Weather Report — {status.get('location', 'Auto Location')}",
    )


def open_notifications_menu() -> str | None:
    """Open interactive Rofi Notification Center (Dunst history, pop, dismiss, and DND toggle)."""
    status = get_dnd_status()
    paused = bool(status.get("paused", False))
    dnd_toggle_label = "󰂚  Resume Notifications (Disable DND)" if paused else "󰂛  Enable Do Not Disturb (Pause)"

    entries: list[str] = [
        dnd_toggle_label,
        "󰎟  Pop Latest Notification from History",
        "󰅖  Dismiss All Active Notifications",
        "󰆴  Clear Notification History",
        MINIMALIST_SEPARATOR,
    ]

    recent = status.get("recent", [])
    if recent:
        for item in recent:
            body_part = f" — {item['body']}" if item.get("body") else ""
            entries.append(f"#{item.get('id', '0')}  [{item.get('app', 'App')}] {item.get('summary', '')}{body_part}")
    else:
        entries.append("(No notifications in history)")

    choice = run_rofi_dmenu(
        entries,
        prompt="󰂚  Notifications",
        mesg=f"Status: {'Paused (DND)' if paused else 'Active'} | History: {status.get('history', 0)}",
    )
    if not choice or choice.startswith("──") or choice == "(No notifications in history)":
        return None

    if "Do Not Disturb" in choice or "Resume Notifications" in choice:
        get_dnd_status(action="toggle")
        return "toggled-dnd"
    if "Pop Latest" in choice:
        get_dnd_status(action="pop")
        return "popped"
    if "Dismiss All" in choice:
        get_dnd_status(action="close-all")
        return "closed-all"
    if "Clear Notification History" in choice:
        get_dnd_status(action="clear")
        return "cleared"
    if choice.startswith("#") and shutil.which("dunstctl"):
        notif_id = choice.split()[0].lstrip("#")
        if notif_id.isdigit():
            subprocess.run(["dunstctl", "history-pop", notif_id], check=False)
            return f"popped-{notif_id}"
    return choice
