-- DETech Window & Layer Rules Configuration (rules.lua)

return {
    window_rules = {
        { rule = "float", match = "class:^(pavucontrol|qt5ct|qt6ct|nwg-look)$" },
        { rule = "float", match = "title:^(DETech Package Installer)$" },
        { rule = "size 900 600", match = "title:^(DETech Package Installer)$" },
        { rule = "center", match = "title:^(DETech Package Installer)$" },
    },
    layer_rules = {
        { rule = "blur", target = "rofi" },
        { rule = "ignorezero", target = "rofi" },
        { rule = "blur", target = "waybar" },
    },
}
