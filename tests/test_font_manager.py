"""Tests for DETech Nerd Fonts Manager & System-Wide Font Switching."""

from __future__ import annotations

from pathlib import Path

from detech.core.compiler import compile_all
from detech.core.font_manager import (
    NERD_FONT_CATALOG,
    get_nerd_font_status_list,
    resolve_font_settings,
)
from detech.core.state import get_effective_context, update_state


def test_nerd_font_catalog_and_status() -> None:
    assert len(NERD_FONT_CATALOG) >= 16
    mock_installed = {"FiraCode Nerd Font", "CustomBSD Nerd Font"}
    status_list = get_nerd_font_status_list(installed_override=mock_installed)

    by_family = {item["family"]: item for item in status_list}
    assert by_family["FiraCode Nerd Font"]["installed"] is True
    assert by_family["JetBrainsMono Nerd Font"]["installed"] is False
    assert by_family["CustomBSD Nerd Font"]["installed"] is True


def test_font_switching_propagates_across_all_configs(tmp_path: Path) -> None:
    state_file = tmp_path / "state.json"
    out_dir = tmp_path / "config"

    update_state(
        state_path=state_file,
        font_mono="CaskaydiaCove Nerd Font",
        font_sans="CaskaydiaCove Nerd Font Propo",
        font_size=13,
    )
    ctx = get_effective_context(state_path=state_file)
    fonts = resolve_font_settings(ctx)
    assert fonts["mono"] == "CaskaydiaCove Nerd Font"
    assert fonts["size"] == 13

    compile_all(output_dir=out_dir, state_path=state_file, reload_daemons=False)

    assert "CaskaydiaCove Nerd Font" in (out_dir / "kitty" / "kitty.conf").read_text(encoding="utf-8")
    assert "CaskaydiaCove Nerd Font" in (out_dir / "waybar" / "style.css").read_text(encoding="utf-8")
    assert "CaskaydiaCove Nerd Font 14" in (out_dir / "rofi" / "fonts.rasi").read_text(encoding="utf-8")
    assert "CaskaydiaCove Nerd Font" in (out_dir / "hypr" / "hyprlock.conf").read_text(encoding="utf-8")
    assert "CaskaydiaCove Nerd Font Propo 13" in (out_dir / "dunst" / "dunstrc").read_text(encoding="utf-8")
    assert "CaskaydiaCove Nerd Font Propo 13" in (out_dir / "gtk-3.0" / "settings.ini").read_text(encoding="utf-8")
    assert "CaskaydiaCove Nerd Font" in (out_dir / "qt6ct" / "qt6ct.conf").read_text(encoding="utf-8")
