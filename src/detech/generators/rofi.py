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


def render_rofi_layout_rasi(
    spec: dict[str, Any],
    icon_theme: str,
    import_prefix: str = "",
) -> str:
    """Render a complete Rofi `.rasi` configuration for a given layout blueprint."""
    layout_id = spec.get("id", "grid-cards")
    variant = spec.get("style_variant", "card-grid")
    show_icons = "true" if spec.get("show_icons", True) else "false"
    show_mode_switcher = bool(spec.get("show_mode_switcher", False))
    prompt_symbol = spec.get("prompt_symbol", " Apps")
    placeholder = spec.get("placeholder", "Search...")
    border_radius = spec.get("border_radius", "12px")
    orientation = spec.get("orientation", "vertical")
    text_align = "0.5" if orientation == "vertical" else "0.0"

    window_props = [
        f"    width: {spec.get('width', '680px')};",
        f"    location: {spec.get('location', 'center')};",
    ]
    if "height" in spec:
        window_props.append(f"    height: {spec['height']};")
    if "x_offset" in spec:
        window_props.append(f"    x-offset: {spec['x_offset']};")
    if "y_offset" in spec:
        window_props.append(f"    y-offset: {spec['y_offset']};")
    if spec.get("fullscreen"):
        window_props.append("    fullscreen: true;")

    window_props.extend(
        [
            "    background-color: @bg-primary;",
            "    border: 2px;",
            "    border-color: @accent;",
            f"    border-radius: {border_radius};",
            f"    padding: {'28px' if variant == 'launchpad' else '18px'};",
        ]
    )

    mainbox_children = "[ inputbar, listview, mode-switcher ]" if show_mode_switcher else "[ inputbar, listview ]"
    inputbar_padding = "22px 18px" if variant in ("banner-card", "hyde-classic") else "10px 14px"

    lines = [
        f"/* DETech Rofi App Drawer — Layout: {spec.get('name', layout_id)} ({layout_id}) */",
        f"/* Variant: {variant} | Description: {spec.get('description', '')} */",
        "configuration {",
        '    modi: "drun,run,filebrowser,window";',
        f"    show-icons: {show_icons};",
        f'    icon-theme: "{icon_theme}";',
        f'    display-drun: "{prompt_symbol}";',
        '    display-run: " Run";',
        '    display-filebrowser: " Files";',
        '    display-window: " Windows";',
        '    drun-display-format: "{name}";',
        "}",
        f'@import "{import_prefix}colors.rasi"',
        f'@import "{import_prefix}fonts.rasi"',
        "",
        "window {",
        *window_props,
        "}",
        "mainbox {",
        "    background-color: transparent;",
        f"    children: {mainbox_children};",
        "    spacing: 14px;",
        "}",
        "inputbar {",
        "    background-color: @bg-secondary;",
        "    text-color: @fg-primary;",
        f"    border-radius: {border_radius};",
        f"    padding: {inputbar_padding};",
        "    children: [ prompt, entry ];",
        "    spacing: 10px;",
        f"    border: {'1px' if variant in ('cyber-hud', 'banner-card', 'retro-term') else '0px'};",
        "    border-color: @accent;",
        "}",
        "prompt {",
        "    background-color: transparent;",
        "    text-color: @accent;",
        "}",
        "entry {",
        "    background-color: transparent;",
        "    text-color: @fg-primary;",
        f'    placeholder: "{placeholder}";',
        "    placeholder-color: @fg-muted;",
        "}",
        "listview {",
        "    background-color: transparent;",
        f"    columns: {spec.get('columns', 4)};",
        f"    lines: {spec.get('lines', 3)};",
        "    spacing: 10px;",
        "    cycle: true;",
        "    dynamic: true;",
        "    layout: vertical;",
        "    border: 1px 0px 0px 0px;",
        "    border-color: @bg-tertiary;",
        "    padding: 12px 0px 0px 0px;",
        "}",
        "element {",
        "    background-color: @bg-secondary;",
        "    text-color: @fg-primary;",
        f"    orientation: {orientation};",
        f"    border-radius: {border_radius};",
        f"    padding: {spec.get('element_padding', '16px 18px')};",
        "    spacing: 10px;",
        "    cursor: pointer;",
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
        f"    horizontal-align: {text_align};",
        "    vertical-align: 0.5;",
        "}",
        "mode-switcher {",
        "    background-color: transparent;",
        "    spacing: 10px;",
        "    border: 1px 0px 0px 0px;",
        "    border-color: @bg-tertiary;",
        "    padding: 10px 0px 0px 0px;",
        "}",
        "    spacing: 8px;",
        "}",
        "button {",
        "    padding: 8px 12px;",
        f"    border-radius: {border_radius};",
        "    background-color: @bg-secondary;",
        "    text-color: @fg-secondary;",
        "}",
        "button selected {",
        "    background-color: @accent;",
        "    text-color: @bg-primary;",
        "}",
    ]
    return "\n".join(lines) + "\n"


def generate_rofi_configs(
    context: dict[str, Any],
    palette: dict[str, str],
    fonts: dict[str, Any],
    config_root: Path,
) -> list[Path]:
    """Generate Rofi `.rasi` files (`colors.rasi`, `fonts.rasi`, `config.rasi`, `menu.rasi`, and all 15 layouts)."""
    rofi_dir = config_root / "rofi"
    layouts_dir = rofi_dir / "layouts"
    rofi_dir.mkdir(parents=True, exist_ok=True)
    layouts_dir.mkdir(parents=True, exist_ok=True)

    appearance = context.get("config", {}).get("appearance", {})
    layout_id = appearance.get("rofi_layout", "grid-cards")
    icon_theme = appearance.get("icon_theme", "Papirus-Dark")
    active_spec = get_rofi_layout(layout_id)

    written: list[Path] = []

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
                f"    border-inactive: {palette.get('border_inactive', palette['bg_tertiary'])};",
                f"    separatorcolor: {palette['bg_tertiary']};",
                "}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    written.append(colors_rasi)

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
    written.append(fonts_rasi)

    # 3. Pre-compile all 15 switchable Rofi layouts into `rofi/layouts/<id>.rasi`
    for item in list_rofi_layouts():
        lid = item["id"]
        l_path = layouts_dir / f"{lid}.rasi"
        l_path.write_text(
            render_rofi_layout_rasi(item, icon_theme=icon_theme, import_prefix="../"),
            encoding="utf-8",
        )
        written.append(l_path)

    # 4. config.rasi (Active App Drawer Layout)
    config_rasi = rofi_dir / "config.rasi"
    config_rasi.write_text(
        render_rofi_layout_rasi(active_spec, icon_theme=icon_theme, import_prefix=""),
        encoding="utf-8",
    )
    written.append(config_rasi)

    # 5. menu.rasi (Dedicated clean list theme for DETech interactive pickers)
    menu_rasi = rofi_dir / "menu.rasi"
    menu_lines = [
        "/* DETech Rofi Interactive Picker Theme */",
        '@import "colors.rasi"',
        '@import "fonts.rasi"',
        "window {",
        "    width: 760px;",
        "    location: center;",
        "    background-color: @bg-primary;",
        "    border: 2px;",
        "    border-color: @accent;",
        "    border-radius: 14px;",
        "    padding: 20px;",
        "}",
        "mainbox {",
        "    background-color: transparent;",
        "    children: [ inputbar, message, listview ];",
        "    spacing: 12px;",
        "}",
        "inputbar {",
        "    background-color: @bg-secondary;",
        "    text-color: @fg-primary;",
        "    border-radius: 10px;",
        "    padding: 12px 16px;",
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
        '    placeholder: "Type to filter...";',
        "    placeholder-color: @fg-muted;",
        "}",
        "message {",
        "    padding: 8px 12px;",
        "    background-color: @bg-secondary;",
        "    border-radius: 8px;",
        "    text-color: @fg-secondary;",
        "}",
        "textbox {",
        "    text-color: inherit;",
        "    background-color: transparent;",
        "}",
        "listview {",
        "    columns: 1;",
        "    lines: 10;",
        "    spacing: 8px;",
        "    cycle: true;",
        "    dynamic: true;",
        "    layout: vertical;",
        "    border: 1px 0px 0px 0px;",
        "    border-color: @bg-tertiary;",
        "    padding: 12px 0px 0px 0px;",
        "}",
        "element {",
        "    orientation: horizontal;",
        "    padding: 14px 18px;",
        "    border-radius: 10px;",
        "    background-color: @bg-secondary;",
        "    text-color: @fg-primary;",
        "    spacing: 12px;",
        "    cursor: pointer;",
        "}",
        "element selected {",
        "    background-color: @accent;",
        "    text-color: @bg-primary;",
        "}",
        "element-icon {",
        "    background-color: transparent;",
        "    size: 28px;",
        "    vertical-align: 0.5;",
        "}",
        "element-text {",
        "    background-color: transparent;",
        "    text-color: inherit;",
        "    vertical-align: 0.5;",
        "}",
    ]
    menu_rasi.write_text("\n".join(menu_lines) + "\n", encoding="utf-8")
    written.append(menu_rasi)

    return written
