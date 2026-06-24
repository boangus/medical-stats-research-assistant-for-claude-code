"""
Tests for AnomalyDetector, DetectionResult, MultivariateDetector, and TrendDetector.
"""

import time
import numpy as np
import pytest
from msra_modules.realtime_analytics.anomaly_detector import (
    AnomalyDetector,
    AlertRule,
    AlertLevel,
    Alert,
    TrendDetector,
    DetectionResult,
    MultivariateDetector,
)


class TestAlertRule:
    """AlertRule 测试"""

    def test_gt_condition(self):
        """测试 gt 条件"""
        rule = AlertRule(name="test", metric="hr", condition="gt", threshold=100)
        assert rule.evaluate(101.0) is True
        assert rule.evaluate(100.0) is False
        assert rule.evaluate(99.0) is False

    def test_lt_condition(self):
        """测试 lt 条件"""
        rule = AlertRule(name="test", metric="hr", condition="lt", threshold=60)
        assert rule.evaluate(59.0) is True
        assert rule.evaluate(60.0) is False
        assert rule.evaluate(61.0) is False

    def test_range_condition(self):
        """测试 range 条件"""
        rule = AlertRule(
            name="test", metric="hr", condition="range",
            threshold=60, threshold_max=100,
        )
        assert rule.evaluate(50.0) is True  # 低于下限
        assert rule.evaluate(110.0) is True  # 高于上限
        assert rule.evaluate(75.0) is False  # 在范围内

    def test_range_no_max(self):
        """测试 range 条件无上限"""
        rule = AlertRule(name="test", metric="hr", condition="range", threshold=60)
        assert rule.evaluate(50.0) is False

    def test_invalid_condition(self):
        """测试无效条件"""
        rule = AlertRule(name="test", metric="hr", condition="invalid", threshold=60)
        assert rule.evaluate(75.0) is False


class TestAnomalyDetector:
    """AnomalyDetector 测试"""

    def test_add_rule(self):
        """测试添加规则"""
        detector = AnomalyDetector()
        rule = AlertRule(name="test", metric="hr", condition="gt", threshold=100)
        detector.add_rule(rule)
        assert len(detector.get_rules()) == 1

    def test_add_default_rules(self):
        """测试添加默认生命体征规则"""
        detector = AnomalyDetector()
        detector.add_default_vital_signs_rules()
        assert len(detector.get_rules()) == 8

    def test_evaluate_triggers_alert(self):
        """测试评估触发告警"""
        detector = AnomalyDetector()
        rule = AlertRule(
            name="tachycardia", metric="heart_rate",
            condition="gt", threshold=150, level=AlertLevel.CRITICAL,
        )
        detector.add_rule(rule)
        alerts = detector.evaluate("heart_rate", 160.0, timestamp=1000.0)
        assert len(alerts) == 1
        assert alerts[0].rule_name == "tachycardia"
        assert alerts[0].level == AlertLevel.CRITICAL

    def test_evaluate_no_trigger(self):
        """测试评估不触发告警"""
        detector = AnomalyDetector()
        rule = AlertRule(name="tachycardia", metric="heart_rate", condition="gt", threshold=150)
        detector.add_rule(rule)
        alerts = detector.evaluate("heart_rate", 120.0, timestamp=1000.0)
        assert len(alerts) == 0

    def test_cooldown_prevents_duplicate(self):
        """测试冷却时间防止重复告警"""
        detector = AnomalyDetector()
        rule = AlertRule(
            name="tachy", metric="hr", condition="gt", threshold=150,
            cooldown_seconds=300,
        )
        detector.add_rule(rule)
        alerts1 = detector.evaluate("hr", 160.0, timestamp=1000.0)
        assert len(alerts1) == 1
        # 冷却期内不触发
        alerts2 = detector.evaluate("hr", 160.0, timestamp=1100.0)
        assert len(alerts2) == 0

    def test_cooldown_expires(self):
        """测试冷却期过后重新触发"""
        detector = AnomalyDetector()
        rule = AlertRule(
            name="tachy", metric="hr", condition="gt", threshold=150,
            cooldown_seconds=300,
        )
        detector.add_rule(rule)
        detector.evaluate("hr", 160.0, timestamp=1000.0)
        # 冷却期过后
        alerts = detector.evaluate("hr", 160.0, timestamp=1400.0)
        assert len(alerts) == 1

    def test_sustained_violation(self):
        """测试持续违规"""
        detector = AnomalyDetector()
        rule = AlertRule(
            name="sustained_tachy", metric="hr", condition="gt", threshold=150,
            sustained_seconds=5,
        )
        detector.add_rule(rule)
        # 第一次违规不触发（开始计时）
        alerts = detector.evaluate("hr", 160.0, timestamp=1000.0)
        assert len(alerts) == 0
        # 持续时间不足
        alerts = detector.evaluate("hr", 160.0, timestamp=1003.0)
        assert len(alerts) == 0
        # 持续时间满足
        alerts = detector.evaluate("hr", 160.0, timestamp=1006.0)
        assert len(alerts) == 1

    def test_alert_handler_called(self):
        """测试告警处理器被调用"""
        detector = AnomalyDetector()
        rule = AlertRule(name="tachy", metric="hr", condition="gt", threshold=150)
        detector.add_rule(rule)
        received = []
        detector.add_alert_handler(lambda a: received.append(a))
        detector.evaluate("hr", 160.0, timestamp=1000.0)
        assert len(received) == 1


class TestDetectionResult:
    """DetectionResult 测试"""

    def test_creation(self):
        """测试创建 DetectionResult"""
        result = DetectionResult(
            index=0, is_anomaly=True, score=-0.5,
            features={"hr": 160.0}, method="isolation_forest",
        )
        assert result.index == 0
        assert result.is_anomaly is True
        assert result.score == -0.5

    def test_to_dict(self):
        """测试转换为字典"""
        result = DetectionResult(
            index=0, is_anomaly=False, score=0.3,
            features={"hr": 75.0}, method="test", timestamp=1000.0,
        )
        d = result.to_dict()
        assert d["index"] == 0
        assert d["is_anomaly"] is False
        assert d["timestamp"] == 1000.0


class TestMultivariateDetector:
    """MultivariateDetector 测试"""

    def test_fit_and_detect(self):
        """测试训练和检测"""
        np.random.seed(42)
        normal_data = np.random.randn(100, 3)
        # 添加异常点
        anomaly = np.array([[10, 10, 10]])
        data = np.vstack([normal_data, anomaly])

        detector = MultivariateDetector(contamination=0.05)
        results = detector.detect(data, feature_names=["hr", "spo2", "bp"])

        assert len(results) == 101
        # 最后一个点应该是异常
        assert results[-1].is_anomaly == True

    def test_auto_fit(self):
        """测试自动训练"""
        data = np.random.randn(50, 2)
        detector = MultivariateDetector()
        results = detector.detect(data)
        assert len(results) == 50

    def test_reset(self):
        """测试重置"""
        data = np.random.randn(50, 2)
        detector = MultivariateDetector()
        detector.detect(data)
        assert detector._is_fitted is True
        detector.reset()
        assert detector._is_fitted is False

    def test_with_timestamps(self):
        """测试带时间戳"""
        data = np.random.randn(20, 2)
        timestamps = [1000.0 + i for i in range(20)]
        detector = MultivariateDetector()
        results = detector.detect(data, timestamps=timestamps)
        assert results[0].timestamp == 1000.0

    def test_1d_data(self):
        """测试一维数据自动 reshape"""
        data = np.random.randn(30)
        detector = MultivariateDetector()
        results = detector.detect(data)
        assert len(results) == 30


class TestTrendDetector:
    """TrendDetector 测试"""

    def test_calibrating_phase(self):
        """测试校准阶段"""
        td = TrendDetector(window_size=10)
        for i in range(5):
            result = td.update(75.0)
            assert result["status"] == "calibrating"

    def test_monitoring_phase(self):
        """测试监控阶段"""
        td = TrendDetector(window_size=5)
        for i in range(6):
            result = td.update(75.0 + np.random.normal(0, 1))
        assert result["status"] == "monitoring"

    def test_detect_increasing_trend(self):
        """测试检测上升趋势"""
        td = TrendDetector(window_size=20, cusum_threshold=2.0)
        # 建立基线（有少量噪声使 std > 0）
        np.random.seed(42)
        for i in range(20):
            td.update(75.0 + np.random.normal(0, 1))
        # 持续上升
        for i in range(30):
            result = td.update(85.0)
        assert result["trend_detected"] is True
        assert result["trend_direction"] == "increasing"

    def test_detect_decreasing_trend(self):
        """测试检测下降趋势"""
        td = TrendDetector(window_size=20, cusum_threshold=2.0)
        # 建立基线（有少量噪声使 std > 0）
        np.random.seed(42)
        for i in range(20):
            td.update(75.0 + np.random.normal(0, 1))
        # 持续下降
        for i in range(30):
            result = td.update(65.0)
        assert result["trend_detected"] is True
        assert result["trend_direction"] == "decreasing"

    def test_reset(self):
        """测试重置"""
        td = TrendDetector(window_size=5)
        for i in range(10):
            td.update(75.0)
        td.reset()
        result = td.update(75.0)
        assert result["status"] == "calibrating"
