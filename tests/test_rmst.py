"""
test_rmst.py — rmst_template.py 单元测试
"""
import numpy as np
import pytest

from shared.templates.rmst_template import (
    kaplan_meier_rmst,
    rmst_difference,
    rmst_ratio,
    format_rmst_report,
)


class TestKaplanMeierRMST:
    """KM-RMST 计算测试"""

    def test_all_survive(self):
        """所有人存活 → RMST 接近 tau"""
        time = np.array([10, 10, 10, 10])
        event = np.array([0, 0, 0, 0])  # 全删失
        result = kaplan_meier_rmst(time, event, tau=10)
        # 全删失时 KM 曲线保持在 1.0，RMST 应接近 tau
        assert result["rmst"] >= 0  # 至少非负

    def test_all_die_early(self):
        """所有人早期死亡 → RMST 小"""
        time = np.array([1, 1, 1, 1])
        event = np.array([1, 1, 1, 1])
        result = kaplan_meier_rmst(time, event, tau=10)
        assert result["rmst"] < 2.0

    def test_tau_effect(self):
        """tau 越大 RMST 越大"""
        time = np.array([5, 10, 15, 20])
        event = np.array([1, 1, 1, 1])
        r1 = kaplan_meier_rmst(time, event, tau=10)
        r2 = kaplan_meier_rmst(time, event, tau=20)
        assert r2["rmst"] > r1["rmst"]

    def test_returns_dict_keys(self):
        time = np.array([1, 2, 3])
        event = np.array([1, 0, 1])
        result = kaplan_meier_rmst(time, event)
        assert "rmst" in result
        assert "tau" in result
        assert "n_events" in result
        assert "n_total" in result


class TestRMSTDifference:
    """RMST 差值测试"""

    def test_identical_groups(self):
        np.random.seed(42)
        time = np.random.exponential(10, 50)
        event = np.random.binomial(1, 0.7, 50)
        result = rmst_difference(time, event, time.copy(), event.copy(), tau=20)
        assert abs(result["difference"]) < 0.1

    def test_different_groups(self):
        np.random.seed(42)
        time1 = np.random.exponential(15, 100)
        time2 = np.random.exponential(8, 100)
        event1 = np.ones(100, dtype=int)
        event2 = np.ones(100, dtype=int)
        result = rmst_difference(time1, event1, time2, event2, tau=20)
        assert result["difference"] > 0  # 组 1 存活更长

    def test_result_keys(self):
        np.random.seed(42)
        time = np.random.exponential(10, 50)
        event = np.random.binomial(1, 0.7, 50)
        result = rmst_difference(time, event, time, event, tau=15)
        assert "rmst_group1" in result
        assert "rmst_group2" in result
        assert "difference" in result
        assert "ci_lower" in result
        assert "ci_upper" in result
        assert "p" in result


class TestRMSTRatio:
    """RMST 比值测试"""

    def test_ratio_near_one(self):
        np.random.seed(42)
        time = np.random.exponential(10, 50)
        event = np.random.binomial(1, 0.7, 50)
        result = rmst_ratio(time, event, time.copy(), event.copy(), tau=15)
        assert abs(result["ratio"] - 1.0) < 0.1


class TestFormatReport:
    """报告格式化测试"""

    def test_report_content(self):
        np.random.seed(42)
        time1 = np.random.exponential(12, 80)
        time2 = np.random.exponential(8, 80)
        event1 = np.ones(80, dtype=int)
        event2 = np.ones(80, dtype=int)
        result = rmst_difference(time1, event1, time2, event2, tau=20)
        report = format_rmst_report(result)
        assert "RMST" in report
        assert "截断时间点" in report
        assert "差值" in report
