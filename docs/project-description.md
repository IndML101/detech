# DETech: Desktop Environment Technology for FreeBSD

**DETech** stands for **Desktop Environment Technology**, engineered specifically for **FreeBSD**.
The project provides a complete, keyboard-centric, modular desktop environment built around the **Hypr ecosystem** (`Hyprland`, `hypridle`, `hyprlock`, `hyprpaper`, and official Hyprland plugins), paired with a **Python Core Engine (`detech`)**, **declarative Lua configuration files**, and native FreeBSD hardware abstractions.

---

## Core Vision & Principles

1. **FreeBSD-Native, Zero Linux Hardcoding**: Eliminates Linux-isms (`systemd`, `/sys/class/power_supply`, `brightnessctl`, `nmcli`). Leverages native FreeBSD utilities (`mixer`, `/usr/bin/backlight`, `sysctl hw.acpi`, `acpiconf`, `ifconfig`, `seatd`, `doas`, and `pkg`).
2. **Hypr Ecosystem Integration**: Built strictly within the Hyprland ecosystem using official plugins (`hyprbars`, `hyprexpo`, `hyprtrails`, `hyprwinwrap`, `csgo-vulkan-fix`, `borders-plus-plus`) with Hyprland 0.56+ configuration syntax.
3. **Declarative Lua Configuration**: User customizability is the top priority. The desktop is configured through clean, human-friendly Lua tables in `~/.config/detech/*.lua`.
4. **Instant Theme & Layout Switching**: Switch among curated dark themes, 15 Waybar layouts, 15 Rofi layouts, 15 Starship prompts, and Nerd Fonts with live synchronization across all applications.
5. **Console & TUI Display Manager Integration**: Integrates the **Ly TUI Display Manager** (`ly`) on FreeBSD console (`ttyv1`), syncing 32-bit theme colors and TUI matrix/doom animations automatically.
6. **Minimalist & Keyboard-Friendly**: Comprehensive keybindings with fuzzy-searchable, executable Rofi pickers (`SUPER + /`).

---

## Key Features

- **Ly TUI Display & Login Manager**:
  - Native FreeBSD `/etc/gettytab` and `/etc/ttys` integration running on `ttyv1`.
  - Themed `config.ini` with 32-bit color mapping synced to the active DETech theme.
  - Interactive animations (`matrix`, `doom`, `colormix`, `gameoflife`) and big clock (`en`, `fa`).
  - Wayland session entry (`/usr/local/share/wayland-sessions/detech.desktop`) and `detech session` startup pipeline.
- **Declarative Lua Configs (`configs/lua/`)**:
  - `config.lua`: Terminal, browser, editor, notification daemon, fonts, appearance, and autostart daemons.
  - `freebsd.lua`: Hardware adapters (`mixer`, `/usr/bin/backlight`), ACPI power/sleep, `doas`/`sudo`, and `login_manager` settings.
  - `keybinds.lua`: Categorized shortcuts with descriptions powering the Rofi keybind search runner.
  - `plugins.lua`: Official Hyprland plugins configuration.
  - `monitors.lua`: Display outputs, resolution, refresh rates, positioning, and scaling.
  - `rules.lua`: Window and layer rules (floating, opacity, blur, workspace assignment).
- **Preset Catalog**:
  - **10 Curated Dark Themes**: `bsd-crimson`, `ryoku-matcha`, `hyde-catppuccin`, `tokyo-cyber`, `nordic-frost`, `gruvbox-material`, `rose-pine-moon`, `kanagawa-wave`, `dracula-pro`, `solarized-bsd`.
  - **15 Waybar Layouts**: `island-top`, `minimal-bar`, `dock-bottom`, `vertical-left`, `vertical-right`, `split-wings`, `cyber-angled`, `compact-center`, `dual-bar`, `retro-box`, `glass-full`, `workspace-centric`, `capsules-dark`, `zen-status`, `freebsd-telemetry`.
  - **15 Rofi App Drawer Layouts**: `grid-cards`, `spotlight-minimal`, `sidebar-left`, `sidebar-right`, `fullscreen-launchpad`, `compact-list`, `dual-pane`, `floating-dock`, `cyber-hud`, `retro-terminal`, `banner-header`, `pill-launcher`, `category-tabs`, `mini-palette`, `hyde-classic`.
  - **15 Starship Prompt Presets**: `tokyo-pill`, `minimal-lambda`, `bsd-devil`, `gruv-ribbon`, `cyber-brackets`, `pure-clone`, `matrix-grid`, `compact-git`, `neon-arrow`, `monochrome-zen`, `boxed-tree`, `pastel-blocks`, `time-right`, `devops-status`, `ryoku-clean`.
  - **6 Hyprland Plugin Presets**: `minimal-expo`, `window-bars`, `eye-candy`, `desktop-widget`, `bsd-gamer`, `vanilla-zero`.
  - **4 Hyprlock Screen Lock Layouts**: `minimal-clock`, `bsd-fortress`, `hyde-card`, `ryoku-zen`.
- **Hybrid Color Scheme & Dynamic Wallpaper Engine**:
  - Enforced dark mode palettes across all themes with high-contrast surfaces.
  - Wallpaper picker (`SUPER + SHIFT + W`) with 64px image thumbnail previews in Rofi.
  - Pure-Python color quantization extracting dominant chromatic tones from wallpapers into a 16-color ANSI + UI surface palette.
- **System-Wide Icon Themes**:
  - 12 curated icon packs plus automatic discovery of installed icon packs in `/usr/local/share/icons` and `~/.local/share/icons`.
  - Synced across GTK-2/3/4, Qt5/6, Rofi, Dunst, and Neofetch.
- **Nerd Fonts Manager**:
  - Curated catalog of 16+ Nerd Fonts with `fc-list` discovery and one-click installer.
  - Instant propagation across Kitty, Waybar, Rofi, Hyprlock, Dunst, GTK, and Qt.
- **Terminal System Info & Shell Hook**:
  - Themed Neofetch configuration (`neofetch/config.conf`) featuring FreeBSD Beastie ASCII art, ZFS root pool status, and active DETech theme details.
  - Shell startup hook (`detech/shell-init.sh`) and `detech fetch` CLI command.
- **Waybar Widget Suite & System Tray**:
  - Weather widget (`wttr.in`), interactive monthly calendar, Dunst Notification Center & Do Not Disturb toggle, FreeBSD network (`ifconfig`), MPRIS media player (`playerctl`), FreeBSD kernel & uptime (`sysctl kern.boottime`), clipboard history (`cliphist`), and System Tray across all 15 layouts.
- **Keyboard-Centric Rofi Interactive Suite**:
  - `SUPER + /` — Search and run any keyboard shortcut directly.
  - Dedicated pickers for themes, wallpapers, fonts, icons, color schemes, layouts, starship prompts, plugins, software (`pkg`), file browser, emojis/glyphs, calendar, weather, clipboard history, and notification center.

---

## Inspirations

- [HyDE](https://github.com/HyDE-Project/HyDE) — Modular theming, rich Rofi picker suite, and dynamic wallpaper color switching.
- [Ryoku](https://github.com/Ryoku-dev/ryoku) — Cohesive, declarative design and clean aesthetics.
- [ML4W](https://github.com/mylinuxforwork/dotfiles) — Practical Waybar widget suite and user settings workflow.
- [JAKooLit](https://github.com/JaKooLit/Hyprland-Dots) — Layout diversity and keybinding ergonomy.
- [end_4](https://github.com/end-4/dots-hyprland) — Modern Wayland visual polish.
