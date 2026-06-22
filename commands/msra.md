---
description: Launch MSRA pipeline with auto-detect entry point
argument-hint: "[context] [--from <stage>] [--status] [--resume]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

Load and execute the skill at `skills/pipeline/SKILL.md` (MSRA Pipeline Orchestrator).

User input: $ARGUMENTS

Follow the SKILL.md instructions exactly. As the orchestrator you must:
- Detect the entry stage from the user's intent (Stage 1 data / Stage 2 plan / Stage 3 exec / Stage 4 report / Stage 5 paper track).
- Run the Material Passport pre-checks before entering any stage.
- Dispatch to the appropriate sub-skill (`data-prep`, `analysis-plan`, `analysis-exec`, `report`, `calibration`, `pipeline`); do NOT do substantive statistical work yourself.
- Enforce the four MANDATORY blocking quality gates (Stage 1.5 / 2.5 / 3.5) and the Stage 4 checkpoint (M4') with [A] report_only / [B] full_paper decision.
- When Stage 4 checkpoint [B] is chosen: generate MSRA Handoff Bundle via `scripts/generate_msra_handoff_bundle.py`, then dispatch to `pipeline` for Paper Track (Stage 5.1-5.9).
- Reject users who have no data processing needs but ask to "write paper" 鈥?redirect to MSRA's `medical-paper` / `pipeline` directly.
- Do not paraphrase, soften, or skip the orchestrator's IRON RULES.
