-- DETech Official Hyprland Plugins Configuration (plugins.lua)
-- Strictly uses official Hypr ecosystem plugins managed via hyprpm / FreeBSD packages.

return {
    preset = "minimal-expo",
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
