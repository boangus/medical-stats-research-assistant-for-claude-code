# RCT Demo Dataset (rct_demo.csv)

> MSRA Pipeline Stage 1-4 Quickstart | 10-min walkthrough

## Overview

Simulated parallel-group randomized controlled trial evaluating an antihypertensive drug vs placebo.
Design follows **CONSORT 2010** reporting guidelines.

- **N**: 200 patients (1:1 randomization)
- **Primary endpoint**: Change in systolic blood pressure (SBP) at Week 12
- **Safety endpoint**: Adverse event incidence

## Data Dictionary

| Column | Type | Description |
|--------|------|-------------|
| `patient_id` | string | Unique identifier, format `RCT-001` to `RCT-200` |
| `age` | integer | Age in years (range 30-80) |
| `sex` | binary | 0 = Female, 1 = Male |
| `treatment` | binary | 0 = Placebo, 1 = Active treatment |
| `baseline_sbp` | float | Baseline systolic BP (mmHg), ~145 mmHg mean |
| `week12_sbp` | float | Week 12 systolic BP (mmHg) |
| `adverse_event` | binary | 0 = No, 1 = Yes (AE during trial) |

## Expected Results (ground truth)

| Metric | Treatment | Placebo |
|--------|-----------|---------|
| Mean SBP change | ~-10.4 mmHg | ~-2.2 mmHg |
| Adverse event rate | ~12% | ~5% |

The treatment effect (~8 mmHg difference) is statistically significant (p < 0.001 by two-sample t-test).

## Suggested MSRA Pipeline Flow

1. **Stage 1 (data-prep)**: Load CSV, check missing values, verify randomization balance
2. **Stage 2 (analysis-plan)**: Primary = ANCOVA on week12_sbp adjusting baseline_sbp; Safety = Fisher exact test
3. **Stage 3 (analysis-exec)**: Run t-test / ANCOVA, compute 95% CI of treatment effect
4. **Stage 4 (report)**: Generate CONSORT flow diagram, Table 1 (baseline), Table 2 (outcomes)

## Quick Verification

```python
import pandas as pd
df = pd.read_csv("rct_demo.csv")
print(df.groupby("treatment")[["baseline_sbp","week12_sbp"]].mean())
# Expected: treatment group ~10 mmHg lower SBP at week 12
```
