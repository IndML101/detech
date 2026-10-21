"""Main CLI entrypoint for DETech (`detech`)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from detech.core.color_engine import list_themes, resolve_active_palette
from detech.core.compiler import compile_all
from detech.core.font_manager import get_nerd_font_status_list, resolve_font_settings
from detech.core.state import get_effective_context, update_state
from detech.freebsd.audio import run_audio_action
from detech.freebsd.backlight import run_backlight_action
from detech.freebsd.pkg_manager import get_pkg_updates_status, list_installed_packages, search_remote_packages
from detech.freebsd.power import (
    build_power_command,
    format_waybar_json,
    get_battery_status,
    get_memory_status,
    get_system_load_status,
    get_thermal_status,
    get_zfs_status,
)
from detech.generators.hyprland import list_hyprlock_layouts
from detech.generators.rofi import list_rofi_layouts
from detech.generators.terminal_shell import list_starship_prompts
from detech.generators.waybar import list_waybar_layouts
from detech.menus.file_browser import open_file_browser
from detech.menus.font_menu import open_font_menu
from detech.menus.glyph_emoji_menu import format_glyph_entries, open_glyph_menu
from detech.menus.keybinds_menu import format_keybind_entries, open_keybinds_menu
from detech.menus.layout_menu import (
    open_hyprlock_layout_menu,
    open_rofi_layout_menu,
    open_starship_menu,
    open_waybar_layout_menu,
)
from detech.menus.pkg_menu import open_software_menu
from detech.menus.rofi_runner import launch_app_drawer
from detech.menus.theme_menu import open_color_scheme_menu, open_icon_menu, open_theme_menu
from detech.menus.wallpaper_menu import open_wallpaper_menu


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="detech",
        description="DETech — FreeBSD Hyprland Desktop Environment Engine (Lua + Python)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # detech status
    p_status = sub.add_parser("status", help="Show active DETech configuration & runtime state")
    p_status.add_argument("--json", action="store_true", help="Output status as JSON")

    # detech apply
    p_apply = sub.add_parser("apply", help="Compile Lua configs into native Hypr/Waybar/Rofi/Kitty/Starship configs")
    p_apply.add_argument("--output-dir", type=Path, default=None, help="Override target XDG ~/.config directory")
    p_apply.add_argument("--no-reload", action="store_true", help="Do not trigger live daemon reloads")

    # detech set <target> <value>
    p_set = sub.add_parser("set", help="Update a DETech preset, theme, font, or layout and recompile")
    p_set.add_argument(
        "target",
        choices=["theme", "waybar", "rofi", "starship", "hyprlock", "font", "icon", "wallpaper", "dynamic-colors"],
    )
    p_set.add_argument("value", help="New value for the target setting")
    p_set.add_argument("--size", type=int, default=None, help="Font size in pt (when setting font)")
    p_set.add_argument("--output-dir", type=Path, default=None, help="Override target XDG ~/.config directory")
    p_set.add_argument("--no-reload", action="store_true", help="Skip live daemon reload")

    # detech list <category>
    p_list = sub.add_parser("list", help="List available themes, layouts, prompts, Nerd Fonts, or keybinds")
    p_list.add_argument(
        "category",
        choices=["themes", "waybar", "rofi", "starship", "hyprlock", "fonts", "keybinds", "glyphs"],
    )

    # detech menu <menu_name>
    p_menu = sub.add_parser("menu", help="Open an interactive Rofi picker menu")
    p_menu.add_argument(
        "menu_name",
        choices=[
            "apps",
            "keybinds",
            "themes",
            "wallpapers",
            "fonts",
            "icons",
            "colors",
            "waybar",
            "rofi-layout",
            "starship",
            "hyprlock",
            "files",
            "software",
            "glyphs",
        ],
    )

    # detech bsd <subsystem>
    p_bsd = sub.add_parser("bsd", help="FreeBSD hardware & OS integration commands")
    bsd_sub = p_bsd.add_subparsers(dest="bsd_subsystem", required=True)

    p_audio = bsd_sub.add_parser("audio", help="FreeBSD audio control (mixer / wpctl / pactl)")
    p_audio.add_argument("action", choices=["up", "down", "mute", "status"])
    p_audio.add_argument("step", nargs="?", type=int, default=5)
    p_audio.add_argument("--json", action="store_true")

    p_bl = bsd_sub.add_parser("backlight", help="FreeBSD display backlight control (/usr/bin/backlight)")
    p_bl.add_argument("action", choices=["up", "down", "set", "status"])
    p_bl.add_argument("step", nargs="?", type=int, default=5)
    p_bl.add_argument("--json", action="store_true")

    p_pow = bsd_sub.add_parser("power", help="FreeBSD ACPI battery, thermal, telemetry, and session power controls")
    p_pow.add_argument(
        "action",
        choices=["battery", "thermal", "load", "memory", "zfs", "lock", "suspend", "reboot", "poweroff", "logout"],
    )
    p_pow.add_argument("--json", action="store_true")

    p_pkg = bsd_sub.add_parser("pkg", help="FreeBSD pkg repository queries")
    p_pkg.add_argument("action", choices=["updates", "list", "search"])
    p_pkg.add_argument("query", nargs="?", default="")
    p_pkg.add_argument("--json", action="store_true")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "status":
        ctx = get_effective_context()
        theme_data, palette = resolve_active_palette(ctx)
        fonts = resolve_font_settings(ctx)
        appearance = ctx.get("config", {}).get("appearance", {})
        summary = {
            "os": ctx.get("freebsd", {}).get("os", "FreeBSD"),
            "theme": appearance.get("theme", "bsd-crimson"),
            "dynamic_wallpaper_colors": bool(appearance.get("dynamic_wallpaper_colors", False)),
            "waybar_layout": appearance.get("waybar_layout", "island-top"),
            "rofi_layout": appearance.get("rofi_layout", "grid-cards"),
            "starship_preset": appearance.get("starship_preset", "tokyo-pill"),
            "hyprlock_layout": appearance.get("hyprlock_layout", "minimal-clock"),
            "icon_theme": appearance.get("icon_theme", theme_data.get("icon_theme", "Papirus-Dark")),
            "font_mono": fonts["mono"],
            "font_sans": fonts["sans"],
            "font_size": fonts["size"],
            "accent_color": palette.get("accent"),
        }
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print("  DETech Status (FreeBSD Hyprland Environment)")
            print("=" * 48)
            for k, v in summary.items():
                print(f"  {k:<26}: {v}")
        return 0

    if args.command == "apply":
        result = compile_all(output_dir=args.output_dir, reload_daemons=not args.no_reload)
        print(f"✓ Compiled {len(result['written_files'])} configuration files into {result['output_dir']}")
        return 0

    if args.command == "set":
        t = args.target
        val = args.value
        if t == "theme":
            update_state(theme=val)
        elif t == "waybar":
            update_state(waybar_layout=val)
        elif t == "rofi":
            update_state(rofi_layout=val)
        elif t == "starship":
            update_state(starship_preset=val)
        elif t == "hyprlock":
            update_state(hyprlock_layout=val)
        elif t == "icon":
            update_state(icon_theme=val)
        elif t == "wallpaper":
            update_state(wallpaper=str(Path(val).expanduser().resolve()), dynamic_wallpaper_colors=True)
        elif t == "dynamic-colors":
            enabled = val.lower() in ("true", "1", "yes", "on")
            update_state(dynamic_wallpaper_colors=enabled)
        elif t == "font":
            updates: dict[str, object] = {
                "font_mono": val,
                "font_sans": f"{val} Propo" if not val.endswith("Propo") else val,
            }
            if args.size is not None:
                updates["font_size"] = args.size
            update_state(**updates)

        result = compile_all(output_dir=args.output_dir, reload_daemons=not args.no_reload)
        print(f"✓ Updated {t} -> {val} ({len(result['written_files'])} files updated)")
        return 0

    if args.command == "list":
        cat = args.category
        if cat == "themes":
            for item in list_themes():
                print(f"{item['name']:<20} — {item.get('display_name', '')}")
        elif cat == "waybar":
            for item in list_waybar_layouts():
                print(
                    f"{item['id']:<20} ({item.get('position', 'top'):<6} | {item.get('style_variant', ''):<16}) — {item.get('name', '')}"
                )
        elif cat == "rofi":
            for item in list_rofi_layouts():
                grid = f"{item.get('columns', 1)}x{item.get('lines', 5)}"
                print(f"{item['id']:<22} ({grid:<5} | {item.get('style_variant', ''):<13}) — {item.get('name', '')}")
        elif cat == "starship":
            for item in list_starship_prompts():
                print(f"{item['id']:<20} — {item.get('name', ''):<42}  {item.get('preview', '')}")
        elif cat == "hyprlock":
            for item in list_hyprlock_layouts():
                print(f"{item['id']:<20} — {item.get('name', '')}")
        elif cat == "fonts":
            for item in get_nerd_font_status_list():
                status = "installed" if item["installed"] else "available"
                print(f"{item['family']:<28} [{status:<9}] — {item['style_hint']}")
        elif cat == "keybinds":
            for item in format_keybind_entries():
                print(item["label"])
        elif cat == "glyphs":
            for item in format_glyph_entries():
                print(item["label"])
        return 0

    if args.command == "menu":
        m = args.menu_name
        if m == "apps":
            return launch_app_drawer()
        if m == "keybinds":
            open_keybinds_menu()
        elif m == "themes":
            open_theme_menu()
        elif m == "wallpapers":
            open_wallpaper_menu()
        elif m == "fonts":
            open_font_menu()
        elif m == "icons":
            open_icon_menu()
        elif m == "colors":
            open_color_scheme_menu()
        elif m == "waybar":
            open_waybar_layout_menu()
        elif m == "rofi-layout":
            open_rofi_layout_menu()
        elif m == "starship":
            open_starship_menu()
        elif m == "hyprlock":
            open_hyprlock_layout_menu()
        elif m == "files":
            open_file_browser()
        elif m == "software":
            open_software_menu()
        elif m == "glyphs":
            open_glyph_menu()
        return 0

    if args.command == "bsd":
        ctx = get_effective_context()
        fbsd = ctx.get("freebsd", {})
        subsys = args.bsd_subsystem

        if subsys == "audio":
            audio_cfg = fbsd.get("audio", {})
            info = run_audio_action(
                args.action,
                step=args.step,
                backend=audio_cfg.get("backend", "auto"),
                device=audio_cfg.get("oss_device", "/dev/mixer0"),
                notify=(args.action != "status"),
            )
            if getattr(args, "json", False):
                icon = "󰝟" if info["muted"] else "󰕾"
                print(
                    format_waybar_json(
                        {
                            "text": f"{icon} {info['volume']}%",
                            "tooltip": f"FreeBSD Audio Volume: {info['volume']}%",
                            "class": "muted" if info["muted"] else "unmuted",
                        }
                    )
                )
            else:
                print(f"Volume: {info['volume']}% (Muted: {info['muted']})")
            return 0

        if subsys == "backlight":
            bl_cfg = fbsd.get("backlight", {})
            info = run_backlight_action(
                args.action,
                step=args.step,
                backend=bl_cfg.get("backend", "backlight"),
                device=bl_cfg.get("device", "/dev/backlight/backlight0"),
                notify=(args.action != "status"),
            )
            if getattr(args, "json", False):
                print(
                    format_waybar_json(
                        {
                            "text": f"󰃠 {info['brightness']}%",
                            "tooltip": f"FreeBSD Display Backlight: {info['brightness']}%",
                        }
                    )
                )
            else:
                print(f"Brightness: {info['brightness']}%")
            return 0

        if subsys == "power":
            if args.action == "battery":
                bat = get_battery_status()
                print(format_waybar_json(bat) if args.json else bat["text"])
                return 0
            if args.action == "thermal":
                therm = get_thermal_status(fbsd.get("power", {}).get("thermal_sysctl", "hw.acpi.thermal.tz0.temperature"))
                print(format_waybar_json(therm) if args.json else therm["text"])
                return 0
            if args.action == "load":
                load_info = get_system_load_status()
                print(format_waybar_json(load_info) if args.json else load_info["text"])
                return 0
            if args.action == "memory":
                mem_info = get_memory_status()
                print(format_waybar_json(mem_info) if args.json else mem_info["text"])
                return 0
            if args.action == "zfs":
                zfs_info = get_zfs_status()
                print(format_waybar_json(zfs_info) if args.json else zfs_info["text"])
                return 0
            cmd = build_power_command(args.action, privilege_cmd=fbsd.get("privilege_cmd", "doas"))
            subprocess.run(cmd, check=False)
            return 0

        if subsys == "pkg":
            if args.action == "updates":
                print(get_pkg_updates_status())
                return 0
            if args.action == "list":
                for p in list_installed_packages():
                    print(f"{p['name']} ({p['version']}) - {p['comment']}")
                return 0
            if args.action == "search":
                for p in search_remote_packages(args.query):
                    print(f"{p['name']} ({p['version']}) - {p['comment']}")
                return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
