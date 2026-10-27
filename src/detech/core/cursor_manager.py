"""Cursor Theme and Trackpad Pointer Management for DETech."""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CursorThemeSpec:
    """Metadata specification for a supported cursor theme."""

    id: str
    name: str
    description: str
    style: str
    pkg: str
    trackpad_optimized: bool = True


CURSOR_CATALOG: list[CursorThemeSpec] = [
    CursorThemeSpec(
        id="Bibata-Modern-Ice",
        name="Bibata Modern Ice",
        description="Crisp rounded white cursor with dark outline, ideal for trackpads & high-DPI",
        style="modern-white",
        pkg="bibata-cursors-modern-ice",
        trackpad_optimized=True,
    ),
    CursorThemeSpec(
        id="Bibata-Modern-Classic",
        name="Bibata Modern Classic",
        description="Black sleek rounded cursor with white outline for high-contrast trackpads",
        style="modern-black",
        pkg="bibata-cursors-modern-classic",
        trackpad_optimized=True,
    ),
    CursorThemeSpec(
        id="Bibata-Modern-Amber",
        name="Bibata Modern Amber",
        description="Warm amber modern rounded cursor with sharp trackpad tracking",
        style="modern-amber",
        pkg="bibata-cursors-modern-amber",
        trackpad_optimized=True,
    ),
    CursorThemeSpec(
        id="Bibata-Original-Ice",
        name="Bibata Original Ice",
        description="Sharp geometric white cursor for precise pointing and selection",
        style="sharp-white",
        pkg="bibata-cursors-original-ice",
        trackpad_optimized=True,
    ),
    CursorThemeSpec(
        id="Bibata-Original-Classic",
        name="Bibata Original Classic",
        description="Sharp geometric black cursor for precise high-contrast pointing",
        style="sharp-black",
        pkg="bibata-cursors-original-classic",
        trackpad_optimized=True,
    ),
    CursorThemeSpec(
        id="Catppuccin-Mocha-Dark-Cursors",
        name="Catppuccin Mocha Dark",
        description="Smooth pastel dark cursor perfectly matching Mocha palette",
        style="pastel-dark",
        pkg="catppuccin-cursors",
        trackpad_optimized=True,
    ),
    CursorThemeSpec(
        id="Catppuccin-Mocha-Lavender-Cursors",
        name="Catppuccin Mocha Lavender",
        description="Lavender-accented pastel cursor for vibrant soothing aesthetics",
        style="pastel-accent",
        pkg="catppuccin-cursors",
        trackpad_optimized=True,
    ),
    CursorThemeSpec(
        id="Nordzy-cursors",
        name="Nordzy Cursors",
        description="Arctic frost polar dark cursor with ice-blue accents",
        style="nordic-dark",
        pkg="nordzy-cursors",
        trackpad_optimized=True,
    ),
    CursorThemeSpec(
        id="Nordzy-cursors-white",
        name="Nordzy White Cursors",
        description="Arctic frost crisp white cursor with polar clarity",
        style="nordic-white",
        pkg="nordzy-cursors-white",
        trackpad_optimized=True,
    ),
    CursorThemeSpec(
        id="Capitaine-Cursors",
        name="Capitaine Cursors",
        description="macOS-inspired clean minimalist vector cursor for fluid gesture tracking",
        style="macos-dark",
        pkg="capitaine-cursors",
        trackpad_optimized=True,
    ),
    CursorThemeSpec(
        id="Capitaine-Cursors-White",
        name="Capitaine Cursors White",
        description="macOS-inspired clean minimalist white cursor for high visibility",
        style="macos-white",
        pkg="capitaine-cursors",
        trackpad_optimized=True,
    ),
    CursorThemeSpec(
        id="BreezeX-Black",
        name="KDE BreezeX Black",
        description="Modern high-contrast vector cursor with smooth sub-pixel rendering",
        style="breeze-black",
        pkg="breeze-cursors",
        trackpad_optimized=True,
    ),
    CursorThemeSpec(
        id="Qogir-cursors",
        name="Qogir Dark Cursors",
        description="Google Material design rounded dark cursor",
        style="material-dark",
        pkg="qogir-cursors",
        trackpad_optimized=True,
    ),
    CursorThemeSpec(
        id="Qogir-white-cursors",
        name="Qogir White Cursors",
        description="Google Material design rounded white cursor",
        style="material-white",
        pkg="qogir-cursors",
        trackpad_optimized=True,
    ),
    CursorThemeSpec(
        id="Adwaita",
        name="Adwaita System Standard",
        description="FreeBSD and GNOME standard high-legibility system cursor",
        style="adwaita",
        pkg="adwaita-icon-theme",
        trackpad_optimized=False,
    ),
    CursorThemeSpec(
        id="redglass",
        name="Redglass X11",
        description="FreeBSD classic translucent red cursor",
        style="retro-red",
        pkg="x11-themes",
        trackpad_optimized=False,
    ),
    CursorThemeSpec(
        id="whiteglass",
        name="Whiteglass X11",
        description="FreeBSD classic translucent white cursor",
        style="retro-white",
        pkg="x11-themes",
        trackpad_optimized=False,
    ),
    CursorThemeSpec(
        id="handhelds",
        name="Handhelds Trackpad",
        description="FreeBSD lightweight stylus and touchpad pointer",
        style="retro-touch",
        pkg="x11-themes",
        trackpad_optimized=True,
    ),
]

TRACKPAD_CURSOR_SIZES: list[dict[str, Any]] = [
    {"size": 24, "label": "24px (Standard)", "desc": "Crisp and compact, standard for 1080p"},
    {"size": 28, "label": "28px (Medium)", "desc": "Balanced visibility for smooth trackpad navigation"},
    {"size": 32, "label": "32px (Large)", "desc": "High visibility for trackpads, gestures & 1440p displays"},
    {"size": 36, "label": "36px (Extra Large)", "desc": "Enhanced trackpad tracking across multi-monitors"},
    {"size": 48, "label": "48px (Ultra)", "desc": "Maximum tracking clarity for 4K / High-DPI trackpads"},
]


def discover_installed_cursor_themes() -> set[str]:
    """Scan FreeBSD and user icon directories to detect all installed cursor themes."""
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
                if not child.is_dir():
                    continue
                # A directory qualifies as a cursor theme if it has a 'cursors' folder
                if (child / "cursors").is_dir():
                    found.add(child.name)
                elif (child / "index.theme").is_file():
                    # Or if index.theme specifies Inherits with cursors or mentions Cursor
                    try:
                        content = (child / "index.theme").read_text(encoding="utf-8", errors="ignore")
                        if "cursor" in content.lower():
                            found.add(child.name)
                    except OSError:
                        pass
        except OSError:
            continue
    return found


def list_cursor_themes(active_cursor: str = "Bibata-Modern-Ice") -> list[dict[str, Any]]:
    """Return catalog of cursor themes annotated with installation and active status."""
    installed = discover_installed_cursor_themes()
    installed_lower = {c.lower() for c in installed}

    items: list[dict[str, Any]] = []
    seen: set[str] = set()

    for spec in CURSOR_CATALOG:
        seen.add(spec.id.lower())
        is_inst = spec.id.lower() in installed_lower or spec.id in installed
        items.append(
            {
                "id": spec.id,
                "name": spec.name,
                "description": spec.description,
                "style": spec.style,
                "pkg": spec.pkg,
                "trackpad_optimized": spec.trackpad_optimized,
                "installed": is_inst,
                "active": spec.id == active_cursor,
            }
        )

    # Also include any custom installed cursor themes discovered on system
    for custom_id in sorted(installed):
        if custom_id.lower() not in seen:
            items.append(
                {
                    "id": custom_id,
                    "name": custom_id,
                    "description": "System / User Installed Cursor Theme",
                    "style": "custom",
                    "pkg": "local",
                    "trackpad_optimized": True,
                    "installed": True,
                    "active": custom_id == active_cursor,
                }
            )
            seen.add(custom_id.lower())

    return items


def sync_default_cursor_theme(cursor_theme: str, target_icons_dir: Path | None = None) -> Path:
    """Generate `~/.icons/default/index.theme` for legacy X11/GTK apps and trackpads."""
    if target_icons_dir is None:
        icons_dir = Path.home() / ".icons"
    else:
        icons_dir = target_icons_dir

    default_dir = icons_dir / "default"
    default_dir.mkdir(parents=True, exist_ok=True)
    index_file = default_dir / "index.theme"
    index_file.write_text(
        f"[Icon Theme]\nName=Default\nComment=Default Cursor Theme for DETech\nInherits={cursor_theme}\n",
        encoding="utf-8",
    )
    return index_file


def apply_cursor_live(cursor_theme: str, cursor_size: int = 24) -> None:
    """Hot-reload cursor theme and size live across Hyprland and GNOME/GTK."""
    if shutil.which("hyprctl"):
        subprocess.run(
            ["hyprctl", "setcursor", cursor_theme, str(cursor_size)],
            check=False,
            capture_output=True,
        )

    if shutil.which("gsettings"):
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.interface", "cursor-theme", cursor_theme],
            check=False,
            capture_output=True,
        )
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.interface", "cursor-size", str(cursor_size)],
            check=False,
            capture_output=True,
        )
