"""Tests for DETech Rofi Menu Entry Builders & Dispatch Logic."""

from __future__ import annotations

from pathlib import Path

from detech.menus.font_menu import build_font_menu_entries
from detech.menus.glyph_emoji_menu import format_glyph_entries
from detech.menus.keybinds_menu import (
    build_hyprctl_dispatch_command,
    build_hyprctl_lua_dispatch_command,
    format_keybind_entries,
)
from detech.menus.pkg_menu import build_software_menu_entries
from detech.menus.screenshot_menu import build_screenshot_menu_entries
from detech.menus.theme_menu import build_theme_menu_entries
from detech.menus.wallpaper_menu import build_wallpaper_menu_entries
from detech.menus.widget_menus import MINIMALIST_SEPARATOR, build_calendar_menu_entries


def test_keybinds_menu_formatting_and_dispatch() -> None:
    entries = format_keybind_entries()
    assert len(entries) >= 25
    fonts_bind = next(e for e in entries if "detech menu fonts" in e["arg"])
    assert "SUPER + SHIFT + F" in fonts_bind["combo"]
    hyprlock_bind = next(e for e in entries if "detech menu hyprlock" in e["arg"])
    assert "SUPER + SHIFT + L" in hyprlock_bind["combo"]
    assert build_hyprctl_dispatch_command(hyprlock_bind) == ["hyprctl", "dispatch", "exec", "detech menu hyprlock"]
    assert build_hyprctl_dispatch_command(fonts_bind) == ["hyprctl", "dispatch", "exec", "detech menu fonts"]
    assert build_hyprctl_lua_dispatch_command(fonts_bind) == [
        "hyprctl",
        "dispatch",
        'hl.dsp.exec_cmd("detech menu fonts")',
    ]
    shot_bind = next(e for e in entries if "detech screenshot area" in e["arg"])
    assert shot_bind["combo"] == "Print"
    shot_menu_bind = next(e for e in entries if "detech menu screenshot" in e["arg"])
    assert "SUPER + SHIFT + S" in shot_menu_bind["combo"]


def test_font_and_theme_and_glyph_menus() -> None:
    font_rows = build_font_menu_entries(installed_override={"JetBrainsMono Nerd Font"}, active_font="JetBrainsMono Nerd Font")
    assert any(r["type"] == "font" and "★ Active" in r["label"] for r in font_rows)
    assert any(r["type"] == "size" for r in font_rows)

    theme_rows = build_theme_menu_entries(active_theme="bsd-crimson")
    assert len(theme_rows) == 10

    glyph_rows = format_glyph_entries()
    assert any(g["char"] == "" for g in glyph_rows)

    pkg_rows = build_software_menu_entries(installed_names={"neovim"})
    nvim_row = next(r for r in pkg_rows if r["name"] == "neovim")
    assert nvim_row["action"] == "delete"

    shot_entries = build_screenshot_menu_entries()
    assert len(shot_entries) >= 9
    assert any("Selected Area" in r["label"] for r in shot_entries)


def test_widget_menu_separators() -> None:
    _, entries = build_calendar_menu_entries(year=2026, month=10)
    assert MINIMALIST_SEPARATOR in entries
    assert "────────────────────────────" not in entries


def test_wallpaper_menu_entries() -> None:
    wallpapers = [
        Path("/usr/local/share/hypr/wall0.png"),
        Path("/usr/local/share/wallpapers/sunset.jpg"),
    ]
    labels, entries = build_wallpaper_menu_entries(wallpapers)
    assert len(labels) == 2
    assert len(entries) == 2
    assert labels[0] == "󰸉  wall0.png  (/usr/local/share/hypr)"
    assert entries[0] == f"{labels[0]}\0icon\x1f/usr/local/share/hypr/wall0.png"
    assert "\0icon\x1f" in entries[1]
