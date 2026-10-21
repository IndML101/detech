"""Path resolution for DETech configs, presets, state, and generated outputs."""

from __future__ import annotations

import os
from pathlib import Path


def get_repo_root() -> Path:
    """Return the root directory of the DETech repository/installation."""
    env_root = os.environ.get("DETECH_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    # src/detech/core/paths.py -> repo root is 3 levels up
    return Path(__file__).resolve().parents[3]


def get_user_config_dir() -> Path:
    """Return user's DETech Lua config directory (~/.config/detech)."""
    env_dir = os.environ.get("DETECH_CONFIG_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()
    xdg_config = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    return Path(xdg_config) / "detech"


def get_xdg_config_dir(override: Path | str | None = None) -> Path:
    """Return target XDG ~/.config directory where native configs are emitted."""
    if override is not None:
        return Path(override).expanduser().resolve()
    xdg_config = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    return Path(xdg_config).resolve()


def get_state_file() -> Path:
    """Return path to runtime mutable state file (~/.local/state/detech/state.json)."""
    env_state = os.environ.get("DETECH_STATE_FILE")
    if env_state:
        return Path(env_state).expanduser().resolve()
    xdg_state = os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state"))
    return Path(xdg_state) / "detech" / "state.json"


def get_presets_dir() -> Path:
    """Return path to DETech presets directory."""
    return get_repo_root() / "presets"


def resolve_lua_file(filename: str) -> Path:
    """Resolve a Lua config file from user config dir first, falling back to repo configs/lua/."""
    user_file = get_user_config_dir() / filename
    if user_file.is_file():
        return user_file
    return get_repo_root() / "configs" / "lua" / filename
