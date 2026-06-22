---
description: Exploratory causal analysis — discover potential causal structures from data
argument-hint: "[file] [--mode causal-discovery|confounding-analysis|exploratory-eda|hypothesis-generation|sensitivity-pre|direction-advisory]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

Load and execute the skill at `skills/exploratory-causal/SKILL.md` (MSRA Exploratory Causal Analysis).

User input: $ARGUMENTS

Follow the SKILL.md instructions exactly:
- **Guard check**: Verify Stage 1.5 data quality gate has passed (cleaned data available).
- Run the exploratory causal analysis workflow (5 phases).
- Present findings as **exploratory** (hypothesis-generating, not confirmatory).
- Output a research direction report that feeds into Stage 2 (analysis-plan).
