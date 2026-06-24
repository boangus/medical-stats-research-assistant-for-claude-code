"""Unit tests for RadiomicsDEGCorrelation.

Tests: correlate() normal flow, insufficient samples, FDR correction,
heatmap generation, method switching.
"""

import numpy as np
import pandas as pd
import pytest

from msra_modules.cross_domain import RadiomicsDEGCorrelation


class TestRadiomicsDEGCorrelation:
    """RadiomicsDEGCorrelation unit tests."""

    def test_correlate_normal_flow(self, mock_radiomics_features, mock_expression_data):
        """Test 1: correlate() 正常流程 — 返回包含 correlations DataFrame 和统计量"""
        corr = RadiomicsDEGCorrelation(correlation_method="spearman")
        result = corr.correlate(mock_radiomics_features, mock_expression_data)

        # 验证返回结构
        assert "correlations" in result
        assert "n_significant" in result
        assert "n_total" in result
        assert "method" in result
        assert "samples" in result

        # 验证类型
        assert isinstance(result["correlations"], pd.DataFrame)
        assert result["method"] == "spearman"
        assert result["samples"] == 10

        # 验证总对数 = 5 features × 6 genes = 30
        assert result["n_total"] == 30

        # 验证列存在
        cols = result["correlations"].columns
        assert "feature" in cols
        assert "gene" in cols
        assert "correlation" in cols
        assert "p_value" in cols
        assert "p_adj" in cols
        assert "significant" in cols

    def test_correlate_insufficient_samples(self):
        """Test 2: 样本不足时抛出 ValueError"""
        np.random.seed(42)
        # 只有 2 个公共样本
        radiomics = pd.DataFrame(
            np.random.randn(2, 3),
            index=["S001", "S002"],
            columns=["f1", "f2", "f3"],
        )
        expression = pd.DataFrame(
            np.random.randn(2, 2),
            index=["S001", "S002"],
            columns=["G1", "G2"],
        )

        corr = RadiomicsDEGCorrelation()
        with pytest.raises(ValueError, match="Insufficient common samples"):
            corr.correlate(radiomics, expression)

    def test_fdr_correction_bonferroni(self):
        """Test 3: FDR 校正 — bonferroni 方法"""
        corr = RadiomicsDEGCorrelation(fdr_method="bonferroni")
        p_values = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
        adjusted = corr._fdr_correction(p_values)

        # Bonferroni: p_adj = p * n
        n = len(p_values)
        expected = np.clip(p_values * n, 0, 1)
        np.testing.assert_allclose(adjusted, expected)

    def test_fdr_correction_bh(self):
        """Test 4: FDR 校正 — Benjamini-Hochberg 方法"""
        corr = RadiomicsDEGCorrelation(fdr_method="bh")
        p_values = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
        adjusted = corr._fdr_correction(p_values)

        # BH 校正后值应 >= 原始 p 值
        assert np.all(adjusted >= p_values - 1e-10)
        # 最大 p 值不变
        assert adjusted[-1] == pytest.approx(p_values[-1])
        # 所有值在 [0, 1] 范围内
        assert np.all(adjusted >= 0)
        assert np.all(adjusted <= 1)

    def test_generate_heatmap_data(self, mock_radiomics_features, mock_expression_data):
        """Test 5: generate_heatmap_data — 生成热图数据结构"""
        corr = RadiomicsDEGCorrelation(correlation_method="pearson")
        result = corr.correlate(mock_radiomics_features, mock_expression_data)
        heatmap = corr.generate_heatmap_data(result["correlations"], top_n=10)

        assert "features" in heatmap
        assert "genes" in heatmap
        assert "matrix" in heatmap

        # 如果有显著结果，验证矩阵维度
        if result["n_significant"] > 0:
            n_features = len(heatmap["features"])
            n_genes = len(heatmap["genes"])
            matrix = np.array(heatmap["matrix"])
            assert matrix.shape == (n_features, n_genes)
        else:
            # 无显著结果时返回空结构
            assert heatmap["features"] == []
            assert heatmap["matrix"] == []

    def test_correlate_method_switching(self, mock_radiomics_features, mock_expression_data):
        """Test 6: 方法切换 — pearson vs spearman vs kendall"""
        for method in ["pearson", "spearman", "kendall"]:
            corr = RadiomicsDEGCorrelation(correlation_method=method)
            result = corr.correlate(mock_radiomics_features, mock_expression_data)
            assert result["method"] == method
            # 相关系数应在 [-1, 1] 范围内
            corrs = result["correlations"]["correlation"].values
            assert np.all(np.abs(corrs) <= 1.0 + 1e-10)
            # p 值应在 [0, 1] 范围内
            pvals = result["correlations"]["p_value"].values
            assert np.all(pvals >= -1e-10)
            assert np.all(pvals <= 1.0 + 1e-10)
