"""
Real-time Analytics Module - 实时数据分析模块

提供实时流处理、异常检测、告警和仪表盘功能。
支持模拟器/Redis/Kafka/CSV 数据源。
"""

from .stream_processor import StreamProcessor, SlidingWindowStats
from .anomaly_detector import (
    AnomalyDetector,
    AlertRule,
    AlertLevel,
    Alert,
    TrendDetector,
    DetectionResult,
    MultivariateDetector,
)
from .data_simulator import VitalSignsSimulator, VitalSigns
from .alert_system import AlertSystem, Alert as SystemAlert, AlertChannel
from .dashboard import RealtimeDashboard, ReportGenerator
from .quality_gates import RealtimeQualityGateChecker

__version__ = "1.2.0"
__all__ = [
    "StreamProcessor",
    "SlidingWindowStats",
    "AnomalyDetector",
    "AlertRule",
    "AlertLevel",
    "Alert",
    "TrendDetector",
    "DetectionResult",
    "MultivariateDetector",
    "VitalSignsSimulator",
    "VitalSigns",
    "AlertSystem",
    "SystemAlert",
    "AlertChannel",
    "RealtimeDashboard",
    "ReportGenerator",
    "RealtimeQualityGateChecker",
]
