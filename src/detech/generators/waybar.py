"""Waybar Configuration & Dynamic CSS Generator (15 Switchable Layouts)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from detech.core.color_engine import hex_to_rgba_css
from detech.core.lua_loader import load_lua_file
from detech.core.paths import get_presets_dir


WORKSPACE_ICON_SETS: dict[str, dict[str, str]] = {
    "numbers": {
        "1": "1",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
        "6": "6",
        "7": "7",
        "8": "8",
        "9": "9",
        "10": "10",
        "urgent": "",
        "focused": "",
        "default": "",
    },
    "dots": {
        "1": "",
        "2": "",
        "3": "",
        "4": "",
        "5": "",
        "urgent": "",
        "active": "󰮯",
        "default": "",
    },
    "pills": {
        "1": "󰎤",
        "2": "󰎧",
        "3": "󰎪",
        "4": "󰎭",
        "5": "󰎱",
        "urgent": "",
        "active": "󰝥",
        "default": "󰝦",
    },
    "kanji": {
        "1": "一",
        "2": "二",
        "3": "三",
        "4": "四",
        "5": "五",
        "6": "六",
        "7": "七",
        "8": "八",
        "9": "九",
        "10": "十",
        "urgent": "",
        "default": "〇",
    },
    "roman": {
        "1": "I",
        "2": "II",
        "3": "III",
        "4": "IV",
        "5": "V",
        "6": "VI",
        "7": "VII",
        "8": "VIII",
        "9": "IX",
        "10": "X",
        "urgent": "!",
        "default": "·",
    },
    "cyber": {
        "1": "01",
        "2": "02",
        "3": "03",
        "4": "04",
        "5": "05",
        "6": "06",
        "urgent": "⚠",
        "default": "00",
    },
    "brackets": {
        "1": "[1]",
        "2": "[2]",
        "3": "[3]",
        "4": "[4]",
        "5": "[5]",
        "urgent": "[!]",
        "default": "[-]",
    },
    "bsd": {
        "1": " 1",
        "2": " 2",
        "3": "󰈹 3",
        "4": " 4",
        "5": " 5",
        "urgent": "",
        "default": "",
    },
}


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


def build_waybar_config_dict(spec: dict[str, Any]) -> dict[str, Any]:
    """Build the Waybar JSON configuration dictionary for a given layout blueprint."""
    position = spec.get("position", "top")
    is_vertical = position in ("left", "right")
    icon_scheme = spec.get("workspace_icons", "numbers")
    ws_icons = WORKSPACE_ICON_SETS.get(icon_scheme, WORKSPACE_ICON_SETS["numbers"])
    clock_fmt = spec.get("clock_format") or ("{:%H\n%M}" if is_vertical else " {:%H:%M   %a %b %d}")

    bar_config: dict[str, Any] = {
        "layer": "top",
        "position": position,
        "spacing": spec.get("spacing", 6),
        "margin": spec.get("margin", "6 12 0 12"),
        "modules-left": spec.get("modules_left", ["custom/bsd-logo", "hyprland/workspaces"]),
        "modules-center": spec.get("modules_center", ["clock"]),
        "modules-right": spec.get("modules_right", ["custom/bsd-audio", "custom/bsd-battery", "tray"]),
        "custom/bsd-logo": {
            "format": "",
            "tooltip-format": "DETech on FreeBSD — Click: App Drawer | Right-Click: Theme Picker",
            "on-click": "detech menu apps",
            "on-click-right": "detech menu themes",
            "on-click-middle": "detech menu keybinds",
        },
        "hyprland/workspaces": {
            "disable-scroll": False,
            "all-outputs": True,
            "format": "{icon}",
            "format-icons": ws_icons,
        },
        "hyprland/window": {
            "max-length": 48,
            "separate-outputs": True,
        },
    "clock": {
            "format": clock_fmt,
            "tooltip-format": "<big>{:%Y %B}</big>\n<tt><small>{calendar}</small></tt>",
            "on-click": "detech menu calendar",
            "calendar": {
                "mode": "month",
                "mode-mon-col": 3,
                "weeks-pos": "right",
                "on-scroll": 1,
                "format": {
                    "months": "<span color='#f5e0dc'><b>{}</b></span>",
                    "days": "<span color='#cdd6f4'><b>{}</b></span>",
                    "weeks": "<span color='#94e2d5'><b>W{}</b></span>",
                    "weekdays": "<span color='#f9e2af'><b>{}</b></span>",
                    "today": "<span background='#e64553' color='#11111b'><b><u>{}</u></b></span>",
                },
            },
            "actions": {
                "on-click-right": "mode",
                "on-scroll-up": "shift_up",
                "on-scroll-down": "shift_down",
            },
        },
        "custom/calendar": {
            "exec": "detech bsd widgets calendar --json",
            "return-type": "json",
            "interval": 60,
            "on-click": "detech menu calendar",
        },
        "custom/weather": {
            "exec": "detech bsd widgets weather --json",
            "return-type": "json",
            "interval": 900,
            "on-click": "detech menu weather",
        },
        "custom/bsd-net": {
            "exec": "detech bsd widgets network --json",
            "return-type": "json",
            "interval": 10,
        },
        "custom/media": {
            "exec": "detech bsd widgets media --json",
            "return-type": "json",
            "interval": 3,
            "on-click": "detech bsd widgets media play-pause",
            "on-scroll-up": "detech bsd widgets media next",
            "on-scroll-down": "detech bsd widgets media prev",
        },
        "custom/dnd": {
            "exec": "detech bsd widgets dnd --json",
            "return-type": "json",
            "interval": 5,
            "on-click": "detech menu notifications",
            "on-click-right": "detech bsd widgets dnd toggle",
            "on-click-middle": "detech bsd widgets dnd close-all",
        },
        "custom/notifications": {
            "exec": "detech bsd widgets dnd --json",
            "return-type": "json",
            "interval": 5,
            "on-click": "detech menu notifications",
            "on-click-right": "detech bsd widgets dnd toggle",
            "on-click-middle": "detech bsd widgets dnd close-all",
        },
        "custom/bsd-uptime": {
            "exec": "detech bsd widgets uptime --json",
            "return-type": "json",
            "interval": 60,
            "on-click": "detech fetch",
        },
        "custom/clipboard": {
            "exec": "detech bsd widgets clipboard --json",
            "return-type": "json",
            "interval": 10,
            "on-click": "detech menu clipboard",
            "on-click-right": "detech bsd widgets clipboard clear",
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
        "custom/bsd-load": {
            "exec": "detech bsd power load --json",
            "return-type": "json",
            "interval": 5,
        },
        "custom/bsd-mem": {
            "exec": "detech bsd power memory --json",
            "return-type": "json",
            "interval": 10,
        },
        "custom/bsd-zfs": {
            "exec": "detech bsd power zfs --json",
            "return-type": "json",
            "interval": 60,
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
        "custom/bsd-power": {
            "format": "⏻",
            "tooltip-format": "FreeBSD Session Lock / Power",
            "on-click": "detech bsd power lock",
            "on-click-right": "detech bsd power suspend",
        },
        "tray": {
            "icon-size": spec.get("tray_icon_size", 16),
            "spacing": spec.get("tray_spacing", 8),
            "show-passive-items": True,
            "reverse-direction": False,
        },
    }

    if "height" in spec:
        bar_config["height"] = spec["height"]
    if "width" in spec:
        bar_config["width"] = spec["width"]

    return bar_config


def render_waybar_css(
    spec: dict[str, Any],
    palette: dict[str, str],
    fonts: dict[str, Any],
) -> str:
    """Render tailored Waybar CSS for the given layout blueprint, palette, and Nerd Font."""
    layout_id = spec.get("id", "island-top")
    variant = spec.get("style_variant", "floating-pills")
    position = spec.get("position", "top")
    is_vertical = position in ("left", "right")

    radius_map = {
        "edge-flat": "0px",
        "retro-box": "0px",
        "sharp-neon": "0px",
        "capsules": "20px",
        "dock-rounded": "16px",
        "center-notch": "0px 0px 16px 16px",
        "split-wings": "14px",
        "vertical-rail": "12px",
        "workspace-centric": "12px",
        "glass-full": "0px",
        "zen-minimal": "6px",
        "segmented-blocks": "6px",
        "telemetry-bar": "8px",
        "floating-pills": "10px",
    }
    radius = radius_map.get(variant, "10px")

    transparent_window_variants = {
        "floating-pills",
        "split-wings",
        "capsules",
        "workspace-centric",
        "zen-minimal",
    }
    if variant in transparent_window_variants:
        window_bg = hex_to_rgba_css(palette["bg_primary"], 0.0)
    elif variant == "glass-full":
        window_bg = hex_to_rgba_css(palette["bg_primary"], 0.74)
    else:
        window_bg = hex_to_rgba_css(palette["bg_primary"], 0.90)

    mod_pad = "6px 4px" if is_vertical else "4px 12px"
    mod_margin = "3px 2px" if is_vertical else "2px 4px"

    all_module_selectors = (
        "#custom-bsd-logo, #workspaces, #window, #clock, "
        "#custom-calendar, #custom-weather, #custom-bsd-net, #custom-media, "
        "#custom-dnd, #custom-notifications, #custom-bsd-uptime, #custom-clipboard, "
        "#custom-bsd-battery, #custom-bsd-temp, #custom-bsd-load, "
        "#custom-bsd-mem, #custom-bsd-zfs, #custom-bsd-audio, "
        "#custom-bsd-backlight, #custom-bsd-pkg, #custom-bsd-power, #tray"
    )

    css_lines = [
        f"/* DETech Waybar Style — Layout: {layout_id} ({variant}) */",
        f"@define-color bg_primary {palette['bg_primary']};",
        f"@define-color bg_secondary {palette['bg_secondary']};",
        f"@define-color bg_tertiary {palette['bg_tertiary']};",
        f"@define-color fg_primary {palette['fg_primary']};",
        f"@define-color fg_secondary {palette['fg_secondary']};",
        f"@define-color fg_muted {palette['fg_muted']};",
        f"@define-color accent {palette['accent']};",
        f"@define-color accent_alt {palette['accent_alt']};",
        f"@define-color urgent {palette['urgent']};",
        f"@define-color warning {palette['warning']};",
        f"@define-color success {palette['success']};",
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
        f"{all_module_selectors} {{",
        f"    background-color: {hex_to_rgba_css(palette['bg_secondary'], 0.92)};",
        "    color: @fg_primary;",
        f"    border-radius: {radius};",
        f"    padding: {mod_pad};",
        f"    margin: {mod_margin};",
        f"    border: 1px solid {hex_to_rgba_css(palette['border_inactive'], 0.6)};",
        "}",
        "",
        "#custom-bsd-logo {",
        "    color: @accent;",
        "    font-weight: bold;",
        f"    font-size: {fonts['bar_size'] + 3}pt;",
        "}",
        "",
        "#custom-bsd-power {",
        "    color: @urgent;",
        "    font-weight: bold;",
        "}",
        "",
        "#workspaces button {",
        f"    padding: {'4px 2px' if is_vertical else '0 7px'};",
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
        "",
        "#custom-bsd-battery.critical, #custom-bsd-temp.critical, #custom-bsd-load.critical, #custom-bsd-mem.critical {",
        "    color: @urgent;",
        "    border-color: @urgent;",
        "}",
        "",
        "#custom-weather {",
        "    color: @accent_alt;",
        "    font-weight: bold;",
        "}",
        "",
        "#custom-calendar {",
        "    color: @accent;",
        "    font-weight: bold;",
        "}",
        "",
        "#custom-media.playing {",
        "    color: @success;",
        "}",
        "",
        "#custom-dnd.dnd-active, #custom-notifications.dnd-active {",
        "    color: @warning;",
        "    border-color: @warning;",
        "}",
        "",
        "#custom-dnd.has-notifications, #custom-notifications.has-notifications {",
        "    color: @accent;",
        "    font-weight: bold;",
        "}",
        "",
        "#tray > .passive {",
        "    -gtk-icon-effect: dim;",
        "}",
        "",
        "#tray > .needs-attention {",
        "    -gtk-icon-effect: highlight;",
        "    background-color: @urgent;",
        f"    border-radius: {radius};",
        "}",
        "",
        "#tray menu {",
        f"    background-color: {hex_to_rgba_css(palette['bg_primary'], 0.96)};",
        "    color: @fg_primary;",
        "    border: 1px solid @accent;",
        f"    border-radius: {radius};",
        "    padding: 4px;",
        "}",
        "",
        "#tray menu menuitem:hover {",
        "    background-color: @accent;",
        "    color: @bg_primary;",
        "}",
        "",
        "#custom-bsd-net.disconnected {",
        "    color: @urgent;",
        "}",
        "",
        "tooltip {",
        f"    background-color: {hex_to_rgba_css(palette['bg_primary'], 0.96)};",
        "    border: 1px solid @accent;",
        f"    border-radius: {radius};",
        "}",
        "",
        "tooltip label {",
        "    color: @fg_primary;",
        "    padding: 6px;",
        "}",
    ]

    # Variant-specific architectural overrides
    if variant == "split-wings":
        css_lines.extend(
            [
                "",
                "/* Split Wings: Three unified island containers */",
                ".modules-left, .modules-center, .modules-right {",
                f"    background-color: {hex_to_rgba_css(palette['bg_primary'], 0.92)};",
                "    border-radius: 14px;",
                "    padding: 2px 8px;",
                "    border: 1px solid @accent;",
                "}",
                f"{all_module_selectors} {{",
                "    background-color: transparent;",
                "    border: none;",
                "    margin: 0 2px;",
                "}",
            ]
        )
    elif variant == "sharp-neon":
        css_lines.extend(
            [
                "",
                "/* Cyber Angled: Sharp tactical borders with accent glow */",
                f"{all_module_selectors} {{",
                "    border-radius: 0px;",
                "    border: 1px solid @accent;",
                "    border-left: 3px solid @accent;",
                "}",
                "#clock {",
                "    border-bottom: 2px solid @accent_alt;",
                "    font-weight: bold;",
                "}",
            ]
        )
    elif variant == "retro-box":
        css_lines.extend(
            [
                "",
                "/* Retro Box: Classic BSD terminal status bar */",
                "window#waybar {",
                "    border-top: 2px solid @accent;",
                "}",
                f"{all_module_selectors} {{",
                "    border-radius: 0px;",
                "    border: 2px solid @fg_muted;",
                "    background-color: @bg_primary;",
                "}",
            ]
        )
    elif variant == "zen-minimal":
        css_lines.extend(
            [
                "",
                "/* Zen Status: Featherweight borderless distraction-free bar */",
                f"{all_module_selectors} {{",
                "    background-color: transparent;",
                "    border: none;",
                "    padding: 2px 8px;",
                "}",
                "#workspaces button.active {",
                "    background-color: transparent;",
                "    color: @accent;",
                "    border-bottom: 2px solid @accent;",
                "}",
            ]
        )
    elif variant == "edge-flat":
        css_lines.extend(
            [
                "",
                "/* Minimal Edge-to-Edge Flat Bar */",
                "window#waybar {",
                f"    border-bottom: 1px solid {hex_to_rgba_css(palette['border_inactive'], 0.8)};",
                "}",
                f"{all_module_selectors} {{",
                "    background-color: transparent;",
                "    border: none;",
                "    border-radius: 0px;",
                "}",
                "#workspaces button.active {",
                "    background-color: @bg_tertiary;",
                "    color: @accent;",
                "    border-bottom: 2px solid @accent;",
                "}",
            ]
        )
    elif variant == "capsules":
        css_lines.extend(
            [
                "",
                "/* Capsules Dark: High-contrast 20px bubble pills */",
                "#custom-bsd-logo, #clock {",
                "    background-color: @accent;",
                "    color: @bg_primary;",
                "    font-weight: bold;",
                "}",
            ]
        )
    elif variant == "telemetry-bar":
        css_lines.extend(
            [
                "",
                "/* FreeBSD Telemetry Bar: Sysadmin dense metrics */",
                "#custom-bsd-zfs, #custom-bsd-pkg {",
                "    color: @accent_alt;",
                "}",
                "#custom-bsd-load, #custom-bsd-mem, #custom-bsd-temp {",
                "    background-color: @bg_tertiary;",
                "}",
            ]
        )

    return "\n".join(css_lines) + "\n"


def generate_waybar_configs(
    context: dict[str, Any],
    palette: dict[str, str],
    fonts: dict[str, Any],
    config_root: Path,
) -> list[Path]:
    """Generate `waybar/config.jsonc`, `waybar/style.css`, and all 15 pre-compiled layouts."""
    waybar_dir = config_root / "waybar"
    layouts_dir = waybar_dir / "layouts"
    styles_dir = waybar_dir / "styles"
    waybar_dir.mkdir(parents=True, exist_ok=True)
    layouts_dir.mkdir(parents=True, exist_ok=True)
    styles_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    all_layouts = list_waybar_layouts()

    # Pre-compile all 15 Waybar layouts into `waybar/layouts/<id>.jsonc` and `waybar/styles/<id>.css`
    for item in all_layouts:
        lid = item["id"]
        cfg_dict = build_waybar_config_dict(item)
        l_path = layouts_dir / f"{lid}.jsonc"
        l_path.write_text(
            f"// DETech Waybar Layout: {item.get('name', lid)} ({lid})\n"
            + json.dumps(cfg_dict, indent=2)
            + "\n",
            encoding="utf-8",
        )
        written.append(l_path)

        # If layout defines a secondary bar (e.g. dual-bar), also write `<id>-bottom.jsonc`
        if isinstance(item.get("secondary_bar"), dict):
            sec_spec = dict(item)
            sec_spec.update(item["secondary_bar"])
            sec_dict = build_waybar_config_dict(sec_spec)
            sec_path = layouts_dir / f"{lid}-secondary.jsonc"
            sec_path.write_text(
                f"// DETech Waybar Secondary Bar: {item.get('name', lid)} ({lid})\n"
                + json.dumps(sec_dict, indent=2)
                + "\n",
                encoding="utf-8",
            )
            written.append(sec_path)

        s_path = styles_dir / f"{lid}.css"
        s_path.write_text(render_waybar_css(item, palette, fonts), encoding="utf-8")
        written.append(s_path)

    # Write active layout to `waybar/config.jsonc` and `waybar/style.css`
    appearance = context.get("config", {}).get("appearance", {})
    active_id = appearance.get("waybar_layout", "island-top")
    active_spec = get_waybar_layout(active_id)
    active_bar_config = build_waybar_config_dict(active_spec)

    config_path = waybar_dir / "config.jsonc"
    config_path.write_text(
        f"// DETech Waybar Layout: {active_spec.get('name', active_id)} ({active_id})\n"
        + json.dumps(active_bar_config, indent=2)
        + "\n",
        encoding="utf-8",
    )
    written.append(config_path)

    style_path = waybar_dir / "style.css"
    style_path.write_text(render_waybar_css(active_spec, palette, fonts), encoding="utf-8")
    written.append(style_path)

    return written
