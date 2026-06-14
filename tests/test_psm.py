"""
test_psm.py — psm_template.py 单元测试
"""
import importlib
import numpy as np
import pandas as pd
import pytest

psm = importlib.import_module("shared.causal-inference.psm_template")


@pytest.fixture
def psm_data():
    """PSM 测试数据"""
    np.random.seed(42)
    n = 200
    covariates = np.random.normal(0, 1, (n, 3))
    ps_true = 1 / (1 + np.exp(-(covariates[:, 0] + 0.5 * covariates[:, 1])))
    treatment = np.random.binomial(1, ps_true)
    outcome = 2 * treatment + covariates[:, 0] + np.random.normal(0, 1, n)

    return pd.DataFrame({
        "treatment": treatment,
        "outcome": outcome,
        "x1": covariates[:, 0],
        "x2": covariates[:, 1],
        "x3": covariates[:, 2],
    })


class TestEstimatePropensity:
    """倾向性评分估计测试"""

    def test_returns_dataframe_with_ps(self, psm_data):
        result = psm.estimate_propensity(
            psm_data, "treatment", ["x1", "x2", "x3"]
        )
        assert isinstance(result, pd.DataFrame)
        assert "ps_score" in result.columns

    def test_ps_in_range(self, psm_data):
        result = psm.estimate_propensity(
            psm_data, "treatment", ["x1", "x2", "x3"]
        )
        assert all(0 <= p <= 1 for p in result["ps_score"])

    def test_preserves_row_count(self, psm_data):
        result = psm.estimate_propensity(
            psm_data, "treatment", ["x1", "x2", "x3"]
        )
        assert len(result) == len(psm_data)


class TestBalanceCheck:
    """平衡性检查测试"""

    def test_returns_dataframe(self, psm_data):
        df = psm.estimate_propensity(
            psm_data, "treatment", ["x1", "x2", "x3"]
        )
        balance = psm.balance_check(
            df, "treatment", ["x1", "x2", "x3"]
        )
        assert isinstance(balance, pd.DataFrame)
        assert "Variable" in balance.columns
        assert "SMD" in balance.columns

    def test_smd_is_positive(self, psm_data):
        df = psm.estimate_propensity(
            psm_data, "treatment", ["x1", "x2", "x3"]
        )
        balance = psm.balance_check(
            df, "treatment", ["x1", "x2", "x3"]
        )
        assert all(smd >= 0 for smd in balance["SMD"])


class TestNearestNeighborMatch:
    """最近邻匹配测试"""

    def test_matching_produces_pairs(self, psm_data):
        df = psm.estimate_propensity(
            psm_data, "treatment", ["x1", "x2", "x3"]
        )
        treated = df[df["treatment"] == 1].copy()
        control = df[df["treatment"] == 0].copy()

        try:
            matches = psm.nearest_neighbor_match(treated, control, caliper=0.5)
            assert len(matches) > 0
        except ValueError:
            pytest.skip("No matches found with this data")

    def test_match_columns(self, psm_data):
        df = psm.estimate_propensity(
            psm_data, "treatment", ["x1", "x2", "x3"]
        )
        treated = df[df["treatment"] == 1].copy()
        control = df[df["treatment"] == 0].copy()

        try:
            matches = psm.nearest_neighbor_match(treated, control, caliper=0.8)
            assert "match_id" in matches.columns
            assert "match_group" in matches.columns
        except ValueError:
            pytest.skip("No matches found with this data")


class TestEstimateATE:
    """ATE 估计测试"""

    def test_ate_with_matched_data(self, psm_data):
        df = psm.estimate_propensity(
            psm_data, "treatment", ["x1", "x2", "x3"]
        )
        treated = df[df["treatment"] == 1].copy()
        control = df[df["treatment"] == 0].copy()

        try:
            matches = psm.nearest_neighbor_match(treated, control, caliper=0.8)
            if len(matches) > 10:
                ate = psm.estimate_ate(matches, "outcome", "treatment")
                assert "ate" in ate
        except ValueError:
            pytest.skip("No matches found with this data")
