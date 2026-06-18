---
description: Enter MSRA Paper Track (Stage 5.0) — convert stats report into a submittable paper
argument-hint: ""
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

Load and execute the skill at `skills/pipeline/SKILL.md` (MSRA Pipeline Orchestrator), starting at Stage 5.0 (Paper Intake).

User input: $ARGUMENTS

Follow the SKILL.md instructions exactly, focusing on the Paper Track entry path:
- **Guard check (IRON RULE)**: Verify passport `track == "full_paper"` and Stage 4 artifacts (final_report + figures + tables) are complete. If guard fails, refuse and explain what is missing.
- Run `scripts/generate_msra_handoff_bundle.py` to generate the MSRA Handoff Bundle.
- Present the Paper Intake workflow: reporting-guideline selection, journal template selection, paper configuration prefill.
- Dispatch to `academic-pipeline` for the full writing/review/revise pipeline (Stage 5.1-5.9).
- Do NOT re-implement the writing pipeline yourself — delegate to academic-pipeline (which manages deep-research, academic-paper, academic-paper-reviewer).
