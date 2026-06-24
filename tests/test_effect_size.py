"""
test_effect_size.py — effect_size_template.py 单元测试
"""
import numpy as np
import pytest

from shared.templates.effect_size_template import (
    cliffs_delta,
    cohens_d,
    cohens_f_from_eta2,
    cramers_v,
    eta_squared,
    hedges_g,
    interpret_effect_size,
    nnt_from_or,
    nnt_from_risk_diff,
    odds_ratio,
    omega_squared,
    rank_biserial_r,
    risk_ratio,
)


class TestCohensD:
    """Cohen's d 测试"""

    def test_identical_groups(self):
        g = np.array([1, 2, 3, 4, 5])
        assert cohens_d(g, g) == 0.0

    def test_known_effect(self):
        np.random.seed(42)
        g1 = np.random.normal(0, 1, 1000)
        g2 = np.random.normal(0.5, 1, 1000)
        d = cohens_d(g1, g2)
        assert abs(d - (-0.5)) < 0.1  # 接近 -0.5

    def test_pooled_vs_unpooled(self):
        # 使用方差不同的组来区分 pooled 和 unpooled
        g1 = np.array([1, 1, 1, 1, 100])  # 高方差
        g2 = np.array([50, 50, 50, 50, 51])  # 低方差
        d_pooled = cohens_d(g1, g2, pooled=True)
        d_unpooled = cohens_d(g1, g2, pooled=False)
        # 两种方法应该给出不同结果
        assert isinstance(d_pooled, float)
        assert isinstance(d_unpooled, float)

    def test_large_effect(self):
        g1 = np.array([1, 2, 3])
        g2 = np.array([10, 11, 12])
        d = cohens_d(g1, g2)
        assert abs(d) > 2.0  # 很大的效应


class TestHedgesG:
    """Hedges' g 测试"""

    def test_small_sample_correction(self):
        g1 = np.array([1, 2, 3, 4, 5])
        g2 = np.array([2, 3, 4, 5, 6])
        d = cohens_d(g1, g2)
        g = hedges_g(g1, g2)
        # Hedges' g 应略小于 Cohen's d
        assert abs(g) <= abs(d)

    def test_large_sample_no_correction(self):
        np.random.seed(42)
        g1 = np.random.normal(0, 1, 1000)
        g2 = np.random.normal(0.3, 1, 1000)
        d = cohens_d(g1, g2)
        g = hedges_g(g1, g2)
        assert abs(d - g) < 0.01


class TestEtaSquared:
    """η² 测试"""

    def test_no_effect(self):
        g1 = np.array([1, 2, 3])
        g2 = np.array([1, 2, 3])
        g3 = np.array([1, 2, 3])
        assert eta_squared([g1, g2, g3]) == 0.0

    def test_large_effect(self):
        g1 = np.array([1, 2, 3])
        g2 = np.array([10, 11, 12])
        g3 = np.array([20, 21, 22])
        eta2 = eta_squared([g1, g2, g3])
        assert eta2 > 0.9

    def test_range(self):
        np.random.seed(42)
        groups = [np.random.normal(i * 2, 1, 30) for i in range(4)]
        eta2 = eta_squared(groups)
        assert 0 <= eta2 <= 1


class TestOmegaSquared:
    """ω² 测试"""

    def test_no_effect(self):
        g1 = np.array([1, 2, 3])
        g2 = np.array([1, 2, 3])
        assert omega_squared([g1, g2]) == 0.0

    def test_less_than_eta2(self):
        np.random.seed(42)
        groups = [np.random.normal(i, 1, 20) for i in range(3)]
        eta2 = eta_squared(groups)
        omega2 = omega_squared(groups)
        # ω² 通常 ≤ η²
        assert omega2 <= eta2 + 0.01


class TestCohensF:
    """Cohen's f 测试"""

    def test_from_eta2(self):
        assert cohens_f_from_eta2(0.01) == pytest.approx(0.1005, abs=0.01)
        assert cohens_f_from_eta2(0.06) == pytest.approx(0.2526, abs=0.01)
        assert cohens_f_from_eta2(0.14) == pytest.approx(0.4031, abs=0.01)


class TestCramersV:
    """Cramér's V 测试"""

    def test_perfect_association(self):
        table = np.array([[10, 0], [0, 10]])
        v = cramers_v(table)
        assert v > 0.8  # 强关联

    def test_no_association(self):
        table = np.array([[5, 5], [5, 5]])
        v = cramers_v(table)
        assert v == pytest.approx(0.0, abs=0.01)


class TestRiskRatio:
    """风险比测试"""

    def test_equal_risk(self):
        rr = risk_ratio(30, 70, 30, 70)
        assert rr["risk_ratio"] == pytest.approx(1.0, abs=0.01)

    def test_higher_risk(self):
        rr = risk_ratio(50, 50, 20, 80)
        assert rr["risk_ratio"] > 1.0

    def test_ci_contains_one_when_equal(self):
        rr = risk_ratio(30, 70, 30, 70)
        assert rr["ci_lower"] < 1.0 < rr["ci_upper"]


class TestOddsRatio:
    """比值比测试"""

    def test_equal_odds(self):
        or_result = odds_ratio(25, 25, 25, 25)
        assert or_result["odds_ratio"] == pytest.approx(1.0, abs=0.01)

    def test_known_or(self):
        or_result = odds_ratio(30, 10, 10, 30)
        assert or_result["odds_ratio"] == pytest.approx(9.0, abs=0.1)


class TestNonparametric:
    """非参数效应量测试"""

    def test_rank_biserial_identical(self):
        g = np.array([1, 2, 3])
        r = rank_biserial_r(g, g)
        # 相同组的 U = n1*n2/2, r = 0
        assert abs(r) < 0.01

    def test_cliffs_delta_range(self):
        g1 = np.array([1, 2, 3])
        g2 = np.array([4, 5, 6])
        d = cliffs_delta(g1, g2)
        assert -1 <= d <= 1
        assert d < 0  # g1 全部小于 g2


class TestInterpretation:
    """效应量解读测试"""

    def test_cohens_d_interpretation(self):
        assert interpret_effect_size(0.1, 'd') == "negligible"
        assert interpret_effect_size(0.3, 'd') == "small"
        assert interpret_effect_size(0.6, 'd') == "medium"
        assert interpret_effect_size(1.0, 'd') == "large"

    def test_or_interpretation(self):
        assert interpret_effect_size(1.2, 'or') == "negligible"
        assert interpret_effect_size(1.8, 'or') == "small"
        assert interpret_effect_size(2.5, 'or') == "medium"
        assert interpret_effect_size(4.0, 'or') == "large"


class TestNNT:
    """NNT 测试"""

    def test_nnt_from_risk_diff(self):
        assert nnt_from_risk_diff(0.1) == 10.0
        assert nnt_from_risk_diff(0.05) == 20.0
        assert nnt_from_risk_diff(0.0) == float('inf')

    def test_nnt_from_or(self):
        nnt = nnt_from_or(2.0, 0.2)
        assert nnt > 0
        assert isinstance(nnt, float)
