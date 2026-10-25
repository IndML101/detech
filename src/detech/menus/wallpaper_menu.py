"""Rofi Wallpaper Picker with Live System-Wide Color Sync."""

from __future__ import annotations

import os
from pathlib import Path

from detech.core.compiler import compile_all
from detech.core.paths import get_presets_dir
from detech.core.state import update_state
from detech.menus.rofi_runner import run_rofi_dmenu

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def discover_wallpapers(extra_dirs: list[Path] | None = None) -> list[Path]:
    """Scan standard FreeBSD user wallpaper directories and DETech theme directories."""
    search_dirs: list[Path] = []
    if extra_dirs:
        search_dirs.extend(extra_dirs)

    home_pics = Path(os.path.expanduser("~/Pictures/Wallpapers"))
    search_dirs.append(home_pics)
    search_dirs.append(get_presets_dir() / "wallpapers")
    search_dirs.append(get_presets_dir() / "themes")
    search_dirs.append(Path("/usr/local/share/wallpapers"))
    search_dirs.append(Path("/usr/local/share/backgrounds"))
    search_dirs.append(Path("/usr/local/share/hypr"))

    found: list[Path] = []
    seen: set[Path] = set()
    for d in search_dirs:
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*")):
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS:
                if d.name == "hypr" and p.name.startswith("lockdead"):
                    continue
                resolved = p.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    found.append(resolved)
    return found


def select_wallpaper(
    wallpaper_path: Path | str,
    enable_dynamic_colors: bool = True,
    reload_daemons: bool = True,
) -> dict:
    """Set active wallpaper, optionally enable dynamic palette extraction, and recompile."""
    resolved = str(Path(wallpaper_path).expanduser().resolve())
    update_state(wallpaper=resolved, dynamic_wallpaper_colors=enable_dynamic_colors)
    return compile_all(reload_daemons=reload_daemons)


def open_wallpaper_menu(extra_dirs: list[Path] | None = None) -> Path | None:
    """Open Rofi Wallpaper Picker and apply selected wallpaper + system-wide colors."""
    wallpapers = discover_wallpapers(extra_dirs=extra_dirs)
    if not wallpapers:
        run_rofi_dmenu(
            ["No wallpapers found in ~/Pictures/Wallpapers"],
            prompt="󰸉  Wallpapers",
        )
        return None

    entries = [f"󰸉  {w.name}  ({w.parent})" for w in wallpapers]
    chosen = run_rofi_dmenu(
        entries,
        prompt="󰸉  Wallpapers",
        mesg="Select a wallpaper to apply immediately and synchronize system-wide colors",
    )
    if not chosen:
        return None

    for idx, label in enumerate(entries):
        if label == chosen:
            chosen_path = wallpapers[idx]
            select_wallpaper(chosen_path, enable_dynamic_colors=True, reload_daemons=True)
            return chosen_path
    return None
