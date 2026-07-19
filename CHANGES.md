# Setup Script Changes — Complete Summary

## 1. Fullscreen TUI Framework
- **Alternate screen buffer** (`\033[?1049h`/`l`) — entire script runs in its own screen, restores cleanly on exit or Ctrl+C/Z
- **Dynamic full-terminal border** — drawn using `tput cols/lines`; top (`┌─┐`), bottom (`└─┘`), left/right (`│`) adapt to terminal size
- **Animated startup** — border spreads from top-left corner, header wipes top-to-bottom, summary wipes right-to-left, prompt types character-by-character
- **`left_border()` helper** — draws `│` at column 1 and column `$W`, clears content area between them; used by every content row
- **Signal handling** — `trap cleanup INT TERM TSTP` restores cursor and primary screen on Ctrl+C/Z

## 2. Initial Summary Display
- Replaced plain `echo` bullets with animated right-to-left wipe across 10 concise lines:
  ```
  - Enable Glass'd color scheme
      + Custom Transparent Color Scheme
      + Required for Full Window Transparency
  - Enable Darkly Application Style
      + Required for Full Window Transparency
  - Change 4v3ngR/kwin-effects-glass settings and enable the effect
  - Change matinlotfali/KDE-Rounded-Corners settings and enable the effect
  - Change Plasma style to Iridescent-round
  - Change GTK Theme to we10x
  - Add Window rule for CSD shadow compatibility
  ```
- Prompt: `Continue? [Y/n]` typed per-character via `type_text()` at 0.004s/char

## 3. Hide Titlebars
- Prompt asked **before** config writing: "Hide titlebars? [y/N]"
- Answer stored in `$hide_titlebars`
- Written to **both** `~/.config/breezerc` and `~/.config/darklyrc` in `[Windeco Exception 0]` section
- `qdbus6 org.kde.KWin /KWin reconfigure` called after CONFIGS loop to apply immediately

## 4. Checklist Box
- Hidden during initial display (blank spaces); appears top-to-bottom after Continue? is answered
- Rows 3-7 at column `$W - 25`:
  ```
  ┌──────────────────────┐
  │ ○ Update Files       │
  │ ○ Apply styles/colors│
  │ ○ Install Manager    │
  └──────────────────────┘
  ```
- Marks update to `✓` as each section completes

## 5. Config File Processing (CONFIGS loop)
- Each file section shows a spinner animation on the file row, then turns into `✓` on completion
- Descriptions populate below each file with `sleep 0.15` between entries
- File summary tracks per-file changes with `~/.config/` prefix for final report

## 6. Style Commands — Spinner + Checkmark
Each style line now shows a live spinner while the command runs:

| Line | Command | Animation |
|------|---------|-----------|
| Setting GTK theme | `kwriteconfig6` + `gsettings` | Post-spinner (instant commands) |
| Applying Darkly style | `kwriteconfig6` | Post-spinner |
| Setting plasma theme | `plasma-apply-desktoptheme` | **Live spinner** (background `$pid`) |
| Applying glassd scheme | `plasma-apply-colorscheme` | **Live spinner** (background `$pid`) |

A 1-second pause after all styles complete lets the user see the `✓` marks, followed by a bottom-up wipe to clean the screen.

## 7. Install Menu — Local / Portable / Skip
Replaced yes/no prompt with 3-option menu:

```
  Install STTM (choose method):
    1) local    - install to ~/.local/bin
    2) portable - install to ~/
    3) skip
  Select:
```

- **Local**: installs to `~/.local/bin`, icon to system dir, `.desktop` auto-created
- **Portable**: installs to `~/STTM/`, icon in same folder, prompts for `.desktop`
- **Skip**: no installation
- `cp_or_fetch()` refactored to accept a 3rd `target_dir` parameter
- Bottom-up wipe clears all previous output before menu appears

## 8. Final Summary — Two-Column Pane

```
── Summary ────────────── │ ── Usage ───────────────────
  Files updated (5):      │   Commands:
    ~/.config/kwinrc (4)  │     blsw morning|noon|...
    ~/.config/kwinrulesrc │     blsw auto
    ~/.config/plasmarc (1)│     blsw --fix
    ~/.config/breezerc (2)│   GUI:
    ~/.config/darklyrc (4)│     sttm
  Styles/Colors applied:  │     python3 sttm --portable
    ✓ glassd installed    │   Examples:
    ✓ GTK: We10X          │     blsw morning   Manual
    ✓ Darkly style        │     blsw auto      Time-based
    ✓ Iridescent-round    │     blsw --fix     Rebuild
    ✓ glassd scheme       │     sttm           GUI
  Manager:                │   File locations:
    ✓ STTM installed      │     <install_dir>/sttm
                          │     <install_dir>/blsw
```

## 9. Theme Consistency
- `plasmarc` writes `name=Iridescent-round` (was `cachyos-emerald`)
- Summary matches actual applied theme

## 10. Timing Reference

| Animation | Per-unit delay | Total |
|-----------|---------------|-------|
| Border spread | 0.002s / 0.0015s | ~0.5s |
| Header wipe | 0.05s per row | 0.4s |
| Summary wipe | 0.001s per column | ~0.1s |
| Prompt typing | 0.004s per char | ~0.15s |
| Checklist reveal | 0.05s per row | 0.25s |
| Bottom-up wipe | 0.02s per row | ~0.2s |
| Style spinner | 0.04s per frame | ~0.3s per line |
| Post-styles pause | — | 1.0s |

## 11. Install Script Changes
- **CachyOS-Emerald-KDE replaced with Iridescent** — `install` now clones `https://github.com/ddh4r4m/Iridescent.git` and copies `plasma/*` (desktoptheme + look-and-feel) to `~/.local/share/plasma/`
- **Check function renamed** — `check_emerald()` → `check_iridescent()`, checks for `Iridescent-round` instead of `cachyos-emerald`
- **Checksum updated** — `install.sha256` reflects the modified `install` script

# GUI Changes

## 1. Layout Restructure
- **Left/right split** — mode settings panel now sits on the left, wallpaper preview on the right, separated by a resizable `QSplitter` (6px handle with visible styling)
- **Left panel minimum width** — set to 400px so no settings are hidden when the splitter is dragged
- **Left panel stretch** — stretch factor 0 prevents it from growing wider when the window is resized; all extra horizontal space goes to the wallpaper preview
- **Mode selector repositioned** — the mode dropdown and "+" add-custom-mode button moved from the main layout into the top of the left panel, above the stacked settings pages
- **Apply button anchored** — moved outside the scroll area, pinned to the bottom of the left panel; the form content (Appearance, Fastfetch, System groups) scrolls independently above it

## 2. Wallpaper Preview
- **Outer `QScrollArea` removed** — each mode page's left side already has its own scroll area; the outer one was redundant and caused the preview to scroll with the form
- **Single shared preview** — one `WallpaperPreview` widget lives on the right side of the outer splitter, shared across all modes; switching modes via the combo updates its wallpaper
- **Full-resolution pixmap cache** — `_full_cache` class dict stores the loaded `QPixmap` by file path, avoiding redundant disk I/O when switching back to a previously viewed mode
- **Always re-scale to current size** — `set_wallpaper` and `resizeEvent` re-scale the cached full pixmap to the widget's current dimensions, ensuring the preview is always the correct size regardless of window size or mode switches
- **No height constraints** — removed `setMinimumHeight`/`setMaximumHeight` so the preview scales freely with the window

## 3. Generate Colors
- **"Generate Colors" button split** — replaced with two dedicated buttons below the wallpaper path row: "Generate from Wallpaper" and "Custom"
- **Generate from Wallpaper** — confirms replacement if colors exist, then extracts dominant colors directly from the wallpaper file (no intermediate method-selection dialog)
- **Custom** — confirms replacement if colors exist, then opens a `QColorDialog` positioned over the left edge of the window so the eyedropper can reach the wallpaper preview on the right

## 4. Window Persistence
- **Geometry saved on close** — `closeEvent` saves the window size, position, and splitter state via `QSettings("sttm", "sttm")`
- **Geometry restored on launch** — `_restore_geometry` is called during `__init__`; if no saved state exists, the default 800×1080 size is used
- **Application icon** — `setWindowIcon` loads `icon.png` from the project directory for the titlebar and taskbar
