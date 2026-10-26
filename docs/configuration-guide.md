# DETech Configuration Guide

This guide details all declarative Lua configuration files located in `~/.config/detech/` (or the repository's `configs/lua/`).

Whenever you edit any of these `.lua` files, compile and apply the changes by running:
```sh
detech apply
```
To test without reloading running daemons:
```sh
detech apply --no-reload
```

---

## 1. `config.lua` — Main Desktop Configuration

The primary configuration file for general preferences, fonts, appearance, and desktop behavior.

```lua
return {
    general = {
        terminal = "kitty",            -- Default terminal emulator
        file_manager = "thunar",        -- Default graphical file manager
        browser = "firefox",           -- Default web browser
        editor = "nvim",               -- Default text/code editor
        notification_daemon = "dunst", -- Notification daemon ("dunst" or "mako")
    },
    terminal_info = {
        enable_neofetch = true,        -- Display themed Neofetch on interactive shell launch
        ascii_distro = "FreeBSD",      -- ASCII art distro logo ("FreeBSD")
        show_zfs = true,               -- Display ZFS root pool telemetry
        show_hyprland_theme = true,    -- Display active DETech theme and layout in Neofetch
    },
    widgets = {
        weather = {
            enabled = true,            -- Enable Waybar weather widget (wttr.in)
            location = "",             -- Specific city name (leave empty for auto-IP location)
            units = "m",               -- "m" for Metric (°C, km/h), "u" for Imperial (°F, mph)
            interval = 900,            -- Cache refresh interval in seconds (15 minutes)
        },
        calendar = {
            enabled = true,            -- Enable Waybar calendar widget & Rofi interactive calendar
            start_monday = true,       -- Start week on Monday
        },
        network = { enabled = true },  -- FreeBSD ifconfig Wi-Fi / Ethernet status
        media = { enabled = true },    -- MPRIS playerctl Now Playing widget
        dnd = {
            enabled = true,            -- Do Not Disturb / Notification Center widget
            history_length = 50,       -- Maximum notification history stored by Dunst
            show_indicators = true,    -- Show unread badge count in Waybar
        },
        tray = {
            enabled = true,            -- System tray in Waybar
            icon_size = 16,            -- Tray icon size in pixels
            spacing = 8,               -- Spacing between tray icons in pixels
            show_passive_items = true, -- Show passive tray items
        },
        uptime = { enabled = true },   -- FreeBSD sysctl uptime & kernel widget
        clipboard = { enabled = true },-- cliphist clipboard manager widget
    },
    fonts = {
        mono = "JetBrainsMono Nerd Font",       -- Monospace font for Terminal, Waybar, Rofi
        sans = "JetBrainsMono Nerd Font Propo", -- Proportional font for GTK / Qt UI
        size = 11,                              -- Base font size in pt
        bar_size = 11,                          -- Waybar font size in pt
        rofi_size = 12,                         -- Rofi font size in pt
        lock_size = 48,                         -- Hyprlock clock font size in pt
    },
    appearance = {
        theme = "bsd-crimson",           -- Active theme pack from presets/themes/
        dynamic_wallpaper_colors = false,-- Dynamically extract palette from wallpaper
        waybar_layout = "island-top",    -- Active Waybar preset (1 of 15)
        rofi_layout = "grid-cards",      -- Active Rofi app drawer preset (1 of 15)
        starship_preset = "tokyo-pill",  -- Active Starship prompt preset (1 of 15)
        hyprlock_layout = "bsd-crimson-guard",-- Active Hyprlock screen lock preset (1 of 14: 10 theme-matched + 4 classic)
        icon_theme = "Papirus-Dark",     -- System-wide icon pack (GTK, Qt, Rofi, Dunst)
        cursor_theme = "Bibata-Modern-Ice", -- System-wide cursor theme
        cursor_size = 24,                -- Cursor size in px
        gaps_in = 6,                     -- Hyprland inner gaps between windows
        gaps_out = 12,                   -- Hyprland outer gaps from screen edges
        border_size = 2,                 -- Window border width in px
        rounding = 10,                   -- Window corner radius in px
        blur = {
            enabled = true,              -- Enable Hyprland background blur
            size = 6,                    -- Blur radius
            passes = 3,                  -- Blur passes
            vibrancy = 0.2,              -- Blur color vibrancy
        },
        animations = "snappy",           -- "snappy", "smooth", "minimal", or "disabled"
    },
    input = {
        kb_layout = "us",                -- Keyboard layout
        kb_variant = "",                 -- Keyboard variant
        kb_options = "caps:escape",      -- XKB options (e.g., Caps Lock as Escape)
        follow_mouse = 1,                -- Window focus follows mouse
        touchpad_natural_scroll = true,  -- Reverse / natural touchpad scrolling
        sensitivity = 0.0,               -- Mouse sensitivity (-1.0 to 1.0)
    },
    autostart = {                        -- Daemons launched on Hyprland startup
        "waybar",
        "hyprpaper",
        "hypridle",
        "dunst",
        "wl-paste --type text --watch cliphist store",
    },
}
```

---

## 2. `freebsd.lua` — FreeBSD Hardware & Subsystem Configuration

Configures FreeBSD-specific utilities, hardware adapters, audio backends, privilege elevation, and the **Ly TUI Login Manager**.

```lua
return {
    os = "FreeBSD",
    privilege_cmd = "doas",        -- Privilege escalation tool ("doas" or "sudo")
    session_manager = "seatd",     -- Session broker ("seatd" or "consolekit2")
    
    -- Ly TUI Login Manager Configuration
    login_manager = {
        manager = "ly",            -- Login manager type ("ly" or "none")
        enable = true,             -- Enable Ly management in DETech
        animation = "matrix",      -- TUI background animation: "matrix", "doom", "colormix", "gameoflife", or "none"
        animation_frame_delay = 5, -- Animation frame delay (lower = faster)
        animation_timeout_sec = 0, -- Seconds before animation stops (0 = infinite)
        bigclock = "en",           -- Big clock display: "en", "none", or "fa"
        bigclock_12hr = false,     -- 12-hour clock format (false = 24-hour)
        bigclock_seconds = false,  -- Display seconds on big clock
        asterisk = "*",            -- Password mask character
        blank_box = true,          -- Clear text inputs on failed login
        hide_borders = false,      -- Hide dialog box borders
        save = true,               -- Save last logged-in username and session
        clear_password = true,     -- Clear password buffer on screen clear
        box_title = "DETech Desktop Environment (FreeBSD)", -- Dialog header title
        auto_login_user = nil,     -- Set to username string for auto-login (or nil)
        auto_login_session = nil,  -- Set to session name for auto-login (or nil)
    },
    
    -- Audio Backend
    audio = {
        backend = "auto",          -- "auto", "mixer" (FreeBSD OSS), "wpctl" (PipeWire), or "pactl"
        oss_device = "/dev/mixer0",-- OSS mixer device
        step = 5,                  -- Volume adjustment step percentage
    },
    
    -- Display Backlight
    backlight = {
        backend = "backlight",     -- "backlight" (/usr/bin/backlight) or "acpi" (sysctl hw.acpi.video)
        device = "/dev/backlight/backlight0", -- Backlight device node
        step = 5,                  -- Brightness adjustment step percentage
    },
    
    -- Power, ACPI & Sleep
    power = {
        battery_sysctl = "hw.acpi.battery",               -- ACPI battery sysctl root
        thermal_sysctl = "hw.acpi.thermal.tz0.temperature",-- ACPI thermal sysctl
        suspend_cmd = "doas acpiconf -s 3",               -- FreeBSD ACPI suspend command
        lock_before_suspend = true,                       -- Lock via hyprlock before suspending
        idle_lock_timeout = 300,                          -- Idle seconds before screen lock (5 min)
        idle_dpms_timeout = 420,                          -- Idle seconds before display sleep (7 min)
        idle_suspend_timeout = 900,                       -- Idle seconds before system suspend (15 min)
    },
    
    -- FreeBSD Package Management
    pkg = {
        binary = "/usr/sbin/pkg",  -- FreeBSD pkg binary path
        cache_ttl_seconds = 3600,  -- Remote package index cache TTL (1 hour)
    },
}
```

---

## 3. `keybinds.lua` — Keyboard Shortcuts & Actions

Every shortcut entry contains `mod`, `key`, `action`, `arg`, `category`, and `desc`. This structure powers the **Rofi Keybind Search & Runner (`SUPER + /`)**, which allows you to fuzzy-search any shortcut and execute it instantly with Enter.

```lua
local mod = "SUPER"

return {
    main_mod = mod,
    binds = {
        -- Launchers & Applications
        { mod = {mod}, key = "Return", action = "exec", arg = "kitty", category = "System", desc = "Launch Kitty Terminal" },
        { mod = {mod}, key = "B", action = "exec", arg = "firefox", category = "System", desc = "Launch Web Browser" },
        { mod = {mod}, key = "N", action = "exec", arg = "thunar", category = "System", desc = "Launch Graphical File Manager" },
        { mod = {mod}, key = "Q", action = "killactive", arg = "", category = "Window", desc = "Close Active Window" },
        { mod = {mod, "SHIFT"}, key = "Q", action = "exit", arg = "", category = "Session", desc = "Exit Hyprland Session" },
        { mod = {mod}, key = "L", action = "exec", arg = "hyprlock", category = "Session", desc = "Lock Screen (hyprlock)" },
        { mod = {mod, "SHIFT"}, key = "Escape", action = "exec", arg = "detech bsd power suspend", category = "Session", desc = "Suspend FreeBSD System (acpiconf)" },

        -- DETech Rofi Menus
        { mod = {mod}, key = "D", action = "exec", arg = "detech menu apps", category = "Launcher", desc = "Open Rofi App Drawer" },
        { mod = {mod}, key = "Slash", action = "exec", arg = "detech menu keybinds", category = "DETech", desc = "Search & Run Keyboard Shortcuts" },
        { mod = {mod, "SHIFT"}, key = "T", action = "exec", arg = "detech menu themes", category = "DETech", desc = "Switch System Theme" },
        { mod = {mod, "SHIFT"}, key = "W", action = "exec", arg = "detech menu wallpapers", category = "DETech", desc = "Pick Wallpaper & Sync Colors" },
        { mod = {mod, "SHIFT"}, key = "F", action = "exec", arg = "detech menu fonts", category = "DETech", desc = "Nerd Fonts Picker & Installer" },
        { mod = {mod, "SHIFT"}, key = "I", action = "exec", arg = "detech menu icons", category = "DETech", desc = "Icon Theme Picker" },
        { mod = {mod, "SHIFT"}, key = "C", action = "exec", arg = "detech menu colors", category = "DETech", desc = "Color Scheme & Dynamic Mode Picker" },
        { mod = {mod, "SHIFT"}, key = "B", action = "exec", arg = "detech menu waybar", category = "DETech", desc = "Switch Waybar Layout (15 Presets)" },
        { mod = {mod, "SHIFT"}, key = "R", action = "exec", arg = "detech menu rofi-layout", category = "DETech", desc = "Switch Rofi App Drawer Layout (15 Presets)" },
        { mod = {mod, "SHIFT"}, key = "P", action = "exec", arg = "detech menu starship", category = "DETech", desc = "Switch Starship Prompt (15 Presets)" },
        { mod = {mod, "SHIFT"}, key = "G", action = "exec", arg = "detech menu plugins", category = "DETech", desc = "Switch Hyprland Plugin Preset" },
        { mod = {mod, "SHIFT"}, key = "L", action = "exec", arg = "detech menu hyprlock", category = "DETech", desc = "Switch Hyprlock Screen Lock Theme (14 Presets)" },
        { mod = {mod}, key = "E", action = "exec", arg = "detech menu files", category = "Launcher", desc = "Rofi File Browser" },
        { mod = {mod}, key = "S", action = "exec", arg = "detech menu software", category = "FreeBSD", desc = "FreeBSD pkg Software Picker" },
        { mod = {mod}, key = "Period", action = "exec", arg = "detech menu glyphs", category = "Launcher", desc = "Emoji, NerdFont Glyph & Symbol Picker" },
        { mod = {mod}, key = "C", action = "exec", arg = "detech menu calendar", category = "Widgets", desc = "Open Interactive Rofi Calendar" },
        { mod = {mod}, key = "M", action = "exec", arg = "detech menu weather", category = "Widgets", desc = "Open Weather Forecast Popup" },
        { mod = {mod}, key = "Y", action = "exec", arg = "detech menu clipboard", category = "Widgets", desc = "Open Clipboard History Picker (cliphist)" },
        { mod = {mod}, key = "O", action = "exec", arg = "detech menu notifications", category = "Widgets", desc = "Open Notification Center (Dunst)" },
        { mod = {mod, "SHIFT"}, key = "N", action = "exec", arg = "detech bsd widgets dnd toggle", category = "Widgets", desc = "Toggle Do Not Disturb (Dunst)" },

        -- Window Tiling & Movement
        { mod = {mod}, key = "V", action = "togglefloating", arg = "", category = "Window", desc = "Toggle Floating Window" },
        { mod = {mod}, key = "F", action = "fullscreen", arg = "0", category = "Window", desc = "Toggle Fullscreen" },
        { mod = {mod}, key = "P", action = "pseudo", arg = "", category = "Window", desc = "Toggle Dwindle Pseudotile" },
        { mod = {mod}, key = "J", action = "layoutmsg", arg = "togglesplit", category = "Window", desc = "Toggle Split Direction" },

        -- FreeBSD Hardware Function Keys
        { mod = {}, key = "XF86AudioRaiseVolume", action = "exec", arg = "detech bsd audio up 5", category = "Hardware", desc = "Increase Volume (mixer/wpctl)" },
        { mod = {}, key = "XF86AudioLowerVolume", action = "exec", arg = "detech bsd audio down 5", category = "Hardware", desc = "Decrease Volume (mixer/wpctl)" },
        { mod = {}, key = "XF86AudioMute", action = "exec", arg = "detech bsd audio mute", category = "Hardware", desc = "Toggle Mute (mixer/wpctl)" },
        { mod = {}, key = "XF86MonBrightnessUp", action = "exec", arg = "detech bsd backlight up 5", category = "Hardware", desc = "Increase Brightness (/usr/bin/backlight)" },
        { mod = {}, key = "XF86MonBrightnessDown", action = "exec", arg = "detech bsd backlight down 5", category = "Hardware", desc = "Decrease Brightness (/usr/bin/backlight)" },
    }
}
```

---

## 4. `plugins.lua` — Official Hyprland Plugins

Configures official Hyprland ecosystem plugins (`hyprbars`, `hyprexpo`, `hyprtrails`, `hyprwinwrap`, `csgo-vulkan-fix`, `borders-plus-plus`).

```lua
return {
    preset = "minimal-expo",             -- Active plugin preset blueprint
    auto_reload_hyprpm = false,
    enabled_plugins = {
        hyprbars = false,
        hyprexpo = true,
        hyprtrails = false,
        hyprwinwrap = false,
        csgo_vulkan_fix = false,
        borders_plus_plus = false,
    },
    hyprbars = {
        bar_height = 28,
        bar_text_size = 10,
        bar_text_align = "center",
        bar_part_of_window = true,
        bar_precedence_over_border = true,
        buttons = {
            { button_size = 12, col = "urgent", cmd = "hyprctl dispatch 'hl.dsp.window.close()'" },
            { button_size = 12, col = "warning", cmd = "hyprctl dispatch 'hl.dsp.window.float({ action = \"toggle\" })'" },
            { button_size = 12, col = "accent", cmd = "hyprctl dispatch 'hl.dsp.window.fullscreen({ mode = \"maximized\", action = \"toggle\" })'" },
        },
    },
    hyprexpo = {
        columns = 3,
        gap_size = 6,
        workspace_method = "center current",
        enable_gesture = true,
    },
    hyprtrails = {
        color = "accent",
    },
    hyprwinwrap = {
        class = "detech-bg-widget",
    },
    csgo_vulkan_fix = {
        res_w = 1920,
        res_h = 1080,
        class = "cs2",
        fix_mouse = true,
    },
    borders_plus_plus = {
        add_borders = 1,
        natural_rounding = true,
        col_border_1 = "border_inactive",
    },
}
```

---

## 5. `monitors.lua` — Display Outputs & Refresh Rates

Defines monitor resolutions, refresh rates, positioning, and scaling.

```lua
return {
    monitors = {
        -- Format: { name, resolution, position, scale, options }
        { name = "", resolution = "preferred", position = "auto", scale = "1" },
        -- Example multi-monitor setup:
        -- { name = "DP-1", resolution = "2560x1440@144", position = "0x0", scale = "1" },
        -- { name = "HDMI-A-1", resolution = "1920x1080@60", position = "2560x0", scale = "1" },
    },
}
```

---

## 6. `rules.lua` — Window & Layer Rules

Defines floating rules, opacity, and positioning for specific application windows and overlays using Hyprland 0.56+ syntax.

```lua
return {
    window_rules = {
        { rule = "float on", match = "match:class ^(pavucontrol|qt5ct|qt6ct|nwg-look)$" },
        { rule = "float on", match = "match:title ^(DETech Package Installer)$" },
        { rule = "size 900 600", match = "match:title ^(DETech Package Installer)$" },
        { rule = "center on", match = "match:title ^(DETech Package Installer)$" },
    },
    layer_rules = {
        { rule = "blur on", target = "match:namespace rofi" },
        { rule = "ignore_alpha 0", target = "match:namespace rofi" },
        { rule = "blur on", target = "match:namespace waybar" },
    },
}
```
