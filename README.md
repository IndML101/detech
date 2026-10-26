# DETech — Desktop Environment Technology for FreeBSD

**DETech** is a minimalist, keyboard-friendly, modular desktop environment built around the **Hypr ecosystem** (`Hyprland`, `hypridle`, `hyprlock`, `hyprpaper`, and official Hyprland plugins) specifically engineered for **FreeBSD**.

Users configure their entire desktop through clean, declarative **Lua configuration files** (`~/.config/detech/*.lua`), while the **DETech Python Engine (`detech`)** compiles them into native configs, manages dynamic wallpaper color extraction with thumbnail previews, synchronizes Nerd Fonts and icon packs system-wide, themes the **Ly TUI Display Manager**, and powers an interactive suite of **Rofi pickers**.

---

## Key Features

- **Ly TUI Display & Login Manager Integration**:
  - First-class FreeBSD console integration running on `ttyv1` via `/usr/libexec/getty Ly` and `/usr/local/bin/ly_wrapper`.
  - Themed `config.ini` with 32-bit hex colors (`0xSSRRGGBB`) synchronized live with the active DETech theme.
  - Interactive TUI animations (`matrix`, `doom`, `colormix`, `gameoflife`) and big clock (`en`, `fa`).
  - Wayland session entry (`/usr/local/share/wayland-sessions/detech.desktop`) and `detech session` startup pipeline.
- **FreeBSD-Native Hardware & OS Stack**:
  - Zero Linux hardcoding. First-class support for FreeBSD `/usr/sbin/mixer` (plus PipeWire/PulseAudio fallback), `/usr/bin/backlight`, `sysctl hw.acpi.battery` & `hw.acpi.thermal`, `vm.loadavg`, `hw.physmem`, `zpool` status, `acpiconf`, `seatd`/`consolekit2`, `doas`, and FreeBSD `pkg`.
- **Hybrid Color Engine & Dynamic Wallpaper Extraction**:
  - Curated palettes from **10 dark theme packs** or dynamic 16-color ANSI + UI surface extraction directly from any wallpaper image.
  - Full **GTK-2/3/4, Qt5ct/Qt6ct, Kvantum SVG/kvconfig, and Dunst** asset bundle generation.
  - Wallpaper picker (`SUPER + SHIFT + W`) with **64px image thumbnail previews** inside Rofi.
- **Rich Waybar Widget Suite, Notifications & System Tray**:
  - **Weather (`custom/weather`)**: Auto-detects location via `wttr.in` (with optional `location` & `units` overrides), caches locally, and opens a 3-day forecast popup (`SUPER + M`).
  - **Interactive Calendar (`custom/calendar` & `clock`)**: Pango-highlighted month grid in tooltip + interactive Rofi month-navigation calendar (`SUPER + C`).
  - **Notifications & Do Not Disturb (`custom/dnd` / `custom/notifications`)**: Unread/history badge count from `dunstctl`, recent notification history in tooltip, interactive **Rofi Notification Center** (`SUPER + O`), and DND toggle (`SUPER + SHIFT + N`).
  - **System Tray (`tray`)**: Enabled across all 15 Waybar layouts with passive item support and dynamic theme-matched context menu CSS (`#tray menu`).
  - **FreeBSD Network & Wi-Fi (`custom/bsd-net`)**: Queries FreeBSD `ifconfig` for active Wi-Fi SSID (`wlan0`) or Ethernet (`em0`) and IPv4 address. Clicking opens the interactive **Rofi Wi-Fi Picker** (`SUPER + I`) to scan and connect to available networks.
  - **FreeBSD Bluetooth Manager (`custom/bsd-bluetooth`)**: Waybar status icon and interactive **Rofi Bluetooth Manager** (`SUPER + U`) with inquiry discovery and pairing wizard (`bluetooth-config scan`).
  - **MPRIS Media Player (`custom/media`)**: Displays `playerctl` Now Playing artist/title with click to play/pause and scroll for next/previous track.
  - **FreeBSD Kernel & Uptime (`custom/bsd-uptime`)**: Queries `sysctl kern.boottime` & `kern.osrelease`, launching `detech fetch` on click.
  - **Clipboard Manager (`custom/clipboard`)**: Displays `cliphist` item count and launches the Rofi clipboard history picker (`SUPER + Y`).
  - **FreeBSD Telemetry**: ACPI battery percentage and remaining time, CPU temperature, system load average, memory usage, and ZFS pool health.
- **Modular Presets Library**:
  - **15 Waybar Layouts**: Switch among floating island pills, docks, vertical sidebars, retro boxes, and telemetry bars.
  - **15 Rofi App Drawer Layouts**: Grid cards, spotlight minimal, sidebars, fullscreen launchpad, HUDs, and category tabs.
  - **15 Starship Prompt Presets**: Tokyo pill, minimal lambda, BSD devil, powerlines, git status, and clean prompts.
  - **6 Official Hyprland Plugin Presets**: Hyprexpo workspace overview, Hyprbars titlebars, Hyprtrails motion trails, Hyprwinwrap desktop widgets, and `csgo-vulkan-fix`.
  - **4 Hyprlock Screen Lock Layouts**: Minimal clock, BSD fortress, HyDE card, and Ryoku zen.
- **System-Wide Icon Themes**:
  - 12 curated icon packs (`Papirus-Dark`, `Papirus-Light`, `Papirus`, `Tela-circle-dark`, `Tela-circle`, `Catppuccin-SE`, `Gruvbox-Plus-Dark`, `TokyoNight-SE`, `Nordzy-dark`, `Qogir-dark`, `Breeze-Dark`, `Numix-Circle`, `Adwaita`) plus automatic discovery of custom icon packs in `/usr/local/share/icons` and `~/.local/share/icons`.
- **Nerd Fonts Manager & Installer**:
  - Built-in catalog of 16+ Nerd Fonts with `fc-list` discovery and one-click downloader/installer into `~/.local/share/fonts/NerdFonts/`.
  - Updates font family and sizes simultaneously across Kitty, Waybar, Rofi, Hyprlock, Dunst, GTK, and Qt.
- **Neofetch Terminal System Info & Shell Hook**:
  - Themed FreeBSD `neofetch/config.conf` displaying FreeBSD Beastie ASCII, kernel, uptime, ZFS root pool, active DETech theme, icon theme, presets, and Nerd Font.
  - Interactive shell startup hook (`detech/shell-init.sh`) and `detech fetch` CLI command.
- **Declarative Lua Configuration**:
  - Configure general settings, terminal info, fonts, appearance, keyboard shortcuts, monitors, window rules, Hyprland plugins, widgets, and FreeBSD hardware backends in Lua (`~/.config/detech/*.lua`).

---

## Quick Start (FreeBSD)

### 1. Bootstrap Dependencies & Configuration

Run the idempotent FreeBSD setup script:
```sh
# Installs packages (hyprland, waybar, rofi, kitty, starship, ly, etc.) and seeds ~/.config/detech/
sh scripts/install-freebsd.sh
```

### 2. Configure Ly Login Manager (Optional but Recommended)

Configure Ly as your system console display manager on `ttyv1` with live DETech theme syncing:
```sh
sudo sh scripts/setup-ly.sh
```

### 3. Launching DETech

- **Via Ly Login Manager**: Reboot or switch to `ttyv1` (`Ctrl + Alt + F2`), select the **DETech** session from the session list, enter your password, and press Enter.
- **From Shell Console**:
  ```sh
  detech session
  ```
  *(Compiles your latest Lua configurations and launches Hyprland.)*

### 4. Basic CLI Management

```sh
# Inspect current DETech configuration, active theme, and hardware state
detech status

# Display FreeBSD Beastie terminal info
detech fetch

# Compile Lua configs and apply live daemon reload
detech apply

# Switch themes, layouts, or fonts instantly
detech set theme bsd-crimson
detech set waybar island-top
detech set rofi grid-cards
detech set starship tokyo-pill
detech set icon Papirus-Dark
detech set font "JetBrainsMono Nerd Font" --size 11
```

---

## Keyboard Shortcuts Reference

All shortcuts can be searched and executed directly via the **Keybind Search & Runner** (`SUPER + /`).

### Launchers & Menus
| Shortcut | Action | Description |
| :--- | :--- | :--- |
| `SUPER + Return` | `kitty` | Launch Kitty Terminal |
| `SUPER + B` | `firefox` | Launch Web Browser |
| `SUPER + N` | `thunar` | Launch Graphical File Manager |
| `SUPER + D` | `detech menu apps` | Open Rofi App Drawer (15 switchable layouts) |
| `SUPER + /` | `detech menu keybinds` | **Search & Run any Keyboard Shortcut** |
| `SUPER + E` | `detech menu files` | Rofi File Browser |
| `SUPER + S` | `detech menu software` | FreeBSD `pkg` Software Picker |
| `SUPER + .` | `detech menu glyphs` | Emoji, NerdFont Glyph & Symbol Picker |

### Theme & Layout Switchers
| Shortcut | Action | Description |
| :--- | :--- | :--- |
| `SUPER + SHIFT + T` | `detech menu themes` | Switch System Theme (10 dark themes) |
| `SUPER + SHIFT + W` | `detech menu wallpapers` | Wallpaper Picker (with 64px icon previews & color sync) |
| `SUPER + SHIFT + F` | `detech menu fonts` | Nerd Fonts Picker & Installer |
| `SUPER + SHIFT + I` | `detech menu icons` | Icon Theme Picker |
| `SUPER + SHIFT + C` | `detech menu colors` | Color Scheme & Dynamic Extraction Mode Picker |
| `SUPER + SHIFT + B` | `detech menu waybar` | Switch Waybar Layout (15 presets) |
| `SUPER + SHIFT + R` | `detech menu rofi-layout` | Switch Rofi App Drawer Layout (15 presets) |
| `SUPER + SHIFT + P` | `detech menu starship` | Switch Starship Prompt (15 presets) |
| `SUPER + SHIFT + G` | `detech menu plugins` | Switch Hyprland Plugin Preset (6 presets) |
| `SUPER + SHIFT + L` | `detech menu hyprlock` | Switch Hyprlock Screen Lock Theme (14 presets) |

### Widgets & Notification Popups
| Shortcut | Action | Description |
| :--- | :--- | :--- |
| `SUPER + C` | `detech menu calendar` | Interactive Monthly Calendar |
| `SUPER + M` | `detech menu weather` | Live Weather Forecast Popup (`wttr.in`) |
| `SUPER + Y` | `detech menu clipboard` | Clipboard History Picker (`cliphist`) |
| `SUPER + O` | `detech menu notifications` | Dunst Notification Center |
| `SUPER + SHIFT + N` | `detech bsd widgets dnd toggle` | Toggle Do Not Disturb |

### Window Management & Workspaces
| Shortcut | Action | Description |
| :--- | :--- | :--- |
| `SUPER + Q` | `killactive` | Close Active Window |
| `SUPER + V` | `togglefloating` | Toggle Floating Window |
| `SUPER + F` | `fullscreen` | Toggle Fullscreen Mode |
| `SUPER + P` | `pseudo` | Toggle Dwindle Pseudotile |
| `SUPER + J` | `layoutmsg togglesplit` | Toggle Window Split Direction |
| `SUPER + Left/Right/Up/Down` | `movefocus l/r/u/d` | Move Window Focus (Arrow Keys) |
| `SUPER + CTRL + H/J/K/L` | `movefocus l/d/u/r` | Move Window Focus (Vim Navigation) |
| `SUPER + 1..10` | `workspace 1..10` | Switch to Workspace 1 through 10 |
| `SUPER + SHIFT + 1..10` | `movetoworkspace 1..10` | Move Window to Workspace 1 through 10 |
| `SUPER + Tab` | `workspace e+1` | Cycle to Next Workspace |

### Session & FreeBSD Hardware Controls
| Shortcut | Action | Description |
| :--- | :--- | :--- |
| `SUPER + L` | `hyprlock` | Lock Screen via `hyprlock` |
| `SUPER + SHIFT + Escape` | `detech bsd power suspend` | Suspend FreeBSD System (`acpiconf -s 3`) |
| `SUPER + SHIFT + Q` | `exit` | Exit Hyprland Session |
| `XF86AudioRaiseVolume` | `detech bsd audio up 5` | Raise Audio Volume (`mixer` / `wpctl`) |
| `XF86AudioLowerVolume` | `detech bsd audio down 5` | Lower Audio Volume (`mixer` / `wpctl`) |
| `XF86AudioMute` | `detech bsd audio mute` | Toggle Audio Mute (`mixer` / `wpctl`) |
| `XF86MonBrightnessUp` | `detech bsd backlight up 5` | Increase Screen Brightness (`backlight`) |
| `XF86MonBrightnessDown` | `detech bsd backlight down 5` | Decrease Screen Brightness (`backlight`) |

---

## Preset Catalogs

### 1. Curated Dark Themes
All themes strictly follow dark mode aesthetics with high-contrast surfaces:
- `bsd-crimson`: FreeBSD daemon dark crimson red with ruby accents
- `ryoku-matcha`: Serene Everforest-inspired matcha green
- `hyde-catppuccin`: Soothing Mocha lavender and sapphire
- `tokyo-cyber`: Neon cyberpunk magenta, cyan, and deep midnight
- `nordic-frost`: Chilled Arctic blue and icy slate
- `gruvbox-material`: Warm retro dark groove with forest and amber accents
- `rose-pine-moon`: Elegant dusky rose, pine, and gold
- `kanagawa-wave`: Classical Japanese sumi ink, wave blue, and autumn red
- `dracula-pro`: High-contrast vampire dark with neon purple and pink
- `solarized-bsd`: Precision low-fatigue dark cyan, green, and deep navy

### 2. Waybar Layouts (15 Presets)
- `island-top`: Floating rounded pill segments at screen top
- `minimal-bar`: Ultra-thin, distraction-free edge-to-edge bar
- `dock-bottom`: macOS/HyDE bottom application dock paired with top status bar
- `vertical-left`: Space-saving vertical left screen bar
- `vertical-right`: Vertical right screen bar
- `split-wings`: Separated left and right island wings with empty center
- `cyber-angled`: Angular powerline cyberpunk edges
- `compact-center`: Centered floating HUD
- `dual-bar`: Dual top status and bottom taskbar
- `retro-box`: Chunky borders and vintage terminal frames
- `glass-full`: Full-width frosted glass blur bar
- `workspace-centric`: Minimalist focused workspace visualizer
- `capsules-dark`: Dark segmented capsule pills
- `zen-status`: Micro status indicator for maximum screen real estate
- `freebsd-telemetry`: Dense hardware telemetry monitor (ZFS, thermal, ACPI, load)

### 3. Rofi App Drawer Layouts (15 Presets)
- `grid-cards`: Icon grid layout (4x3) with large app tiles
- `spotlight-minimal`: Centered spotlight search bar
- `sidebar-left`: Full-height left slide-in drawer
- `sidebar-right`: Full-height right slide-in drawer
- `fullscreen-launchpad`: Fullscreen application launchpad
- `compact-list`: Ultra-compact vertical single-column list
- `dual-pane`: Dual-pane layout with category sidebar and item grid
- `floating-dock`: Compact floating launcher dock
- `cyber-hud`: Sci-fi cyberpunk HUD overlay
- `retro-terminal`: Vintage ASCII monospace launcher
- `banner-header`: Large graphical banner with quick-launch pills
- `pill-launcher`: Floating rounded pill prompt
- `category-tabs`: Tabbed launcher categorized by application type
- `mini-palette`: Micro command palette
- `hyde-classic`: Signature HyDE-style floating search drawer

### 4. Starship Prompts (15 Presets)
- `tokyo-pill`, `minimal-lambda`, `bsd-devil`, `gruv-ribbon`, `cyber-brackets`, `pure-clone`, `matrix-grid`, `compact-git`, `neon-arrow`, `monochrome-zen`, `boxed-tree`, `pastel-blocks`, `time-right`, `devops-status`, `ryoku-clean`.

### 5. Official Hyprland Plugin Presets
- `minimal-expo`: Workspace expo overview grid with 3-finger gesture support
- `window-bars`: Hyprbars titlebars with close, float, and maximize buttons
- `eye-candy`: Hyprexpo overview + smooth Hyprtrails motion trails + dual borders
- `desktop-widget`: Hyprwinwrap desktop widget layer
- `bsd-gamer`: Stretched Vulkan resolution fixes via `csgo-vulkan-fix`
- `vanilla-zero`: Core Hyprland compositor with zero plugins loaded

### 6. Hyprlock Screen Lock Layouts
- `minimal-clock`: Centered large digital clock with minimalist password box
- `bsd-fortress`: FreeBSD daemon workstation security card
- `hyde-card`: Sleek top-left clock card
- `ryoku-zen`: Calm, distraction-free minimalist lock screen

---

## CLI Command Reference (`detech`)

The `detech` command is your administrative interface for runtime inspection, compilation, and live updates:

```
detech <command> [options]

Commands:
  status               Show active configuration, themes, layouts, fonts, and login manager
                       Options: --json
  fetch                Display FreeBSD Beastie system information via themed Neofetch
  apply                Compile Lua configs into native configs and reload daemons
                       Options: --no-reload, --output-dir <path>
  session              Compile configurations and launch the DETech Hyprland session
  set <target> <value> Update a setting in state and recompile:
                       Targets: theme, waybar, rofi, starship, hyprlock, plugins, font,
                                icon, wallpaper, dynamic-colors, neofetch,
                                weather-location, weather-units
                       Options: --size <pt> (for fonts), --no-reload
  list <category>      List available options:
                       Categories: themes, waybar, rofi, starship, hyprlock, plugins,
                                   fonts, icons, keybinds, glyphs
  menu <menu_name>     Open an interactive Rofi picker:
                       Menus: apps, keybinds, themes, wallpapers, fonts, icons,
                              colors, waybar, rofi-layout, starship, hyprlock,
                              plugins, files, software, glyphs, calendar,
                              weather, clipboard, notifications
  bsd <subsystem>      FreeBSD hardware and telemetry controls:
                       Subsystems:
                         audio {up|down|mute|status} [step] [--json]
                         backlight {up|down|set|status} [step] [--json]
                         power {battery|thermal|load|memory|zfs|lock|suspend|reboot|poweroff} [--json]
                         pkg {updates|list|search} [query] [--json]
                         widgets {weather|calendar|network|media|dnd|uptime|clipboard} [--json]
```

---

## Repository Structure

```
DETech/
├── pyproject.toml              # Python package definition (console entry points)
├── README.md                   # Project overview, quick start & reference
├── LICENSE                     # Open source license (BSD-2-Clause)
├── docs/
│   ├── project-description.md              # Architectural vision & features
│   ├── architecture.md                     # Compilation pipeline & daemon hot-reloading
│   ├── implementation-plan.md              # Implementation status & component breakdown
│   ├── configuration-guide.md              # In-depth declarative Lua reference
│   └── installation-and-troubleshooting.md # FreeBSD prerequisites, drivers & troubleshooting
├── configs/
│   └── lua/
│       ├── config.lua          # Main desktop configuration (appearance, widgets, fonts)
│       ├── freebsd.lua         # FreeBSD hardware adapters & Ly login manager
│       ├── keybinds.lua        # Keyboard shortcuts & runner descriptions
│       ├── monitors.lua        # Display outputs, scaling, and resolutions
│       ├── plugins.lua         # Official Hyprland plugins configuration
│       └── rules.lua           # Window and layer rules (floating, opacity, blur)
├── presets/
│   ├── themes/                 # 10 Curated dark theme packs
│   ├── waybar/                 # 15 Switchable Waybar layouts & styles
│   ├── rofi/                   # 15 Switchable Rofi app drawer layouts
│   ├── starship/               # 15 Switchable Starship prompt presets
│   ├── hyprplugins/            # 6 Official Hyprland plugin presets
│   └── hyprlock/               # 14 Hyprlock screen lock layouts (10 theme-matched + 4 classic)
├── scripts/
│   ├── install-freebsd.sh      # FreeBSD dependency installer & setup script
│   └── setup-ly.sh             # Ly TUI login manager installer & FreeBSD console config
├── src/
│   └── detech/
│       ├── __init__.py
│       ├── cli.py              # CLI entry point (`detech`, `detech fetch`, `detech session`)
│       ├── core/               # Lua loader, compiler, color engine, font manager, state
│       ├── freebsd/            # Native FreeBSD adapters (audio, backlight, power, pkg, widgets)
│       ├── generators/         # Native emitters (hypr, waybar, rofi, terminal, gtk/qt, ly)
│       └── menus/              # Rofi interactive picker suite & widget popups
└── tests/                      # Automated unit and integration test suite
```

---

## Documentation Links

For further details, consult the documentation in `docs/`:
- [Architecture Guide](docs/architecture.md) — Compilation pipeline, color quantization, and daemon synchronization.
- [Configuration Guide](docs/configuration-guide.md) — Comprehensive reference for every setting in `configs/lua/*.lua`.
- [Installation & Troubleshooting Guide](docs/installation-and-troubleshooting.md) — FreeBSD prerequisites, graphics drivers, and solutions to common issues.
- [Project Description](docs/project-description.md) — Core principles and feature set.
- [Implementation Status](docs/implementation-plan.md) — Implementation verification and milestones.
