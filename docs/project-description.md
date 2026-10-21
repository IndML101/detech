# DETech 

DETech stands for desktop environment technology. It's specifically for freeBSD OS. 
In this project I want to create a desktop environment using hyprland WM and associated tools hypridle, hyprlock, hyprpaper, waybar, rofi etc.
In short I want to rice hyprland using python scripts and lua configs.

## Features 
- It should be keyboard friendly with lot of configurable keyboard shortcuts, and rofi menu for searching and running the shortcut 
- 10 - 20 waybar layouts, which can be switched 
- Waybar widgets for Weather (`wttr.in`), Interactive Calendar, Notifications & Do Not Disturb (`dunstctl`), System Tray (`tray`), FreeBSD Network (`ifconfig`), MPRIS Media (`playerctl`), FreeBSD Kernel & Uptime (`sysctl kern.boottime`), Clipboard History (`cliphist`), ZFS, `pkg`, ACPI Battery, Thermal, Load, Memory, Audio (`mixer`), and Backlight
- Themes with icons, wallpapers, screen lock layout, waybar layout, color schemes - for GTK and QT apps.
- Kitty will be default terminal, displaying FreeBSD & DETech system information via a themed Neofetch configuration (`neofetch`) on interactive terminal startup
- rofi picker for themes, browsing files, picking software, keyboard shortcuts, wallpapers, color scemes, glyph, emojis, calendar, weather forecast, notification center, and clipboard history
- 10 - 20 rofi layouts, for app drawer 
- 10 - 20 cool starship prompts
- icons picker (curated icon packs + automatic discovery of FreeBSD `/usr/local/share/icons` themes synced across GTK-2/3/4, Qt5/6, Rofi, Dunst, and Neofetch)
- modular configuration 
- system wide color schemes should change on picking walpapers and themes

## Inspirations 
- [ML4W](https://github.com/mylinuxforwork/dotfiles)
- [JAKooLit](https://github.com/JaKooLit/Hyprland-Dots)
- [end_4](https://github.com/end-4/dots-hyprland)
- [HyDE](https://github.com/HyDE-Project/HyDE)
- [Omarchy](https://omarchy.org/)
- [Dank Linux](https://github.com/AvengeMedia/DankMaterialShell)
- [Ryoku](https://github.com/Ryoku-dev/ryoku)

**Note: I like HyDE among all of them and Rayoku too**
**Note: Omarchy is the worst, but we'll sttill draw ideas, only good ones**

## Instructions 
- I want to stay in Hypr ecosystem and use hyprland plugins only 
- I want to publish this as an open-source git repo 
- Inspirations are provided to just draw ideas, I don't want to fork them 
- I want to keep a minimalistic setup 
- User customizability using config files is the priority 
- This whole thing is for freeBSD 
