"""Tests for DETech Screenshot Utility and Interactive Screenshot Picker."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from detech.cli import build_parser
from detech.menus.screenshot_menu import build_screenshot_menu_entries, open_screenshot_menu
from detech.screenshot import (
    build_grim_command,
    build_slurp_command,
    capture_screenshot,
    check_screenshot_tools,
    copy_image_to_clipboard,
    get_active_window_geometry,
    get_screenshots_dir,
    open_screenshot_in_editor,
    open_screenshots_folder,
    resolve_screenshot_path,
    send_screenshot_notification,
)


def test_check_screenshot_tools() -> None:
    tools = check_screenshot_tools()
    assert "grim" in tools
    assert "slurp" in tools
    assert "wl-copy" in tools
    assert "notify-send" in tools
    assert "hyprctl" in tools
    assert "swappy" in tools
    assert isinstance(tools["grim"], bool)


def test_get_screenshots_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Explicit directory
    custom = tmp_path / "custom_shots"
    resolved = get_screenshots_dir(custom)
    assert resolved == custom.resolve()
    assert custom.is_dir()

    # From context config
    cfg_dir = tmp_path / "ctx_shots"
    context = {"config": {"screenshots": {"directory": str(cfg_dir)}}}
    resolved_ctx = get_screenshots_dir(context=context)
    assert resolved_ctx == cfg_dir.resolve()
    assert cfg_dir.is_dir()

    # From XDG_PICTURES_DIR (when no explicit directory configured in config)
    xdg_pics = tmp_path / "Pictures"
    monkeypatch.setenv("XDG_PICTURES_DIR", str(xdg_pics))
    resolved_xdg = get_screenshots_dir(context={"config": {}})
    assert resolved_xdg == (xdg_pics / "Screenshots").resolve()
    assert resolved_xdg.is_dir()


def test_resolve_screenshot_path(tmp_path: Path) -> None:
    dest_dir = tmp_path / "shots"
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Automatically generate timestamped file
    path = resolve_screenshot_path(default_dir=dest_dir)
    assert path.parent == dest_dir
    assert path.name.startswith("Screenshot_")
    assert path.suffix == ".png"

    # Custom filename
    custom_file = dest_dir / "my_capture.png"
    resolved_custom = resolve_screenshot_path(custom_output=custom_file)
    assert resolved_custom == custom_file

    # Custom filename without extension
    no_ext = dest_dir / "screen_output"
    resolved_ext = resolve_screenshot_path(custom_output=no_ext)
    assert resolved_ext == dest_dir / "screen_output.png"

    # Collision incrementing
    existing = dest_dir / "Screenshot_2026-10-26_12-00-00.png"
    existing.write_text("existing", encoding="utf-8")
    with patch("datetime.datetime") as mock_dt:
        mock_now = MagicMock()
        mock_now.strftime.return_value = "2026-10-26_12-00-00"
        mock_dt.now.return_value = mock_now
        c1 = resolve_screenshot_path(default_dir=dest_dir)
        assert c1.name == "Screenshot_2026-10-26_12-00-00_1.png"


def test_build_slurp_command() -> None:
    palette = {
        "accent": "#ff5577",
        "bg_primary": "#1a1b26",
    }
    cmd = build_slurp_command(palette=palette, border_width=3, show_dimensions=True)
    assert cmd[0] == "slurp"
    assert "-b" in cmd
    assert "-c" in cmd
    assert "#ff5577ee" in cmd
    assert "-s" in cmd
    assert "#ff557722" in cmd
    assert "-w" in cmd
    assert "3" in cmd
    assert "-d" in cmd


def test_get_active_window_geometry() -> None:
    sample_json = json.dumps(
        {
            "class": "kitty",
            "title": "kitty",
            "at": [120, 80],
            "size": [960, 540],
        }
    )
    mock_proc = MagicMock(returncode=0, stdout=sample_json)

    with patch("shutil.which", return_value="/usr/local/bin/hyprctl"), patch(
        "subprocess.run", return_value=mock_proc
    ):
        geo = get_active_window_geometry()
        assert geo == "120,80 960x540"

    # Test failure / no active window
    with patch("shutil.which", return_value="/usr/local/bin/hyprctl"), patch(
        "subprocess.run", return_value=MagicMock(returncode=1, stdout="")
    ):
        assert get_active_window_geometry() is None


def test_build_grim_command(tmp_path: Path) -> None:
    out = tmp_path / "test.png"
    cmd_full = build_grim_command(output_path=out)
    assert cmd_full == ["grim", "-t", "png", str(out)]

    cmd_area = build_grim_command(
        output_path=out,
        geometry="100,100 200x200",
        include_cursor=True,
    )
    assert cmd_area == ["grim", "-c", "-g", "100,100 200x200", "-t", "png", str(out)]


def test_copy_image_to_clipboard(tmp_path: Path) -> None:
    img = tmp_path / "test.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n...")

    with patch("shutil.which", return_value="/usr/local/bin/wl-copy"), patch(
        "subprocess.run", return_value=MagicMock(returncode=0)
    ) as mock_run:
        assert copy_image_to_clipboard(img) is True
        assert mock_run.called
        assert mock_run.call_args[0][0] == ["wl-copy", "--type", "image/png"]


def test_send_screenshot_notification(tmp_path: Path) -> None:
    img = tmp_path / "test.png"
    img.write_text("image")
    with patch("shutil.which", return_value="/usr/local/bin/notify-send"), patch(
        "subprocess.Popen"
    ) as mock_popen:
        send_screenshot_notification(img, "Saved to test.png")
        assert mock_popen.called
        args = mock_popen.call_args[0][0]
        assert "notify-send" in args
        assert "-i" in args
        assert str(img) in args


def test_open_screenshot_in_editor(tmp_path: Path) -> None:
    img = tmp_path / "test.png"
    with patch("shutil.which", side_effect=lambda name: "/usr/local/bin/swappy" if name == "swappy" else None), patch(
        "subprocess.Popen"
    ) as mock_popen:
        assert open_screenshot_in_editor(img) is True
        assert mock_popen.call_args[0][0] == ["swappy", "-f", str(img)]


def test_open_screenshots_folder(tmp_path: Path) -> None:
    folder = tmp_path / "Screenshots"
    with patch("shutil.which", side_effect=lambda name: "/usr/local/bin/thunar" if name == "thunar" else None), patch(
        "subprocess.Popen"
    ) as mock_popen:
        assert open_screenshots_folder(folder) is True
        assert mock_popen.call_args[0][0] == ["thunar", str(folder)]


def test_capture_screenshot_missing_grim() -> None:
    with patch("shutil.which", return_value=None):
        res = capture_screenshot(mode="full", notify=False)
        assert res["status"] == "error"
        assert "grim" in res["message"]


def test_capture_screenshot_full_success(tmp_path: Path) -> None:
    out = tmp_path / "shot.png"

    def mock_which(cmd: str) -> str | None:
        if cmd in ("grim", "wl-copy", "notify-send"):
            return f"/usr/local/bin/{cmd}"
        return None

    def fake_subprocess_run(cmd, *args, **kwargs):
        if cmd[0] == "grim":
            out.write_bytes(b"\x89PNG\r\n\x1a\n")
            return MagicMock(returncode=0, stderr="")
        if cmd[0] == "wl-copy":
            return MagicMock(returncode=0)
        return MagicMock(returncode=0)

    with patch("shutil.which", side_effect=mock_which), patch(
        "subprocess.run", side_effect=fake_subprocess_run
    ) as mock_run:
        res = capture_screenshot(mode="full", target="both", output=out, notify=False)
        assert res["status"] == "success"
        assert res["mode"] == "full"
        assert res["path"] == str(out)
        assert res["copied"] is True
        assert mock_run.called


def test_capture_screenshot_area_cancelled() -> None:
    def mock_which(cmd: str) -> str | None:
        if cmd in ("grim", "slurp"):
            return f"/usr/local/bin/{cmd}"
        return None

    # Slurp returns returncode=1 when user cancels selection (e.g. Escape)
    with patch("shutil.which", side_effect=mock_which), patch(
        "subprocess.run", return_value=MagicMock(returncode=1, stdout="")
    ):
        res = capture_screenshot(mode="area", notify=False)
        assert res["status"] == "cancelled"


def test_capture_screenshot_area_success(tmp_path: Path) -> None:
    out = tmp_path / "shot_area.png"

    def mock_which(cmd: str) -> str | None:
        if cmd in ("grim", "slurp", "wl-copy"):
            return f"/usr/local/bin/{cmd}"
        return None

    def fake_subprocess_run(cmd, *args, **kwargs):
        if cmd[0] == "slurp":
            return MagicMock(returncode=0, stdout="10,20 300x400\n")
        if cmd[0] == "grim":
            return MagicMock(returncode=0, stderr="")
        if cmd[0] == "wl-copy":
            return MagicMock(returncode=0)
        return MagicMock(returncode=0)

    with patch("shutil.which", side_effect=mock_which), patch(
        "subprocess.run", side_effect=fake_subprocess_run
    ):
        res = capture_screenshot(mode="area", target="save", output=out, notify=False)
        assert res["status"] == "success"
        assert res["geometry"] == "10,20 300x400"
        assert res["path"] == str(out)


def test_screenshot_menu_entries() -> None:
    entries = build_screenshot_menu_entries()
    assert len(entries) >= 9
    ids = {e["id"] for e in entries}
    assert "area" in ids
    assert "full" in ids
    assert "window" in ids
    assert "area_clipboard" in ids
    assert "edit" in ids
    assert "open_folder" in ids

    area_entry = next(e for e in entries if e["id"] == "area")
    assert "Selected Area" in area_entry["label"]
    assert area_entry["mode"] == "area"
    assert area_entry["target"] == "both"


def test_cli_screenshot_parser() -> None:
    parser = build_parser()

    # detech screenshot
    args = parser.parse_args(["screenshot"])
    assert args.command == "screenshot"
    assert args.mode == "menu"
    assert args.target == "both"

    # detech screenshot area -t copy
    args_area = parser.parse_args(["screenshot", "area", "-t", "copy", "-c", "--no-notify"])
    assert args_area.mode == "area"
    assert args_area.target == "copy"
    assert args_area.cursor is True
    assert args_area.no_notify is True

    # detech screenshot window -d 3
    args_win = parser.parse_args(["screenshot", "window", "-d", "3", "--json"])
    assert args_win.mode == "window"
    assert args_win.delay == 3
    assert args_win.json is True

    # detech menu screenshot
    args_menu = parser.parse_args(["menu", "screenshot"])
    assert args_menu.command == "menu"
    assert args_menu.menu_name == "screenshot"

    # detech set screenshot-dir /tmp/shots
    args_set = parser.parse_args(["set", "screenshot-dir", "/tmp/shots"])
    assert args_set.command == "set"
    assert args_set.target == "screenshot-dir"
    assert args_set.value == "/tmp/shots"
