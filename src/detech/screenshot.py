"""Screenshot engine and utilities for DETech (FreeBSD + Hyprland / Wayland).

Supports full screen, interactive region selection (`slurp`), active window capture
via `hyprctl`, delay timers, clipboard copying (`wl-copy`), themed selections,
notifications with image previews (`notify-send`), and annotations (`swappy` / `satty`).
"""

from __future__ import annotations

import datetime
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from detech.core.color_engine import resolve_active_palette
from detech.core.paths import get_repo_root
from detech.core.state import get_effective_context


def check_screenshot_tools() -> dict[str, bool]:
    """Check availability of Wayland screenshot, clipboard, and notification tools."""
    return {
        "grim": bool(shutil.which("grim")),
        "slurp": bool(shutil.which("slurp")),
        "wl-copy": bool(shutil.which("wl-copy")),
        "notify-send": bool(shutil.which("notify-send")),
        "hyprctl": bool(shutil.which("hyprctl")),
        "swappy": bool(shutil.which("swappy")),
        "satty": bool(shutil.which("satty")),
        "thunar": bool(shutil.which("thunar")),
        "xdg-open": bool(shutil.which("xdg-open")),
    }


def get_screenshots_dir(
    custom_dir: Path | str | None = None,
    context: dict[str, Any] | None = None,
) -> Path:
    """Resolve target directory for saving screenshots."""
    if custom_dir:
        dest = Path(custom_dir).expanduser().resolve()
        dest.mkdir(parents=True, exist_ok=True)
        return dest

    ctx = context if context is not None else get_effective_context()
    cfg_dir = ctx.get("config", {}).get("screenshots", {}).get("directory")
    if cfg_dir:
        dest = Path(cfg_dir).expanduser().resolve()
        dest.mkdir(parents=True, exist_ok=True)
        return dest

    xdg_pictures = os.environ.get("XDG_PICTURES_DIR")
    if xdg_pictures:
        dest = (Path(xdg_pictures).expanduser() / "Screenshots").resolve()
    else:
        dest = (Path.home() / "Pictures" / "Screenshots").resolve()

    dest.mkdir(parents=True, exist_ok=True)
    return dest


def resolve_screenshot_path(
    custom_output: Path | str | None = None,
    default_dir: Path | str | None = None,
    prefix: str = "Screenshot",
) -> Path:
    """Resolve destination file path for a new screenshot."""
    if custom_output:
        p = Path(custom_output).expanduser()
        if p.is_dir() or str(custom_output).endswith(("/", "\\")):
            target_dir = p.resolve()
            target_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            return target_dir / f"{prefix}_{ts}.png"
        if p.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            p = p.with_suffix(".png")
        p.parent.mkdir(parents=True, exist_ok=True)
        return p.resolve()

    target_dir = get_screenshots_dir(default_dir)
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    candidate = target_dir / f"{prefix}_{ts}.png"
    counter = 1
    while candidate.exists():
        candidate = target_dir / f"{prefix}_{ts}_{counter}.png"
        counter += 1
    return candidate


def build_slurp_command(
    palette: dict[str, str] | None = None,
    border_width: int = 2,
    show_dimensions: bool = True,
) -> list[str]:
    """Build themed `slurp` command using the active DETech desktop color palette."""
    pal = palette or {}
    accent = pal.get("accent", "#e64553").lstrip("#")
    bg = pal.get("bg_primary", "#1e1e2e").lstrip("#")

    border_color = f"#{accent}ee"
    selection_color = f"#{accent}22"
    backdrop_color = f"#{bg}66" if len(bg) == 6 else "#00000044"

    cmd = [
        "slurp",
        "-b",
        backdrop_color,
        "-c",
        border_color,
        "-s",
        selection_color,
        "-w",
        str(border_width),
    ]
    if show_dimensions:
        cmd.append("-d")
    return cmd


def get_active_window_geometry() -> str | None:
    """Retrieve geometry `X,Y WxH` of currently focused Hyprland window via `hyprctl activewindow -j`."""
    if not shutil.which("hyprctl"):
        return None
    try:
        proc = subprocess.run(
            ["hyprctl", "activewindow", "-j"],
            capture_output=True,
            text=True,
            timeout=1.5,
            check=False,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return None
        data = json.loads(proc.stdout)
        at = data.get("at")
        size = data.get("size")
        if (
            isinstance(at, list)
            and len(at) >= 2
            and isinstance(size, list)
            and len(size) >= 2
            and size[0] > 0
            and size[1] > 0
        ):
            return f"{at[0]},{at[1]} {size[0]}x{size[1]}"
    except Exception:
        pass
    return None


def build_grim_command(
    output_path: Path | str | None = None,
    geometry: str | None = None,
    include_cursor: bool = False,
    image_type: str = "png",
) -> list[str]:
    """Build `grim` screenshot capture command."""
    cmd = ["grim"]
    if include_cursor:
        cmd.append("-c")
    if geometry:
        cmd.extend(["-g", geometry])
    if image_type:
        cmd.extend(["-t", image_type])
    if output_path and str(output_path) != "-":
        cmd.append(str(output_path))
    return cmd


def copy_image_to_clipboard(image_path: Path | bytes) -> bool:
    """Copy PNG image data directly into Wayland clipboard via `wl-copy`."""
    if not shutil.which("wl-copy"):
        return False
    try:
        if isinstance(image_path, Path):
            with open(image_path, "rb") as f:
                res = subprocess.run(["wl-copy", "--type", "image/png"], stdin=f, check=False)
                return res.returncode == 0
        else:
            res = subprocess.run(["wl-copy", "--type", "image/png"], input=image_path, check=False)
            return res.returncode == 0
    except Exception:
        return False


def send_screenshot_notification(
    image_path: Path | None,
    message: str,
    title: str = "󰄄 Screenshot Captured",
) -> None:
    """Send desktop notification via `notify-send` with thumbnail preview."""
    if not shutil.which("notify-send"):
        return
    cmd = ["notify-send", "-a", "DETech Screenshot", "-t", "4000"]
    if image_path and Path(image_path).is_file():
        cmd.extend(["-i", str(image_path)])
    cmd.extend([title, message])
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def open_screenshot_in_editor(image_path: Path) -> bool:
    """Open screenshot in annotation/editing tool (`swappy` or `satty`)."""
    if shutil.which("swappy"):
        subprocess.Popen(["swappy", "-f", str(image_path)])
        return True
    if shutil.which("satty"):
        subprocess.Popen(["satty", "--filename", str(image_path)])
        return True
    if shutil.which("xdg-open"):
        subprocess.Popen(["xdg-open", str(image_path)])
        return True
    return False


def open_screenshots_folder(folder_path: Path | None = None) -> bool:
    """Open screenshots directory in GUI file manager."""
    folder = folder_path or get_screenshots_dir()
    folder.mkdir(parents=True, exist_ok=True)
    if shutil.which("thunar"):
        subprocess.Popen(["thunar", str(folder)])
        return True
    if shutil.which("xdg-open"):
        subprocess.Popen(["xdg-open", str(folder)])
        return True
    return False


def capture_screenshot(
    mode: str = "area",
    target: str = "both",
    output: Path | str | None = None,
    delay: int = 0,
    include_cursor: bool = False,
    notify: bool = True,
    slurp_border_width: int = 2,
    palette: dict[str, str] | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Capture desktop screenshot on FreeBSD / Wayland.

    Args:
        mode: Capture mode ('full', 'area', 'window').
        target: Destination ('both', 'save', 'copy', 'edit').
        output: Optional custom file or directory path.
        delay: Countdown delay in seconds before capturing.
        include_cursor: Include mouse cursor in capture.
        notify: Send desktop notification on completion.
        slurp_border_width: Pixel border width for interactive selection.
        palette: Optional theme palette dict for styling slurp box.
        context: Optional DETech configuration context.

    Returns:
        Dict with status, path, mode, target, and geometry.
    """
    tools = check_screenshot_tools()
    if not tools["grim"]:
        msg = "Missing required screenshot tool 'grim'. Install it on FreeBSD via: pkg install grim"
        if notify:
            send_screenshot_notification(None, msg, title="DETech Screenshot Error")
        return {"status": "error", "message": msg}

    ctx = context or get_effective_context()
    if palette is None:
        _, palette = resolve_active_palette(ctx)

    # Optional countdown delay
    if delay > 0:
        time.sleep(delay)

    geometry: str | None = None
    if mode == "area":
        if not tools["slurp"]:
            msg = "Missing required region selection tool 'slurp'. Install it via: pkg install slurp"
            if notify:
                send_screenshot_notification(None, msg, title="DETech Screenshot Error")
            return {"status": "error", "message": msg}

        slurp_cmd = build_slurp_command(
            palette=palette,
            border_width=slurp_border_width,
        )
        try:
            slurp_proc = subprocess.run(
                slurp_cmd,
                capture_output=True,
                text=True,
                check=False,
            )
            if slurp_proc.returncode != 0 or not slurp_proc.stdout.strip():
                return {"status": "cancelled", "message": "Screenshot region selection cancelled"}
            geometry = slurp_proc.stdout.strip()
        except Exception as e:
            return {"status": "error", "message": f"Selection failed: {e}"}

    elif mode == "window":
        geometry = get_active_window_geometry()
        # Fallback to slurp if hyprctl is not active or no window is focused
        if not geometry:
            if tools["slurp"]:
                slurp_cmd = build_slurp_command(palette=palette, border_width=slurp_border_width)
                slurp_proc = subprocess.run(slurp_cmd, capture_output=True, text=True, check=False)
                if slurp_proc.returncode != 0 or not slurp_proc.stdout.strip():
                    return {"status": "cancelled", "message": "Window selection cancelled"}
                geometry = slurp_proc.stdout.strip()
            else:
                geometry = None

    # Resolve output destination
    is_clipboard_only = (target == "copy") and (output is None)
    if is_clipboard_only:
        cache_dir = Path.home() / ".cache" / "detech"
        cache_dir.mkdir(parents=True, exist_ok=True)
        dest_file = cache_dir / "screenshot_clipboard.png"
    else:
        dest_file = resolve_screenshot_path(custom_output=output, default_dir=None)

    # Execute grim
    grim_cmd = build_grim_command(
        output_path=dest_file,
        geometry=geometry,
        include_cursor=include_cursor,
        image_type="png",
    )
    try:
        proc = subprocess.run(grim_cmd, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            err = proc.stderr.strip() or "grim execution failed"
            return {"status": "error", "message": err}
    except Exception as e:
        return {"status": "error", "message": str(e)}

    # Handle clipboard copying
    copied = False
    if target in ("copy", "both"):
        copied = copy_image_to_clipboard(dest_file)

    # Handle annotation / edit
    edited = False
    if target == "edit":
        edited = open_screenshot_in_editor(dest_file)

    # Construct user-facing message & notification
    if is_clipboard_only:
        summary_msg = "Screenshot copied to Wayland clipboard"
    elif target == "both":
        summary_msg = f"Saved to {dest_file.name} & copied to clipboard"
    elif target == "edit":
        summary_msg = f"Saved to {dest_file.name} (Opening editor)"
    else:
        summary_msg = f"Saved to {dest_file.name}"

    if notify:
        send_screenshot_notification(dest_file, summary_msg)

    return {
        "status": "success",
        "path": str(dest_file),
        "mode": mode,
        "target": target,
        "geometry": geometry,
        "copied": copied,
        "edited": edited,
        "timestamp": datetime.datetime.now().isoformat(),
    }
