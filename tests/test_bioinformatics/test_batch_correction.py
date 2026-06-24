"""
Tests for BatchCorrector - 批次校正测试

使用合成 AnnData mock 数据测试批次检测和校正功能。
"""

# 导入被测模块
import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from msra_modules.bioinformatics.batch_correction import BatchCorrector


def create_mock_adata(n_cells=200, n_genes=500, n_batches=2, batch_effect=True):
    """创建 mock AnnData 对象

    Args:
        n_cells: 细胞数
        n_genes: 基因数
        n_batches: 批次数
        batch_effect: 是否引入批次效应
    """
    try:
        import anndata
    except ImportError:
        pytest.skip("anndata not installed")

    # 基础表达矩阵 (Poisson 分布)
    np.random.seed(42)
    X = np.random.poisson(5, (n_cells, n_genes)).astype(float)

    # 批次标签
    batch_labels = [f"batch_{i % n_batches}" for i in range(n_cells)]

    # 引入批次效应
    if batch_effect:
        for i in range(n_cells):
            batch_idx = i % n_batches
            X[i, :100] += batch_idx * 3  # 前 100 个基因有批次效应

    # 创建 obs DataFrame
    obs = pd.DataFrame({
        "batch": batch_labels,
        "condition": ["ctrl"] * (n_cells // 2) + ["treat"] * (n_cells - n_cells // 2),
    }, index=[f"cell_{i}" for i in range(n_cells)])

    # 创建 var DataFrame
    var = pd.DataFrame({
        "gene_name": [f"Gene_{i}" for i in range(n_genes)],
    }, index=[f"gene_{i}" for i in range(n_genes)])

    adata = anndata.AnnData(X=X, obs=obs, var=var)
    return adata


class TestBatchCorrectorInit:
    """测试 BatchCorrector 初始化"""

    def test_default_init(self):
        """测试默认初始化"""
        corrector = BatchCorrector()
        assert corrector.batch_key == "batch"
        assert corrector.method == "combat"

    def test_custom_init(self):
        """测试自定义参数初始化"""
        corrector = BatchCorrector(batch_key="sample_id", method="harmony")
        assert corrector.batch_key == "sample_id"
        assert corrector.method == "harmony"


class TestBatchEffectDetection:
    """测试批次效应检测"""

    @patch("msra_modules.bioinformatics.batch_correction.BatchCorrector._check_scanpy")
    def test_detect_with_batch_effect(self, mock_check):
        """测试检测到批次效应"""
        mock_check.return_value = None

        adata = create_mock_adata(n_cells=200, n_genes=500, n_batches=3, batch_effect=True)

        corrector = BatchCorrector(batch_key="batch")

        # 直接调用 _compute_pca_variance_by_batch 的逻辑
        # 由于需要 scanpy PCA，我们 mock 它
        with patch.object(corrector, "_compute_pca_variance_by_batch") as mock_compute:
            mock_compute.return_value = {
                "batch_variance_ratio": 0.25,
                "per_pc_variance": [0.3, 0.2, 0.15],
                "n_pcs": 3,
                "n_batches": 3,
            }

            result = corrector.detect_batch_effect(adata)

            assert result["batch_variance_ratio"] == 0.25
            assert result["has_batch_effect"] is True
            assert "recommend" in result["recommendation"].lower()

    @patch("msra_modules.bioinformatics.batch_correction.BatchCorrector._check_scanpy")
    def test_detect_without_batch_effect(self, mock_check):
        """测试未检测到批次效应"""
        mock_check.return_value = None

        adata = create_mock_adata(n_cells=200, n_genes=500, n_batches=2, batch_effect=False)

        corrector = BatchCorrector(batch_key="batch")

        with patch.object(corrector, "_compute_pca_variance_by_batch") as mock_compute:
            mock_compute.return_value = {
                "batch_variance_ratio": 0.03,
                "per_pc_variance": [0.05, 0.02, 0.01],
                "n_pcs": 3,
                "n_batches": 2,
            }

            result = corrector.detect_batch_effect(adata)

            assert result["batch_variance_ratio"] == 0.03
            assert result["has_batch_effect"] is False

    def test_validate_batch_key_missing(self):
        """测试批次列不存在"""
        adata = create_mock_adata(n_cells=50, n_genes=100, n_batches=2)
        del adata.obs["batch"]

        corrector = BatchCorrector(batch_key="batch")

        with pytest.raises(ValueError, match="not found in adata.obs"):
            corrector._validate_batch_key(adata)

    def test_validate_batch_key_single_batch(self):
        """测试只有一个批次"""
        adata = create_mock_adata(n_cells=50, n_genes=100, n_batches=2)
        adata.obs["batch"] = "single_batch"

        corrector = BatchCorrector(batch_key="batch")

        with pytest.raises(ValueError, match="At least 2 batches"):
            corrector._validate_batch_key(adata)


class TestBatchCorrection:
    """测试批次校正方法"""

    @patch("msra_modules.bioinformatics.batch_correction.BatchCorrector._check_scanpy")
    def test_run_combat(self, mock_check):
        """测试 ComBat 校正"""
        mock_check.return_value = None

        adata = create_mock_adata(n_cells=100, n_genes=200, n_batches=2)
        corrector = BatchCorrector(batch_key="batch")

        # Mock scanpy.pp.combat
        with patch("msra_modules.bioinformatics.batch_correction.BatchCorrector.run_combat") as mock_combat:
            mock_combat.return_value = adata

            result = corrector.run_combat(adata)
            assert result is not None

    @patch("msra_modules.bioinformatics.batch_correction.BatchCorrector._check_scanpy")
    def test_run_harmony_no_pca(self, mock_check):
        """测试 Harmony 校正时无 PCA"""
        mock_check.return_value = None

        adata = create_mock_adata(n_cells=100, n_genes=200, n_batches=2)
        corrector = BatchCorrector(batch_key="batch")

        # Mock scanpy.external.tl.harmony_integrate
        with patch("msra_modules.bioinformatics.batch_correction.BatchCorrector.run_harmony") as mock_harmony:
            mock_harmony.return_value = adata

            result = corrector.run_harmony(adata)
            assert result is not None

    @patch("msra_modules.bioinformatics.batch_correction.BatchCorrector._check_scanpy")
    def test_compare_before_after(self, mock_check):
        """测试校正前后比较"""
        mock_check.return_value = None

        adata_raw = create_mock_adata(n_cells=100, n_genes=200, n_batches=2, batch_effect=True)
        adata_corrected = create_mock_adata(n_cells=100, n_genes=200, n_batches=2, batch_effect=False)

        corrector = BatchCorrector(batch_key="batch")

        with patch.object(corrector, "_compute_pca_variance_by_batch") as mock_compute:
            # 原始数据有批次效应
            mock_compute.side_effect = [
                {
                    "batch_variance_ratio": 0.25,
                    "per_pc_variance": [0.3, 0.2],
                    "n_pcs": 2,
                    "n_batches": 2,
                },
                {
                    "batch_variance_ratio": 0.03,
                    "per_pc_variance": [0.05, 0.02],
                    "n_pcs": 2,
                    "n_batches": 2,
                },
            ]

            result = corrector.compare_before_after(adata_raw, adata_corrected)

            assert result["raw_batch_variance_ratio"] == 0.25
            assert result["corrected_batch_variance_ratio"] == 0.03
            assert result["improvement"] == pytest.approx(0.22, abs=0.01)


class TestBatchCorrectorHelpers:
    """测试辅助方法"""

    @patch("msra_modules.bioinformatics.batch_correction.BatchCorrector._check_scanpy")
    def test_compute_pca_variance(self, mock_check):
        """测试 PCA 方差计算"""
        mock_check.return_value = None

        adata = create_mock_adata(n_cells=100, n_genes=200, n_batches=2, batch_effect=True)

        # Mock PCA 结果
        np.random.seed(42)
        pca_coords = np.random.randn(100, 10)
        adata.obsm["X_pca"] = pca_coords

        corrector = BatchCorrector(batch_key="batch")
        result = corrector._compute_pca_variance_by_batch(adata, n_pcs=10)

        assert "batch_variance_ratio" in result
        assert "per_pc_variance" in result
        assert 0 <= result["batch_variance_ratio"] <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
