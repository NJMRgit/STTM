---
title: "STTM — modes, colours and the keyboard write"
section: Backend
doc_type: spec
id: "sttm/mode-and-colour"
description: >
  How STTM picks a mode and a colour, how the symbolic colour sources
  (tint, outline, logo, live) resolve, and how a keyboard colour reaches
  the hardware.
status: current
updated: "2026-09-22"
source_files:
  - setup (the installer that consumes install/install.sha256)
  - kb-rgb
  - blsw
  - sttm
  - install
  - install.sha256
related:
  - docs/design/testing.md
tags: [spec, sttm, colours, keyboard]
---

# Modes, colours and the keyboard write

## Modes

STTM switches a KDE Plasma theme by time of day: five default modes
(Morning, Noon, Afternoon, Evening, Night), each with a configurable trigger
hour. `sttm` owns the mode state; a tool that needs it reads the state
(`kb-rgb`'s `state_mode`) and accepts `--mode <name>` to override it for one
run, which is what `blsw` passes when it drives the keyboard from the same
theme switch.

## Colour sources

The keyboard colour is chosen in this order:

1. `--rgb #RRGGBB` — an explicit colour.
2. `--rgb <symbol>` — a **symbolic** source, never parsed as a colour:
   `tint` (the mode accent), `outline`, `logo` (the fastfetch accent) or
   `live` (the colour the OpenRGB daemon currently reports).
3. `--theme <field>` / `--accent <field>` / `--live` — the same symbolic
   sources named directly.
4. Empty or absent — the theme's own default.

Symbolic values resolve through the theme lookup (`theme_colour`, with
`THEME_FIELDS` mapping the log's field names onto the theme keys) or, for
`live`, through the OpenRGB SDK. A symbolic value that is mistaken for a hex
colour is a bug: the last fix of that class is pinned by
`tests/test_kb_rgb.py::test_symbolic_colour_is_a_theme_source_not_an_rgb`.

## Brightness and saturation

`--value`, `--sat` and `--hsv h,s,v` adjust the resolved colour before it is
written. The RGB/HSV conversion is `rgb_to_hsv_bytes`, whose contract (0–255
per channel, hue scaled to 0–255) is pinned by the unit tests.

## OpenRGB profiles

`profile_paths` looks for a profile under `/etc/openrgb/profiles` and
`~/.config/OpenRGB/profiles`, trying the name as given and in lower case,
capitalised and upper case; `profile_base_rgb` reads the profile's base
colour, which is what `tint`-style themes are derived from. Writes that need
the daemon go through the SDK socket; `--live` reads the current colour back
from it.

## The keyboard write

Writes go over the USB-C cable only: the 2.4 GHz dongle has no command
channel. Supported models are an explicit list (currently the Keychron K2 HE);
an unsupported keyboard must fail loudly rather than write garbage.

## Install integrity

`install.sha256` must match the committed `install` script, because a stale
checksum makes every clean curl-pipe install fail its own self check. The rule
is enforced by CI and by
`tests/test_install_integrity.py::InstallChecksum::test_install_matches_install_sha256`.
