# DETech — Desktop Environment Technology for FreeBSD

**DETech** is a minimalist, keyboard-friendly, modular desktop environment built around the **Hypr ecosystem** (`Hyprland`, `hypridle`, `hyprlock`, `hyprpaper`, and official Hyprland plugins) specifically engineered for **FreeBSD**.

Users configure their entire desktop through clean, declarative **Lua configuration files** (`configs/lua/*.lua`), while the **DETech Python Engine (`detech`)** compiles them into native configs, manages dynamic wallpaper color extraction, switches Nerd Fonts system-wide, and powers an interactive suite of **Rofi pickers**.

---

## Key Features

- **FreeBSD-Native Hardware & OS Stack**: First-class support for FreeBSD `/usr/sbin/mixer` (plus PipeWire/PulseAudio), `/usr/bin/backlight`, `sysctl hw.acpi.battery` & `hw.acpi.thermal`, `acpiconf`, `seatd`/`consolekit2`, `doas`, and FreeBSD `pkg`.
- **Declarative Lua Configuration**: Configure general settings, fonts, appearance, keyboard shortcuts, monitors, window rules, Hyprland plugins, and FreeBSD hardware backends in Lua (`~/.config/detech/*.lua`).
- **Keyboard-Centric Rofi Picker Suite**:
  - `SUPER + /` — **Keybind Search & Runner** (fuzzy search and execute any shortcut directly)
  - `SUPER + D` — **Rofi App Drawer** (switchable between **15 layouts**)
  - `SUPER + SHIFT + T` — **Theme Picker** (switch curated themes with icons, wallpapers, lock screens, GTK/Qt schemes)
  - `SUPER + SHIFT + W` — **Wallpaper Picker** (with live system-wide color extraction & sync)
  - `SUPER + SHIFT + F` — **Nerd Fonts Picker & Installer** (switch or install Nerd Fonts across Kitty, Waybar, Rofi, Hyprlock, Dunst, GTK/Qt)
  - `SUPER + SHIFT + I` — **Icon Theme Picker**
  - `SUPER + SHIFT + C` — **Color Scheme & Dynamic Mode Picker**
  - `SUPER + SHIFT + B` — **Waybar Layout Switcher** (**15 layouts** included)
  - `SUPER + SHIFT + R` — **Rofi Layout Switcher** (**15 layouts** included)
  - `SUPER + SHIFT + P` — **Starship Prompt Switcher** (**15 prompts** included)
  - `SUPER + SHIFT + G` — **Hyprland Plugin Preset Switcher** (**6 presets** included)
  - `SUPER + S` — **FreeBSD `pkg` Software Picker**
  - `SUPER + E` — **Rofi File Browser**
  - `SUPER + .` — **Emoji, NerdFont Glyph & Symbol Picker**
- **Hybrid Color Engine**: Use curated palettes from **10 theme packs** (`bsd-crimson`, `ryoku-matcha`, `hyde-catppuccin`, `tokyo-cyber`, `nordic-frost`, `gruvbox-material`, `rose-pine-moon`, `kanagawa-wave`, `dracula-pro`, `solarized-bsd`) or dynamically generate 16-color + surface palettes from any wallpaper, with full **GTK-2/3/4, Qt5ct/Qt6ct, and Kvantum SVG/kvconfig asset bundle generation**.

---

## Quick Start (FreeBSD)

```sh
# 1. Bootstrap FreeBSD dependencies, seatd/dbus, and DETech configs
sh scripts/install-freebsd.sh

# 2. Check current DETech state and compile configs
detech status
detech apply

# 3. Switch presets from the CLI or via Rofi menus
detech set theme bsd-crimson
detech set waybar island-top
detech set rofi grid-cards
detech set starship tokyo-pill
detech set font "JetBrainsMono Nerd Font" --size 11
```

---

## Repository Structure

- `configs/lua/` — User-editable declarative Lua configurations (`config.lua`, `keybinds.lua`, `monitors.lua`, `rules.lua`, `plugins.lua`, `freebsd.lua`)
- `presets/` — Modular catalog of 10 themes, 15 Waybar layouts, 15 Rofi app drawer layouts, 15 Starship prompts, 6 Hyprland plugin presets, and Hyprlock layouts
- `src/detech/` — Python engine, Lua loader, hybrid color extractor, Nerd Font manager, FreeBSD hardware adapters, native config generators, and Rofi menus
- `scripts/install-freebsd.sh` — FreeBSD installer and setup script
- `docs/` — Project description, architecture specification, and implementation plan
- `tests/` — Automated `pytest` verification suite
