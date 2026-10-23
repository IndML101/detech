"""Rofi Keyboard Shortcut Search & Runner (`SUPER + /` or `detech menu keybinds`)."""

from __future__ import annotations

import shutil
import subprocess
from typing import Any

from detech.core.lua_loader import load_lua_file
from detech.core.paths import resolve_lua_file
from detech.generators.hyprland import format_lua_dispatcher, normalize_keybind_action
from detech.menus.rofi_runner import run_rofi_dmenu


def format_keybind_entries(binds_data: dict[str, Any] | None = None) -> list[dict[str, str]]:
    """Format all shortcuts from `keybinds.lua` into searchable display entries and dispatch commands."""
    if binds_data is None:
        binds_data = load_lua_file(resolve_lua_file("keybinds.lua"))

    items: list[dict[str, str]] = []
    for bind in binds_data.get("binds", []):
        mods = bind.get("mod", [])
        key = str(bind.get("key", ""))
        combo = " + ".join([*mods, key]) if mods else key
        category = str(bind.get("category", "General"))
        desc = str(bind.get("desc", ""))
        action, arg = normalize_keybind_action(str(bind.get("action", "exec")), str(bind.get("arg", "")))
        lua_dsp = format_lua_dispatcher(action, arg)

        label = f"[{category:<9}]  {combo:<22} ⟶  {desc}"
        items.append(
            {
                "label": label,
                "combo": combo,
                "category": category,
                "desc": desc,
                "action": action,
                "arg": arg,
                "lua_dsp": lua_dsp,
            }
        )
    return items


def build_hyprctl_dispatch_command(entry: dict[str, str]) -> list[str]:
    """Build `hyprctl dispatch <action> <arg>` for a selected keybind entry."""
    action, arg = normalize_keybind_action(entry["action"], entry.get("arg", ""))
    if arg:
        return ["hyprctl", "dispatch", action, arg]
    return ["hyprctl", "dispatch", action]


def build_hyprctl_lua_dispatch_command(entry: dict[str, str]) -> list[str]:
    """Build `hyprctl dispatch '<hl.dsp.*>'` for Hyprland 0.56/0.57+ Lua config mode."""
    lua_dsp = entry.get("lua_dsp") or format_lua_dispatcher(entry["action"], entry.get("arg", ""))
    return ["hyprctl", "dispatch", lua_dsp]


def open_keybinds_menu() -> dict[str, str] | None:
    """Open Rofi keybind search menu and execute the chosen shortcut."""
    items = format_keybind_entries()
    labels = [it["label"] for it in items]
    chosen_label = run_rofi_dmenu(
        labels,
        prompt="  Shortcuts",
        mesg="Search keyboard shortcuts — Press Enter to execute action immediately",
    )
    if not chosen_label:
        return None

    for item in items:
        if item["label"] == chosen_label:
            if shutil.which("hyprctl"):
                lua_cmd = build_hyprctl_lua_dispatch_command(item)
                res = subprocess.run(lua_cmd, check=False, capture_output=True, text=True)
                if "Invalid dispatcher" in (res.stdout or ""):
                    cmd = build_hyprctl_dispatch_command(item)
                    subprocess.run(cmd, check=False)
            return item
    return None
