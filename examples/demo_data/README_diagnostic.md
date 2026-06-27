# Diagnostic Demo Dataset (diagnostic_demo.csv)

> MSRA Pipeline Stage 1-4 Quickstart | 10-min walkthrough

## Overview

Simulated cross-sectional diagnostic accuracy study evaluating a biomarker against a gold-standard reference.
Design follows **STARD 2015** reporting guidelines.

- **N**: 300 patients
- **Index test**: Continuous biomarker value
- **Reference standard**: Gold-standard binary diagnosis (35% disease prevalence)
- **Target AUC**: ~0.85

## Data Dictionary

| Column | Type | Description |
|--------|------|-------------|
| `patient_id` | string | Unique identifier, format `DIA-001` to `DIA-300` |
| `gold_standard` | binary | 0 = Healthy, 1 = Disease (reference diagnosis) |
| `biomarker_value` | float | Continuous biomarker concentration (AU), range 0-150 |
| `age` | integer | Age in years (range 20-85) |
| `sex` | binary | 0 = Female, 1 = Male |

## Expected Results (ground truth)

| Group | Mean Biomarker |
|-------|---------------|
| Disease (gold_standard=1) | ~73.5 |
| Healthy (gold_standard=0) | ~50.9 |

The biomarker shows clear separation between groups, yielding an AUC of approximately 0.85.

## Suggested MSRA Pipeline Flow

1. **Stage 1 (data-prep)**: Load CSV, check distributions, verify no missing data
2. **Stage 2 (analysis-plan)**: Primary = ROC curve + AUC; Secondary = sensitivity/specificity at optimal cutoff (Youden index)
3. **Stage 3 (analysis-exec)**: Compute ROC, AUC with 95% CI, optimal cutoff, likelihood ratios
4. **Stage 4 (report)**: Generate STARD flow diagram, ROC plot, Table of sensitivity/specificity at multiple cutoffs

## Quick Verification

```python
import pandas as pd
df = pd.read_csv("diagnostic_demo.csv")
print(df.groupby("gold_standard")["biomarker_value"].mean())
# Expected: diseased group ~22 points higher
# AUC ~0.85 (can verify with sklearn.metrics.roc_auc_score)
```
