"""Integration tests for cross_domain module.

Tests: export_v1_schema output, file generation, schema_version verification,
end-to-end correlation analysis flow.
"""

import json
import os
import numpy as np
import pandas as pd
import pytest

from msra_modules.cross_domain import (
    RadiomicsDEGCorrelation,
    RealtimePredictionModel,
    MultiModalVisualizer,
    CrossDomainQualityGateChecker,
    DataAligner,
    export_v1_schema,
)


class TestExportV1Schema:
    """export_v1_schema integration tests."""

    def test_schema_export_with_correlation(self, mock_correlation_results, tmp_path):
        """Test 1: Schema 导出 — 关联分析结果"""
        result = export_v1_schema(
            correlation_results=mock_correlation_results,
            output_dir=str(tmp_path),
        )

        # 验证返回结构
        assert result["schema_version"] == "msra/cross_domain_result/v1"
        assert "correlation_results" in result
        assert "model_metrics" in result
        assert "visualization_bundle" in result
        assert "report" in result

        # 验证文件存在
        assert os.path.exists(result["correlation_results"])
        assert os.path.exists(result["model_metrics"])
        assert os.path.exists(result["visualization_bundle"])
        assert os.path.exists(result["report"])

        # 验证 correlation_results.csv 内容
        corr_df = pd.read_csv(result["correlation_results"])
        assert "feature" in corr_df.columns
        assert "gene" in corr_df.columns
        assert "correlation" in corr_df.columns
        assert "p_value" in corr_df.columns
        assert "p_adj" in corr_df.columns
        assert "significant" in corr_df.columns

    def test_schema_export_with_model_metrics(self, mock_model_metrics, tmp_path):
        """Test 2: Schema 导出 — 模型评估指标"""
        result = export_v1_schema(
            model_metrics=mock_model_metrics,
            output_dir=str(tmp_path),
        )

        assert result["schema_version"] == "msra/cross_domain_result/v1"

        # 验证 JSON 内容
        with open(result["model_metrics"], "r", encoding="utf-8") as f:
            metrics = json.load(f)
        assert metrics["accuracy"] == 0.85
        assert metrics["auroc"] == 0.82
        assert metrics["model_type"] == "logistic"

    def test_schema_export_empty(self, tmp_path):
        """Test 3: Schema 导出 — 无数据时仍生成空文件"""
        result = export_v1_schema(output_dir=str(tmp_path))

        assert result["schema_version"] == "msra/cross_domain_result/v1"
        assert os.path.exists(result["correlation_results"])
        assert os.path.exists(result["model_metrics"])
        assert os.path.exists(result["report"])

        # 空 JSON
        with open(result["model_metrics"], "r", encoding="utf-8") as f:
            metrics = json.load(f)
        assert metrics == {}

    def test_end_to_end_correlation_flow(
        self,
        mock_radiomics_features,
        mock_expression_data,
        tmp_path,
    ):
        """Test 4: 端到端 — 对齐 → 门闸 → 关联分析 → 导出"""
        # Step 1: 数据对齐
        aligner = DataAligner(strategy="inner")
        aligned = aligner.align({
            "radiomics": mock_radiomics_features,
            "expression": mock_expression_data,
        })

        # Step 2: Gate CD-1.5
        checker = CrossDomainQualityGateChecker(study_id="CD-E2E-001")
        gate15 = checker.run_gate_cd15(
            data_sources=aligned,
            min_samples=3,
            scenario="correlation",
        )
        assert gate15.verdict.value in ("PASS", "CONDITIONAL")

        # Step 3: 关联分析
        corr = RadiomicsDEGCorrelation(correlation_method="spearman")
        corr_result = corr.correlate(aligned["radiomics"], aligned["expression"])

        # Step 4: Gate CD-3.5
        gate35 = checker.run_gate_cd35(correlation_results=corr_result)
        assert gate35.total_items == 3

        # Step 5: 导出 Schema
        export_result = export_v1_schema(
            correlation_results=corr_result,
            output_dir=str(tmp_path / "e2e_output"),
        )
        assert export_result["schema_version"] == "msra/cross_domain_result/v1"
        assert os.path.exists(export_result["correlation_results"])
        assert os.path.exists(export_result["report"])
