#!/usr/bin/env python3
"""
Synthetic Clinical Data Fixture Generator for E2E Pipeline Testing
=================================================================

Generates 3 synthetic clinical datasets, each embedding 10-15 known
data quality issues for regression testing of the MSRA data pipeline.

Datasets:
  1. rct_dataset.csv      -- Two-arm RCT (n=200)
  2. cohort_dataset.csv    -- Prospective cohort (n=300)
  3. case_control.csv      -- Case-control study (n=150)

Each dataset intentionally contains quality issues classified by type:
  - Type errors (TC)
  - Range violations (RC)
  - Logic contradictions (LC)
  - Missing data patterns (MD)
  - Duplicate rows (DP)
  - Format issues (FI)
  - Encoding inconsistencies (EI)
  - Extreme outliers (EO)

Usage:
    python -m tests.fixtures.generate_synthetic_clinical
"""

import csv
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(2026)

FIXTURES_DIR = Path(__file__).parent


def _rand_date(base_year=2022, span_days=730):
    base = datetime(base_year, 1, 1)
    return base + timedelta(days=random.randint(0, span_days))


def _inject_missing(value, prob=0.03):
    return "" if random.random() < prob else value


# =========================================================================
# Dataset 1: RCT (Two-arm, n=200)
# Known issues: 12
# =========================================================================
def generate_rct(n=200):
    """Generate a two-arm RCT dataset with embedded quality issues."""
    rows = []
    for i in range(n):
        row = {}
        pid = f"RCT-{i+1:04d}"
        row["subject_id"] = pid

        # Age: integer 18-75
        row["age"] = random.randint(18, 75)
        row["sex"] = random.choice(["M", "F"])
        row["bmi"] = round(random.uniform(18.5, 35.0), 1)
        row["treatment"] = random.choice(["Drug_A", "Placebo"])
        row["baseline_sbp"] = random.randint(110, 160)
        row["baseline_dbp"] = random.randint(60, 100)
        row["followup_sbp"] = random.randint(100, 150)
        row["followup_dbp"] = random.randint(55, 95)
        row["adverse_event"] = random.choice(["None", "Mild", "Moderate"])
        row["dropout"] = random.choice([0, 0, 0, 0, 1])
        row["enroll_date"] = _rand_date().strftime("%Y-%m-%d")
        row["end_date"] = (_rand_date() + timedelta(days=180)).strftime("%Y-%m-%d")
        rows.append(row)

    # ── Issue 1 (TC): Age as string in row 10 ──
    rows[10]["age"] = "thirty-five"

    # ── Issue 2 (RC): Negative BMI in row 20 ──
    rows[20]["bmi"] = -3.2

    # ── Issue 3 (RC): SBP > 300 in row 30 ──
    rows[30]["baseline_sbp"] = 320

    # ── Issue 4 (LC): end_date before enroll_date in row 40 ──
    rows[40]["end_date"] = "2021-01-15"
    rows[40]["enroll_date"] = "2023-06-01"

    # ── Issue 5 (MD): Bulk missing followup_sbp rows 50-55 ──
    for j in range(50, 56):
        rows[j]["followup_sbp"] = ""

    # ── Issue 6 (DP): Duplicate rows 60-61 ──
    rows[61] = dict(rows[60])
    rows[61]["subject_id"] = "RCT-0062"  # different ID, same data

    # ── Issue 7 (EI): Inconsistent sex encoding row 70 ──
    rows[70]["sex"] = "male"  # lowercase

    # ── Issue 8 (EO): Extreme outlier BMI row 80 ──
    rows[80]["bmi"] = 99.9

    # ── Issue 9 (FI): Date format inconsistency row 90 ──
    rows[90]["enroll_date"] = "06/15/2023"  # MM/DD/YYYY instead of YYYY-MM-DD

    # ── Issue 10 (RC): DBP > SBP (logic) row 100 ──
    rows[100]["baseline_sbp"] = 80
    rows[100]["baseline_dbp"] = 120

    # ── Issue 11 (TC): Numeric treatment value row 110 ──
    rows[110]["treatment"] = "1"  # should be Drug_A or Placebo

    # ── Issue 12 (MD): MAR pattern -- dropout=1 has missing followup ──
    for j in range(n):
        if rows[j]["dropout"] == 1 and random.random() < 0.8:
            rows[j]["followup_dbp"] = ""

    columns = [
        "subject_id", "age", "sex", "bmi", "treatment",
        "baseline_sbp", "baseline_dbp", "followup_sbp", "followup_dbp",
        "adverse_event", "dropout", "enroll_date", "end_date",
    ]
    return columns, rows


# =========================================================================
# Dataset 2: Cohort (Prospective, n=300)
# Known issues: 13
# =========================================================================
def generate_cohort(n=300):
    """Generate a prospective cohort dataset with embedded quality issues."""
    rows = []
    for i in range(n):
        row = {}
        row["patient_id"] = f"COH-{i+1:04d}"
        row["age"] = random.randint(20, 80)
        row["sex"] = random.choice(["Male", "Female"])
        row["smoking"] = random.choice(["Never", "Former", "Current"])
        row["alcohol"] = random.choice(["None", "Social", "Regular"])
        row["diabetes"] = random.choice([0, 1])
        row["hypertension"] = random.choice([0, 1])
        row["cholesterol"] = round(random.uniform(3.0, 8.0), 1)
        row["hba1c"] = round(random.uniform(4.5, 12.0), 1)
        row["egfr"] = round(random.uniform(15, 120), 1)
        row["outcome_event"] = random.choice([0, 0, 0, 1])
        row["followup_months"] = random.randint(6, 60)
        row["center"] = random.choice(["Beijing", "Shanghai", "Guangzhou"])
        rows.append(row)

    # ── Issue 1 (TC): Age as float row 5 ──
    rows[5]["age"] = 45.7  # should be integer

    # ── Issue 2 (RC): HbA1c > 20% row 15 ──
    rows[15]["hba1c"] = 25.3

    # ── Issue 3 (RC): eGFR < 0 row 25 ──
    rows[25]["egfr"] = -5.0

    # ── Issue 4 (EI): Sex encoding "1"/"0" row 35 ──
    rows[35]["sex"] = "1"

    # ── Issue 5 (EI): Smoking encoding "Y/N" row 45 ──
    rows[45]["smoking"] = "Y"

    # ── Issue 6 (MD): Bulk missing cholesterol rows 55-62 ──
    for j in range(55, 63):
        rows[j]["cholesterol"] = ""

    # ── Issue 7 (DP): Duplicate rows 70-71 ──
    rows[71] = dict(rows[70])

    # ── Issue 8 (EO): Extreme cholesterol outlier row 80 ──
    rows[80]["cholesterol"] = 35.0

    # ── Issue 9 (LC): diabetes=0 but hba1c=11.5 row 90 ──
    rows[90]["diabetes"] = 0
    rows[90]["hba1c"] = 11.5

    # ── Issue 10 (FI): Center name inconsistency row 100 ──
    rows[100]["center"] = "beijing"  # lowercase

    # ── Issue 11 (FI): Center name with space row 110 ──
    rows[110]["center"] = " Shanghai"  # leading space

    # ── Issue 12 (RC): followup_months = 0 row 120 ──
    rows[120]["followup_months"] = 0

    # ── Issue 13 (MD): MNAR -- outcome_event=1 has more missing cholesterol ──
    for j in range(n):
        if rows[j]["outcome_event"] == 1 and random.random() < 0.3:
            rows[j]["cholesterol"] = ""

    columns = [
        "patient_id", "age", "sex", "smoking", "alcohol",
        "diabetes", "hypertension", "cholesterol", "hba1c", "egfr",
        "outcome_event", "followup_months", "center",
    ]
    return columns, rows


# =========================================================================
# Dataset 3: Case-Control (n=150)
# Known issues: 11
# =========================================================================
def generate_case_control(n=150):
    """Generate a case-control dataset with embedded quality issues."""
    rows = []
    for i in range(n):
        row = {}
        row["id"] = f"CC-{i+1:04d}"
        row["age"] = random.randint(30, 70)
        row["sex"] = random.choice(["M", "F"])
        row["case_status"] = 1 if i < 75 else 0  # 75 cases, 75 controls
        row["exposure"] = random.choice([0, 1])
        row["bmi"] = round(random.uniform(18, 40), 1)
        row["systolic_bp"] = random.randint(100, 180)
        row["fasting_glucose"] = round(random.uniform(3.5, 15.0), 1)
        row["smoking_years"] = random.randint(0, 40)
        row["family_history"] = random.choice([0, 1])
        row["occupation"] = random.choice(["Office", "Manual", "Service", "Other"])
        row["enrollment_date"] = _rand_date(2021, 365).strftime("%Y-%m-%d")
        rows.append(row)

    # ── Issue 1 (TC): case_status as "Yes"/"No" row 5 ──
    rows[5]["case_status"] = "Yes"

    # ── Issue 2 (RC): BMI = 0 row 15 ──
    rows[15]["bmi"] = 0

    # ── Issue 3 (RC): Fasting glucose < 1 row 25 ──
    rows[25]["fasting_glucose"] = 0.5

    # ── Issue 4 (TC): Smoking years negative row 35 ──
    rows[35]["smoking_years"] = -5

    # ── Issue 5 (EI): Sex encoding "男"/"女" row 45 ──
    rows[45]["sex"] = "男"

    # ── Issue 6 (MD): Bulk missing BMI rows 55-58 ──
    for j in range(55, 59):
        rows[j]["bmi"] = ""

    # ── Issue 7 (DP): Duplicate row 65 ──
    rows[64] = dict(rows[63])
    rows[64]["id"] = "CC-0065"

    # ── Issue 8 (EO): Systolic BP = 350 row 70 ──
    rows[70]["systolic_bp"] = 350

    # ── Issue 9 (LC): smoking_years=30 but age=25 row 80 ──
    rows[80]["age"] = 25
    rows[80]["smoking_years"] = 30

    # ── Issue 10 (FI): Date format row 90 ──
    rows[90]["enrollment_date"] = "2022/03/15"  # slash instead of dash

    # ── Issue 11 (EI): Occupation encoding row 100 ──
    rows[100]["occupation"] = "office worker"  # not in standard set

    columns = [
        "id", "age", "sex", "case_status", "exposure", "bmi",
        "systolic_bp", "fasting_glucose", "smoking_years",
        "family_history", "occupation", "enrollment_date",
    ]
    return columns, rows


# =========================================================================
# Known Issue Registry
# =========================================================================

KNOWN_ISSUES = {
    "rct": [
        {"id": "RCT-TC-01", "type": "type_error", "row_hint": 10, "column": "age", "description": "Age stored as string 'thirty-five'"},
        {"id": "RCT-RC-01", "type": "range_violation", "row_hint": 20, "column": "bmi", "description": "Negative BMI (-3.2)"},
        {"id": "RCT-RC-02", "type": "range_violation", "row_hint": 30, "column": "baseline_sbp", "description": "SBP > 300 (320)"},
        {"id": "RCT-LC-01", "type": "logic_contradiction", "row_hint": 40, "column": "end_date", "description": "end_date before enroll_date"},
        {"id": "RCT-MD-01", "type": "missing_data", "row_hint": "50-55", "column": "followup_sbp", "description": "Bulk missing followup_sbp (6 rows)"},
        {"id": "RCT-DP-01", "type": "duplicate", "row_hint": "60-61", "column": "all", "description": "Duplicate data with different ID"},
        {"id": "RCT-EI-01", "type": "encoding_inconsistency", "row_hint": 70, "column": "sex", "description": "Inconsistent sex encoding 'male' vs 'M'"},
        {"id": "RCT-EO-01", "type": "extreme_outlier", "row_hint": 80, "column": "bmi", "description": "BMI = 99.9"},
        {"id": "RCT-FI-01", "type": "format_issue", "row_hint": 90, "column": "enroll_date", "description": "Date format MM/DD/YYYY vs YYYY-MM-DD"},
        {"id": "RCT-LC-02", "type": "logic_contradiction", "row_hint": 100, "column": "baseline_sbp/dbp", "description": "DBP > SBP"},
        {"id": "RCT-TC-02", "type": "type_error", "row_hint": 110, "column": "treatment", "description": "Treatment = '1' instead of Drug_A/Placebo"},
        {"id": "RCT-MD-02", "type": "missing_data", "row_hint": "MAR", "column": "followup_dbp", "description": "MAR pattern: dropout=1 has 80% missing followup"},
    ],
    "cohort": [
        {"id": "COH-TC-01", "type": "type_error", "row_hint": 5, "column": "age", "description": "Age as float 45.7"},
        {"id": "COH-RC-01", "type": "range_violation", "row_hint": 15, "column": "hba1c", "description": "HbA1c > 20% (25.3)"},
        {"id": "COH-RC-02", "type": "range_violation", "row_hint": 25, "column": "egfr", "description": "Negative eGFR (-5.0)"},
        {"id": "COH-EI-01", "type": "encoding_inconsistency", "row_hint": 35, "column": "sex", "description": "Sex as '1' instead of Male/Female"},
        {"id": "COH-EI-02", "type": "encoding_inconsistency", "row_hint": 45, "column": "smoking", "description": "Smoking as 'Y' instead of Never/Former/Current"},
        {"id": "COH-MD-01", "type": "missing_data", "row_hint": "55-62", "column": "cholesterol", "description": "Bulk missing cholesterol (8 rows)"},
        {"id": "COH-DP-01", "type": "duplicate", "row_hint": "70-71", "column": "all", "description": "Exact duplicate row"},
        {"id": "COH-EO-01", "type": "extreme_outlier", "row_hint": 80, "column": "cholesterol", "description": "Cholesterol = 35.0"},
        {"id": "COH-LC-01", "type": "logic_contradiction", "row_hint": 90, "column": "diabetes/hba1c", "description": "diabetes=0 but HbA1c=11.5"},
        {"id": "COH-FI-01", "type": "format_issue", "row_hint": 100, "column": "center", "description": "Center name lowercase 'beijing'"},
        {"id": "COH-FI-02", "type": "format_issue", "row_hint": 110, "column": "center", "description": "Center name with leading space ' Shanghai'"},
        {"id": "COH-RC-03", "type": "range_violation", "row_hint": 120, "column": "followup_months", "description": "followup_months = 0"},
        {"id": "COH-MD-02", "type": "missing_data", "row_hint": "MNAR", "column": "cholesterol", "description": "MNAR: outcome=1 has 30% more missing cholesterol"},
    ],
    "case_control": [
        {"id": "CC-TC-01", "type": "type_error", "row_hint": 5, "column": "case_status", "description": "case_status as 'Yes' instead of 1/0"},
        {"id": "CC-RC-01", "type": "range_violation", "row_hint": 15, "column": "bmi", "description": "BMI = 0"},
        {"id": "CC-RC-02", "type": "range_violation", "row_hint": 25, "column": "fasting_glucose", "description": "Fasting glucose < 1 (0.5)"},
        {"id": "CC-TC-02", "type": "type_error", "row_hint": 35, "column": "smoking_years", "description": "Negative smoking years (-5)"},
        {"id": "CC-EI-01", "type": "encoding_inconsistency", "row_hint": 45, "column": "sex", "description": "Sex as Chinese '男' instead of M/F"},
        {"id": "CC-MD-01", "type": "missing_data", "row_hint": "55-58", "column": "bmi", "description": "Bulk missing BMI (4 rows)"},
        {"id": "CC-DP-01", "type": "duplicate", "row_hint": "63-64", "column": "all", "description": "Duplicate data with different ID"},
        {"id": "CC-EO-01", "type": "extreme_outlier", "row_hint": 70, "column": "systolic_bp", "description": "SBP = 350"},
        {"id": "CC-LC-01", "type": "logic_contradiction", "row_hint": 80, "column": "age/smoking_years", "description": "smoking_years=30 but age=25"},
        {"id": "CC-FI-01", "type": "format_issue", "row_hint": 90, "column": "enrollment_date", "description": "Date format YYYY/MM/DD vs YYYY-MM-DD"},
        {"id": "CC-EI-02", "type": "encoding_inconsistency", "row_hint": 100, "column": "occupation", "description": "Occupation 'office worker' not in standard set"},
    ],
}


def write_dataset(columns, rows, filename):
    """Write dataset to CSV."""
    outpath = FIXTURES_DIR / filename
    with open(outpath, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        w.writerows(rows)
    return str(outpath)


def generate_all():
    """Generate all fixture datasets and return paths + issue registry."""
    results = {}

    # RCT
    cols, rows = generate_rct()
    path = write_dataset(cols, rows, "rct_dataset.csv")
    results["rct"] = {"path": path, "rows": len(rows), "issues": len(KNOWN_ISSUES["rct"])}

    # Cohort
    cols, rows = generate_cohort()
    path = write_dataset(cols, rows, "cohort_dataset.csv")
    results["cohort"] = {"path": path, "rows": len(rows), "issues": len(KNOWN_ISSUES["cohort"])}

    # Case-control
    cols, rows = generate_case_control()
    path = write_dataset(cols, rows, "case_control.csv")
    results["case_control"] = {"path": path, "rows": len(rows), "issues": len(KNOWN_ISSUES["case_control"])}

    return results


if __name__ == "__main__":
    results = generate_all()
    total_issues = 0
    for name, info in results.items():
        print(f"[{name}] {info['rows']} rows, {info['issues']} known issues -> {info['path']}")
        total_issues += info["issues"]
    print(f"\nTotal: {sum(r['rows'] for r in results.values())} rows, {total_issues} known issues")
    print(f"\nIssue types covered: type_error, range_violation, logic_contradiction, "
          f"missing_data, duplicate, format_issue, encoding_inconsistency, extreme_outlier")
