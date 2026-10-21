-- DETech Official Hyprland Plugins Configuration (plugins.lua)
-- Strictly uses official Hypr ecosystem plugins managed via hyprpm / FreeBSD packages.

return {
    enabled_plugins = {
        hyprbars = false,
        hyprexpo = true,
        hyprtrails = false,
        hyprwinwrap = false,
    },
    hyprbars = {
        bar_height = 28,
        bar_text_size = 10,
        bar_part_of_window = true,
        bar_precedence_over_border = true,
        buttons = {
            { button_size = 12, col = "urgent", cmd = "hyprctl dispatch killactive" },
            { button_size = 12, col = "accent", cmd = "hyprctl dispatch fullscreen 1" },
        },
    },
    hyprexpo = {
        columns = 3,
        gap_size = 5,
        workspace_method = "center current",
        enable_gesture = true,
        gesture_fingers = 3,
        gesture_distance = 300,
    },
    hyprtrails = {
        color = "accent",
    },
}
