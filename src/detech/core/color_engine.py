"""Hybrid Color Engine for DETech.

Supports both:
1. Curated static palettes defined in `presets/themes/<theme>/theme.lua`
2. Dynamic wallpaper color extraction using Pillow (HSL luminance/saturation
   harmony synthesis) so system-wide colors adapt when picking wallpapers.
"""

from __future__ import annotations

import colorsys
from pathlib import Path
from typing import Any

from PIL import Image

from detech.core.lua_loader import load_lua_file
from detech.core.paths import get_presets_dir


def normalize_hex(color: str) -> str:
    """Normalize a hex color string to `#rrggbb`."""
    c = color.strip().lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    if len(c) != 6:
        raise ValueError(f"Invalid hex color: {color!r}")
    return f"#{c.lower()}"


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    """Convert `#rrggbb` to `(r, g, b)` tuple (0..255)."""
    h = normalize_hex(color)[1:]
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert `(r, g, b)` integers to `#rrggbb`."""
    r = max(0, min(255, int(round(r))))
    g = max(0, min(255, int(round(g))))
    b = max(0, min(255, int(round(b))))
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_rgba_css(color: str, alpha: float = 1.0) -> str:
    """Format hex color as CSS `rgba(r, g, b, alpha)`."""
    r, g, b = hex_to_rgb(color)
    return f"rgba({r}, {g}, {b}, {alpha:.2f})"


def hex_to_hypr_rgba(color: str, alpha_hex: str = "ff") -> str:
    """Format hex color as Hyprland `rgba(rrggbbaa)`."""
    h = normalize_hex(color)[1:]
    return f"rgba({h}{alpha_hex.lower()})"


def _hsl_to_hex(h: float, s: float, l: float) -> str:
    """Convert H (0..1), S (0..1), L (0..1) to `#rrggbb`."""
    r, g, b = colorsys.hls_to_rgb(h % 1.0, max(0.0, min(1.0, l)), max(0.0, min(1.0, s)))
    return rgb_to_hex(int(r * 255), int(g * 255), int(b * 255))


def list_themes() -> list[dict[str, Any]]:
    """List all available themes under `presets/themes/`."""
    themes_dir = get_presets_dir() / "themes"
    results: list[dict[str, Any]] = []
    if not themes_dir.is_dir():
        return results
    for theme_dir in sorted(themes_dir.iterdir()):
        lua_path = theme_dir / "theme.lua"
        if lua_path.is_file():
            data = load_lua_file(lua_path)
            results.append(data)
    return results


def load_theme(theme_name: str) -> dict[str, Any]:
    """Load a theme definition by name from `presets/themes/<theme_name>/theme.lua`."""
    lua_path = get_presets_dir() / "themes" / theme_name / "theme.lua"
    if not lua_path.is_file():
        # Fallback to bsd-crimson
        fallback = get_presets_dir() / "themes" / "bsd-crimson" / "theme.lua"
        if fallback.is_file():
            return load_lua_file(fallback)
        raise FileNotFoundError(f"Theme not found: {theme_name}")
    return load_lua_file(lua_path)


def extract_palette_from_wallpaper(
    image_path: Path | str,
    base_theme: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Extract a full DETech semantic + 16-ANSI color palette from a wallpaper image."""
    img_path = Path(image_path)
    if not img_path.is_file():
        raise FileNotFoundError(f"Wallpaper image not found: {img_path}")

    with Image.open(img_path) as img:
        small = img.convert("RGB").resize((64, 64))
        if hasattr(small, "get_flattened_data"):
            pixels = list(small.get_flattened_data())
        else:
            pixels = list(small.getdata())

    # Score pixels by saturation and balanced lightness to find dominant chromatic accent
    best_h = 0.98
    best_s = 0.70
    best_score = -1.0

    for r, g, b in pixels:
        h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
        # Prefer vibrant colors that aren't pure black or pure white
        lightness_weight = 1.0 - abs(l - 0.52) * 1.6
        score = (s * 1.5) + max(0.0, lightness_weight)
        if score > best_score:
            best_score = score
            best_h = h
            best_s = max(0.45, min(0.88, s))

    alt_h = (best_h + 0.08) % 1.0
    comp_h = (best_h + 0.5) % 1.0

    palette: dict[str, str] = {
        "bg_primary": _hsl_to_hex(best_h, 0.22, 0.09),
        "bg_secondary": _hsl_to_hex(best_h, 0.24, 0.13),
        "bg_tertiary": _hsl_to_hex(best_h, 0.25, 0.19),
        "fg_primary": _hsl_to_hex(best_h, 0.28, 0.92),
        "fg_secondary": _hsl_to_hex(best_h, 0.18, 0.76),
        "fg_muted": _hsl_to_hex(best_h, 0.14, 0.48),
        "accent": _hsl_to_hex(best_h, best_s, 0.62),
        "accent_alt": _hsl_to_hex(alt_h, best_s, 0.68),
        "urgent": _hsl_to_hex(0.98, 0.82, 0.64),
        "success": _hsl_to_hex(0.36, 0.60, 0.62),
        "warning": _hsl_to_hex(0.10, 0.80, 0.66),
        "border_active": _hsl_to_hex(best_h, best_s, 0.64),
        "border_inactive": _hsl_to_hex(best_h, 0.18, 0.26),
        "color0": _hsl_to_hex(best_h, 0.22, 0.10),
        "color1": _hsl_to_hex(0.98, 0.75, 0.62),
        "color2": _hsl_to_hex(0.35, 0.58, 0.60),
        "color3": _hsl_to_hex(0.11, 0.76, 0.65),
        "color4": _hsl_to_hex(best_h, best_s, 0.62),
        "color5": _hsl_to_hex(alt_h, best_s, 0.66),
        "color6": _hsl_to_hex(comp_h, 0.62, 0.64),
        "color7": _hsl_to_hex(best_h, 0.20, 0.82),
        "color8": _hsl_to_hex(best_h, 0.18, 0.30),
        "color9": _hsl_to_hex(0.98, 0.85, 0.68),
        "color10": _hsl_to_hex(0.35, 0.68, 0.68),
        "color11": _hsl_to_hex(0.11, 0.86, 0.72),
        "color12": _hsl_to_hex(best_h, min(0.95, best_s + 0.1), 0.70),
        "color13": _hsl_to_hex(alt_h, min(0.95, best_s + 0.1), 0.72),
        "color14": _hsl_to_hex(comp_h, 0.72, 0.72),
        "color15": "#ffffff",
    }

    if base_theme and "colors" in base_theme:
        merged = dict(base_theme["colors"])
        merged.update(palette)
        return {k: normalize_hex(v) for k, v in merged.items()}

    return {k: normalize_hex(v) for k, v in palette.items()}


def resolve_active_palette(context: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    """Resolve active theme metadata and color palette from merged context."""
    appearance = context.get("config", {}).get("appearance", {})
    theme_name = appearance.get("theme", "bsd-crimson")
    theme_data = load_theme(theme_name)
    palette = {k: normalize_hex(v) for k, v in theme_data.get("colors", {}).items()}

    dynamic = bool(appearance.get("dynamic_wallpaper_colors", False))
    wallpaper = appearance.get("wallpaper")
    if dynamic and wallpaper and Path(wallpaper).expanduser().is_file():
        palette = extract_palette_from_wallpaper(Path(wallpaper).expanduser(), base_theme=theme_data)

    return theme_data, palette
