"""FreeBSD `pkg` Package Manager Adapter for Rofi Software Picker & Waybar Updates."""

from __future__ import annotations

import json
import subprocess
from typing import Any


def parse_pkg_query_output(output: str) -> list[dict[str, str]]:
    """Parse `pkg rquery '%n|%v|%c'` or `pkg query '%n|%v|%c'` output."""
    packages: list[dict[str, str]] = []
    for line in output.splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        parts = line.split("|", 2)
        if len(parts) == 3:
            name, version, comment = parts
        elif len(parts) == 2:
            name, version = parts
            comment = ""
        else:
            continue
        packages.append(
            {
                "name": name.strip(),
                "version": version.strip(),
                "comment": comment.strip(),
            }
        )
    return packages


def list_installed_packages(pkg_bin: str = "/usr/sbin/pkg") -> list[dict[str, str]]:
    """Query installed FreeBSD packages via `pkg query '%n|%v|%c'`."""
    try:
        proc = subprocess.run(
            [pkg_bin, "query", "%n|%v|%c"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return []
    return parse_pkg_query_output(proc.stdout)


def search_remote_packages(query: str = "", pkg_bin: str = "/usr/sbin/pkg") -> list[dict[str, str]]:
    """Search FreeBSD repository packages via `pkg rquery`."""
    cmd = [pkg_bin, "rquery", "%n|%v|%c"]
    if query:
        cmd.append(query)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except OSError:
        return []
    return parse_pkg_query_output(proc.stdout)


def build_pkg_terminal_command(
    action: str,
    pkg_name: str,
    privilege_cmd: str = "doas",
    terminal: str = "kitty",
) -> list[str]:
    """Build a floating Kitty terminal command to install or delete a FreeBSD package."""
    if action not in ("install", "delete", "upgrade"):
        raise ValueError(f"Unsupported pkg action: {action!r}")
    inner_cmd = f"{privilege_cmd} pkg {action} -y {pkg_name}; printf '\\nPress Enter to close...'; read _"
    return [
        terminal,
        "--title",
        "DETech Package Installer",
        "sh",
        "-c",
        inner_cmd,
    ]


def get_pkg_updates_status(pkg_bin: str = "/usr/sbin/pkg") -> str:
    """Return Waybar JSON string with count of pending FreeBSD pkg upgrades."""
    try:
        proc = subprocess.run(
            [pkg_bin, "version", "-vRL="],
            capture_output=True,
            text=True,
            check=False,
        )
        stdout = proc.stdout
    except OSError:
        stdout = ""
    lines = [ln for ln in stdout.splitlines() if "<" in ln]
    count = len(lines)
    return json.dumps(
        {
            "text": f"󰏔 {count}",
            "tooltip": f"{count} FreeBSD package update(s) available",
            "class": "updates-available" if count > 0 else "up-to-date",
        }
    )
