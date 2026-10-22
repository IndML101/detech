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
    rofi
    kitty
    starship
    neofetch
    playerctl
    curl
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
    python312
    py312-pillow
"

PYTHON_BIN="python3.12"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    PYTHON_BIN="python3"
fi

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
    echo "[1/4] Checking and installing FreeBSD packages via pkg..."
    MISSING_PACKAGES=""
    for pkg_name in $FREEBSD_PACKAGES; do
        if [ "$DRY_RUN" -eq 1 ] || ! pkg info -e "$pkg_name" >/dev/null 2>&1; then
            MISSING_PACKAGES="$MISSING_PACKAGES $pkg_name"
        fi
    done
    if [ -n "$MISSING_PACKAGES" ]; then
        # shellcheck disable=SC2086
        run_cmd "$PRIV_CMD" pkg install -y $MISSING_PACKAGES
    else
        echo "  -> All required FreeBSD packages are already installed."
    fi

    echo "[2/4] Verifying FreeBSD /etc/rc.conf services (seatd & dbus)..."
    for svc in dbus seatd; do
        if ! sysrc -n "${svc}_enable" 2>/dev/null | grep -qi "YES"; then
            run_cmd "$PRIV_CMD" sysrc "${svc}_enable=YES"
            run_cmd "$PRIV_CMD" service "$svc" start || true
        else
            echo "  -> Service '$svc' is already enabled."
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
    run_cmd cp "$lua_file" "$CONFIG_DEST/$base_name"
    echo "  -> Installed $CONFIG_DEST/$base_name"
done

echo "[4/4] Installing DETech Python 3.12 package and compiling initial configs..."
if [ "$DRY_RUN" -eq 0 ]; then
    if command -v python3.12 >/dev/null 2>&1; then
        PYTHON_BIN="python3.12"
    fi
    "$PYTHON_BIN" -m pip install --user --break-system-packages -e "$REPO_ROOT" 2>/dev/null \
        || "$PYTHON_BIN" -m pip install --user -e "$REPO_ROOT" 2>/dev/null \
        || true
    for bin_dir in "$HOME/.local/bin" "$HOME/bin"; do
        mkdir -p "$bin_dir"
        cat > "$bin_dir/detech" <<EOF
#!/bin/sh
PYTHONPATH="$REPO_ROOT/src\${PYTHONPATH:+:\$PYTHONPATH}" exec $PYTHON_BIN -m detech.cli "\$@"
EOF
        chmod +x "$bin_dir/detech"
        echo "  -> Installed CLI launcher $bin_dir/detech (using $PYTHON_BIN)"
    done
    export PATH="$HOME/.local/bin:$HOME/bin:$PATH"
    if [ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]; then
        PYTHONPATH="$REPO_ROOT/src" "$PYTHON_BIN" -m detech.cli apply
    else
        PYTHONPATH="$REPO_ROOT/src" "$PYTHON_BIN" -m detech.cli apply --no-reload
    fi
    SHELL_INIT_LINE='[ -f "${XDG_CONFIG_HOME:-$HOME/.config}/detech/shell-init.sh" ] && . "${XDG_CONFIG_HOME:-$HOME/.config}/detech/shell-init.sh"'
    for rc_file in "$HOME/.profile" "$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.shrc"; do
        if [ -f "$rc_file" ] && ! grep -q "detech/shell-init.sh" "$rc_file" 2>/dev/null; then
            printf "\n# DETech Neofetch & Starship Shell Hook\n%s\n" "$SHELL_INIT_LINE" >> "$rc_file"
            echo "  -> Added DETech shell hook (Neofetch + Starship) to $rc_file"
        fi
    done
else
    echo "[dry-run] $PYTHON_BIN -m pip install --user -e $REPO_ROOT"
    echo "[dry-run] PYTHONPATH=$REPO_ROOT/src $PYTHON_BIN -m detech.cli apply --no-reload"
fi

echo ""
echo "✓ DETech installation complete! Start Hyprland or run 'detech status'."
