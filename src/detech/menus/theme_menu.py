"""Rofi Theme, Color Scheme, and Icon Pack Pickers."""

from __future__ import annotations

from typing import Any

from detech.core.color_engine import list_themes
from detech.core.compiler import compile_all
from detech.core.state import get_effective_context, update_state
from detech.menus.rofi_runner import run_rofi_dmenu

ICON_PACK_CATALOG: list[tuple[str, str]] = [
    ("Papirus-Dark", "Papirus Dark (Crisp flat vector icons)"),
    ("Papirus-Light", "Papirus Light (For high-contrast light/pastel setups)"),
    ("Tela-circle", "Tela Circle (Modern circular colorful icons)"),
    ("Catppuccin-SE", "Catppuccin Soothing Pastel Icons"),
    ("Gruvbox-Plus-Dark", "Gruvbox Retro Warm Icon Pack"),
    ("Adwaita", "FreeBSD / GNOME Standard Fallback Icons"),
]


def build_theme_menu_entries(active_theme: str = "bsd-crimson") -> list[dict[str, Any]]:
    """Build Rofi menu entries for all available DETech themes."""
    themes = list_themes()
    entries: list[dict[str, Any]] = []
    for t in themes:
        name = t.get("name", "")
        disp = t.get("display_name", name)
        accent = t.get("colors", {}).get("accent", "#e63946")
        mark = "★ Active" if name == active_theme else "Switch"
        label = f"󰔎  {disp:<36} [{mark}] (Accent: {accent})"
        entries.append(
            {
                "name": name,
                "label": label,
                "theme": t,
            }
        )
    return entries


def open_theme_menu() -> dict[str, Any] | None:
    """Open Rofi Theme Picker and apply the selected theme (including its default layouts/icons)."""
    ctx = get_effective_context()
    active_theme = ctx.get("config", {}).get("appearance", {}).get("theme", "bsd-crimson")
    entries = build_theme_menu_entries(active_theme=active_theme)
    chosen = run_rofi_dmenu(
        [e["label"] for e in entries],
        prompt="󰔎  Themes",
        mesg="Switch full DETech theme (colors, GTK/Qt, icons, and matching defaults)",
    )
    if not chosen:
        return None

    for item in entries:
        if item["label"] == chosen:
            t = item["theme"]
            update_state(
                theme=item["name"],
                icon_theme=t.get("icon_theme", "Papirus-Dark"),
                waybar_layout=t.get("default_waybar", "island-top"),
                rofi_layout=t.get("default_rofi", "grid-cards"),
                starship_preset=t.get("default_starship", "tokyo-pill"),
            )
            compile_all(reload_daemons=True)
            return item
    return None


def open_color_scheme_menu() -> str | None:
    """Open Rofi Color Scheme & Dynamic Wallpaper Mode Picker."""
    ctx = get_effective_context()
    appearance = ctx.get("config", {}).get("appearance", {})
    dynamic = bool(appearance.get("dynamic_wallpaper_colors", False))
    active_theme = appearance.get("theme", "bsd-crimson")

    options: list[tuple[str, dict[str, Any]]] = [
        (
            f"󰸉  Dynamic Wallpaper Colors: {'ON (Active)' if dynamic else 'OFF'} — Extract palette from wallpaper",
            {"dynamic_wallpaper_colors": not dynamic},
        ),
    ]
    for t in list_themes():
        tname = t.get("name", "")
        disp = t.get("display_name", tname)
        is_cur = (not dynamic) and (tname == active_theme)
        badge = "★ Active Palette" if is_cur else "Apply Palette Only"
        options.append(
            (
                f"  {disp:<34} [{badge}]",
                {"theme": tname, "dynamic_wallpaper_colors": False},
            )
        )

    chosen = run_rofi_dmenu(
        [label for label, _ in options],
        prompt="  Colors",
        mesg="Switch system-wide color palette or toggle dynamic wallpaper color extraction",
    )
    if not chosen:
        return None

    for label, state_updates in options:
        if label == chosen:
            update_state(**state_updates)
            compile_all(reload_daemons=True)
            return label
    return None


def open_icon_menu() -> str | None:
    """Open Rofi Icon Pack Picker and update GTK/Qt/Rofi icon themes."""
    ctx = get_effective_context()
    current_icon = ctx.get("config", {}).get("appearance", {}).get("icon_theme", "Papirus-Dark")
    rows = []
    for pack_id, desc in ICON_PACK_CATALOG:
        badge = "★ Active" if pack_id == current_icon else "Apply"
        rows.append((f"󰀻  {pack_id:<22} [{badge}] — {desc}", pack_id))

    chosen = run_rofi_dmenu(
        [r[0] for r in rows],
        prompt="󰀻  Icons",
        mesg=f"Active Icon Theme: {current_icon}",
    )
    if not chosen:
        return None

    for label, pack_id in rows:
        if label == chosen:
            update_state(icon_theme=pack_id)
            compile_all(reload_daemons=True)
            return pack_id
    return None
