"""
Quality Metrics Store — 质量指标持久化模块 (T25.1)

将门闸运行结果以 JSONL 格式追加到 quality_metrics.jsonl，
支持跨运行的指标聚合和趋势查询。

Usage:
    from shared.quality_gates.metrics_store import MetricsStore, QualityMetric
    store = MetricsStore("MSRA/quality_metrics.jsonl")
    store.append(QualityMetric(...))
    history = store.query(study_id="MSRA-2026-001")
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class QualityMetric:
    """单条质量指标记录"""
    metric_name: str       # e.g. "gate_pass_rate", "failed_items_count"
    value: float           # 指标值
    timestamp: str = ""    # ISO 8601
    data_version: str = "" # 数据集版本
    phase_id: str = ""     # e.g. "1.5", "2.5", "3.5"
    study_id: str = ""     # e.g. "MSRA-2026-001"
    gate_type: str = ""    # e.g. "data_quality", "sap_quality"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "QualityMetric":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


class MetricsStore:
    """
    JSONL-based quality metrics store.

    Appends one JSON line per metric event. Supports filtered queries.
    """

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, metric: QualityMetric) -> None:
        """Append a single metric to the JSONL file."""
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(metric.to_dict(), ensure_ascii=False) + "\n")
        logger.debug("Metric appended: %s=%s [%s]", metric.metric_name, metric.value, metric.study_id)

    def append_many(self, metrics: List[QualityMetric]) -> None:
        """Append multiple metrics in a single file operation."""
        with open(self.path, "a", encoding="utf-8") as f:
            for m in metrics:
                f.write(json.dumps(m.to_dict(), ensure_ascii=False) + "\n")
        logger.debug("%d metrics appended", len(metrics))

    def query(
        self,
        study_id: Optional[str] = None,
        metric_name: Optional[str] = None,
        gate_type: Optional[str] = None,
        phase_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[QualityMetric]:
        """Query metrics with optional filters."""
        results = []
        if not self.path.exists():
            return results

        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if study_id and d.get("study_id") != study_id:
                    continue
                if metric_name and d.get("metric_name") != metric_name:
                    continue
                if gate_type and d.get("gate_type") != gate_type:
                    continue
                if phase_id and d.get("phase_id") != phase_id:
                    continue

                results.append(QualityMetric.from_dict(d))

        if limit:
            results = results[-limit:]

        return results

    def get_trend(
        self,
        metric_name: str,
        study_id: Optional[str] = None,
        last_n: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Get trend data for a specific metric.

        Returns list of {timestamp, value} dicts, sorted by time.
        """
        metrics = self.query(study_id=study_id, metric_name=metric_name, limit=last_n)
        return [
            {"timestamp": m.timestamp, "value": m.value, "study_id": m.study_id}
            for m in metrics
        ]

    def detect_regression(
        self,
        metric_name: str,
        study_id: Optional[str] = None,
        threshold: float = 0.05,
    ) -> bool:
        """
        Detect if a metric has regressed in the last 2 measurements.

        Returns True if the metric has decreased by more than threshold
        in each of the last 2 consecutive measurements.
        """
        trend = self.get_trend(metric_name, study_id, last_n=3)
        if len(trend) < 3:
            return False

        values = [t["value"] for t in trend]
        # Check if last 2 values are both lower than their predecessor
        decline_1 = values[-2] < values[-3] - threshold
        decline_2 = values[-1] < values[-2] - threshold
        return decline_1 and decline_2

    def clear(self) -> None:
        """Clear all stored metrics (for testing)."""
        if self.path.exists():
            self.path.unlink()
