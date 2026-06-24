"""
Integration Tests - 端到端集成测试

测试完整的生物信息学分析流程：
数据加载 → QC → 质量门闸 → 差异表达 → 质量门闸
"""

import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


# 导入被测模块
import sys

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from msra_modules.bioinformatics import (
    ScRNASeqLoader,
    SingleCellQC,
    DifferentialExpression,
    DimensionalityReduction,
    PathwayEnrichment,
    BatchCorrector,
    BioQualityGateChecker,
)
from shared.quality_gates.gate_runner import GateResult, GateVerdict


def create_integration_adata(n_cells=200, n_genes=1000):
    """创建用于集成测试的 AnnData 对象"""
    try:
        import anndata
    except ImportError:
        pytest.skip("anndata not installed")

    np.random.seed(42)

    # 模拟单细胞 count 数据
    X = np.random.poisson(5, (n_cells, n_genes)).astype(float)

    # 创建带有批次效应的数据
    batch_labels = [f"batch_{i % 2}" for i in range(n_cells)]
    for i in range(n_cells):
        batch_idx = i % 2
        X[i, :100] += batch_idx * 2

    # 创建 cluster 标签
    cluster_labels = [f"cluster_{i % 4}" for i in range(n_cells)]

    obs = pd.DataFrame({
        "batch": batch_labels,
        "leiden": cluster_labels,
        "condition": ["ctrl"] * (n_cells // 2) + ["treat"] * (n_cells - n_cells // 2),
    }, index=[f"cell_{i}" for i in range(n_cells)])

    var = pd.DataFrame({
        "gene_name": [f"Gene_{i}" for i in range(n_genes)],
        "mt": [f"Gene_{i}".startswith("MT-") for i in range(n_genes)],
    }, index=[f"gene_{i}" for i in range(n_genes)])

    # 确保有一些 MT 基因
    var.loc["gene_0", "gene_name"] = "MT-CO1"
    var.loc["gene_0", "mt"] = True
    var.loc["gene_1", "gene_name"] = "MT-ND1"
    var.loc["gene_1", "mt"] = True

    adata = anndata.AnnData(X=X, obs=obs, var=var)
    return adata


class TestEndToEndBioPipeline:
    """端到端生物信息学流程测试"""

    def test_full_pipeline_data_to_gates(self):
        """测试完整流程：数据创建 → QC → Gate 1.5 → DE → Gate 3.5"""
        # Step 1: 创建数据
        adata = create_integration_adata(n_cells=200, n_genes=1000)
        assert adata.shape == (200, 1000)

        # Step 2: 样本信息
        sample_info = pd.DataFrame({
            "batch": adata.obs["batch"],
            "condition": adata.obs["condition"],
        }, index=adata.obs_names)

        # Step 3: Gate Bio-1.5 (数据质量门闸)
        checker = BioQualityGateChecker(study_id="INT-TEST-001")

        gate_15_result = checker.run_bio_gate_15(
            adata, sample_info=sample_info, batch_key="batch"
        )

        assert isinstance(gate_15_result, GateResult)
        assert gate_15_result.total_items == 5
        assert gate_15_result.verdict in [
            GateVerdict.PASS, GateVerdict.CONDITIONAL, GateVerdict.BLOCKED
        ]

        # Step 4: 模拟差异表达结果
        np.random.seed(42)
        n_de_genes = 500
        pvals = np.random.uniform(0, 1, n_de_genes)
        pvals[:50] = np.random.uniform(0, 0.001, 50)

        from scipy.stats import rankdata
        ranks = rankdata(pvals)
        padj = pvals * n_de_genes / ranks
        padj = np.minimum(padj, 1.0)

        de_results = pd.DataFrame({
            "gene": [f"Gene_{i}" for i in range(n_de_genes)],
            "log2FC": np.random.randn(n_de_genes) * 2,
            "pvals": pvals,
            "pvals_adj": padj,
        })

        # 让显著基因有更大的 fold change
        de_results.loc[:49, "log2FC"] = np.random.choice([-3, -2, 2, 3], 50)

        # Step 5: Gate Bio-3.5 (分析结果门闸)
        gate_35_result = checker.run_bio_gate_35(de_results)

        assert isinstance(gate_35_result, GateResult)
        assert gate_35_result.total_items == 5
        assert gate_35_result.verdict in [
            GateVerdict.PASS, GateVerdict.CONDITIONAL, GateVerdict.BLOCKED
        ]

    def test_pipeline_with_poor_data_quality(self):
        """测试数据质量差时门闸阻断"""
        # 创建有质量问题的数据
        adata = create_integration_adata(n_cells=200, n_genes=1000)
        adata.X[0, 0] = np.nan  # 引入 NaN

        checker = BioQualityGateChecker(study_id="INT-TEST-002")
        gate_15_result = checker.run_bio_gate_15(adata)

        # 关键项 1 应失败 → BLOCKED
        assert gate_15_result.verdict == GateVerdict.BLOCKED
        assert len(gate_15_result.risks) > 0

    def test_pipeline_with_no_correction(self):
        """测试未校正的 DE 结果被门闸拦截"""
        # 创建未校正的 DE 结果
        np.random.seed(42)
        n_genes = 200
        pvals = np.random.uniform(0, 1, n_genes)

        de_results = pd.DataFrame({
            "gene": [f"Gene_{i}" for i in range(n_genes)],
            "log2FC": np.random.randn(n_genes),
            "pvals": pvals,
            # 注意：没有 pvals_adj 列
        })

        checker = BioQualityGateChecker(study_id="INT-TEST-003")
        gate_35_result = checker.run_bio_gate_35(de_results)

        # 多重比较校正检查应失败
        assert gate_35_result.verdict == GateVerdict.BLOCKED


class TestModuleImports:
    """测试模块导入"""

    def test_import_all_classes(self):
        """测试所有类都可以正确导入"""
        assert ScRNASeqLoader is not None
        assert SingleCellQC is not None
        assert DifferentialExpression is not None
        assert DimensionalityReduction is not None
        assert PathwayEnrichment is not None
        assert BatchCorrector is not None
        assert BioQualityGateChecker is not None

    def test_version(self):
        """测试版本号"""
        from msra_modules import bioinformatics
        assert bioinformatics.__version__ == "1.1.0"

    def test_all_exports(self):
        """测试 __all__ 列表"""
        from msra_modules import bioinformatics

        expected = [
            "ScRNASeqLoader", "read_10x_mtx", "SingleCellQC",
            "DifferentialExpression", "TrajectoryAnalysis", "DimensionalityReduction",
            "CellBenderDenoiser", "BioVisualizer",
            "PathwayEnrichment", "BatchCorrector", "BioQualityGateChecker",
        ]

        for name in expected:
            assert name in bioinformatics.__all__, f"{name} not in __all__"


class TestGateRunnerIntegration:
    """测试与 GateRunner 框架的集成"""

    def test_gate_result_to_dict(self):
        """测试 GateResult 可序列化为 dict"""
        checker = BioQualityGateChecker(study_id="INT-TEST-004")
        adata = create_integration_adata(n_cells=50, n_genes=200)

        result = checker.run_bio_gate_15(adata)
        result_dict = result.to_dict()

        assert "gate_type" in result_dict
        assert "verdict" in result_dict
        assert "check_results" in result_dict
        assert isinstance(result_dict["check_results"], list)

    def test_check_item_result_fields(self):
        """测试 CheckItemResult 字段完整性"""
        checker = BioQualityGateChecker(study_id="INT-TEST-005")
        adata = create_integration_adata(n_cells=50, n_genes=200)

        result = checker._check_count_matrix_integrity(adata)

        assert hasattr(result, "item_id")
        assert hasattr(result, "name")
        assert hasattr(result, "is_key")
        assert hasattr(result, "status")
        assert hasattr(result, "evidence")
        assert hasattr(result, "notes")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
