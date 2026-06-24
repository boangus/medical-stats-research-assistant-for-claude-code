"""
Tests for RealtimeQualityGateChecker (Gate RT-1).
"""

import time
import numpy as np
import pytest
from msra_modules.realtime_analytics.quality_gates import RealtimeQualityGateChecker
from msra_modules.realtime_analytics.data_simulator import VitalSignsSimulator
from shared.quality_gates.gate_runner import GateVerdict


class TestRealtimeQualityGateChecker:
    """RealtimeQualityGateChecker 测试"""

    def test_init(self):
        """测试初始化"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        assert checker.study_id == "RT-TEST-001"


class TestCheckDataSourceAvailable:
    """check_data_source_available 测试"""

    def test_simulator_available(self):
        """测试模拟器可用"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        sim = VitalSignsSimulator()
        result = checker.check_data_source_available(sim)
        assert result.status == "PASS"
        assert result.is_key is True

    def test_no_source(self):
        """测试无数据源"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        result = checker.check_data_source_available(None)
        assert result.status == "FAIL"
        assert result.is_key is True

    def test_stream_processor_with_metrics(self):
        """测试有指标的流处理器"""
        from msra_modules.realtime_analytics.stream_processor import StreamProcessor
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        sp = StreamProcessor()
        sp.register_metric("hr")
        result = checker.check_data_source_available(sp)
        assert result.status == "PASS"

    def test_stream_processor_no_metrics(self):
        """测试无指标的流处理器"""
        from msra_modules.realtime_analytics.stream_processor import StreamProcessor
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        sp = StreamProcessor()
        result = checker.check_data_source_available(sp)
        assert result.status == "FAIL"

    def test_object_with_generate_stream(self):
        """测试有 generate_stream 方法的对象"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")

        class MockSource:
            def generate_stream(self):
                return []

        result = checker.check_data_source_available(MockSource())
        assert result.status == "PASS"

    def test_object_with_is_connected(self):
        """测试有 is_connected 方法的对象"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")

        class ConnectedSource:
            def is_connected(self):
                return True

        class DisconnectedSource:
            def is_connected(self):
                return False

        assert checker.check_data_source_available(ConnectedSource()).status == "PASS"
        assert checker.check_data_source_available(DisconnectedSource()).status == "FAIL"

    def test_unknown_object(self):
        """测试无法识别的对象"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        result = checker.check_data_source_available("not_a_source")
        assert result.status == "FAIL"


class TestCheckTimestampContinuity:
    """check_timestamp_continuity 测试"""

    def test_continuous_timestamps(self):
        """测试连续时间戳"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        timestamps = [float(i) for i in range(60)]
        result = checker.check_timestamp_continuity(timestamps, window_size=60)
        assert result.status == "PASS"

    def test_large_gap(self):
        """测试过大间隔"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        timestamps = [0, 1, 2, 3, 200, 201]  # 200 - 3 = 197 > 60*2=120
        result = checker.check_timestamp_continuity(timestamps, window_size=60, max_gap_multiplier=2.0)
        assert result.status == "FAIL"

    def test_too_few_timestamps(self):
        """测试时间戳不足"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        result = checker.check_timestamp_continuity([1000.0], window_size=60)
        assert result.status == "FAIL"

    def test_empty_timestamps(self):
        """测试空时间戳列表"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        result = checker.check_timestamp_continuity([], window_size=60)
        assert result.status == "FAIL"

    def test_none_timestamps(self):
        """测试 None 时间戳"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        result = checker.check_timestamp_continuity(None, window_size=60)
        assert result.status == "FAIL"


class TestCheckDetectionSensitivity:
    """check_detection_sensitivity 测试"""

    def test_normal_rate(self):
        """测试正常检测率"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        result = checker.check_detection_sensitivity(0.05)
        assert result.status == "PASS"

    def test_too_low_rate(self):
        """测试检测率过低"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        result = checker.check_detection_sensitivity(0.001)
        assert result.status == "FAIL"

    def test_too_high_rate(self):
        """测试检测率过高"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        result = checker.check_detection_sensitivity(0.5)
        assert result.status == "FAIL"

    def test_boundary_values(self):
        """测试边界值"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        assert checker.check_detection_sensitivity(0.01).status == "PASS"
        assert checker.check_detection_sensitivity(0.20).status == "PASS"

    def test_out_of_range(self):
        """测试超出范围的检测率"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        result = checker.check_detection_sensitivity(1.5)
        assert result.status == "FAIL"

    def test_custom_range(self):
        """测试自定义范围"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        result = checker.check_detection_sensitivity(0.005, min_rate=0.001, max_rate=0.50)
        assert result.status == "PASS"


class TestRunGateRT1:
    """run_gate_rt1 集成测试"""

    def test_all_pass(self):
        """测试全部通过"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        sim = VitalSignsSimulator()
        timestamps = [float(i) for i in range(60)]
        result = checker.run_gate_rt1(
            source=sim,
            timestamps=timestamps,
            detection_rate=0.05,
        )
        assert result.verdict == GateVerdict.PASS
        assert result.total_items == 3
        assert result.passed_items == 3

    def test_key_check_fails(self):
        """测试关键项失败"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        result = checker.run_gate_rt1(source=None)
        assert result.verdict == GateVerdict.BLOCKED

    def test_optional_check_skipped(self):
        """测试可选项跳过"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        sim = VitalSignsSimulator()
        timestamps = [float(i) for i in range(60)]
        result = checker.run_gate_rt1(
            source=sim,
            timestamps=timestamps,
            # detection_rate 不提供 → N/A
        )
        assert result.verdict == GateVerdict.PASS
        assert result.total_items == 3

    def test_result_has_check_results(self):
        """测试结果包含检查结果"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        sim = VitalSignsSimulator()
        result = checker.run_gate_rt1(source=sim)
        assert len(result.check_results) == 3

    def test_result_serializable(self):
        """测试结果可序列化"""
        checker = RealtimeQualityGateChecker(study_id="RT-TEST-001")
        sim = VitalSignsSimulator()
        result = checker.run_gate_rt1(source=sim)
        d = result.to_dict()
        assert "verdict" in d
        assert "check_results" in d
