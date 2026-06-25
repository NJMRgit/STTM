# AGENTS.md — sttm (Stoned Theme Manager)

## Build & Run

```bash
cd ~/pi/projects/sttm
./install          # Install dependencies
./setup            # First-time setup
./sttm             # Run GUI
```

## Architecture

- **GUI**: `sttm` (PyQt6 application)
- **Backend**: `blsw` (shell script for mode settings)
- **Config**: `~/.config/sttm/sttm.conf`
- **Schedule**: `~/.blur-schedule` (last active mode)

## Key Files

| File | Purpose |
|------|---------|
| `sttm` | PyQt6 GUI application |
| `blsw` | Backend script that applies mode settings |
| `install` | Dependency installer with distro detection |
| `setup` | First-time KDE theme setup |
| `glassd.colors` | Transparent KDE color scheme |
| `icon.png` | Application icon |

## Features

- Time-based mode switching (Morning, Noon, Afternoon, Evening, Night)
- Wallpaper, glass tint, rounded-corners colors
- OpenRGB lighting profiles
- Fastfetch logo customization
- Auto mode with systemd timer (hourly + login) or cron
- Custom themes
- Partial mode application (empty settings skipped)

## Development Conventions

### GUI writes only to blsw
- GUI modifies `blsw` in-place (updates existing `KEY=` lines)
- Never writes to `~/.blur-schedule` — only reads it
- Schedule file is the sole source of truth for current mode

### Mode case convention
- GUI stores modes in uppercase (e.g., `"AFTERNOON"`)
- blsw receives lowercase (e.g., `"afternoon"`)
- Schedule file stores lowercase: `_MODE=afternoon`

### Button colors
- Buttons use default PyQt6 native appearance (no custom styling)
- No mode-based color logic on buttons

### Sync workflow
- Development copy: `~/pi/projects/sttm/blsw`
- Deployed copy: `~/.local/bin/blsw`
- Both `sttm` copies must stay identical
- Script logic synced between dev and deployed `blsw`

## Session Management

### Session Start
```bash
cp sttm ~/.local/bin/sttm.bak
cp blsw ~/.local/bin/blsw.bak
cp sttm ~/pi/projects/sttm/sttm.bak
cp blsw ~/pi/projects/sttm/blsw.bak
```

### Session End
```bash
cp ~/.local/bin/sttm ~/pi/projects/sttm/sttm.last
cp ~/.local/bin/blsw ~/pi/projects/sttm/blsw.last
```

## Important Constraints

- Yakuake wait loop is indefinite — terminating while programs running interrupts them
- No CI / tests — local development only
- Changes must be prompted to user before applying
- No git commits/pushes without explicit approval

## Known Issues

See `~/pi/notes/SESSION_PROGRESS.md` for complete bug history