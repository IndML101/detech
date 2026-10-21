"""Waybar Configuration & Dynamic CSS Generator (15 Switchable Layouts)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from detech.core.color_engine import hex_to_rgba_css
from detech.core.lua_loader import load_lua_file
from detech.core.paths import get_presets_dir


def list_waybar_layouts() -> list[dict[str, Any]]:
    """Return all 15 switchable Waybar layouts from `presets/waybar/layouts.lua`."""
    path = get_presets_dir() / "waybar" / "layouts.lua"
    if not path.is_file():
        return []
    data = load_lua_file(path)
    return list(data.get("layouts", []))


def get_waybar_layout(layout_id: str) -> dict[str, Any]:
    """Retrieve a specific Waybar layout blueprint by ID."""
    layouts = list_waybar_layouts()
    for item in layouts:
        if item.get("id") == layout_id:
            return item
    if layouts:
        return layouts[0]
    raise ValueError(f"Waybar layout not found: {layout_id}")


def generate_waybar_configs(
    context: dict[str, Any],
    palette: dict[str, str],
    fonts: dict[str, Any],
    config_root: Path,
) -> list[Path]:
    """Generate `waybar/config.jsonc` and `waybar/style.css` for the active layout."""
    waybar_dir = config_root / "waybar"
    waybar_dir.mkdir(parents=True, exist_ok=True)

    appearance = context.get("config", {}).get("appearance", {})
    layout_id = appearance.get("waybar_layout", "island-top")
    spec = get_waybar_layout(layout_id)

    bar_config: dict[str, Any] = {
        "layer": "top",
        "position": spec.get("position", "top"),
        "margin": spec.get("margin", "6 12 0 12"),
        "modules-left": spec.get("modules_left", ["custom/bsd-logo", "hyprland/workspaces"]),
        "modules-center": spec.get("modules_center", ["clock"]),
        "modules-right": spec.get("modules_right", ["custom/bsd-audio", "custom/bsd-battery", "tray"]),
        "custom/bsd-logo": {
            "format": "",
            "tooltip-format": "DETech on FreeBSD — Click for App Drawer",
            "on-click": "detech menu apps",
            "on-click-right": "detech menu themes",
        },
        "hyprland/workspaces": {
            "disable-scroll": False,
            "all-outputs": True,
            "format": "{icon}",
            "format-icons": {
                "1": "1",
                "2": "2",
                "3": "3",
                "4": "4",
                "5": "5",
                "urgent": "",
                "focused": "",
                "default": "",
            },
        },
        "hyprland/window": {
            "max-length": 48,
            "separate-outputs": True,
        },
        "clock": {
            "format": " {:%H:%M   %a %b %d}",
            "tooltip-format": "<big>{:%Y %B}</big>\n<tt><small>{calendar}</small></tt>",
        },
        "custom/bsd-battery": {
            "exec": "detech bsd power battery --json",
            "return-type": "json",
            "interval": 15,
        },
        "custom/bsd-temp": {
            "exec": "detech bsd power thermal --json",
            "return-type": "json",
            "interval": 10,
        },
        "custom/bsd-audio": {
            "exec": "detech bsd audio status --json",
            "return-type": "json",
            "interval": 5,
            "on-click": "detech bsd audio mute",
            "on-scroll-up": "detech bsd audio up 5",
            "on-scroll-down": "detech bsd audio down 5",
        },
        "custom/bsd-backlight": {
            "exec": "detech bsd backlight status --json",
            "return-type": "json",
            "interval": 5,
            "on-scroll-up": "detech bsd backlight up 5",
            "on-scroll-down": "detech bsd backlight down 5",
        },
        "custom/bsd-pkg": {
            "exec": "detech bsd pkg updates --json",
            "return-type": "json",
            "interval": 1800,
            "on-click": "detech menu software",
        },
        "tray": {
            "icon-size": 16,
            "spacing": 8,
        },
    }

    if "height" in spec:
        bar_config["height"] = spec["height"]
    if "width" in spec:
        bar_config["width"] = spec["width"]

    config_path = waybar_dir / "config.jsonc"
    config_path.write_text(
        f"// DETech Waybar Layout: {spec.get('name', layout_id)} ({layout_id})\n"
        + json.dumps(bar_config, indent=2)
        + "\n",
        encoding="utf-8",
    )

    # Generate style.css tailored to layout variant + Nerd Font + active palette
    variant = spec.get("style_variant", "floating-pills")
    radius = "0px" if variant in ("edge-flat", "retro-box", "sharp-neon") else ("20px" if variant == "capsules" else "10px")
    window_bg = (
        hex_to_rgba_css(palette["bg_primary"], 0.0)
        if variant in ("floating-pills", "split-wings", "capsules")
        else hex_to_rgba_css(palette["bg_primary"], 0.88)
    )

    css_lines = [
        f"/* DETech Waybar Style — Layout: {layout_id} ({variant}) */",
        f"@define-color bg_primary {palette['bg_primary']};",
        f"@define-color bg_secondary {palette['bg_secondary']};",
        f"@define-color bg_tertiary {palette['bg_tertiary']};",
        f"@define-color fg_primary {palette['fg_primary']};",
        f"@define-color fg_secondary {palette['fg_secondary']};",
        f"@define-color accent {palette['accent']};",
        f"@define-color accent_alt {palette['accent_alt']};",
        f"@define-color urgent {palette['urgent']};",
        "",
        "* {",
        f'    font-family: "{fonts["mono"]}", "{fonts["sans"]}", sans-serif;',
        f"    font-size: {fonts['bar_size']}pt;",
        "    min-height: 0;",
        "}",
        "",
        "window#waybar {",
        f"    background: {window_bg};",
        "    color: @fg_primary;",
        f"    border-radius: {radius};",
        "}",
        "",
        "#custom-bsd-logo, #workspaces, #window, #clock, #custom-bsd-battery, #custom-bsd-temp, #custom-bsd-audio, #custom-bsd-backlight, #custom-bsd-pkg, #tray {",
        f"    background-color: {hex_to_rgba_css(palette['bg_secondary'], 0.92)};",
        "    color: @fg_primary;",
        f"    border-radius: {radius};",
        "    padding: 4px 12px;",
        "    margin: 2px 4px;",
        f"    border: 1px solid {hex_to_rgba_css(palette['border_inactive'], 0.6)};",
        "}",
        "",
        "#custom-bsd-logo {",
        "    color: @accent;",
        "    font-weight: bold;",
        f"    font-size: {fonts['bar_size'] + 3}pt;",
        "}",
        "",
        "#workspaces button {",
        "    padding: 0 6px;",
        "    color: @fg_secondary;",
        f"    border-radius: {radius};",
        "}",
        "",
        "#workspaces button.active {",
        "    color: @bg_primary;",
        "    background-color: @accent;",
        "    font-weight: bold;",
        "}",
        "",
        "#workspaces button.urgent {",
        "    color: @bg_primary;",
        "    background-color: @urgent;",
        "}",
    ]

    style_path = waybar_dir / "style.css"
    style_path.write_text("\n".join(css_lines) + "\n", encoding="utf-8")

    return [config_path, style_path]
