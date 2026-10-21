"""FreeBSD Display Backlight Control Adapter (`/usr/bin/backlight` & `sysctl hw.acpi.video`)."""

from __future__ import annotations

import re
import shutil
import subprocess
from typing import Any


def build_backlight_command(
    action: str,
    step: int = 5,
    backend: str = "backlight",
    device: str = "/dev/backlight/backlight0",
) -> list[str]:
    """Build the FreeBSD command line for screen brightness control."""
    if backend == "acpi":
        # Fallback for older ACPI video driver
        return ["sysctl", "hw.acpi.video.lcd0.brightness"]

    base = ["backlight", "-f", device]
    if action == "up":
        return [*base, "+", str(step)]
    if action == "down":
        return [*base, "-", str(step)]
    if action == "set":
        return [*base, str(step)]
    return [*base, "-q"]


def parse_backlight_output(output: str) -> int:
    """Parse FreeBSD `backlight -q` or `backlight` output into percentage (0..100)."""
    m = re.search(r"(\d{1,3})", output)
    if m:
        return max(0, min(100, int(m.group(1))))
    return 100


def run_backlight_action(
    action: str,
    step: int = 5,
    backend: str = "backlight",
    device: str = "/dev/backlight/backlight0",
    notify: bool = True,
) -> dict[str, Any]:
    """Execute backlight action on FreeBSD and optionally send an OSD notification."""
    cmd = build_backlight_command(action, step=step, backend=backend, device=device)
    subprocess.run(cmd, check=False, capture_output=True, text=True)

    status_cmd = build_backlight_command("status", step=step, backend=backend, device=device)
    proc = subprocess.run(status_cmd, check=False, capture_output=True, text=True)
    level = parse_backlight_output(proc.stdout)

    if notify and shutil.which("notify-send") and action in ("up", "down", "set"):
        subprocess.run(
            [
                "notify-send",
                "-a",
                "DETech OSD",
                "-h",
                f"int:value:{level}",
                "-h",
                "string:x-canonical-private-synchronous:backlight",
                f"󰃠 Brightness {level}%",
            ],
            check=False,
        )
    return {"brightness": level}
