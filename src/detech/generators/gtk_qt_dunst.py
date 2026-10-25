"""GTK-2/3/4, Qt5ct/Qt6ct, Kvantum Asset Bundle, and Dunst Notification Daemon Generator."""

from __future__ import annotations

import shutil
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


def render_gtk2_gtkrc(
    gtk_theme: str,
    icon_theme: str,
    font_str: str,
    cursor_theme: str,
    cursor_size: int,
    palette: dict[str, str],
) -> str:
    """Render GTK-2.0 gtkrc with system-wide dark palette, color-scheme, and fallback styling."""
    bg_pri = palette["bg_primary"]
    bg_sec = palette["bg_secondary"]
    bg_ter = palette["bg_tertiary"]
    fg_pri = palette["fg_primary"]
    fg_muted = palette["fg_muted"]
    accent = palette["accent"]
    bdr = palette.get("border_inactive", bg_ter)

    color_scheme = (
        f"base_color:{bg_sec}\\n"
        f"bg_color:{bg_pri}\\n"
        f"tooltip_bg_color:{bg_sec}\\n"
        f"selected_bg_color:{accent}\\n"
        f"text_color:{fg_pri}\\n"
        f"fg_color:{fg_pri}\\n"
        f"tooltip_fg_color:{fg_pri}\\n"
        f"selected_fg_color:{bg_pri}"
    )

    lines = [
        "# DETech GTK-2.0 Dark Configuration",
        f'gtk-theme-name="{gtk_theme}"',
        f'gtk-icon-theme-name="{icon_theme}"',
        f'gtk-font-name="{font_str}"',
        f'gtk-cursor-theme-name="{cursor_theme}"',
        f"gtk-cursor-theme-size={cursor_size}",
        f'gtk-color-scheme="{color_scheme}"',
        "",
        'style "detech-dark" {',
        f'    base[NORMAL] = "{bg_sec}"',
        f'    base[PRELIGHT] = "{bg_ter}"',
        f'    base[ACTIVE] = "{accent}"',
        f'    base[SELECTED] = "{accent}"',
        f'    base[INSENSITIVE] = "{bg_pri}"',
        "",
        f'    bg[NORMAL] = "{bg_pri}"',
        f'    bg[PRELIGHT] = "{bg_sec}"',
        f'    bg[ACTIVE] = "{bg_sec}"',
        f'    bg[SELECTED] = "{accent}"',
        f'    bg[INSENSITIVE] = "{bg_pri}"',
        "",
        f'    fg[NORMAL] = "{fg_pri}"',
        f'    fg[PRELIGHT] = "{fg_pri}"',
        f'    fg[ACTIVE] = "{fg_pri}"',
        f'    fg[SELECTED] = "{bg_pri}"',
        f'    fg[INSENSITIVE] = "{fg_muted}"',
        "",
        f'    text[NORMAL] = "{fg_pri}"',
        f'    text[PRELIGHT] = "{fg_pri}"',
        f'    text[ACTIVE] = "{fg_pri}"',
        f'    text[SELECTED] = "{bg_pri}"',
        f'    text[INSENSITIVE] = "{fg_muted}"',
        "}",
        'class "GtkWidget" style "detech-dark"',
    ]
    return "\n".join(lines) + "\n"


def render_gtk_css(palette: dict[str, str]) -> str:
    """Render a comprehensive GTK-3.0 / GTK-4.0 & Libadwaita dark theme CSS asset bundle."""
    bg_pri = palette["bg_primary"]
    bg_sec = palette["bg_secondary"]
    bg_ter = palette["bg_tertiary"]
    fg_pri = palette["fg_primary"]
    fg_sec = palette["fg_secondary"]
    fg_muted = palette["fg_muted"]
    accent = palette["accent"]
    accent_alt = palette["accent_alt"]
    urgent = palette["urgent"]
    success = palette.get("success", "#52b788")
    warning = palette.get("warning", "#f4a261")
    bdr = palette.get("border_inactive", bg_ter)

    lines = [
        "/* DETech Dynamic GTK-3/4 & Libadwaita Complete Dark Theme Color & Widget Sheet */",
        f"@define-color accent_bg_color {accent};",
        f"@define-color accent_fg_color {bg_pri};",
        f"@define-color accent_color {accent};",
        f"@define-color window_bg_color {bg_pri};",
        f"@define-color window_fg_color {fg_pri};",
        f"@define-color view_bg_color {bg_sec};",
        f"@define-color view_fg_color {fg_pri};",
        f"@define-color headerbar_bg_color {bg_sec};",
        f"@define-color headerbar_fg_color {fg_pri};",
        f"@define-color headerbar_border_color {bdr};",
        f"@define-color headerbar_backdrop_color {bg_pri};",
        f"@define-color card_bg_color {bg_ter};",
        f"@define-color card_fg_color {fg_pri};",
        f"@define-color dialog_bg_color {bg_pri};",
        f"@define-color dialog_fg_color {fg_pri};",
        f"@define-color popover_bg_color {bg_sec};",
        f"@define-color popover_fg_color {fg_pri};",
        f"@define-color sidebar_bg_color {bg_sec};",
        f"@define-color sidebar_fg_color {fg_pri};",
        f"@define-color destructive_bg_color {urgent};",
        f"@define-color destructive_fg_color {bg_pri};",
        f"@define-color success_bg_color {success};",
        f"@define-color warning_bg_color {warning};",
        f"@define-color theme_bg_color {bg_pri};",
        f"@define-color theme_fg_color {fg_pri};",
        f"@define-color theme_base_color {bg_sec};",
        f"@define-color theme_text_color {fg_pri};",
        f"@define-color theme_selected_bg_color {accent};",
        f"@define-color theme_selected_fg_color {bg_pri};",
        f"@define-color borders {bdr};",
        f"@define-color scrollbar_slider_color {bg_ter};",
        f"@define-color scrollbar_slider_hover_color {accent};",
        "",
        "/* Base Windows, Dialogs, Surfaces */",
        "window, dialog, messagedialog, .background, window.background {",
        "    background-color: @window_bg_color;",
        "    color: @window_fg_color;",
        "}",
        "",
        "/* Views, Text Editors, Treeviews, Lists */",
        "view, textview, textview text, iconview, .view {",
        "    background-color: @view_bg_color;",
        "    color: @view_fg_color;",
        "}",
        "",
        "/* Text Inputs, Search Bars, Entries */",
        "entry, searchbar entry, spinbutton {",
        "    background-color: @view_bg_color;",
        "    color: @theme_text_color;",
        "    border: 1px solid @borders;",
        "    border-radius: 6px;",
        "    padding: 6px 10px;",
        "}",
        "entry:focus, searchbar entry:focus, spinbutton:focus {",
        "    border-color: @accent_color;",
        "}",
        "",
        "/* Buttons & Actions */",
        "button {",
        "    background-color: @theme_base_color;",
        "    color: @theme_text_color;",
        "    border: 1px solid @borders;",
        "    border-radius: 6px;",
        "    padding: 6px 12px;",
        "}",
        "button:hover {",
        "    background-color: @card_bg_color;",
        "    border-color: @accent_color;",
        "}",
        "button:checked, button:active, button.suggested-action {",
        "    background-color: @accent_bg_color;",
        "    color: @accent_fg_color;",
        "    border-color: @accent_color;",
        "}",
        "button.destructive-action {",
        "    background-color: @destructive_bg_color;",
        "    color: @destructive_fg_color;",
        "}",
        "",
        "/* Headerbars, Titlebars, Toolbars */",
        "headerbar, .titlebar, toolbar {",
        "    background-color: @headerbar_bg_color;",
        "    color: @headerbar_fg_color;",
        "    border-bottom: 1px solid @headerbar_border_color;",
        "}",
        "headerbar:backdrop, .titlebar:backdrop {",
        "    background-color: @headerbar_backdrop_color;",
        "}",
        "",
        "/* Sidebars & Lists */",
        ".sidebar, placessidebar, stacksidebar, list, row {",
        "    background-color: @sidebar_bg_color;",
        "    color: @sidebar_fg_color;",
        "}",
        "row:selected, list > row:selected, treeview.view:selected {",
        "    background-color: @accent_bg_color;",
        "    color: @accent_fg_color;",
        "}",
        "",
        "/* Selection & Focus */",
        "selection, :selected, *:selected {",
        "    background-color: @accent_bg_color;",
        "    color: @accent_fg_color;",
        "}",
        "",
        "/* Notebook Tabs */",
        "notebook, notebook > stack {",
        "    background-color: @window_bg_color;",
        "}",
        "notebook > header {",
        "    background-color: @view_bg_color;",
        "    border-color: @borders;",
        "}",
        "notebook > header tab {",
        "    background-color: @view_bg_color;",
        "    color: @theme_text_color;",
        "    padding: 6px 14px;",
        "}",
        "notebook > header tab:checked {",
        "    background-color: @window_bg_color;",
        "    border-bottom: 2px solid @accent_color;",
        "    color: @accent_color;",
        "}",
        "",
        "/* Popovers, Menus, Dropdowns */",
        "popover, popover.background, menu, menubar {",
        "    background-color: @popover_bg_color;",
        "    color: @popover_fg_color;",
        "    border: 1px solid @borders;",
        "    border-radius: 8px;",
        "}",
        "menuitem:hover, modelbutton:hover {",
        "    background-color: @accent_bg_color;",
        "    color: @accent_fg_color;",
        "}",
        "",
        "/* Tooltips */",
        "tooltip, tooltip.background {",
        "    background-color: @popover_bg_color;",
        "    color: @popover_fg_color;",
        "    border: 1px solid @accent_color;",
        "    border-radius: 8px;",
        "    padding: 6px 10px;",
        "}",
        "",
        "/* Scrollbars */",
        "scrollbar slider {",
        "    background-color: @scrollbar_slider_color;",
        "    border-radius: 6px;",
        "    min-width: 6px;",
        "    min-height: 6px;",
        "}",
        "scrollbar slider:hover {",
        "    background-color: @scrollbar_slider_hover_color;",
        "}",
        "",
        "/* Progress Bars & Sliders */",
        "progressbar progress, progressbar > trough > progress {",
        "    background-color: @accent_color;",
        "    border-radius: 4px;",
        "}",
        "progressbar trough, progressbar > trough {",
        "    background-color: @view_bg_color;",
        "    border: 1px solid @borders;",
        "}",
        "scale slider, scale > contents > trough > slider {",
        "    background-color: @accent_color;",
        "    border-radius: 50%;",
        "}",
        "scale highlight, scale > contents > trough > highlight {",
        "    background-color: @accent_color;",
        "}",
        "scale trough, scale > contents > trough {",
        "    background-color: @view_bg_color;",
        "}",
        "",
        "/* Switches, Checkboxes & Radio */",
        "check:checked, radio:checked, switch:checked {",
        "    background-color: @accent_color;",
        "    color: @accent_fg_color;",
        "    border-color: @accent_color;",
        "}",
        "",
        "/* Links & Accents */",
        "link, link:link, *:link {",
        "    color: @accent_color;",
        "}",
        f"link:visited, *:visited {{",
        f"    color: {accent_alt};",
        "}",
        "separator {",
        "    background-color: @borders;",
        "}",
    ]
    return "\n".join(lines) + "\n"


def render_qt_colors_conf(palette: dict[str, str]) -> str:
    """Render 21-role Qt5ct / Qt6ct detech.conf color scheme synced with primary/secondary and accent colors."""
    c_fg = f"#ff{palette['fg_primary'].lstrip('#')}"
    c_fg_muted = f"#ff{palette['fg_muted'].lstrip('#')}"
    c_bg_pri = f"#ff{palette['bg_primary'].lstrip('#')}"
    c_bg_sec = f"#ff{palette['bg_secondary'].lstrip('#')}"
    c_bg_ter = f"#ff{palette['bg_tertiary'].lstrip('#')}"
    c_border = f"#ff{palette.get('border_inactive', palette['bg_tertiary']).lstrip('#')}"
    c_accent = f"#ff{palette['accent'].lstrip('#')}"
    c_accent_alt = f"#ff{palette['accent_alt'].lstrip('#')}"

    # Standard 21 QPalette roles:
    # 0:WindowText, 1:Button, 2:Light, 3:Midlight, 4:Dark, 5:Mid, 6:Text, 7:BrightText,
    # 8:ButtonText, 9:Base (secondary), 10:Window (primary), 11:Shadow, 12:Highlight (accent),
    # 13:HighlightedText, 14:Link, 15:LinkVisited, 16:AlternateBase, 17:NoRole, 18:ToolTipBase,
    # 19:ToolTipText, 20:PlaceholderText
    active = [
        c_fg,        # 0: WindowText
        c_bg_sec,    # 1: Button
        c_bg_ter,    # 2: Light
        c_bg_sec,    # 3: Midlight
        c_bg_pri,    # 4: Dark
        c_border,    # 5: Mid
        c_fg,        # 6: Text
        "#ffffffff", # 7: BrightText
        c_fg,        # 8: ButtonText
        c_bg_sec,    # 9: Base
        c_bg_pri,    # 10: Window
        "#ff000000", # 11: Shadow
        c_accent,    # 12: Highlight
        c_bg_pri,    # 13: HighlightedText
        c_accent,    # 14: Link
        c_accent_alt,# 15: LinkVisited
        c_bg_ter,    # 16: AlternateBase
        c_fg,        # 17: NoRole
        c_bg_sec,    # 18: ToolTipBase
        c_fg,        # 19: ToolTipText
        c_fg_muted,  # 20: PlaceholderText
    ]

    disabled = list(active)
    disabled[0] = c_fg_muted
    disabled[6] = c_fg_muted
    disabled[8] = c_fg_muted
    disabled[13] = c_fg_muted
    disabled[17] = c_fg_muted
    disabled[19] = c_fg_muted

    return "\n".join(
        [
            "[ColorScheme]",
            f"active_colors={', '.join(active)}",
            f"disabled_colors={', '.join(disabled)}",
            f"inactive_colors={', '.join(active)}",
        ]
    ) + "\n"


def render_qt_qss(palette: dict[str, str]) -> str:
    """Render a comprehensive Qt Style Sheet (QSS) enforcing dark background and accent colors."""
    bg_pri = palette["bg_primary"]
    bg_sec = palette["bg_secondary"]
    bg_ter = palette["bg_tertiary"]
    fg_pri = palette["fg_primary"]
    fg_sec = palette["fg_secondary"]
    accent = palette["accent"]
    bdr = palette.get("border_inactive", bg_ter)

    return f"""/* DETech Qt Dynamic Color & Dark Theme QSS */
QWidget {{
    background-color: {bg_pri};
    color: {fg_pri};
    selection-background-color: {accent};
    selection-color: {bg_pri};
}}

QMainWindow, QDialog, QMessageBox {{
    background-color: {bg_pri};
    color: {fg_pri};
}}

QTextEdit, QPlainTextEdit, QLineEdit, QAbstractItemView, QListView, QTreeView, QTableView {{
    background-color: {bg_sec};
    color: {fg_pri};
    selection-background-color: {accent};
    selection-color: {bg_pri};
    border: 1px solid {bdr};
    border-radius: 4px;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {accent};
}}

QPushButton {{
    background-color: {bg_sec};
    color: {fg_pri};
    border: 1px solid {bdr};
    border-radius: 5px;
    padding: 6px 14px;
}}

QPushButton:hover {{
    background-color: {bg_ter};
    border-color: {accent};
}}

QPushButton:pressed {{
    background-color: {accent};
    color: {bg_pri};
}}

QTabBar::tab {{
    background-color: {bg_sec};
    color: {fg_sec};
    padding: 7px 14px;
    border: 1px solid {bdr};
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}}

QTabBar::tab:selected {{
    background-color: {bg_pri};
    color: {accent};
    border-bottom: 2px solid {accent};
}}

QTabBar::tab:hover:!selected {{
    background-color: {bg_ter};
}}

QMenuBar {{
    background-color: {bg_sec};
    color: {fg_pri};
    border-bottom: 1px solid {bdr};
}}

QMenuBar::item:selected {{
    background-color: {accent};
    color: {bg_pri};
}}

QMenu {{
    background-color: {bg_sec};
    color: {fg_pri};
    border: 1px solid {bdr};
    border-radius: 6px;
    padding: 4px;
}}

QMenu::item {{
    padding: 6px 24px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {accent};
    color: {bg_pri};
}}

QScrollBar:vertical {{
    background-color: {bg_pri};
    width: 10px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {bg_ter};
    min-height: 20px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {accent};
}}

QScrollBar:horizontal {{
    background-color: {bg_pri};
    height: 10px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background-color: {bg_ter};
    min-width: 20px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {accent};
}}

QProgressBar {{
    background-color: {bg_sec};
    border: 1px solid {bdr};
    border-radius: 4px;
    text-align: center;
    color: {fg_pri};
}}

QProgressBar::chunk {{
    background-color: {accent};
    border-radius: 3px;
}}

QSlider::groove:horizontal {{
    height: 6px;
    background-color: {bg_sec};
    border-radius: 3px;
}}

QSlider::sub-page:horizontal {{
    background-color: {accent};
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background-color: {accent};
    width: 14px;
    margin-top: -4px;
    margin-bottom: -4px;
    border-radius: 7px;
}}

QToolTip {{
    background-color: {bg_sec};
    color: {fg_pri};
    border: 1px solid {accent};
    border-radius: 6px;
    padding: 4px 8px;
}}
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
    kvantum_theme = appearance.get("kvantum_theme") or "DETech"
    font_str = f"{fonts['sans']} {fonts['size']}"

    # 1. GTK-2.0 gtkrc
    gtk2_dir = config_root / "gtk-2.0"
    gtk2_dir.mkdir(parents=True, exist_ok=True)
    gtk2_rc = gtk2_dir / "gtkrc"
    gtk2_rc.write_text(
        render_gtk2_gtkrc(gtk_theme, icon_theme, font_str, cursor_theme, cursor_size, palette),
        encoding="utf-8",
    )
    written.append(gtk2_rc)

    # 2. GTK-3.0 & GTK-4.0 settings.ini + complete gtk.css asset sheet
    gtk_color_scheme = (
        f"base_color:{palette['bg_secondary']};"
        f"bg_color:{palette['bg_primary']};"
        f"tooltip_bg_color:{palette['bg_secondary']};"
        f"selected_bg_color:{palette['accent']};"
        f"text_color:{palette['fg_primary']};"
        f"fg_color:{palette['fg_primary']};"
        f"tooltip_fg_color:{palette['fg_primary']};"
        f"selected_fg_color:{palette['bg_primary']}"
    )

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
                    f"gtk-color-scheme={gtk_color_scheme}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        written.append(settings_ini)

        gtk_css = gtk_dir / "gtk.css"
        gtk_css.write_text(render_gtk_css(palette), encoding="utf-8")
        written.append(gtk_css)

    # 3. Qt5ct & Qt6ct configs, color scheme, and QSS style sheet
    has_kvantum = bool(
        shutil.which("kvantummanager")
        or Path("/usr/local/lib/qt5/plugins/styles/libkvantum.so").is_file()
        or Path("/usr/local/lib/qt6/plugins/styles/libkvantum.so").is_file()
        or Path("/usr/lib/qt5/plugins/styles/libkvantum.so").is_file()
        or Path("/usr/lib/qt6/plugins/styles/libkvantum.so").is_file()
    )
    qt_style = appearance.get("qt_style") or ("kvantum-dark" if has_kvantum else "Fusion")

    for qt_ver in ("qt5ct", "qt6ct"):
        qt_dir = config_root / qt_ver
        colors_dir = qt_dir / "colors"
        qss_dir = qt_dir / "qss"
        colors_dir.mkdir(parents=True, exist_ok=True)
        qss_dir.mkdir(parents=True, exist_ok=True)

        color_conf = colors_dir / "detech.conf"
        color_conf.write_text(render_qt_colors_conf(palette), encoding="utf-8")
        written.append(color_conf)

        qss_conf = qss_dir / "detech.qss"
        qss_conf.write_text(render_qt_qss(palette), encoding="utf-8")
        written.append(qss_conf)

        qt_conf = qt_dir / f"{qt_ver}.conf"
        qt_conf.write_text(
            "\n".join(
                [
                    "[Appearance]",
                    f"color_scheme_path={color_conf}",
                    "custom_palette=true",
                    f"icon_theme={icon_theme}",
                    f"qss_path={qss_conf}",
                    f"style={qt_style}",
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
