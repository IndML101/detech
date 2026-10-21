"""Configuration Compiler & Live Hot-Reload Orchestrator for DETech."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from detech.core.color_engine import resolve_active_palette
from detech.core.font_manager import resolve_font_settings
from detech.core.paths import get_xdg_config_dir
from detech.core.state import get_effective_context
from detech.generators.gtk_qt_dunst import generate_gtk_qt_dunst_configs
from detech.generators.hyprland import generate_hypr_configs
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

    if reload_daemons:
        trigger_hot_reload(context, theme_data, fonts)

    return {
        "context": context,
        "theme": theme_data,
        "palette": palette,
        "fonts": fonts,
        "output_dir": str(target_root),
        "written_files": [str(p) for p in written_files],
    }


def trigger_hot_reload(
    context: dict[str, Any],
    theme_data: dict[str, Any],
    fonts: dict[str, Any],
) -> None:
    """Trigger non-disruptive live reloads for Hyprland, Waybar, Kitty, Hyprpaper, and GTK."""
    appearance = context.get("config", {}).get("appearance", {})

    if shutil.which("hyprctl"):
        subprocess.run(["hyprctl", "reload"], check=False, capture_output=True)
        wallpaper = appearance.get("wallpaper")
        if wallpaper and Path(wallpaper).expanduser().is_file():
            wall_str = str(Path(wallpaper).expanduser())
            subprocess.run(["hyprctl", "hyprpaper", "preload", wall_str], check=False, capture_output=True)
            subprocess.run(["hyprctl", "hyprpaper", "wallpaper", f",{wall_str}"], check=False, capture_output=True)

    if shutil.which("pkill"):
        subprocess.run(["pkill", "-USR2", "waybar"], check=False, capture_output=True)
        subprocess.run(["pkill", "-USR1", "kitty"], check=False, capture_output=True)

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
