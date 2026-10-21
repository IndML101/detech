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
    assert len(list_waybar_layouts()) == 15
    assert len(list_rofi_layouts()) == 15
    assert len(list_starship_prompts()) == 15
    assert len(list_hyprlock_layouts()) >= 4


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
    assert len(result["written_files"]) >= 20

    # Verify Hyprland configs
    assert (out_dir / "hypr" / "hyprland.conf").is_file()
    assert (out_dir / "hypr" / "detech-keybinds.conf").is_file()
    assert (out_dir / "hypr" / "detech-plugins.conf").is_file()
    assert (out_dir / "hypr" / "hyprlock.conf").is_file()
    assert (out_dir / "hypr" / "hypridle.conf").is_file()
    assert "acpiconf -s 3" in (out_dir / "hypr" / "hypridle.conf").read_text(encoding="utf-8")

    # Verify Waybar JSONC is valid JSON after stripping header comment
    wb_lines = (out_dir / "waybar" / "config.jsonc").read_text(encoding="utf-8").splitlines()
    wb_json = json.loads("\n".join(wb_lines[1:]))
    assert "custom/bsd-battery" in wb_json["modules-right"]

    # Verify Rofi & Starship
    rofi_text = (out_dir / "rofi" / "config.rasi").read_text(encoding="utf-8")
    assert "spotlight-minimal" in rofi_text

    starship_text = (out_dir / "starship.toml").read_text(encoding="utf-8")
    assert "bsd-devil" in starship_text
    assert "#a7c080" in starship_text  # ryoku-matcha accent color
