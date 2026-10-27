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
2. Install required packages via `pkg` (`hyprland`, `hyprlock`, `hypridle`, `hyprpaper`, `waybar`, `rofi`, `kitty`, `zsh`, `zsh-autosuggestions`, `zsh-syntax-highlighting`, `zsh-completions`, `starship`, `neofetch`, `playerctl`, `dunst`, `wl-clipboard`, `cliphist`, `seatd`, `dbus`, `fontconfig`, `nerd-fonts`, `papirus-icon-theme`, `qt5ct`, `qt6ct`, `python312`, `py312-pillow`, and `ly`).
3. Enable and start `seatd` and `dbus` services in `/etc/rc.conf`.
4. Install the Wayland session desktop file `/usr/local/share/wayland-sessions/detech.desktop`.
5. Seed your declarative configuration into `~/.config/detech/`.
6. Compile all configurations and install the `detech` launcher script into `~/.local/bin/detech`.
7. Configure **Zsh** as your default login shell:
   - Registers `/usr/local/bin/zsh` in `/etc/shells` if not already present.
   - Sets the user's login shell to `/usr/local/bin/zsh` using FreeBSD `pw usermod`.
   - Pre-seeds `~/.zshrc` with the DETech Neofetch + Starship shell hook (preventing the first-time `zsh-newuser-install` prompt from blocking startup).
   - Appends the shell hook into `~/.zshrc`, `~/.bashrc`, `~/.profile`, and `~/.shrc`.

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
4. Verifies and ensures the user's default login shell is set to `/usr/local/bin/zsh`.

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

## 6. Zsh Shell Experience: Autosuggestions, Completions & Oh My Zsh Integration

DETech configures **Zsh** as your default interactive login shell, fully integrated with Starship prompts, FreeBSD Beastie Neofetch, and Fish-like CLI enhancements.

### Native Plugins (Pre-configured via `pkg`)
The DETech installer automatically installs and wires three native FreeBSD packages:
1. **`zsh-autosuggestions`**: Suggests commands as you type based on your history and completions (press `Right Arrow` or `End` to accept).
2. **`zsh-syntax-highlighting`**: Real-time fish-style command syntax highlighting (green for valid commands, red for unknown commands/syntax errors).
3. **`zsh-completions`**: Additional tab-completion definitions for hundreds of CLI utilities.

### Do We Need Oh My Zsh?
**No.** DETech intentionally does **not** require Oh My Zsh:
- **Startup Latency**: Native FreeBSD packages load in under 15 ms, whereas Oh My Zsh typically introduces 100–300 ms of shell startup latency.
- **Zero Prompt Conflicts**: DETech uses **Starship** with 15 switchable theme presets. Oh My Zsh comes with its own theme engine that can conflict with Starship unless explicitly disabled.
- **Package Management**: Native packages update automatically with FreeBSD `pkg upgrade` without needing separate Git pulls.

### How `shell-init.sh` Automates Everything
You do not need to manually configure `compinit` or plugin paths in `~/.zshrc`. The generated hook `~/.config/detech/shell-init.sh` automatically:
1. Adds `/usr/local/share/zsh-completions` to `$fpath`.
2. Initializes cached Zsh completions via `autoload -Uz compinit && compinit -C`.
3. Discovers and sources `zsh-autosuggestions.zsh`.
4. Discovers and sources `zsh-syntax-highlighting.zsh`.
5. Initializes Starship prompt presets (`eval "$(starship init zsh)"`).
6. Displays FreeBSD Beastie Neofetch system info on interactive launches.

Your `~/.zshrc` simply needs:
```zsh
[ -f "${XDG_CONFIG_HOME:-$HOME/.config}/detech/shell-init.sh" ] && . "${XDG_CONFIG_HOME:-$HOME/.config}/detech/shell-init.sh"
```

### Installing Oh My Zsh Along with DETech (Optional)
If you specifically want Oh My Zsh for its Git aliases, directory navigations, or custom plugins, follow these steps to prevent conflicts with DETech:

1. **Run the Unattended Oh My Zsh Installer**:
   Keep your existing `~/.zshrc` hook and avoid automated shell resets:
   ```sh
   sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended --keep-zshrc
   ```

2. **Disable the Oh My Zsh Theme in `~/.zshrc`**:
   Set `ZSH_THEME=""` so Starship remains the primary prompt renderer:
   ```zsh
   ZSH_THEME=""
   ```

3. **Configure Desired Plugins in `~/.zshrc`**:
   ```zsh
   plugins=(git sudo)
   ```
   *(Note: `zsh-autosuggestions` and `zsh-syntax-highlighting` are already loaded by `shell-init.sh` from native packages, but can also be cloned to `${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/` if preferred.)*

4. **Verify the DETech Hook at the Bottom of `~/.zshrc`**:
   Ensure the DETech initialization line remains at the end of `~/.zshrc`:
   ```zsh
   [ -f "${XDG_CONFIG_HOME:-$HOME/.config}/detech/shell-init.sh" ] && . "${XDG_CONFIG_HOME:-$HOME/.config}/detech/shell-init.sh"
   ```

---

## 7. Common Issues & Troubleshooting

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

### Issue: Verifying or switching default shell to Zsh manually
- **Check active login shell**:
  ```sh
  getent passwd "$USER" | cut -d: -f7
  # Or: echo "$SHELL"
  ```
- **Ensure `/usr/local/bin/zsh` is registered in `/etc/shells`**:
  ```sh
  grep "/usr/local/bin/zsh" /etc/shells
  # If missing, append it:
  echo "/usr/local/bin/zsh" | sudo tee -a /etc/shells
  ```
- **Change default shell to Zsh**:
  ```sh
  sudo pw usermod "$USER" -s /usr/local/bin/zsh
  # Or using chsh:
  chsh -s /usr/local/bin/zsh
  ```
- **Interactive Shell Hook (`Neofetch + Starship`)**:
  Ensure your `~/.zshrc` sources the DETech shell initialization script:
  ```zsh
  [ -f "${XDG_CONFIG_HOME:-$HOME/.config}/detech/shell-init.sh" ] && . "${XDG_CONFIG_HOME:-$HOME/.config}/detech/shell-init.sh"
  ```
  This automatically initializes Starship prompt themes and displays the FreeBSD Beastie Neofetch system banner upon terminal launch.
