"""FreeBSD Audio Control Adapter (OSS mixer, PipeWire wpctl, PulseAudio pactl)."""

from __future__ import annotations

import re
import shutil
import subprocess
from typing import Any


def detect_audio_backend(preferred: str = "auto") -> str:
    """Detect available audio control utility on FreeBSD."""
    if preferred != "auto":
        return preferred
    # Check if PipeWire wpctl is actually responsive
    if shutil.which("wpctl"):
        try:
            res = subprocess.run(["wpctl", "status"], capture_output=True, timeout=0.3)
            if res.returncode == 0:
                return "wpctl"
        except Exception:
            pass
    # On FreeBSD, native OSS mixer is the primary, first-class base utility
    if shutil.which("mixer"):
        return "mixer"
    # Fallback to PulseAudio pactl if responsive
    if shutil.which("pactl"):
        try:
            res = subprocess.run(["pactl", "info"], capture_output=True, timeout=0.3)
            if res.returncode == 0:
                return "pactl"
        except Exception:
            pass
    return "mixer"


def build_audio_command(
    action: str,
    step: int = 5,
    backend: str = "auto",
    device: str = "/dev/mixer0",
) -> list[str]:
    """Build the FreeBSD command line for audio volume up/down/mute/status."""
    resolved = detect_audio_backend(backend)

    if resolved == "wpctl":
        if action == "up":
            return ["wpctl", "set-volume", "-l", "1.0", "@DEFAULT_AUDIO_SINK@", f"{step}%+"]
        if action == "down":
            return ["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{step}%-"]
        if action == "mute":
            return ["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"]
        return ["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"]

    if resolved == "pactl":
        if action == "up":
            return ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"+{step}%"]
        if action == "down":
            return ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"-{step}%"]
        if action == "mute":
            return ["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"]
        return ["pactl", "get-sink-volume", "@DEFAULT_SINK@"]

    # FreeBSD 14+ native `/usr/sbin/mixer` syntax
    base = ["mixer", "-f", device]
    if action == "up":
        return [*base, f"vol.volume=+{step}%"]
    if action == "down":
        return [*base, f"vol.volume=-{step}%"]
    if action == "mute":
        return [*base, "vol.mute=^"]
    return [*base, "vol"]


def parse_mixer_output(output: str) -> dict[str, Any]:
    """Parse FreeBSD `mixer vol` or `wpctl get-volume` output into `{volume: int, muted: bool}`."""
    muted = "MUTED" in output.upper() or "mute=on" in output.lower() or "mute: yes" in output.lower()

    # Check FreeBSD 14+ float format e.g. `vol.volume=0.75:0.75`
    m_float = re.search(r"volume=([0-9.]+):", output)
    if m_float:
        vol = int(round(float(m_float.group(1)) * 100))
        return {"volume": max(0, min(100, vol)), "muted": muted}

    # Check wpctl format e.g. `Volume: 0.65 [MUTED]`
    m_wp = re.search(r"Volume:\s*([0-9.]+)", output)
    if m_wp:
        vol = int(round(float(m_wp.group(1)) * 100))
        return {"volume": max(0, min(100, vol)), "muted": muted}

    # Classic FreeBSD mixer format `Mixer vol is currently set to 75:75`
    m_classic = re.search(r"(\d{1,3}):(\d{1,3})", output)
    if m_classic:
        return {"volume": int(m_classic.group(1)), "muted": muted}

    m_pct = re.search(r"(\d{1,3})%", output)
    if m_pct:
        return {"volume": int(m_pct.group(1)), "muted": muted}

    return {"volume": 50, "muted": muted}


def run_audio_action(
    action: str,
    step: int = 5,
    backend: str = "auto",
    device: str = "/dev/mixer0",
    notify: bool = True,
) -> dict[str, Any]:
    """Execute audio action on FreeBSD and optionally send an OSD notification."""
    cmd = build_audio_command(action, step=step, backend=backend, device=device)
    subprocess.run(cmd, check=False, capture_output=True, text=True)

    status_cmd = build_audio_command("status", step=step, backend=backend, device=device)
    proc = subprocess.run(status_cmd, check=False, capture_output=True, text=True)
    info = parse_mixer_output(proc.stdout)

    if notify and shutil.which("notify-send") and action in ("up", "down", "mute"):
        icon = "󰝟 Muted" if info["muted"] else f"󰕾 Volume {info['volume']}%"
        try:
            subprocess.Popen(
                [
                    "notify-send",
                    "-t",
                    "1500",
                    "-a",
                    "DETech OSD",
                    "-h",
                    f"int:value:{info['volume']}",
                    "-h",
                    "string:x-canonical-private-synchronous:audio",
                    icon,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass
    return info
