"""
test_calibration.py — calibration_runner.py 单元测试
"""
import json
import os

import numpy as np
import pandas as pd
import pytest

from shared.calibration.calibration_runner import (
    CalibrationEngine,
    CalibrationResult,
    CalibrationDatabase,
    CalibrationEntry,
    format_calibration_report,
    save_calibration_report,
)


class TestCalibrationEngine:
    """校准引擎测试"""

    def test_perfect_match(self):
        """金标准与 MSRA 完全匹配"""
        n = 10
        data = {
            "analysis_id": [f"A{i}" for i in range(n)],
            "gold_method": ["Logistic"] * n,
            "gold_estimate": [1.5] * n,
            "gold_lower": [1.0] * n,
            "gold_upper": [2.0] * n,
            "gold_p": [0.01] * n,
            "gold_significant": [True] * n,
            "msra_method": ["Logistic"] * n,
            "msra_estimate": [1.5] * n,
            "msra_lower": [1.0] * n,
            "msra_upper": [2.0] * n,
            "msra_p": [0.01] * n,
            "msra_significant": [True] * n,
        }
        gold = pd.DataFrame({k: data[k] for k in list(data.keys())[:7]})
        msra = pd.DataFrame(
            {"analysis_id": data["analysis_id"]},
        )
        for k in list(data.keys())[7:]:
            msra[k] = data[k]

        engine = CalibrationEngine(gold, msra)
        result = engine.run()

        assert result.n_total == n
        assert result.tp == n
        assert result.tn == 0
        assert result.fp == 0
        assert result.fn == 0
        assert result.sensitivity == 1.0
        assert result.accuracy == 1.0

    def test_mixed_results(self, calibration_data):
        """混合结果测试"""
        gold, msra = calibration_data
        engine = CalibrationEngine(gold, msra)
        result = engine.run()

        assert result.n_total > 0
        assert 0 <= result.sensitivity <= 1
        assert 0 <= result.specificity <= 1
        assert 0 <= result.accuracy <= 1
        assert result.mae >= 0

    def test_no_overlap_raises(self):
        """无重叠 ID 应抛出异常"""
        gold = pd.DataFrame({
            "analysis_id": ["A1"],
            "gold_method": ["t-test"],
            "gold_estimate": [1.0],
            "gold_lower": [0.5],
            "gold_upper": [1.5],
            "gold_p": [0.05],
            "gold_significant": [True],
        })
        msra = pd.DataFrame({
            "analysis_id": ["B1"],
            "msra_method": ["t-test"],
            "msra_estimate": [1.0],
            "msra_lower": [0.5],
            "msra_upper": [1.5],
            "msra_p": [0.05],
            "msra_significant": [True],
        })

        with pytest.raises(ValueError, match="No matching"):
            CalibrationEngine(gold, msra).run()

    def test_confusion_matrix(self):
        """混淆矩阵计算"""
        gold = pd.DataFrame({
            "analysis_id": ["A1", "A2", "A3", "A4"],
            "gold_method": ["t"] * 4,
            "gold_estimate": [1.0] * 4,
            "gold_lower": [0.5] * 4,
            "gold_upper": [1.5] * 4,
            "gold_p": [0.01] * 4,
            "gold_significant": [True, True, False, False],
        })
        msra = pd.DataFrame({
            "analysis_id": ["A1", "A2", "A3", "A4"],
            "msra_method": ["t"] * 4,
            "msra_estimate": [1.0] * 4,
            "msra_lower": [0.5] * 4,
            "msra_upper": [1.5] * 4,
            "msra_p": [0.01] * 4,
            "msra_significant": [True, False, True, False],
        })

        result = CalibrationEngine(gold, msra).run()
        assert result.tp == 1  # A1
        assert result.fn == 1  # A2
        assert result.fp == 1  # A3
        assert result.tn == 1  # A4


class TestFormatReport:
    """报告格式化测试"""

    def test_report_contains_key_metrics(self):
        result = CalibrationResult(
            n_total=20, tp=8, tn=8, fp=2, fn=2,
            sensitivity=0.8, specificity=0.8, accuracy=0.8,
            mae=0.05, rmse=0.07, pcc=0.95,
        )
        report = format_calibration_report(result)
        assert "灵敏度" in report
        assert "特异度" in report
        assert "MAE" in report
        assert "准确率" in report


class TestCalibrationDatabase:
    """校准数据库测试"""

    def test_record_and_retrieve(self, tmp_dir):
        db_path = os.path.join(tmp_dir, "test_db.json")
        db = CalibrationDatabase(db_path)

        db.record(
            msra_result={"method": "t-test", "estimate": 2.1, "lower": 0.5,
                         "upper": 3.7, "p": 0.02, "significant": True},
            gold_result={"analysis_id": "T1", "method": "t-test",
                         "estimate": 2.0, "lower": 0.4, "upper": 3.6,
                         "p": 0.018, "significant": True},
        )

        assert len(db.entries) == 1
        assert db.entries[0].analysis_id == "T1"

    def test_persistence(self, tmp_dir):
        db_path = os.path.join(tmp_dir, "test_db.json")

        db1 = CalibrationDatabase(db_path)
        db1.record(
            msra_result={"method": "t", "estimate": 1.0},
            gold_result={"analysis_id": "X1", "method": "t", "estimate": 1.0},
        )

        db2 = CalibrationDatabase(db_path)
        assert len(db2.entries) == 1

    def test_run_calibration(self, tmp_dir):
        db_path = os.path.join(tmp_dir, "test_db.json")
        db = CalibrationDatabase(db_path)

        for i in range(5):
            db.record(
                msra_result={"method": "t", "estimate": 2.0, "p": 0.03,
                             "significant": True},
                gold_result={"analysis_id": f"T{i}", "method": "t",
                             "estimate": 2.0, "p": 0.03, "significant": True},
            )

        result = db.run_calibration()
        assert result.n_total == 5
        assert result.accuracy == 1.0
