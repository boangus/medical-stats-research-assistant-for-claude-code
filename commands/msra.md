---
description: Launch MSRA pipeline with auto-detect entry point
argument-hint: "[context] [--from <stage>] [--status] [--resume]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

Load and execute the skill at `skills/pipeline/SKILL.md` (MSRA Pipeline Orchestrator).

User input: $ARGUMENTS

Follow the SKILL.md instructions exactly. As the orchestrator you must:
- Detect the entry stage from the user's intent (Stage 1 data / Stage 2 plan / Stage 3 exec / Stage 4 report).
- Run the Material Passport pre-checks before entering any stage.
- Dispatch to the appropriate sub-skill (`data-prep`, `analysis-plan`, `analysis-exec`, `report`, `calibration`); do NOT do substantive statistical work yourself.
- Enforce the three MANDATORY blocking quality gates (Stage 1.5 / 2.5 / 3.5) and the convergence / rollback rules.
- Do not paraphrase, soften, or skip the orchestrator's IRON RULES.
