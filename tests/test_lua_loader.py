"""Tests for DETech declarative Lua configuration parser."""

from __future__ import annotations

from detech.core.lua_loader import load_all_user_configs, load_lua_string


def test_pure_lua_parser_handles_locals_and_nested_tables() -> None:
    lua_src = """
    -- Sample comment
    local mod = "SUPER"
    --[[ Multi-line
         comment ]]
    return {
        main_mod = mod,
        gaps = 8,
        blur = { enabled = true, vibrancy = 0.25 },
        binds = {
            { mod = {mod, "SHIFT"}, key = "F", desc = "Nerd Fonts Picker" },
        },
    }
    """
    parsed = load_lua_string(lua_src, use_lupa=False)
    assert parsed["main_mod"] == "SUPER"
    assert parsed["gaps"] == 8
    assert parsed["blur"]["enabled"] is True
    assert parsed["blur"]["vibrancy"] == 0.25
    assert parsed["binds"][0]["mod"] == ["SUPER", "SHIFT"]
    assert parsed["binds"][0]["key"] == "F"


def test_load_all_default_repo_lua_configs() -> None:
    configs = load_all_user_configs()
    assert set(configs.keys()) == {"config", "keybinds", "monitors", "rules", "plugins", "freebsd"}
    assert configs["config"]["general"]["terminal"] == "kitty"
    assert configs["config"]["fonts"]["mono"] == "JetBrainsMono Nerd Font"
    assert configs["freebsd"]["os"] == "FreeBSD"
    assert len(configs["keybinds"]["binds"]) >= 25


def test_pure_lua_parser_preserves_unicode_and_nerd_fonts() -> None:
    lua_src = """
    return {
        prompt = " ~/detech  main ❯",
        clock = " {:%H:%M}",
        symbols = "󱎫 󰥔   󰁔",
    }
    """
    parsed = load_lua_string(lua_src, use_lupa=False)
    assert parsed["prompt"] == " ~/detech  main ❯"
    assert parsed["clock"] == " {:%H:%M}"
    assert parsed["symbols"] == "󱎫 󰥔   󰁔"

