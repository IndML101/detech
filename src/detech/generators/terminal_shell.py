"""Kitty Terminal, Neofetch System Info & Starship Prompt Generator (15 Switchable Starship Prompts)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from detech.core.lua_loader import load_lua_file
from detech.core.paths import get_presets_dir


def render_neofetch_conf(
    context: dict[str, Any],
    palette: dict[str, str],
    fonts: dict[str, Any],
) -> str:
    """Render a FreeBSD + DETech themed `neofetch/config.conf` file."""
    cfg = context.get("config", {})
    appearance = cfg.get("appearance", {})
    term_info = cfg.get("terminal_info", {})

    theme_name = appearance.get("theme", "bsd-crimson")
    waybar_layout = appearance.get("waybar_layout", "island-top")
    starship_preset = appearance.get("starship_preset", "tokyo-pill")
    ascii_distro = term_info.get("ascii_distro", "FreeBSD")
    show_zfs = bool(term_info.get("show_zfs", True))
    show_hypr_theme = bool(term_info.get("show_hyprland_theme", True))

    info_lines = [
        "print_info() {",
        "    info title",
        "    info underline",
        '    info " OS" distro',
        '    info "󰌢 Host" model',
        '    info " Kernel" kernel',
        '    info "󱎫 Uptime" uptime',
        '    info "󰏖 Packages" packages',
        '    info " Shell" shell',
        '    info " WM" wm',
    ]
    if show_hypr_theme:
        icon_theme = appearance.get("icon_theme", "Papirus-Dark")
        info_lines.extend(
            [
                f'    prin "󰔎 DETech Theme" "{theme_name} ({palette["accent"]})"',
                f'    prin "󰀻 Icon Theme" "{icon_theme}"',
                f'    prin "󰕮 Waybar Layout" "{waybar_layout}"',
                f'    prin "󱆃 Starship" "{starship_preset}"',
            ]
        )
    info_lines.extend(
        [
            f'    prin "󰛖 Nerd Font" "{fonts["mono"]} ({fonts["size"]}pt)"',
            '    info " Terminal" term',
            '    info "󰍛 CPU" cpu',
            '    info "󰢮 GPU" gpu',
            '    info "󰘚 Memory" memory',
        ]
    )
    if show_zfs:
        info_lines.append('    info "󰋊 Disk (ZFS)" disk')
    info_lines.extend(
        [
            "    info cols",
            "}",
            "",
            f"# DETech Active Palette Accent: {palette['accent']}",
            'title_fqdn="off"',
            'kernel_shorthand="on"',
            'distro_shorthand="off"',
            'os_arch="on"',
            'uptime_shorthand="tiny"',
            'memory_percent="on"',
            'memory_unit="gib"',
            'package_managers="on"',
            'shell_path="off"',
            'shell_version="on"',
            'speed_type="bios_limit"',
            'speed_shorthand="on"',
            'cpu_brand="on"',
            'cpu_speed="on"',
            'cpu_cores="logical"',
            'cpu_temp="C"',
            'gpu_brand="on"',
            'gpu_type="all"',
            'disk_show=("/")',
            'disk_subtitle="mount"',
            'disk_percent="on"',
            'colors=(1 7 4 1 3 7)',
            'bold="on"',
            'underline_enabled="on"',
            'underline_char="─"',
            'separator=" ❯"',
            'block_range=(0 15)',
            'color_blocks="on"',
            'block_width=3',
            'block_height=1',
            'col_offset="auto"',
            'bar_char_elapsed="━"',
            'bar_char_total="─"',
            'bar_border="on"',
            'bar_length=15',
            'bar_color_elapsed="distro"',
            'bar_color_total="distro"',
            'image_backend="ascii"',
            'image_source="auto"',
            f'ascii_distro="{ascii_distro}"',
            'ascii_colors=(1 7 3)',
            'ascii_bold="on"',
            'gap=3',
        ]
    )
    return (
        "# DETech FreeBSD Neofetch Configuration\n"
        f"# Theme: {theme_name} | Accent: {palette['accent']}\n\n"
        + "\n".join(info_lines)
        + "\n"
    )


def render_shell_init_sh(context: dict[str, Any], config_root: Path) -> str:
    """Render POSIX/Zsh/Bash startup script that runs Neofetch and initializes Starship."""
    cfg = context.get("config", {})
    term_info = cfg.get("terminal_info", {})
    enable_neofetch = bool(term_info.get("enable_neofetch", True))
    neofetch_conf = config_root / "neofetch" / "config.conf"
    starship_conf = config_root / "starship.toml"

    lines = [
        "# DETech Interactive Shell Initialization (Zsh / Bash / FreeBSD sh)",
        "# Source this file in ~/.zshrc or ~/.bashrc: [ -f ~/.config/detech/shell-init.sh ] && . ~/.config/detech/shell-init.sh",
        "",
        'case ":$PATH:" in',
        '    *":$HOME/.local/bin:"*) ;;',
        '    *) export PATH="$HOME/.local/bin:$HOME/bin:$PATH" ;;',
        "esac",
        "",
        f'export STARSHIP_CONFIG="{starship_conf}"',
        f'export DETECH_NEOFETCH="{"1" if enable_neofetch else "0"}"',
        "",
        "# Auto-display FreeBSD system information via Neofetch in interactive terminals",
        'case "$-" in',
        "    *i*)",
        '        if [ "$DETECH_NEOFETCH" = "1" ] && [ -z "${DETECH_NEOFETCH_SHOWN:-}" ]; then',
        '            export DETECH_NEOFETCH_SHOWN=1',
        "            if command -v neofetch >/dev/null 2>&1; then",
        f'                neofetch --config "{neofetch_conf}"',
        "            elif command -v fastfetch >/dev/null 2>&1; then",
        "                fastfetch",
        "            fi",
        "        fi",
        "        if command -v starship >/dev/null 2>&1; then",
        '            if [ -n "${ZSH_VERSION:-}" ]; then',
        '                eval "$(starship init zsh)"',
        '            elif [ -n "${BASH_VERSION:-}" ]; then',
        '                eval "$(starship init bash)"',
        "            fi",
        "        fi",
        "        ;;",
        "esac",
    ]
    return "\n".join(lines) + "\n"


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


def render_starship_toml(spec: dict[str, Any], palette: dict[str, str]) -> str:
    """Render a complete `starship.toml` configuration for the given preset blueprint and palette."""
    preset_id = spec.get("id", "tokyo-pill")
    add_nl = "true" if spec.get("add_newline", True) else "false"
    fmt = spec.get("format", "$directory$git_branch$character").replace("\n", "\\n")
    rfmt = spec.get("right_format", "")

    dir_style = spec.get("directory_style", "bold fg:accent")
    dir_format = spec.get("directory_format", "[$path]($style)[$read_only]($read_only_style) ")
    git_branch_style = spec.get("git_branch_style", "fg:accent_alt")
    git_branch_format = spec.get("git_branch_format", "[$symbol$branch]($style) ")

    starship_lines = [
        f"# DETech Starship Prompt — Preset: {spec.get('name', preset_id)} ({preset_id})",
        f"# Preview: {spec.get('preview', '')}",
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
            "[os]",
            "disabled = false",
            'style = "bold fg:accent"',
            "",
            "[os.symbols]",
            'FreeBSD = " "',
            "",
            "[username]",
            "show_always = true",
            'style_user = "bold fg:accent_alt"',
            'style_root = "bold fg:urgent"',
            'format = "[$user]($style)"',
            "",
            "[hostname]",
            "ssh_only = false",
            'style = "bold fg:accent"',
            'format = "[$hostname]($style)"',
            "",
            "[directory]",
            "truncation_length = 3",
            'truncation_symbol = "…/"',
            f'style = "{dir_style}"',
            f'format = "{dir_format}"',
            'read_only = " 󰌾"',
            'read_only_style = "fg:urgent"',
            "",
            "[git_branch]",
            'symbol = " "',
            f'style = "{git_branch_style}"',
            f'format = "{git_branch_format}"',
            "",
            "[git_status]",
            'style = "fg:warning"',
            'format = "([$all_status$ahead_behind]($style))"',
            "",
            "[cmd_duration]",
            "min_time = 500",
            'format = "[󱎫 $duration](fg:warning) "',
            "",
            "[jobs]",
            'symbol = "✦ "',
            'style = "bold fg:accent_alt"',
            "",
            "[time]",
            "disabled = false",
            'time_format = "%H:%M"',
            'format = "[ $time](fg:fg_muted)"',
            "",
            "[python]",
            'symbol = " "',
            'style = "fg:accent_alt"',
            'format = "[${symbol}${version} ]($style)"',
            "",
            "[rust]",
            'symbol = " "',
            'style = "fg:warning"',
            'format = "[${symbol}${version} ]($style)"',
            "",
            "[golang]",
            'symbol = " "',
            'style = "fg:accent"',
            'format = "[${symbol}${version} ]($style)"',
            "",
            "[nodejs]",
            'symbol = " "',
            'style = "fg:success"',
            'format = "[${symbol}${version} ]($style)"',
            "",
            "[c]",
            'symbol = " "',
            'style = "fg:fg_secondary"',
            'format = "[${symbol}${version} ]($style)"',
            "",
            "[lua]",
            'symbol = " "',
            'style = "fg:accent_alt"',
            'format = "[${symbol}${version} ]($style)"',
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
    for idx in range(16):
        key = f"color{idx}"
        if key in palette:
            starship_lines.append(f'{key} = "{palette[key]}"')

    return "\n".join(starship_lines) + "\n"


def generate_terminal_and_shell_configs(
    context: dict[str, Any],
    palette: dict[str, str],
    fonts: dict[str, Any],
    config_root: Path,
) -> list[Path]:
    """Generate `kitty/kitty.conf`, `kitty/detech-theme.conf`, `starship.toml`, and all 15 Starship presets."""
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
        "symbol_map U+23FB-U+23FE,U+2B58,U+E200-U+E2A9,U+E0A0-U+E0A3,U+E0B0-U+E0BF,U+E0C0-U+E0C8,U+E0CC-U+E0CF,U+E0D0-U+E0D2,U+E0D4,U+E700-U+E7C5,U+F000-U+F2E0,U+2665,U+26A1,U+F400-U+F4A9,U+F27C,U+F300-U+F372,U+F0001-U+F1AF0 Symbols Nerd Font Mono",
        "include detech-theme.conf",
    ]
    kitty_conf.write_text("\n".join(kitty_lines) + "\n", encoding="utf-8")
    written.append(kitty_conf)

    # 2. Pre-compile all 15 Starship prompt presets into `starship/presets/<id>.toml`
    starship_presets_dir = config_root / "starship" / "presets"
    starship_presets_dir.mkdir(parents=True, exist_ok=True)
    for item in list_starship_prompts():
        pid = item["id"]
        p_path = starship_presets_dir / f"{pid}.toml"
        p_path.write_text(render_starship_toml(item, palette), encoding="utf-8")
        written.append(p_path)

    # 3. Active `starship.toml`
    appearance = context.get("config", {}).get("appearance", {})
    preset_id = appearance.get("starship_preset", "tokyo-pill")
    active_spec = get_starship_prompt(preset_id)

    starship_path = config_root / "starship.toml"
    starship_path.write_text(render_starship_toml(active_spec, palette), encoding="utf-8")
    written.append(starship_path)

    # 4. Neofetch configuration (`neofetch/config.conf`) & Shell Startup hook (`detech/shell-init.sh`)
    neofetch_dir = config_root / "neofetch"
    neofetch_dir.mkdir(parents=True, exist_ok=True)
    neofetch_conf_path = neofetch_dir / "config.conf"
    neofetch_conf_path.write_text(render_neofetch_conf(context, palette, fonts), encoding="utf-8")
    written.append(neofetch_conf_path)

    detech_dir = config_root / "detech"
    detech_dir.mkdir(parents=True, exist_ok=True)
    shell_init_path = detech_dir / "shell-init.sh"
    shell_init_path.write_text(render_shell_init_sh(context, config_root), encoding="utf-8")
    written.append(shell_init_path)

    return written
