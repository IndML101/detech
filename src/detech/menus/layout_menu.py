"""Rofi Switchers for Waybar (15 Layouts), Rofi (15 Layouts), Starship (15 Prompts), and Hyprlock."""

from __future__ import annotations

from detech.core.compiler import compile_all
from detech.core.state import get_effective_context, update_state
from detech.generators.hyprland import list_hyprlock_layouts
from detech.generators.rofi import list_rofi_layouts
from detech.generators.terminal_shell import list_starship_prompts
from detech.generators.waybar import list_waybar_layouts
from detech.menus.rofi_runner import run_rofi_dmenu


def open_waybar_layout_menu() -> str | None:
    """Open Rofi menu to switch between the 15 Waybar layouts."""
    ctx = get_effective_context()
    current = ctx.get("config", {}).get("appearance", {}).get("waybar_layout", "island-top")
    layouts = list_waybar_layouts()

    rows = []
    for item in layouts:
        lid = item["id"]
        badge = "★ Active" if lid == current else item.get("position", "top")
        variant = item.get("style_variant", "pill")
        rows.append((f"󰍜  {lid:<20} [{badge:<10} | {variant:<16}] — {item.get('name', lid)}", lid))

    chosen = run_rofi_dmenu(
        [r[0] for r in rows],
        prompt="󰍜  Waybar Layout",
        mesg=f"Active Waybar Layout: {current} (15 presets available)",
    )
    if not chosen:
        return None

    for label, lid in rows:
        if label == chosen:
            update_state(waybar_layout=lid)
            compile_all(reload_daemons=True)
            return lid
    return None


def open_rofi_layout_menu() -> str | None:
    """Open Rofi menu to switch between the 15 Rofi app drawer layouts."""
    ctx = get_effective_context()
    current = ctx.get("config", {}).get("appearance", {}).get("rofi_layout", "grid-cards")
    layouts = list_rofi_layouts()

    rows = []
    for item in layouts:
        lid = item["id"]
        grid = f"{item.get('columns', 1)}x{item.get('lines', 5)}"
        badge = "★ Active" if lid == current else grid
        rows.append((f"󰀻  {lid:<22} [{badge:<8}] — {item.get('name', lid)}", lid))

    chosen = run_rofi_dmenu(
        [r[0] for r in rows],
        prompt="󰀻  Rofi Layout",
        mesg=f"Active Rofi App Drawer Layout: {current} (15 presets available)",
    )
    if not chosen:
        return None

    for label, lid in rows:
        if label == chosen:
            update_state(rofi_layout=lid)
            compile_all(reload_daemons=True)
            return lid
    return None


def open_starship_menu() -> str | None:
    """Open Rofi menu to switch between the 15 Starship prompt presets."""
    ctx = get_effective_context()
    current = ctx.get("config", {}).get("appearance", {}).get("starship_preset", "tokyo-pill")
    prompts = list_starship_prompts()

    rows = []
    for item in prompts:
        pid = item["id"]
        badge = "★ Active" if pid == current else "Apply"
        preview = item.get("preview", "")
        rows.append((f"  {pid:<18} [{badge:<8}] — {item.get('name', pid):<38}  {preview}", pid))

    chosen = run_rofi_dmenu(
        [r[0] for r in rows],
        prompt="  Starship Prompt",
        mesg=f"Active Starship Prompt: {current} (15 presets available)",
    )
    if not chosen:
        return None

    for label, pid in rows:
        if label == chosen:
            update_state(starship_preset=pid)
            compile_all(reload_daemons=True)
            return pid
    return None


def open_hyprlock_layout_menu() -> str | None:
    """Open Rofi menu to switch Hyprlock screen lock layout."""
    ctx = get_effective_context()
    current = ctx.get("config", {}).get("appearance", {}).get("hyprlock_layout", "minimal-clock")
    layouts = list_hyprlock_layouts()

    rows = []
    for item in layouts:
        lid = item["id"]
        badge = "★ Active" if lid == current else "Apply"
        rows.append((f"󰌾  {lid:<20} [{badge:<8}] — {item.get('name', lid)}", lid))

    chosen = run_rofi_dmenu(
        [r[0] for r in rows],
        prompt="󰌾  Hyprlock",
        mesg=f"Active Lock Screen Layout: {current}",
    )
    if not chosen:
        return None

    for label, lid in rows:
        if label == chosen:
            update_state(hyprlock_layout=lid)
            compile_all(reload_daemons=True)
            return lid
    return None
