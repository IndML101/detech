-- DETech Window & Layer Rules Configuration (rules.lua)

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
