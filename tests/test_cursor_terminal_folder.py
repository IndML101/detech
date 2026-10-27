"""Tests for Terminal Text Colors, Trackpad Cursor Themes, and Thunar Theme-Colored Folder Icons."""

from __future__ import annotations

import json
from pathlib import Path

from detech.cli import main
from detech.core.color_engine import list_themes, resolve_active_palette
from detech.core.compiler import compile_all
from detech.core.cursor_manager import (
    CURSOR_CATALOG,
    TRACKPAD_CURSOR_SIZES,
    discover_installed_cursor_themes,
    list_cursor_themes,
    sync_default_cursor_theme,
)
from detech.core.folder_colors import (
    PAPIRUS_FOLDER_COLORS,
    THEME_FOLDER_COLOR_MAP,
    generate_custom_folder_svg,
    match_accent_to_folder_color,
    resolve_folder_color,
    sync_theme_folder_icons,
)
from detech.core.state import update_state
from detech.generators.gtk_qt_dunst import render_gtk_css
from detech.generators.hyprland import generate_hypr_configs
from detech.generators.terminal_shell import (
    generate_terminal_and_shell_configs,
    render_alacritty_conf,
    render_alacritty_theme,
    render_foot_conf,
    render_foot_theme,
    render_kitty_theme,
    render_term_colors_sh,
)


def test_theme_presets_have_folder_and_cursor_definitions() -> None:
    """Verify all 10 curated themes have valid folder_color and cursor_theme attributes."""
    themes = list_themes()
    assert len(themes) == 10

    for t in themes:
        tname = t["name"]
        assert "folder_color" in t, f"Theme {tname} missing folder_color"
        assert t["folder_color"] in PAPIRUS_FOLDER_COLORS, f"Theme {tname} folder_color {t['folder_color']} not in catalog"
        assert "cursor_theme" in t, f"Theme {tname} missing cursor_theme"
        assert len(t["cursor_theme"]) > 0


def test_terminal_text_color_palette_generation(tmp_path: Path) -> None:
    """Verify Kitty, Alacritty, Foot, and OSC terminal color palette generation."""
    ctx = {
        "config": {
            "appearance": {"theme": "bsd-crimson"},
            "general": {"shell": "zsh"},
        }
    }
    _, palette = resolve_active_palette(ctx)
    fonts = {"mono": "JetBrainsMono Nerd Font", "size": 11}

    out_dir = tmp_path / "term_test"
    written = generate_terminal_and_shell_configs(ctx, palette, fonts, out_dir)
    assert len(written) >= 20

    # 1. Kitty Palette
    kitty_theme = out_dir / "kitty" / "detech-theme.conf"
    assert kitty_theme.is_file()
    k_content = kitty_theme.read_text(encoding="utf-8")
    assert f"background {palette['bg_primary']}" in k_content
    assert f"foreground {palette['fg_primary']}" in k_content
    assert f"cursor {palette['accent']}" in k_content
    assert f"cursor_text_color {palette['bg_primary']}" in k_content
    assert f"selection_background {palette['bg_tertiary']}" in k_content
    assert f"selection_foreground {palette['fg_primary']}" in k_content
    for i in range(16):
        assert f"color{i} {palette[f'color{i}']}" in k_content

    # 2. Alacritty Palette
    alac_theme = out_dir / "alacritty" / "detech-theme.toml"
    assert alac_theme.is_file()
    a_content = alac_theme.read_text(encoding="utf-8")
    assert f'background = "{palette["bg_primary"]}"' in a_content
    assert f'foreground = "{palette["fg_primary"]}"' in a_content
    assert f'cursor = "{palette["accent"]}"' in a_content
    assert f'red     = "{palette["color1"]}"' in a_content
    assert f'green   = "{palette["color2"]}"' in a_content

    alac_conf = out_dir / "alacritty" / "alacritty.toml"
    assert alac_conf.is_file()
    assert "detech-theme.toml" in alac_conf.read_text(encoding="utf-8")

    # 3. Foot Palette
    foot_theme = out_dir / "foot" / "detech-theme.ini"
    assert foot_theme.is_file()
    f_content = foot_theme.read_text(encoding="utf-8")
    assert f"background={palette['bg_primary'].lstrip('#')}" in f_content
    assert f"foreground={palette['fg_primary'].lstrip('#')}" in f_content
    assert f"regular1={palette['color1'].lstrip('#')}" in f_content

    foot_conf = out_dir / "foot" / "foot.ini"
    assert foot_conf.is_file()
    assert "detech-theme.ini" in foot_conf.read_text(encoding="utf-8")

    # 4. OSC Terminal Color Escape Code Hook
    term_colors_sh = out_dir / "detech" / "term-colors.sh"
    assert term_colors_sh.is_file()
    t_content = term_colors_sh.read_text(encoding="utf-8")
    assert f"printf '\\033]10;{palette['fg_primary']}\\007'" in t_content
    assert f"printf '\\033]11;{palette['bg_primary']}\\007'" in t_content
    assert f"printf '\\033]12;{palette['accent']}\\007'" in t_content
    assert f"printf '\\033]4;1;{palette['color1']}\\007'" in t_content

    # 5. Shell Init Sources term-colors.sh
    shell_init = out_dir / "detech" / "shell-init.sh"
    assert shell_init.is_file()
    assert "term-colors.sh" in shell_init.read_text(encoding="utf-8")


def test_cursor_manager_catalog_and_trackpad_sizes() -> None:
    """Verify cursor catalog has rich modern cursors and trackpad sizes."""
    assert len(CURSOR_CATALOG) >= 15
    ids = {c.id for c in CURSOR_CATALOG}
    assert "Bibata-Modern-Ice" in ids
    assert "Bibata-Modern-Classic" in ids
    assert "Bibata-Modern-Amber" in ids
    assert "Catppuccin-Mocha-Dark-Cursors" in ids
    assert "Nordzy-cursors" in ids
    assert "Capitaine-Cursors" in ids
    assert "BreezeX-Black" in ids

    # Check trackpad sizes catalog
    assert len(TRACKPAD_CURSOR_SIZES) == 5
    sizes = [item["size"] for item in TRACKPAD_CURSOR_SIZES]
    assert 24 in sizes
    assert 28 in sizes
    assert 32 in sizes
    assert 36 in sizes
    assert 48 in sizes

    # Check listing cursor themes
    cursor_items = list_cursor_themes(active_cursor="Bibata-Modern-Ice")
    active_found = False
    for item in cursor_items:
        if item["id"] == "Bibata-Modern-Ice":
            assert item["active"] is True
            active_found = True
    assert active_found


def test_hyprland_trackpad_and_cursor_configuration(tmp_path: Path) -> None:
    """Verify Hyprland generated config includes rich trackpad options and cursor settings."""
    ctx = {
        "config": {
            "appearance": {
                "theme": "bsd-crimson",
                "cursor_theme": "Bibata-Modern-Ice",
                "cursor_size": 32,
            },
            "input": {
                "kb_layout": "us",
                "follow_mouse": 1,
                "sensitivity": 0.2,
                "touchpad": {
                    "natural_scroll": True,
                    "tap_to_click": True,
                    "drag_lock": True,
                    "tap_and_drag": True,
                    "middle_button_emulation": True,
                    "clickfinger_behavior": False,
                    "disable_while_typing": True,
                    "scroll_factor": 1.2,
                },
            },
        }
    }
    _, palette = resolve_active_palette(ctx)
    fonts = {"mono": "JetBrainsMono Nerd Font", "sans": "JetBrainsMono Nerd Font Propo", "size": 11, "bar_size": 11, "rofi_size": 12, "lock_size": 48}

    out_dir = tmp_path / "hypr_trackpad_test"
    generate_hypr_configs(ctx, palette, fonts, out_dir)

    # Legacy .conf
    conf_text = (out_dir / "hypr" / "hyprland.conf").read_text(encoding="utf-8")
    assert "env = XCURSOR_THEME,Bibata-Modern-Ice" in conf_text
    assert "env = XCURSOR_SIZE,32" in conf_text
    assert "env = HYPRCURSOR_THEME,Bibata-Modern-Ice" in conf_text
    assert "env = HYPRCURSOR_SIZE,32" in conf_text
    assert "exec-once = hyprctl setcursor Bibata-Modern-Ice 32" in conf_text
    assert "tap-to-click = true" in conf_text
    assert "drag_lock = true" in conf_text
    assert "scroll_factor = 1.2" in conf_text
    assert "cursor {" in conf_text
    assert "enable_hyprcursor = true" in conf_text

    # Native .lua
    lua_text = (out_dir / "hypr" / "hyprland.lua").read_text(encoding="utf-8")
    assert 'hl.env("XCURSOR_THEME", "Bibata-Modern-Ice")' in lua_text
    assert 'hl.env("XCURSOR_SIZE", "32")' in lua_text
    assert 'hl.env("HYPRCURSOR_THEME", "Bibata-Modern-Ice")' in lua_text
    assert "natural_scroll = true" in lua_text
    assert "tap_to_click = true" in lua_text
    assert "drag_lock = true" in lua_text
    assert "scroll_factor = 1.2" in lua_text


def test_thunar_folder_colors_resolution_and_sync(tmp_path: Path) -> None:
    """Verify theme folder color resolution, Papirus overlay sync, and Thunar CSS."""
    # 1. Preset Mapping
    assert THEME_FOLDER_COLOR_MAP["bsd-crimson"] == "carmine"
    assert THEME_FOLDER_COLOR_MAP["ryoku-matcha"] == "green"
    assert THEME_FOLDER_COLOR_MAP["tokyo-cyber"] == "cyan"
    assert THEME_FOLDER_COLOR_MAP["gruvbox-material"] == "orange"

    # 2. Nearest Color Distance Matching
    assert match_accent_to_folder_color("#e63946") in ("red", "carmine")
    assert match_accent_to_folder_color("#a7c080") in ("green", "teal")
    assert match_accent_to_folder_color("#7aa2f7") in ("blue", "cyan", "nordic")

    # 3. Dynamic Custom SVG Generation
    svg_code = generate_custom_folder_svg("#e63946", "#ff758f", size=48)
    assert '<svg xmlns="http://www.w3.org/2000/svg"' in svg_code
    assert 'fill:#e63946' in svg_code
    assert 'fill:#ff758f' in svg_code

    # 4. Folder Icons Synchronization
    icons_target = tmp_path / "share" / "icons"
    ctx = {"config": {"appearance": {"theme": "bsd-crimson"}}}
    _, palette = resolve_active_palette(ctx)
    written = sync_theme_folder_icons("carmine", palette, target_icons_dir=icons_target, base_theme_name="Papirus-Dark")
    assert len(written) > 0
    theme_dir = icons_target / "Papirus-Dark"
    assert (theme_dir / "index.theme").is_file()
    assert (theme_dir / "48x48" / "places" / "folder.svg").is_file() or (theme_dir / "48x48" / "places" / "folder.svg").is_symlink()

    # 5. Thunar GTK-3 CSS Styling
    css = render_gtk_css(palette)
    assert "window.thunar, thunar-window, .thunar, ThunarWindow" in css
    assert "thunar .view" in css
    assert "thunar .sidebar" in css
    assert "thunar .view:selected" in css


def test_cli_cursor_and_folder_color_commands(tmp_path: Path, monkeypatch) -> None:
    """Verify `detech cursor`, `detech folder-color`, and `detech term-colors` CLI commands."""
    state_file = tmp_path / "state.json"
    out_dir = tmp_path / "xdg_config"
    monkeypatch.setenv("DETECH_STATE_FILE", str(state_file))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(out_dir))

    # 1. detech cursor set
    ret = main(["set", "cursor", "Catppuccin-Mocha-Dark-Cursors", "--size", "28", "--output-dir", str(out_dir), "--no-reload"])
    assert ret == 0
    raw_state = json.loads(state_file.read_text(encoding="utf-8"))
    assert raw_state["cursor_theme"] == "Catppuccin-Mocha-Dark-Cursors"
    assert raw_state["cursor_size"] == 28

    # 2. detech folder-color set
    ret = main(["set", "folder-color", "green", "--output-dir", str(out_dir), "--no-reload"])
    assert ret == 0
    raw_state = json.loads(state_file.read_text(encoding="utf-8"))
    assert raw_state["folder_color"] == "green"

    # 3. detech status shows cursor and folder-color
    ret = main(["status", "--json"])
    assert ret == 0

    # 4. detech list cursors & folder-colors
    assert main(["list", "cursors"]) == 0
    assert main(["list", "folder-colors"]) == 0

    # 5. detech term-colors --print
    assert main(["term-colors", "--print"]) == 0


def test_cursor_shortcut_keybind_registered() -> None:
    """Verify SUPER + SHIFT + X shortcut is registered for cursor picker."""
    from detech.menus.keybinds_menu import format_keybind_entries

    entries = format_keybind_entries()
    found = False
    for entry in entries:
        if "detech menu cursors" in entry.get("arg", "") and "X" in entry.get("combo", ""):
            found = True
            break
    assert found, "SUPER + SHIFT + X shortcut for detech menu cursors not found in keybinds"

