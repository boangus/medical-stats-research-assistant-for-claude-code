---
description: Run metric calibration against a gold standard, or view calibration status
argument-hint: "[gold_standard.csv] [--status] [--update results.csv]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

Load and execute the skill at `skills/calibration/SKILL.md` (MSRA Calibration).

User input: $ARGUMENTS

Follow the SKILL.md instructions exactly. This is the experimental calibration
mode: compare pipeline outputs against a user-supplied gold standard, update the
calibration database (`calibration_db.json`) with cumulative TPR/FPR per method
type, and expose calibration confidence to the Stage 3.5 results quality gate.
Honor the IRON RULES in the skill.
