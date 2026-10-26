"""Native configuration generators for DETech."""

from detech.generators.gtk_qt_dunst import generate_gtk_qt_dunst_configs
from detech.generators.hyprland import generate_hypr_configs
from detech.generators.ly import generate_ly_configs
from detech.generators.rofi import generate_rofi_configs
from detech.generators.terminal_shell import generate_terminal_and_shell_configs
from detech.generators.waybar import generate_waybar_configs

__all__ = [
    "generate_gtk_qt_dunst_configs",
    "generate_hypr_configs",
    "generate_ly_configs",
    "generate_rofi_configs",
    "generate_terminal_and_shell_configs",
    "generate_waybar_configs",
]

