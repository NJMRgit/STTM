#!/bin/sh

set -e

TEST=false
for arg in "$@"; do
    case "$arg" in
        --test) TEST=true ;;
    esac
done

TMPDIR=""

cleanup() {
    if [ "$TEST" = true ] && [ -n "$TMPDIR" ]; then
        rm -rf "$TMPDIR"
    fi
}
trap cleanup EXIT

prompt() {
    if [ "$TEST" = true ]; then
        echo "  [test] prompt '$1' -> auto-yes"
        return 0
    fi
    if [ $# -eq 2 ]; then
        printf "\n%s\n%s\n  [Y/n]: " "$1" "$2" >&2
    else
        printf "\n[%s]" "$1" >&2
        [ -n "$2" ] && printf " %s" "$2" >&2
        printf "\n%s [Y/n]: " "$3" >&2
    fi
    read -r ans < /dev/tty
    case "$ans" in
        [nN]|[nN][oO]) return 1 ;;
        *) return 0 ;;
    esac
}

run_install() {
    if [ "$TEST" = true ]; then
        echo "  [test] would run: $*"
        return 0
    fi
    "$@"
}

safe_cd() {
    cd "$1" 2>/dev/null || { echo "  Failed to enter $1" >&2; return 1; }
}

git_clone() {
    dest="$1"
    repo="$2"
    if [ "$TEST" = true ]; then
        dest="$TMPDIR/$dest"
        echo "  [test] cloning $repo -> $dest"
        mkdir -p "$dest"
        git clone --depth=1 "$repo" "$dest" >/dev/null 2>&1 || echo "  [test] clone skipped (network)"
        return 0
    fi
    if [ -d "$dest" ]; then
        echo "  $dest already exists, skipping clone."
    else
        git clone "$repo" "$dest" || echo "  Warning: clone failed (check network). You may need to clone manually."
    fi
}

# ----------------------------------------------------------------

detect_pm() {
    if command -v pacman >/dev/null 2>&1; then
        echo "pacman"
    elif command -v apt >/dev/null 2>&1; then
        echo "apt"
    elif command -v dnf >/dev/null 2>&1; then
        echo "dnf"
    else
        echo "unknown"
    fi
}

printf '\033[36m'
printf '███████╗ ████████╗ ████████╗ ███╗   ███╗\n'
printf '██╔════╝ ╚══██╔══╝ ╚══██╔══╝ ████╗ ████║\n'
printf '███████╗    ██║       ██║    ██╔████╔██║\n'
printf '╚════██║    ██║       ██║    ██║╚██╔╝██║\n'
printf '███████║    ██║       ██║    ██║ ╚═╝ ██║\n'
printf '╚══════╝    ╚═╝       ╚═╝    ╚═╝     ╚═╝\n'
printf '\033[0m'
echo "  Stoned Theme Manager — Automated Installer"
printf '\033[2m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n'
echo

PM=$(detect_pm)
echo "Detected package manager: $PM"

if [ "$TEST" = true ]; then
    TMPDIR=$(mktemp -d)
    echo "Test mode — no files will be installed"
fi

echo

# Only need cronie if systemd is not available
if [ -d /run/systemd/system ]; then
    CRON_PKG=""
else
    CRON_PKG="cronie"
fi

case "$PM" in
    pacman)
        BASE="python-pyqt6 plasma-workspace qt6-tools openrgb $CRON_PKG"
        INSTALL_CMD="sudo pacman -S --needed"
        AUR_HELPER=""
        for h in yay paru trizen pikaur pacaur; do
            if command -v "$h" >/dev/null 2>&1; then
                AUR_HELPER=$h
                break
            fi
        done
        ;;
    apt)
        BASE="python3-pyqt6 plasma-workspace qt6-base-dev-tools $CRON_PKG"
        INSTALL_CMD="sudo apt install"
        AUR_HELPER=""
        EXTRA_APT="openrgb"
        ;;
    dnf)
        BASE="python3-pyqt6 plasma-workspace qt6-qtbase-tools $CRON_PKG"
        INSTALL_CMD="sudo dnf install"
        AUR_HELPER=""
        EXTRA_DNF="openrgb"
        ;;
    *)
        echo "Error: unknown package manager"
        echo "Please install dependencies manually: python3, PyQt6, plasma-workspace, qt6-tools, openrgb"
        exit 1
        ;;
esac

# shellcheck disable=SC2086
PKG_LIST=$(printf '%s\n' $BASE | sed '/^$/d; s/^/  - /')
if prompt "Check system package manager for available packages?" "$PKG_LIST"; then
    # shellcheck disable=SC2086
    run_install $INSTALL_CMD $BASE
    # openrgb may not be in default repos on apt/dnf, try separately
    if [ -n "$EXTRA_APT" ] || [ -n "$EXTRA_DNF" ]; then
        extra=${EXTRA_APT:-$EXTRA_DNF}
        run_install $INSTALL_CMD "$extra" 2>/dev/null || echo "  $extra not found in repositories, skipping (install manually if needed)"
    fi
fi

echo
echo "--- Items from GitHub / AUR / pipx ---"

# --- darkly ---
if [ "$PM" = "pacman" ] && [ -n "$AUR_HELPER" ]; then
    if prompt "darkly" "Global dark theme for KDE/GTK" "Install from AUR via $AUR_HELPER?"; then
        run_install "$AUR_HELPER" -S darkly-bin
    fi
elif [ "$PM" = "dnf" ]; then
    if prompt "darkly" "Global dark theme for KDE/GTK" "Install via Copr?"; then
        run_install sudo dnf copr enable deltacopy/darkly
        run_install sudo dnf install darkly
    fi
elif prompt "darkly" "Global dark theme for KDE/GTK" "Build from GitHub? (https://github.com/Bali10050/Darkly.git)"; then
    git_clone "Darkly" "https://github.com/Bali10050/Darkly.git"
    if [ "$TEST" = false ] && [ -d "Darkly" ]; then
        safe_cd "Darkly" && echo "  See README.md for build/install instructions." || true
    fi
fi

# --- kwin-effects-glass ---
if [ "$PM" = "pacman" ] && [ -n "$AUR_HELPER" ]; then
    if prompt "kwin-effects-glass" "Blur/glass KWin effect" "Install from AUR via $AUR_HELPER?"; then
        run_install "$AUR_HELPER" -S kwin-effects-glass-git
    fi
elif [ "$PM" = "dnf" ]; then
    if prompt "kwin-effects-glass" "Blur/glass KWin effect" "Install via Copr?"; then
        run_install sudo dnf copr enable ama1470/kwin-effects-glass
        run_install sudo dnf install kwin-effects-glass
    fi
elif prompt "kwin-effects-glass" "Blur/glass KWin effect" "Build from GitHub? (https://github.com/4v3ngR/kwin-effects-glass.git)"; then
    git_clone "kwin-effects-glass" "https://github.com/4v3ngR/kwin-effects-glass.git"
    if [ "$TEST" = false ] && [ -d "kwin-effects-glass" ]; then
        safe_cd "kwin-effects-glass" && echo "  See repo for build/install instructions." || true
    fi
fi

# --- KDE-Rounded-Corners ---
if [ "$PM" = "pacman" ] && [ -n "$AUR_HELPER" ]; then
    if prompt "kwin-rounded-corners" "Rounded corners KWin effect" "Install from AUR via $AUR_HELPER?"; then
        run_install "$AUR_HELPER" -S kwin-effect-rounded-corners-git
    fi
elif [ "$PM" = "dnf" ]; then
    if prompt "kwin-rounded-corners" "Rounded corners KWin effect" "Install via Copr?"; then
        run_install sudo dnf copr enable matinlotfali/KDE-Rounded-Corners
        run_install sudo dnf install kwin-effect-roundcorners
    fi
elif prompt "kwin-rounded-corners" "Rounded corners KWin effect" "Build from GitHub? (https://github.com/matinlotfali/KDE-Rounded-Corners.git)"; then
    git_clone "KDE-Rounded-Corners" "https://github.com/matinlotfali/KDE-Rounded-Corners.git"
    if [ "$TEST" = false ] && [ -d "KDE-Rounded-Corners" ]; then
        safe_cd "KDE-Rounded-Corners" && echo "  See repo for build/install instructions." || true
    fi
fi

# --- CachyOS-Emerald-KDE ---
if prompt "cachyos-emerald" "CachyOS Emerald Plasma theme" "Install from GitHub?"; then
    git_clone "CachyOS-Emerald-KDE" "https://github.com/CachyOS/CachyOS-Emerald-KDE.git"
    echo "  Copy the 'plasma' folder contents to ~/.local/share/plasma/ to install."
fi

# --- We10X ---
if prompt "we10x" "Windows 11 style GTK theme" "Install from GitHub? (recommended)"; then
    git_clone "We10X-gtk-theme" "https://github.com/yeyushengfan258/We10X-gtk-theme.git"
    if [ "$TEST" = true ]; then
        echo "  [test] would run: ./We10X-gtk-theme/install.sh -t grey -c dark -s compact -i arch --tweaks float round blur noborder"
    elif [ -d "We10X-gtk-theme" ]; then
        (cd We10X-gtk-theme && ./install.sh -t grey -c dark -s compact -i arch --tweaks float round blur noborder) || echo "  Warning: We10X install failed."
    fi
fi

echo
echo "Done. Run: python3 blur_gui.py"
