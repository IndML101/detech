"""Runtime state management for DETech."""

from __future__ import annotations

import copy
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from detech.core.lua_loader import load_all_user_configs
from detech.core.paths import get_state_file


@dataclass
class RuntimeState:
    """Mutable runtime selections persisted in state.json."""

    theme: str | None = None
    wallpaper: str | None = None
    dynamic_wallpaper_colors: bool | None = None
    waybar_layout: str | None = None
    rofi_layout: str | None = None
    starship_preset: str | None = None
    hyprlock_layout: str | None = None
    plugin_preset: str | None = None
    icon_theme: str | None = None
    font_mono: str | None = None
    font_sans: str | None = None
    font_size: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


def load_state(state_path: Path | None = None) -> RuntimeState:
    """Load runtime state from state.json, returning empty state if missing."""
    path = state_path or get_state_file()
    if not path.is_file():
        return RuntimeState()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        allowed = {f for f in RuntimeState.__dataclass_fields__}
        filtered = {k: v for k, v in raw.items() if k in allowed}
        return RuntimeState(**filtered)
    except Exception:
        return RuntimeState()


def save_state(state: RuntimeState, state_path: Path | None = None) -> Path:
    """Persist runtime state to state.json atomically."""
    path = state_path or get_state_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(state.to_dict(), indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(path)
    return path


def update_state(state_path: Path | None = None, **updates: Any) -> RuntimeState:
    """Update specific fields in runtime state and save."""
    state = load_state(state_path)
    for key, value in updates.items():
        if hasattr(state, key):
            setattr(state, key, value)
    save_state(state, state_path)
    return state


def get_effective_context(state_path: Path | None = None) -> dict[str, Any]:
    """Merge declarative Lua configs with runtime state overrides."""
    configs = copy.deepcopy(load_all_user_configs())
    state = load_state(state_path)

    cfg = configs.setdefault("config", {})
    appearance = cfg.setdefault("appearance", {})
    fonts = cfg.setdefault("fonts", {})

    if state.theme is not None:
        appearance["theme"] = state.theme
    if state.dynamic_wallpaper_colors is not None:
        appearance["dynamic_wallpaper_colors"] = state.dynamic_wallpaper_colors
    if state.waybar_layout is not None:
        appearance["waybar_layout"] = state.waybar_layout
    if state.rofi_layout is not None:
        appearance["rofi_layout"] = state.rofi_layout
    if state.starship_preset is not None:
        appearance["starship_preset"] = state.starship_preset
    if state.hyprlock_layout is not None:
        appearance["hyprlock_layout"] = state.hyprlock_layout
    if state.plugin_preset is not None:
        plugins_cfg = configs.setdefault("plugins", {})
        plugins_cfg["preset"] = state.plugin_preset
    if state.icon_theme is not None:
        appearance["icon_theme"] = state.icon_theme
    if state.wallpaper is not None:
        appearance["wallpaper"] = state.wallpaper

    if state.font_mono is not None:
        fonts["mono"] = state.font_mono
    if state.font_sans is not None:
        fonts["sans"] = state.font_sans
    if state.font_size is not None:
        fonts["size"] = int(state.font_size)
        fonts["bar_size"] = int(state.font_size)
        fonts["rofi_size"] = int(state.font_size) + 1

    configs["runtime_state"] = state.to_dict()
    return configs
