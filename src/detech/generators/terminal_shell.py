"""Kitty Terminal & Starship Prompt Generator (15 Switchable Starship Prompts)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from detech.core.lua_loader import load_lua_file
from detech.core.paths import get_presets_dir


def list_starship_prompts() -> list[dict[str, Any]]:
    """Return all 15 switchable Starship prompt presets from `presets/starship/prompts.lua`."""
    path = get_presets_dir() / "starship" / "prompts.lua"
    if not path.is_file():
        return []
    data = load_lua_file(path)
    return list(data.get("prompts", []))


def get_starship_prompt(preset_id: str) -> dict[str, Any]:
    """Retrieve a Starship prompt blueprint by ID."""
    prompts = list_starship_prompts()
    for item in prompts:
        if item.get("id") == preset_id:
            return item
    if prompts:
        return prompts[0]
    raise ValueError(f"Starship prompt preset not found: {preset_id}")


def generate_terminal_and_shell_configs(
    context: dict[str, Any],
    palette: dict[str, str],
    fonts: dict[str, Any],
    config_root: Path,
) -> list[Path]:
    """Generate `kitty/kitty.conf`, `kitty/detech-theme.conf`, and `starship.toml`."""
    written: list[Path] = []

    # 1. Kitty configs
    kitty_dir = config_root / "kitty"
    kitty_dir.mkdir(parents=True, exist_ok=True)

    kitty_theme = kitty_dir / "detech-theme.conf"
    theme_lines = [
        "# DETech Kitty Color Palette",
        f"background {palette['bg_primary']}",
        f"foreground {palette['fg_primary']}",
        f"cursor {palette['accent']}",
        f"selection_background {palette['bg_tertiary']}",
        f"selection_foreground {palette['fg_primary']}",
        f"active_border_color {palette['accent']}",
        f"inactive_border_color {palette['border_inactive']}",
        f"active_tab_background {palette['accent']}",
        f"active_tab_foreground {palette['bg_primary']}",
        f"inactive_tab_background {palette['bg_secondary']}",
        f"inactive_tab_foreground {palette['fg_secondary']}",
    ]
    for idx in range(16):
        key = f"color{idx}"
        if key in palette:
            theme_lines.append(f"{key} {palette[key]}")
    kitty_theme.write_text("\n".join(theme_lines) + "\n", encoding="utf-8")
    written.append(kitty_theme)

    kitty_conf = kitty_dir / "kitty.conf"
    kitty_lines = [
        "# DETech Kitty Terminal Configuration",
        f"font_family      {fonts['mono']}",
        "bold_font        auto",
        "italic_font      auto",
        "bold_italic_font auto",
        f"font_size        {fonts['size']}.0",
        "window_padding_width 10",
        "confirm_os_window_close 0",
        "enable_audio_bell no",
        "background_opacity 0.92",
        "allow_remote_control yes",
        "include detech-theme.conf",
    ]
    kitty_conf.write_text("\n".join(kitty_lines) + "\n", encoding="utf-8")
    written.append(kitty_conf)

    # 2. Starship prompt config (15 presets)
    appearance = context.get("config", {}).get("appearance", {})
    preset_id = appearance.get("starship_preset", "tokyo-pill")
    spec = get_starship_prompt(preset_id)

    starship_path = config_root / "starship.toml"
    add_nl = "true" if spec.get("add_newline", True) else "false"
    fmt = spec.get("format", "$directory$git_branch$character").replace("\n", "\\n")
    rfmt = spec.get("right_format", "")

    starship_lines = [
        f"# DETech Starship Prompt — Preset: {spec.get('name', preset_id)} ({preset_id})",
        '"$schema" = "https://starship.rs/config-schema.json"',
        f"add_newline = {add_nl}",
        'palette = "detech"',
        f'format = "{fmt}"',
    ]
    if rfmt:
        starship_lines.append(f'right_format = "{rfmt}"')

    starship_lines.extend(
        [
            "",
            "[character]",
            f"success_symbol = '{spec.get('character_success', '[❯](bold fg:accent)')}'",
            f"error_symbol = '{spec.get('character_error', '[❯](bold fg:urgent)')}'",
            "",
            "[directory]",
            "truncation_length = 3",
            'truncation_symbol = "…/"',
            'style = "bold fg:accent"',
            "",
            "[git_branch]",
            'symbol = " "',
            'style = "fg:accent_alt"',
            "",
            "[git_status]",
            'style = "fg:warning"',
            "",
            "[cmd_duration]",
            "min_time = 500",
            'format = "[󱎫 $duration](fg:warning) "',
            "",
            "[time]",
            "disabled = false",
            'time_format = "%H:%M"',
            'format = "[$time](fg:fg_muted)"',
            "",
            "[palettes.detech]",
            f'bg_primary = "{palette["bg_primary"]}"',
            f'bg_secondary = "{palette["bg_secondary"]}"',
            f'bg_tertiary = "{palette["bg_tertiary"]}"',
            f'fg_primary = "{palette["fg_primary"]}"',
            f'fg_secondary = "{palette["fg_secondary"]}"',
            f'fg_muted = "{palette["fg_muted"]}"',
            f'accent = "{palette["accent"]}"',
            f'accent_alt = "{palette["accent_alt"]}"',
            f'urgent = "{palette["urgent"]}"',
            f'success = "{palette["success"]}"',
            f'warning = "{palette["warning"]}"',
        ]
    )
    starship_path.write_text("\n".join(starship_lines) + "\n", encoding="utf-8")
    written.append(starship_path)

    return written
