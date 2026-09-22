---
title: "STTM — tests"
section: Validation
doc_type: spec
id: "sttm/testing"
description: >
  What the STTM suite covers, what it deliberately does not, and the commands.
status: current
updated: "2026-09-22"
related:
  - docs/design/mode-and-colour.md
tags: [spec, sttm, tests]
---

# Tests

The suite is the standard library's runner, so no dependency is needed:

```
python3 -m unittest discover -s tests -t .
```

`scripts/dev/spec-gate` runs it (plus spec coherence) and is the gate.

Covered: the `install.sha256` integrity rule, and the pure colour logic in
`kb-rgb` (`rgb_to_hsv_bytes`, `parse_overrides` including the symbolic-colour
path).

Not covered, on purpose: anything that needs the hardware or the
daemon — the actual USB write, the OpenRGB SDK reads, the KDE theme files and
the wallpaper switch. Those are verified by hand on the machine; a test that
fakes them would only pin the fake.
