"""Shared Rofi invocation helper for DETech menus."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from detech.core.paths import get_xdg_config_dir


def run_rofi_dmenu(
    entries: list[str],
    prompt: str = " DETech",
    mesg: str | None = None,
    theme_file: Path | None = None,
    show_icons: bool = False,
    theme_str: str | None = None,
) -> str | None:
    """Display `entries` in Rofi dmenu mode and return the selected line (or None if cancelled)."""
    if not shutil.which("rofi"):
        return None

    menu_rasi = theme_file or (get_xdg_config_dir() / "rofi" / "menu.rasi")
    cmd = ["rofi", "-dmenu", "-i", "-p", prompt]
    if show_icons:
        cmd.append("-show-icons")
    if mesg:
        cmd.extend(["-mesg", mesg])
    if menu_rasi.is_file():
        cmd.extend(["-theme", str(menu_rasi)])
    if theme_str:
        cmd.extend(["-theme-str", theme_str])

    payload = "\n".join(entries)
    proc = subprocess.run(
        cmd,
        input=payload,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    choice = proc.stdout.strip()
    return choice if choice else None


def launch_app_drawer(config_file: Path | None = None) -> int:
    """Launch the Rofi application drawer (`rofi -show drun`) with the active layout."""
    if not shutil.which("rofi"):
        return 1
    cfg = config_file or (get_xdg_config_dir() / "rofi" / "config.rasi")
    cmd = ["rofi", "-show", "drun"]
    if cfg.is_file():
        cmd.extend(["-config", str(cfg)])
    proc = subprocess.run(cmd, check=False)
    return proc.returncode
