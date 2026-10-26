"""Interactive Rofi Screenshot Picker for DETech."""

from __future__ import annotations

from typing import Any

from detech.menus.rofi_runner import run_rofi_dmenu
from detech.screenshot import (
    capture_screenshot,
    get_screenshots_dir,
    open_screenshots_folder,
)


def build_screenshot_menu_entries() -> list[dict[str, Any]]:
    """Build list of interactive screenshot choices with icons and metadata."""
    return [
        {
            "id": "area",
            "label": "󰒅  Selected Area (Save & Copy)",
            "desc": "Select rectangular region with crosshair and copy + save",
            "mode": "area",
            "target": "both",
            "delay": 0,
        },
        {
            "id": "full",
            "label": "󰹑  Entire Screen (Save & Copy)",
            "desc": "Capture entire Wayland desktop and copy + save",
            "mode": "full",
            "target": "both",
            "delay": 0,
        },
        {
            "id": "window",
            "label": "󱂬  Active Window (Save & Copy)",
            "desc": "Capture the currently focused Hyprland window",
            "mode": "window",
            "target": "both",
            "delay": 0,
        },
        {
            "id": "area_clipboard",
            "label": "󰅌  Selected Area (Clipboard Only)",
            "desc": "Select region and copy PNG to clipboard without saving file",
            "mode": "area",
            "target": "copy",
            "delay": 0,
        },
        {
            "id": "full_clipboard",
            "label": "󰅌  Entire Screen (Clipboard Only)",
            "desc": "Capture entire screen to clipboard without saving file",
            "mode": "full",
            "target": "copy",
            "delay": 0,
        },
        {
            "id": "area_delayed",
            "label": "󰔛  Selected Area (5s Delay)",
            "desc": "Wait 5 seconds countdown, then select region",
            "mode": "area",
            "target": "both",
            "delay": 5,
        },
        {
            "id": "full_delayed",
            "label": "󰔛  Entire Screen (5s Delay)",
            "desc": "Wait 5 seconds countdown, then capture screen",
            "mode": "full",
            "target": "both",
            "delay": 5,
        },
        {
            "id": "window_delayed",
            "label": "󰔛  Active Window (5s Delay)",
            "desc": "Wait 5 seconds countdown, then capture active window",
            "mode": "window",
            "target": "both",
            "delay": 5,
        },
        {
            "id": "edit",
            "label": "  Selected Area & Annotate / Edit",
            "desc": "Select region and open in Swappy / Satty image annotator",
            "mode": "area",
            "target": "edit",
            "delay": 0,
        },
        {
            "id": "open_folder",
            "label": "󰋩  Open Screenshots Directory",
            "desc": "Open ~/Pictures/Screenshots in Graphical File Manager",
            "mode": "open_folder",
            "target": "",
            "delay": 0,
        },
    ]


def open_screenshot_menu() -> dict[str, Any] | None:
    """Open interactive Rofi screenshot mode menu and execute selected capture."""
    entries = build_screenshot_menu_entries()
    labels = [item["label"] for item in entries]

    choice = run_rofi_dmenu(
        labels,
        prompt="󰄄  Screenshot",
        mesg="Select capture mode (Area, Full Screen, Window, Timer, Annotate)",
    )
    if not choice:
        return None

    selected = next((item for item in entries if item["label"] == choice), None)
    if not selected:
        return None

    if selected["mode"] == "open_folder":
        folder = get_screenshots_dir()
        open_screenshots_folder(folder)
        return {"status": "success", "action": "open_folder", "path": str(folder)}

    return capture_screenshot(
        mode=selected["mode"],
        target=selected["target"],
        delay=selected.get("delay", 0),
        notify=True,
    )
