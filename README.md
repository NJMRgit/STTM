# Stoned Theme Manager

KDE Plasma theme manager with time-based mode switching. Automatically adjusts wallpaper, window glass tint, rounded-corners outline/shadow colors, fastfetch logo, and OpenRGB lighting profiles based on the time of day.

<img width="2560" height="1440" alt="time" src="https://github.com/user-attachments/assets/fec7936d-c23c-4647-99d1-413a7ec93c71" />


<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/user-attachments/assets/c1c8ab32-b5de-473d-b466-611d6ad87ae5">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/user-attachments/assets/c1c8ab32-b5de-473d-b466-611d6ad87ae5">
  <img alt="Project Logo" src="https://github.com/user-attachments/assets/c1c8ab32-b5de-473d-b466-611d6ad87ae5">
</picture>

## Features

### Customization Options
- **Wallpaper** — Per-theme wallpaper
- **Glass Tint** — Glass tint color 
- **Outline Colors** — rounded-corners outline (active + inactive) 
- **Shadow Colors** — rounded-corners shadow (active + inactive)
- **Fastfetch Logo** — Fastfetch logo file and logo color (Currently Ascii only)
- **OpenRGB Profile** — set RGB lighting profile on per-theme basis


### Automatic Color Generation
- Generates tint/shadow/outline colors from the dominant wallpaper colors when adding wallpaper to a new theme

### Time-Based Modes
- Five default modes: **Morning**, **Noon**, **Afternoon**, **Evening**, **Night**
- Configurable trigger hour for each mode (24-hour format)
- Auto mode: systemd timer or cron checks hourly and applies the correct mode

### Custom themes
- Add custom themes to directly to script or with included GUI
- Enabling custom themes in GUI disables schedule mode 

### Partial Mode Application
- Empty settings in a mode are skipped — previously applied or manually configured values persist
- Apply only the settings you want per mode (e.g., set wallpaper without touching fastfetch logo)
- Enables sparse mode configs: set just tint + wallpaper for morning, just wallpaper for evening, etc.

### Portable Config
- Default config stored at `~/.config/sttm/sttm.conf`
- Launch with `--portable` to use local config (saved alongside `sttm`)
- Schedule file: `~/.blur-schedule` by default, `.blur-schedule` in local dir with `--portable`
- Auto-detects `blsw` next to the GUI in portable mode

### First-Time Setup
- `setup` — interactive ASCII-art installer that configures KDE with the necessary theme elements
- Description of each change

### Automated Installer
- `install` — dependency installer with distro detection (pacman/apt/dnf)
- Handles AUR packages via detected helper (yay, paru, trizen, pikaur, pacaur)

- Installs Darkly, We10X, kwin-effects-glass, KDE-Rounded-Corners, CachyOS-Emerald-KDE

### KDE Plasma Integration
- Applies settings via `kwriteconfig6`, `plasma-apply-wallpaperimage`, and `qdbus6`
- Wayland Only

### Additional Integrations
- **OpenRGB** — load a profile per mode
- **Fastfetch** — per-mode logo and logo color applied to `~/.config/fastfetch/config.jsonc`
- **Yakuake** — When updating theme to a new mode the script will check to see if yakuake is running a program. If it detects a running program it will wait till it's finished then close the yakuake session to update the fastfetch logo

## How to install 

```bash
curl -fsSL -o install.sh "https://raw.githubusercontent.com/NJMRgit/STTM/main/install" && curl -fsSL -o install.sha256 "https://raw.githubusercontent.com/NJMRgit/STTM/main/install.sha256" && sha256sum -c install.sha256 --ignore-missing && sh install.sh
```

## Requirements

- Python 3 + PyQt6
- KDE Plasma 6.6.5
- `openrgb` (optional, for RGB lighting)
- `systemctl --user` or `cronie` (for auto mode scheduling)
- [Glass](https://github.com/4v3ngR/kwin-effects-glass)
- [Darkly](https://github.com/Bali10050/Darkly)
- [KDE-Rounded-Corners](https://github.com/matinlotfali/KDE-Rounded-Corners)

## Usage

```
python3 sttm
python3 sttm --portable
```

The backend script can also be called directly if installed to ~/.local:

```
blsw auto        # Apply mode based on current time
blsw morning     # Force a specific mode
blsw noon
blsw afternoon
blsw evening
blsw night
```

## Quick Install

```bash
# Automated dependency installer (run first)
./install

# First-time KDE theme setup
./setup
```
## Tips

- Calling the script directly allows changing to a custom theme without disabling scheduled mode

## Files

| File | Purpose |
|---|---|
| `sttm` | PyQt6 GUI application |
| `blsw` | Backend shell script that applies mode settings |
| `sttm.conf` | Config file (stores path to `blsw`) |
| `install` | Automated dependency installer with distro detection |
| `setup` | First-time KDE theme setup with interactive prompts |
| `install.sha256` | SHA256 checksum for install script verification |
| `icon.png` | Application icon for desktop entry |
| `.blur-schedule` | Stores the last active mode (auto-generated) |

**Disclaimer: This project was made with the help of deepseek and opencode. 

I am not a developer. I created the blsw.sh script mostly myself with inspiration from other projects.

The GUI, install, and setup scripts have been mostly generated by deepseek/opencode
