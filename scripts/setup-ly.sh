#!/bin/sh
# DETech FreeBSD Ly Login Manager Configuration Script
# Usage: sudo sh scripts/setup-ly.sh

set -eu

if [ "$(id -u)" -ne 0 ]; then
    echo "[!] Error: This script must be run as root (e.g. 'sudo sh scripts/setup-ly.sh')." >&2
    exit 1
fi

TARGET_USER="${SUDO_USER:-$(logname 2>/dev/null || whoami)}"
USER_HOME="$(getent passwd "$TARGET_USER" | cut -d: -f6)"
CONFIG_FILE="$USER_HOME/.config/detech/generated/ly/config.ini"

echo "========================================================"
echo "  DETech — Ly Login Manager Setup for FreeBSD"
echo "  Target User: $TARGET_USER ($USER_HOME)"
echo "========================================================"

# 1. Verify ly package
if ! pkg info -e ly >/dev/null 2>&1; then
    echo "[1/5] Installing ly package via pkg..."
    pkg install -y ly
else
    echo "[1/5] ly package is already installed."
fi

# 2. Configure /etc/gettytab with ly_wrapper
echo "[2/5] Updating /etc/gettytab to use ly_wrapper..."
if grep -q ":lo=/usr/local/bin/ly_wrapper:" /etc/gettytab 2>/dev/null && ! grep -q "Ly:\\\\n" /etc/gettytab 2>/dev/null; then
    echo "  -> /etc/gettytab already contains properly formatted ly_wrapper entry."
else
    # Remove older/malformed Ly entry if present
    if grep -qi "Ly" /etc/gettytab 2>/dev/null; then
        sed -i '' '/^Ly:/,/^# End/d' /etc/gettytab 2>/dev/null || true
        sed -i '' '/^Ly:\\n/d' /etc/gettytab 2>/dev/null || true
    fi
    cat << 'EOF' >> /etc/gettytab

Ly:\
	:lo=/usr/local/bin/ly_wrapper:\
	:al=root:
# End Ly entry
EOF
    echo "  -> Added Ly with ly_wrapper to /etc/gettytab."
fi

# 3. Configure /etc/ttys for ttyv1
echo "[3/5] Verifying /etc/ttys configuration..."
if grep -E "^ttyv1[[:space:]]+\"/usr/libexec/getty Ly\"" /etc/ttys >/dev/null 2>&1; then
    echo "  -> ttyv1 is already enabled with getty Ly."
else
    sed -i '' 's/^[#]*ttyv1.*/ttyv1\t"\/usr\/libexec\/getty Ly"\t\txterm\tonifexists secure/' /etc/ttys
    echo "  -> Configured ttyv1 in /etc/ttys."
fi

# 4. Install DETech Wayland Session Desktop Entry
echo "[4/5] Installing DETech session desktop entry..."
mkdir -p /usr/local/share/wayland-sessions
cat > /usr/local/share/wayland-sessions/detech.desktop <<'EOF'
[Desktop Entry]
Name=DETech
Comment=Desktop Environment Technology for FreeBSD (Hyprland)
Exec=/usr/local/bin/detech session
Type=Application
DesktopNames=DETech;Hyprland
Keywords=tiling;wayland;compositor;detech;hyprland;
EOF
chmod 644 /usr/local/share/wayland-sessions/detech.desktop
echo "  -> Installed /usr/local/share/wayland-sessions/detech.desktop"

# 5. Link Ly configuration to DETech generated config
echo "[5/5] Symlinking Ly configuration for live theme syncing..."
mkdir -p /usr/local/etc/ly
if [ -f "$CONFIG_FILE" ]; then
    ln -sf "$CONFIG_FILE" /usr/local/etc/ly/config.ini
    chown -h "$TARGET_USER" /usr/local/etc/ly/config.ini 2>/dev/null || true
    echo "  -> Symlinked /usr/local/etc/ly/config.ini -> $CONFIG_FILE"
else
    echo "  -> Note: $CONFIG_FILE not found yet. Run 'detech apply' as $TARGET_USER to compile it."
fi

echo ""
echo "✓ Ly setup completed successfully!"
echo "  Ly will now automatically launch on ttyv1 at boot,"
echo "  theme colors will sync on every 'detech apply',"
echo "  and both DETech and Hyprland will be selectable in the session list."
