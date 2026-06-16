# Stoned Theme Manager

KDE Plasma theme manager with time-based mode switching. Automatically adjusts wallpaper, window glass tint, rounded-corners outline/shadow colors, fastfetch logo, and OpenRGB lighting profiles based on the time of day.

## Features

### Time-Based Modes
- Five default modes: **Morning**, **Noon**, **Afternoon**, **Evening**, **Night**
- Configurable trigger hour for each mode (24-hour format)
- Auto mode: systemd timer or cron checks hourly and applies the correct mode
- Custom modes can be added/removed from the GUI

### Partial Mode Application
- Empty settings in a mode are skipped — previously applied or manually configured values persist
- Apply only the settings you want per mode (e.g., set wallpaper without touching fastfetch logo)
- Enables sparse mode configs: set just tint + wallpaper for morning, just wallpaper for evening, etc.

### Per-Mode Settings
- **Wallpaper** — set a different wallpaper per mode
- **Glass Tint** — Glass tint color 
- **Outline Colors** — rounded-corners outline (active + inactive) 
- **Shadow Colors** — rounded-corners shadow (active + inactive)
- **Fastfetch Logo** — per-mode logo file and logo color
- **OpenRGB Profile** — per-mode RGB lighting profile

### Material You Color Generation
- Generates tint/shadow/outline colors automatically when adding wallpaper to an unconfigured mode
- Warns when a wallpaper has no extracted colors (no `primary_container`)
- Button to regenerate colors when updating wallpaper

### Portable Config
- Default config stored at `~/.config/sttm/sttm.conf`
- Launch with `--portable` to use local config (saved alongside `blur_gui.py`)
- Schedule file: `~/.blur-schedule` by default, `.blur-schedule` in local dir with `--portable`
- Auto-detects `blsw.sh` next to the GUI in portable mode

### First-Time Setup
- `setup.sh` — interactive ASCII-art installer that configures KDE with the necessary theme elements
- Description of each change

### Automated Installer
- `install.sh` — dependency installer with distro detection (pacman/apt/dnf)
- Handles AUR packages via detected helper (yay, paru, trizen, pikaur, pacaur)
- Offers pipx as alternative for matugen installation
- Installs Darkly, We10X, kwin-effects-glass, KDE-Rounded-Corners, CachyOS-Emerald-KDE

### KDE Plasma Integration
- Applies settings via `kwriteconfig6`, `plasma-apply-wallpaperimage`, and `qdbus6`
- Wayland Only

### Additional Integrations
- **OpenRGB** — load a profile per mode
- **Fastfetch** — per-mode logo and logo color applied to `~/.config/fastfetch/config.jsonc`
- **Yakuake** — When updating theme to a new mode the script will check to see if yakuake is running a program. If it detects a running program it will wait till it's finished then close the yakuake session to update the fastfetch logo

## Requirements

- Python 3 + PyQt6
- KDE Plasma 6 with Glass and Rounded Corners effects
- `matugen` (for color generation) — install via AUR, pipx, or GitHub
- `kwriteconfig6`, `plasma-apply-wallpaperimage`, `qdbus6`
- `openrgb` (optional, for RGB lighting)
- `systemctl --user` or `cronie` (for auto mode scheduling)

## Usage

```
python3 blur_gui.py
python3 blur_gui.py --portable
```

The backend script can also be called directly:

```
./blsw.sh auto        # Apply mode based on current time
./blsw.sh morning     # Force a specific mode
./blsw.sh noon
./blsw.sh afternoon
./blsw.sh evening
./blsw.sh night
```

## Quick Install

```bash
# Automated dependency installer (run first)
./install.sh

# First-time KDE theme setup
./setup.sh
```

## Files

| File | Purpose |
|---|---|
| `blur_gui.py` | PyQt6 GUI application |
| `blsw.sh` | Backend shell script that applies mode settings |
| `sttm.conf` | Config file (stores path to `blsw.sh`) |
| `install.sh` | Automated dependency installer with distro detection |
| `setup.sh` | First-time KDE theme setup with interactive prompts |
| `icon.png` | Application icon for desktop entry |
| `.blur-schedule` | Stores the last active mode (auto-generated) |
