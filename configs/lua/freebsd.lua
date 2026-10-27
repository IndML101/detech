-- DETech FreeBSD Hardware & OS Integration Configuration (freebsd.lua)

return {
    os = "FreeBSD",
    privilege_cmd = "doas", -- "doas" or "sudo"
    session_manager = "seatd", -- "seatd" or "consolekit2"
    login_manager = {
        manager = "ly", -- "ly" or "none"
        enable = true,
        animation = "none", -- "matrix", "doom", "colormix", "gameoflife", "none"
        animation_frame_delay = 5,
        animation_timeout_sec = 0,
        bigclock = "en", -- "en", "none", "fa"
        bigclock_12hr = false,
        bigclock_seconds = false,
        asterisk = "*",
        blank_box = true,
        hide_borders = false,
        save = true,
        clear_password = true,
        box_title = "DETech Desktop Environment (FreeBSD)",
        auto_login_user = nil,
        auto_login_session = nil,
    },
    audio = {
        backend = "auto", -- "auto", "mixer", "wpctl", "pactl"
        oss_device = "/dev/mixer0",
        step = 5,
    },
    backlight = {
        backend = "backlight", -- "backlight" (/usr/bin/backlight) or "acpi" (sysctl hw.acpi.video)
        device = "/dev/backlight/backlight0",
        step = 5,
    },
    power = {
        battery_sysctl = "hw.acpi.battery",
        thermal_sysctl = "hw.acpi.thermal.tz0.temperature",
        suspend_cmd = "doas acpiconf -s 3",
        lock_before_suspend = true,
        idle_lock_timeout = 300,
        idle_dpms_timeout = 420,
        idle_suspend_timeout = 900,
    },
    pkg = {
        binary = "/usr/sbin/pkg",
        cache_ttl_seconds = 3600,
    },
}
