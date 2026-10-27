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
    swaybg
    waybar
    rofi
    kitty
    zsh
    zsh-autosuggestions
    zsh-syntax-highlighting
    zsh-completions
    starship
    neofetch
    playerctl
    curl
    dunst
    grim
    slurp
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
    ly
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
    echo "[1/5] Checking and installing FreeBSD packages via pkg..."
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

    echo "[2/5] Verifying FreeBSD services & Ly login manager..."
    for svc in dbus seatd; do
        if ! sysrc -n "${svc}_enable" 2>/dev/null | grep -qi "YES"; then
            run_cmd "$PRIV_CMD" sysrc "${svc}_enable=YES"
            run_cmd "$PRIV_CMD" service "$svc" start || true
        else
            echo "  -> Service '$svc' is already enabled."
        fi
    done

    # Setup Ly gettytab wrapper entry if missing or using un-wrapped binary
    if ! grep -q "ly_wrapper" /etc/gettytab 2>/dev/null; then
        echo "  -> Configuring Ly in /etc/gettytab (using ly_wrapper)..."
        if grep -q "Ly:" /etc/gettytab 2>/dev/null; then
            run_cmd "$PRIV_CMD" sed -i '' '/^Ly:/,/^# End/d' /etc/gettytab 2>/dev/null || true
        fi
        run_cmd "$PRIV_CMD" sh -c "cat << 'EOF' >> /etc/gettytab

Ly:\
	:lo=/usr/local/bin/ly_wrapper:\
	:al=root:
# End Ly entry
EOF"
    fi

    # Ensure /etc/ttys has ttyv1 configured for Ly
    if ! grep -E "ttyv1.*getty Ly" /etc/ttys 2>/dev/null | grep -qv "^#"; then
        echo "  -> Enabling Ly on ttyv1 in /etc/ttys..."
        run_cmd "$PRIV_CMD" sed -i '' 's/^[#]*ttyv1.*/ttyv1\t"\/usr\/libexec\/getty Ly"\t\txterm\tonifexists secure/' /etc/ttys
    fi

    # Install DETech session desktop file into /usr/local/share/wayland-sessions
    run_cmd "$PRIV_CMD" mkdir -p /usr/local/share/wayland-sessions
    run_cmd "$PRIV_CMD" sh -c "cat > /usr/local/share/wayland-sessions/detech.desktop <<'EOF'
[Desktop Entry]
Name=DETech
Comment=Desktop Environment Technology for FreeBSD (Hyprland)
Exec=/usr/local/bin/detech session
Type=Application
DesktopNames=DETech;Hyprland
Keywords=tiling;wayland;compositor;detech;hyprland;
EOF"
    echo "  -> Installed /usr/local/share/wayland-sessions/detech.desktop"
else
    echo "[1/5] Skipping FreeBSD pkg installation on non-FreeBSD host."
    echo "[2/5] Skipping FreeBSD rc.conf service check on non-FreeBSD host."
fi

echo "[3/5] Seeding user declarative Lua configs into $CONFIG_DEST..."
run_cmd mkdir -p "$CONFIG_DEST"
for lua_file in "$REPO_ROOT"/configs/lua/*.lua; do
    base_name="$(basename "$lua_file")"
    run_cmd cp "$lua_file" "$CONFIG_DEST/$base_name"
    echo "  -> Installed $CONFIG_DEST/$base_name"
done

echo "[4/5] Installing DETech Python 3.12 package and compiling initial configs..."
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
    # Symlink /usr/local/etc/ly/config.ini to generated user config for live syncing
    if [ "$OS_NAME" = "FreeBSD" ] && [ -f "$CONFIG_DEST/generated/ly/config.ini" ]; then
        if [ ! -L "/usr/local/etc/ly/config.ini" ]; then
            run_cmd "$PRIV_CMD" mkdir -p /usr/local/etc/ly
            run_cmd "$PRIV_CMD" ln -sf "$CONFIG_DEST/generated/ly/config.ini" /usr/local/etc/ly/config.ini || true
            echo "  -> Symlinked /usr/local/etc/ly/config.ini to $CONFIG_DEST/generated/ly/config.ini"
        fi
    fi
else
    echo "[dry-run] $PYTHON_BIN -m pip install --user -e $REPO_ROOT"
    echo "[dry-run] PYTHONPATH=$REPO_ROOT/src $PYTHON_BIN -m detech.cli apply --no-reload"
fi

echo "[5/5] Configuring default shell (Zsh) and interactive shell startup hook..."
CURRENT_USER="${SUDO_USER:-${USER:-$(whoami)}}"
USER_HOME="${HOME:-$(getent passwd "$CURRENT_USER" 2>/dev/null | cut -d: -f6)}"

ZSH_BIN=""
if [ -x "/usr/local/bin/zsh" ]; then
    ZSH_BIN="/usr/local/bin/zsh"
elif command -v zsh >/dev/null 2>&1; then
    ZSH_BIN="$(command -v zsh)"
elif [ -x "/bin/zsh" ]; then
    ZSH_BIN="/bin/zsh"
elif [ -x "/usr/bin/zsh" ]; then
    ZSH_BIN="/usr/bin/zsh"
fi

if [ -n "$ZSH_BIN" ]; then
    # Ensure Zsh is listed in /etc/shells
    if [ -f /etc/shells ] && ! grep -qFx "$ZSH_BIN" /etc/shells 2>/dev/null; then
        echo "  -> Adding $ZSH_BIN to /etc/shells..."
        run_cmd "$PRIV_CMD" sh -c "echo '$ZSH_BIN' >> /etc/shells"
    fi

    # Set default shell for target user if not already zsh
    CURRENT_SHELL="$(getent passwd "$CURRENT_USER" 2>/dev/null | cut -d: -f7 || true)"
    if [ -z "$CURRENT_SHELL" ] && [ -f /etc/passwd ]; then
        CURRENT_SHELL="$(grep -E "^${CURRENT_USER}:" /etc/passwd 2>/dev/null | cut -d: -f7 || true)"
    fi

    if [ "$CURRENT_SHELL" != "$ZSH_BIN" ]; then
        echo "  -> Setting default shell to $ZSH_BIN for user '$CURRENT_USER'..."
        if [ "$OS_NAME" = "FreeBSD" ] && command -v pw >/dev/null 2>&1; then
            run_cmd "$PRIV_CMD" pw usermod "$CURRENT_USER" -s "$ZSH_BIN"
        elif command -v chsh >/dev/null 2>&1; then
            run_cmd chsh -s "$ZSH_BIN" "$CURRENT_USER" 2>/dev/null || run_cmd "$PRIV_CMD" chsh -s "$ZSH_BIN" "$CURRENT_USER"
        elif command -v usermod >/dev/null 2>&1; then
            run_cmd "$PRIV_CMD" usermod -s "$ZSH_BIN" "$CURRENT_USER"
        fi
        echo "  -> Default login shell successfully updated to $ZSH_BIN."
    else
        echo "  -> Default shell for '$CURRENT_USER' is already $ZSH_BIN."
    fi
else
    echo "  [!] Notice: Zsh binary not found. Please verify zsh package installation."
fi

# Ensure ~/.zshrc exists (prevents first-time zsh-newuser-install wizard from blocking startup)
SHELL_INIT_LINE='[ -f "${XDG_CONFIG_HOME:-$HOME/.config}/detech/shell-init.sh" ] && . "${XDG_CONFIG_HOME:-$HOME/.config}/detech/shell-init.sh"'
ZSHRC="$USER_HOME/.zshrc"
if [ ! -f "$ZSHRC" ]; then
    echo "  -> Initializing $ZSHRC with DETech Neofetch + Starship hook..."
    if [ "$DRY_RUN" -eq 1 ]; then
        echo "[dry-run] create $ZSHRC with DETech shell hook"
    else
        cat > "$ZSHRC" <<'EOF'
# DETech Interactive Shell Configuration (Zsh)
# Initializes Starship prompt, autocompletions, autosuggestions, syntax highlighting, and Neofetch
[ -f "${XDG_CONFIG_HOME:-$HOME/.config}/detech/shell-init.sh" ] && . "${XDG_CONFIG_HOME:-$HOME/.config}/detech/shell-init.sh"
EOF
    fi
fi

# Ensure DETech shell hook is present across shell rc files
for rc_file in "$USER_HOME/.zshrc" "$USER_HOME/.bashrc" "$USER_HOME/.profile" "$USER_HOME/.shrc"; do
    if [ -f "$rc_file" ] && ! grep -q "detech/shell-init.sh" "$rc_file" 2>/dev/null; then
        if [ "$DRY_RUN" -eq 1 ]; then
            echo "[dry-run] append DETech shell hook to $rc_file"
        else
            printf "\n# DETech Neofetch & Starship Shell Hook\n%s\n" "$SHELL_INIT_LINE" >> "$rc_file"
            echo "  -> Added DETech shell hook (Neofetch + Starship) to $rc_file"
        fi
    fi
done

echo ""
echo "✓ DETech installation complete! Start Hyprland or run 'detech status'."
