---
description: Create and review the statistical analysis plan (Stage 2)
argument-hint: "[data] [--study RCT|observational|diagnostic] [--quick]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

Load and execute the skill at `skills/analysis-plan/SKILL.md` (MSRA Analysis Planning).

User input: $ARGUMENTS

Follow the SKILL.md instructions exactly. As the Method Consultant you define
estimands (ICH E9(R1)), discuss method selection with the user, draft the SAP,
and run the plan review. Branch by study type (RCT → ITT/PP + ANCOVA;
observational → DAG + PSM/IPTW; diagnostic → AUC + gold-standard bias).
Honor the IRON RULES in the skill.
