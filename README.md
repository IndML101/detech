# DETech — Desktop Environment Technology for FreeBSD

**DETech** is a minimalist, keyboard-friendly, modular desktop environment built around the **Hypr ecosystem** (`Hyprland`, `hypridle`, `hyprlock`, `hyprpaper`, and official Hyprland plugins) specifically engineered for **FreeBSD**.

Users configure their entire desktop through clean, declarative **Lua configuration files** (`configs/lua/*.lua`), while the **DETech Python Engine (`detech`)** compiles them into native configs, manages dynamic wallpaper color extraction, switches Nerd Fonts system-wide, and powers an interactive suite of **Rofi pickers**.

---

## Key Features

- **FreeBSD-Native Hardware & OS Stack**: First-class support for FreeBSD `/usr/sbin/mixer` (plus PipeWire/PulseAudio), `/usr/bin/backlight`, `sysctl hw.acpi.battery` & `hw.acpi.thermal`, `acpiconf`, `seatd`/`consolekit2`, `doas`, and FreeBSD `pkg`.
- **Neofetch Terminal System Info**: Generates a themed FreeBSD `neofetch/config.conf` (displaying FreeBSD Beastie ASCII, kernel, uptime, ZFS root pool, active DETech theme, icon theme, Waybar/Starship presets, and Nerd Font) and an interactive shell startup hook (`detech/shell-init.sh`) + `detech fetch` CLI command.
- **Rich Waybar Widget Suite, Notifications & System Tray**:
  - **Weather (`custom/weather`)**: Auto-detects location via `wttr.in` (with optional `location` & `units` overrides), caches locally, and opens a 3-day forecast popup (`SUPER + M`).
  - **Interactive Calendar (`custom/calendar` & `clock`)**: Pango-highlighted month grid in tooltip + interactive Rofi month-navigation calendar (`SUPER + C`).
  - **Notifications & Do Not Disturb (`custom/dnd` / `custom/notifications`)**: Displays unread/history badge count from `dunstctl`, recent notification history in tooltip, interactive **Rofi Notification Center** (`SUPER + O`, left-click), DND toggle (`SUPER + SHIFT + N`, right-click), and dismiss-all (middle-click).
  - **System Tray (`tray`)**: Enabled across all 15 Waybar layouts with passive item support and dynamic theme-matched context menu CSS (`#tray menu`).
  - **FreeBSD Network (`custom/bsd-net`)**: Queries FreeBSD `ifconfig` for active Wi-Fi SSID (`wlan0`) or Ethernet (`em0`) and IPv4 address.
  - **MPRIS Media Player (`custom/media`)**: Displays `playerctl` Now Playing artist/title with click to play/pause and scroll for next/previous track.
  - **FreeBSD Kernel & Uptime (`custom/bsd-uptime`)**: Queries `sysctl kern.boottime` & `kern.osrelease`, launching `detech fetch` on click.
  - **Clipboard Manager (`custom/clipboard`)**: Displays `cliphist` item count and launches the Rofi clipboard history picker (`SUPER + Y`).
- **System-Wide Icon Themes**: Includes 12 curated icon packs (`Papirus-Dark`, `Papirus-Light`, `Papirus`, `Tela-circle-dark`, `Tela-circle`, `Catppuccin-SE`, `Gruvbox-Plus-Dark`, `TokyoNight-SE`, `Nordzy-dark`, `Qogir-dark`, `Breeze-Dark`, `Numix-Circle`, `Adwaita`) plus automatic discovery of custom icon packs in `/usr/local/share/icons` and `~/.local/share/icons`, synced across GTK-2/3/4, Qt5/Qt6, Rofi, Dunst, and Neofetch.
- **Declarative Lua Configuration**: Configure general settings, terminal info, fonts, appearance, keyboard shortcuts, monitors, window rules, Hyprland plugins, widgets, and FreeBSD hardware backends in Lua (`~/.config/detech/*.lua`).
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
  - `SUPER + C` — **Interactive Rofi Calendar**
  - `SUPER + M` — **Weather Forecast Popup**
  - `SUPER + Y` — **Clipboard History Picker (`cliphist`)**
  - `SUPER + O` — **Rofi Notification Center (`dunstctl` history, pop, dismiss)**
  - `SUPER + SHIFT + N` — **Toggle Do Not Disturb (`dunst`)**
- **Hybrid Color Engine**: Use curated palettes from **10 theme packs** (`bsd-crimson`, `ryoku-matcha`, `hyde-catppuccin`, `tokyo-cyber`, `nordic-frost`, `gruvbox-material`, `rose-pine-moon`, `kanagawa-wave`, `dracula-pro`, `solarized-bsd`) or dynamically generate 16-color + surface palettes from any wallpaper, with full **GTK-2/3/4, Qt5ct/Qt6ct, and Kvantum SVG/kvconfig asset bundle generation**.

---

## Quick Start (FreeBSD)

```sh
# 1. Bootstrap FreeBSD dependencies, seatd/dbus, and DETech configs
sh scripts/install-freebsd.sh

# 2. Check current DETech state, display Neofetch system info, and compile configs
detech status
detech fetch
detech apply

# 3. Switch presets, icon themes, and widget settings from the CLI or via Rofi menus
detech set theme bsd-crimson
detech set waybar island-top
detech set rofi grid-cards
detech set starship tokyo-pill
detech set icon Papirus-Dark
detech set font "JetBrainsMono Nerd Font" --size 11
detech set neofetch true
detech set weather-location "San Francisco"
detech set weather-units m

# 4. List available themes, layouts, Nerd Fonts, or icon packs
detech list themes
detech list waybar
detech list icons
detech list fonts
```

---

## Repository Structure

- `configs/lua/` — User-editable declarative Lua configurations (`config.lua`, `keybinds.lua`, `monitors.lua`, `rules.lua`, `plugins.lua`, `freebsd.lua`)
- `presets/` — Modular catalog of 10 themes, 15 Waybar layouts, 15 Rofi app drawer layouts, 15 Starship prompts, 6 Hyprland plugin presets, and Hyprlock layouts
- `src/detech/` — Python engine, Lua loader, hybrid color extractor, Nerd Font manager, FreeBSD hardware adapters, native config generators, and Rofi menus
- `scripts/install-freebsd.sh` — FreeBSD installer and setup script
- `docs/` — Project description, architecture specification, and implementation plan
- `tests/` — Automated `pytest` verification suite
