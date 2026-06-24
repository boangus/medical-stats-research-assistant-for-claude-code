"""
Tests for AlertSystem.
"""

import time
import json
import tempfile
import pytest
from pathlib import Path
from msra_modules.realtime_analytics.alert_system import (
    AlertSystem,
    Alert,
    AlertChannel,
)


class TestAlert:
    """Alert 测试"""

    def test_creation(self):
        """测试创建 Alert"""
        alert = Alert(
            rule_name="tachycardia",
            metric="heart_rate",
            value=160.0,
            level="critical",
            message="HR too high",
            timestamp=1000.0,
        )
        assert alert.rule_name == "tachycardia"
        assert alert.context == {}

    def test_to_dict(self):
        """测试转换为字典"""
        alert = Alert(
            rule_name="test", metric="hr", value=100.0,
            level="warning", message="test msg", timestamp=1000.0,
        )
        d = alert.to_dict()
        assert d["rule_name"] == "test"
        assert d["value"] == 100.0

    def test_to_json(self):
        """测试转换为 JSON"""
        alert = Alert(
            rule_name="test", metric="hr", value=100.0,
            level="warning", message="test msg", timestamp=1000.0,
        )
        j = alert.to_json()
        parsed = json.loads(j)
        assert parsed["rule_name"] == "test"


class TestAlertSystem:
    """AlertSystem 测试"""

    def test_init_default(self):
        """测试默认初始化"""
        system = AlertSystem()
        assert AlertChannel.LOG in system._handlers

    def test_init_with_log_file(self):
        """测试带日志文件初始化"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = str(Path(tmpdir) / "alerts.log")
            system = AlertSystem(log_file=log_file)
            assert AlertChannel.FILE in system._handlers

    def test_send_alert_records_history(self):
        """测试发送告警记录历史"""
        system = AlertSystem()
        alert = Alert(
            rule_name="test", metric="hr", value=100.0,
            level="warning", message="test", timestamp=1000.0,
        )
        system.send_alert(alert, channels=[AlertChannel.LOG])
        history = system.get_history()
        assert len(history) == 1
        assert history[0].rule_name == "test"

    def test_get_history_with_level_filter(self):
        """测试按级别筛选历史"""
        system = AlertSystem()
        system.send_alert(Alert(
            rule_name="a", metric="hr", value=100.0,
            level="warning", message="a", timestamp=1000.0,
        ), channels=[AlertChannel.LOG])
        system.send_alert(Alert(
            rule_name="b", metric="hr", value=100.0,
            level="critical", message="b", timestamp=1001.0,
        ), channels=[AlertChannel.LOG])
        warnings = system.get_history(level="warning")
        assert len(warnings) == 1

    def test_get_statistics(self):
        """测试获取统计"""
        system = AlertSystem()
        for i in range(3):
            system.send_alert(Alert(
                rule_name="tachy", metric="hr", value=160.0,
                level="critical", message=f"alert {i}", timestamp=1000.0 + i,
            ), channels=[AlertChannel.LOG])
        system.send_alert(Alert(
            rule_name="hyper", metric="temp", value=39.0,
            level="warning", message="temp high", timestamp=1003.0,
        ), channels=[AlertChannel.LOG])
        stats = system.get_statistics()
        assert stats["total_alerts"] == 4
        assert stats["by_level"]["critical"] == 3
        assert stats["by_rule"]["tachy"] == 3

    def test_file_handler_writes(self):
        """测试文件处理器写入"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = str(Path(tmpdir) / "alerts.log")
            system = AlertSystem(log_file=log_file)
            alert = Alert(
                rule_name="test", metric="hr", value=100.0,
                level="warning", message="test", timestamp=1000.0,
            )
            system.send_alert(alert, channels=[AlertChannel.FILE])
            assert Path(log_file).exists()
            content = Path(log_file).read_text(encoding="utf-8")
            parsed = json.loads(content.strip())
            assert parsed["rule_name"] == "test"

    def test_custom_handler(self):
        """测试自定义处理器"""
        system = AlertSystem()
        received = []
        system.register_handler(
            AlertChannel.WEBHOOK,
            lambda alert: received.append(alert),
        )
        alert = Alert(
            rule_name="test", metric="hr", value=100.0,
            level="warning", message="test", timestamp=1000.0,
        )
        system.send_alert(alert, channels=[AlertChannel.WEBHOOK])
        assert len(received) == 1

    def test_history_limit(self):
        """测试历史记录上限"""
        system = AlertSystem()
        system._max_history = 5
        for i in range(10):
            system.send_alert(Alert(
                rule_name=f"r{i}", metric="hr", value=100.0,
                level="warning", message=f"msg {i}", timestamp=1000.0 + i,
            ), channels=[AlertChannel.LOG])
        assert len(system._alert_history) == 5
