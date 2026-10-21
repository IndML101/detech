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

    pkgs = parse_pkg_query_output("hyprland|0.42.0|Dynamic tiling Wayland compositor\nrofi-wayland|1.7.5|Window switcher\n")
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
