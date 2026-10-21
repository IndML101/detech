"""Tests for DETech Native Config Generators and Preset Catalogs (15 Waybar, 15 Rofi, 15 Starship)."""

from __future__ import annotations

import json
from pathlib import Path

from detech.core.compiler import compile_all
from detech.core.state import update_state
from detech.generators.hyprland import list_hyprlock_layouts
from detech.generators.rofi import list_rofi_layouts
from detech.generators.terminal_shell import list_starship_prompts
from detech.generators.waybar import list_waybar_layouts


def test_preset_catalog_counts() -> None:
    waybar_layouts = list_waybar_layouts()
    rofi_layouts = list_rofi_layouts()
    starship_prompts = list_starship_prompts()

    assert len(waybar_layouts) == 15
    assert len(rofi_layouts) == 15
    assert len(starship_prompts) == 15
    assert len(list_hyprlock_layouts()) >= 4

    # Ensure every preset has rich metadata
    for item in waybar_layouts:
        assert item.get("id")
        assert item.get("name")
        assert item.get("description")
        assert item.get("style_variant")
        assert item.get("workspace_icons")

    for item in rofi_layouts:
        assert item.get("id")
        assert item.get("name")
        assert item.get("description")
        assert item.get("style_variant")
        assert item.get("prompt_symbol")

    for item in starship_prompts:
        assert item.get("id")
        assert item.get("name")
        assert item.get("description")
        assert item.get("preview")
        assert item.get("style_variant")


def test_compile_all_generates_complete_desktop_configs(tmp_path: Path) -> None:
    state_file = tmp_path / "state.json"
    out_dir = tmp_path / "xdg_config"

    update_state(
        state_path=state_file,
        theme="ryoku-matcha",
        waybar_layout="freebsd-telemetry",
        rofi_layout="spotlight-minimal",
        starship_preset="bsd-devil",
        hyprlock_layout="bsd-fortress",
    )

    result = compile_all(output_dir=out_dir, state_path=state_file, reload_daemons=False)
    assert len(result["written_files"]) >= 80

    # Verify Hyprland configs
    assert (out_dir / "hypr" / "hyprland.conf").is_file()
    assert (out_dir / "hypr" / "detech-keybinds.conf").is_file()
    assert (out_dir / "hypr" / "detech-plugins.conf").is_file()
    assert (out_dir / "hypr" / "hyprlock.conf").is_file()
    assert (out_dir / "hypr" / "hypridle.conf").is_file()
    assert "acpiconf -s 3" in (out_dir / "hypr" / "hypridle.conf").read_text(encoding="utf-8")

    # Verify active Waybar JSONC is valid JSON after stripping header comment
    wb_lines = (out_dir / "waybar" / "config.jsonc").read_text(encoding="utf-8").splitlines()
    wb_json = json.loads("\n".join(wb_lines[1:]))
    assert "custom/bsd-battery" in wb_json["modules-right"]
    assert "custom/bsd-zfs" in wb_json["modules-left"]

    # Verify all 15 pre-compiled Waybar layouts and stylesheets
    for item in list_waybar_layouts():
        lid = item["id"]
        l_file = out_dir / "waybar" / "layouts" / f"{lid}.jsonc"
        s_file = out_dir / "waybar" / "styles" / f"{lid}.css"
        assert l_file.is_file()
        assert s_file.is_file()
        parsed = json.loads("\n".join(l_file.read_text(encoding="utf-8").splitlines()[1:]))
        assert parsed["position"] == item["position"]
        assert f"Layout: {lid}" in s_file.read_text(encoding="utf-8")

    assert (out_dir / "waybar" / "layouts" / "dual-bar-secondary.jsonc").is_file()

    # Verify all 15 pre-compiled Rofi layouts and active config.rasi
    rofi_text = (out_dir / "rofi" / "config.rasi").read_text(encoding="utf-8")
    assert "spotlight-minimal" in rofi_text
    for item in list_rofi_layouts():
        lid = item["id"]
        r_file = out_dir / "rofi" / "layouts" / f"{lid}.rasi"
        assert r_file.is_file()
        r_content = r_file.read_text(encoding="utf-8")
        assert f"({lid})" in r_content
        assert item["prompt_symbol"] in r_content

    # Verify all 15 pre-compiled Starship prompts and active starship.toml
    starship_text = (out_dir / "starship.toml").read_text(encoding="utf-8")
    assert "bsd-devil" in starship_text
    assert "#a7c080" in starship_text  # ryoku-matcha accent color
    for item in list_starship_prompts():
        pid = item["id"]
        p_file = out_dir / "starship" / "presets" / f"{pid}.toml"
        assert p_file.is_file()
        p_content = p_file.read_text(encoding="utf-8")
        assert f"({pid})" in p_content
        assert item["preview"] in p_content
