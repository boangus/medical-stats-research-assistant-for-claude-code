# Cohort Demo Dataset (cohort_demo.csv)

> MSRA Pipeline Stage 1-4 Quickstart | 10-min walkthrough

## Overview

Simulated prospective observational cohort studying the association between smoking and cardiovascular events.
Design follows **STROBE 2007** reporting guidelines.

- **N**: 500 patients
- **Exposure**: Smoking status (30% prevalence)
- **Primary outcome**: Cardiovascular event during follow-up
- **Follow-up**: 1-10 years (uniform distribution)

## Data Dictionary

| Column | Type | Description |
|--------|------|-------------|
| `patient_id` | string | Unique identifier, format `COH-001` to `COH-500` |
| `age` | integer | Age in years (range 25-85) |
| `sex` | binary | 0 = Female, 1 = Male |
| `smoking` | binary | 0 = Non-smoker, 1 = Current smoker |
| `bmi` | float | Body mass index (kg/m^2), range 16-45 |
| `diabetes` | binary | 0 = No, 1 = Yes (type 2 diabetes) |
| `follow_up_years` | float | Duration of follow-up (years) |
| `event` | binary | 0 = No event, 1 = CV event during follow-up |

## Expected Results (ground truth)

| Group | Event Rate |
|-------|-----------|
| Smokers | ~56% |
| Non-smokers | ~40% |

Smoking is associated with higher event risk (crude OR ~1.9). Age, BMI, and diabetes are confounders that should be adjusted in multivariable analysis.

## Suggested MSRA Pipeline Flow

1. **Stage 1 (data-prep)**: Load CSV, check distributions, identify confounders via DAG
2. **Stage 2 (analysis-plan)**: Primary = logistic regression (event ~ smoking + age + bmi + diabetes); Secondary = Kaplan-Meier + Cox PH
3. **Stage 3 (analysis-exec)**: Fit logistic model, compute adjusted OR with 95% CI; Cox model for HR
4. **Stage 4 (report)**: Generate STROBE checklist, Table 1 (baseline by smoking), Table 2 (regression results), KM curves

## Quick Verification

```python
import pandas as pd
df = pd.read_csv("cohort_demo.csv")
print(df.groupby("smoking")["event"].mean())
# Expected: smokers have ~15 percentage points higher event rate
print(df.groupby("event")[["age","bmi"]].mean())
# Expected: events associated with higher age and BMI
```
