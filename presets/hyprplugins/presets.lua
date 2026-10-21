-- DETech Official Hyprland Plugin Presets Catalog
-- Switches enabled official Hyprland plugins (`hyprbars`, `hyprexpo`, `hyprtrails`, `hyprwinwrap`, `csgo-vulkan-fix`, `borders-plus-plus`).

return {
    presets = {
        {
            id = "minimal-expo",
            name = "Minimal Expo (Workspace Overview Grid Only)",
            description = "Clean borderless tiling with 3-finger gesture & hotkey workspace overview",
            enabled_plugins = {
                hyprbars = false,
                hyprexpo = true,
                hyprtrails = false,
                hyprwinwrap = false,
                csgo_vulkan_fix = false,
                borders_plus_plus = false,
            },
        },
        {
            id = "window-bars",
            name = "Window Bars (Hyprbars Titlebars + Hyprexpo)",
            description = "Adds theme-synced titlebars with Close/Fullscreen/Float buttons to windows",
            enabled_plugins = {
                hyprbars = true,
                hyprexpo = true,
                hyprtrails = false,
                hyprwinwrap = false,
                csgo_vulkan_fix = false,
                borders_plus_plus = false,
            },
        },
        {
            id = "eye-candy",
            name = "Eye Candy (Hyprexpo + Hyprtrails + Double Borders)",
            description = "Full visual flair: workspace expo, smooth accent motion trails, and dual borders",
            enabled_plugins = {
                hyprbars = false,
                hyprexpo = true,
                hyprtrails = true,
                hyprwinwrap = false,
                csgo_vulkan_fix = false,
                borders_plus_plus = true,
            },
        },
        {
            id = "desktop-widget",
            name = "Desktop Widget (Hyprwinwrap Background App + Hyprexpo)",
            description = "Wraps a custom background app (e.g. cava / matrix / clock) as a desktop layer",
            enabled_plugins = {
                hyprbars = false,
                hyprexpo = true,
                hyprtrails = false,
                hyprwinwrap = true,
                csgo_vulkan_fix = false,
                borders_plus_plus = false,
            },
        },
        {
            id = "bsd-gamer",
            name = "BSD Gamer (CSGO/Vulkan Fix + Zero Overhead)",
            description = "Enables csgo-vulkan-fix for stretched/custom Vulkan resolutions with minimal overhead",
            enabled_plugins = {
                hyprbars = false,
                hyprexpo = false,
                hyprtrails = false,
                hyprwinwrap = false,
                csgo_vulkan_fix = true,
                borders_plus_plus = false,
            },
        },
        {
            id = "vanilla-zero",
            name = "Vanilla Zero (All Plugins Disabled)",
            description = "Pure core Hyprland compositor with zero plugins loaded",
            enabled_plugins = {
                hyprbars = false,
                hyprexpo = false,
                hyprtrails = false,
                hyprwinwrap = false,
                csgo_vulkan_fix = false,
                borders_plus_plus = false,
            },
        },
    },
}
