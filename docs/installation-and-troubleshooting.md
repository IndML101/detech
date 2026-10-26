# FreeBSD Installation & Troubleshooting Guide

This guide details the complete installation workflow, system prerequisites, permissions, and troubleshooting steps for running **DETech** on FreeBSD.

---

## 1. System Prerequisites & Hardware Setup

Before launching Hyprland on FreeBSD, ensure your kernel graphics drivers and session daemons are configured.

### Graphics Drivers (`drm-kmod`)

Install the appropriate DRM kernel module package for your GPU:

```sh
# For modern Intel or AMD GPUs
sudo pkg install -y drm-kmod
```

Add the driver to `/etc/rc.conf` so it loads on boot:

- **Intel Integrated Graphics (Gen 4 to Gen 12+)**:
  ```sh
  sudo sysrc kld_list+="i915kms"
  ```
- **AMD Radeon (GCN / RDNA)**:
  ```sh
  sudo sysrc kld_list+="amdgpu"
  ```

Load the module immediately without rebooting:
```sh
sudo kldload /boot/modules/i915kms.ko   # Or amdgpu.ko
```
Verify with `kldstat | grep -E "i915|amdgpu|drm"`.

### User Groups & Permissions

Your user account **must** be a member of the `video` and `wheel` groups:

```sh
sudo pw groupmod video -m "$USER"
sudo pw groupmod wheel -m "$USER"
```

Verify your memberships with `groups` or `id`.

---

## 2. Automated Installation

### Step 1: Run the Bootstrap Script

Clone the DETech repository and run the FreeBSD installer:

```sh
git clone https://github.com/your-repo/DETech.git
cd DETech
sh scripts/install-freebsd.sh
```

The script will:
1. Verify FreeBSD OS.
2. Install required packages via `pkg` (`hyprland`, `hyprlock`, `hypridle`, `hyprpaper`, `waybar`, `rofi`, `kitty`, `starship`, `neofetch`, `playerctl`, `dunst`, `wl-clipboard`, `cliphist`, `seatd`, `dbus`, `fontconfig`, `nerd-fonts`, `papirus-icon-theme`, `qt5ct`, `qt6ct`, `python312`, `py312-pillow`, and `ly`).
3. Enable and start `seatd` and `dbus` services in `/etc/rc.conf`.
4. Install the Wayland session desktop file `/usr/local/share/wayland-sessions/detech.desktop`.
5. Seed your declarative configuration into `~/.config/detech/`.
6. Compile all configurations and install the `detech` launcher script.

---

## 3. Ly TUI Login Manager Setup

DETech provides full integration with the **Ly TUI Display Manager** on FreeBSD:

```sh
sudo sh scripts/setup-ly.sh
```

This script:
1. Configures `/etc/gettytab` with the `Ly:` definition invoking `/usr/local/bin/ly_wrapper`.
2. Enables `ttyv1` in `/etc/ttys` for automatic display manager startup on virtual terminal 2 (`Ctrl + Alt + F2`).
3. Symlinks `/usr/local/etc/ly/config.ini` to your user-compiled config in `~/.config/detech/generated/ly/config.ini`.

Now on every boot, Ly displays a themed login screen featuring your chosen color palette and TUI animation (`matrix`, `doom`, etc.).

---

## 4. Privilege Elevation Configuration (`doas`)

DETech uses `doas` by default for FreeBSD package management (`pkg`) and ACPI power management (`acpiconf`).

Create or edit `/usr/local/etc/doas.conf`:

```
# Allow user to run acpiconf for suspend/sleep without password prompt
permit nopass keepenv :video cmd acpiconf
permit nopass keepenv :video cmd /usr/sbin/acpiconf

# Allow wheel members to run pkg install / update
permit :wheel cmd pkg
permit :wheel cmd /usr/sbin/pkg

# General admin privileges
permit :wheel
```

Test with:
```sh
doas acpiconf -i batt
```

---

## 5. Starting the Desktop

### Method A: Via Ly Display Manager (Recommended)
Switch to `ttyv1` (`Ctrl + Alt + F2`), choose **DETech** in the session selector (`F2`), enter your credentials, and hit Enter.

### Method B: Directly from TTY Console
From any virtual console (`ttyv0`), run:
```sh
detech session
```
This automatically compiles your latest Lua configurations and launches Hyprland.

---

## 6. Common Issues & Troubleshooting

### Issue: Hyprland crashes on startup with `[CRITICAL] failed to open drm device`
- **Cause**: Graphics driver module is not loaded or user lacks permission to access `/dev/dri/card*`.
- **Fix**:
  1. Check driver: `kldstat | grep -E "i915|amdgpu|drm"`
  2. Verify user in `video` group: `id | grep video`
  3. Ensure device exists: `ls -la /dev/dri/`

### Issue: `seatd: connection refused` or `seatd: error opening socket`
- **Cause**: The `seatd` daemon is not running or socket permissions are restricted.
- **Fix**:
  ```sh
  sudo service seatd restart
  sudo sysrc seatd_enable="YES"
  ```
  Ensure user is in `video` group (FreeBSD `seatd` grants access to `video` group members).

### Issue: Volume keys do not change sound or no audio device detected
- **Cause**: The default FreeBSD OSS audio unit might not point to your active output.
- **Fix**:
  1. List audio devices: `cat /dev/sndstat`
  2. Set default PCM unit (e.g. unit 1 for headphones/speakers):
     ```sh
     sudo sysrc hw.snd.default_unit=1
     ```
  3. In `~/.config/detech/freebsd.lua`, set:
     ```lua
     audio = { backend = "mixer", oss_device = "/dev/mixer1", step = 5 }
     ```
  4. Run `detech apply`.

### Issue: Screen brightness keys do not respond
- **Cause**: Backlight driver permissions or multiple backlight controllers.
- **Fix**:
  1. Check available backlight devices: `ls -la /dev/backlight/`
  2. Test command: `/usr/bin/backlight`
  3. If permissions deny non-root access:
     Add `/etc/devfs.rules`:
     ```
     [system=10]
     add path 'backlight/*' mode 0660 group video
     ```
     Enable in `/etc/rc.conf`: `sysrc devfs_system_ruleset="system"` and run `sudo service devfs restart`.

### Issue: Rofi or Waybar displays missing glyphs or square boxes
- **Cause**: Nerd Font symbols are not cached.
- **Fix**:
  1. Run `fc-cache -fv` to refresh font caches.
  2. Switch font:
     ```sh
     detech set font "JetBrainsMono Nerd Font" --size 11
     ```

### Issue: Ly login manager displays blank screen or doesn't launch
- **Cause**: `/etc/ttys` or `/etc/gettytab` was not properly updated.
- **Fix**:
  1. Inspect `/etc/ttys`:
     ```sh
     grep ttyv1 /etc/ttys
     # Expected: ttyv1 "/usr/libexec/getty Ly" xterm onifexists secure
     ```
  2. Inspect `/etc/gettytab`:
     ```sh
     grep -A 3 "Ly:" /etc/gettytab
     # Expected: :lo=/usr/local/bin/ly_wrapper:
     ```
  3. Re-run `sudo sh scripts/setup-ly.sh` and reboot.
