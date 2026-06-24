"""
Cross-domain Integration Module - 三领域交叉集成模块

提供医学影像、生物信息和实时分析的交叉集成功能。
"""

from .integration import (
    RadiomicsDEGCorrelation,
    RealtimePredictionModel,
    MultiModalVisualizer,
    DataAligner,
    export_v1_schema,
)
from .quality_gates import CrossDomainQualityGateChecker

__version__ = "1.0.0"
__all__ = [
    "RadiomicsDEGCorrelation",
    "RealtimePredictionModel",
    "MultiModalVisualizer",
    "DataAligner",
    "export_v1_schema",
    "CrossDomainQualityGateChecker",
]
