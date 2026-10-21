"""Rofi Nerd Fonts Picker & Installer (`SUPER + SHIFT + F` or `detech menu fonts`)."""

from __future__ import annotations

from typing import Any

from detech.core.compiler import compile_all
from detech.core.font_manager import (
    get_nerd_font_status_list,
    install_nerd_font,
    resolve_font_settings,
)
from detech.core.state import get_effective_context, update_state
from detech.menus.rofi_runner import run_rofi_dmenu

FONT_SIZE_CHOICES = [10, 11, 12, 13, 14, 15, 16]


def build_font_menu_entries(
    installed_override: set[str] | None = None,
    active_font: str = "JetBrainsMono Nerd Font",
    active_size: int = 11,
) -> list[dict[str, Any]]:
    """Build Rofi menu rows for Nerd Fonts and font sizes."""
    catalog = get_nerd_font_status_list(installed_override=installed_override)
    rows: list[dict[str, Any]] = []

    # Sort installed fonts first
    sorted_catalog = sorted(catalog, key=lambda x: (not x["installed"], x["family"]))

    for item in sorted_catalog:
        fam = item["family"]
        is_active = fam.lower() == active_font.lower()
        badge = "★ Active" if is_active else ("✓ Installed" if item["installed"] else "⬇ Install")
        label = f"󰛖  {fam:<28} [{badge:<11}] — {item['style_hint']}"
        rows.append(
            {
                "type": "font",
                "label": label,
                "family": fam,
                "propo_family": item["propo_family"],
                "archive_name": item["archive_name"],
                "installed": item["installed"],
            }
        )

    for sz in FONT_SIZE_CHOICES:
        mark = "★ Current" if sz == active_size else "Set Size"
        rows.append(
            {
                "type": "size",
                "label": f"fontsize  Font Size: {sz}pt ({mark})",
                "size": sz,
            }
        )

    return rows


def apply_font_selection(choice: dict[str, Any], reload_daemons: bool = True) -> dict[str, Any]:
    """Apply a selected Nerd Font or font size and recompile all DETech configs."""
    if choice["type"] == "size":
        update_state(font_size=int(choice["size"]))
        return compile_all(reload_daemons=reload_daemons)

    if not choice.get("installed", False) and choice.get("archive_name"):
        install_nerd_font(choice["archive_name"])

    update_state(
        font_mono=choice["family"],
        font_sans=choice.get("propo_family", f"{choice['family']} Propo"),
    )
    return compile_all(reload_daemons=reload_daemons)


def open_font_menu() -> dict[str, Any] | None:
    """Display interactive Rofi Nerd Fonts picker and apply selection."""
    ctx = get_effective_context()
    fonts = resolve_font_settings(ctx)
    rows = build_font_menu_entries(active_font=fonts["mono"], active_size=fonts["size"])

    selected = run_rofi_dmenu(
        [r["label"] for r in rows],
        prompt="󰛖  Nerd Fonts",
        mesg=f"Active: {fonts['mono']} ({fonts['size']}pt) — Select to switch or auto-install",
    )
    if not selected:
        return None

    for row in rows:
        if row["label"] == selected:
            apply_font_selection(row, reload_daemons=True)
            return row
    return None
