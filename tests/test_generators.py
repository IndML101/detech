"""Tests for DETech Native Config Generators and Preset Catalogs (15 Waybar, 15 Rofi, 15 Starship)."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from detech.core.compiler import compile_all
from detech.core.state import update_state
from detech.generators.hyprland import list_hyprlock_layouts, list_plugin_presets
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
    assert len(list_plugin_presets()) == 6

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

    # Verify Hyprland configs (both native 0.56/0.57+ .lua and legacy .conf fallbacks)
    assert (out_dir / "hypr" / "hyprland.lua").is_file()
    assert (out_dir / "hypr" / "detech-colors.lua").is_file()
    assert (out_dir / "hypr" / "detech-keybinds.lua").is_file()
    assert (out_dir / "hypr" / "detech-plugins.lua").is_file()
    assert (out_dir / "hypr" / "hyprland.conf").is_file()
    assert (out_dir / "hypr" / "detech-keybinds.conf").is_file()
    assert (out_dir / "hypr" / "detech-plugins.conf").is_file()
    assert (out_dir / "hypr" / "hyprlock.conf").is_file()
    assert (out_dir / "hypr" / "hypridle.conf").is_file()
    assert "acpiconf -s 3" in (out_dir / "hypr" / "hypridle.conf").read_text(encoding="utf-8")
    assert "hl.dsp.dpms" in (out_dir / "hypr" / "hypridle.conf").read_text(encoding="utf-8")

    # Verify Waybar launcher script and D-Bus readiness
    wb_sh = out_dir / "hypr" / "launch-waybar.sh"
    assert wb_sh.is_file()
    wb_sh_text = wb_sh.read_text(encoding="utf-8")
    assert "dbus-launch" in wb_sh_text
    assert "exec waybar" in wb_sh_text

    # Verify Wallpaper launcher script
    wp_sh = out_dir / "hypr" / "launch-wallpaper.sh"
    assert wp_sh.is_file()
    wp_sh_text = wp_sh.read_text(encoding="utf-8")
    assert "swaybg" in wp_sh_text
    assert "hyprpaper" in wp_sh_text

    hl_lua_text = (out_dir / "hypr" / "hyprland.lua").read_text(encoding="utf-8")
    assert 'local colors = require("detech-colors")' in hl_lua_text
    assert 'hl.on("hyprland.start", function()' in hl_lua_text
    assert "launch-waybar.sh" in hl_lua_text
    assert "launch-wallpaper.sh" in hl_lua_text
    assert "dbus-update-activation-environment" in hl_lua_text
    assert "hl.window_rule({" in hl_lua_text
    assert "hl.layer_rule({" in hl_lua_text
    assert 'require("detech-keybinds")' in hl_lua_text
    assert 'require("detech-plugins")' in hl_lua_text

    hl_conf_text = (out_dir / "hypr" / "hyprland.conf").read_text(encoding="utf-8")
    assert "launch-waybar.sh" in hl_conf_text
    assert "launch-wallpaper.sh" in hl_conf_text
    assert "dbus-update-activation-environment" in hl_conf_text

    kb_lua_text = (out_dir / "hypr" / "detech-keybinds.lua").read_text(encoding="utf-8")
    assert "hl.bind(" in kb_lua_text
    assert 'hl.dsp.layout("togglesplit")' in kb_lua_text
    assert "hl.dsp.window.drag()" in kb_lua_text
    assert "hl.dsp.window.resize()" in kb_lua_text

    plug_lua_default = (out_dir / "hypr" / "detech-plugins.lua").read_text(encoding="utf-8")
    assert "hl.gesture({" in plug_lua_default
    assert 'action = "workspace"' in plug_lua_default

    hl_text = (out_dir / "hypr" / "hyprland.conf").read_text(encoding="utf-8")
    assert "pseudotile" not in hl_text
    assert "windowrulev2" not in hl_text
    assert "windowrule = float on, match:class ^(pavucontrol|qt5ct|qt6ct|nwg-look)$" in hl_text
    assert "layerrule = blur on, match:namespace rofi" in hl_text
    assert "layerrule = ignore_alpha 0, match:namespace rofi" in hl_text

    kb_text = (out_dir / "hypr" / "detech-keybinds.conf").read_text(encoding="utf-8")
    assert "layoutmsg, togglesplit" in kb_text
    assert "hyprexpo:expo" not in kb_text

    plug_default = (out_dir / "hypr" / "detech-plugins.conf").read_text(encoding="utf-8")
    assert "gesture = 3, horizontal, workspace" in plug_default
    assert "gesture_fingers" not in plug_default

    # Verify active Waybar JSONC is valid JSON after stripping header comment
    wb_lines = (out_dir / "waybar" / "config.jsonc").read_text(encoding="utf-8").splitlines()
    wb_json = json.loads("\n".join(wb_lines[1:]))
    assert "custom/bsd-battery" in wb_json["modules-right"]
    assert "custom/bsd-zfs" in wb_json["modules-left"]
    assert "custom/calendar" in wb_json["modules-center"]
    assert "custom/weather" in wb_json["modules-center"]
    assert "custom/bsd-net" in wb_json["modules-right"]
    assert "custom/dnd" in wb_json["modules-right"]
    assert "custom/clipboard" in wb_json["modules-right"]
    assert "custom/bsd-uptime" in wb_json["modules-left"]
    assert "calendar" in wb_json["clock"]

    # Verify Neofetch config and shell startup hook
    neofetch_conf = out_dir / "neofetch" / "config.conf"
    shell_init = out_dir / "detech" / "shell-init.sh"
    assert neofetch_conf.is_file()
    assert shell_init.is_file()
    nf_text = neofetch_conf.read_text(encoding="utf-8")
    assert 'ascii_distro="FreeBSD"' in nf_text
    assert "ryoku-matcha" in nf_text
    sh_text = shell_init.read_text(encoding="utf-8")
    assert 'export DETECH_NEOFETCH="1"' in sh_text
    assert "neofetch --config" in sh_text

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
    assert "border: 1px 0px 0px 0px;" in rofi_text
    assert "border-color: @bg-tertiary;" in rofi_text

    colors_rasi = (out_dir / "rofi" / "colors.rasi").read_text(encoding="utf-8")
    assert "separatorcolor:" in colors_rasi

    menu_rasi = (out_dir / "rofi" / "menu.rasi").read_text(encoding="utf-8")
    assert "padding: 14px 18px;" in menu_rasi
    assert "border: 1px 0px 0px 0px;" in menu_rasi
    assert "border-color: @bg-tertiary;" in menu_rasi

    for item in list_rofi_layouts():
        lid = item["id"]
        r_file = out_dir / "rofi" / "layouts" / f"{lid}.rasi"
        assert r_file.is_file()
        r_content = r_file.read_text(encoding="utf-8")
        assert f"({lid})" in r_content
        assert item["prompt_symbol"] in r_content
        assert "border: 1px 0px 0px 0px;" in r_content
        assert "border-color: @bg-tertiary;" in r_content

    # Validate Rofi syntax parsing if rofi binary is installed
    if shutil.which("rofi"):
        for rasi_file in [out_dir / "rofi" / "config.rasi", out_dir / "rofi" / "menu.rasi", *(out_dir / "rofi" / "layouts").glob("*.rasi")]:
            proc = subprocess.run(
                ["rofi", "-dump-theme", "-theme", str(rasi_file)],
                capture_output=True,
                text=True,
                check=False,
            )
            assert proc.returncode == 0, f"Rofi returned non-zero for {rasi_file}: {proc.stderr}"
            assert "Failed to parse theme" not in proc.stderr, f"Rofi syntax parsing error in {rasi_file}:\n{proc.stderr}"

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

    # Verify GTK-2/3/4 and Kvantum asset bundle
    assert (out_dir / "gtk-2.0" / "gtkrc").is_file()
    assert (out_dir / "Kvantum" / "DETech" / "DETech.kvconfig").is_file()
    assert (out_dir / "Kvantum" / "DETech" / "DETech.svg").is_file()
    kv_svg = (out_dir / "Kvantum" / "DETech" / "DETech.svg").read_text(encoding="utf-8")
    assert "#a7c080" in kv_svg

    # Verify switching Hyprland plugin presets
    update_state(state_path=state_file, plugin_preset="eye-candy")
    compile_all(output_dir=out_dir, state_path=state_file, reload_daemons=False)
    plug_text = (out_dir / "hypr" / "detech-plugins.conf").read_text(encoding="utf-8")
    assert "Preset: eye-candy" in plug_text
    assert "hyprtrails {" in plug_text
    assert "borders-plus-plus {" in plug_text

    update_state(state_path=state_file, plugin_preset="bsd-gamer")
    compile_all(output_dir=out_dir, state_path=state_file, reload_daemons=False)
    plug_gamer = (out_dir / "hypr" / "detech-plugins.conf").read_text(encoding="utf-8")
    assert "csgo-vulkan-fix {" in plug_gamer
