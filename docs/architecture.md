# DETech Architecture Guide

## Overview

DETech separates **user intent** (written in declarative Lua tables) from **tool-specific configuration syntax** (Hyprlang, Waybar JSONC/CSS, Rofi RASI, Kitty conf, Starship TOML, GTK/Qt INI/CSS).

## Compilation & Hot-Reload Pipeline

1. **Input Merging**:
   - Reads base Lua files from `~/.config/detech/` (falling back to repository `configs/lua/`).
   - Overlays runtime overrides stored in `~/.local/state/detech/state.json` (modified by Rofi menus or `detech set ...`).
2. **Color Resolution (`color_engine.py`)**:
   - Loads the base palette from `presets/themes/<active_theme>/theme.lua`.
   - If `dynamic_wallpaper_colors = true` and a wallpaper image is set, extracts dominant/accent colors from the image and synthesizes a balanced 16-color ANSI + UI surface palette.
3. **Font Resolution (`font_manager.py`)**:
   - Resolves the active Nerd Font family (`mono`, `sans`) and sizes (`size`, `bar_size`, `rofi_size`, `lock_size`).
4. **Native Emission (`generators/*.py`)**:
   - Emits configs into `~/.config/hypr/`, `~/.config/waybar/`, `~/.config/rofi/`, `~/.config/kitty/`, `~/.config/starship.toml`, `~/.config/dunst/`, `~/.config/gtk-3.0/`, `~/.config/gtk-4.0/`, `~/.config/qt5ct/`, and `~/.config/qt6ct/`.
5. **Hot Reload (`compiler.py`)**:
   - Reloads Hyprland (`hyprctl reload`), updates wallpaper (`hyprctl hyprpaper`), reloads Waybar (`pkill -USR2 waybar`), reloads Kitty (`pkill -USR1 kitty`), and applies GTK settings via `gsettings`.
