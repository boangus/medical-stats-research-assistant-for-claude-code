"""
Anomaly Detector - 异常检测器

RT-005: 异常检测规则引擎
RT-006: 实时趋势检测
"""

import numpy as np
from collections import deque
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """警报级别"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AlertRule:
    """警报规则"""
    name: str
    metric: str
    condition: str  # "gt", "lt", "gte", "lte", "range"
    threshold: float
    threshold_max: Optional[float] = None
    level: AlertLevel = AlertLevel.WARNING
    sustained_seconds: int = 0  # 持续时间要求
    cooldown_seconds: int = 300  # 冷却时间
    description: str = ""

    def evaluate(self, value: float) -> bool:
        """评估规则

        Args:
            value: 当前值

        Returns:
            是否触发
        """
        if self.condition == "gt":
            return value > self.threshold
        elif self.condition == "lt":
            return value < self.threshold
        elif self.condition == "gte":
            return value >= self.threshold
        elif self.condition == "lte":
            return value <= self.threshold
        elif self.condition == "range":
            if self.threshold_max is None:
                return False
            return value < self.threshold or value > self.threshold_max
        else:
            return False


@dataclass
class Alert:
    """警报事件"""
    rule_name: str
    metric: str
    value: float
    level: AlertLevel
    message: str
    timestamp: float
    context: Dict = field(default_factory=dict)


class AnomalyDetector:
    """异常检测器"""

    def __init__(self):
        """初始化异常检测器"""
        self._rules: List[AlertRule] = []
        self._sustained_violations: Dict[str, float] = {}  # rule_name -> start_time
        self._last_alert: Dict[str, float] = {}  # rule_name -> last alert time
        self._alert_handlers: List[Callable[[Alert], None]] = []

    def add_rule(self, rule: AlertRule):
        """添加规则

        Args:
            rule: 警报规则
        """
        self._rules.append(rule)
        logger.info(f"Added rule: {rule.name} for metric {rule.metric}")

    def add_default_vital_signs_rules(self):
        """添加默认生命体征规则"""
        default_rules = [
            AlertRule(
                name="bradycardia",
                metric="heart_rate",
                condition="lt",
                threshold=40,
                level=AlertLevel.CRITICAL,
                description="Bradycardia: HR < 40 bpm"
            ),
            AlertRule(
                name="tachycardia",
                metric="heart_rate",
                condition="gt",
                threshold=150,
                level=AlertLevel.CRITICAL,
                description="Tachycardia: HR > 150 bpm"
            ),
            AlertRule(
                name="hypoxemia",
                metric="spo2",
                condition="lt",
                threshold=90,
                level=AlertLevel.CRITICAL,
                description="Hypoxemia: SpO2 < 90%"
            ),
            AlertRule(
                name="severe_hypoxemia",
                metric="spo2",
                condition="lt",
                threshold=85,
                level=AlertLevel.CRITICAL,
                description="Severe hypoxemia: SpO2 < 85%"
            ),
            AlertRule(
                name="hypertension",
                metric="systolic_bp",
                condition="gt",
                threshold=180,
                level=AlertLevel.WARNING,
                description="Hypertension: SBP > 180 mmHg"
            ),
            AlertRule(
                name="hypotension",
                metric="systolic_bp",
                condition="lt",
                threshold=90,
                level=AlertLevel.CRITICAL,
                description="Hypotension: SBP < 90 mmHg"
            ),
            AlertRule(
                name="hyperthermia",
                metric="temperature",
                condition="gt",
                threshold=38.5,
                level=AlertLevel.WARNING,
                description="Hyperthermia: Temp > 38.5°C"
            ),
            AlertRule(
                name="hypothermia",
                metric="temperature",
                condition="lt",
                threshold=35.0,
                level=AlertLevel.WARNING,
                description="Hypothermia: Temp < 35.0°C"
            ),
        ]

        for rule in default_rules:
            self.add_rule(rule)

    def evaluate(self, metric: str, value: float,
                 timestamp: Optional[float] = None) -> List[Alert]:
        """评估指标

        Args:
            metric: 指标名称
            value: 当前值
            timestamp: 时间戳

        Returns:
            触发的警报列表
        """
        import time
        if timestamp is None:
            timestamp = time.time()

        alerts = []

        for rule in self._rules:
            if rule.metric != metric:
                continue

            is_violated = rule.evaluate(value)

            if is_violated:
                # 检查持续时间要求
                if rule.sustained_seconds > 0:
                    if rule.name not in self._sustained_violations:
                        self._sustained_violations[rule.name] = timestamp
                        continue
                    elif timestamp - self._sustained_violations[rule.name] < rule.sustained_seconds:
                        continue

                # 检查冷却时间
                if rule.name in self._last_alert:
                    if timestamp - self._last_alert[rule.name] < rule.cooldown_seconds:
                        continue

                # 触发警报
                alert = Alert(
                    rule_name=rule.name,
                    metric=metric,
                    value=value,
                    level=rule.level,
                    message=f"{rule.description}: current={value:.1f}",
                    timestamp=timestamp,
                    context={"threshold": rule.threshold}
                )

                alerts.append(alert)
                self._last_alert[rule.name] = timestamp

                # 触发处理器
                for handler in self._alert_handlers:
                    try:
                        handler(alert)
                    except Exception as e:
                        logger.error(f"Alert handler error: {e}")

            else:
                # 清除持续违规记录
                if rule.name in self._sustained_violations:
                    del self._sustained_violations[rule.name]

        return alerts

    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """添加警报处理器

        Args:
            handler: 处理函数
        """
        self._alert_handlers.append(handler)

    def get_rules(self) -> List[AlertRule]:
        """获取所有规则"""
        return self._rules


class TrendDetector:
    """趋势检测器"""

    def __init__(self, window_size: int = 60,
                 cusum_threshold: float = 5.0):
        """初始化趋势检测

        Args:
            window_size: 窗口大小
            cusum_threshold: CUSUM阈值
        """
        self.window_size = window_size
        self.cusum_threshold = cusum_threshold
        self._baseline_mean = None
        self._baseline_std = None
        self._cusum_pos = 0.0
        self._cusum_neg = 0.0
        self._history: deque = deque(maxlen=window_size)

    def update(self, value: float) -> Dict:
        """更新检测器

        Args:
            value: 新数据点

        Returns:
            检测结果
        """
        self._history.append(value)

        # 如果还没有基线，使用前N个点建立基线
        if self._baseline_mean is None:
            if len(self._history) >= self.window_size:
                self._baseline_mean = np.mean(self._history)
                self._baseline_std = np.std(self._history)
            return {"status": "calibrating", "n_samples": len(self._history)}

        # CUSUM计算
        if self._baseline_std > 0:
            normalized = (value - self._baseline_mean) / self._baseline_std
            self._cusum_pos = max(0, self._cusum_pos + normalized - 0.5)
            self._cusum_neg = min(0, self._cusum_neg + normalized + 0.5)

        result = {
            "status": "monitoring",
            "value": value,
            "baseline_mean": self._baseline_mean,
            "baseline_std": self._baseline_std,
            "cusum_pos": self._cusum_pos,
            "cusum_neg": self._cusum_neg,
            "trend_detected": False,
            "trend_direction": None,
        }

        # 检测趋势
        if self._cusum_pos > self.cusum_threshold:
            result["trend_detected"] = True
            result["trend_direction"] = "increasing"
        elif abs(self._cusum_neg) > self.cusum_threshold:
            result["trend_detected"] = True
            result["trend_direction"] = "decreasing"

        return result

    def reset(self):
        """重置检测器"""
        self._baseline_mean = None
        self._baseline_std = None
        self._cusum_pos = 0.0
        self._cusum_neg = 0.0
        self._history.clear()
