"""
Tests for Quality Metrics Store (T25.1 + T25.2)
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from shared.quality_gates.metrics_store import MetricsStore, QualityMetric
from shared.quality_gates.gate_runner import (
    GateRunner,
    GateType,
    CheckItemResult,
    RunMode,
)


class TestQualityMetric:
    """Test QualityMetric dataclass."""

    def test_create_metric(self):
        m = QualityMetric(metric_name="test", value=0.95)
        assert m.metric_name == "test"
        assert m.value == 0.95
        assert m.timestamp != ""  # auto-populated

    def test_to_dict(self):
        m = QualityMetric(metric_name="pass_rate", value=0.8, study_id="S1")
        d = m.to_dict()
        assert d["metric_name"] == "pass_rate"
        assert d["value"] == 0.8
        assert d["study_id"] == "S1"

    def test_from_dict(self):
        d = {"metric_name": "x", "value": 1.0, "timestamp": "2026-01-01T00:00:00"}
        m = QualityMetric.from_dict(d)
        assert m.metric_name == "x"
        assert m.value == 1.0


class TestMetricsStore:
    """Test MetricsStore JSONL operations."""

    @pytest.fixture
    def tmp_store(self, tmp_path):
        return MetricsStore(str(tmp_path / "test_metrics.jsonl"))

    def test_append_and_query(self, tmp_store):
        m1 = QualityMetric(metric_name="pass_rate", value=0.9, study_id="S1")
        m2 = QualityMetric(metric_name="pass_rate", value=0.85, study_id="S2")
        tmp_store.append(m1)
        tmp_store.append(m2)

        all_metrics = tmp_store.query()
        assert len(all_metrics) == 2

    def test_query_filter_study_id(self, tmp_store):
        tmp_store.append(QualityMetric(metric_name="x", value=1.0, study_id="S1"))
        tmp_store.append(QualityMetric(metric_name="x", value=2.0, study_id="S2"))

        result = tmp_store.query(study_id="S1")
        assert len(result) == 1
        assert result[0].value == 1.0

    def test_query_filter_metric_name(self, tmp_store):
        tmp_store.append(QualityMetric(metric_name="pass_rate", value=0.9, study_id="S1"))
        tmp_store.append(QualityMetric(metric_name="fail_count", value=3.0, study_id="S1"))

        result = tmp_store.query(metric_name="pass_rate")
        assert len(result) == 1

    def test_query_limit(self, tmp_store):
        for i in range(10):
            tmp_store.append(QualityMetric(metric_name="x", value=float(i)))

        result = tmp_store.query(limit=3)
        assert len(result) == 3
        assert result[0].value == 7.0  # last 3

    def test_append_many(self, tmp_store):
        metrics = [QualityMetric(metric_name="x", value=float(i)) for i in range(5)]
        tmp_store.append_many(metrics)
        assert len(tmp_store.query()) == 5

    def test_get_trend(self, tmp_store):
        for i in range(5):
            tmp_store.append(QualityMetric(
                metric_name="pass_rate", value=0.9 - i * 0.05
            ))

        trend = tmp_store.get_trend("pass_rate", last_n=3)
        assert len(trend) == 3
        assert "timestamp" in trend[0]
        assert "value" in trend[0]

    def test_detect_regression_true(self, tmp_store):
        """Regression detected when last 2 values both decline."""
        for v in [0.95, 0.85, 0.70, 0.55]:
            tmp_store.append(QualityMetric(metric_name="pass_rate", value=v))

        assert tmp_store.detect_regression("pass_rate", threshold=0.05) is True

    def test_detect_regression_false(self, tmp_path):
        """No regression when values are stable."""
        store = MetricsStore(str(tmp_path / "stable.jsonl"))
        for v in [0.9, 0.91, 0.90, 0.89]:
            store.append(QualityMetric(metric_name="pass_rate", value=v))

        assert store.detect_regression("pass_rate", threshold=0.05) is False

    def test_empty_query(self, tmp_store):
        assert tmp_store.query() == []

    def test_clear(self, tmp_store):
        tmp_store.append(QualityMetric(metric_name="x", value=1.0))
        tmp_store.clear()
        assert tmp_store.query() == []


class TestGateRunnerMetricsSink:
    """Test gate_runner metrics_sink integration."""

    @pytest.fixture
    def tmp_store(self, tmp_path):
        return MetricsStore(str(tmp_path / "gate_metrics.jsonl"))

    def test_run_gate_emits_metrics(self, tmp_store):
        """GateRunner.run_gate should emit metrics when sink is provided."""
        runner = GateRunner(study_id="TEST-001")
        check_results = [
            CheckItemResult(item_id="1", name="Test1", is_key=False, status="PASS"),
            CheckItemResult(item_id="2", name="Test2", is_key=False, status="PASS"),
            CheckItemResult(item_id="3", name="Test3", is_key=False, status="PASS"),
            CheckItemResult(item_id="4", name="Test4", is_key=False, status="PASS"),
            CheckItemResult(item_id="5", name="Test5", is_key=False, status="PASS"),
            CheckItemResult(item_id="6", name="Test6", is_key=False, status="PASS"),
            CheckItemResult(item_id="7", name="Test7", is_key=False, status="PASS"),
            CheckItemResult(item_id="8", name="Test8", is_key=False, status="PASS"),
            CheckItemResult(item_id="9", name="Test9", is_key=False, status="PASS"),
        ]

        def sink(metrics):
            tmp_store.append_many(metrics)

        result = runner.run_gate(
            GateType.DATA_QUALITY,
            artifacts={},
            mode=RunMode.SKILL,
            check_results=check_results,
            metrics_sink=sink,
        )

        assert result.verdict.value == "PASS"
        stored = tmp_store.query()
        assert len(stored) == 2  # pass_rate + failed_items
        pass_rate_metric = [m for m in stored if m.metric_name == "gate_pass_rate"][0]
        assert pass_rate_metric.value == 1.0
        assert pass_rate_metric.study_id == "TEST-001"
