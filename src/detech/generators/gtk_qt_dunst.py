"""GTK-3/4, Qt5ct/Qt6ct, Kvantum, and Dunst Notification Daemon Generator."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def generate_gtk_qt_dunst_configs(
    context: dict[str, Any],
    theme_data: dict[str, Any],
    palette: dict[str, str],
    fonts: dict[str, Any],
    config_root: Path,
) -> list[Path]:
    """Generate GTK-3/4, Qt5ct/Qt6ct, Kvantum, and Dunst configs with synced colors and Nerd Fonts."""
    written: list[Path] = []
    appearance = context.get("config", {}).get("appearance", {})

    gtk_theme = theme_data.get("gtk_theme", "Adwaita-dark")
    icon_theme = appearance.get("icon_theme") or theme_data.get("icon_theme", "Papirus-Dark")
    cursor_theme = appearance.get("cursor_theme") or theme_data.get("cursor_theme", "Bibata-Modern-Ice")
    cursor_size = appearance.get("cursor_size", 24)
    kvantum_theme = theme_data.get("kvantum_theme", "KvArcDark")
    font_str = f"{fonts['sans']} {fonts['size']}"

    # 1. GTK-3.0 & GTK-4.0 settings.ini + gtk.css
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
                    "/* DETech Dynamic GTK Color Overrides */",
                    f"@define-color accent_bg_color {palette['accent']};",
                    f"@define-color accent_color {palette['accent']};",
                    f"@define-color window_bg_color {palette['bg_primary']};",
                    f"@define-color window_fg_color {palette['fg_primary']};",
                    f"@define-color view_bg_color {palette['bg_secondary']};",
                    f"@define-color view_fg_color {palette['fg_primary']};",
                    f"@define-color headerbar_bg_color {palette['bg_secondary']};",
                    f"@define-color headerbar_fg_color {palette['fg_primary']};",
                    f"@define-color card_bg_color {palette['bg_tertiary']};",
                    f"@define-color card_fg_color {palette['fg_primary']};",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        written.append(gtk_css)

    # 2. Qt5ct & Qt6ct configs and color scheme
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

    # 3. Kvantum config
    kv_dir = config_root / "Kvantum"
    kv_dir.mkdir(parents=True, exist_ok=True)
    kv_conf = kv_dir / "kvantum.kvconfig"
    kv_conf.write_text(f"[General]\ntheme={kvantum_theme}\n", encoding="utf-8")
    written.append(kv_conf)

    # 4. Dunst Notification Daemon config
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
