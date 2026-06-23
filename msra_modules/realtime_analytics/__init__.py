"""
Real-time Analytics Module - 实时数据分析模块

提供基于Faust的实时流处理功能。
"""

from .stream_processor import StreamProcessor, SlidingWindowStats
from .anomaly_detector import AnomalyDetector, AlertRule, AlertLevel, Alert, TrendDetector
from .data_simulator import VitalSignsSimulator, VitalSigns
from .alert_system import AlertSystem, Alert as SystemAlert, AlertChannel
from .dashboard import RealtimeDashboard, ReportGenerator

__version__ = "1.1.0"
__all__ = [
    "StreamProcessor",
    "SlidingWindowStats",
    "AnomalyDetector",
    "AlertRule",
    "AlertLevel",
    "Alert",
    "TrendDetector",
    "VitalSignsSimulator",
    "VitalSigns",
    "AlertSystem",
    "SystemAlert",
    "AlertChannel",
    "RealtimeDashboard",
    "ReportGenerator",
]
