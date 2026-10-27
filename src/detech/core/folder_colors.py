"""Theme-Matched Folder Icon Synchronization Engine for Thunar and GTK File Managers."""

from __future__ import annotations

import math
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from detech.core.color_engine import hex_to_rgb, normalize_hex
from detech.core.paths import get_xdg_config_dir

# Curated catalog of Papirus folder color variants with canonical reference hex swatches
PAPIRUS_FOLDER_COLORS: dict[str, dict[str, str]] = {
    "carmine": {"hex": "#a30002", "name": "Carmine (FreeBSD / Crimson Deep Red)", "desc": "Deep BSD crimson red"},
    "red": {"hex": "#e25252", "name": "Red (Vibrant Coral Red)", "desc": "Bright vivid cherry red"},
    "blue": {"hex": "#5294e2", "name": "Blue (Classic Royal Blue)", "desc": "Standard crisp Linux blue"},
    "cyan": {"hex": "#00bcd4", "name": "Cyan (Neon Cyber Cyan)", "desc": "High-contrast electric turquoise"},
    "darkcyan": {"hex": "#45abb7", "name": "Dark Cyan (Muted Teal Cyan)", "desc": "Balanced oceanic blue-green"},
    "teal": {"hex": "#16a085", "name": "Teal (Solarized / Emerald Teal)", "desc": "Rich deep pine teal"},
    "green": {"hex": "#87b158", "name": "Green (Matcha / Everforest Green)", "desc": "Organic sage matcha green"},
    "yellow": {"hex": "#f9bd30", "name": "Yellow (Warm Amber Yellow)", "desc": "Golden sunny amber"},
    "orange": {"hex": "#ee923a", "name": "Orange (Gruvbox Warm Orange)", "desc": "Retro warm tangerine orange"},
    "deeporange": {"hex": "#eb6637", "name": "Deep Orange (Fiery Terracotta)", "desc": "Warm vibrant burnt orange"},
    "magenta": {"hex": "#ca71df", "name": "Magenta (Dracula Neon Magenta)", "desc": "Electric synthwave magenta"},
    "violet": {"hex": "#7e57c2", "name": "Violet (Catppuccin Lavender / Iris)", "desc": "Smooth purple twilight lavender"},
    "indigo": {"hex": "#5c6bc0", "name": "Indigo (Kanagawa Wave Indigo)", "desc": "Deep twilight indigo blue"},
    "nordic": {"hex": "#81a1c1", "name": "Nordic (Arctic Frost Polar Blue)", "desc": "Nord arctic polar blue"},
    "pink": {"hex": "#f06292", "name": "Pink (Pastel Sakura Pink)", "desc": "Soft gentle rose pink"},
    "grey": {"hex": "#8e8e8e", "name": "Grey (Neutral Slate Grey)", "desc": "Balanced monochrome grey"},
    "black": {"hex": "#4f4f4f", "name": "Black (Dark Carbon Black)", "desc": "Stealth dark grey-black"},
    "white": {"hex": "#e4e4e4", "name": "White (Crisp Chalk White)", "desc": "Clean bright white-silver"},
}

# Mapping of DETech theme names to default folder colors
THEME_FOLDER_COLOR_MAP: dict[str, str] = {
    "bsd-crimson": "carmine",
    "dracula-pro": "magenta",
    "gruvbox-material": "orange",
    "hyde-catppuccin": "violet",
    "kanagawa-wave": "indigo",
    "nordic-frost": "nordic",
    "rose-pine-moon": "violet",
    "ryoku-matcha": "green",
    "solarized-bsd": "teal",
    "tokyo-cyber": "cyan",
}

FOLDER_ICON_NAMES: list[str] = [
    "folder",
    "folder-open",
    "inode-directory",
    "folder-activities",
    "folder-documents",
    "folder-download",
    "folder-music",
    "folder-pictures",
    "folder-videos",
    "folder-publicshare",
    "folder-templates",
    "folder-recent",
    "folder-saved-search",
    "folder-tar",
    "folder-text",
    "user-home",
    "user-desktop",
]

FOLDER_SIZES: list[str] = [
    "16x16",
    "22x22",
    "24x24",
    "32x32",
    "48x48",
    "64x64",
    "128x128",
]


def find_system_papirus_dir() -> Path | None:
    """Find system Papirus icon theme directory."""
    candidates = [
        Path("/usr/local/share/icons/Papirus"),
        Path("/usr/share/icons/Papirus"),
        Path.home() / ".local" / "share" / "icons" / "Papirus",
        Path.home() / ".icons" / "Papirus",
    ]
    for p in candidates:
        if p.is_dir() and (p / "48x48" / "places").is_dir():
            return p
    return None


def calculate_color_distance(hex1: str, hex2: str) -> float:
    """Calculate Euclidean RGB color distance between two hex colors."""
    r1, g1, b1 = hex_to_rgb(hex1)
    r2, g2, b2 = hex_to_rgb(hex2)
    # Weighted Euclidean distance (human eye is more sensitive to green, then red, then blue)
    dr = r1 - r2
    dg = g1 - g2
    db = b1 - b2
    return math.sqrt(2 * (dr**2) + 4 * (dg**2) + 3 * (db**2))


def match_accent_to_folder_color(accent_hex: str) -> str:
    """Resolve the closest Papirus folder color variant for a given hex accent color."""
    normalized = normalize_hex(accent_hex)
    best_color = "blue"
    min_dist = float("inf")
    for cname, data in PAPIRUS_FOLDER_COLORS.items():
        dist = calculate_color_distance(normalized, data["hex"])
        if dist < min_dist:
            min_dist = dist
            best_color = cname
    return best_color


def resolve_folder_color(
    theme_data: dict[str, Any],
    palette: dict[str, str],
    appearance: dict[str, Any],
) -> str:
    """Determine the active folder color name based on config, theme, or palette."""
    explicit = appearance.get("folder_color")
    if explicit and str(explicit).lower() != "auto":
        color_name = str(explicit).lower()
        if color_name in PAPIRUS_FOLDER_COLORS:
            return color_name

    theme_color = theme_data.get("folder_color")
    if theme_color and str(theme_color).lower() in PAPIRUS_FOLDER_COLORS:
        return str(theme_color).lower()

    tname = theme_data.get("name", "")
    if tname in THEME_FOLDER_COLOR_MAP:
        return THEME_FOLDER_COLOR_MAP[tname]

    accent = palette.get("accent", "#e63946")
    return match_accent_to_folder_color(accent)


def generate_custom_folder_svg(accent: str, accent_alt: str, size: int = 48) -> str:
    """Generate a clean SVG folder icon styled directly with the theme's exact hex accent colors."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 48 48">
  <rect style="opacity:0.2" width="40" height="26" x="4" y="17" rx="2" ry="2"/>
  <path style="fill:{accent_alt}" d="M 4,34 C 4,35.108 4.892,36 6,36 H 42 C 43.108,36 44,35.108 44,34 V 12 C 44,10.892 43.108,10 42,10 H 24 C 21,10 20,6 17,6 H 6 C 4.892,6 4,6.892 4,8"/>
  <rect style="opacity:0.2" width="40" height="26" x="4" y="15" rx="2" ry="2"/>
  <rect style="fill:#e4e4e4" width="36" height="16" x="6" y="13" rx="2" ry="2"/>
  <rect style="fill:{accent}" width="40" height="26" x="4" y="16" rx="2" ry="2"/>
  <path style="opacity:0.15;fill:#ffffff" d="M 6,6 C 4.892,6 4,6.892 4,8 V 9 C 4,7.892 4.892,7 6,7 H 17 C 20,7 21,11 24,11 H 42 C 43.108,11 44,11.892 44,13 V 12 C 44,10.892 43.108,10 42,10 H 24 C 21,10 20,6 17,6 Z"/>
</svg>
"""


def sync_theme_folder_icons(
    folder_color: str,
    palette: dict[str, str],
    target_icons_dir: Path | None = None,
    base_theme_name: str = "Papirus-Dark",
) -> list[Path]:
    """Sync folder icons in user's icon directory to match the active theme color for Thunar."""
    written: list[Path] = []
    if target_icons_dir is None:
        user_icons = Path(os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))) / "icons"
    else:
        user_icons = target_icons_dir

    papirus_sys = find_system_papirus_dir()
    theme_overlay_dir = user_icons / base_theme_name
    theme_overlay_dir.mkdir(parents=True, exist_ok=True)

    # 1. Write index.theme for user overlay
    index_theme = theme_overlay_dir / "index.theme"
    dir_entries = [f"{sz}/places" for sz in FOLDER_SIZES]
    index_content = [
        "[Icon Theme]",
        f"Name={base_theme_name}",
        "Comment=DETech Theme-Colored Folder Icon Theme for Thunar & GTK",
        f"Inherits={base_theme_name},Papirus,Adwaita,hicolor",
        f"Directories={','.join(dir_entries)}",
        "",
    ]
    for sz in FOLDER_SIZES:
        dim = sz.split("x")[0]
        index_content.extend([
            f"[{sz}/places]",
            f"Size={dim}",
            "Context=Places",
            "Type=Fixed",
            "",
        ])
    index_theme.write_text("\n".join(index_content) + "\n", encoding="utf-8")
    written.append(index_theme)

    accent = palette.get("accent", "#e63946")
    accent_alt = palette.get("accent_alt", palette.get("bg_tertiary", "#281c23"))

    # 2. Populate places folders for each size
    for sz in FOLDER_SIZES:
        places_dir = theme_overlay_dir / sz / "places"
        places_dir.mkdir(parents=True, exist_ok=True)
        sys_places = (papirus_sys / sz / "places") if papirus_sys else None

        # Check if sys_places has colored folder files for folder_color
        has_sys_color = bool(sys_places and (sys_places / f"folder-{folder_color}.svg").is_file())

        for name in FOLDER_ICON_NAMES:
            target_file = places_dir / f"{name}.svg"

            if has_sys_color and sys_places:
                # Try finding exact color variant file in system Papirus
                src_filename = f"{name.replace('folder', f'folder-{folder_color}')}.svg" if name.startswith("folder") else f"{name.replace('user-', f'user-{folder_color}-')}.svg"
                src_path = sys_places / src_filename
                if not src_path.is_file():
                    # Fallback to main folder colored variant
                    src_path = sys_places / f"folder-{folder_color}.svg"

                if src_path.is_file():
                    if target_file.is_symlink() or target_file.is_file():
                        try:
                            target_file.unlink()
                        except OSError:
                            pass
                    try:
                        target_file.symlink_to(src_path)
                        written.append(target_file)
                        continue
                    except OSError:
                        pass

            # Fallback: write clean custom SVG
            sz_int = int(sz.split("x")[0])
            svg_data = generate_custom_folder_svg(accent, accent_alt, size=sz_int)
            target_file.write_text(svg_data, encoding="utf-8")
            written.append(target_file)

    # 3. Refresh icon cache if gtk-update-icon-cache is available
    if shutil.which("gtk-update-icon-cache"):
        subprocess.run(
            ["gtk-update-icon-cache", "-q", "-f", "-t", str(theme_overlay_dir)],
            check=False,
            capture_output=True,
        )

    # 4. If thunar daemon is running, reload it so Thunar windows pick up new folder icons immediately
    if shutil.which("thunar"):
        subprocess.run(["thunar", "-q"], check=False, capture_output=True)

    return written
