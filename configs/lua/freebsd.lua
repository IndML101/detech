-- DETech FreeBSD Hardware & OS Integration Configuration (freebsd.lua)

return {
    os = "FreeBSD",
    privilege_cmd = "doas", -- "doas" or "sudo"
    session_manager = "seatd", -- "seatd" or "consolekit2"
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
