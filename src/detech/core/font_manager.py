"""Nerd Fonts Manager for DETech.

Provides:
- Curated catalog of 16+ popular Nerd Fonts with release metadata
- System font discovery via `fc-list : family` on FreeBSD
- One-click Nerd Font installation into `~/.local/share/fonts/NerdFonts/` or via FreeBSD `pkg`
- Font resolution for all DETech generators (Kitty, Waybar, Rofi, Hyprlock, Dunst, GTK, Qt)
"""

from __future__ import annotations

import os
import shutil
import subprocess
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class NerdFontSpec:
    """Metadata for a supported Nerd Font family."""

    family: str
    propo_family: str
    archive_name: str
    style_hint: str
    sample_glyphs: str = "󰣠    󰂄"


NERD_FONT_CATALOG: list[NerdFontSpec] = [
    NerdFontSpec("JetBrainsMono Nerd Font", "JetBrainsMono Nerd Font Propo", "JetBrainsMono", "Crisp ligatures & IDE favorite"),
    NerdFontSpec("FiraCode Nerd Font", "FiraCode Nerd Font Propo", "FiraCode", "Classic programming ligatures"),
    NerdFontSpec("CaskaydiaCove Nerd Font", "CaskaydiaCove Nerd Font Propo", "CascadiaCode", "Microsoft Cascadia with cursive italics"),
    NerdFontSpec("Hack Nerd Font", "Hack Nerd Font Propo", "Hack", "High-legibility workhorse monospace"),
    NerdFontSpec("Iosevka Nerd Font", "Iosevka Nerd Font Propo", "Iosevka", "Slender, space-efficient coding font"),
    NerdFontSpec("MesloLGS Nerd Font", "MesloLGS Nerd Font Propo", "Meslo", "Powerlevel10k & Starship classic"),
    NerdFontSpec("GeistMono Nerd Font", "GeistMono Nerd Font Propo", "GeistMono", "Modern neo-grotesque technical mono"),
    NerdFontSpec("0xProto Nerd Font", "0xProto Nerd Font Propo", "0xProto", "Futuristic distinctive glyph shapes"),
    NerdFontSpec("CommitMono Nerd Font", "CommitMono Nerd Font Propo", "CommitMono", "Neutral smart-kerning coding font"),
    NerdFontSpec("Mononoki Nerd Font", "Mononoki Nerd Font Propo", "Mononoki", "Rounded friendly code font"),
    NerdFontSpec("UbuntuMono Nerd Font", "UbuntuMono Nerd Font Propo", "UbuntuMono", "Warm humanistic monospace"),
    NerdFontSpec("SourceCodePro Nerd Font", "SauceCodePro Nerd Font Propo", "SourceCodePro", "Adobe clean monospace"),
    NerdFontSpec("VictorMono Nerd Font", "VictorMono Nerd Font Propo", "VictorMono", "Slender with cursive italics"),
    NerdFontSpec("SpaceMono Nerd Font", "SpaceMono Nerd Font Propo", "SpaceMono", "Retro-futuristic geometric mono"),
    NerdFontSpec("ZedMono Nerd Font", "ZedMono Nerd Font Propo", "ZedMono", "Zed editor custom Iosevka variant"),
    NerdFontSpec("Inconsolata Nerd Font", "Inconsolata Nerd Font Propo", "Inconsolata", "Classic humanist terminal font"),
]

NERD_FONTS_RELEASE_BASE = "https://github.com/ryanoasis/nerd-fonts/releases/latest/download"


def discover_installed_nerd_fonts() -> set[str]:
    """Query `fc-list : family` to detect installed Nerd Font families on the system."""
    if not shutil.which("fc-list"):
        return set()
    try:
        proc = subprocess.run(
            ["fc-list", ":", "family"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        installed: set[str] = set()
        for line in proc.stdout.splitlines():
            for part in line.split(","):
                fam = part.strip()
                if "nerd font" in fam.lower():
                    installed.add(fam)
        return installed
    except Exception:
        return set()


def get_nerd_font_status_list(installed_override: set[str] | None = None) -> list[dict[str, Any]]:
    """Return catalog of Nerd Fonts annotated with installation status."""
    installed = installed_override if installed_override is not None else discover_installed_nerd_fonts()
    installed_lower = {f.lower() for f in installed}

    entries: list[dict[str, Any]] = []
    seen_families: set[str] = set()

    for spec in NERD_FONT_CATALOG:
        is_inst = spec.family.lower() in installed_lower
        entries.append(
            {
                "family": spec.family,
                "propo_family": spec.propo_family,
                "archive_name": spec.archive_name,
                "style_hint": spec.style_hint,
                "installed": is_inst,
            }
        )
        seen_families.add(spec.family.lower())

    # Also include any extra Nerd Fonts discovered via fc-list
    for fam in sorted(installed):
        if fam.lower() not in seen_families and not fam.lower().endswith("propo") and not fam.lower().endswith("mono"):
            entries.append(
                {
                    "family": fam,
                    "propo_family": f"{fam} Propo",
                    "archive_name": "",
                    "style_hint": "System installed Nerd Font",
                    "installed": True,
                }
            )
    return entries


def get_user_fonts_dir() -> Path:
    """Return user fonts directory (`~/.local/share/fonts/NerdFonts`)."""
    xdg_data = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    return Path(xdg_data) / "fonts" / "NerdFonts"


def install_nerd_font(
    font_family_or_archive: str,
    target_dir: Path | None = None,
) -> Path:
    """Download and install a Nerd Font archive into `~/.local/share/fonts/NerdFonts/<name>`."""
    archive_name = font_family_or_archive
    for spec in NERD_FONT_CATALOG:
        if spec.family.lower() == font_family_or_archive.lower() or spec.archive_name.lower() == font_family_or_archive.lower():
            archive_name = spec.archive_name
            break

    dest_root = target_dir or get_user_fonts_dir()
    font_dir = dest_root / archive_name
    font_dir.mkdir(parents=True, exist_ok=True)

    url = f"{NERD_FONTS_RELEASE_BASE}/{archive_name}.zip"
    zip_path = font_dir / f"{archive_name}.zip"

    urllib.request.urlretrieve(url, zip_path)
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():
            if member.lower().endswith((".ttf", ".otf")):
                zf.extract(member, font_dir)
    zip_path.unlink(missing_ok=True)

    if shutil.which("fc-cache"):
        subprocess.run(["fc-cache", "-fv", str(font_dir)], check=False, capture_output=True)

    return font_dir


def resolve_font_settings(context: dict[str, Any]) -> dict[str, Any]:
    """Return normalized font settings dictionary for all config generators."""
    fonts_cfg = context.get("config", {}).get("fonts", {})
    mono = str(fonts_cfg.get("mono", "JetBrainsMono Nerd Font"))
    sans = str(fonts_cfg.get("sans", f"{mono} Propo" if not mono.endswith("Propo") else mono))
    size = int(fonts_cfg.get("size", 11))
    bar_size = int(fonts_cfg.get("bar_size", size))
    rofi_size = int(fonts_cfg.get("rofi_size", size + 1))
    lock_size = int(fonts_cfg.get("lock_size", 48))

    return {
        "mono": mono,
        "sans": sans,
        "size": size,
        "bar_size": bar_size,
        "rofi_size": rofi_size,
        "lock_size": lock_size,
    }
