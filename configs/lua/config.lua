-- DETech Main Declarative Configuration (config.lua)
-- Edit this file and run `detech apply` to update your FreeBSD Hyprland environment.

return {
    general = {
        terminal = "kitty",
        file_manager = "thunar",
        browser = "firefox",
        editor = "nvim",
        notification_daemon = "dunst", -- "dunst" or "mako"
    },
    fonts = {
        mono = "JetBrainsMono Nerd Font",
        sans = "JetBrainsMono Nerd Font Propo",
        size = 11,
        bar_size = 11,
        rofi_size = 12,
        lock_size = 48,
    },
    appearance = {
        theme = "bsd-crimson",
        dynamic_wallpaper_colors = false,
        waybar_layout = "island-top",
        rofi_layout = "grid-cards",
        starship_preset = "tokyo-pill",
        hyprlock_layout = "minimal-clock",
        icon_theme = "Papirus-Dark",
        cursor_theme = "Bibata-Modern-Ice",
        cursor_size = 24,
        gaps_in = 6,
        gaps_out = 12,
        border_size = 2,
        rounding = 10,
        blur = {
            enabled = true,
            size = 6,
            passes = 3,
            vibrancy = 0.2,
        },
        animations = "snappy",
    },
    input = {
        kb_layout = "us",
        kb_variant = "",
        kb_options = "caps:escape",
        follow_mouse = 1,
        touchpad_natural_scroll = true,
        sensitivity = 0.0,
    },
    autostart = {
        "waybar",
        "hyprpaper",
        "hypridle",
        "dunst",
        "wl-paste --type text --watch cliphist store",
    },
}
