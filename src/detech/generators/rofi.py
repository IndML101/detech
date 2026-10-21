"""Rofi Configuration & App Drawer Layout Generator (15 Switchable Layouts)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from detech.core.lua_loader import load_lua_file
from detech.core.paths import get_presets_dir


def list_rofi_layouts() -> list[dict[str, Any]]:
    """Return all 15 switchable Rofi app drawer layouts from `presets/rofi/layouts.lua`."""
    path = get_presets_dir() / "rofi" / "layouts.lua"
    if not path.is_file():
        return []
    data = load_lua_file(path)
    return list(data.get("layouts", []))


def get_rofi_layout(layout_id: str) -> dict[str, Any]:
    """Retrieve a Rofi layout blueprint by ID."""
    layouts = list_rofi_layouts()
    for item in layouts:
        if item.get("id") == layout_id:
            return item
    if layouts:
        return layouts[0]
    raise ValueError(f"Rofi layout not found: {layout_id}")


def generate_rofi_configs(
    context: dict[str, Any],
    palette: dict[str, str],
    fonts: dict[str, Any],
    config_root: Path,
) -> list[Path]:
    """Generate Rofi `.rasi` files (`colors.rasi`, `fonts.rasi`, `config.rasi`, `menu.rasi`)."""
    rofi_dir = config_root / "rofi"
    rofi_dir.mkdir(parents=True, exist_ok=True)

    appearance = context.get("config", {}).get("appearance", {})
    layout_id = appearance.get("rofi_layout", "grid-cards")
    icon_theme = appearance.get("icon_theme", "Papirus-Dark")
    spec = get_rofi_layout(layout_id)

    # 1. colors.rasi
    colors_rasi = rofi_dir / "colors.rasi"
    colors_rasi.write_text(
        "\n".join(
            [
                "/* DETech Rofi Color Palette */",
                "* {",
                f"    bg-primary: {palette['bg_primary']};",
                f"    bg-secondary: {palette['bg_secondary']};",
                f"    bg-tertiary: {palette['bg_tertiary']};",
                f"    fg-primary: {palette['fg_primary']};",
                f"    fg-secondary: {palette['fg_secondary']};",
                f"    fg-muted: {palette['fg_muted']};",
                f"    accent: {palette['accent']};",
                f"    accent-alt: {palette['accent_alt']};",
                f"    urgent: {palette['urgent']};",
                "}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    # 2. fonts.rasi
    fonts_rasi = rofi_dir / "fonts.rasi"
    fonts_rasi.write_text(
        "\n".join(
            [
                "/* DETech Rofi Nerd Font Configuration */",
                "* {",
                f'    font: "{fonts["mono"]} {fonts["rofi_size"]}";',
                "}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    # 3. config.rasi (Active App Drawer Layout)
    show_icons = "true" if spec.get("show_icons", True) else "false"
    config_rasi = rofi_dir / "config.rasi"
    config_lines = [
        f"/* DETech Rofi App Drawer — Layout: {spec.get('name', layout_id)} ({layout_id}) */",
        "configuration {",
        '    modi: "drun,run,filebrowser,window";',
        f"    show-icons: {show_icons};",
        f'    icon-theme: "{icon_theme}";',
        '    display-drun: " Apps";',
        '    display-run: " Run";',
        '    display-filebrowser: " Files";',
        '    display-window: " Windows";',
        '    drun-display-format: "{name}";',
        "}",
        '@import "colors.rasi"',
        '@import "fonts.rasi"',
        "",
        "window {",
        f"    width: {spec.get('width', '680px')};",
        f"    location: {spec.get('location', 'center')};",
        "    background-color: @bg-primary;",
        "    border: 2px;",
        "    border-color: @accent;",
        f"    border-radius: {spec.get('border_radius', '12px')};",
        "    padding: 18px;",
        "}",
        "mainbox {",
        "    background-color: transparent;",
        "    children: [ inputbar, listview ];",
        "    spacing: 14px;",
        "}",
        "inputbar {",
        "    background-color: @bg-secondary;",
        "    text-color: @fg-primary;",
        f"    border-radius: {spec.get('border_radius', '12px')};",
        "    padding: 10px 14px;",
        "    children: [ prompt, entry ];",
        "    spacing: 10px;",
        "}",
        "prompt {",
        "    background-color: transparent;",
        "    text-color: @accent;",
        "}",
        "entry {",
        "    background-color: transparent;",
        "    text-color: @fg-primary;",
        '    placeholder: "Search...";',
        "    placeholder-color: @fg-muted;",
        "}",
        "listview {",
        "    background-color: transparent;",
        f"    columns: {spec.get('columns', 4)};",
        f"    lines: {spec.get('lines', 3)};",
        "    spacing: 8px;",
        "    cycle: true;",
        "    dynamic: true;",
        "    layout: vertical;",
        "}",
        "element {",
        "    background-color: @bg-secondary;",
        "    text-color: @fg-primary;",
        f"    orientation: {spec.get('orientation', 'vertical')};",
        f"    border-radius: {spec.get('border_radius', '12px')};",
        f"    padding: {spec.get('element_padding', '14px')};",
        "}",
        "element selected {",
        "    background-color: @accent;",
        "    text-color: @bg-primary;",
        "}",
        "element-icon {",
        "    background-color: transparent;",
        f"    size: {spec.get('icon_size', '42px')};",
        "    horizontal-align: 0.5;",
        "}",
        "element-text {",
        "    background-color: transparent;",
        "    text-color: inherit;",
        "    horizontal-align: 0.5;",
        "    vertical-align: 0.5;",
        "}",
    ]
    config_rasi.write_text("\n".join(config_lines) + "\n", encoding="utf-8")

    # 4. menu.rasi (Dedicated clean list theme for DETech interactive pickers)
    menu_rasi = rofi_dir / "menu.rasi"
    menu_lines = [
        "/* DETech Rofi Interactive Picker Theme */",
        '@import "colors.rasi"',
        '@import "fonts.rasi"',
        "window {",
        "    width: 720px;",
        "    location: center;",
        "    background-color: @bg-primary;",
        "    border: 2px;",
        "    border-color: @accent;",
        "    border-radius: 12px;",
        "    padding: 16px;",
        "}",
        "listview {",
        "    columns: 1;",
        "    lines: 12;",
        "    spacing: 6px;",
        "}",
        "element {",
        "    orientation: horizontal;",
        "    padding: 8px 12px;",
        "    border-radius: 8px;",
        "    background-color: @bg-secondary;",
        "    text-color: @fg-primary;",
        "}",
        "element selected {",
        "    background-color: @accent;",
        "    text-color: @bg-primary;",
        "}",
    ]
    menu_rasi.write_text("\n".join(menu_lines) + "\n", encoding="utf-8")

    return [colors_rasi, fonts_rasi, config_rasi, menu_rasi]
