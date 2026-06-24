"""
Stream Processor - 流处理器

RT-001: Faust环境集成
RT-002: Kafka消费者wrapper
RT-004: 滑动窗口统计
RT-007: 事件处理与聚合
"""

import numpy as np
import time
from typing import Optional, Dict, Callable, List, Any, Union
from collections import deque
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class StreamEvent:
    """流事件"""
    timestamp: float
    value: float
    metadata: Dict = field(default_factory=dict)


class SlidingWindowStats:
    """滑动窗口统计"""

    def __init__(self, window_size: int = 60):
        """初始化滑动窗口

        Args:
            window_size: 窗口大小 (秒)
        """
        self.window_size = window_size
        self._data: deque = deque()
        self._timestamps: deque = deque()

    def add(self, value: float, timestamp: Optional[float] = None):
        """添加数据点

        Args:
            value: 数据值
            timestamp: 时间戳 (默认当前时间)
        """
        if timestamp is None:
            timestamp = time.time()

        self._data.append(value)
        self._timestamps.append(timestamp)

        # 移除过期数据
        cutoff = timestamp - self.window_size
        while self._timestamps and self._timestamps[0] < cutoff:
            self._data.popleft()
            self._timestamps.popleft()

    def get_stats(self) -> Dict[str, float]:
        """获取统计指标

        Returns:
            统计字典
        """
        if not self._data:
            return {
                "count": 0,
                "mean": 0.0,
                "std": 0.0,
                "min": 0.0,
                "max": 0.0,
                "median": 0.0,
            }

        data = np.array(self._data)
        return {
            "count": len(data),
            "mean": float(np.mean(data)),
            "std": float(np.std(data)),
            "min": float(np.min(data)),
            "max": float(np.max(data)),
            "median": float(np.median(data)),
            "p25": float(np.percentile(data, 25)),
            "p75": float(np.percentile(data, 75)),
        }

    def clear(self):
        """清空数据"""
        self._data.clear()
        self._timestamps.clear()


class StreamProcessor:
    """流处理器"""

    def __init__(self,
                 window_size: int = 60,
                 kafka_bootstrap_servers: str = "localhost:9092"):
        """初始化流处理器

        Args:
            window_size: 滑动窗口大小 (秒)
            kafka_bootstrap_servers: Kafka服务器地址
        """
        self.window_size = window_size
        self.kafka_servers = kafka_bootstrap_servers
        self._windows: Dict[str, SlidingWindowStats] = {}
        self._handlers: List[Callable] = []
        self._running = False

    def register_metric(self, name: str, window_size: Optional[int] = None):
        """注册指标

        Args:
            name: 指标名称
            window_size: 窗口大小 (覆盖默认值)
        """
        ws = window_size or self.window_size
        self._windows[name] = SlidingWindowStats(window_size=ws)
        logger.info(f"Registered metric: {name} (window={ws}s)")

    def add_data_point(self, metric: str, value: float,
                       timestamp: Optional[float] = None):
        """添加数据点

        Args:
            metric: 指标名称
            value: 数据值
            timestamp: 时间戳
        """
        if metric not in self._windows:
            self.register_metric(metric)

        self._windows[metric].add(value, timestamp)

        # 触发处理器
        for handler in self._handlers:
            try:
                handler(metric, value, timestamp)
            except Exception as e:
                logger.error(f"Handler error: {e}")

    def get_metric_stats(self, metric: str) -> Dict[str, float]:
        """获取指标统计

        Args:
            metric: 指标名称

        Returns:
            统计字典
        """
        if metric not in self._windows:
            return {"error": f"Metric {metric} not found"}

        return self._windows[metric].get_stats()

    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """获取所有指标统计

        Returns:
            所有指标统计字典
        """
        return {
            metric: window.get_stats()
            for metric, window in self._windows.items()
        }

    def add_handler(self, handler: Callable[[str, float, Optional[float]], None]):
        """添加数据处理器

        Args:
            handler: 处理函数 (metric, value, timestamp)
        """
        self._handlers.append(handler)

    def start_kafka_consumer(self, topic: str,
                             metric_field: str = "value"):
        """启动Kafka消费者

        Args:
            topic: Kafka主题
            metric_field: 值字段名
        """
        try:
            from kafka import KafkaConsumer
            import json

            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.kafka_servers,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest'
            )

            logger.info(f"Started Kafka consumer for topic: {topic}")
            self._running = True

            for message in consumer:
                if not self._running:
                    break

                data = message.value
                metric = data.get('metric', 'default')
                value = data.get(metric_field, 0)
                timestamp = data.get('timestamp', time.time())

                self.add_data_point(metric, value, timestamp)

        except ImportError:
            logger.warning(
                "kafka-python not installed. Install with: pip install kafka-python"
            )
        except Exception as e:
            logger.error(f"Kafka consumer error: {e}")

    def stop(self):
        """停止处理"""
        self._running = False
        logger.info("Stream processor stopped")

    def get_all_metrics(self) -> List[str]:
        """获取所有已注册的指标名

        Returns:
            指标名列表
        """
        return list(self._windows.keys())

    def aggregate(self, metric: str, func: str = "mean") -> float:
        """对窗口数据进行聚合计算

        Args:
            metric: 指标名称
            func: 聚合函数名 ('mean', 'std', 'min', 'max', 'median', 'sum', 'count')

        Returns:
            聚合结果

        Raises:
            ValueError: 指标不存在或聚合函数不支持
        """
        if metric not in self._windows:
            raise ValueError(f"Metric '{metric}' not found. Available: {self.get_all_metrics()}")

        window = self._windows[metric]
        if not window._data:
            raise ValueError(f"No data in window for metric '{metric}'")

        data = np.array(window._data)

        agg_funcs = {
            "mean": lambda d: float(np.mean(d)),
            "std": lambda d: float(np.std(d)),
            "min": lambda d: float(np.min(d)),
            "max": lambda d: float(np.max(d)),
            "median": lambda d: float(np.median(d)),
            "sum": lambda d: float(np.sum(d)),
            "count": lambda d: float(len(d)),
            "p25": lambda d: float(np.percentile(d, 25)),
            "p75": lambda d: float(np.percentile(d, 75)),
        }

        if func not in agg_funcs:
            raise ValueError(
                f"Unsupported aggregation function '{func}'. "
                f"Supported: {list(agg_funcs.keys())}"
            )

        return agg_funcs[func](data)

    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """统一事件处理入口

        接受字典格式的事件数据，提取指标和值，处理并返回结果。

        Args:
            event: 事件字典，必须包含:
                - metric (str): 指标名称
                - value (float): 指标值
                可选包含:
                - timestamp (float): 时间戳
                - metadata (Dict): 额外元数据

        Returns:
            处理结果字典，包含:
                - metric: 指标名称
                - value: 处理的值
                - timestamp: 时间戳
                - stats: 当前窗口统计
                - handlers_called: 已调用的处理器数量
        """
        metric = event.get("metric")
        value = event.get("value")

        if metric is None:
            raise ValueError("Event must contain 'metric' field")
        if value is None:
            raise ValueError("Event must contain 'value' field")

        timestamp = event.get("timestamp", time.time())

        # 添加数据点
        self.add_data_point(metric, float(value), timestamp)

        # 获取统计
        stats = self.get_metric_stats(metric)

        return {
            "metric": metric,
            "value": float(value),
            "timestamp": timestamp,
            "stats": stats,
            "handlers_called": len(self._handlers),
        }

    def create_faust_app(self, app_name: str = "msra-stream"):
        """创建Faust应用

        Args:
            app_name: 应用名称

        Returns:
            Faust App对象
        """
        try:
            import faust

            app = faust.App(
                app_name,
                broker=f"kafka://{self.kafka_servers}",
                value_serializer='json'
            )

            logger.info(f"Created Faust app: {app_name}")
            return app

        except ImportError:
            logger.warning(
                "Faust not installed. Install with: pip install faust"
            )
            return None
