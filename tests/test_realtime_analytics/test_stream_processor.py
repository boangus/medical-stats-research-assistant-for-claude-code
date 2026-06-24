"""
Tests for StreamProcessor and SlidingWindowStats.
"""

import pytest

from msra_modules.realtime_analytics.stream_processor import (
    SlidingWindowStats,
    StreamEvent,
    StreamProcessor,
)


class TestSlidingWindowStats:
    """SlidingWindowStats 测试"""

    def test_init_default_window(self):
        """测试默认窗口大小"""
        sw = SlidingWindowStats()
        assert sw.window_size == 60

    def test_init_custom_window(self):
        """测试自定义窗口大小"""
        sw = SlidingWindowStats(window_size=30)
        assert sw.window_size == 30

    def test_add_single_point(self):
        """测试添加单个数据点"""
        sw = SlidingWindowStats(window_size=60)
        sw.add(75.0, timestamp=1000.0)
        stats = sw.get_stats()
        assert stats["count"] == 1
        assert stats["mean"] == 75.0

    def test_add_multiple_points(self):
        """测试添加多个数据点"""
        sw = SlidingWindowStats(window_size=60)
        for i in range(10):
            sw.add(float(i), timestamp=1000.0 + i)
        stats = sw.get_stats()
        assert stats["count"] == 10
        assert abs(stats["mean"] - 4.5) < 1e-6

    def test_window_expiration(self):
        """测试窗口过期数据被移除"""
        sw = SlidingWindowStats(window_size=10)
        sw.add(1.0, timestamp=1000.0)
        sw.add(2.0, timestamp=1005.0)
        sw.add(3.0, timestamp=1020.0)  # 1000.0 已过期 (1020 - 10 > 1000)
        stats = sw.get_stats()
        assert stats["count"] == 1  # 只有 1020.0 的数据在窗口内
        assert stats["mean"] == 3.0

    def test_get_stats_empty(self):
        """测试空窗口返回零值"""
        sw = SlidingWindowStats(window_size=60)
        stats = sw.get_stats()
        assert stats["count"] == 0
        assert stats["mean"] == 0.0
        assert stats["std"] == 0.0

    def test_get_stats_all_keys(self):
        """测试统计字典包含所有键"""
        sw = SlidingWindowStats(window_size=60)
        for i in range(20):
            sw.add(float(i), timestamp=1000.0 + i)
        stats = sw.get_stats()
        expected_keys = {"count", "mean", "std", "min", "max", "median", "p25", "p75"}
        assert expected_keys.issubset(set(stats.keys()))

    def test_clear(self):
        """测试清空数据"""
        sw = SlidingWindowStats(window_size=60)
        sw.add(1.0, timestamp=1000.0)
        sw.add(2.0, timestamp=1001.0)
        sw.clear()
        stats = sw.get_stats()
        assert stats["count"] == 0


class TestStreamProcessor:
    """StreamProcessor 测试"""

    def test_init_default(self):
        """测试默认初始化"""
        sp = StreamProcessor()
        assert sp.window_size == 60

    def test_register_metric(self):
        """测试注册指标"""
        sp = StreamProcessor(window_size=30)
        sp.register_metric("heart_rate")
        assert "heart_rate" in sp._windows

    def test_register_metric_custom_window(self):
        """测试注册指标时自定义窗口大小"""
        sp = StreamProcessor(window_size=60)
        sp.register_metric("hr", window_size=120)
        assert sp._windows["hr"].window_size == 120

    def test_add_data_point_auto_register(self):
        """测试添加数据点自动注册指标"""
        sp = StreamProcessor()
        sp.add_data_point("heart_rate", 75.0, timestamp=1000.0)
        assert "heart_rate" in sp._windows

    def test_get_metric_stats(self):
        """测试获取指标统计"""
        sp = StreamProcessor(window_size=60)
        sp.register_metric("hr")
        for i in range(10):
            sp.add_data_point("hr", 70.0 + i, timestamp=1000.0 + i)
        stats = sp.get_metric_stats("hr")
        assert stats["count"] == 10
        assert abs(stats["mean"] - 74.5) < 1e-6

    def test_get_metric_stats_not_found(self):
        """测试获取不存在指标的统计"""
        sp = StreamProcessor()
        result = sp.get_metric_stats("nonexistent")
        assert "error" in result

    def test_get_all_stats(self):
        """测试获取所有指标统计"""
        sp = StreamProcessor()
        sp.add_data_point("hr", 75.0, timestamp=1000.0)
        sp.add_data_point("spo2", 98.0, timestamp=1000.0)
        all_stats = sp.get_all_stats()
        assert "hr" in all_stats
        assert "spo2" in all_stats

    def test_handler_triggered(self):
        """测试处理器被触发"""
        sp = StreamProcessor()
        received = []
        sp.add_handler(lambda m, v, t: received.append((m, v, t)))
        sp.add_data_point("hr", 75.0, timestamp=1000.0)
        assert len(received) == 1
        assert received[0] == ("hr", 75.0, 1000.0)

    def test_multiple_handlers(self):
        """测试多个处理器"""
        sp = StreamProcessor()
        count = [0]
        sp.add_handler(lambda m, v, t: count.__setitem__(0, count[0] + 1))
        sp.add_handler(lambda m, v, t: count.__setitem__(0, count[0] + 1))
        sp.add_data_point("hr", 75.0, timestamp=1000.0)
        assert count[0] == 2

    def test_handler_error_does_not_break(self):
        """测试处理器错误不影响其他处理器"""
        sp = StreamProcessor()
        sp.add_handler(lambda m, v, t: 1 / 0)  # 故意抛出错误
        received = []
        sp.add_handler(lambda m, v, t: received.append(m))
        sp.add_data_point("hr", 75.0, timestamp=1000.0)
        assert len(received) == 1

    def test_get_all_metrics(self):
        """测试获取所有指标名"""
        sp = StreamProcessor()
        sp.register_metric("hr")
        sp.register_metric("spo2")
        sp.register_metric("bp")
        metrics = sp.get_all_metrics()
        assert set(metrics) == {"hr", "spo2", "bp"}

    def test_get_all_metrics_empty(self):
        """测试无指标时返回空列表"""
        sp = StreamProcessor()
        assert sp.get_all_metrics() == []

    def test_aggregate_mean(self):
        """测试聚合 mean"""
        sp = StreamProcessor(window_size=60)
        for i in range(10):
            sp.add_data_point("hr", float(i), timestamp=1000.0 + i)
        result = sp.aggregate("hr", "mean")
        assert abs(result - 4.5) < 1e-6

    def test_aggregate_std(self):
        """测试聚合 std"""
        sp = StreamProcessor(window_size=60)
        for i in range(10):
            sp.add_data_point("hr", float(i), timestamp=1000.0 + i)
        result = sp.aggregate("hr", "std")
        assert result > 0

    def test_aggregate_sum(self):
        """测试聚合 sum"""
        sp = StreamProcessor(window_size=60)
        for i in range(5):
            sp.add_data_point("hr", float(i), timestamp=1000.0 + i)
        result = sp.aggregate("hr", "sum")
        assert abs(result - 10.0) < 1e-6

    def test_aggregate_count(self):
        """测试聚合 count"""
        sp = StreamProcessor(window_size=60)
        for i in range(5):
            sp.add_data_point("hr", float(i), timestamp=1000.0 + i)
        result = sp.aggregate("hr", "count")
        assert result == 5.0

    def test_aggregate_unsupported_func(self):
        """测试不支持的聚合函数"""
        sp = StreamProcessor(window_size=60)
        sp.add_data_point("hr", 75.0, timestamp=1000.0)
        with pytest.raises(ValueError, match="Unsupported aggregation"):
            sp.aggregate("hr", "invalid_func")

    def test_aggregate_metric_not_found(self):
        """测试聚合不存在的指标"""
        sp = StreamProcessor()
        with pytest.raises(ValueError, match="not found"):
            sp.aggregate("nonexistent", "mean")

    def test_aggregate_empty_window(self):
        """测试聚合空窗口"""
        sp = StreamProcessor()
        sp.register_metric("hr")
        with pytest.raises(ValueError, match="No data"):
            sp.aggregate("hr", "mean")

    def test_process_event_basic(self):
        """测试 process_event 基本功能"""
        sp = StreamProcessor(window_size=60)
        result = sp.process_event({
            "metric": "heart_rate",
            "value": 75.0,
            "timestamp": 1000.0,
        })
        assert result["metric"] == "heart_rate"
        assert result["value"] == 75.0
        assert result["timestamp"] == 1000.0
        assert result["stats"]["count"] == 1

    def test_process_event_auto_timestamp(self):
        """测试 process_event 自动生成时间戳"""
        sp = StreamProcessor(window_size=60)
        result = sp.process_event({"metric": "hr", "value": 72.0})
        assert result["timestamp"] is not None
        assert result["timestamp"] > 0

    def test_process_event_missing_metric(self):
        """测试 process_event 缺少 metric"""
        sp = StreamProcessor()
        with pytest.raises(ValueError, match="must contain 'metric'"):
            sp.process_event({"value": 75.0})

    def test_process_event_missing_value(self):
        """测试 process_event 缺少 value"""
        sp = StreamProcessor()
        with pytest.raises(ValueError, match="must contain 'value'"):
            sp.process_event({"metric": "hr"})

    def test_process_event_multiple_times(self):
        """测试多次 process_event 积累数据"""
        sp = StreamProcessor(window_size=60)
        for i in range(5):
            sp.process_event({
                "metric": "hr",
                "value": 70.0 + i,
                "timestamp": 1000.0 + i,
            })
        stats = sp.get_metric_stats("hr")
        assert stats["count"] == 5


class TestStreamEvent:
    """StreamEvent 测试"""

    def test_creation(self):
        """测试创建 StreamEvent"""
        event = StreamEvent(timestamp=1000.0, value=75.0)
        assert event.timestamp == 1000.0
        assert event.value == 75.0
        assert event.metadata == {}

    def test_with_metadata(self):
        """测试带元数据的 StreamEvent"""
        event = StreamEvent(timestamp=1000.0, value=75.0, metadata={"source": "simulator"})
        assert event.metadata["source"] == "simulator"
