"""
Tests for BioQualityGateChecker - 生信质量门闸测试

覆盖 Gate Bio-1.5 和 Gate Bio-3.5 的全部检查项，
测试正常路径和异常路径。
"""

import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock


# 导入被测模块
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from msra_modules.bioinformatics.quality_gates import BioQualityGateChecker
from shared.quality_gates.gate_runner import (
    GateType,
    GateResult,
    GateVerdict,
    CheckItemResult,
)


def create_mock_adata(n_cells=100, n_genes=500, with_nan=False, with_negative=False):
    """创建 mock AnnData 对象"""
    try:
        import anndata
    except ImportError:
        pytest.skip("anndata not installed")

    np.random.seed(42)
    X = np.random.poisson(5, (n_cells, n_genes)).astype(float)

    if with_nan:
        X[0, 0] = np.nan
    if with_negative:
        X[1, 1] = -1.0

    obs = pd.DataFrame({
        "batch": [f"batch_{i % 2}" for i in range(n_cells)],
        "condition": ["ctrl"] * (n_cells // 2) + ["treat"] * (n_cells - n_cells // 2),
    }, index=[f"cell_{i}" for i in range(n_cells)])

    var = pd.DataFrame({
        "gene_name": [f"Gene_{i}" for i in range(n_genes)],
    }, index=[f"gene_{i}" for i in range(n_genes)])

    adata = anndata.AnnData(X=X, obs=obs, var=var)
    return adata


def create_de_results(n_genes=500, with_padj=True):
    """创建 mock 差异表达结果"""
    np.random.seed(42)

    pvals = np.random.uniform(0, 1, n_genes)
    # 让一些 p 值很小（模拟真阳性）
    pvals[:50] = np.random.uniform(0, 0.01, 50)
    pvals = np.sort(pvals)

    log2fc = np.random.randn(n_genes)
    # 让显著基因有较大的 fold change
    log2fc[:50] = np.random.choice([-2, -1.5, 1.5, 2], 50)

    result = pd.DataFrame({
        "gene": [f"Gene_{i}" for i in range(n_genes)],
        "log2FC": log2fc,
        "pvals": pvals,
    })

    if with_padj:
        # BH 校正 (简化版)
        from scipy.stats import rankdata
        ranks = rankdata(pvals)
        padj = pvals * n_genes / ranks
        padj = np.minimum(padj, 1.0)
        result["pvals_adj"] = padj

    return result


def create_enrichment_results(n_pathways=20, with_significant=True):
    """创建 mock 通路富集结果"""
    np.random.seed(42)

    padj = np.random.uniform(0.001, 0.2, n_pathways)
    if with_significant:
        padj[:5] = np.random.uniform(0.001, 0.04, 5)

    return pd.DataFrame({
        "Term": [f"Pathway_{i}" for i in range(n_pathways)],
        "Adjusted P-value": padj,
        "Overlap": [f"{np.random.randint(5, 30)}/{np.random.randint(100, 500)}" for _ in range(n_pathways)],
    })


class TestBioQualityGateCheckerInit:
    """测试 BioQualityGateChecker 初始化"""

    def test_init(self):
        """测试初始化"""
        checker = BioQualityGateChecker(study_id="BIO-2026-001")
        assert checker.study_id == "BIO-2026-001"


class TestGateBio15:
    """测试 Gate Bio-1.5 数据质量门闸"""

    def test_check_count_matrix_integrity_pass(self):
        """测试 Count 矩阵完整性 - 通过"""
        adata = create_mock_adata(n_cells=100, n_genes=500)
        checker = BioQualityGateChecker(study_id="test")

        result = checker._check_count_matrix_integrity(adata)

        assert result.item_id == "BIO-DG-01"
        assert result.is_key is True
        assert result.status == "PASS"

    def test_check_count_matrix_integrity_fail_nan(self):
        """测试 Count 矩阵完整性 - NaN 失败"""
        adata = create_mock_adata(n_cells=100, n_genes=500, with_nan=True)
        checker = BioQualityGateChecker(study_id="test")

        result = checker._check_count_matrix_integrity(adata)

        assert result.status == "FAIL"
        assert "NaN" in result.notes

    def test_check_count_matrix_integrity_fail_negative(self):
        """测试 Count 矩阵完整性 - 负值失败"""
        adata = create_mock_adata(n_cells=100, n_genes=500, with_negative=True)
        checker = BioQualityGateChecker(study_id="test")

        result = checker._check_count_matrix_integrity(adata)

        assert result.status == "FAIL"
        assert "负值" in result.notes

    def test_check_sample_consistency_pass(self):
        """测试样本信息一致性 - 通过"""
        adata = create_mock_adata(n_cells=100, n_genes=500)
        sample_info = pd.DataFrame(
            {"batch": ["batch_0"] * 50 + ["batch_1"] * 50},
            index=[f"cell_{i}" for i in range(100)]
        )

        checker = BioQualityGateChecker(study_id="test")
        result = checker._check_sample_consistency(adata, sample_info)

        assert result.status == "PASS"

    def test_check_sample_consistency_fail(self):
        """测试样本信息一致性 - 失败"""
        adata = create_mock_adata(n_cells=100, n_genes=500)
        sample_info = pd.DataFrame(
            {"batch": ["batch_0"] * 50 + ["batch_1"] * 50},
            index=[f"cell_{i}" for i in range(50)] + [f"missing_{i}" for i in range(50)]
        )

        checker = BioQualityGateChecker(study_id="test")
        result = checker._check_sample_consistency(adata, sample_info)

        assert result.status == "FAIL"
        assert "缺失" in result.notes

    def test_check_library_size_pass(self):
        """测试文库大小合理性 - 通过"""
        adata = create_mock_adata(n_cells=100, n_genes=500)
        checker = BioQualityGateChecker(study_id="test")

        result = checker._check_library_size(adata)

        assert result.status == "PASS"
        assert "占比" in result.evidence

    def test_check_gene_annotation_pass(self):
        """测试基因注释覆盖率 - 通过"""
        adata = create_mock_adata(n_cells=100, n_genes=500)
        checker = BioQualityGateChecker(study_id="test")

        result = checker._check_gene_annotation(adata)

        assert result.status == "PASS"

    def test_check_gene_annotation_fail(self):
        """测试基因注释覆盖率 - 失败"""
        adata = create_mock_adata(n_cells=100, n_genes=500)
        # 清空大部分 gene_name
        adata.var["gene_name"] = [f"Gene_{i}" if i < 100 else "" for i in range(500)]

        checker = BioQualityGateChecker(study_id="test")
        result = checker._check_gene_annotation(adata)

        assert result.status == "FAIL"

    def test_run_bio_gate_15_pass(self):
        """测试 Gate Bio-1.5 完整执行 - 通过"""
        adata = create_mock_adata(n_cells=100, n_genes=500)
        sample_info = pd.DataFrame(
            {"batch": ["batch_0"] * 50 + ["batch_1"] * 50},
            index=[f"cell_{i}" for i in range(100)]
        )

        checker = BioQualityGateChecker(study_id="test")

        with patch.object(checker, "_check_batch_effect") as mock_batch:
            mock_batch.return_value = CheckItemResult(
                item_id="BIO-DG-05",
                name="批次效应检测",
                is_key=False,
                status="PASS",
                evidence="PCA 上 batch 方差占比=0.05",
            )

            result = checker.run_bio_gate_15(adata, sample_info, batch_key="batch")

            assert isinstance(result, GateResult)
            assert result.verdict == GateVerdict.PASS
            assert result.passed_items == 5
            assert result.failed_items == 0

    def test_run_bio_gate_15_blocked(self):
        """测试 Gate Bio-1.5 完整执行 - 阻断"""
        adata = create_mock_adata(n_cells=100, n_genes=500, with_nan=True)

        checker = BioQualityGateChecker(study_id="test")
        result = checker.run_bio_gate_15(adata)

        # NaN 会导致关键项 1 失败 → BLOCKED
        assert result.verdict == GateVerdict.BLOCKED

    def test_run_bio_gate_15_no_sample_info(self):
        """测试 Gate Bio-1.5 无样本信息"""
        adata = create_mock_adata(n_cells=100, n_genes=500)

        checker = BioQualityGateChecker(study_id="test")
        result = checker.run_bio_gate_15(adata, sample_info=None)

        # 项 2 为 N/A，其余应通过
        assert isinstance(result, GateResult)
        n_na = sum(1 for cr in result.check_results if cr.status == "N/A")
        assert n_na >= 1  # 至少 sample consistency 是 N/A


class TestGateBio35:
    """测试 Gate Bio-3.5 分析结果门闸"""

    def test_check_pvalue_distribution_pass(self):
        """测试 P 值分布合理性 - 通过"""
        pvalues = np.random.uniform(0, 1, 500)
        pvalues[:50] = np.random.uniform(0, 0.01, 50)

        checker = BioQualityGateChecker(study_id="test")
        result = checker._check_pvalue_distribution(pd.Series(pvalues))

        assert result.item_id == "BIO-RG-01"
        assert result.is_key is True
        assert result.status == "PASS"

    def test_check_pvalue_distribution_fail_range(self):
        """测试 P 值分布合理性 - 范围异常"""
        pvalues = np.random.uniform(0, 1, 500)
        pvalues[0] = -0.1  # 负值

        checker = BioQualityGateChecker(study_id="test")
        result = checker._check_pvalue_distribution(pd.Series(pvalues))

        assert result.status == "FAIL"

    def test_check_pvalue_distribution_fail_all_zero(self):
        """测试 P 值分布合理性 - 全为 0"""
        pvalues = np.zeros(100)

        checker = BioQualityGateChecker(study_id="test")
        result = checker._check_pvalue_distribution(pd.Series(pvalues))

        assert result.status == "FAIL"

    def test_check_effect_consistency_pass(self):
        """测试 log2FC 与 P 值一致性 - 通过"""
        np.random.seed(42)
        n = 500
        log2fc = np.random.randn(n)
        # 大 fold change → 小 p-value
        pvals = np.exp(-np.abs(log2fc) * 2) * np.random.uniform(0.1, 1, n)
        pvals = np.clip(pvals, 1e-300, 1)

        checker = BioQualityGateChecker(study_id="test")
        result = checker._check_effect_consistency(
            pd.Series(log2fc), pd.Series(pvals)
        )

        assert result.status == "PASS"

    def test_check_effect_consistency_fail(self):
        """测试 log2FC 与 P 值一致性 - 失败（无相关性）"""
        np.random.seed(42)
        n = 500
        log2fc = np.random.randn(n)
        pvals = np.random.uniform(0, 1, n)  # 随机 p 值，与 log2FC 无关

        checker = BioQualityGateChecker(study_id="test")
        result = checker._check_effect_consistency(
            pd.Series(log2fc), pd.Series(pvals)
        )

        # 随机数据相关性应很低
        assert result.status == "FAIL"

    def test_check_multiple_testing_pass(self):
        """测试多重比较校正 - 通过"""
        np.random.seed(42)
        n = 500
        pvals = np.random.uniform(0, 1, n)
        padj = pvals * 1.5  # 简化版 BH：padj >= pvals
        padj = np.minimum(padj, 1.0)

        checker = BioQualityGateChecker(study_id="test")
        result = checker._check_multiple_testing(
            pd.Series(pvals), pd.Series(padj)
        )

        assert result.status == "PASS"

    def test_check_multiple_testing_fail_same(self):
        """测试多重比较校正 - padj = pval"""
        np.random.seed(42)
        n = 500
        pvals = np.random.uniform(0, 1, n)
        padj = pvals.copy()  # 未校正

        checker = BioQualityGateChecker(study_id="test")
        result = checker._check_multiple_testing(
            pd.Series(pvals), pd.Series(padj)
        )

        assert result.status == "FAIL"

    def test_check_enrichment_fdr_pass(self):
        """测试通路富集 FDR - 通过"""
        enrich_df = create_enrichment_results(n_pathways=20, with_significant=True)

        checker = BioQualityGateChecker(study_id="test")
        result = checker._check_enrichment_fdr(enrich_df)

        assert result.status == "PASS"

    def test_check_enrichment_fdr_fail(self):
        """测试通路富集 FDR - 失败"""
        enrich_df = create_enrichment_results(n_pathways=20, with_significant=False)
        # 强制所有 padj > 0.05
        enrich_df["Adjusted P-value"] = np.random.uniform(0.06, 0.2, 20)

        checker = BioQualityGateChecker(study_id="test")
        result = checker._check_enrichment_fdr(enrich_df)

        assert result.status == "FAIL"

    def test_run_bio_gate_35_pass(self):
        """测试 Gate Bio-3.5 完整执行 - 通过"""
        de_results = create_de_results(n_genes=500, with_padj=True)
        enrich_df = create_enrichment_results(n_pathways=20, with_significant=True)

        checker = BioQualityGateChecker(study_id="test")
        result = checker.run_bio_gate_35(de_results, enrichment_df=enrich_df)

        assert isinstance(result, GateResult)
        assert result.verdict == GateVerdict.PASS

    def test_run_bio_gate_35_no_padj(self):
        """测试 Gate Bio-3.5 无 adjusted p-value"""
        de_results = create_de_results(n_genes=500, with_padj=False)

        checker = BioQualityGateChecker(study_id="test")
        result = checker.run_bio_gate_35(de_results)

        # 项 3 (多重比较校正) 应失败
        assert result.verdict == GateVerdict.BLOCKED

    def test_run_bio_gate_35_no_enrichment(self):
        """测试 Gate Bio-3.5 无通路富集"""
        de_results = create_de_results(n_genes=500, with_padj=True)

        checker = BioQualityGateChecker(study_id="test")
        result = checker.run_bio_gate_35(de_results, enrichment_df=None)

        # 项 4 应为 N/A，其余应通过
        n_na = sum(1 for cr in result.check_results if cr.status == "N/A")
        assert n_na >= 1


class TestGateResultBuilding:
    """测试门闸结果构建"""

    def test_build_gate_result_pass(self):
        """测试构建 PASS 结果"""
        checker = BioQualityGateChecker(study_id="test")

        check_results = [
            CheckItemResult(item_id="1", name="item1", is_key=True, status="PASS"),
            CheckItemResult(item_id="2", name="item2", is_key=False, status="PASS"),
        ]

        result = checker._build_gate_result(
            GateType.DATA_QUALITY, check_results, total_items=2
        )

        assert result.verdict == GateVerdict.PASS
        assert result.passed_items == 2
        assert result.failed_items == 0

    def test_build_gate_result_blocked_key(self):
        """测试构建 BLOCKED 结果（关键项失败）"""
        checker = BioQualityGateChecker(study_id="test")

        check_results = [
            CheckItemResult(item_id="1", name="item1", is_key=True, status="FAIL", notes="error"),
            CheckItemResult(item_id="2", name="item2", is_key=False, status="PASS"),
        ]

        result = checker._build_gate_result(
            GateType.DATA_QUALITY, check_results, total_items=2
        )

        assert result.verdict == GateVerdict.BLOCKED
        assert result.key_items_status != "all_pass"
        assert len(result.risks) > 0

    def test_build_gate_result_conditional(self):
        """测试构建 CONDITIONAL 结果"""
        checker = BioQualityGateChecker(study_id="test")

        check_results = [
            CheckItemResult(item_id="1", name="item1", is_key=True, status="PASS"),
            CheckItemResult(item_id="2", name="item2", is_key=False, status="FAIL", notes="minor issue"),
            CheckItemResult(item_id="3", name="item3", is_key=False, status="PASS"),
        ]

        result = checker._build_gate_result(
            GateType.DATA_QUALITY, check_results, total_items=3
        )

        assert result.verdict == GateVerdict.CONDITIONAL
        assert result.key_items_status == "all_pass"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
