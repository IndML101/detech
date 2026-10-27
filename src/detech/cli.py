"""Main CLI entrypoint for DETech (`detech`)."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from detech.core.color_engine import list_themes, load_theme, resolve_active_palette
from detech.core.compiler import compile_all
from detech.core.font_manager import get_nerd_font_status_list, resolve_font_settings
from detech.core.paths import get_xdg_config_dir
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
from detech.freebsd.widgets import (
    get_calendar_status,
    get_clipboard_status,
    get_dnd_status,
    get_media_status,
    get_network_status,
    get_uptime_kernel_status,
    get_weather_status,
    run_media_action,
)
from detech.generators.hyprland import list_hyprlock_layouts, list_plugin_presets
from detech.generators.rofi import list_rofi_layouts
from detech.generators.terminal_shell import list_starship_prompts
from detech.generators.waybar import list_waybar_layouts
from detech.freebsd.bluetooth import get_bluetooth_status
from detech.menus.bluetooth_menu import open_bluetooth_menu
from detech.menus.wifi_menu import open_wifi_menu
from detech.menus.file_browser import open_file_browser
from detech.menus.font_menu import open_font_menu
from detech.menus.glyph_emoji_menu import format_glyph_entries, open_glyph_menu
from detech.menus.keybinds_menu import format_keybind_entries, open_keybinds_menu
from detech.menus.layout_menu import (
    open_hyprlock_layout_menu,
    open_plugins_menu,
    open_rofi_layout_menu,
    open_starship_menu,
    open_waybar_layout_menu,
)
from detech.menus.pkg_menu import open_software_menu
from detech.menus.rofi_runner import launch_app_drawer
from detech.core.cursor_manager import (
    TRACKPAD_CURSOR_SIZES,
    list_cursor_themes,
)
from detech.core.folder_colors import (
    PAPIRUS_FOLDER_COLORS,
    resolve_folder_color,
)
from detech.menus.theme_menu import (
    list_icon_themes,
    open_color_scheme_menu,
    open_cursor_menu,
    open_cursor_size_menu,
    open_folder_color_menu,
    open_icon_menu,
    open_theme_menu,
)
from detech.menus.wallpaper_menu import open_wallpaper_menu
from detech.menus.screenshot_menu import open_screenshot_menu
from detech.screenshot import capture_screenshot
from detech.menus.widget_menus import (
    open_calendar_menu,
    open_clipboard_menu,
    open_notifications_menu,
    open_weather_menu,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="detech",
        description="DETech — FreeBSD Hyprland Desktop Environment Engine (Lua + Python)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # detech status
    p_status = sub.add_parser("status", help="Show active DETech configuration & runtime state")
    p_status.add_argument("--json", action="store_true", help="Output status as JSON")

    # detech fetch
    p_fetch = sub.add_parser("fetch", help="Display FreeBSD + DETech system information in terminal via Neofetch")
    p_fetch.add_argument("--config-dir", type=Path, default=None, help="Override XDG ~/.config directory")

    # detech apply
    p_apply = sub.add_parser("apply", help="Compile Lua configs into native Hypr/Waybar/Rofi/Kitty/Starship configs")
    p_apply.add_argument("--output-dir", type=Path, default=None, help="Override target XDG ~/.config directory")
    p_apply.add_argument("--no-reload", action="store_true", help="Do not trigger live daemon reloads")

    # detech session
    p_sess = sub.add_parser("session", help="Compile configs and launch DETech Hyprland Wayland session")

    # detech set <target> <value>
    p_set = sub.add_parser("set", help="Update a DETech preset, theme, font, or layout and recompile")
    p_set.add_argument(
        "target",
        choices=[
            "theme",
            "waybar",
            "rofi",
            "starship",
            "hyprlock",
            "plugins",
            "font",
            "icon",
            "cursor",
            "cursor-size",
            "folder-color",
            "wallpaper",
            "dynamic-colors",
            "neofetch",
            "weather-location",
            "weather-units",
            "screenshot-dir",
        ],
    )
    p_set.add_argument("value", help="New value for the target setting")
    p_set.add_argument("--size", type=int, default=None, help="Font or cursor size (when setting font or cursor)")
    p_set.add_argument("--output-dir", type=Path, default=None, help="Override target XDG ~/.config directory")
    p_set.add_argument("--no-reload", action="store_true", help="Skip live daemon reload")

    # detech screenshot [mode]
    p_shot = sub.add_parser("screenshot", help="Capture desktop screenshot or launch interactive picker")
    p_shot.add_argument(
        "mode",
        nargs="?",
        default="menu",
        choices=["menu", "full", "area", "window"],
        help="Capture mode: menu, full, area, or window (default: menu)",
    )
    p_shot.add_argument(
        "-t",
        "--target",
        choices=["both", "save", "copy", "edit"],
        default="both",
        help="Destination: both (save & clipboard), save, copy, or edit (default: both)",
    )
    p_shot.add_argument("-o", "--output", type=Path, default=None, help="Custom output file or directory")
    p_shot.add_argument("-d", "--delay", type=int, default=0, help="Countdown delay in seconds")
    p_shot.add_argument("-c", "--cursor", action="store_true", help="Include mouse cursor in screenshot")
    p_shot.add_argument("--no-notify", action="store_true", help="Do not send desktop notification")
    p_shot.add_argument("--json", action="store_true", help="Output result as JSON")

    # detech list <category>
    p_list = sub.add_parser("list", help="List available themes, layouts, prompts, plugins, Nerd Fonts, icons, or keybinds")
    p_list.add_argument(
        "category",
        choices=[
            "themes",
            "waybar",
            "rofi",
            "starship",
            "hyprlock",
            "plugins",
            "fonts",
            "icons",
            "cursors",
            "folder-colors",
            "keybinds",
            "glyphs",
        ],
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
            "cursor",
            "cursors",
            "cursor-size",
            "folder-color",
            "folder-colors",
            "colors",
            "waybar",
            "rofi-layout",
            "starship",
            "hyprlock",
            "plugins",
            "files",
            "software",
            "glyphs",
            "calendar",
            "weather",
            "clipboard",
            "notifications",
            "wifi",
            "bluetooth",
            "screenshot",
        ],
    )

    # detech cursor [theme]
    p_cur = sub.add_parser("cursor", help="Select or list cursor themes for trackpad & high-DPI")
    p_cur.add_argument("theme", nargs="?", default=None, help="Cursor theme name to apply")
    p_cur.add_argument("--size", type=int, default=None, help="Cursor size in px (e.g. 24, 28, 32, 36, 48)")
    p_cur.add_argument("--list", action="store_true", help="List available cursor themes")

    # detech folder-color [color]
    p_fc = sub.add_parser("folder-color", help="Set or list Thunar theme-matched folder icon colors")
    p_fc.add_argument("color", nargs="?", default=None, help="Folder color (e.g. auto, carmine, red, cyan, green, violet)")
    p_fc.add_argument("--list", action="store_true", help="List available folder color variants")

    # detech term-colors
    p_tc = sub.add_parser("term-colors", help="Synchronize active theme colors to terminal via OSC escape codes")
    p_tc.add_argument("--print", action="store_true", help="Print escape code sequences to stdout")

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

    p_widgets = bsd_sub.add_parser("widgets", help="Waybar widgets (weather, calendar, network, bluetooth, media, dnd, uptime, clipboard)")
    p_widgets.add_argument(
        "widget",
        choices=["weather", "calendar", "network", "bluetooth", "media", "dnd", "uptime", "clipboard"],
    )
    p_widgets.add_argument("subaction", nargs="?", default="status")
    p_widgets.add_argument("--json", action="store_true")
    p_widgets.add_argument("--location", default=None, help="Override weather city/location")
    p_widgets.add_argument("--units", default=None, help="Override weather units (m or u)")

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
            "plugin_preset": ctx.get("plugins", {}).get("preset", "minimal-expo"),
            "icon_theme": appearance.get("icon_theme", theme_data.get("icon_theme", "Papirus-Dark")),
            "folder_color": appearance.get("folder_color", theme_data.get("folder_color", "auto")),
            "cursor_theme": appearance.get("cursor_theme", theme_data.get("cursor_theme", "Bibata-Modern-Ice")),
            "cursor_size": appearance.get("cursor_size", 24),
            "font_mono": fonts["mono"],
            "font_sans": fonts["sans"],
            "font_size": fonts["size"],
            "accent_color": palette.get("accent"),
            "terminal": ctx.get("config", {}).get("general", {}).get("terminal", "kitty"),
            "shell": ctx.get("config", {}).get("general", {}).get("shell", "zsh"),
            "login_manager": ctx.get("freebsd", {}).get("login_manager", {}).get("manager", "ly"),
            "login_animation": ctx.get("freebsd", {}).get("login_manager", {}).get("animation", "matrix"),
        }
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print("  DETech Status (FreeBSD Hyprland Environment)")
            print("=" * 48)
            for k, v in summary.items():
                print(f"  {k:<26}: {v}")
        return 0

    if args.command == "fetch":
        cfg_root = get_xdg_config_dir(args.config_dir)
        nf_conf = cfg_root / "neofetch" / "config.conf"
        if shutil.which("neofetch"):
            cmd = ["neofetch"]
            if nf_conf.is_file():
                cmd.extend(["--config", str(nf_conf)])
            subprocess.run(cmd, check=False)
        else:
            ctx = get_effective_context()
            _, palette = resolve_active_palette(ctx)
            fonts = resolve_font_settings(ctx)
            appearance = ctx.get("config", {}).get("appearance", {})
            up = get_uptime_kernel_status()
            mem = get_memory_status()
            zfs = get_zfs_status()
            print("   _       _       FreeBSD — DETech Hyprland")
            print("  / \\     / \\    ──────────────────────────────")
            print(f" (   \\___/   )    Kernel   ❯ {up['kernel']}")
            print(f"  \\         /    󱎫 Uptime   ❯ {up['uptime']}")
            print(f"   |  O O  |      WM       ❯ Hyprland ({appearance.get('waybar_layout', 'island-top')})")
            print(f"   |   v   |     󰔎 Theme    ❯ {appearance.get('theme', 'bsd-crimson')} ({palette['accent']})")
            print(f"    \\_____/      󰛖 Font     ❯ {fonts['mono']} ({fonts['size']}pt)")
            print(f"                 󰘚 Memory   ❯ {mem['text']}")
            print(f"                 󰋊 ZFS      ❯ {zfs['text']}")
        return 0

    if args.command == "apply":
        result = compile_all(output_dir=args.output_dir, reload_daemons=not args.no_reload)
        print(f"✓ Compiled {len(result['written_files'])} configuration files into {result['output_dir']}")
        return 0

    if args.command == "session":
        try:
            compile_all(reload_daemons=False)
        except Exception:
            pass
        hyprland_bin = (
            shutil.which("start-hyprland")
            or shutil.which("Hyprland")
            or "/usr/local/bin/start-hyprland"
        )
        os.environ["XDG_CURRENT_DESKTOP"] = "Hyprland"
        os.environ["XDG_SESSION_DESKTOP"] = "Hyprland"
        os.environ["XDG_SESSION_TYPE"] = "wayland"
        os.execv(hyprland_bin, [hyprland_bin])

    if args.command == "set":
        t = args.target
        val = args.value
        if t == "theme":
            try:
                t_obj = load_theme(val)
                theme_updates: dict[str, object] = {"theme": val}
                if "default_waybar" in t_obj:
                    theme_updates["waybar_layout"] = t_obj["default_waybar"]
                if "default_rofi" in t_obj:
                    theme_updates["rofi_layout"] = t_obj["default_rofi"]
                if "default_starship" in t_obj:
                    theme_updates["starship_preset"] = t_obj["default_starship"]
                if "default_hyprlock" in t_obj:
                    theme_updates["hyprlock_layout"] = t_obj["default_hyprlock"]
                if "icon_theme" in t_obj:
                    theme_updates["icon_theme"] = t_obj["icon_theme"]
                update_state(**theme_updates)
            except Exception:
                update_state(theme=val)
        elif t == "waybar":
            update_state(waybar_layout=val)
        elif t == "rofi":
            update_state(rofi_layout=val)
        elif t == "starship":
            update_state(starship_preset=val)
        elif t == "hyprlock":
            update_state(hyprlock_layout=val)
        elif t == "plugins":
            update_state(plugin_preset=val)
        elif t == "icon":
            update_state(icon_theme=val)
        elif t == "cursor":
            updates = {"cursor_theme": val}
            if args.size is not None:
                updates["cursor_size"] = args.size
            update_state(**updates)
        elif t == "cursor-size":
            update_state(cursor_size=int(val))
        elif t == "folder-color":
            update_state(folder_color=val)
        elif t == "wallpaper":
            update_state(wallpaper=str(Path(val).expanduser().resolve()), dynamic_wallpaper_colors=True)
        elif t == "dynamic-colors":
            enabled = val.lower() in ("true", "1", "yes", "on")
            update_state(dynamic_wallpaper_colors=enabled)
        elif t == "neofetch":
            enabled = val.lower() in ("true", "1", "yes", "on")
            update_state(enable_neofetch=enabled)
        elif t == "weather-location":
            update_state(weather_location=val)
        elif t == "weather-units":
            update_state(weather_units=val)
        elif t == "screenshot-dir":
            update_state(screenshot_dir=str(Path(val).expanduser().resolve()))
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
        elif cat == "plugins":
            for item in list_plugin_presets():
                print(f"{item['id']:<20} — {item.get('name', '')} ({item.get('description', '')})")
        elif cat == "fonts":
            for item in get_nerd_font_status_list():
                status = "installed" if item["installed"] else "available"
                print(f"{item['family']:<28} [{status:<9}] — {item['style_hint']}")
        elif cat == "icons":
            ctx = get_effective_context()
            cur_icon = ctx.get("config", {}).get("appearance", {}).get("icon_theme", "Papirus-Dark")
            for item in list_icon_themes(active_icon=cur_icon):
                status = "active" if item["active"] else ("installed" if item["installed"] else "available")
                print(f"{item['id']:<22} [{status:<9}] — {item['description']} (pkg: {item['pkg']})")
        elif cat == "cursors":
            ctx = get_effective_context()
            cur_cursor = ctx.get("config", {}).get("appearance", {}).get("cursor_theme", "Bibata-Modern-Ice")
            for item in list_cursor_themes(active_cursor=cur_cursor):
                status = "active" if item["active"] else ("installed" if item["installed"] else "available")
                opt = " [trackpad-optimized]" if item["trackpad_optimized"] else ""
                print(f"{item['id']:<28} [{status:<9}]{opt} — {item['description']} (pkg: {item['pkg']})")
        elif cat == "folder-colors":
            ctx = get_effective_context()
            cur_fc = ctx.get("config", {}).get("appearance", {}).get("folder_color", "auto")
            print(f"{'auto':<16} [{'active' if cur_fc == 'auto' else 'available':<9}] — Automatically match theme accent palette")
            for cname, info in PAPIRUS_FOLDER_COLORS.items():
                status = "active" if cname == cur_fc else "available"
                print(f"{cname:<16} [{status:<9}] — {info['name']} (Hex: {info['hex']})")
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
        elif m in ("cursor", "cursors"):
            open_cursor_menu()
        elif m == "cursor-size":
            open_cursor_size_menu()
        elif m in ("folder-color", "folder-colors"):
            open_folder_color_menu()
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
        elif m == "plugins":
            open_plugins_menu()
        elif m == "files":
            open_file_browser()
        elif m == "software":
            open_software_menu()
        elif m == "glyphs":
            open_glyph_menu()
        elif m == "calendar":
            open_calendar_menu()
        elif m == "weather":
            ctx = get_effective_context()
            w_cfg = ctx.get("config", {}).get("widgets", {}).get("weather", {})
            open_weather_menu(
                location=str(w_cfg.get("location", "")),
                units=str(w_cfg.get("units", "m")),
            )
        elif m == "clipboard":
            open_clipboard_menu()
        elif m == "notifications":
            open_notifications_menu()
        elif m == "wifi":
            open_wifi_menu()
        elif m == "bluetooth":
            open_bluetooth_menu()
        elif m == "screenshot":
            open_screenshot_menu()
        return 0

    if args.command == "cursor":
        if args.list:
            ctx = get_effective_context()
            cur_cursor = ctx.get("config", {}).get("appearance", {}).get("cursor_theme", "Bibata-Modern-Ice")
            for item in list_cursor_themes(active_cursor=cur_cursor):
                status = "active" if item["active"] else ("installed" if item["installed"] else "available")
                opt = " [trackpad-optimized]" if item["trackpad_optimized"] else ""
                print(f"{item['id']:<28} [{status:<9}]{opt} — {item['description']}")
            return 0
        if args.theme:
            updates: dict[str, object] = {"cursor_theme": args.theme}
            if args.size is not None:
                updates["cursor_size"] = args.size
            update_state(**updates)
            compile_all(reload_daemons=True)
            print(f"✓ Applied cursor theme: {args.theme}" + (f" ({args.size}px)" if args.size else ""))
            return 0
        open_cursor_menu()
        return 0

    if args.command == "folder-color":
        if args.list:
            ctx = get_effective_context()
            cur_fc = ctx.get("config", {}).get("appearance", {}).get("folder_color", "auto")
            print(f"{'auto':<16} [{'active' if cur_fc == 'auto' else 'available':<9}] — Automatically match theme accent palette")
            for cname, info in PAPIRUS_FOLDER_COLORS.items():
                status = "active" if cname == cur_fc else "available"
                print(f"{cname:<16} [{status:<9}] — {info['name']} (Hex: {info['hex']})")
            return 0
        if args.color:
            update_state(folder_color=args.color)
            compile_all(reload_daemons=True)
            print(f"✓ Applied Thunar folder color: {args.color}")
            return 0
        open_folder_color_menu()
        return 0

    if args.command == "term-colors":
        ctx = get_effective_context()
        _, palette = resolve_active_palette(ctx)
        from detech.generators.terminal_shell import render_term_colors_sh
        script = render_term_colors_sh(palette)
        if args.print:
            print(script, end="")
        else:
            for line in script.splitlines():
                if line.startswith("printf "):
                    seq = line.split("printf ")[1].strip("'\"")
                    formatted = seq.replace("\\033", "\x1b").replace("\\007", "\x07")
                    sys.stdout.write(formatted)
            sys.stdout.flush()
            print("✓ Synchronized terminal text color palette with active DETech theme.")
        return 0

    if args.command == "screenshot":
        if args.mode == "menu":
            res = open_screenshot_menu()
            if res and getattr(args, "json", False):
                print(json.dumps(res, indent=2))
            return 0 if res else 1

        res = capture_screenshot(
            mode=args.mode,
            target=args.target,
            output=args.output,
            delay=args.delay,
            include_cursor=args.cursor,
            notify=not args.no_notify,
        )
        if getattr(args, "json", False):
            print(json.dumps(res, indent=2))
        elif res.get("status") == "success":
            print(f"✓ Screenshot captured: {res['path']}")
            if res.get("copied"):
                print("  󰅌 Copied to Wayland clipboard (image/png)")
            if res.get("edited"):
                print("   Launched image annotator")
        elif res.get("status") == "cancelled":
            print("Screenshot selection cancelled.")
        else:
            print(f"Error: {res.get('message', 'Capture failed')}", file=sys.stderr)
            return 1
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
            if args.action == "logout" and shutil.which("hyprctl"):
                res = subprocess.run(
                    ["hyprctl", "dispatch", "hl.dsp.exit()"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if "Invalid dispatcher" not in (res.stdout or ""):
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

        if subsys == "widgets":
            w_cfg = ctx.get("config", {}).get("widgets", {})
            _, palette = resolve_active_palette(ctx)
            w_type = args.widget

            if w_type == "weather":
                weather_conf = w_cfg.get("weather", {})
                loc = args.location if args.location is not None else str(weather_conf.get("location", ""))
                units = args.units if args.units is not None else str(weather_conf.get("units", "m"))
                ttl = int(weather_conf.get("interval", 900))
                res = get_weather_status(location=loc, units=units, cache_ttl=ttl)
            elif w_type == "calendar":
                res = get_calendar_status(accent_color=palette.get("accent", "#e64553"))
            elif w_type == "network":
                res = get_network_status()
            elif w_type == "bluetooth":
                res = get_bluetooth_status()
            elif w_type == "media":
                if args.subaction in ("play-pause", "next", "prev"):
                    res = run_media_action(args.subaction)
                else:
                    res = get_media_status()
            elif w_type == "dnd":
                res = get_dnd_status(action=args.subaction)
            elif w_type == "uptime":
                res = get_uptime_kernel_status()
            else:
                res = get_clipboard_status(clear=(args.subaction == "clear"))

            print(format_waybar_json(res) if args.json else res["text"])
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
