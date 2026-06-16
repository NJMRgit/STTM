#!/bin/sh

# some env vars that are needed for kwin effects to work
export XDG_SESSION_TYPE=wayland
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export XDG_CONFIG_DIRS=/home/$(id -un)/.config/kdedefaults:/etc/xdg
export LIBGL_ALWAYS_REDIRECT=
export QT_WAYLAND_RECONNECT=1


#-------------------------------------------------------------------------------------------------#
# set the hours for auto mode
MORNING_HOUR="6"
NOON_HOUR="12"
AFTERNOON_HOUR="14"
EVENING_HOUR="17"
NIGHT_HOUR="21"
#-------------------------------------------------------------------------------------------------#
#IMPORTANT#
# $TINT values need to be in hex w/ alpha (ex: #00112233)
# OUTLINE_COLOR and SHADOW_COLOR need to be in RGB (ex: 225,225,225)
#-------------------------------------------------------------------------------------------------#
# noon mode settings
NOON_TINT=
NOON_OUTLINE_COLOR_ACTIVE=
NOON_OUTLINE_COLOR_INACTIVE=
NOON_SHADOW_COLOR=
NOON_SHADOW_COLOR_INACTIVE=
NOON_WALLPAPER=
NOON_FF_LOGO=
NOON_FF_LOGO_COLOR=
NOON_RGB=
#-------------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------------#
# afternoon mode settings
AFTERNOON_TINT=
AFTERNOON_OUTLINE_COLOR_ACTIVE=
AFTERNOON_OUTLINE_COLOR_INACTIVE=
AFTERNOON_SHADOW_COLOR=
AFTERNOON_SHADOW_COLOR_INACTIVE=
AFTERNOON_WALLPAPER=
AFTERNOON_FF_LOGO=
AFTERNOON_FF_LOGO_COLOR=
AFTERNOON_RGB=
#-------------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------------#
# evening mode settings
EVENING_TINT=
EVENING_OUTLINE_COLOR_ACTIVE=
EVENING_OUTLINE_COLOR_INACTIVE=
EVENING_SHADOW_COLOR=
EVENING_SHADOW_COLOR_INACTIVE=
EVENING_WALLPAPER=
EVENING_FF_LOGO=
EVENING_FF_LOGO_COLOR=
EVENING_RGB=
#-------------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------------#
# night mode settings
NIGHT_TINT=
NIGHT_OUTLINE_COLOR_ACTIVE=
NIGHT_OUTLINE_COLOR_INACTIVE=
NIGHT_SHADOW_COLOR=
NIGHT_SHADOW_COLOR_INACTIVE=
NIGHT_WALLPAPER=
NIGHT_FF_LOGO=
NIGHT_FF_LOGO_COLOR=
NIGHT_RGB=
#-------------------------------------------------------------------------------------------------#





#get time
h=$(date +%H)

[ -z "$HOME" ] && HOME=/tmp/

# Allow manual mode selection with flags
MODE="$_MODE"

if [ -z "$1" ]; then
	scriptname=$(basename "$0")
	scheduled_modes="MORNING NOON AFTERNOON EVENING NIGHT"
	sorted=""
	for m in $scheduled_modes; do
		eval "h=\${${m}_HOUR}"
		sorted="$sorted$h:$m "
	done
	sorted=$(echo "$sorted" | tr ' ' '\n' | sort -n | cut -d: -f2 | tr '\n' ' ' | tr '[:upper:]' '[:lower:]')
	all_modes=$(grep -o '^[A-Z0-9_]*_TINT=' "$0" | sed 's/_TINT=//' | sort -u)
	custom=""
	for m in $all_modes; do
		case " $scheduled_modes " in *" $m "*) ;; *) custom="$custom $m" ;; esac
	done
	if [ -n "$custom" ]; then
		custom=$(echo "$custom" | tr '[:upper:]' '[:lower:]' | sort -u | tr '\n' ' ')
	fi
	printf '\033[36m'
	printf '██████╗ ██╗     ███████╗██╗    ██╗\n'
	printf '██╔══██╗██║     ██╔════╝██║    ██║\n'
	printf '██████╔╝██║     ███████╗██║ █╗ ██║\n'
	printf '██╔══██╗██║     ╚════██║██║███╗██║\n'
	printf '██████╔╝███████╗███████║╚███╔███╔╝\n'
	printf '╚═════╝ ╚══════╝╚══════╝ ╚══╝╚══╝ \n'
	printf '\033[0m'
	printf '         Blur Switch\n'
	printf '\033[2m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m\n'
	printf '\n'
	printf 'usage:      %s auto        #sets mode according to time\n' "$scriptname"
	printf '            %s morning     #sets mode to morning\n' "$scriptname"
	printf '\n'
	printf '     Note:The script can be renamed to whatever you like and placed anywhere.\n'
	printf '          If using the GUI and there is no blsw.sh script in the same directory\n'
	printf '          it will ask for the script location on first launch\n'
	printf '\n'
	printf '  [Scheduled modes] \n'
	printf '\n'
	for m in $sorted; do
		eval "h=\${$(echo "$m" | tr '[:lower:]' '[:upper:]')_HOUR}"
		printf '  %-12s (%s:00)\n' "$m" "$h"
	done
	if [ -n "$custom" ]; then
		printf '\n'
		printf '  [Custom Modes]    \n'
		printf '\n'
		for m in $custom; do
			printf '  %s\n' "$m"
		done
	fi
	printf '\n'
	exit 0
fi

# Load previous mode BEFORE determining new mode
_MODE="auto"
[ -f "$HOME/.blur-schedule" ] && . "$HOME/.blur-schedule"
PREVIOUS_MODE="$_MODE"

if [ ! -z "$1" ]; then
	MODE="$1"
fi

# determine current time-based mode
if [ "$h" -ge "$NIGHT_HOUR" ] || [ "$h" -lt "$MORNING_HOUR" ]; then
    CURRENT_MODE="night"
elif [ "$h" -ge "$EVENING_HOUR" ]; then
    CURRENT_MODE="evening"
elif [ "$h" -ge "$AFTERNOON_HOUR" ]; then
    CURRENT_MODE="afternoon"
elif [ "$h" -ge "$NOON_HOUR" ]; then
    CURRENT_MODE="noon"
elif [ "$h" -ge "$MORNING_HOUR" ]; then
    CURRENT_MODE="morning"
fi

# handle auto mode
if [ "$MODE" = "auto" ] || [ "$MODE" = "smart" ]; then
	MODE="auto"
	ACTIVE_MODE="$CURRENT_MODE"
else
	ACTIVE_MODE="$MODE"
fi

# Check if mode actually changed
MODE_CHANGED=false
if [ "$_MODE" != "$ACTIVE_MODE" ] && [ "$_MODE" != "auto" ]; then
	MODE_CHANGED=true
elif [ "$_MODE" = "auto" ] && [ "$ACTIVE_MODE" != "$CURRENT_MODE" ]; then
	MODE_CHANGED=true
fi

# read active mode values; empty vars are left unapplied so prior/manual values persist
MODE_UPPER=$(echo "$ACTIVE_MODE" | tr '[:lower:]' '[:upper:]')

for var in TINT OUTLINE_COLOR_ACTIVE OUTLINE_COLOR_INACTIVE SHADOW_COLOR SHADOW_COLOR_INACTIVE WALLPAPER FF_LOGO FF_LOGO_COLOR RGB; do
    eval "$var=\"\${${MODE_UPPER}_$var}\""
done

# nothing to change if all key vars are empty for this mode
if [ -z "$TINT" ] && [ -z "$OUTLINE_COLOR_ACTIVE" ] && [ -z "$OUTLINE_COLOR_INACTIVE" ] && \
   [ -z "$SHADOW_COLOR" ] && [ -z "$SHADOW_COLOR_INACTIVE" ] && \
   [ -z "$WALLPAPER" ] && [ -z "$FF_LOGO" ] && [ -z "$FF_LOGO_COLOR" ] && [ -z "$RGB" ]; then
    exit 0
fi

# update glass variables
[ -n "$TINT" ] && kwriteconfig6 --file kwinrc --group Effect-blurplus --key TintColor $TINT

# update kde-rounded-corners shadow and outline variables
[ -n "$SHADOW_COLOR" ] && kwriteconfig6 --file kwinrc --group "Round-Corners" --key ShadowColor $SHADOW_COLOR
[ -n "$SHADOW_COLOR_INACTIVE" ] && kwriteconfig6 --file kwinrc --group "Round-Corners" --key InactiveShadowColor $SHADOW_COLOR_INACTIVE
[ -n "$OUTLINE_COLOR_ACTIVE" ] && kwriteconfig6 --file kwinrc --group "Round-Corners" --key OutlineColor $OUTLINE_COLOR_ACTIVE
[ -n "$OUTLINE_COLOR_INACTIVE" ] && kwriteconfig6 --file kwinrc --group "Round-Corners" --key InactiveOutlineColor $OUTLINE_COLOR_INACTIVE

# change openrgb profile
[ -n "$RGB" ] && openrgb -p "$RGB"

# apply wallpaper & fastfetch logo
[ -n "$WALLPAPER" ] && plasma-apply-wallpaperimage "$WALLPAPER"
[ -n "$FF_LOGO" ] && EXTRA_JQ=".logo.source = \"$FF_LOGO\" |"
[ -n "$FF_LOGO_COLOR" ] && EXTRA_JQ="${EXTRA_JQ} .logo.color = { \"1\": \"$FF_LOGO_COLOR\" } |"
if [ -n "$FF_LOGO" ] || [ -n "$FF_LOGO_COLOR" ]; then
    jq "${EXTRA_JQ%|}" "$HOME/.config/fastfetch/config.jsonc" > tmp.json && mv tmp.json "$HOME/.config/fastfetch/config.jsonc"
fi

# reload kwin effects (fixes issue with some effects not updating correctly)
qdbus6 org.kde.KWin /Effects reconfigureEffect glass #update glass config
qdbus6 --literal org.kde.KWin /Effects org.kde.kwin.Effects.unloadEffect kwin4_effect_shapecorners #unload rounded-corners so colors update properly
qdbus6 --literal org.kde.KWin /Effects org.kde.kwin.Effects.loadEffect kwin4_effect_shapecorners #reload rounded-corners

# Save current mode
echo "_MODE=$ACTIVE_MODE" > "$HOME/.blur-schedule"

echo "Applied $ACTIVE_MODE mode settings"

# Only close Yakuake session if the mode actually changed
if [ "$MODE_CHANGED" = true ]; then
    if pstree -s $$ 2>/dev/null | grep -q yakuake; then
        echo "Running inside Yakuake, removing current session for reload"
        qdbus6 org.kde.yakuake /yakuake/sessions removeSession $(qdbus6 org.kde.yakuake /yakuake/sessions activeSessionId)
    else
        echo "Mode changed, waiting for Yakuake session to be idle..."
        YAKUAKE_PTY=$(for p in /dev/pts/*; do [ -n "$(ps -t $(basename $p) -o pid= 2>/dev/null | head -1)" ] && pstree -s $(ps -t $(basename $p) -o pid= | head -1) 2>/dev/null | grep -q yakuake && basename $p && break; done) && [ -n "$YAKUAKE_PTY" ] && while ps -t "$YAKUAKE_PTY" -o comm= 2>/dev/null | grep -v -E '^(bash|zsh|fish|sh|dash|ksh|tcsh)$' | grep -q .; do sleep 1; done; qdbus6 org.kde.yakuake /yakuake/sessions removeSession $(qdbus6 org.kde.yakuake /yakuake/sessions activeSessionId)
    fi
else
    echo "Mode unchanged, skipping Yakuake session restart"
fi
