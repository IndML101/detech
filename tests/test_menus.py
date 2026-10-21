"""Tests for DETech Rofi Menu Entry Builders & Dispatch Logic."""

from __future__ import annotations

from detech.menus.font_menu import build_font_menu_entries
from detech.menus.glyph_emoji_menu import format_glyph_entries
from detech.menus.keybinds_menu import build_hyprctl_dispatch_command, format_keybind_entries
from detech.menus.pkg_menu import build_software_menu_entries
from detech.menus.theme_menu import build_theme_menu_entries


def test_keybinds_menu_formatting_and_dispatch() -> None:
    entries = format_keybind_entries()
    assert len(entries) >= 25
    fonts_bind = next(e for e in entries if "detech menu fonts" in e["arg"])
    assert "SUPER + SHIFT + F" in fonts_bind["combo"]
    assert build_hyprctl_dispatch_command(fonts_bind) == ["hyprctl", "dispatch", "exec", "detech menu fonts"]


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
