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
        'export COLOR_SCHEME="prefer-dark"',
        "",
        "        # Synchronize terminal text color palette dynamically with DETech theme",
        f'        _term_colors="{config_root}/detech/term-colors.sh"',
        '        if [ -f "$_term_colors" ]; then',
        '            . "$_term_colors"',
        "        fi",
        "        unset _term_colors",
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
        '        if [ -n "${ZSH_VERSION:-}" ]; then',
        "            # Zsh Autocompletion & Additional Definitions",
        '            if [ -d "/usr/local/share/zsh-completions" ]; then',
        '                fpath=(/usr/local/share/zsh-completions $fpath)',
        '            elif [ -d "/usr/share/zsh/site-functions" ]; then',
        '                fpath=(/usr/share/zsh/site-functions $fpath)',
        "            fi",
        '            autoload -Uz compinit && compinit -C 2>/dev/null || autoload -Uz compinit && compinit',
        "",
        "            # Zsh Autosuggestions",
        "            for _asugg in \\",
        '                "/usr/local/share/zsh-autosuggestions/zsh-autosuggestions.zsh" \\',
        '                "/usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh" \\',
        '                "/usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh" \\',
        '                "$HOME/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh" \\',
        '                "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh"; do',
        '                if [ -f "$_asugg" ]; then',
        '                    . "$_asugg"',
        "                    break",
        "                fi",
        "            done",
        "            unset _asugg",
        "",
        "            # Zsh Syntax Highlighting (must be loaded after completions)",
        "            for _shl in \\",
        '                "/usr/local/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" \\',
        '                "/usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" \\',
        '                "/usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" \\',
        '                "$HOME/.zsh/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" \\',
        '                "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"; do',
        '                if [ -f "$_shl" ]; then',
        '                    . "$_shl"',
        "                    break",
        "                fi",
        "            done",
        "            unset _shl",
        "",
        "            if command -v starship >/dev/null 2>&1; then",
        '                eval "$(starship init zsh)"',
        "            fi",
        '        elif [ -n "${BASH_VERSION:-}" ]; then',
        "            if command -v starship >/dev/null 2>&1; then",
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


def render_kitty_theme(palette: dict[str, str]) -> str:
    """Render `kitty/detech-theme.conf` synchronized with the active theme color palette."""
    lines = [
        "# DETech Kitty Terminal Color Palette",
        f"background {palette['bg_primary']}",
        f"foreground {palette['fg_primary']}",
        f"cursor {palette['accent']}",
        f"cursor_text_color {palette['bg_primary']}",
        f"selection_background {palette['bg_tertiary']}",
        f"selection_foreground {palette['fg_primary']}",
        f"active_border_color {palette['accent']}",
        f"inactive_border_color {palette['border_inactive']}",
        f"active_tab_background {palette['accent']}",
        f"active_tab_foreground {palette['bg_primary']}",
        f"inactive_tab_background {palette['bg_secondary']}",
        f"inactive_tab_foreground {palette['fg_secondary']}",
        f"url_color {palette.get('accent_alt', palette['accent'])}",
        f"visual_bell_color {palette['accent']}",
    ]
    for idx in range(16):
        key = f"color{idx}"
        if key in palette:
            lines.append(f"{key} {palette[key]}")
    return "\n".join(lines) + "\n"


def render_alacritty_theme(palette: dict[str, str]) -> str:
    """Render `alacritty/detech-theme.toml` synchronized with active theme palette."""
    lines = [
        "# DETech Alacritty Color Palette",
        "[colors.primary]",
        f'background = "{palette["bg_primary"]}"',
        f'foreground = "{palette["fg_primary"]}"',
        "",
        "[colors.cursor]",
        f'text = "{palette["bg_primary"]}"',
        f'cursor = "{palette["accent"]}"',
        "",
        "[colors.selection]",
        f'text = "{palette["fg_primary"]}"',
        f'background = "{palette["bg_tertiary"]}"',
        "",
        "[colors.normal]",
        f'black   = "{palette.get("color0", palette["bg_primary"])}"',
        f'red     = "{palette.get("color1", "#e63946")}"',
        f'green   = "{palette.get("color2", "#52b788")}"',
        f'yellow  = "{palette.get("color3", "#f4a261")}"',
        f'blue    = "{palette.get("color4", "#457b9d")}"',
        f'magenta = "{palette.get("color5", "#c77dff")}"',
        f'cyan    = "{palette.get("color6", "#48cae4")}"',
        f'white   = "{palette.get("color7", palette["fg_primary"])}"',
        "",
        "[colors.bright]",
        f'black   = "{palette.get("color8", palette["bg_tertiary"])}"',
        f'red     = "{palette.get("color9", "#ff5c6a")}"',
        f'green   = "{palette.get("color10", "#74c69d")}"',
        f'yellow  = "{palette.get("color11", "#ffb703")}"',
        f'blue    = "{palette.get("color12", "#68a3c7")}"',
        f'magenta = "{palette.get("color13", "#d89eff")}"',
        f'cyan    = "{palette.get("color14", "#72ddf7")}"',
        f'white   = "{palette.get("color15", "#ffffff")}"',
    ]
    return "\n".join(lines) + "\n"


def render_alacritty_conf(fonts: dict[str, Any], general_shell: str | None = None) -> str:
    """Render `alacritty/alacritty.toml`."""
    lines = [
        "# DETech Alacritty Configuration",
        '[general]',
        'import = ["~/.config/alacritty/detech-theme.toml"]',
        "",
        "[font.normal]",
        f'family = "{fonts["mono"]}"',
        'style = "Regular"',
        "",
        "[font]",
        f'size = {fonts["size"]}.0',
        "",
        "[window]",
        "opacity = 0.92",
        "padding = { x = 10, y = 10 }",
    ]
    if general_shell:
        lines.extend([
            "",
            "[terminal.shell]",
            f'program = "{general_shell}"',
        ])
    return "\n".join(lines) + "\n"


def render_foot_theme(palette: dict[str, str]) -> str:
    """Render `foot/detech-theme.ini` synchronized with active theme palette."""
    lines = [
        "# DETech Foot Terminal Color Palette",
        "[colors]",
        f'background={palette["bg_primary"].lstrip("#")}',
        f'foreground={palette["fg_primary"].lstrip("#")}',
        f'regular0={palette.get("color0", palette["bg_primary"]).lstrip("#")}',
        f'regular1={palette.get("color1", "#e63946").lstrip("#")}',
        f'regular2={palette.get("color2", "#52b788").lstrip("#")}',
        f'regular3={palette.get("color3", "#f4a261").lstrip("#")}',
        f'regular4={palette.get("color4", "#457b9d").lstrip("#")}',
        f'regular5={palette.get("color5", "#c77dff").lstrip("#")}',
        f'regular6={palette.get("color6", "#48cae4").lstrip("#")}',
        f'regular7={palette.get("color7", palette["fg_primary"]).lstrip("#")}',
        f'bright0={palette.get("color8", palette["bg_tertiary"]).lstrip("#")}',
        f'bright1={palette.get("color9", "#ff5c6a").lstrip("#")}',
        f'bright2={palette.get("color10", "#74c69d").lstrip("#")}',
        f'bright3={palette.get("color11", "#ffb703").lstrip("#")}',
        f'bright4={palette.get("color12", "#68a3c7").lstrip("#")}',
        f'bright5={palette.get("color13", "#d89eff").lstrip("#")}',
        f'bright6={palette.get("color14", "#72ddf7").lstrip("#")}',
        f'bright7={palette.get("color15", "#ffffff").lstrip("#")}',
        f'selection-foreground={palette["fg_primary"].lstrip("#")}',
        f'selection-background={palette["bg_tertiary"].lstrip("#")}',
        f'urls={palette["accent"].lstrip("#")}',
    ]
    return "\n".join(lines) + "\n"


def render_foot_conf(fonts: dict[str, Any], general_shell: str | None = None) -> str:
    """Render `foot/foot.ini`."""
    lines = [
        "# DETech Foot Terminal Configuration",
        "include=detech-theme.ini",
        "",
        "[main]",
        f"font={fonts['mono']}:size={fonts['size']}",
        "pad=10x10",
    ]
    if general_shell:
        lines.append(f"shell={general_shell}")
    return "\n".join(lines) + "\n"


def render_term_colors_sh(palette: dict[str, str]) -> str:
    """Render POSIX shell script that emits OSC 4/10/11/12 escape sequences to set terminal colors."""
    lines = [
        "#!/bin/sh",
        "# DETech Terminal Color Palette Sync (OSC 4/10/11/12 Escape Sequences)",
        "# Applies theme text and ANSI colors dynamically to any running VT100 / Wayland terminal",
        "[ -t 1 ] || return 0 2>/dev/null || exit 0",
        "",
        f"printf '\\033]10;{palette['fg_primary']}\\007'",
        f"printf '\\033]11;{palette['bg_primary']}\\007'",
        f"printf '\\033]12;{palette['accent']}\\007'",
    ]
    for idx in range(16):
        key = f"color{idx}"
        if key in palette:
            lines.append(f"printf '\\033]4;{idx};{palette[key]}\\007'")
    return "\n".join(lines) + "\n"


def generate_terminal_and_shell_configs(
    context: dict[str, Any],
    palette: dict[str, str],
    fonts: dict[str, Any],
    config_root: Path,
) -> list[Path]:
    """Generate terminal themes (Kitty, Alacritty, Foot), Starship presets, Neofetch, and shell hooks."""
    written: list[Path] = []
    general_shell = context.get("config", {}).get("general", {}).get("shell", "zsh")

    # 1. Kitty configs
    kitty_dir = config_root / "kitty"
    kitty_dir.mkdir(parents=True, exist_ok=True)

    kitty_theme = kitty_dir / "detech-theme.conf"
    kitty_theme.write_text(render_kitty_theme(palette), encoding="utf-8")
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
    ]
    if general_shell:
        kitty_lines.append(f"shell            {general_shell}")
    kitty_lines.extend([
        "symbol_map U+23FB-U+23FE,U+2B58,U+E200-U+E2A9,U+E0A0-U+E0A3,U+E0B0-U+E0BF,U+E0C0-U+E0C8,U+E0CC-U+E0CF,U+E0D0-U+E0D2,U+E0D4,U+E700-U+E7C5,U+F000-U+F2E0,U+2665,U+26A1,U+F400-U+F4A9,U+F27C,U+F300-U+F372,U+F0001-U+F1AF0 Symbols Nerd Font Mono",
        "include detech-theme.conf",
    ])
    kitty_conf.write_text("\n".join(kitty_lines) + "\n", encoding="utf-8")
    written.append(kitty_conf)

    # 2. Alacritty configs
    alacritty_dir = config_root / "alacritty"
    alacritty_dir.mkdir(parents=True, exist_ok=True)
    alacritty_theme = alacritty_dir / "detech-theme.toml"
    alacritty_theme.write_text(render_alacritty_theme(palette), encoding="utf-8")
    written.append(alacritty_theme)

    alacritty_conf = alacritty_dir / "alacritty.toml"
    alacritty_conf.write_text(render_alacritty_conf(fonts, general_shell), encoding="utf-8")
    written.append(alacritty_conf)

    # 3. Foot configs
    foot_dir = config_root / "foot"
    foot_dir.mkdir(parents=True, exist_ok=True)
    foot_theme = foot_dir / "detech-theme.ini"
    foot_theme.write_text(render_foot_theme(palette), encoding="utf-8")
    written.append(foot_theme)

    foot_conf = foot_dir / "foot.ini"
    foot_conf.write_text(render_foot_conf(fonts, general_shell), encoding="utf-8")
    written.append(foot_conf)

    # 4. Dynamic Terminal Color Broadcaster (`detech/term-colors.sh`)
    detech_dir = config_root / "detech"
    detech_dir.mkdir(parents=True, exist_ok=True)
    term_colors_path = detech_dir / "term-colors.sh"
    term_colors_path.write_text(render_term_colors_sh(palette), encoding="utf-8")
    term_colors_path.chmod(0o755)
    written.append(term_colors_path)

    # 5. Pre-compile all 15 Starship prompt presets into `starship/presets/<id>.toml`
    starship_presets_dir = config_root / "starship" / "presets"
    starship_presets_dir.mkdir(parents=True, exist_ok=True)
    for item in list_starship_prompts():
        pid = item["id"]
        p_path = starship_presets_dir / f"{pid}.toml"
        p_path.write_text(render_starship_toml(item, palette), encoding="utf-8")
        written.append(p_path)

    # 6. Active `starship.toml`
    appearance = context.get("config", {}).get("appearance", {})
    preset_id = appearance.get("starship_preset", "tokyo-pill")
    active_spec = get_starship_prompt(preset_id)

    starship_path = config_root / "starship.toml"
    starship_path.write_text(render_starship_toml(active_spec, palette), encoding="utf-8")
    written.append(starship_path)

    # 7. Neofetch configuration (`neofetch/config.conf`) & Shell Startup hook (`detech/shell-init.sh`)
    neofetch_dir = config_root / "neofetch"
    neofetch_dir.mkdir(parents=True, exist_ok=True)
    neofetch_conf_path = neofetch_dir / "config.conf"
    neofetch_conf_path.write_text(render_neofetch_conf(context, palette, fonts), encoding="utf-8")
    written.append(neofetch_conf_path)

    shell_init_path = detech_dir / "shell-init.sh"
    shell_init_path.write_text(render_shell_init_sh(context, config_root), encoding="utf-8")
    written.append(shell_init_path)

    return written
