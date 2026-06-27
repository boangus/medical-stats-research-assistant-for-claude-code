#!/usr/bin/env python3
"""
Generate 3 demo datasets for MSRA Pipeline quickstart (10-min walkthrough).

Seed: 42 (fully reproducible)
Dependencies: numpy, pandas (standard scientific Python stack)

Output:
  1. rct_demo.csv          — 200 rows, antihypertensive RCT
  2. cohort_demo.csv       — 500 rows, observational cohort
  3. diagnostic_demo.csv   — 300 rows, diagnostic accuracy study
"""

import numpy as np
import pandas as pd
from pathlib import Path

SEED = 42
OUT_DIR = Path(__file__).parent

rng = np.random.default_rng(SEED)


# ============================================================
# 1. RCT Demo — Antihypertensive Drug Trial (CONSORT-style)
# ============================================================
def generate_rct(n=200):
    """Parallel-group RCT: treatment vs placebo on systolic BP."""
    # Randomization 1:1
    treatment = rng.integers(0, 2, size=n)

    # Demographics
    age = rng.normal(55, 10, size=n).clip(30, 80).astype(int)
    sex = rng.integers(0, 2, size=n)  # 0=Female, 1=Male

    # Baseline SBP: ~145 mmHg, slightly higher in older patients
    baseline_sbp = (140 + 0.15 * age + rng.normal(0, 8, size=n)).round(1)

    # Treatment effect: -10 mmHg (treatment) vs -2 mmHg (placebo) + noise
    delta = np.where(treatment == 1, -10.0, -2.0)
    week12_sbp = (baseline_sbp + delta + rng.normal(0, 5, size=n)).round(1)

    # Adverse events: treatment arm ~12%, placebo ~5%
    ae_prob = np.where(treatment == 1, 0.12, 0.05)
    adverse_event = (rng.random(n) < ae_prob).astype(int)

    df = pd.DataFrame({
        "patient_id": [f"RCT-{i:03d}" for i in range(1, n + 1)],
        "age": age,
        "sex": sex,
        "treatment": treatment,
        "baseline_sbp": baseline_sbp,
        "week12_sbp": week12_sbp,
        "adverse_event": adverse_event,
    })
    return df


# ============================================================
# 2. Cohort Demo — Observational Cohort (STROBE-style)
# ============================================================
def generate_cohort(n=500):
    """Prospective cohort: smoking → cardiovascular event."""
    age = rng.normal(50, 12, size=n).clip(25, 85).astype(int)
    sex = rng.integers(0, 2, size=n)

    # Smoking prevalence ~30%
    smoking = (rng.random(n) < 0.30).astype(int)

    # BMI: slightly higher in smokers (common confounder)
    bmi = (24 + 2 * smoking + rng.normal(0, 3.5, size=n)).round(1).clip(16, 45)

    # Diabetes: ~15% prevalence, correlated with BMI
    diabetes_prob = 1 / (1 + np.exp(-( -5 + 0.12 * bmi )))
    diabetes = (rng.random(n) < diabetes_prob).astype(int)

    # Follow-up: 1-10 years, uniform-ish
    follow_up_years = rng.uniform(1.0, 10.0, size=n).round(1)

    # Event: logistic model — smoking increases risk (OR ~2.0)
    logit = (-4.0 + 0.4 * smoking + 0.03 * age + 0.08 * bmi + 0.5 * diabetes)
    event_prob = 1 / (1 + np.exp(-logit))
    event = (rng.random(n) < event_prob).astype(int)

    df = pd.DataFrame({
        "patient_id": [f"COH-{i:03d}" for i in range(1, n + 1)],
        "age": age,
        "sex": sex,
        "smoking": smoking,
        "bmi": bmi,
        "diabetes": diabetes,
        "follow_up_years": follow_up_years,
        "event": event,
    })
    return df


# ============================================================
# 3. Diagnostic Demo — Biomarker Accuracy Study (STARD-style)
# ============================================================
def generate_diagnostic(n=300):
    """Cross-sectional: biomarker vs gold-standard diagnosis."""
    age = rng.normal(55, 12, size=n).clip(20, 85).astype(int)
    sex = rng.integers(0, 2, size=n)

    # Gold standard: ~35% disease prevalence
    gold_standard = (rng.random(n) < 0.35).astype(int)

    # Biomarker: higher in diseased (AUC ~0.85)
    mu_diseased, mu_healthy = 75, 50
    sigma = 15
    biomarker_value = np.where(
        gold_standard == 1,
        rng.normal(mu_diseased, sigma, size=n),
        rng.normal(mu_healthy, sigma, size=n),
    ).round(2).clip(0, 150)

    df = pd.DataFrame({
        "patient_id": [f"DIA-{i:03d}" for i in range(1, n + 1)],
        "gold_standard": gold_standard,
        "biomarker_value": biomarker_value,
        "age": age,
        "sex": sex,
    })
    return df


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    # Generate
    rct = generate_rct(200)
    cohort = generate_cohort(500)
    diag = generate_diagnostic(300)

    # Save CSV (UTF-8 with BOM for Excel compatibility)
    rct.to_csv(OUT_DIR / "rct_demo.csv", index=False, encoding="utf-8-sig")
    cohort.to_csv(OUT_DIR / "cohort_demo.csv", index=False, encoding="utf-8-sig")
    diag.to_csv(OUT_DIR / "diagnostic_demo.csv", index=False, encoding="utf-8-sig")

    # Quick verification
    print("=== RCT Demo ===")
    print(f"  Rows: {len(rct)}, Columns: {list(rct.columns)}")
    print(f"  Treatment group SBP change: {(rct.loc[rct.treatment==1, 'week12_sbp'] - rct.loc[rct.treatment==1, 'baseline_sbp']).mean():.1f} mmHg")
    print(f"  Placebo group SBP change:   {(rct.loc[rct.treatment==0, 'week12_sbp'] - rct.loc[rct.treatment==0, 'baseline_sbp']).mean():.1f} mmHg")
    print(f"  AE rate (treatment): {rct.loc[rct.treatment==1, 'adverse_event'].mean():.1%}")
    print(f"  AE rate (placebo):   {rct.loc[rct.treatment==0, 'adverse_event'].mean():.1%}")

    print("\n=== Cohort Demo ===")
    print(f"  Rows: {len(cohort)}, Columns: {list(cohort.columns)}")
    print(f"  Smoking prevalence: {cohort.smoking.mean():.1%}")
    print(f"  Event rate (smokers):    {cohort.loc[cohort.smoking==1, 'event'].mean():.1%}")
    print(f"  Event rate (non-smokers):{cohort.loc[cohort.smoking==0, 'event'].mean():.1%}")

    print("\n=== Diagnostic Demo ===")
    print(f"  Rows: {len(diag)}, Columns: {list(diag.columns)}")
    print(f"  Disease prevalence: {diag.gold_standard.mean():.1%}")
    print(f"  Biomarker (diseased):  {diag.loc[diag.gold_standard==1, 'biomarker_value'].mean():.1f}")
    print(f"  Biomarker (healthy):   {diag.loc[diag.gold_standard==0, 'biomarker_value'].mean():.1f}")

    print("\nAll 3 CSV files saved to:", OUT_DIR)
