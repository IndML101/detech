-- DETech Keyboard Shortcuts Configuration (keybinds.lua)
-- Every shortcut includes a category and description for the Rofi Keybind Search & Runner (`SUPER + /`).

local mod = "SUPER"

return {
    main_mod = mod,
    binds = {
        -- Core Applications & Session
        { mod = {mod}, key = "Return", action = "exec", arg = "kitty", category = "System", desc = "Launch Kitty Terminal" },
        { mod = {mod}, key = "B", action = "exec", arg = "firefox", category = "System", desc = "Launch Web Browser" },
        { mod = {mod}, key = "N", action = "exec", arg = "thunar", category = "System", desc = "Launch Graphical File Manager" },
        { mod = {mod}, key = "Q", action = "killactive", arg = "", category = "Window", desc = "Close Active Window" },
        { mod = {mod, "SHIFT"}, key = "Q", action = "exit", arg = "", category = "Session", desc = "Exit Hyprland Session" },
        { mod = {mod}, key = "L", action = "exec", arg = "hyprlock", category = "Session", desc = "Lock Screen (hyprlock)" },
        { mod = {mod, "SHIFT"}, key = "Escape", action = "exec", arg = "detech bsd power suspend", category = "Session", desc = "Suspend FreeBSD System (acpiconf)" },

        -- DETech Rofi Interactive Pickers
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
        { mod = {mod}, key = "Tab", action = "hyprexpo:expo", arg = "toggle", category = "Workspace", desc = "Toggle Hyprexpo Workspace Overview" },
        { mod = {mod}, key = "E", action = "exec", arg = "detech menu files", category = "Launcher", desc = "Rofi File Browser" },
        { mod = {mod}, key = "S", action = "exec", arg = "detech menu software", category = "FreeBSD", desc = "FreeBSD pkg Software Picker" },
        { mod = {mod}, key = "Period", action = "exec", arg = "detech menu glyphs", category = "Launcher", desc = "Emoji, NerdFont Glyph & Symbol Picker" },
        { mod = {mod}, key = "C", action = "exec", arg = "detech menu calendar", category = "Widgets", desc = "Open Interactive Rofi Calendar" },
        { mod = {mod}, key = "M", action = "exec", arg = "detech menu weather", category = "Widgets", desc = "Open Weather Forecast Popup" },
        { mod = {mod}, key = "Y", action = "exec", arg = "detech menu clipboard", category = "Widgets", desc = "Open Clipboard History Picker (cliphist)" },
        { mod = {mod}, key = "O", action = "exec", arg = "detech menu notifications", category = "Widgets", desc = "Open Notification Center (Dunst)" },
        { mod = {mod, "SHIFT"}, key = "N", action = "exec", arg = "detech bsd widgets dnd toggle", category = "Widgets", desc = "Toggle Do Not Disturb (Dunst)" },

        -- Window Management & Layout
        { mod = {mod}, key = "V", action = "togglefloating", arg = "", category = "Window", desc = "Toggle Floating Window" },
        { mod = {mod}, key = "F", action = "fullscreen", arg = "0", category = "Window", desc = "Toggle Fullscreen" },
        { mod = {mod}, key = "P", action = "pseudo", arg = "", category = "Window", desc = "Toggle Dwindle Pseudotile" },
        { mod = {mod}, key = "J", action = "togglesplit", arg = "", category = "Window", desc = "Toggle Split Direction" },

        -- Focus Movement (Vim + Arrow Keys)
        { mod = {mod}, key = "Left", action = "movefocus", arg = "l", category = "Focus", desc = "Move Focus Left" },
        { mod = {mod}, key = "Right", action = "movefocus", arg = "r", category = "Focus", desc = "Move Focus Right" },
        { mod = {mod}, key = "Up", action = "movefocus", arg = "u", category = "Focus", desc = "Move Focus Up" },
        { mod = {mod}, key = "Down", action = "movefocus", arg = "d", category = "Focus", desc = "Move Focus Down" },
        { mod = {mod, "CTRL"}, key = "H", action = "movefocus", arg = "l", category = "Focus", desc = "Move Focus Left (Vim)" },
        { mod = {mod, "CTRL"}, key = "L", action = "movefocus", arg = "r", category = "Focus", desc = "Move Focus Right (Vim)" },
        { mod = {mod, "CTRL"}, key = "K", action = "movefocus", arg = "u", category = "Focus", desc = "Move Focus Up (Vim)" },
        { mod = {mod, "CTRL"}, key = "J", action = "movefocus", arg = "d", category = "Focus", desc = "Move Focus Down (Vim)" },

        -- Workspaces (1-10)
        { mod = {mod}, key = "1", action = "workspace", arg = "1", category = "Workspace", desc = "Switch to Workspace 1" },
        { mod = {mod}, key = "2", action = "workspace", arg = "2", category = "Workspace", desc = "Switch to Workspace 2" },
        { mod = {mod}, key = "3", action = "workspace", arg = "3", category = "Workspace", desc = "Switch to Workspace 3" },
        { mod = {mod}, key = "4", action = "workspace", arg = "4", category = "Workspace", desc = "Switch to Workspace 4" },
        { mod = {mod}, key = "5", action = "workspace", arg = "5", category = "Workspace", desc = "Switch to Workspace 5" },
        { mod = {mod}, key = "6", action = "workspace", arg = "6", category = "Workspace", desc = "Switch to Workspace 6" },
        { mod = {mod}, key = "7", action = "workspace", arg = "7", category = "Workspace", desc = "Switch to Workspace 7" },
        { mod = {mod}, key = "8", action = "workspace", arg = "8", category = "Workspace", desc = "Switch to Workspace 8" },
        { mod = {mod}, key = "9", action = "workspace", arg = "9", category = "Workspace", desc = "Switch to Workspace 9" },
        { mod = {mod}, key = "0", action = "workspace", arg = "10", category = "Workspace", desc = "Switch to Workspace 10" },

        -- Move Active Window to Workspace (1-10)
        { mod = {mod, "SHIFT"}, key = "1", action = "movetoworkspace", arg = "1", category = "Workspace", desc = "Move Window to Workspace 1" },
        { mod = {mod, "SHIFT"}, key = "2", action = "movetoworkspace", arg = "2", category = "Workspace", desc = "Move Window to Workspace 2" },
        { mod = {mod, "SHIFT"}, key = "3", action = "movetoworkspace", arg = "3", category = "Workspace", desc = "Move Window to Workspace 3" },
        { mod = {mod, "SHIFT"}, key = "4", action = "movetoworkspace", arg = "4", category = "Workspace", desc = "Move Window to Workspace 4" },
        { mod = {mod, "SHIFT"}, key = "5", action = "movetoworkspace", arg = "5", category = "Workspace", desc = "Move Window to Workspace 5" },
        { mod = {mod, "SHIFT"}, key = "6", action = "movetoworkspace", arg = "6", category = "Workspace", desc = "Move Window to Workspace 6" },
        { mod = {mod, "SHIFT"}, key = "7", action = "movetoworkspace", arg = "7", category = "Workspace", desc = "Move Window to Workspace 7" },
        { mod = {mod, "SHIFT"}, key = "8", action = "movetoworkspace", arg = "8", category = "Workspace", desc = "Move Window to Workspace 8" },
        { mod = {mod, "SHIFT"}, key = "9", action = "movetoworkspace", arg = "9", category = "Workspace", desc = "Move Window to Workspace 9" },
        { mod = {mod, "SHIFT"}, key = "0", action = "movetoworkspace", arg = "10", category = "Workspace", desc = "Move Window to Workspace 10" },

        -- FreeBSD Hardware Keys
        { mod = {}, key = "XF86AudioRaiseVolume", action = "exec", arg = "detech bsd audio up 5", category = "Hardware", desc = "Increase Audio Volume (+5%)" },
        { mod = {}, key = "XF86AudioLowerVolume", action = "exec", arg = "detech bsd audio down 5", category = "Hardware", desc = "Decrease Audio Volume (-5%)" },
        { mod = {}, key = "XF86AudioMute", action = "exec", arg = "detech bsd audio mute", category = "Hardware", desc = "Toggle Audio Mute" },
        { mod = {}, key = "XF86MonBrightnessUp", action = "exec", arg = "detech bsd backlight up 5", category = "Hardware", desc = "Increase Display Brightness (+5%)" },
        { mod = {}, key = "XF86MonBrightnessDown", action = "exec", arg = "detech bsd backlight down 5", category = "Hardware", desc = "Decrease Display Brightness (-5%)" },
    },
}
