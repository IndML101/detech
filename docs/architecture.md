# DETech Architecture Guide

## Overview

DETech separates **user intent** (written in declarative Lua tables) from **tool-specific configuration syntax** (Hyprlang, Waybar JSONC/CSS, Rofi RASI, Kitty conf, Neofetch conf, POSIX shell startup hooks, Starship TOML, Dunst rc, GTK-2/3/4 INI/CSS, Qt5ct/Qt6ct, and Kvantum SVG/kvconfig).

## Compilation & Hot-Reload Pipeline

1. **Input Merging (`lua_loader.py` & `state.py`)**:
   - Reads base Lua files from `~/.config/detech/` (falling back to repository `configs/lua/`).
   - Overlays runtime overrides stored in `~/.local/state/detech/state.json` (modified by Rofi menus or `detech set ...`, including theme, Waybar/Rofi/Starship/Hyprlock/plugin presets, icon theme, Nerd Font, `enable_neofetch`, and weather location/units).
2. **Color & Icon Resolution (`color_engine.py` & `theme_menu.py`)**:
   - Loads the base palette and default `icon_theme` from `presets/themes/<active_theme>/theme.lua`.
   - If `dynamic_wallpaper_colors = true` and a wallpaper image is set, extracts dominant/accent colors from the image and synthesizes a balanced 16-color ANSI + UI surface palette.
   - Auto-discovers installed icon packs in `/usr/local/share/icons`, `/usr/share/icons`, and `~/.local/share/icons` alongside 12 curated icon themes.
3. **Font Resolution (`font_manager.py`)**:
   - Resolves the active Nerd Font family (`mono`, `sans`) and sizes (`size`, `bar_size`, `rofi_size`, `lock_size`).
4. **Native Emission (`generators/*.py`)**:
   - `hyprland.py`: Emits `~/.config/hypr/{hyprland,detech-colors,detech-keybinds,detech-plugins,hyprlock,hypridle,hyprpaper}.conf`.
   - `waybar.py`: Emits `~/.config/waybar/{config.jsonc,style.css}` and pre-compiles all 15 switchable layouts (`layouts/*.jsonc`, `styles/*.css`) with FreeBSD telemetry, Weather, Calendar, Network, MPRIS Media, Dunst Notification Center/DND, Uptime/Kernel, Clipboard, and System Tray modules.
   - `rofi.py`: Emits `~/.config/rofi/{colors,fonts,config,menu}.rasi` and all 15 app drawer layouts (`layouts/*.rasi`) synced with the active `icon_theme`.
   - `terminal_shell.py`: Emits `~/.config/kitty/{kitty,detech-theme}.conf`, `~/.config/starship.toml` (plus all 15 presets in `starship/presets/*.toml`), `~/.config/neofetch/config.conf` (themed FreeBSD Beastie system info), and `~/.config/detech/shell-init.sh` (interactive terminal startup hook for Neofetch + Starship).
   - `gtk_qt_dunst.py`: Emits `~/.config/gtk-2.0/gtkrc`, `~/.config/gtk-3.0/{settings.ini,gtk.css}`, `~/.config/gtk-4.0/{settings.ini,gtk.css}`, `~/.config/qt5ct/`, `~/.config/qt6ct/`, `~/.config/Kvantum/DETech/DETech.{kvconfig,svg}`, and `~/.config/dunst/dunstrc` (with notification history, recursive icon lookup, and OSD progress bars).
5. **Hot Reload (`compiler.py`)**:
   - Reloads Hyprland (`hyprctl reload`), updates wallpaper (`hyprctl hyprpaper`), reloads Waybar (`pkill -USR2 waybar`), reloads Kitty (`pkill -USR1 kitty`), reloads Dunst (`dunstctl reload`), and applies GTK theme/icon/font settings via `gsettings`.

## FreeBSD Telemetry & Waybar Widget Layer (`src/detech/freebsd/`)

- **`power.py`**: Queries `sysctl hw.acpi.battery`, `hw.acpi.thermal`, `vm.loadavg`, `hw.physmem`/`vm.stats.vm`, and `zpool list`, plus session power actions (`acpiconf -s 3`, `shutdown`, `hyprlock`).
- **`audio.py` & `backlight.py`**: Wraps FreeBSD `/usr/sbin/mixer` (with `wpctl`/`pactl` auto-detection) and `/usr/bin/backlight`.
- **`pkg_manager.py`**: Wraps FreeBSD `/usr/sbin/pkg` for update checks, package search, and interactive installation.
- **`widgets.py` & `menus/widget_menus.py`**:
  - **Weather (`custom/weather`)**: Fetches and caches `wttr.in` JSON (`~/.cache/detech/weather_*.json`) with auto-IP geolocation or explicit city override, plus Rofi 3-day forecast popup (`detech menu weather`).
  - **Calendar (`custom/calendar` & `clock`)**: Pango-highlighted monthly calendar tooltip + interactive Rofi month navigator (`detech menu calendar`).
  - **Notifications & DND (`custom/dnd` / `custom/notifications`)**: Queries `dunstctl` for waiting/history counts and recent notification summaries, paired with the interactive Rofi Notification Center (`detech menu notifications`).
  - **Network (`custom/bsd-net`)**: Parses FreeBSD `ifconfig` for active Wi-Fi SSID (`wlan0`) or Ethernet (`em0`) and IPv4 address.
  - **Media (`custom/media`)**: Queries and controls MPRIS playback via `playerctl`.
  - **Uptime & Kernel (`custom/bsd-uptime`)**: Parses `sysctl kern.boottime` and `kern.osrelease`.
  - **Clipboard (`custom/clipboard`)**: Integrates with `cliphist` and `wl-copy` (`detech menu clipboard`).
