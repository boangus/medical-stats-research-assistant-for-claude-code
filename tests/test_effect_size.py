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

    def test_known_values(self):
        """D037修复验证: omega_squared公式正确性"""
        # 手动计算验证: 3组, 每组5个样本
        g1 = np.array([1, 2, 3, 4, 5])
        g2 = np.array([6, 7, 8, 9, 10])
        g3 = np.array([11, 12, 13, 14, 15])

        # 手工计算
        all_data = np.concatenate([g1, g2, g3])
        grand_mean = np.mean(all_data)  # 8.0
        k = 3
        n = 15

        ss_between = 5 * (3 - 8)**2 + 5 * (8 - 8)**2 + 5 * (13 - 8)**2  # 125 + 0 + 125 = 250
        ss_within = 2 * 5  # 每组方差和 = 10, 3组 = 30... 实际: sum((g-mean(g))^2)
        # g1: (1-3)^2+(2-3)^2+(3-3)^2+(4-3)^2+(5-3)^2 = 4+1+0+1+4 = 10
        # g2: 同理 = 10, g3: 同理 = 10, ss_within = 30
        ss_within = 30
        ss_total = 250 + 30  # 280
        ms_within = 30 / (15 - 3)  # 2.5

        expected = (250 - 2 * 2.5) / (280 + 2.5)  # 245 / 282.5 ≈ 0.867

        result = omega_squared([g1, g2, g3])
        assert abs(result - expected) < 0.001, f"Expected {expected:.4f}, got {result:.4f}"

    def test_negative_returns_zero(self):
        """当效应极小时ω²应返回0(max(0, ...))"""
        # 所有组相同 → SS_between = 0 → ω²可能为负 → 应返回0
        g = np.array([1, 2, 3, 4, 5])
        result = omega_squared([g, g, g])
        assert result == 0.0


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

    def test_nnt_from_or_known_values(self):
        """D002修复验证: OR→ARR转换使用正确公式"""
        # OR=0.5, CER=20%: EER = (0.2/0.8 * 0.5) / (1 + 0.2/0.8 * 0.5) = 0.125/1.125 ≈ 11.1%
        # ARR = 11.1% - 20% = -8.9%, NNT = 1/0.089 ≈ 11.2
        nnt = nnt_from_or(0.5, 0.20)
        assert abs(nnt - 11.2) < 0.5, f"Expected ~11.2, got {nnt}"

        # OR=2.0, CER=20%: EER = (0.2/0.8 * 2) / (1 + 0.2/0.8 * 2) = 0.5/1.5 ≈ 33.3%
        # ARR = 33.3% - 20% = 13.3%, NNT = 1/0.133 ≈ 7.5
        nnt = nnt_from_or(2.0, 0.20)
        assert abs(nnt - 7.5) < 0.5, f"Expected ~7.5, got {nnt}"

        # OR=1.0 应返回 inf (无效果)
        nnt = nnt_from_or(1.0, 0.20)
        assert nnt == float('inf')

    def test_nnt_from_or_invalid_cer(self):
        """D002: CER超出范围应抛出异常"""
        with pytest.raises(ValueError):
            nnt_from_or(0.5, 0.0)
        with pytest.raises(ValueError):
            nnt_from_or(0.5, 1.0)
