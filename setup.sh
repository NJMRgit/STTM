#!/bin/sh

set -e

prompt_yn() {
    printf "\n%s [Y/n]: " "$1" >&2
    read -r REPLY < /dev/tty
    case "$REPLY" in
        [nN]|[nN][oO]) return 1 ;;
        *) return 0 ;;
    esac
}

# Silent apply — no output
apply() {
    file="$1"; group="$2"; key="$3"; value="$4"
    [ -z "$value" ] && return
    case "$group" in
        *\]\[*)
            first=$(echo "$group" | sed 's/\]\[.*//')
            rest=$(echo "$group" | sed 's/^[^]]*\]\[//')
            kwriteconfig6 --file "$file" --group "$first" --group "$rest" --key "$key" "$value"
            ;;
        *)
            kwriteconfig6 --file "$file" --group "$group" --key "$key" "$value"
            ;;
    esac
}

# Type text with per-character delay
type_text() {
    str="$1"
    while [ -n "$str" ]; do
        c=$(printf '%s' "$str" | sed 's/\(.\.*/\1/')
        printf '%s' "$c"
        str=$(printf '%s' "$str" | sed 's/.//')
        sleep 0.003
    done
}

# Strip inline comment markers
clean() {
    echo "$1" | sed 's/[[:space:]]*#.*//' | sed 's/[[:space:]]*$//'
}

printf '\033[36m'
printf '███████╗ ████████╗ ████████╗ ███╗   ███╗\n'
printf '██╔════╝ ╚══██╔══╝ ╚══██╔══╝ ████╗ ████║\n'
printf '███████╗    ██║       ██║    ██╔████╔██║\n'
printf '╚════██║    ██║       ██║    ██║╚██╔╝██║\n'
printf '███████║    ██║       ██║    ██║ ╚═╝ ██║\n'
printf '╚══════╝    ╚═╝       ╚═╝    ╚═╝     ╚═╝\n'
printf '\033[0m'
echo "  Stoned Theme Manager — First Time Setup"
printf '\033[2m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n'
echo "  - Adds grey transparent color scheme to work with darkly and glass"
echo "  - Sets glass defaults"
echo "  - Sets outline and glow defaults"
echo "  - Enables Darkly application theme"
echo "  - Enables CachyOS Emerald Plasma theme"
echo "  - Adds window rule for CSD shadow compatability"
echo
if ! prompt_yn "Apply these changes?"; then
    echo "Aborted."
    exit 0
fi
echo

# Ensure config files exist before writing to them
for cfg in breezerc darklyrc; do
    path="$HOME/.config/$cfg"
    if [ ! -f "$path" ]; then
        echo "  Creating $cfg..."
        touch "$path"
    fi
done

anim_apply=false
do_anim=false
group_open=false

close_group() {
    if $group_open; then
        for c in - \\ \| / -; do
            printf '%s\b' "$c"
            sleep 0.035
        done
        printf '\033[32m✓\033[0m\n'
        group_open=false
    fi
}

while IFS= read -r line || [ -n "$line" ]; do
    # Strip leading whitespace, skip empties and comments
    raw=$(printf "%s" "$line" | sed 's/^[[:space:]]*//')
    case "$raw" in
        ""|"#"*) continue ;;
    esac

    # Section header — file|group
    case "$raw" in
        \[*\])
            close_group
            sect=$(echo "$raw" | sed 's/^\[\(.*\)\]$/\1/')
            file=$(echo "$sect" | sed 's/|.*//')
            group=$(echo "$sect" | sed 's/.*|//')
            printf "  "
            type_text "${file} [${group}]"
            printf ": "
            group_open=true
            continue
            ;;
    esac

    # key=value
    case "$raw" in
        *=*)
            key=$(echo "$raw" | sed 's/=.*//;s/[[:space:]]*$//')
            val=$(echo "$raw" | sed 's/^[^=]*=//')

            # --- animation prompt ---
            if echo "$val" | grep -q "Prompt user for this change"; then
                if ! $do_anim; then
                    do_anim=true
                    if prompt_yn "Change animations? (May prevent flicker)"; then
                        anim_apply=true
                        v=$(clean "$val")
                        apply "$file" "$group" "$key" "$v"
                    fi
                fi
                continue
            fi

            if echo "$val" | grep -q "include as part of the previous prompt"; then
                if $anim_apply; then
                    v=$(clean "$val")
                    apply "$file" "$group" "$key" "$v"
                fi
                continue
            fi

            # --- inactive shadow alpha prompt ---
            if echo "$val" | grep -q "enable inactive shadows"; then
                printf "\n%s [y/N]: " "Enable inactive shadows? (not recommended)" >&2
                read -r REPLY < /dev/tty
                case "$REPLY" in
                    [yY]|[yY][eE][sS])
                        apply "$file" "$group" "$key" "170"
                        ;;
                    *)
                        apply "$file" "$group" "$key" "0"
                        ;;
                esac
                continue
            fi

            v=$(clean "$val")
            apply "$file" "$group" "$key" "$v"
            ;;
    esac
done <<'CONFIGS'
# ----------------------------------------------------------------
# Format: [file|group]
#         key=value
# Lines starting with # are skipped.
# Inline annotations are stripped.
# ----------------------------------------------------------------

[kdeglobals|ColorEffects:Disabled]
ChangeSelectionColor=
Color=23,23,23
ColorAmount=0
ColorEffect=0
ContrastAmount=0.65
ContrastEffect=1
Enable=
IntensityAmount=0.1
IntensityEffect=2

[kdeglobals|ColorEffects:Inactive]
ChangeSelectionColor=false
Color=112,111,110
ColorAmount=0.025
ColorEffect=2
ContrastAmount=0.1
ContrastEffect=2
Enable=false
IntensityAmount=0
IntensityEffect=0

[kdeglobals|Colors:Button]
BackgroundAlternate=105,105,105
BackgroundNormal=0,0,0,45
DecorationFocus=0,109,12,60
DecorationHover=175,175,175
ForegroundActive=120,120,120
ForegroundInactive=102,106,115
ForegroundLink=41,128,185
ForegroundNegative=41,189,13
ForegroundNeutral=255,106,0
ForegroundNormal=195,199,209
ForegroundPositive=113,247,159
ForegroundVisited=69,40,134

[kdeglobals|Colors:Complementary]
BackgroundAlternate=93,93,93
BackgroundNormal=93,93,93
DecorationFocus=82,82,82
DecorationHover=90,90,90,150
ForegroundActive=120,120,120
ForegroundInactive=174,181,196
ForegroundLink=41,128,185
ForegroundNegative=41,189,13
ForegroundNeutral=255,106,0
ForegroundNormal=211,218,227
ForegroundPositive=113,247,159
ForegroundVisited=179,13,191

[kdeglobals|Colors:Header]
BackgroundAlternate=29,31,34
BackgroundNormal=20,22,24,20
DecorationFocus=120,120,120,
DecorationHover=90,90,90,150
ForegroundActive=120,120,120
ForegroundInactive=161,169,177
ForegroundLink=29,153,243
ForegroundNegative=218,68,83
ForegroundNeutral=246,116,0
ForegroundNormal=200,200,200
ForegroundPositive=39,174,96
ForegroundVisited=155,89,182

[kdeglobals|Colors:Header][Inactive]
BackgroundAlternate=29,31,34
BackgroundNormal=20,22,24,20
DecorationFocus=120,120,120
DecorationHover=90,90,90,150
ForegroundActive=120,120,120
ForegroundInactive=161,169,177
ForegroundLink=29,153,243
ForegroundNegative=218,68,83
ForegroundNeutral=246,116,0
ForegroundNormal=252,252,252
ForegroundPositive=39,174,96
ForegroundVisited=155,89,182

[kdeglobals|Colors:Selection]
BackgroundAlternate=116,116,116,155
BackgroundNormal=50,50,50,85
DecorationFocus=66,14,210
DecorationHover=66,14,210
ForegroundActive=252,252,252
ForegroundInactive=211,218,227
ForegroundLink=253,188,75
ForegroundNegative=41,189,13
ForegroundNeutral=255,106,0
ForegroundNormal=225,225,225
ForegroundPositive=113,247,159
ForegroundVisited=189,195,199

[kdeglobals|Colors:Tooltip]
BackgroundAlternate=30,32,36
BackgroundNormal=90,90,90,150
DecorationFocus=0,72,82
DecorationHover=0,144,20
ForegroundActive=120,120,120
ForegroundInactive=174,181,196
ForegroundLink=41,128,185
ForegroundNegative=41,189,13
ForegroundNeutral=255,106,0
ForegroundNormal=211,218,227
ForegroundPositive=113,247,159
ForegroundVisited=37,22,75

[kdeglobals|Colors:View]
BackgroundAlternate=29,31,34,32
BackgroundNormal=35,35,35,1
DecorationFocus=0,0,0,45
DecorationHover=90,90,90,150
ForegroundActive=255,255,255,0
ForegroundInactive=161,169,177
ForegroundLink=29,153,243
ForegroundNegative=218,68,83
ForegroundNeutral=246,116,0
ForegroundNormal=240,240,240
ForegroundPositive=39,174,96
ForegroundVisited=155,89,182

[kdeglobals|Colors:Window]
BackgroundAlternate=41,44,48
BackgroundNormal=35,35,35,1
DecorationFocus=200,200,200
DecorationHover=90,90,90,150
ForegroundActive=0,0,0,20
ForegroundInactive=161,169,177
ForegroundLink=29,153,243
ForegroundNegative=218,68,83
ForegroundNeutral=246,116,0
ForegroundNormal=252,252,252
ForegroundPositive=39,174,96
ForegroundVisited=155,89,182

[kdeglobals|General]
ColorScheme=glassd
ColorSchemeHash=363bb2816ae591cbef60d92d8fd040f725221af3

[kwinrc|Effect-blurplus]
BlurDecorations=true
BlurMatching=false
BlurNonMatching=true
BlurStrength=6
BottomCornerRadius=6
Brightness=0.85
EdgeLighting=true
EdgeLightingTooltip=true
FakeBlur=true
GlowColor=
MenuCornerRadius=11.5
NoiseStrength=3
OklabSaturation=true
RefractionNormalPow=22
RefractionRGBFringing=0
TintColor=#37199054
TopCornerRadius=6
WindowClasses=gsr-ui\nactivate-linux

[kwinrc|Plugins]
blurEnabled=false
fadeEnabled=true  
glassEnabled=true
scaleEnabled=false  

[kwinrc|Round-Corners]
ActiveShadowAlpha=170
ActiveShadowUseCustom=true
DisableOutlineMaximize=false
DisableOutlineTile=false
DisableRoundMaximize=false
DisableRoundTile=false
Exclusions=gsr-ui
InactiveCornerRadius=6
InactiveOutlineColor=55,55,55
InactiveOutlineThickness=4
InactiveSecondOutlineThickness=0
InactiveShadowColor=55,55,55
InactiveShadowSize=50
InactiveShadowUseCustom=true
OutlineColor=55,55,55
OutlineThickness=4
SecondOutlineThickness=0
ShadowColor=55,55,55
ShadowSize=50
Size=6
UseNativeDecorationShadows=false

[kwinrc|org.kde.kdecoration2]
NoPlugin=false
library=org.kde.darkly
theme=Darkly

[kwinrulesrc|50a6fdb6-57ad-47da-aedd-67ff644f4ef5]
Description=Global Shadows (For Stoned Theme Manager)
noborderrule=2

[plasmarc|Theme]
name=cachyos-emerald

[breezerc|Common]
OutlineIntensity=OutlineOff

[breezerc|Windeco Exception 0]
BorderSize=0
Enabled=true
ExceptionPattern=.*
ExceptionType=0
HideTitleBar=false
Mask=0

[darklyrc|Windeco Exception 0]
BorderSize=0
Enabled=true
ExceptionPattern=.*
ExceptionType=0
HideTitleBar=false
Mask=0
CONFIGS
close_group

# Install color scheme file
sleep 0.15
echo "Installing color scheme..."
mkdir -p "$HOME/.local/share/color-schemes"
cat > "$HOME/.local/share/color-schemes/glassd.colors" <<'CSFILE'
[ColorEffects:Disabled]
Color=23,23,23
ColorAmount=0
ColorEffect=0
ContrastAmount=0.65
ContrastEffect=1
IntensityAmount=0.1
IntensityEffect=2

[ColorEffects:Inactive]
ChangeSelectionColor=false
Color=112,111,110
ColorAmount=0.025
ColorEffect=2
ContrastAmount=0.1
ContrastEffect=2
Enable=false
IntensityAmount=0
IntensityEffect=0

[Colors:Button]
BackgroundAlternate=105,105,105
BackgroundNormal=0,0,0,45
DecorationFocus=0,109,12,60
DecorationHover=175,175,175
ForegroundActive=120,120,120
ForegroundInactive=102,106,115
ForegroundLink=41,128,185
ForegroundNegative=41,189,13
ForegroundNeutral=255,106,0
ForegroundNormal=195,199,209
ForegroundPositive=113,247,159
ForegroundVisited=69,40,134

[Colors:Complementary]
BackgroundAlternate=93,93,93
BackgroundNormal=93,93,93
DecorationFocus=82,82,82
DecorationHover=90,90,90,150
ForegroundActive=120,120,120
ForegroundInactive=174,181,196
ForegroundLink=41,128,185
ForegroundNegative=41,189,13
ForegroundNeutral=255,106,0
ForegroundNormal=211,218,227
ForegroundPositive=113,247,159
ForegroundVisited=179,13,191

[Colors:Header]
BackgroundAlternate=29,31,34
BackgroundNormal=20,22,24,20
DecorationFocus=120,120,120,
DecorationHover=90,90,90,150
ForegroundActive=120,120,120
ForegroundInactive=161,169,177
ForegroundLink=29,153,243
ForegroundNegative=218,68,83
ForegroundNeutral=246,116,0
ForegroundNormal=200,200,200
ForegroundPositive=39,174,96
ForegroundVisited=155,89,182

[Colors:Header][Inactive]
BackgroundAlternate=29,31,34
BackgroundNormal=20,22,24,20
DecorationFocus=120,120,120
DecorationHover=90,90,90,150
ForegroundActive=120,120,120
ForegroundInactive=161,169,177
ForegroundLink=29,153,243
ForegroundNegative=218,68,83
ForegroundNeutral=246,116,0
ForegroundNormal=252,252,252
ForegroundPositive=39,174,96
ForegroundVisited=155,89,182

[Colors:Selection]
BackgroundAlternate=116,116,116,155
BackgroundNormal=50,50,50,85
DecorationFocus=66,14,210
DecorationHover=66,14,210
ForegroundActive=252,252,252
ForegroundInactive=211,218,227
ForegroundLink=253,188,75
ForegroundNegative=41,189,13
ForegroundNeutral=255,106,0
ForegroundNormal=225,225,225
ForegroundPositive=113,247,159
ForegroundVisited=189,195,199

[Colors:Tooltip]
BackgroundAlternate=30,32,36
BackgroundNormal=90,90,90,150
DecorationFocus=0,72,82
DecorationHover=0,144,20
ForegroundActive=120,120,120
ForegroundInactive=174,181,196
ForegroundLink=41,128,185
ForegroundNegative=41,189,13
ForegroundNeutral=255,106,0
ForegroundNormal=211,218,227
ForegroundPositive=113,247,159
ForegroundVisited=37,22,75

[Colors:View]
BackgroundAlternate=29,31,34,32
BackgroundNormal=35,35,35,1
DecorationFocus=0,0,0,45
DecorationHover=90,90,90,150
ForegroundActive=255,255,255,0
ForegroundInactive=161,169,177
ForegroundLink=29,153,243
ForegroundNegative=218,68,83
ForegroundNeutral=246,116,0
ForegroundNormal=240,240,240
ForegroundPositive=39,174,96
ForegroundVisited=155,89,182

[Colors:Window]
BackgroundAlternate=41,44,48
BackgroundNormal=35,35,35,1
DecorationFocus=200,200,200
DecorationHover=90,90,90,150
ForegroundActive=0,0,0,20
ForegroundInactive=161,169,177
ForegroundLink=29,153,243
ForegroundNegative=218,68,83
ForegroundNeutral=246,116,0
ForegroundNormal=252,252,252
ForegroundPositive=39,174,96
ForegroundVisited=155,89,182

[General]
ColorScheme=Glass'd
Name=Glass'd
shadeSortColumn=true

[KDE]
contrast=4

[WM]
activeBackground=0,81,93,80
activeBlend=255,255,255
activeForeground=211,211,211
inactiveBackground=0,81,93,125
inactiveBlend=120,120,120
inactiveForeground=120,120,120
CSFILE
printf '\033[32mOK\033[0m\n'

# Toggle ColorScheme to force it to take effect
kwriteconfig6 --file kdeglobals --group General --key ColorScheme breeze
kwriteconfig6 --file kdeglobals --group General --key ColorScheme glassd

echo
sleep 0.2
printf '\033[32m  All configs applied.\033[0m\n'
echo

echo "  Note: The GUI can also be run as a portable app from the project"
echo "  directory with: python3 blur_gui.py --portable"
if prompt_yn "Install Stoned Theme Manager to /opt/sttm?"; then
    echo "Installing STTM GUI..."
    sudo mkdir -p /opt/sttm
    SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
    sudo cp "$SCRIPT_DIR/blur_gui.py" /opt/sttm/
    sudo cp "$SCRIPT_DIR/blsw.sh" /opt/sttm/
    sudo chmod +x /opt/sttm/blur_gui.py /opt/sttm/blsw.sh

    echo "Installing icon..."
    mkdir -p "$HOME/.local/share/icons/hicolor/256x256/apps"
    if command -v convert >/dev/null 2>&1; then
        convert "$SCRIPT_DIR/icon.png" -resize 256x256 "$HOME/.local/share/icons/hicolor/256x256/apps/sttm.png"
    else
        echo "  ImageMagick not found, skipping icon resize."
        cp "$SCRIPT_DIR/icon.png" "$HOME/.local/share/icons/hicolor/256x256/apps/sttm.png" 2>/dev/null || echo "  Warning: icon.png not found."
    fi

    echo "Creating desktop entry..."
    mkdir -p "$HOME/.local/share/applications"
    cat > "$HOME/.local/share/applications/sttm.desktop" <<DESKTOP
[Desktop Entry]
Name=STTM
GenericName=Stoned Theme Manager
Comment=KDE theme manager with wallpaper-based color generation
Exec=/opt/sttm/blur_gui.py
Icon=sttm
Terminal=false
Type=Application
Categories=Qt;KDE;System;Utility;
DESKTOP
    printf '\033[32mOK\033[0m\n'
fi

if prompt_yn "Restart plasmashell?"; then
    echo "Restarting plasmashell..."
    kquitapp6 plasmashell 2>/dev/null || true
    sleep 1
    kstart6 plasmashell >/dev/null 2>&1 || plasmashell >/dev/null 2>&1 &
    sleep 2
    echo "Plasmashell restarted."
else
    echo "Skipping. Restart manually: kquitapp6 plasmashell && kstart6 plasmashell"
fi

echo
echo "Install Complete. You may need to log out/restart for all changes to take effect."
printf "\n%s" "Press Enter to exit."
read -r REPLY
