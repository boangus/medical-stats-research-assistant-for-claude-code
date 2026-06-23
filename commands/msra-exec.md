---
description: Execute analysis per approved SAP (Stage 3)
argument-hint: "--sap [plan] --data [data] [--check-only]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

Load and execute the skill at `skills/analysis-exec/SKILL.md` (MSRA Analysis Execution).

User input: $ARGUMENTS

Follow the SKILL.md instructions exactly. As the Exec Runner (Phase 0-6) and
Exec Inference (Phase 7-9) you must execute strictly per the approved SAP:
sample-size verification, variable construction, descriptive stats (Table 1),
compliance, primary analysis, sensitivity/safety/subgroup analyses, independent
hypothesis testing, and the results quality check. Do not deviate from the SAP
without recording a deviation. Honor the IRON RULES in the skill.
