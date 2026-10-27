"""Configuration Compiler & Live Hot-Reload Orchestrator for DETech."""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from detech.core.color_engine import resolve_active_palette
from detech.core.cursor_manager import apply_cursor_live, sync_default_cursor_theme
from detech.core.folder_colors import resolve_folder_color, sync_theme_folder_icons
from detech.core.font_manager import resolve_font_settings
from detech.core.paths import get_xdg_config_dir
from detech.core.state import get_effective_context
from detech.generators.gtk_qt_dunst import generate_gtk_qt_dunst_configs
from detech.generators.hyprland import generate_hypr_configs
from detech.generators.ly import generate_ly_configs
from detech.generators.rofi import generate_rofi_configs
from detech.generators.terminal_shell import generate_terminal_and_shell_configs
from detech.generators.waybar import generate_waybar_configs


def compile_all(
    output_dir: Path | str | None = None,
    state_path: Path | None = None,
    reload_daemons: bool = False,
) -> dict[str, Any]:
    """Compile all declarative Lua configs + runtime state into native configuration files."""
    context = get_effective_context(state_path=state_path)
    theme_data, palette = resolve_active_palette(context)
    fonts = resolve_font_settings(context)
    target_root = get_xdg_config_dir(output_dir)

    written_files: list[Path] = []
    written_files.extend(generate_hypr_configs(context, palette, fonts, target_root))
    written_files.extend(generate_waybar_configs(context, palette, fonts, target_root))
    written_files.extend(generate_rofi_configs(context, palette, fonts, target_root))
    written_files.extend(generate_terminal_and_shell_configs(context, palette, fonts, target_root))
    written_files.extend(generate_gtk_qt_dunst_configs(context, theme_data, palette, fonts, target_root))
    written_files.extend(generate_ly_configs(context, palette, fonts, target_root))

    # Synchronize theme-colored folder icons for Thunar and GTK file choosers
    appearance = context.get("config", {}).get("appearance", {})
    icon_theme = appearance.get("icon_theme") or theme_data.get("icon_theme", "Papirus-Dark")
    cursor_theme = appearance.get("cursor_theme") or theme_data.get("cursor_theme", "Bibata-Modern-Ice")
    cursor_size = appearance.get("cursor_size", 24)

    if output_dir is not None:
        icons_dir = target_root.parent / "share" / "icons"
        user_icons_legacy = target_root.parent / "icons"
    else:
        icons_dir = Path(os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))) / "icons"
        user_icons_legacy = Path.home() / ".icons"

    folder_color = resolve_folder_color(theme_data, palette, appearance)
    written_files.extend(
        sync_theme_folder_icons(folder_color, palette, target_icons_dir=icons_dir, base_theme_name=icon_theme)
    )
    written_files.append(sync_default_cursor_theme(cursor_theme, target_icons_dir=user_icons_legacy))

    if reload_daemons:
        trigger_hot_reload(context, theme_data, fonts, target_root=target_root)

    return {
        "context": context,
        "theme": theme_data,
        "palette": palette,
        "fonts": fonts,
        "output_dir": str(target_root),
        "written_files": [str(p) for p in written_files],
    }


def reload_wallpaper(
    appearance: dict[str, Any],
    target_root: Path | None = None,
) -> None:
    """Hot-reload wallpaper live via swaybg, hyprpaper IPC, or wallpaper launcher."""
    wallpaper = appearance.get("wallpaper")
    wall_path = Path(wallpaper).expanduser() if wallpaper else None
    wall_str = str(wall_path) if wall_path and wall_path.is_file() else None

    config_dir = target_root or get_xdg_config_dir()
    wp_launcher = config_dir / "hypr" / "launch-wallpaper.sh"

    # 1. Prefer swaybg when available (fastest, most reliable Wayland wallpaper daemon on FreeBSD)
    if shutil.which("swaybg") and wall_str:
        launched = False
        cmd = f"{wp_launcher} {wall_str}" if wp_launcher.is_file() else f"swaybg -i {wall_str} -m fill"
        if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE") and shutil.which("hyprctl"):
            subprocess.run(["pkill", "-x", "hyprpaper"], check=False, capture_output=True)
            subprocess.run(["pkill", "-x", "swaybg"], check=False, capture_output=True)
            time.sleep(0.1)
            dsp_res = subprocess.run(
                ["hyprctl", "dispatch", f'hl.dsp.exec_cmd("{cmd}")'],
                check=False,
                capture_output=True,
                text=True,
            )
            if dsp_res.returncode == 0 and "ok" in (dsp_res.stdout or "").lower():
                launched = True
            elif "Invalid dispatcher" in (dsp_res.stdout or "") or dsp_res.returncode != 0:
                dsp_res2 = subprocess.run(
                    ["hyprctl", "dispatch", "exec", cmd],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if dsp_res2.returncode == 0 and "ok" in (dsp_res2.stdout or "").lower():
                    launched = True
        if not launched:
            subprocess.run(["pkill", "-x", "hyprpaper"], check=False, capture_output=True)
            subprocess.run(["pkill", "-x", "swaybg"], check=False, capture_output=True)
            time.sleep(0.1)
            if wp_launcher.is_file():
                subprocess.Popen([str(wp_launcher), wall_str], start_new_session=True)
            else:
                subprocess.Popen(["swaybg", "-i", wall_str, "-m", "fill"], start_new_session=True)
        return

    # 2. Try hyprpaper dynamic IPC
    ipc_applied = False
    if wall_str and shutil.which("hyprctl") and os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        res = subprocess.run(
            ["hyprctl", "hyprpaper", "wallpaper", f",{wall_str},cover"],
            check=False,
            capture_output=True,
            text=True,
        )
        if res.returncode == 0 and "error" not in (res.stdout or "").lower() and "error" not in (res.stderr or "").lower():
            ipc_applied = True
        else:
            res2 = subprocess.run(
                ["hyprctl", "hyprpaper", "wallpaper", f",{wall_str}"],
                check=False,
                capture_output=True,
                text=True,
            )
            if res2.returncode == 0 and "error" not in (res2.stdout or "").lower() and "error" not in (res2.stderr or "").lower():
                ipc_applied = True

    # 3. If hyprpaper IPC failed (e.g. AF_UNIX socket path > 104 bytes on FreeBSD), restart hyprpaper
    if not ipc_applied and shutil.which("hyprpaper"):
        subprocess.run(["pkill", "-x", "hyprpaper"], check=False, capture_output=True)
        time.sleep(0.1)
        cmd = str(wp_launcher) if wp_launcher.is_file() else "hyprpaper"
        launched = False
        if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE") and shutil.which("hyprctl"):
            dsp_res = subprocess.run(
                ["hyprctl", "dispatch", f'hl.dsp.exec_cmd("{cmd}")'],
                check=False,
                capture_output=True,
                text=True,
            )
            if dsp_res.returncode == 0 and "ok" in (dsp_res.stdout or "").lower():
                launched = True
            elif "Invalid dispatcher" in (dsp_res.stdout or "") or dsp_res.returncode != 0:
                dsp_res2 = subprocess.run(
                    ["hyprctl", "dispatch", "exec", cmd],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if dsp_res2.returncode == 0 and "ok" in (dsp_res2.stdout or "").lower():
                    launched = True
        if not launched:
            subprocess.Popen(["hyprpaper"], start_new_session=True)


def trigger_hot_reload(
    context: dict[str, Any],
    theme_data: dict[str, Any],
    fonts: dict[str, Any],
    target_root: Path | None = None,
) -> None:
    """Trigger non-disruptive live reloads for Hyprland, Waybar, Kitty, Wallpaper, and GTK."""
    appearance = context.get("config", {}).get("appearance", {})

    if shutil.which("hyprctl"):
        probe = subprocess.run(
            ["hyprctl", "dispatch", "hl.dsp.no_op()"],
            check=False,
            capture_output=True,
            text=True,
        )
        if "Invalid dispatcher" in (probe.stdout or ""):
            subprocess.run(["hyprctl", "reload", "full-reset"], check=False, capture_output=True)
        else:
            subprocess.run(["hyprctl", "reload"], check=False, capture_output=True)

    reload_wallpaper(appearance, target_root=target_root)

    if shutil.which("pkill"):
        wb_res = subprocess.run(["pkill", "-USR2", "waybar"], check=False, capture_output=True)
        if wb_res.returncode != 0 and os.environ.get("HYPRLAND_INSTANCE_SIGNATURE") and shutil.which("hyprctl"):
            wb_cmd = "waybar"
            config_dir = target_root or get_xdg_config_dir()
            wb_launcher = config_dir / "hypr" / "launch-waybar.sh"
            if wb_launcher.is_file():
                wb_cmd = str(wb_launcher)
            dsp_res = subprocess.run(
                ["hyprctl", "dispatch", f'hl.dsp.exec_cmd("{wb_cmd}")'],
                check=False,
                capture_output=True,
                text=True,
            )
            if "Invalid dispatcher" in (dsp_res.stdout or ""):
                subprocess.run(["hyprctl", "dispatch", "exec", wb_cmd], check=False, capture_output=True)
        subprocess.run(["pkill", "-USR1", "kitty"], check=False, capture_output=True)
        subprocess.run(["pkill", "-USR1", "foot"], check=False, capture_output=True)

    if shutil.which("thunar"):
        subprocess.run(["thunar", "-q"], check=False, capture_output=True)

    cursor_theme = appearance.get("cursor_theme") or theme_data.get("cursor_theme", "Bibata-Modern-Ice")
    cursor_size = appearance.get("cursor_size", 24)
    apply_cursor_live(cursor_theme, cursor_size)

    if shutil.which("dunstctl"):
        subprocess.run(["dunstctl", "reload"], check=False, capture_output=True)

    if shutil.which("gsettings"):
        gtk_theme = theme_data.get("gtk_theme", "Adwaita-dark")
        icon_theme = appearance.get("icon_theme") or theme_data.get("icon_theme", "Papirus-Dark")
        font_name = f"{fonts['sans']} {fonts['size']}"
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", gtk_theme],
            check=False,
            capture_output=True,
        )
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", icon_theme],
            check=False,
            capture_output=True,
        )
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.interface", "font-name", font_name],
            check=False,
            capture_output=True,
        )
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", "prefer-dark"],
            check=False,
            capture_output=True,
        )
