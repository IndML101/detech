"""GTK-2/3/4, Qt5ct/Qt6ct, Kvantum Asset Bundle, and Dunst Notification Daemon Generator."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def render_kvantum_kvconfig(palette: dict[str, str], theme_name: str = "DETech") -> str:
    """Render a complete Kvantum `.kvconfig` theme file synced with the active DETech palette."""
    lines = [
        f"# DETech Dynamic Kvantum Theme ({theme_name})",
        "[%General]",
        "author=DETech Engine",
        "comment=Dynamic FreeBSD Hyprland Kvantum Theme",
        "x11drag=all",
        "alt_mnemonic=true",
        "left_tabs=true",
        "mirror_doc_tabs=true",
        "group_toolbar_buttons=false",
        "toolbar_item_spacing=2",
        "toolbar_interior_spacing=4",
        "spread_progressbar=true",
        "composite=true",
        "menu_shadow_depth=6",
        "tooltip_shadow_depth=4",
        "splitter_width=4",
        "scroll_width=10",
        "scroll_arrows=false",
        "slider_width=4",
        "slider_handle_width=16",
        "slider_handle_length=16",
        "check_size=16",
        "textless_progressbar=false",
        "progressbar_thickness=6",
        "",
        "[GeneralColors]",
        f"window.color={palette['bg_primary']}",
        f"base.color={palette['bg_secondary']}",
        f"alt.base.color={palette['bg_tertiary']}",
        f"button.color={palette['bg_secondary']}",
        f"light.color={palette['bg_tertiary']}",
        f"mid.light.color={palette['bg_secondary']}",
        f"dark.color={palette['bg_primary']}",
        f"mid.color={palette['border_inactive']}",
        f"shadow.color=#000000",
        f"highlight.color={palette['accent']}",
        f"inactive.highlight.color={palette['bg_tertiary']}",
        f"text.color={palette['fg_primary']}",
        f"window.text.color={palette['fg_primary']}",
        f"button.text.color={palette['fg_primary']}",
        f"disabled.text.color={palette['fg_muted']}",
        f"tooltip.text.color={palette['fg_primary']}",
        f"highlight.text.color={palette['bg_primary']}",
        f"link.color={palette['accent']}",
        f"link.visited.color={palette['accent_alt']}",
        f"progress.indicator.text.color={palette['bg_primary']}",
        "",
        "[Hacks]",
        "transparent_dolphin_view=true",
        "transparent_pcmanfm_sidepane=true",
        "blur_translucent=true",
        "transparent_ktitle_label=true",
        "transparent_menutitle=true",
        "respect_darkness=true",
        "kcapacitybar_as_progressbar=true",
        "",
        "[Window]",
        "inherits=General",
        "interior.element=Window",
        "frame.element=Window",
        "translucent=true",
        "",
        "[PanelButtonCommand]",
        "frame=true",
        "frame.element=PanelButtonCommand",
        "interior=true",
        "interior.element=PanelButtonCommand",
        f"text.normal.color={palette['fg_primary']}",
        f"text.focus.color={palette['accent']}",
        f"text.press.color={palette['bg_primary']}",
        f"text.toggle.color={palette['bg_primary']}",
        "frame.top=4",
        "frame.bottom=4",
        "frame.left=6",
        "frame.right=6",
        "",
        "[Toolbar]",
        "inherits=PanelButtonCommand",
        "interior.element=Toolbar",
        "frame.element=Toolbar",
        f"text.normal.color={palette['fg_primary']}",
        "",
        "[MenuItem]",
        "inherits=PanelButtonCommand",
        "frame.element=MenuItem",
        "interior.element=MenuItem",
        f"text.normal.color={palette['fg_primary']}",
        f"text.focus.color={palette['bg_primary']}",
        "",
        "[Tab]",
        "inherits=PanelButtonCommand",
        "interior.element=Tab",
        "frame.element=Tab",
        f"text.normal.color={palette['fg_secondary']}",
        f"text.focus.color={palette['fg_primary']}",
        f"text.toggle.color={palette['accent']}",
        "",
        "[Header]",
        "inherits=PanelButtonCommand",
        "interior.element=Header",
        "frame.element=Header",
        "",
        "[LineEdit]",
        "inherits=PanelButtonCommand",
        "frame.element=LineEdit",
        "interior.element=LineEdit",
        "",
        "[Tooltip]",
        "frame=true",
        "interior=true",
        "frame.element=Tooltip",
        "interior.element=Tooltip",
        f"text.normal.color={palette['fg_primary']}",
    ]
    return "\n".join(lines) + "\n"


def render_kvantum_svg(palette: dict[str, str]) -> str:
    """Render a vector SVG skin for the DETech Kvantum theme bundle."""
    bg1 = palette["bg_primary"]
    bg2 = palette["bg_secondary"]
    bg3 = palette["bg_tertiary"]
    acc = palette["accent"]
    acc_alt = palette["accent_alt"]
    bdr = palette["border_inactive"]

    return f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="240" height="160" viewBox="0 0 240 160">
  <defs>
    <linearGradient id="detechAccent" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{acc}" />
      <stop offset="100%" stop-color="{acc_alt}" />
    </linearGradient>
  </defs>
  <g id="Window">
    <rect x="0" y="0" width="48" height="48" rx="8" fill="{bg1}" stroke="{bdr}" stroke-width="1"/>
  </g>
  <g id="Toolbar">
    <rect x="52" y="0" width="48" height="32" fill="{bg2}" stroke="{bdr}" stroke-width="1"/>
  </g>
  <g id="PanelButtonCommand-normal">
    <rect x="0" y="54" width="44" height="28" rx="6" fill="{bg2}" stroke="{bdr}" stroke-width="1"/>
  </g>
  <g id="PanelButtonCommand-focus">
    <rect x="48" y="54" width="44" height="28" rx="6" fill="{bg3}" stroke="{acc}" stroke-width="1.5"/>
  </g>
  <g id="PanelButtonCommand-pressed">
    <rect x="96" y="54" width="44" height="28" rx="6" fill="url(#detechAccent)" stroke="{acc}" stroke-width="1"/>
  </g>
  <g id="PanelButtonCommand-toggled">
    <rect x="144" y="54" width="44" height="28" rx="6" fill="{acc}" stroke="{acc_alt}" stroke-width="1"/>
  </g>
  <g id="MenuItem-focus">
    <rect x="0" y="88" width="44" height="24" rx="5" fill="{acc}"/>
  </g>
  <g id="Tab-normal">
    <rect x="48" y="88" width="44" height="24" rx="6" fill="{bg2}"/>
  </g>
  <g id="Tab-toggled">
    <rect x="96" y="88" width="44" height="24" rx="6" fill="{bg3}" stroke="{acc}" stroke-width="1.5"/>
  </g>
  <g id="Header-normal">
    <rect x="144" y="88" width="44" height="24" fill="{bg2}" stroke="{bdr}" stroke-width="1"/>
  </g>
  <g id="LineEdit-normal">
    <rect x="0" y="120" width="60" height="26" rx="6" fill="{bg2}" stroke="{bdr}" stroke-width="1"/>
  </g>
  <g id="LineEdit-focus">
    <rect x="64" y="120" width="60" height="26" rx="6" fill="{bg1}" stroke="{acc}" stroke-width="1.5"/>
  </g>
  <g id="Tooltip">
    <rect x="130" y="120" width="60" height="26" rx="6" fill="{bg2}" stroke="{acc}" stroke-width="1"/>
  </g>
</svg>
"""


def generate_gtk_qt_dunst_configs(
    context: dict[str, Any],
    theme_data: dict[str, Any],
    palette: dict[str, str],
    fonts: dict[str, Any],
    config_root: Path,
) -> list[Path]:
    """Generate GTK-2/3/4, Qt5ct/Qt6ct, Kvantum asset bundle, and Dunst configs."""
    written: list[Path] = []
    appearance = context.get("config", {}).get("appearance", {})

    gtk_theme = theme_data.get("gtk_theme", "Adwaita-dark")
    icon_theme = appearance.get("icon_theme") or theme_data.get("icon_theme", "Papirus-Dark")
    cursor_theme = appearance.get("cursor_theme") or theme_data.get("cursor_theme", "Bibata-Modern-Ice")
    cursor_size = appearance.get("cursor_size", 24)
    kvantum_theme = theme_data.get("kvantum_theme", "DETech")
    font_str = f"{fonts['sans']} {fonts['size']}"

    # 1. GTK-2.0 gtkrc
    gtk2_dir = config_root / "gtk-2.0"
    gtk2_dir.mkdir(parents=True, exist_ok=True)
    gtk2_rc = gtk2_dir / "gtkrc"
    gtk2_rc.write_text(
        "\n".join(
            [
                "# DETech GTK-2.0 Configuration",
                f'gtk-theme-name="{gtk_theme}"',
                f'gtk-icon-theme-name="{icon_theme}"',
                f'gtk-font-name="{font_str}"',
                f'gtk-cursor-theme-name="{cursor_theme}"',
                f"gtk-cursor-theme-size={cursor_size}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    written.append(gtk2_rc)

    # 2. GTK-3.0 & GTK-4.0 settings.ini + complete gtk.css asset sheet
    for gtk_ver in ("gtk-3.0", "gtk-4.0"):
        gtk_dir = config_root / gtk_ver
        gtk_dir.mkdir(parents=True, exist_ok=True)
        settings_ini = gtk_dir / "settings.ini"
        settings_ini.write_text(
            "\n".join(
                [
                    "[Settings]",
                    f"gtk-theme-name={gtk_theme}",
                    f"gtk-icon-theme-name={icon_theme}",
                    f"gtk-font-name={font_str}",
                    f"gtk-cursor-theme-name={cursor_theme}",
                    f"gtk-cursor-theme-size={cursor_size}",
                    "gtk-application-prefer-dark-theme=1",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        written.append(settings_ini)

        gtk_css = gtk_dir / "gtk.css"
        gtk_css.write_text(
            "\n".join(
                [
                    "/* DETech Dynamic GTK-3/4 & Libadwaita Color & Widget Asset Bundle */",
                    f"@define-color accent_bg_color {palette['accent']};",
                    f"@define-color accent_fg_color {palette['bg_primary']};",
                    f"@define-color accent_color {palette['accent']};",
                    f"@define-color window_bg_color {palette['bg_primary']};",
                    f"@define-color window_fg_color {palette['fg_primary']};",
                    f"@define-color view_bg_color {palette['bg_secondary']};",
                    f"@define-color view_fg_color {palette['fg_primary']};",
                    f"@define-color headerbar_bg_color {palette['bg_secondary']};",
                    f"@define-color headerbar_fg_color {palette['fg_primary']};",
                    f"@define-color headerbar_border_color {palette['border_inactive']};",
                    f"@define-color card_bg_color {palette['bg_tertiary']};",
                    f"@define-color card_fg_color {palette['fg_primary']};",
                    f"@define-color dialog_bg_color {palette['bg_primary']};",
                    f"@define-color dialog_fg_color {palette['fg_primary']};",
                    f"@define-color popover_bg_color {palette['bg_secondary']};",
                    f"@define-color popover_fg_color {palette['fg_primary']};",
                    f"@define-color sidebar_bg_color {palette['bg_secondary']};",
                    f"@define-color sidebar_fg_color {palette['fg_primary']};",
                    f"@define-color destructive_bg_color {palette['urgent']};",
                    f"@define-color success_bg_color {palette['success']};",
                    f"@define-color warning_bg_color {palette['warning']};",
                    f"@define-color theme_bg_color {palette['bg_primary']};",
                    f"@define-color theme_fg_color {palette['fg_primary']};",
                    f"@define-color theme_base_color {palette['bg_secondary']};",
                    f"@define-color theme_text_color {palette['fg_primary']};",
                    f"@define-color theme_selected_bg_color {palette['accent']};",
                    f"@define-color theme_selected_fg_color {palette['bg_primary']};",
                    f"@define-color borders {palette['border_inactive']};",
                    "",
                    "selection {",
                    "    background-color: @accent_bg_color;",
                    "    color: @accent_fg_color;",
                    "}",
                    "tooltip {",
                    "    background-color: @popover_bg_color;",
                    "    color: @popover_fg_color;",
                    "    border: 1px solid @accent_color;",
                    "    border-radius: 8px;",
                    "}",
                    "headerbar {",
                    "    background-color: @headerbar_bg_color;",
                    "    color: @headerbar_fg_color;",
                    "}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        written.append(gtk_css)

    # 3. Qt5ct & Qt6ct configs and color scheme
    for qt_ver in ("qt5ct", "qt6ct"):
        qt_dir = config_root / qt_ver
        colors_dir = qt_dir / "colors"
        colors_dir.mkdir(parents=True, exist_ok=True)

        color_conf = colors_dir / "detech.conf"
        active_colors = ", ".join(
            [
                f"#ff{palette['fg_primary'][1:]}",
                f"#ff{palette['bg_secondary'][1:]}",
                f"#ff{palette['bg_tertiary'][1:]}",
                f"#ff{palette['bg_secondary'][1:]}",
                f"#ff{palette['bg_primary'][1:]}",
                f"#ff{palette['bg_secondary'][1:]}",
                f"#ff{palette['fg_primary'][1:]}",
                "#ffffffff",
                f"#ff{palette['fg_primary'][1:]}",
                f"#ff{palette['bg_primary'][1:]}",
                f"#ff{palette['bg_primary'][1:]}",
                "#ff000000",
                f"#ff{palette['accent'][1:]}",
                f"#ff{palette['bg_primary'][1:]}",
                f"#ff{palette['accent_alt'][1:]}",
                f"#ff{palette['urgent'][1:]}",
                f"#ff{palette['bg_secondary'][1:]}",
                f"#ff{palette['fg_primary'][1:]}",
                f"#ff{palette['bg_secondary'][1:]}",
                f"#ff{palette['fg_primary'][1:]}",
            ]
        )
        color_conf.write_text(
            "\n".join(
                [
                    "[ColorScheme]",
                    f"active_colors={active_colors}",
                    f"disabled_colors={active_colors}",
                    f"inactive_colors={active_colors}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        written.append(color_conf)

        qt_conf = qt_dir / f"{qt_ver}.conf"
        qt_conf.write_text(
            "\n".join(
                [
                    "[Appearance]",
                    f"color_scheme_path={color_conf}",
                    "custom_palette=true",
                    f"icon_theme={icon_theme}",
                    "style=kvantum-dark",
                    "",
                    "[Fonts]",
                    f'fixed="{fonts["mono"]},{fonts["size"]},-1,5,50,0,0,0,0,0"',
                    f'general="{fonts["sans"]},{fonts["size"]},-1,5,50,0,0,0,0,0"',
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        written.append(qt_conf)

    # 4. Kvantum Theme Asset Bundle (`Kvantum/kvantum.kvconfig` + `Kvantum/DETech/DETech.{kvconfig,svg}`)
    kv_dir = config_root / "Kvantum"
    kv_theme_dir = kv_dir / "DETech"
    kv_theme_dir.mkdir(parents=True, exist_ok=True)

    kv_conf = kv_dir / "kvantum.kvconfig"
    kv_conf.write_text(f"[General]\ntheme={kvantum_theme}\n", encoding="utf-8")
    written.append(kv_conf)

    detech_kvconfig = kv_theme_dir / "DETech.kvconfig"
    detech_kvconfig.write_text(render_kvantum_kvconfig(palette, theme_name="DETech"), encoding="utf-8")
    written.append(detech_kvconfig)

    detech_svg = kv_theme_dir / "DETech.svg"
    detech_svg.write_text(render_kvantum_svg(palette), encoding="utf-8")
    written.append(detech_svg)

    # 5. Dunst Notification Daemon config
    dunst_dir = config_root / "dunst"
    dunst_dir.mkdir(parents=True, exist_ok=True)
    dunstrc = dunst_dir / "dunstrc"
    dunstrc.write_text(
        "\n".join(
            [
                "# DETech Dunst Configuration",
                "[global]",
                "    monitor = 0",
                "    follow = mouse",
                "    width = 340",
                "    height = (0, 140)",
                "    origin = top-right",
                "    offset = (16, 16)",
                f"    font = {fonts['sans']} {fonts['size']}",
                "    frame_width = 2",
                f'    frame_color = "{palette["accent"]}"',
                "    corner_radius = 10",
                f'    highlight = "{palette["accent"]}"',
                "    history_length = 50",
                "    sticky_history = yes",
                "    show_indicators = yes",
                f'    icon_theme = "{icon_theme}"',
                "    enable_recursive_icon_lookup = true",
                "    icon_position = left",
                "    min_icon_size = 24",
                "    max_icon_size = 48",
                "    progress_bar = true",
                "    progress_bar_height = 8",
                "    progress_bar_frame_width = 1",
                "    mouse_left_click = close_current",
                "    mouse_middle_click = do_action, close_current",
                "    mouse_right_click = close_all",
                "",
                "[urgency_low]",
                f'    background = "{palette["bg_secondary"]}"',
                f'    foreground = "{palette["fg_secondary"]}"',
                "    timeout = 4",
                "",
                "[urgency_normal]",
                f'    background = "{palette["bg_primary"]}"',
                f'    foreground = "{palette["fg_primary"]}"',
                "    timeout = 6",
                "",
                "[urgency_critical]",
                f'    background = "{palette["bg_primary"]}"',
                f'    foreground = "{palette["urgent"]}"',
                f'    frame_color = "{palette["urgent"]}"',
                "    timeout = 0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    written.append(dunstrc)

    return written
