#!/bin/sh
# DETech FreeBSD Bootstrap & Installer Script
# Usage: sh scripts/install-freebsd.sh [--dry-run]

set -eu

DRY_RUN=0
if [ "${1:-}" = "--dry-run" ]; then
    DRY_RUN=1
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_DEST="${XDG_CONFIG_HOME:-$HOME/.config}/detech"
PRIV_CMD="doas"
if ! command -v doas >/dev/null 2>&1; then
    PRIV_CMD="sudo"
fi

FREEBSD_PACKAGES="
    hyprland
    hyprlock
    hypridle
    hyprpaper
    waybar
    rofi-wayland
    kitty
    starship
    dunst
    wl-clipboard
    cliphist
    seatd
    dbus
    fontconfig
    nerd-fonts
    papirus-icon-theme
    qt5ct
    qt6ct
    py311-pillow
"

echo "========================================================"
echo "  DETech — FreeBSD Hyprland Desktop Environment Setup"
echo "========================================================"

OS_NAME="$(uname -s)"
if [ "$OS_NAME" != "FreeBSD" ]; then
    echo "[!] Notice: Current OS is '$OS_NAME' (DETech targets FreeBSD)."
fi

run_cmd() {
    if [ "$DRY_RUN" -eq 1 ]; then
        echo "[dry-run] $*"
    else
        "$@"
    fi
}

if [ "$OS_NAME" = "FreeBSD" ]; then
    echo "[1/4] Installing FreeBSD packages via pkg..."
    # shellcheck disable=SC2086
    run_cmd "$PRIV_CMD" pkg install -y $FREEBSD_PACKAGES

    echo "[2/4] Verifying FreeBSD /etc/rc.conf services (seatd & dbus)..."
    for svc in dbus seatd; do
        if ! sysrc -n "${svc}_enable" 2>/dev/null | grep -qi "YES"; then
            run_cmd "$PRIV_CMD" sysrc "${svc}_enable=YES"
            run_cmd "$PRIV_CMD" service "$svc" start || true
        fi
    done
else
    echo "[1/4] Skipping FreeBSD pkg installation on non-FreeBSD host."
    echo "[2/4] Skipping FreeBSD rc.conf service check on non-FreeBSD host."
fi

echo "[3/4] Seeding user declarative Lua configs into $CONFIG_DEST..."
run_cmd mkdir -p "$CONFIG_DEST"
for lua_file in "$REPO_ROOT"/configs/lua/*.lua; do
    base_name="$(basename "$lua_file")"
    if [ ! -f "$CONFIG_DEST/$base_name" ]; then
        run_cmd cp "$lua_file" "$CONFIG_DEST/$base_name"
        echo "  -> Installed $CONFIG_DEST/$base_name"
    else
        echo "  -> Preserved existing $CONFIG_DEST/$base_name"
    fi
done

echo "[4/4] Installing DETech Python package and compiling initial configs..."
if [ "$DRY_RUN" -eq 0 ]; then
    python3 -m pip install --user -e "$REPO_ROOT" || true
    PYTHONPATH="$REPO_ROOT/src" python3 -m detech.cli apply --no-reload
else
    echo "[dry-run] python3 -m pip install --user -e $REPO_ROOT"
    echo "[dry-run] PYTHONPATH=$REPO_ROOT/src python3 -m detech.cli apply --no-reload"
fi

echo ""
echo "✓ DETech installation complete! Start Hyprland or run 'detech status'."
