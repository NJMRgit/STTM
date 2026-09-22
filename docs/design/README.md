---
title: "STTM design documents"
section: root
doc_type: index
id: "STTM/index"
description: >
  Entry point for the STTM design documents: one document per flow, each
  declaring the source files it governs.
status: current
updated: "2026-09-22"
tags: [index, spec, STTM]
---

# STTM design documents

The behavioural specification for STTM. One document per flow; each declares
the files it governs in its `source_files` frontmatter, so a change to a
governed file must update its document (the `~/Projects/dev-standard` rule,
enforced by `scripts/dev/spec-gate`).

- [mode-and-colour.md](mode-and-colour.md) — modes, the symbolic colour
  sources, OpenRGB profiles and the keyboard write.
- [testing.md](testing.md) — what the suite covers and what it deliberately
  does not.
