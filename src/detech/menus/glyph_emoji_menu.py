"""Rofi Nerd Font Glyph, Symbol, and Emoji Picker (`SUPER + .` or `detech menu glyphs`)."""

from __future__ import annotations

import shutil
import subprocess

from detech.menus.rofi_runner import run_rofi_dmenu

GLYPH_EMOJI_CATALOG: list[tuple[str, str, str]] = [
    ("", "FreeBSD Daemon (Beastie)", "nerd-os"),
    ("󰣠", "Hyprland Droplet", "nerd-wm"),
    ("", "Terminal Prompt", "nerd-dev"),
    ("", "Shell Console", "nerd-dev"),
    ("", "Git Branch", "nerd-git"),
    ("󰂄", "Battery Charging", "nerd-hw"),
    ("󰕾", "Audio Speaker High", "nerd-hw"),
    ("󰝟", "Audio Muted", "nerd-hw"),
    ("󰃠", "Brightness Sun", "nerd-hw"),
    ("󰔎", "Theme Palette", "nerd-ui"),
    ("󰸉", "Wallpaper Image", "nerd-ui"),
    ("󰛖", "Font Typography", "nerd-ui"),
    ("", "Folder Directory", "nerd-files"),
    ("", "Lock Security", "nerd-sec"),
    ("", "Rocket Launch", "nerd-misc"),
    ("λ", "Greek Lambda", "symbol"),
    ("❯", "Heavy Right Angle Prompt", "symbol"),
    ("⟶", "Long Right Arrow", "symbol"),
    ("🔥", "Fire Flame", "emoji"),
    ("⚡", "High Voltage Lightning", "emoji"),
    ("🚀", "Rocket Ship", "emoji"),
    ("✨", "Sparkles", "emoji"),
    ("🦀", "Crab / Rust", "emoji"),
    ("🐍", "Snake / Python", "emoji"),
    ("🌙", "Crescent Moon / Lua", "emoji"),
    ("😈", "Smiling Devil / BSD", "emoji"),
    ("✅", "Check Mark Button", "emoji"),
    ("❌", "Cross Mark", "emoji"),
]


def format_glyph_entries() -> list[dict[str, str]]:
    """Return formatted entries for the Rofi glyph & emoji picker."""
    items: list[dict[str, str]] = []
    for char, name, category in GLYPH_EMOJI_CATALOG:
        label = f"{char}   {name:<30} [{category}]"
        items.append({"char": char, "name": name, "category": category, "label": label})
    return items


def copy_to_wayland_clipboard(text: str) -> bool:
    """Copy string to Wayland clipboard via `wl-copy`."""
    if not shutil.which("wl-copy"):
        return False
    proc = subprocess.run(["wl-copy", text], check=False)
    return proc.returncode == 0


def open_glyph_menu() -> str | None:
    """Open Rofi Glyph & Emoji Picker and copy selection to clipboard."""
    items = format_glyph_entries()
    chosen = run_rofi_dmenu(
        [it["label"] for it in items],
        prompt="󰞅  Glyphs & Emoji",
        mesg="Select a Nerd Font glyph, symbol, or emoji to copy to Wayland clipboard (wl-copy)",
    )
    if not chosen:
        return None

    for it in items:
        if it["label"] == chosen:
            copy_to_wayland_clipboard(it["char"])
            return it["char"]
    return None
