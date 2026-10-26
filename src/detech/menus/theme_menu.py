"""Rofi Theme, Color Scheme, and Icon Pack Pickers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from detech.core.color_engine import list_themes
from detech.core.compiler import compile_all
from detech.core.state import get_effective_context, update_state
from detech.menus.rofi_runner import run_rofi_dmenu

ICON_PACK_CATALOG: list[tuple[str, str, str]] = [
    ("Papirus-Dark", "Papirus Dark (Crisp flat vector icons)", "papirus-icon-theme"),
    ("Papirus-Light", "Papirus Light (For high-contrast light/pastel setups)", "papirus-icon-theme"),
    ("Papirus", "Papirus Standard (Balanced colorful vector icons)", "papirus-icon-theme"),
    ("Tela-circle-dark", "Tela Circle Dark (Modern circular dark icons)", "tela-icon-theme"),
    ("Tela-circle", "Tela Circle (Modern circular colorful icons)", "tela-icon-theme"),
    ("Catppuccin-SE", "Catppuccin Soothing Pastel Icons", "catppuccin-icon-theme"),
    ("Gruvbox-Plus-Dark", "Gruvbox Retro Warm Icon Pack", "gruvbox-icon-theme"),
    ("TokyoNight-SE", "Tokyo Night Cyber Neon Icon Pack", "tokyonight-icon-theme"),
    ("Nordzy-dark", "Nordic Frost Polar Dark Icons", "nordzy-icon-theme"),
    ("Qogir-dark", "Qogir Flat Material Dark Icons", "qogir-icon-theme"),
    ("Breeze-Dark", "KDE Breeze Dark Vector Icons", "kf6-breeze-icons"),
    ("Numix-Circle", "Numix Circular App Icons", "numix-icon-theme-circle"),
    ("Adwaita", "FreeBSD / GNOME Standard Fallback Icons", "adwaita-icon-theme"),
]


def discover_installed_icon_themes() -> set[str]:
    """Scan FreeBSD (`/usr/local/share/icons`) and user (`~/.local/share/icons`, `~/.icons`) directories."""
    search_dirs = [
        Path("/usr/local/share/icons"),
        Path("/usr/share/icons"),
        Path.home() / ".local" / "share" / "icons",
        Path.home() / ".icons",
    ]
    found: set[str] = set()
    for base in search_dirs:
        if not base.is_dir():
            continue
        try:
            for child in base.iterdir():
                if child.is_dir() and (child / "index.theme").is_file():
                    if child.name.lower() not in ("default", "hicolor", "locolor"):
                        found.add(child.name)
        except OSError:
            continue
    return found


def list_icon_themes(active_icon: str = "Papirus-Dark") -> list[dict[str, Any]]:
    """Return curated and system-discovered icon themes with installation & active status."""
    installed = discover_installed_icon_themes()
    items: list[dict[str, Any]] = []
    seen: set[str] = set()

    for pack_id, desc, pkg_name in ICON_PACK_CATALOG:
        seen.add(pack_id)
        is_inst = pack_id in installed
        items.append(
            {
                "id": pack_id,
                "description": desc,
                "pkg": pkg_name,
                "installed": is_inst,
                "active": pack_id == active_icon,
            }
        )

    for custom_id in sorted(installed - seen):
        items.append(
            {
                "id": custom_id,
                "description": "System / User Installed Icon Theme",
                "pkg": "local",
                "installed": True,
                "active": custom_id == active_icon,
            }
        )
    return items


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
                hyprlock_layout=t.get("default_hyprlock", "bsd-crimson-guard"),
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
    """Open Rofi Icon Pack Picker and update GTK/Qt/Rofi/Dunst icon themes."""
    ctx = get_effective_context()
    current_icon = ctx.get("config", {}).get("appearance", {}).get("icon_theme", "Papirus-Dark")
    rows = []
    for item in list_icon_themes(active_icon=current_icon):
        pack_id = item["id"]
        desc = item["description"]
        badge = "★ Active" if item["active"] else ("Installed" if item["installed"] else "Available")
        rows.append((f"󰀻  {pack_id:<22} [{badge:<9}] — {desc}", pack_id))

    chosen = run_rofi_dmenu(
        [r[0] for r in rows],
        prompt="󰀻  Icons",
        mesg=f"Active Icon Theme: {current_icon} (Syncs GTK-2/3/4, Qt5/6, Rofi & Dunst)",
    )
    if not chosen:
        return None

    for label, pack_id in rows:
        if label == chosen:
            update_state(icon_theme=pack_id)
            compile_all(reload_daemons=True)
            return pack_id
    return None
