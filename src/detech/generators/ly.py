"""Ly TUI Display Manager Configuration Generator for DETech on FreeBSD."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from detech.core.color_engine import hex_to_rgb


def color_to_ly_hex(hex_str: str, bold: bool = False, dim: bool = False) -> str:
    """Convert `#rrggbb` hex color string to Ly 32-bit `0xSSRRGGBB` format.

    Ly styling byte options:
    - 0x00: Normal
    - 0x01: Bold (TB_BOLD)
    - 0x80: Dim (TB_DIM)
    """
    try:
        r, g, b = hex_to_rgb(hex_str)
    except Exception:
        return "0x00FFFFFF"

    style = 0x00
    if bold:
        style |= 0x01
    if dim:
        style |= 0x80

    return f"0x{style:02X}{r:02X}{g:02X}{b:02X}"


def render_ly_config(
    context: dict[str, Any],
    palette: dict[str, str],
    fonts: dict[str, Any] | None = None,
) -> str:
    """Render a complete, themed Ly `config.ini` synchronized with the active DETech theme."""
    freebsd_cfg = context.get("freebsd", {})
    login_cfg = freebsd_cfg.get("login_manager", {})

    animation = login_cfg.get("animation", "matrix")
    animation_delay = int(login_cfg.get("animation_frame_delay", 5))
    animation_timeout = int(login_cfg.get("animation_timeout_sec", 0))
    bigclock = login_cfg.get("bigclock", "en")
    bigclock_12hr = "true" if login_cfg.get("bigclock_12hr", False) else "false"
    bigclock_seconds = "true" if login_cfg.get("bigclock_seconds", False) else "false"
    asterisk = login_cfg.get("asterisk", "*")
    blank_box = "true" if login_cfg.get("blank_box", True) else "false"
    hide_borders = "true" if login_cfg.get("hide_borders", False) else "false"
    save = "true" if login_cfg.get("save", True) else "false"
    clear_password = "true" if login_cfg.get("clear_password", true := True) else "false"
    box_title = login_cfg.get("box_title", "DETech Desktop Environment (FreeBSD)")

    # Color mapping from active palette
    bg_hex = palette.get("bg_primary", "#1e1e2e")
    fg_hex = palette.get("fg_primary", "#cdd6f4")
    accent_hex = palette.get("accent", "#89b4fa")
    border_hex = palette.get("border_active", accent_hex)
    urgent_hex = palette.get("urgent", "#f38ba8")
    subtext_hex = palette.get("fg_muted", "#6c7086")

    ly_bg = color_to_ly_hex(bg_hex)
    ly_fg = color_to_ly_hex(fg_hex)
    ly_border = color_to_ly_hex(border_hex, bold=True)
    ly_error_fg = color_to_ly_hex(urgent_hex, bold=True)
    ly_error_bg = color_to_ly_hex(bg_hex)

    # Animation color accents
    matrix_fg = color_to_ly_hex(accent_hex)
    colormix_1 = color_to_ly_hex(accent_hex)
    colormix_2 = color_to_ly_hex(palette.get("accent_alt", "#b4befe"))
    colormix_3 = color_to_ly_hex(subtext_hex)
    doom_top = color_to_ly_hex(urgent_hex)
    doom_mid = color_to_ly_hex(palette.get("warning", "#fab387"))
    doom_bot = color_to_ly_hex(fg_hex)
    gameoflife_fg = color_to_ly_hex(accent_hex)

    lines = [
        "# DETech Automated Ly Configuration (FreeBSD)",
        "# Generated automatically by DETech Compiler",
        "# Manual edits in configs/lua/freebsd.lua (login_manager table)",
        "",
        "# 24-bit True Color Mode",
        "full_color = true",
        "",
        "# Core Colors synced to DETech active theme",
        f"bg = {ly_bg}",
        f"fg = {ly_fg}",
        f"border_fg = {ly_border}",
        f"error_bg = {ly_error_bg}",
        f"error_fg = {ly_error_fg}",
        "",
        "# Visual Layout & Styling",
        f"blank_box = {blank_box}",
        f"hide_borders = {hide_borders}",
        f"box_title = {box_title}",
        f"asterisk = {asterisk}",
        f"clear_password = {clear_password}",
        "margin_box_h = 2",
        "margin_box_v = 1",
        "input_len = 34",
        "edge_margin = 0",
        "",
        "# Clock Settings",
        f"bigclock = {bigclock}",
        f"bigclock_12hr = {bigclock_12hr}",
        f"bigclock_seconds = {bigclock_seconds}",
        "",
        "# Background Animation",
        f"animation = {animation}",
        f"animation_frame_delay = {animation_delay}",
        f"animation_timeout_sec = {animation_timeout}",
        f"cmatrix_fg = {matrix_fg}",
        "cmatrix_head_col = 0x01FFFFFF",
        "cmatrix_min_codepoint = 0x21",
        "cmatrix_max_codepoint = 0x7B",
        f"colormix_col1 = {colormix_1}",
        f"colormix_col2 = {colormix_2}",
        f"colormix_col3 = {colormix_3}",
        f"doom_top_color = {doom_top}",
        f"doom_middle_color = {doom_mid}",
        f"doom_bottom_color = {doom_bot}",
        f"gameoflife_fg = {gameoflife_fg}",
        "",
        "# Session & User Preferences",
        f"save = {save}",
        "service_name = ly",
        "auto_login_service = ly-autologin",
        "waylandsessions = /usr/local/share/wayland-sessions",
        "xsessions = /usr/local/share/xsessions",
        "setup_cmd = /usr/local/etc/ly/setup.sh",
        "session_log = .local/state/ly-session.log",
        "",
        "# FreeBSD Power Controls",
        "shutdown_cmd = /sbin/shutdown -p now",
        "restart_cmd = /sbin/shutdown -r now",
        "brightness_up_cmd = /usr/bin/backlight + 10",
        "brightness_down_cmd = /usr/bin/backlight - 10",
        "brightness_up_key = F6",
        "brightness_down_key = F5",
        "shutdown_key = F1",
        "restart_key = F2",
        "sleep_key = F3",
        "",
    ]

    auto_user = login_cfg.get("auto_login_user")
    auto_session = login_cfg.get("auto_login_session")
    if auto_user and auto_session:
        lines.extend([
            f"auto_login_user = {auto_user}",
            f"auto_login_session = {auto_session}",
        ])
    else:
        lines.extend([
            "auto_login_user = null",
            "auto_login_session = null",
        ])

    return "\n".join(lines) + "\n"


def generate_ly_configs(
    context: dict[str, Any],
    palette: dict[str, str],
    fonts: dict[str, Any] | None,
    target_root: Path,
) -> list[Path]:
    """Generate Ly configuration files and synchronize with the system config if writeable."""
    written: list[Path] = []

    # 1. User config in ~/.config/detech/generated/ly/config.ini
    user_ly_dir = target_root / "detech" / "generated" / "ly"
    user_ly_dir.mkdir(parents=True, exist_ok=True)
    user_ly_conf = user_ly_dir / "config.ini"

    content = render_ly_config(context, palette, fonts)
    user_ly_conf.write_text(content, encoding="utf-8")
    written.append(user_ly_conf)

    # 2. Also write to target_root / "ly" / "config.ini" as fallback
    dot_ly_dir = target_root / "ly"
    dot_ly_dir.mkdir(parents=True, exist_ok=True)
    dot_ly_conf = dot_ly_dir / "config.ini"
    dot_ly_conf.write_text(content, encoding="utf-8")
    written.append(dot_ly_conf)

    # 3. If /usr/local/etc/ly/config.ini is writeable (or a symlink pointing to user path), sync it live!
    sys_ly_conf = Path("/usr/local/etc/ly/config.ini")
    try:
        if sys_ly_conf.is_symlink():
            # If it's a symlink pointing to our user config, writing to user_ly_conf already updated it!
            pass
        elif sys_ly_conf.exists() and os.access(sys_ly_conf, os.W_OK):
            sys_ly_conf.write_text(content, encoding="utf-8")
            written.append(sys_ly_conf)
    except Exception:
        pass

    return written
