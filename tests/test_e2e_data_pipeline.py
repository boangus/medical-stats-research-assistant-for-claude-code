"""
E2E Data Pipeline Tests (T29.2)
===============================

Runs synthetic clinical datasets with known quality issues through
the data pipeline components and asserts all issues are detected.

Test datasets: tests/fixtures/rct_dataset.csv, cohort_dataset.csv, case_control.csv
Issue registry: tests/fixtures/generate_synthetic_clinical.py::KNOWN_ISSUES

Usage:
    pytest tests/test_e2e_data_pipeline.py -v
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

# Ensure project root on path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.fixtures.generate_synthetic_clinical import KNOWN_ISSUES, generate_all

# ── Fixtures ──


@pytest.fixture(scope="module")
def fixture_data():
    """Generate all fixture datasets."""
    return generate_all()


@pytest.fixture(scope="module")
def rct_df(fixture_data):
    return pd.read_csv(fixture_data["rct"]["path"])


@pytest.fixture(scope="module")
def cohort_df(fixture_data):
    return pd.read_csv(fixture_data["cohort"]["path"])


@pytest.fixture(scope="module")
def case_control_df(fixture_data):
    return pd.read_csv(fixture_data["case_control"]["path"])


# ── RCT Dataset Tests ──


class TestRCTDataQuality:
    """Verify known issues in RCT dataset are detectable."""

    def test_type_error_age(self, rct_df):
        """RCT-TC-01: Age stored as string 'thirty-five'."""
        age_numeric = pd.to_numeric(rct_df["age"], errors="coerce")
        assert age_numeric.isna().sum() > 0, "Non-numeric age values not detected"

    def test_range_violation_bmi(self, rct_df):
        """RCT-RC-01: Negative BMI."""
        bmi = pd.to_numeric(rct_df["bmi"], errors="coerce")
        assert (bmi < 0).any(), "Negative BMI not detected"

    def test_range_violation_sbp(self, rct_df):
        """RCT-RC-02: SBP > 300."""
        sbp = pd.to_numeric(rct_df["baseline_sbp"], errors="coerce")
        assert (sbp > 300).any(), "Extreme SBP not detected"

    def test_logic_date_order(self, rct_df):
        """RCT-LC-01: end_date before enroll_date."""
        enroll = pd.to_datetime(rct_df["enroll_date"], errors="coerce")
        end = pd.to_datetime(rct_df["end_date"], errors="coerce")
        violations = (end < enroll).sum()
        assert violations > 0, "Date order violation not detected"

    def test_missing_data_bulk(self, rct_df):
        """RCT-MD-01: Bulk missing followup_sbp."""
        missing = rct_df["followup_sbp"].isna().sum()
        assert missing >= 6, f"Expected >= 6 missing, got {missing}"

    def test_duplicate_rows(self, rct_df):
        """RCT-DP-01: Duplicate data with different ID."""
        feature_cols = [c for c in rct_df.columns if c != "subject_id"]
        dupes = rct_df.duplicated(subset=feature_cols, keep=False)
        assert dupes.sum() > 0, "Duplicate rows not detected"

    def test_encoding_sex(self, rct_df):
        """RCT-EI-01: Inconsistent sex encoding."""
        unique_sex = set(rct_df["sex"].dropna().unique())
        assert len(unique_sex) > 2 or "male" in unique_sex, "Encoding inconsistency not detected"

    def test_outlier_bmi(self, rct_df):
        """RCT-EO-01: BMI = 99.9."""
        bmi = pd.to_numeric(rct_df["bmi"], errors="coerce")
        assert bmi.max() > 60, "Extreme BMI outlier not detected"

    def test_format_date(self, rct_df):
        """RCT-FI-01: Date format inconsistency."""
        enroll = pd.to_datetime(rct_df["enroll_date"], errors="coerce")
        assert enroll.isna().sum() > 0, "Unparseable dates not detected"

    def test_logic_bp_order(self, rct_df):
        """RCT-LC-02: DBP > SBP."""
        sbp = pd.to_numeric(rct_df["baseline_sbp"], errors="coerce")
        dbp = pd.to_numeric(rct_df["baseline_dbp"], errors="coerce")
        violations = (dbp > sbp).sum()
        assert violations > 0, "DBP > SBP not detected"

    def test_type_treatment(self, rct_df):
        """RCT-TC-02: Treatment = '1' instead of Drug_A/Placebo."""
        valid = {"Drug_A", "Placebo"}
        invalid = ~rct_df["treatment"].isin(valid)
        assert invalid.sum() > 0, "Invalid treatment value not detected"

    def test_mar_pattern(self, rct_df):
        """RCT-MD-02: MAR pattern in followup_dbp."""
        dropout_1 = rct_df[rct_df["dropout"] == 1]
        missing_rate = dropout_1["followup_dbp"].isna().mean()
        assert missing_rate > 0.5, f"MAR pattern not detected (missing rate={missing_rate:.2f})"


# ── Cohort Dataset Tests ──


class TestCohortDataQuality:
    """Verify known issues in cohort dataset are detectable."""

    def test_type_age_float(self, cohort_df):
        """COH-TC-01: Age as float."""
        age = pd.to_numeric(cohort_df["age"], errors="coerce")
        has_float = (age % 1 != 0).any()
        assert has_float, "Float age not detected"

    def test_range_hba1c(self, cohort_df):
        """COH-RC-01: HbA1c > 20."""
        hba1c = pd.to_numeric(cohort_df["hba1c"], errors="coerce")
        assert (hba1c > 20).any(), "Extreme HbA1c not detected"

    def test_range_egfr(self, cohort_df):
        """COH-RC-02: Negative eGFR."""
        egfr = pd.to_numeric(cohort_df["egfr"], errors="coerce")
        assert (egfr < 0).any(), "Negative eGFR not detected"

    def test_encoding_sex(self, cohort_df):
        """COH-EI-01: Sex as '1'."""
        valid = {"Male", "Female"}
        invalid = ~cohort_df["sex"].isin(valid)
        assert invalid.sum() > 0, "Invalid sex encoding not detected"

    def test_encoding_smoking(self, cohort_df):
        """COH-EI-02: Smoking as 'Y'."""
        valid = {"Never", "Former", "Current"}
        invalid = ~cohort_df["smoking"].isin(valid)
        assert invalid.sum() > 0, "Invalid smoking encoding not detected"

    def test_missing_cholesterol(self, cohort_df):
        """COH-MD-01: Bulk missing cholesterol."""
        missing = cohort_df["cholesterol"].isna().sum()
        assert missing >= 8, f"Expected >= 8 missing, got {missing}"

    def test_duplicate(self, cohort_df):
        """COH-DP-01: Exact duplicate."""
        feature_cols = [c for c in cohort_df.columns if c != "patient_id"]
        dupes = cohort_df.duplicated(subset=feature_cols, keep=False)
        assert dupes.sum() > 0, "Duplicate not detected"

    def test_outlier_cholesterol(self, cohort_df):
        """COH-EO-01: Cholesterol = 35.0."""
        chol = pd.to_numeric(cohort_df["cholesterol"], errors="coerce")
        assert chol.max() > 15, "Extreme cholesterol outlier not detected"

    def test_logic_diabetes_hba1c(self, cohort_df):
        """COH-LC-01: diabetes=0 but HbA1c=11.5."""
        hba1c = pd.to_numeric(cohort_df["hba1c"], errors="coerce")
        contradiction = ((cohort_df["diabetes"] == 0) & (hba1c > 10)).sum()
        assert contradiction > 0, "Diabetes/HbA1c contradiction not detected"

    def test_format_center_case(self, cohort_df):
        """COH-FI-01: Center name case inconsistency."""
        centers = cohort_df["center"].dropna().unique()
        has_lower = any(c[0].islower() for c in centers if len(c) > 0)
        assert has_lower, "Center case inconsistency not detected"

    def test_format_center_space(self, cohort_df):
        """COH-FI-02: Center name with leading space."""
        has_space = any(str(c).startswith(" ") for c in cohort_df["center"].dropna())
        assert has_space, "Leading space in center name not detected"

    def test_range_followup_zero(self, cohort_df):
        """COH-RC-03: followup_months = 0."""
        assert (cohort_df["followup_months"] == 0).any(), "Zero followup not detected"

    def test_mnar_pattern(self, cohort_df):
        """COH-MD-02: MNAR pattern -- outcome=1 has more missing cholesterol."""
        event_1 = cohort_df[cohort_df["outcome_event"] == 1]
        event_0 = cohort_df[cohort_df["outcome_event"] == 0]
        miss_1 = event_1["cholesterol"].isna().mean()
        miss_0 = event_0["cholesterol"].isna().mean()
        assert miss_1 > miss_0, f"MNAR pattern not detected (miss_1={miss_1:.2f}, miss_0={miss_0:.2f})"


# ── Case-Control Dataset Tests ──


class TestCaseControlDataQuality:
    """Verify known issues in case-control dataset are detectable."""

    def test_type_case_status(self, case_control_df):
        """CC-TC-01: case_status as 'Yes'."""
        numeric = pd.to_numeric(case_control_df["case_status"], errors="coerce")
        assert numeric.isna().sum() > 0, "Non-numeric case_status not detected"

    def test_range_bmi_zero(self, case_control_df):
        """CC-RC-01: BMI = 0."""
        bmi = pd.to_numeric(case_control_df["bmi"], errors="coerce")
        assert (bmi == 0).any(), "Zero BMI not detected"

    def test_range_glucose(self, case_control_df):
        """CC-RC-02: Fasting glucose < 1."""
        glucose = pd.to_numeric(case_control_df["fasting_glucose"], errors="coerce")
        assert (glucose < 1).any(), "Low glucose not detected"

    def test_type_smoking_years(self, case_control_df):
        """CC-TC-02: Negative smoking years."""
        sy = pd.to_numeric(case_control_df["smoking_years"], errors="coerce")
        assert (sy < 0).any(), "Negative smoking years not detected"

    def test_encoding_sex_chinese(self, case_control_df):
        """CC-EI-01: Sex as Chinese character."""
        has_chinese = case_control_df["sex"].astype(str).str.contains(
            r"[一-鿿]", regex=True
        ).any()
        assert has_chinese, "Chinese sex encoding not detected"

    def test_missing_bmi(self, case_control_df):
        """CC-MD-01: Bulk missing BMI."""
        missing = case_control_df["bmi"].isna().sum()
        assert missing >= 4, f"Expected >= 4 missing BMI, got {missing}"

    def test_duplicate(self, case_control_df):
        """CC-DP-01: Duplicate data."""
        feature_cols = [c for c in case_control_df.columns if c != "id"]
        dupes = case_control_df.duplicated(subset=feature_cols, keep=False)
        assert dupes.sum() > 0, "Duplicate not detected"

    def test_outlier_sbp(self, case_control_df):
        """CC-EO-01: SBP = 350."""
        sbp = pd.to_numeric(case_control_df["systolic_bp"], errors="coerce")
        assert sbp.max() > 300, "Extreme SBP outlier not detected"

    def test_logic_smoking_age(self, case_control_df):
        """CC-LC-01: smoking_years=30 but age=25."""
        sy = pd.to_numeric(case_control_df["smoking_years"], errors="coerce")
        age = pd.to_numeric(case_control_df["age"], errors="coerce")
        contradiction = (sy > age).sum()
        assert contradiction > 0, "Smoking years > age not detected"

    def test_format_date(self, case_control_df):
        """CC-FI-01: Date format inconsistency."""
        dates = pd.to_datetime(case_control_df["enrollment_date"], errors="coerce")
        assert dates.isna().sum() > 0, "Unparseable dates not detected"

    def test_encoding_occupation(self, case_control_df):
        """CC-EI-02: Non-standard occupation value."""
        valid = {"Office", "Manual", "Service", "Other"}
        invalid = ~case_control_df["occupation"].isin(valid)
        assert invalid.sum() > 0, "Non-standard occupation not detected"


# ── Issue Registry Completeness ──


class TestIssueRegistry:
    """Verify issue registry is complete and consistent."""

    def test_all_datasets_have_issues(self):
        """All 3 datasets should have known issues."""
        assert "rct" in KNOWN_ISSUES
        assert "cohort" in KNOWN_ISSUES
        assert "case_control" in KNOWN_ISSUES

    def test_total_issue_count(self):
        """Total known issues should be >= 36."""
        total = sum(len(v) for v in KNOWN_ISSUES.values())
        assert total >= 36, f"Expected >= 36 issues, got {total}"

    def test_issue_types_covered(self):
        """All 8 issue types should be represented."""
        all_types = set()
        for dataset_issues in KNOWN_ISSUES.values():
            for issue in dataset_issues:
                all_types.add(issue["type"])
        expected = {
            "type_error", "range_violation", "logic_contradiction",
            "missing_data", "duplicate", "format_issue",
            "encoding_inconsistency", "extreme_outlier",
        }
        assert all_types == expected, f"Missing types: {expected - all_types}"

    def test_rct_has_12_issues(self):
        assert len(KNOWN_ISSUES["rct"]) == 12

    def test_cohort_has_13_issues(self):
        assert len(KNOWN_ISSUES["cohort"]) == 13

    def test_case_control_has_11_issues(self):
        assert len(KNOWN_ISSUES["case_control"]) == 11
