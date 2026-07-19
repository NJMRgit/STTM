# Stoned Theme Manager 

<div align="right">
            <a href="https://ko-fi.com/s7oned" target="_blank" style="display: inline-block;">
                <img
                    src="https://img.shields.io/badge/Donate-Ko--fi-F16061.svg?style=flat-square&logo=ko-fi" 
                    align="right"
                />
            </a></div>


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
- Generates tint/shadow/outline colors from chosen color or wallpaper

### Time-Based Modes
- Five default modes: **Morning**, **Noon**, **Afternoon**, **Evening**, **Night**
- Configurable trigger hour for each mode (24-hour format)
- Auto mode: systemd timer or cron checks hourly and applies the correct mode

### Custom themes
- Add custom themes directly to script or with included GUI
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
curl -fsSL -o install "https://raw.githubusercontent.com/NJMRgit/STTM/main/install" && sh install
```

The script verifies its own integrity against the GitHub API before running.

Running the install script if program is already installed will check for any user set themes and preserve them and update the GUI + Script logic


## Requirements

- Python 3 + PyQt6
- KDE Plasma 6+ (Tested working on 6.6.5 and 6.7)
- `openrgb` (optional, for RGB lighting)
- `systemctl --user` or `cronie` (for auto mode scheduling)
- [Glass](https://github.com/4v3ngR/kwin-effects-glass)
- [Darkly](https://github.com/Bali10050/Darkly)
- [KDE-Rounded-Corners](https://github.com/matinlotfali/KDE-Rounded-Corners)

## Usage

```
sttm
sttm --portable
```

Or launch the GUI from your app menu after install

The backend script can also be called directly if installed to ~/.local:

```
blsw auto        # Apply mode based on current time
blsw morning     # Force a specific mode
blsw noon
blsw afternoon
blsw evening
blsw night
```
## Notes

- The effects used for the blur/tint and shadows/outlines sometimes need to be rebuilt after an
  update. The script includes a flag to rebuild and reload the effects
```
blsw --fix
```

+ or download and rebuild from source ([1](https://github.com/4v3ngR/kwin-effects-glass),[2](https://github.com/matinlotfali/KDE-Rounded-Corners))
  
## Tips

- Calling the script directly allows changing to a custom theme without disabling scheduled mode

- If you want to disable titlebars disable them in here
  <img width="942" height="781" alt="image" src="https://github.com/user-attachments/assets/f486a424-c2b1-4334-81a8-e3a5c595be4d" />

- Currently colors appear too bright/saturated in HDR if using KDE 6.7+ - Lower brightness in desktop effects > glass
  <img width="1026" height="1087" alt="image" src="https://github.com/user-attachments/assets/5a726bf3-40ed-4f24-be65-df8f7d33a0b9" />
  
- To mitigate transparency issues in dolphin when renaming items disable this option
  <img width="988" height="901" alt="image" src="https://github.com/user-attachments/assets/dd227b23-fb40-4e42-9fd8-7fbd08612154" />
             

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

The GUI, install, and setup scripts have been mostly generated by deepseek/opencode with review, tweaking, and testing by myself and some others. 
