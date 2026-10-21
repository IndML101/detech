"""Rofi FreeBSD `pkg` Software Picker (`SUPER + S` or `detech menu software`)."""

from __future__ import annotations

import subprocess
from typing import Any

from detech.core.state import get_effective_context
from detech.freebsd.pkg_manager import (
    build_pkg_terminal_command,
    list_installed_packages,
    search_remote_packages,
)
from detech.menus.rofi_runner import run_rofi_dmenu

CURATED_FREEBSD_DESKTOP_PKGS: list[dict[str, str]] = [
    {"name": "firefox", "version": "latest", "comment": "Mozilla Firefox Web Browser (Wayland)"},
    {"name": "chromium", "version": "latest", "comment": "Chromium Web Browser"},
    {"name": "neovim", "version": "latest", "comment": "Hyperextensible Vim-based text editor"},
    {"name": "thunar", "version": "latest", "comment": "XFCE lightweight graphical file manager"},
    {"name": "imv", "version": "latest", "comment": "Wayland native image viewer"},
    {"name": "mpv", "version": "latest", "comment": "Free and open-source media player"},
    {"name": "zathura", "version": "latest", "comment": "Keyboard-driven minimalistic PDF viewer"},
    {"name": "btop", "version": "latest", "comment": "Resource monitor for FreeBSD"},
    {"name": "fastfetch", "version": "latest", "comment": "Fast system information tool"},
    {"name": "grim", "version": "latest", "comment": "Grab images from a Wayland compositor"},
    {"name": "slurp", "version": "latest", "comment": "Select a region in a Wayland compositor"},
    {"name": "wl-clipboard", "version": "latest", "comment": "Command-line Wayland clipboard utilities"},
    {"name": "cliphist", "version": "latest", "comment": "Wayland clipboard history manager"},
    {"name": "nerd-fonts", "version": "latest", "comment": "Developer-targeted fonts with high number of glyphs"},
    {"name": "papirus-icon-theme", "version": "latest", "comment": "Papirus SVG icon theme"},
]


def build_software_menu_entries(installed_names: set[str] | None = None) -> list[dict[str, Any]]:
    """Build Rofi software picker list combining installed and curated FreeBSD packages."""
    if installed_names is None:
        installed_pkgs = list_installed_packages()
        installed_names = {p["name"] for p in installed_pkgs}

    remote = search_remote_packages()
    catalog = remote if remote else CURATED_FREEBSD_DESKTOP_PKGS

    rows: list[dict[str, Any]] = []
    for pkg in catalog[:500]:
        name = pkg["name"]
        is_inst = name in installed_names
        badge = "✓ Installed (Remove)" if is_inst else "⬇ Install via pkg"
        label = f"  {name:<24} [{badge}] — {pkg.get('comment', '')}"
        rows.append(
            {
                "label": label,
                "name": name,
                "installed": is_inst,
                "action": "delete" if is_inst else "install",
            }
        )
    return rows


def open_software_menu() -> dict[str, Any] | None:
    """Open Rofi FreeBSD Software Picker and launch Kitty to install/remove selected pkg."""
    ctx = get_effective_context()
    privilege_cmd = ctx.get("freebsd", {}).get("privilege_cmd", "doas")
    terminal = ctx.get("config", {}).get("general", {}).get("terminal", "kitty")

    rows = build_software_menu_entries()
    chosen = run_rofi_dmenu(
        [r["label"] for r in rows],
        prompt="  FreeBSD pkg",
        mesg="Select a package to install or remove via FreeBSD pkg",
    )
    if not chosen:
        return None

    for row in rows:
        if row["label"] == chosen:
            cmd = build_pkg_terminal_command(
                action=row["action"],
                pkg_name=row["name"],
                privilege_cmd=privilege_cmd,
                terminal=terminal,
            )
            subprocess.Popen(cmd)
            return row
    return None
