---
description: ARS academic-paper — 9 modes for paper writing, revision, and export
argument-hint: "--mode <abstract-only|citation-check|disclosure|format-convert|outline-only|plan|revision|revision-coach|lit-review>"
---

Trigger the `academic-paper` skill (via `report/SKILL.md`) in the specified mode.

## Available Modes

| Mode | Output | Model |
|------|--------|-------|
| `abstract-only` | Bilingual abstract (zh-TW + EN) + keywords | sonnet |
| `citation-check` | Citation error report | sonnet |
| `disclosure` | AI-usage disclosure statement | sonnet |
| `format-convert` | Convert between LaTeX/DOCX/PDF/Markdown | sonnet |
| `outline-only` | Detailed outline + evidence map | sonnet |
| `plan` | Socratic chapter-by-chapter planning | sonnet |
| `revision` | Revised draft + R&R responses | sonnet |
| `revision-coach` | Revision Roadmap + Response Letter skeleton | opus |
| `lit-review` | Annotated bibliography as literature review section | sonnet |

## Usage

```
/ars-paper --mode abstract-only
/ars-paper --mode plan
/ars-paper --mode revision-coach
```

## Dispatch

Parse the `--mode` flag from `$ARGUMENTS`. If missing or invalid, list available modes and ask the user to choose.

Load the skill at `report/SKILL.md` and invoke it in the specified mode. For `revision-coach`, use the opus model per project policy for review-interpretation depth; all other modes use sonnet.
