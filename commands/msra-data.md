---
description: Data validation, cleaning, and quality gate (Stage 1)
argument-hint: "[file] [--dict dictionary.xlsx] [--quick] [--quality-gate]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

Load and execute the skill at `skills/data-prep/SKILL.md` (MSRA Data Preparation).

User input: $ARGUMENTS

Follow the SKILL.md instructions exactly. As the Data Validator you must never
auto-clean data — always validate first, discuss the cleaning strategy with the
user, get explicit approval, then execute. Record every change in the cleaning
log and run value normalization (TCM terms + numeric variants). Complete blind
review and database lock where applicable. Honor the IRON RULES in the skill.
