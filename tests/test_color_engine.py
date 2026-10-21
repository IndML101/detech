"""Tests for DETech Hybrid Color Engine (static themes + dynamic wallpaper extraction)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from detech.core.color_engine import (
    extract_palette_from_wallpaper,
    hex_to_hypr_rgba,
    hex_to_rgba_css,
    list_themes,
    load_theme,
    normalize_hex,
)


def test_color_format_helpers() -> None:
    assert normalize_hex("#E63946") == "#e63946"
    assert normalize_hex("abc") == "#aabbcc"
    assert hex_to_rgba_css("#e63946", 0.85) == "rgba(230, 57, 70, 0.85)"
    assert hex_to_hypr_rgba("#e63946", "ee") == "rgba(e63946ee)"


def test_curated_themes_catalog() -> None:
    themes = list_themes()
    names = {t["name"] for t in themes}
    assert {"bsd-crimson", "ryoku-matcha", "hyde-catppuccin", "tokyo-cyber", "nordic-frost"}.issubset(names)

    bsd = load_theme("bsd-crimson")
    assert bsd["colors"]["accent"] == "#e63946"
    assert "color0" in bsd["colors"]
    assert "color15" in bsd["colors"]


def test_dynamic_wallpaper_palette_extraction(tmp_path: Path) -> None:
    wall = tmp_path / "sample_wall.png"
    img = Image.new("RGB", (120, 120), color=(30, 140, 210))
    img.save(wall)

    palette = extract_palette_from_wallpaper(wall)
    required_keys = {
        "bg_primary",
        "bg_secondary",
        "fg_primary",
        "accent",
        "accent_alt",
        "urgent",
        "border_active",
        "color0",
        "color15",
    }
    assert required_keys.issubset(set(palette.keys()))
    for val in palette.values():
        assert val.startswith("#") and len(val) == 7
