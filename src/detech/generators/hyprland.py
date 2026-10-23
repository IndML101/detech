"""Hypr Ecosystem Configuration Generator (`hyprland`, `hyprlock`, `hypridle`, `hyprpaper`)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from detech.core.color_engine import hex_to_hypr_rgba, hex_to_rgb
from detech.core.lua_loader import load_lua_file
from detech.core.paths import get_presets_dir


def list_hyprlock_layouts() -> list[dict[str, Any]]:
    """Return available Hyprlock screen lock layouts."""
    path = get_presets_dir() / "hyprlock" / "layouts.lua"
    if not path.is_file():
        return []
    data = load_lua_file(path)
    return list(data.get("layouts", []))


def list_plugin_presets() -> list[dict[str, Any]]:
    """Return available official Hyprland plugin presets from `presets/hyprplugins/presets.lua`."""
    path = get_presets_dir() / "hyprplugins" / "presets.lua"
    if not path.is_file():
        return []
    data = load_lua_file(path)
    return list(data.get("presets", []))


def get_plugin_preset(preset_id: str) -> dict[str, Any] | None:
    """Retrieve a Hyprland plugin preset blueprint by ID."""
    for item in list_plugin_presets():
        if item.get("id") == preset_id:
            return item
    return None


_BOOL_WINDOW_RULES = {
    "float",
    "tile",
    "fullscreen",
    "maximize",
    "pseudo",
    "pin",
    "center",
    "nofocus",
    "no_focus",
    "noborder",
    "no_border",
    "noshadow",
    "no_shadow",
    "noblur",
    "no_blur",
    "noanim",
    "no_anim",
    "opaque",
    "stayfocused",
}


def _lua_str(val: str) -> str:
    """Format a Python string as a safely escaped Lua double-quoted string literal."""
    escaped = (
        str(val)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )
    return f'"{escaped}"'


def _lua_val(val: Any) -> str:
    """Format a Python scalar (bool, int, float, str) as a Lua literal."""
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (int, float)):
        return str(val)
    return _lua_str(str(val))


def normalize_keybind_action(action: str, arg: str = "") -> tuple[str, str]:
    """Normalize legacy or plugin-dependent Hyprland dispatchers to Hyprland 0.56+ built-ins."""
    act = (action or "exec").strip()
    argument = (arg or "").strip()
    if act == "togglesplit":
        return "layoutmsg", argument or "togglesplit"
    if act == "hyprexpo:expo":
        return "workspace", "e+1"
    return act, argument


def format_lua_dispatcher(action: str, arg: str = "") -> str:
    """Convert a DETech keybind `(action, arg)` into a Hyprland 0.56/0.57+ `hl.dsp.*` expression."""
    act, argument = normalize_keybind_action(action, arg)
    if act.startswith("hl.dsp."):
        return act

    dir_map = {
        "l": "left",
        "r": "right",
        "u": "up",
        "d": "down",
        "left": "left",
        "right": "right",
        "up": "up",
        "down": "down",
    }

    if act == "exec":
        return f"hl.dsp.exec_cmd({_lua_str(argument)})"
    if act in ("execr", "exec_raw"):
        return f"hl.dsp.exec_raw({_lua_str(argument)})"
    if act in ("killactive", "closewindow"):
        return "hl.dsp.window.close()"
    if act in ("forcekillactive", "killwindow"):
        return "hl.dsp.window.kill()"
    if act == "exit":
        return "hl.dsp.exit()"
    if act == "togglefloating":
        return 'hl.dsp.window.float({ action = "toggle" })'
    if act == "setfloating":
        return 'hl.dsp.window.float({ action = "set" })'
    if act == "settiled":
        return 'hl.dsp.window.float({ action = "unset" })'
    if act == "fullscreen":
        mode = "maximized" if argument in ("1", "maximized") else "fullscreen"
        return f'hl.dsp.window.fullscreen({{ mode = "{mode}", action = "toggle" }})'
    if act == "pseudo":
        return "hl.dsp.window.pseudo()"
    if act == "pin":
        return 'hl.dsp.window.pin({ action = "toggle" })'
    if act in ("centerwindow", "center"):
        return "hl.dsp.window.center()"
    if act in ("layoutmsg", "layout"):
        return f"hl.dsp.layout({_lua_str(argument or 'togglesplit')})"
    if act == "movefocus":
        direction = dir_map.get(argument.lower(), "left")
        return f"hl.dsp.focus({{ direction = {_lua_str(direction)} }})"
    if act == "workspace":
        ws_val = str(int(argument)) if argument.isdigit() else _lua_str(argument or "1")
        return f"hl.dsp.focus({{ workspace = {ws_val} }})"
    if act == "movetoworkspace":
        ws_val = str(int(argument)) if argument.isdigit() else _lua_str(argument or "1")
        return f"hl.dsp.window.move({{ workspace = {ws_val} }})"
    if act == "movetoworkspacesilent":
        ws_val = str(int(argument)) if argument.isdigit() else _lua_str(argument or "1")
        return f"hl.dsp.window.move({{ workspace = {ws_val}, follow = false }})"
    if act == "movewindow":
        direction = dir_map.get(argument.lower(), "left")
        return f"hl.dsp.window.move({{ direction = {_lua_str(direction)} }})"
    if act == "swapwindow":
        direction = dir_map.get(argument.lower(), "left")
        return f"hl.dsp.window.swap({{ direction = {_lua_str(direction)} }})"
    if act == "togglespecialworkspace":
        return f"hl.dsp.workspace.toggle_special({_lua_str(argument or 'magic')})"
    if act == "dpms":
        dpms_act = argument.lower() if argument.lower() in ("on", "off", "toggle") else "toggle"
        return f"hl.dsp.dpms({{ action = {_lua_str(dpms_act)} }})"
    if act == "submap":
        return f"hl.dsp.submap({_lua_str(argument)})"

    cmd_fallback = f"{act} {argument}".strip()
    return f"hl.dsp.exec_cmd({_lua_str(cmd_fallback)})"


def parse_window_rule_to_lua(rule: str, match: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Parse a window rule and match selector into `(match_dict, effect_dict)` for `hl.window_rule`."""
    r_str, m_str = normalize_window_rule(rule, match)
    match_dict: dict[str, Any] = {}
    effect_dict: dict[str, Any] = {}
    if not r_str or not m_str:
        return match_dict, effect_dict

    m_body = m_str[len("match:") :].strip() if m_str.startswith("match:") else m_str
    if " " in m_body:
        m_prop, m_val = m_body.split(" ", 1)
    else:
        m_prop, m_val = "class", m_body
    m_val = m_val.strip()
    if m_val.lower() in ("true", "on", "yes"):
        match_dict[m_prop.strip()] = True
    elif m_val.lower() in ("false", "off", "no"):
        match_dict[m_prop.strip()] = False
    else:
        match_dict[m_prop.strip()] = m_val

    if " " in r_str:
        e_key, e_val = r_str.split(" ", 1)
    else:
        e_key, e_val = r_str, "on"

    key_map = {
        "nofocus": "no_focus",
        "noborder": "no_border",
        "noshadow": "no_shadow",
        "noblur": "no_blur",
        "noanim": "no_anim",
        "stayfocused": "stay_focused",
    }
    e_key_norm = key_map.get(e_key.strip(), e_key.strip())
    e_val_clean = e_val.strip()
    if e_val_clean.lower() in ("on", "true", "yes"):
        effect_dict[e_key_norm] = True
    elif e_val_clean.lower() in ("off", "false", "no"):
        effect_dict[e_key_norm] = False
    elif e_val_clean.isdigit():
        effect_dict[e_key_norm] = int(e_val_clean)
    else:
        effect_dict[e_key_norm] = e_val_clean

    return match_dict, effect_dict


def parse_layer_rule_to_lua(rule: str, target: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Parse a layer rule and target into `(match_dict, effect_dict)` for `hl.layer_rule`."""
    r_str, t_str = normalize_layer_rule(rule, target)
    match_dict: dict[str, Any] = {}
    effect_dict: dict[str, Any] = {}
    if not r_str or not t_str:
        return match_dict, effect_dict

    t_body = t_str[len("match:") :].strip() if t_str.startswith("match:") else f"namespace {t_str}"
    if " " in t_body:
        t_prop, t_val = t_body.split(" ", 1)
    else:
        t_prop, t_val = "namespace", t_body
    match_dict[t_prop.strip()] = t_val.strip()

    if " " in r_str:
        e_key, e_val = r_str.split(" ", 1)
    else:
        e_key, e_val = r_str, "on"

    e_key_norm = e_key.strip()
    e_val_clean = e_val.strip()
    if e_val_clean.lower() in ("on", "true", "yes"):
        effect_dict[e_key_norm] = True
    elif e_val_clean.lower() in ("off", "false", "no"):
        effect_dict[e_key_norm] = False
    else:
        try:
            effect_dict[e_key_norm] = int(e_val_clean) if e_val_clean.isdigit() else float(e_val_clean)
        except ValueError:
            effect_dict[e_key_norm] = e_val_clean

    return match_dict, effect_dict


def normalize_window_rule(rule: str, match: str) -> tuple[str, str]:
    """Normalize window rule effect and match selector to Hyprland 0.53+ `windowrule` syntax."""
    r = (rule or "").strip()
    if r in _BOOL_WINDOW_RULES:
        r = f"{r} on"

    m = (match or "").strip()
    if m and not m.startswith("match:"):
        if ":" in m:
            prop, val = m.split(":", 1)
            prop_map = {
                "initialClass": "initial_class",
                "initialTitle": "initial_title",
            }
            prop_norm = prop_map.get(prop.strip(), prop.strip())
            m = f"match:{prop_norm} {val.strip()}"
        else:
            m = f"match:class {m}"
    elif m.startswith("match:"):
        rest = m[len("match:") :]
        if ":" in rest and (" " not in rest or rest.index(":") < rest.index(" ")):
            prop, val = rest.split(":", 1)
            m = f"match:{prop.strip()} {val.strip()}"

    return r, m


def normalize_layer_rule(rule: str, target: str) -> tuple[str, str]:
    """Normalize layer rule effect and target to Hyprland 0.53+ `layerrule` syntax."""
    r = (rule or "").strip()
    rule_map = {
        "blur": "blur on",
        "ignorezero": "ignore_alpha 0",
        "noanim": "no_anim on",
        "no_anim": "no_anim on",
        "xray": "xray on",
        "dimaround": "dim_around on",
        "dim_around": "dim_around on",
    }
    r = rule_map.get(r, r)
    if r.startswith("ignorealpha "):
        r = "ignore_alpha " + r.split(" ", 1)[1].strip()

    t = (target or "").strip()
    if t and not t.startswith("match:"):
        t = f"match:namespace {t}"
    elif t.startswith("match:namespace:"):
        t = "match:namespace " + t[len("match:namespace:") :].strip()

    return r, t


def generate_hypr_configs(
    context: dict[str, Any],
    palette: dict[str, str],
    fonts: dict[str, Any],
    config_root: Path,
) -> list[Path]:
    """Generate all Hypr ecosystem configs under `<config_root>/hypr/`."""
    hypr_dir = config_root / "hypr"
    hypr_dir.mkdir(parents=True, exist_ok=True)

    cfg = context.get("config", {})
    appearance = cfg.get("appearance", {})
    inp = cfg.get("input", {})
    autostart = cfg.get("autostart", [])
    keybinds_data = context.get("keybinds", {})
    monitors_data = context.get("monitors", {})
    rules_data = context.get("rules", {})
    plugins_data = context.get("plugins", {})
    freebsd_data = context.get("freebsd", {})

    written: list[Path] = []
    home_dir = str(Path.home())
    bsd_path_env = (
        f"{home_dir}/.local/bin:{home_dir}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    )

    bg_primary_rgba = hex_to_hypr_rgba(palette["bg_primary"])
    bg_secondary_rgba = hex_to_hypr_rgba(palette["bg_secondary"])
    fg_primary_rgba = hex_to_hypr_rgba(palette["fg_primary"])
    accent_rgba = hex_to_hypr_rgba(palette["accent"])
    accent_alt_rgba = hex_to_hypr_rgba(palette["accent_alt"])
    urgent_rgba = hex_to_hypr_rgba(palette["urgent"])
    border_active_1 = hex_to_hypr_rgba(palette["border_active"])
    border_active_2 = hex_to_hypr_rgba(palette["accent_alt"])
    border_inactive_rgba = hex_to_hypr_rgba(palette["border_inactive"], "aa")

    # 1a. detech-colors.lua (Hyprland 0.56/0.57+ Native Lua Config)
    colors_lua = hypr_dir / "detech-colors.lua"
    colors_lua_lines = [
        "-- Generated by DETech — Do not edit directly (edit configs/lua/ instead)",
        "return {",
        f"    bg_primary = {_lua_str(bg_primary_rgba)},",
        f"    bg_secondary = {_lua_str(bg_secondary_rgba)},",
        f"    fg_primary = {_lua_str(fg_primary_rgba)},",
        f"    accent = {_lua_str(accent_rgba)},",
        f"    accent_alt = {_lua_str(accent_alt_rgba)},",
        f"    urgent = {_lua_str(urgent_rgba)},",
        "    border_active = {",
        f"        colors = {{ {_lua_str(border_active_1)}, {_lua_str(border_active_2)} }},",
        "        angle = 45,",
        "    },",
        f"    border_inactive = {_lua_str(border_inactive_rgba)},",
        "}",
    ]
    colors_lua.write_text("\n".join(colors_lua_lines) + "\n", encoding="utf-8")
    written.append(colors_lua)

    # 1b. detech-colors.conf (Legacy fallback)
    colors_conf = hypr_dir / "detech-colors.conf"
    colors_lines = [
        "# Generated by DETech — Do not edit directly (edit configs/lua/ instead)",
        f"$bg_primary = {bg_primary_rgba}",
        f"$bg_secondary = {bg_secondary_rgba}",
        f"$fg_primary = {fg_primary_rgba}",
        f"$accent = {accent_rgba}",
        f"$accent_alt = {accent_alt_rgba}",
        f"$urgent = {urgent_rgba}",
        f"$border_active = {border_active_1} {border_active_2} 45deg",
        f"$border_inactive = {border_inactive_rgba}",
    ]
    colors_conf.write_text("\n".join(colors_lines) + "\n", encoding="utf-8")
    written.append(colors_conf)

    # 2a. detech-keybinds.lua (Hyprland 0.56/0.57+ Native Lua Config)
    main_mod = str(keybinds_data.get("main_mod", "SUPER"))
    binds_lua = hypr_dir / "detech-keybinds.lua"
    binds_lua_lines = [
        "-- Generated by DETech from keybinds.lua (Hyprland 0.56/0.57+ hl.bind API)",
        f"local mainMod = {_lua_str(main_mod)}",
        "",
    ]
    for bind in keybinds_data.get("binds", []):
        raw_mods = [main_mod if m == "$mainMod" else str(m) for m in bind.get("mod", []) if str(m).strip()]
        key = str(bind.get("key", "")).strip()
        combo_str = " + ".join([*raw_mods, key]) if raw_mods else key
        dsp_expr = format_lua_dispatcher(str(bind.get("action", "exec")), str(bind.get("arg", "")))
        desc = str(bind.get("desc", "")).strip()
        opts_parts: list[str] = []
        if key.startswith("XF86"):
            opts_parts.append("locked = true")
            opts_parts.append("repeating = true")
        if desc:
            opts_parts.append(f"desc = {_lua_str(desc)}")
        if opts_parts:
            binds_lua_lines.append(f"hl.bind({_lua_str(combo_str)}, {dsp_expr}, {{ {', '.join(opts_parts)} }})")
        else:
            binds_lua_lines.append(f"hl.bind({_lua_str(combo_str)}, {dsp_expr})")

    binds_lua_lines.extend(
        [
            "",
            "-- Mouse Window Drag/Resize & Workspace Scroll",
            'hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))',
            'hl.bind(mainMod .. " + mouse_up", hl.dsp.focus({ workspace = "e-1" }))',
            'hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(), { mouse = true })',
            'hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })',
        ]
    )
    binds_lua.write_text("\n".join(binds_lua_lines) + "\n", encoding="utf-8")
    written.append(binds_lua)

    # 2b. detech-keybinds.conf (Legacy fallback)
    binds_conf = hypr_dir / "detech-keybinds.conf"
    binds_lines = [
        "# Generated by DETech from keybinds.lua",
        f"$mainMod = {main_mod}",
        "",
    ]
    for bind in keybinds_data.get("binds", []):
        mods = " ".join(bind.get("mod", []))
        key = bind.get("key", "")
        action, arg = normalize_keybind_action(bind.get("action", "exec"), bind.get("arg", ""))
        desc = bind.get("desc", "")
        if arg:
            binds_lines.append(f"bind = {mods}, {key}, {action}, {arg} # {desc}")
        else:
            binds_lines.append(f"bind = {mods}, {key}, {action} # {desc}")
    binds_lines.extend(
        [
            "bind = $mainMod, mouse_down, workspace, e+1",
            "bind = $mainMod, mouse_up, workspace, e-1",
            "bindm = $mainMod, mouse:272, movewindow",
            "bindm = $mainMod, mouse:273, resizewindow",
        ]
    )
    binds_conf.write_text("\n".join(binds_lines) + "\n", encoding="utf-8")
    written.append(binds_conf)

    # 3a. detech-plugins.lua & 3b. detech-plugins.conf (Official Hyprland plugins)
    plugins_lua = hypr_dir / "detech-plugins.lua"
    plugins_conf = hypr_dir / "detech-plugins.conf"
    preset_id = plugins_data.get("preset", "minimal-expo")
    preset_spec = get_plugin_preset(preset_id)
    enabled_plugins = dict(plugins_data.get("enabled_plugins", {}))
    if preset_spec and isinstance(preset_spec.get("enabled_plugins"), dict):
        enabled_plugins.update(preset_spec["enabled_plugins"])

    plug_lua_lines = [
        f"-- Generated by DETech from plugins.lua (Preset: {preset_id})",
    ]
    plug_lines = [
        f"# Generated by DETech from plugins.lua (Preset: {preset_id})",
    ]
    if plugins_data.get("auto_reload_hyprpm", False):
        plug_lua_lines.extend(
            [
                'hl.on("hyprland.start", function()',
                '    hl.exec_cmd("[ -d /var/cache/hyprpm ] && hyprpm reload -n")',
                "end)",
            ]
        )
        plug_lines.append("exec-once = [ -d /var/cache/hyprpm ] && hyprpm reload -n")

    he_cfg = plugins_data.get("hyprexpo", {})
    if enabled_plugins.get("hyprexpo", True) and he_cfg.get("enable_gesture", True):
        plug_lua_lines.extend(
            [
                "hl.gesture({",
                "    fingers = 3,",
                '    direction = "horizontal",',
                '    action = "workspace",',
                "})",
            ]
        )
        plug_lines.append("gesture = 3, horizontal, workspace")

    plug_lines.append("")
    plug_lines.append("plugin {")

    if enabled_plugins.get("hyprbars", False):
        hb = plugins_data.get("hyprbars", {})
        bar_col = hex_to_hypr_rgba(palette["bg_secondary"], "ee")
        plug_lua_lines.extend(
            [
                'if hl.get_config("plugin.hyprbars.bar_height") ~= nil then',
                "    hl.config({",
                "        plugin = {",
                "            hyprbars = {",
                f"                bar_height = {hb.get('bar_height', 28)},",
                f"                bar_color = {_lua_str(bar_col)},",
                f"                ['col.text'] = {_lua_str(fg_primary_rgba)},",
                f"                bar_text_size = {hb.get('bar_text_size', 10)},",
                f"                bar_text_font = {_lua_str(fonts['sans'])},",
                f"                bar_part_of_window = {'true' if hb.get('bar_part_of_window', True) else 'false'},",
                f"                bar_precedence_over_border = {'true' if hb.get('bar_precedence_over_border', True) else 'false'},",
                "            },",
                "        },",
                "    })",
                "end",
            ]
        )
        plug_lines.extend(
            [
                "    hyprbars {",
                f"        bar_height = {hb.get('bar_height', 28)}",
                f"        bar_color = {bar_col}",
                f"        col.text = {fg_primary_rgba}",
                f"        bar_text_size = {hb.get('bar_text_size', 10)}",
                f"        bar_text_font = {fonts['sans']}",
                f"        bar_part_of_window = {'true' if hb.get('bar_part_of_window', True) else 'false'}",
                f"        bar_precedence_over_border = {'true' if hb.get('bar_precedence_over_border', True) else 'false'}",
            ]
        )
        for btn in hb.get("buttons", []):
            col_key = btn.get("col", "accent")
            col_hex = palette.get(col_key, palette["accent"])
            plug_lines.append(
                f"        hyprbars-button = {hex_to_hypr_rgba(col_hex)}, {btn.get('button_size', 12)}, , {btn.get('cmd', '')}"
            )
        plug_lines.append("    }")

    if enabled_plugins.get("hyprexpo", True):
        he = plugins_data.get("hyprexpo", {})
        plug_lua_lines.extend(
            [
                'if hl.get_config("plugin.hyprexpo.columns") ~= nil then',
                "    hl.config({",
                "        plugin = {",
                "            hyprexpo = {",
                f"                columns = {he.get('columns', 3)},",
                f"                gap_size = {he.get('gap_size', 6)},",
                f"                bg_col = {_lua_str(bg_primary_rgba)},",
                f"                workspace_method = {_lua_str(he.get('workspace_method', 'center current'))},",
                "            },",
                "        },",
                "    })",
                "end",
            ]
        )
        plug_lines.extend(
            [
                "    hyprexpo {",
                f"        columns = {he.get('columns', 3)}",
                f"        gap_size = {he.get('gap_size', 6)}",
                f"        bg_col = {bg_primary_rgba}",
                f"        workspace_method = {he.get('workspace_method', 'center current')}",
                "    }",
            ]
        )

    if enabled_plugins.get("hyprtrails", False):
        trail_col = hex_to_hypr_rgba(palette["accent"], "aa")
        plug_lua_lines.extend(
            [
                'if hl.get_config("plugin.hyprtrails.color") ~= nil then',
                "    hl.config({",
                "        plugin = {",
                "            hyprtrails = {",
                f"                color = {_lua_str(trail_col)},",
                "            },",
                "        },",
                "    })",
                "end",
            ]
        )
        plug_lines.extend(
            [
                "    hyprtrails {",
                f"        color = {trail_col}",
                "    }",
            ]
        )

    if enabled_plugins.get("hyprwinwrap", False):
        hw = plugins_data.get("hyprwinwrap", {})
        hw_class = hw.get("class", "detech-bg-widget")
        plug_lua_lines.extend(
            [
                'if hl.get_config("plugin.hyprwinwrap.class") ~= nil then',
                "    hl.config({",
                "        plugin = {",
                "            hyprwinwrap = {",
                f"                class = {_lua_str(hw_class)},",
                "            },",
                "        },",
                "    })",
                "end",
            ]
        )
        plug_lines.extend(
            [
                "    hyprwinwrap {",
                f"        class = {hw_class}",
                "    }",
            ]
        )

    if enabled_plugins.get("csgo_vulkan_fix", False):
        cvf = plugins_data.get("csgo_vulkan_fix", {})
        plug_lua_lines.extend(
            [
                'if hl.get_config("plugin.csgo-vulkan-fix.res_w") ~= nil then',
                "    hl.config({",
                "        plugin = {",
                "            ['csgo-vulkan-fix'] = {",
                f"                res_w = {cvf.get('res_w', 1920)},",
                f"                res_h = {cvf.get('res_h', 1080)},",
                f"                class = {_lua_str(cvf.get('class', 'cs2'))},",
                f"                fix_mouse = {'true' if cvf.get('fix_mouse', True) else 'false'},",
                "            },",
                "        },",
                "    })",
                "end",
            ]
        )
        plug_lines.extend(
            [
                "    csgo-vulkan-fix {",
                f"        res_w = {cvf.get('res_w', 1920)}",
                f"        res_h = {cvf.get('res_h', 1080)}",
                f"        class = {cvf.get('class', 'cs2')}",
                f"        fix_mouse = {'true' if cvf.get('fix_mouse', True) else 'false'}",
                "    }",
            ]
        )

    if enabled_plugins.get("borders_plus_plus", False):
        bpp = plugins_data.get("borders_plus_plus", {})
        col1_key = bpp.get("col_border_1", "border_inactive")
        col1_hex = palette.get(col1_key, palette["border_inactive"])
        col1_rgba = hex_to_hypr_rgba(col1_hex)
        plug_lua_lines.extend(
            [
                'if hl.get_config("plugin.borders-plus-plus.add_borders") ~= nil then',
                "    hl.config({",
                "        plugin = {",
                "            ['borders-plus-plus'] = {",
                f"                add_borders = {bpp.get('add_borders', 1)},",
                f"                ['col.border_1'] = {_lua_str(col1_rgba)},",
                f"                natural_rounding = {'true' if bpp.get('natural_rounding', True) else 'false'},",
                "            },",
                "        },",
                "    })",
                "end",
            ]
        )
        plug_lines.extend(
            [
                "    borders-plus-plus {",
                f"        add_borders = {bpp.get('add_borders', 1)}",
                f"        col.border_1 = {col1_rgba}",
                f"        natural_rounding = {'yes' if bpp.get('natural_rounding', True) else 'no'}",
                "    }",
            ]
        )

    plug_lines.append("}")
    plugins_lua.write_text("\n".join(plug_lua_lines) + "\n", encoding="utf-8")
    written.append(plugins_lua)
    plugins_conf.write_text("\n".join(plug_lines) + "\n", encoding="utf-8")
    written.append(plugins_conf)

    # 4a. Main hyprland.lua (Hyprland 0.56/0.57+ Native Lua Config)
    hyprland_lua = hypr_dir / "hyprland.lua"
    blur = appearance.get("blur", {})
    blur_enabled = "true" if blur.get("enabled", True) else "false"
    anim_mode = appearance.get("animations", "snappy")
    anim_enabled = "false" if anim_mode == "disabled" else "true"
    cursor_theme = str(appearance.get("cursor_theme", "Bibata-Modern-Ice"))
    cursor_size = str(appearance.get("cursor_size", 24))

    hl_lua_lines = [
        "-- DETech Compiled Hyprland Lua Configuration for FreeBSD (Hyprland 0.56/0.57+)",
        'local colors = require("detech-colors")',
        "",
        "-- FreeBSD & Wayland Environment Variables",
        f'hl.env("PATH", {_lua_str(bsd_path_env)})',
        'hl.env("XDG_CURRENT_DESKTOP", "Hyprland")',
        'hl.env("XDG_SESSION_TYPE", "wayland")',
        'hl.env("XDG_SESSION_DESKTOP", "Hyprland")',
        'hl.env("QT_QPA_PLATFORM", "wayland;xcb")',
        'hl.env("QT_QPA_PLATFORMTHEME", "qt6ct")',
        f'hl.env("XCURSOR_THEME", {_lua_str(cursor_theme)})',
        f'hl.env("XCURSOR_SIZE", {_lua_str(cursor_size)})',
        f'hl.env("HYPRCURSOR_SIZE", {_lua_str(cursor_size)})',
        "",
        "-- Monitors",
    ]
    for mon in monitors_data.get("monitors", [{"name": "", "resolution": "preferred", "position": "auto", "scale": "1"}]):
        m_name = str(mon.get("name", ""))
        m_res = str(mon.get("resolution", "preferred"))
        m_pos = str(mon.get("position", "auto"))
        m_scale = str(mon.get("scale", "1"))
        hl_lua_lines.extend(
            [
                "hl.monitor({",
                f"    output = {_lua_str(m_name)},",
                f"    mode = {_lua_str(m_res)},",
                f"    position = {_lua_str(m_pos)},",
                f"    scale = {_lua_str(m_scale)},",
                "})",
            ]
        )

    hl_lua_lines.extend(
        [
            "",
            "-- Autostart Daemons",
            'hl.on("hyprland.start", function()',
        ]
    )
    for cmd in autostart:
        hl_lua_lines.append(f"    hl.exec_cmd({_lua_str(str(cmd))})")
    hl_lua_lines.extend(
        [
            "end)",
            "",
            "-- Appearance, Input & Layout Configuration",
            "hl.config({",
            "    general = {",
            f"        gaps_in = {appearance.get('gaps_in', 6)},",
            f"        gaps_out = {appearance.get('gaps_out', 12)},",
            f"        border_size = {appearance.get('border_size', 2)},",
            "        col = {",
            "            active_border = colors.border_active,",
            "            inactive_border = colors.border_inactive,",
            "        },",
            '        layout = "dwindle",',
            "    },",
            "    decoration = {",
            f"        rounding = {appearance.get('rounding', 10)},",
            "        blur = {",
            f"            enabled = {blur_enabled},",
            f"            size = {blur.get('size', 6)},",
            f"            passes = {blur.get('passes', 3)},",
            f"            vibrancy = {blur.get('vibrancy', 0.2)},",
            "        },",
            "    },",
            "    animations = {",
            f"        enabled = {anim_enabled},",
            "    },",
            "    input = {",
            f"        kb_layout = {_lua_str(inp.get('kb_layout', 'us'))},",
            f"        kb_variant = {_lua_str(inp.get('kb_variant', ''))},",
            f"        kb_options = {_lua_str(inp.get('kb_options', 'caps:escape'))},",
            f"        follow_mouse = {inp.get('follow_mouse', 1)},",
            f"        sensitivity = {inp.get('sensitivity', 0.0)},",
            "        touchpad = {",
            f"            natural_scroll = {'true' if inp.get('touchpad_natural_scroll', True) else 'false'},",
            "        },",
            "    },",
            "    dwindle = {",
            "        preserve_split = true,",
            "    },",
            "    misc = {",
            "        disable_hyprland_logo = true,",
            "        force_default_wallpaper = 0,",
            "    },",
            "})",
            "",
            "-- Animation Curves & Leaves",
            'hl.curve("detechCurve", { type = "bezier", points = { { 0.05, 0.9 }, { 0.1, 1.05 } } })',
            f'hl.animation({{ leaf = "windows", enabled = {anim_enabled}, speed = 5, bezier = "detechCurve" }})',
            f'hl.animation({{ leaf = "windowsOut", enabled = {anim_enabled}, speed = 4, bezier = "default", style = "popin 80%" }})',
            f'hl.animation({{ leaf = "border", enabled = {anim_enabled}, speed = 8, bezier = "default" }})',
            f'hl.animation({{ leaf = "fade", enabled = {anim_enabled}, speed = 5, bezier = "default" }})',
            f'hl.animation({{ leaf = "workspaces", enabled = {anim_enabled}, speed = 5, bezier = "detechCurve", style = "slide" }})',
            "",
            "-- Window & Layer Rules",
        ]
    )

    for idx, wrule in enumerate(rules_data.get("window_rules", []), start=1):
        m_dict, e_dict = parse_window_rule_to_lua(str(wrule.get("rule", "")), str(wrule.get("match", "")))
        if m_dict and e_dict:
            m_items = ", ".join(f"{k} = {_lua_val(v)}" for k, v in m_dict.items())
            e_items = ", ".join(f"{k} = {_lua_val(v)}" for k, v in e_dict.items())
            hl_lua_lines.append(
                f'hl.window_rule({{ name = "detech-wrule-{idx}", match = {{ {m_items} }}, {e_items} }})'
            )

    for idx, lrule in enumerate(rules_data.get("layer_rules", []), start=1):
        m_dict, e_dict = parse_layer_rule_to_lua(str(lrule.get("rule", "")), str(lrule.get("target", "")))
        if m_dict and e_dict:
            m_items = ", ".join(f"{k} = {_lua_val(v)}" for k, v in m_dict.items())
            e_items = ", ".join(f"{k} = {_lua_val(v)}" for k, v in e_dict.items())
            hl_lua_lines.append(
                f'hl.layer_rule({{ name = "detech-lrule-{idx}", match = {{ {m_items} }}, {e_items} }})'
            )

    hl_lua_lines.extend(
        [
            "",
            'require("detech-keybinds")',
            'require("detech-plugins")',
        ]
    )
    hyprland_lua.write_text("\n".join(hl_lua_lines) + "\n", encoding="utf-8")
    written.append(hyprland_lua)

    # 4b. Main hyprland.conf (Legacy fallback)
    hyprland_conf = hypr_dir / "hyprland.conf"
    hl_lines = [
        "# DETech Compiled Hyprland Configuration for FreeBSD",
        "source = ~/.config/hypr/detech-colors.conf",
        "",
        "# FreeBSD & Wayland Environment Variables",
        f"env = PATH,{bsd_path_env}",
        "env = XDG_CURRENT_DESKTOP,Hyprland",
        "env = XDG_SESSION_TYPE,wayland",
        "env = XDG_SESSION_DESKTOP,Hyprland",
        "env = QT_QPA_PLATFORM,wayland;xcb",
        "env = QT_QPA_PLATFORMTHEME,qt6ct",
        f"env = XCURSOR_THEME,{cursor_theme}",
        f"env = XCURSOR_SIZE,{cursor_size}",
        "",
        "# Monitors",
    ]
    for mon in monitors_data.get("monitors", [{"name": "", "resolution": "preferred", "position": "auto", "scale": "1"}]):
        hl_lines.append(
            f"monitor = {mon.get('name', '')}, {mon.get('resolution', 'preferred')}, {mon.get('position', 'auto')}, {mon.get('scale', '1')}"
        )

    hl_lines.extend(["", "# Autostart Daemons"])
    for cmd in autostart:
        hl_lines.append(f"exec-once = {cmd}")

    hl_lines.extend(
        [
            "",
            "general {",
            f"    gaps_in = {appearance.get('gaps_in', 6)}",
            f"    gaps_out = {appearance.get('gaps_out', 12)}",
            f"    border_size = {appearance.get('border_size', 2)}",
            "    col.active_border = $border_active",
            "    col.inactive_border = $border_inactive",
            "    layout = dwindle",
            "}",
            "",
            "decoration {",
            f"    rounding = {appearance.get('rounding', 10)}",
            "    blur {",
            f"        enabled = {blur_enabled}",
            f"        size = {blur.get('size', 6)}",
            f"        passes = {blur.get('passes', 3)}",
            "    }",
            "}",
            "",
            "animations {",
            f"    enabled = {anim_enabled}",
            "    bezier = detechCurve, 0.05, 0.9, 0.1, 1.05",
            "    animation = windows, 1, 5, detechCurve",
            "    animation = windowsOut, 1, 4, default, popin 80%",
            "    animation = border, 1, 8, default",
            "    animation = fade, 1, 5, default",
            "    animation = workspaces, 1, 5, detechCurve, slide",
            "}",
            "",
            "input {",
            f"    kb_layout = {inp.get('kb_layout', 'us')}",
            f"    kb_variant = {inp.get('kb_variant', '')}",
            f"    kb_options = {inp.get('kb_options', 'caps:escape')}",
            f"    follow_mouse = {inp.get('follow_mouse', 1)}",
            "    touchpad {",
            f"        natural_scroll = {'true' if inp.get('touchpad_natural_scroll', True) else 'false'}",
            "    }",
            "}",
            "",
            "dwindle {",
            "    preserve_split = true",
            "}",
            "",
            "# Window & Layer Rules",
        ]
    )

    for wrule in rules_data.get("window_rules", []):
        r_str, m_str = normalize_window_rule(str(wrule.get("rule", "")), str(wrule.get("match", "")))
        if r_str and m_str:
            hl_lines.append(f"windowrule = {r_str}, {m_str}")
    for lrule in rules_data.get("layer_rules", []):
        r_str, t_str = normalize_layer_rule(str(lrule.get("rule", "")), str(lrule.get("target", "")))
        if r_str and t_str:
            hl_lines.append(f"layerrule = {r_str}, {t_str}")

    hl_lines.extend(
        [
            "",
            "source = ~/.config/hypr/detech-keybinds.conf",
            "source = ~/.config/hypr/detech-plugins.conf",
        ]
    )
    hyprland_conf.write_text("\n".join(hl_lines) + "\n", encoding="utf-8")
    written.append(hyprland_conf)

    # 5. hyprlock.conf
    lock_layout_id = appearance.get("hyprlock_layout", "minimal-clock")
    lock_layouts = {item["id"]: item for item in list_hyprlock_layouts()}
    lock_spec = lock_layouts.get(
        lock_layout_id,
        {
            "id": "minimal-clock",
            "blur_passes": 3,
            "blur_size": 7,
            "clock_size": fonts["lock_size"],
            "clock_pos": "0, 120",
            "input_width": 280,
            "input_height": 52,
            "input_pos": "0, -80",
            "greeting": "  Locked — $USER",
        },
    )
    wallpaper = appearance.get("wallpaper", "")
    bg_r, bg_g, bg_b = hex_to_rgb(palette["bg_secondary"])
    fg_r, fg_g, fg_b = hex_to_rgb(palette["fg_primary"])
    acc_r, acc_g, acc_b = hex_to_rgb(palette["accent"])

    hyprlock_conf = hypr_dir / "hyprlock.conf"
    lock_lines = [
        f"# DETech Hyprlock Configuration (Layout: {lock_spec['id']})",
        "background {",
        "    monitor =",
        f"    path = {wallpaper if wallpaper else 'screenshot'}",
        f"    color = rgba({bg_r}, {bg_g}, {bg_b}, 1.0)",
        f"    blur_passes = {lock_spec.get('blur_passes', 3)}",
        f"    blur_size = {lock_spec.get('blur_size', 7)}",
        "}",
        "",
        "label {",
        "    monitor =",
        '    text = cmd[update:1000] echo "$(date +\'%H:%M\')"',
        f"    color = rgba({fg_r}, {fg_g}, {fg_b}, 1.0)",
        f"    font_size = {lock_spec.get('clock_size', fonts['lock_size'])}",
        f"    font_family = {fonts['mono']}",
        f"    position = {lock_spec.get('clock_pos', '0, 120')}",
        "    halign = center",
        "    valign = center",
        "}",
        "",
        "label {",
        "    monitor =",
        f"    text = {lock_spec.get('greeting', '  Locked — $USER')}",
        f"    color = rgba({acc_r}, {acc_g}, {acc_b}, 1.0)",
        f"    font_size = {fonts['size'] + 3}",
        f"    font_family = {fonts['sans']}",
        "    position = 0, -20",
        "    halign = center",
        "    valign = center",
        "}",
        "",
        "input-field {",
        "    monitor =",
        f"    size = {lock_spec.get('input_width', 280)}, {lock_spec.get('input_height', 52)}",
        "    outline_thickness = 2",
        f"    outer_color = rgba({acc_r}, {acc_g}, {acc_b}, 1.0)",
        f"    inner_color = rgba({bg_r}, {bg_g}, {bg_b}, 0.85)",
        f"    font_color = rgba({fg_r}, {fg_g}, {fg_b}, 1.0)",
        f"    font_family = {fonts['mono']}",
        "    fade_on_empty = false",
        "    placeholder_text = <i>Password...</i>",
        f"    position = {lock_spec.get('input_pos', '0, -80')}",
        "    halign = center",
        "    valign = center",
        "}",
    ]
    hyprlock_conf.write_text("\n".join(lock_lines) + "\n", encoding="utf-8")
    written.append(hyprlock_conf)

    # 6. hypridle.conf (FreeBSD acpiconf & Hyprland 0.56/0.57+ Lua/Legacy compatible)
    power_cfg = freebsd_data.get("power", {})
    suspend_cmd = power_cfg.get("suspend_cmd", "doas acpiconf -s 3")
    hypridle_conf = hypr_dir / "hypridle.conf"
    dpms_on_cmd = "hyprctl dispatch 'hl.dsp.dpms({ action = \"on\" })' >/dev/null 2>&1; hyprctl dispatch dpms on >/dev/null 2>&1"
    dpms_off_cmd = "hyprctl dispatch 'hl.dsp.dpms({ action = \"off\" })' >/dev/null 2>&1; hyprctl dispatch dpms off >/dev/null 2>&1"
    idle_lines = [
        "# DETech Hypridle Configuration for FreeBSD",
        "general {",
        "    lock_cmd = pidof hyprlock || hyprlock",
        "    before_sleep_cmd = pidof hyprlock || hyprlock",
        f"    after_sleep_cmd = {dpms_on_cmd}",
        "}",
        "",
        "listener {",
        f"    timeout = {power_cfg.get('idle_lock_timeout', 300)}",
        "    on-timeout = pidof hyprlock || hyprlock",
        "}",
        "",
        "listener {",
        f"    timeout = {power_cfg.get('idle_dpms_timeout', 420)}",
        f"    on-timeout = {dpms_off_cmd}",
        f"    on-resume = {dpms_on_cmd}",
        "}",
        "",
        "listener {",
        f"    timeout = {power_cfg.get('idle_suspend_timeout', 900)}",
        f"    on-timeout = {suspend_cmd}",
        "}",
    ]
    hypridle_conf.write_text("\n".join(idle_lines) + "\n", encoding="utf-8")
    written.append(hypridle_conf)

    # 7. hyprpaper.conf
    hyprpaper_conf = hypr_dir / "hyprpaper.conf"
    paper_wallpaper = wallpaper
    if not paper_wallpaper:
        default_bsd_wall = Path("/usr/local/share/hypr/wall0.png")
        if default_bsd_wall.is_file():
            paper_wallpaper = str(default_bsd_wall)

    paper_lines = [
        "# DETech Hyprpaper Configuration",
        "ipc = true",
        "splash = false",
    ]
    if paper_wallpaper:
        paper_lines.extend(
            [
                "",
                "wallpaper {",
                "    monitor = ",
                f"    path = {paper_wallpaper}",
                "    fit_mode = cover",
                "}",
            ]
        )
    hyprpaper_conf.write_text("\n".join(paper_lines) + "\n", encoding="utf-8")
    written.append(hyprpaper_conf)

    return written
