"""
Integration tests for realtime_analytics module.

端到端测试: 模拟器 → 流处理 → 异常检测 → 告警 → 报告。
"""

import tempfile
from pathlib import Path

import numpy as np

from msra_modules.realtime_analytics.alert_system import Alert, AlertChannel, AlertSystem
from msra_modules.realtime_analytics.anomaly_detector import (
    AlertLevel,
    AnomalyDetector,
    MultivariateDetector,
)
from msra_modules.realtime_analytics.dashboard import RealtimeDashboard, ReportGenerator
from msra_modules.realtime_analytics.data_simulator import VitalSignsSimulator
from msra_modules.realtime_analytics.quality_gates import RealtimeQualityGateChecker
from msra_modules.realtime_analytics.stream_processor import StreamProcessor
from shared.quality_gates.gate_runner import GateVerdict


class TestEndToEndNormalFlow:
    """端到端正常流程测试"""

    def test_simulator_to_stream_to_detect(self):
        """测试: 模拟器 → 流处理 → 异常检测"""
        # 初始化组件
        sim = VitalSignsSimulator()
        processor = StreamProcessor(window_size=60)
        detector = AnomalyDetector()
        detector.add_default_vital_signs_rules()

        # 生成正常数据
        n_samples = 50
        all_alerts = []
        for i in range(n_samples):
            sample = sim.generate_sample(timestamp=1000.0 + i)
            processor.add_data_point("heart_rate", sample.heart_rate, sample.timestamp)
            processor.add_data_point("spo2", sample.spo2, sample.timestamp)

            # 检测异常
            hr_alerts = detector.evaluate("heart_rate", sample.heart_rate, sample.timestamp)
            spo2_alerts = detector.evaluate("spo2", sample.spo2, sample.timestamp)
            all_alerts.extend(hr_alerts)
            all_alerts.extend(spo2_alerts)

        # 正常数据不应产生太多告警
        assert len(all_alerts) <= 5  # 容许少量随机波动触发

        # 验证流处理器统计
        hr_stats = processor.get_metric_stats("heart_rate")
        assert hr_stats["count"] == n_samples
        assert 60 < hr_stats["mean"] < 90  # 正常心率范围

    def test_anomaly_detection_with_simulated_anomaly(self):
        """测试: 模拟器注入异常 → 检测器捕获"""
        sim = VitalSignsSimulator()
        detector = AnomalyDetector()
        detector.add_default_vital_signs_rules()

        # 生成正常数据建立基线
        for i in range(10):
            sample = sim.generate_sample(timestamp=1000.0 + i)
            detector.evaluate("heart_rate", sample.heart_rate, sample.timestamp)

        # 注入心动过速异常
        sim.trigger_anomaly("tachycardia", duration=10)
        detected = False
        for i in range(10):
            sample = sim.generate_sample(timestamp=1010.0 + i)
            alerts = detector.evaluate("heart_rate", sample.heart_rate, sample.timestamp)
            if alerts:
                detected = True
                assert alerts[0].level == AlertLevel.CRITICAL

        assert detected is True

    def test_alert_system_integration(self):
        """测试: 异常检测 → 告警系统分发"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = str(Path(tmpdir) / "alerts.log")
            alert_system = AlertSystem(log_file=log_file)
            detector = AnomalyDetector()
            detector.add_default_vital_signs_rules()

            # 注册告警处理器
            alert_system.register_handler(
                AlertChannel.WEBHOOK,
                lambda alert: None,  # 占位处理器
            )

            # 连接检测器到告警系统
            def on_alert(detector_alert):
                system_alert = Alert(
                    rule_name=detector_alert.rule_name,
                    metric=detector_alert.metric,
                    value=detector_alert.value,
                    level=detector_alert.level.value,
                    message=detector_alert.message,
                    timestamp=detector_alert.timestamp,
                )
                alert_system.send_alert(system_alert)

            detector.add_alert_handler(on_alert)

            # 触发告警
            alerts = detector.evaluate("heart_rate", 160.0, timestamp=1000.0)
            # 通过处理器发送到 alert_system
            for a in alerts:
                on_alert(a)

            # 验证告警系统接收到
            history = alert_system.get_history()
            assert len(history) >= 1
            assert Path(log_file).exists()


class TestMultivariateIntegration:
    """多变量异常检测集成测试"""

    def test_multivariate_with_simulator(self):
        """测试: 模拟器数据 → 多变量检测"""
        sim = VitalSignsSimulator()
        mv_detector = MultivariateDetector(contamination=0.05)

        # 生成数据矩阵
        data_points = []
        for i in range(100):
            sample = sim.generate_sample(timestamp=1000.0 + i)
            data_points.append([
                sample.heart_rate,
                sample.spo2,
                sample.systolic_bp,
                sample.temperature,
            ])

        data = np.array(data_points)
        results = mv_detector.detect(
            data,
            feature_names=["hr", "spo2", "bp", "temp"],
            timestamps=[1000.0 + i for i in range(100)],
        )

        assert len(results) == 100
        # 应该有少量异常（正常数据中 ~5%）
        anomalies = [r for r in results if r.is_anomaly]
        assert len(anomalies) <= 20  # 合理范围


class TestDashboardIntegration:
    """仪表盘集成测试"""

    def test_dashboard_with_stream_data(self):
        """测试: 流数据 → 仪表盘"""
        dashboard = RealtimeDashboard(max_points=1000)
        dashboard.add_metric("heart_rate", display_name="心率", unit="bpm")

        # 添加数据
        for i in range(50):
            dashboard.update("heart_rate", 70.0 + np.random.normal(0, 3), timestamp=1000.0 + i)

        data = dashboard.get_dashboard_data()
        assert "heart_rate" in data["metrics"]
        assert data["metrics"]["heart_rate"]["stats"]["current"] != 0.0

    def test_report_generation(self):
        """测试: 监控报告生成"""
        with tempfile.TemporaryDirectory() as tmpdir:
            reporter = ReportGenerator(output_dir=tmpdir)

            stats = {
                "heart_rate": {"mean": 75.0, "std": 3.0, "min": 65.0, "max": 85.0},
                "spo2": {"mean": 98.0, "std": 0.5, "min": 96.0, "max": 99.0},
            }
            alerts = [
                {
                    "rule_name": "tachycardia",
                    "metric": "heart_rate",
                    "value": 160.0,
                    "level": "critical",
                    "message": "HR > 150",
                    "timestamp": 1000.0,
                }
            ]

            # HTML 报告
            html_path = reporter.generate_monitoring_report(
                duration="60 seconds",
                stats=stats,
                alerts=alerts,
                output_format="html",
            )
            assert Path(html_path).exists()
            assert html_path.endswith(".html")

            # Markdown 报告
            md_path = reporter.generate_monitoring_report(
                duration="60 seconds",
                stats=stats,
                alerts=alerts,
                output_format="markdown",
            )
            assert Path(md_path).exists()
            assert md_path.endswith(".markdown")


class TestQualityGateIntegration:
    """质量门闸集成测试"""

    def test_full_gate_with_simulator(self):
        """测试: 模拟器完整门闸检查"""
        checker = RealtimeQualityGateChecker(study_id="RT-INT-001")
        sim = VitalSignsSimulator()

        # 生成时间戳序列
        timestamps = [float(i) for i in range(100)]

        result = checker.run_gate_rt1(
            source=sim,
            timestamps=timestamps,
            detection_rate=0.05,
        )

        assert result.verdict == GateVerdict.PASS
        assert result.pass_rate == 1.0

    def test_gate_with_stream_processor(self):
        """测试: 流处理器门闸检查"""
        checker = RealtimeQualityGateChecker(study_id="RT-INT-002")
        sp = StreamProcessor()
        sp.register_metric("hr")

        # 添加数据
        for i in range(30):
            sp.add_data_point("hr", 75.0 + i * 0.1, timestamp=1000.0 + i)

        timestamps = [1000.0 + i for i in range(30)]
        result = checker.run_gate_rt1(
            source=sp,
            timestamps=timestamps,
            detection_rate=0.03,
        )

        assert result.verdict == GateVerdict.PASS
