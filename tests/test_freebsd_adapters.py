"""Tests for FreeBSD Hardware & OS Integration Adapters."""

from __future__ import annotations

from detech.freebsd.audio import build_audio_command, parse_mixer_output
from detech.freebsd.backlight import build_backlight_command, parse_backlight_output
from detech.freebsd.pkg_manager import build_pkg_terminal_command, parse_pkg_query_output
from detech.freebsd.power import (
    build_power_command,
    get_memory_status,
    get_system_load_status,
    get_zfs_status,
)
from detech.freebsd.widgets import (
    get_calendar_status,
    get_uptime_kernel_status,
    parse_boottime_sysctl,
    parse_dunst_history,
    parse_ifconfig_network_output,
    parse_wttr_json,
)
from detech.menus.widget_menus import build_calendar_menu_entries


def test_freebsd_audio_commands_and_parser() -> None:
    cmd_up = build_audio_command("up", step=5, backend="mixer", device="/dev/mixer0")
    assert cmd_up == ["mixer", "-f", "/dev/mixer0", "vol.volume=+5%"]

    cmd_mute = build_audio_command("mute", backend="mixer", device="/dev/mixer0")
    assert cmd_mute == ["mixer", "-f", "/dev/mixer0", "vol.mute=^"]

    parsed_bsd14 = parse_mixer_output("vol.volume=0.80:0.80\nvol.mute=off\n")
    assert parsed_bsd14 == {"volume": 80, "muted": False}

    parsed_muted = parse_mixer_output("vol.volume=0.45:0.45\nvol.mute=on\n")
    assert parsed_muted == {"volume": 45, "muted": True}


def test_freebsd_backlight_commands_and_parser() -> None:
    cmd = build_backlight_command("up", step=10, backend="backlight", device="/dev/backlight/backlight0")
    assert cmd == ["backlight", "-f", "/dev/backlight/backlight0", "+", "10"]
    assert parse_backlight_output("brightness: 65\n") == 65


def test_freebsd_power_and_pkg_commands() -> None:
    assert build_power_command("suspend", privilege_cmd="doas") == ["doas", "acpiconf", "-s", "3"]
    assert build_power_command("poweroff", privilege_cmd="doas") == ["doas", "shutdown", "-p", "now"]

    pkgs = parse_pkg_query_output("hyprland|0.42.0|Dynamic tiling Wayland compositor\nrofi|1.7.5|Window switcher\n")
    assert len(pkgs) == 2
    assert pkgs[0]["name"] == "hyprland"

    term_cmd = build_pkg_terminal_command("install", "neovim", privilege_cmd="doas", terminal="kitty")
    assert term_cmd[:3] == ["kitty", "--title", "DETech Package Installer"]
    assert "doas pkg install -y neovim" in term_cmd[-1]


def test_freebsd_telemetry_status_helpers() -> None:
    load_info = get_system_load_status()
    assert "load_1m" in load_info
    assert "text" in load_info

    mem_info = get_memory_status()
    assert 0 <= mem_info["percent"] <= 100
    assert "FreeBSD Memory" in mem_info["tooltip"]

    zfs_info = get_zfs_status()
    assert "pool" in zfs_info
    assert "health" in zfs_info


def test_freebsd_and_waybar_widgets() -> None:
    sample_wttr = {
        "current_condition": [
            {
                "temp_C": "24",
                "temp_F": "75",
                "FeelsLikeC": "25",
                "FeelsLikeF": "77",
                "weatherCode": "113",
                "weatherDesc": [{"value": "Sunny"}],
                "humidity": "45",
                "windspeedKmph": "12",
            }
        ],
        "nearest_area": [
            {
                "areaName": [{"value": "San Francisco"}],
                "country": [{"value": "United States"}],
            }
        ],
        "weather": [
            {"date": "2026-10-21", "maxtempC": "25", "mintempC": "14", "maxtempF": "77", "mintempF": "57"}
        ],
    }
    w_metric = parse_wttr_json(sample_wttr, units="m")
    assert w_metric["text"] == "󰖙 24°C"
    assert "San Francisco" in w_metric["tooltip"]
    assert "2026-10-21" in w_metric["tooltip"]

    w_imperial = parse_wttr_json(sample_wttr, units="u")
    assert w_imperial["text"] == "󰖙 75°F"

    cal_info = get_calendar_status(accent_color="#e64553")
    assert "" in cal_info["text"]
    assert "#e64553" in cal_info["tooltip"]

    _, cal_entries = build_calendar_menu_entries(2026, 10)
    assert any("Previous Month" in e for e in cal_entries)
    assert any("Next Month" in e for e in cal_entries)

    sample_ifconfig = (
        "lo0: flags=8049<UP,LOOPBACK,RUNNING,MULTICAST> metric 0 mtu 16384\n"
        "\tinet 127.0.0.1 netmask 0xff000000\n"
        "wlan0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> metric 0 mtu 1500\n"
        "\tinet 192.168.1.42 netmask 0xffffff00 broadcast 192.168.1.255\n"
        "\tssid BSDNet channel 36 (5180 MHz 11a)\n"
        "\tstatus: associated\n"
    )
    net_info = parse_ifconfig_network_output(sample_ifconfig)
    assert net_info["connected"] is True
    assert net_info["interface"] == "wlan0"
    assert net_info["ssid"] == "BSDNet"
    assert "󰤨 BSDNet" == net_info["text"]

    uptime_sec = parse_boottime_sysctl("{ sec = 1700000000, usec = 0 }", now_ts=1700007500)
    assert uptime_sec == 7500

    up_status = get_uptime_kernel_status()
    assert "󱎫" in up_status["text"]
    assert "FreeBSD Kernel:" in up_status["tooltip"]

    sample_dunst = (
        '{"data":[[{"id":{"data":12},"appname":{"data":"Firefox"},'
        '"summary":{"data":"Download Complete"},"body":{"data":"freebsd.iso"}}]]}'
    )
    hist = parse_dunst_history(sample_dunst)
    assert len(hist) == 1
    assert hist[0]["id"] == "12"
    assert hist[0]["app"] == "Firefox"
    assert hist[0]["summary"] == "Download Complete"
