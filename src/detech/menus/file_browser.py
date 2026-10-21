"""Rofi Interactive File Browser (`SUPER + E` or `detech menu files`)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from detech.core.state import get_effective_context
from detech.menus.rofi_runner import run_rofi_dmenu


def list_directory_entries(directory: Path) -> list[tuple[str, Path, bool]]:
    """Return `(label, path, is_dir)` entries for a directory."""
    resolved = directory.expanduser().resolve()
    entries: list[tuple[str, Path, bool]] = []
    if resolved.parent != resolved:
        entries.append(("  .. (Parent Directory)", resolved.parent, True))

    try:
        children = sorted(resolved.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        return entries

    for child in children:
        if child.name.startswith("."):
            continue
        if child.is_dir():
            entries.append((f"  {child.name}/", child, True))
        else:
            entries.append((f"  {child.name}", child, False))
    return entries


def open_file_browser(start_dir: Path | str | None = None) -> Path | None:
    """Navigate directories in Rofi and open the chosen file in editor or xdg-open."""
    current = Path(start_dir or os.path.expanduser("~")).expanduser().resolve()
    ctx = get_effective_context()
    general = ctx.get("config", {}).get("general", {})
    terminal = general.get("terminal", "kitty")
    editor = general.get("editor", "nvim")

    while True:
        items = list_directory_entries(current)
        chosen = run_rofi_dmenu(
            [it[0] for it in items],
            prompt="  Files",
            mesg=f"Path: {current}",
        )
        if not chosen:
            return None

        matched = next((it for it in items if it[0] == chosen), None)
        if not matched:
            return None

        _, target_path, is_dir = matched
        if is_dir:
            current = target_path
            continue

        # Open text/code files in Kitty + editor, others via xdg-open
        if target_path.suffix.lower() in {".lua", ".py", ".sh", ".md", ".conf", ".toml", ".json", ".jsonc", ".css", ".rasi", ".txt"}:
            subprocess.Popen([terminal, editor, str(target_path)])
        else:
            subprocess.Popen(["xdg-open", str(target_path)])
        return target_path
