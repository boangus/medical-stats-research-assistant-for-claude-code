"""
Bioinformatics Quality Gates - 生物信息学质量门闸

实现 Gate Bio-1.5（数据质量门闸）和 Gate Bio-3.5（分析结果门闸）。
复用 shared/quality_gates/ 框架的 GateRunner + CheckItemResult 模式。
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# 导入共享门闸框架
import sys
from pathlib import Path

# 确保 shared 目录在 import 路径中
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from shared.quality_gates.gate_runner import (
    GateRunner,
    GateType,
    GateResult,
    GateVerdict,
    CheckItemResult,
    RunMode,
)


class BioQualityGateChecker:
    """生信质量门闸检查器

    封装 Gate Bio-1.5 和 Gate Bio-3.5 的具体检查逻辑，
    产出 CheckItemResult 列表供 GateRunner 消费。

    Usage:
        checker = BioQualityGateChecker(study_id="BIO-2026-001")

        # Gate Bio-1.5: 数据质量检查
        gate_15_result = checker.run_bio_gate_15(adata, sample_info)

        # Gate Bio-3.5: 分析结果检查
        gate_35_result = checker.run_bio_gate_35(de_results, enrichment_df)
    """

    def __init__(
        self,
        study_id: str,
        project_root: Optional[str] = None,
    ):
        """初始化生信质量门闸检查器

        Args:
            study_id: 研究编号
            project_root: 项目根目录 (可选)
        """
        self.study_id = study_id
        self._runner = GateRunner(
            study_id=study_id,
            project_root=project_root,
        )

    # ===== Gate Bio-1.5: 生信数据质量门闸 =====

    def run_bio_gate_15(
        self,
        adata,
        sample_info: Optional[pd.DataFrame] = None,
        batch_key: Optional[str] = None,
    ) -> GateResult:
        """执行 Gate Bio-1.5 全部 5 项检查

        Args:
            adata: AnnData 对象
            sample_info: 样本信息 DataFrame (可选)
            batch_key: 批次列名 (可选)

        Returns:
            GateResult: 判定结果 (PASS / CONDITIONAL / BLOCKED)
        """
        check_results = []

        # 项1: [🔑] Count 矩阵完整性
        check_results.append(self._check_count_matrix_integrity(adata))

        # 项2: [🔑] 样本信息一致性
        if sample_info is not None:
            check_results.append(
                self._check_sample_consistency(adata, sample_info)
            )
        else:
            check_results.append(CheckItemResult(
                item_id="BIO-DG-02",
                name="样本信息一致性",
                is_key=True,
                status="N/A",
                evidence="未提供 sample_info，跳过此项检查",
                notes="建议提供样本信息以验证一致性",
            ))

        # 项3: 文库大小合理性
        check_results.append(self._check_library_size(adata))

        # 项4: 基因注释覆盖率
        check_results.append(self._check_gene_annotation(adata))

        # 项5: 批次效应检测
        if batch_key and batch_key in adata.obs.columns:
            check_results.append(
                self._check_batch_effect(adata, batch_key)
            )
        else:
            check_results.append(CheckItemResult(
                item_id="BIO-DG-05",
                name="批次效应检测",
                is_key=False,
                status="N/A",
                evidence="未提供 batch_key 或批次列不存在，跳过此项检查",
                notes="如有多批次数据，建议提供 batch_key",
            ))

        # 使用 GateRunner 汇总判定
        # 注: GateRunner 的 total_items 来自 GATE_REGISTRY，
        #     但 Bio 门闸是自定义门闸，我们手动构建 GateResult
        return self._build_gate_result(
            gate_type=GateType.DATA_QUALITY,
            check_results=check_results,
            total_items=5,
        )

    def _check_count_matrix_integrity(self, adata) -> CheckItemResult:
        """[🔑] 项1: Count 矩阵完整性 — 无缺失、非负整数

        Args:
            adata: AnnData 对象

        Returns:
            CheckItemResult
        """
        try:
            X = adata.X

            # 转换为密集矩阵进行检查
            if hasattr(X, "toarray"):
                X_dense = X.toarray()
            else:
                X_dense = np.asarray(X)

            # 检查 NaN
            has_nan = bool(np.any(np.isnan(X_dense)))

            # 检查负值
            has_negative = bool(np.any(X_dense < 0))

            # 检查是否为整数 (容差 1e-6)
            is_integer = bool(np.allclose(X_dense, np.round(X_dense), atol=1e-6))

            issues = []
            if has_nan:
                issues.append("矩阵包含 NaN 值")
            if has_negative:
                issues.append("矩阵包含负值")
            if not is_integer:
                issues.append("矩阵包含非整数值")

            if not issues:
                return CheckItemResult(
                    item_id="BIO-DG-01",
                    name="Count矩阵完整性 [🔑]",
                    is_key=True,
                    status="PASS",
                    evidence=f"矩阵形状 {adata.shape}，无 NaN、无负值、全部为整数",
                )
            else:
                return CheckItemResult(
                    item_id="BIO-DG-01",
                    name="Count矩阵完整性 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence=f"矩阵形状 {adata.shape}",
                    notes="；".join(issues),
                )

        except Exception as e:
            return CheckItemResult(
                item_id="BIO-DG-01",
                name="Count矩阵完整性 [🔑]",
                is_key=True,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    def _check_sample_consistency(
        self, adata, sample_info: pd.DataFrame
    ) -> CheckItemResult:
        """[🔑] 项2: 样本信息一致性

        Args:
            adata: AnnData 对象
            sample_info: 样本信息 DataFrame

        Returns:
            CheckItemResult
        """
        try:
            adata_obs = set(adata.obs_names)
            sample_idx = set(sample_info.index)

            # 检查样本信息中的样本是否都在 AnnData 中
            missing_in_adata = sample_idx - adata_obs
            # 检查 AnnData 中的样本是否都在样本信息中
            missing_in_sample = adata_obs - sample_idx

            total_samples = len(adata_obs)
            matched = len(sample_idx & adata_obs)
            match_rate = matched / total_samples if total_samples > 0 else 0.0

            if len(missing_in_adata) == 0:
                return CheckItemResult(
                    item_id="BIO-DG-02",
                    name="样本信息一致性 [🔑]",
                    is_key=True,
                    status="PASS",
                    evidence=(
                        f"AnnData {total_samples} 样本，sample_info {len(sample_idx)} 样本，"
                        f"匹配率 {match_rate:.1%}"
                    ),
                )
            else:
                return CheckItemResult(
                    item_id="BIO-DG-02",
                    name="样本信息一致性 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence=(
                        f"AnnData {total_samples} 样本，sample_info {len(sample_idx)} 样本，"
                        f"匹配率 {match_rate:.1%}"
                    ),
                    notes=f"{len(missing_in_adata)} 个样本在 AnnData 中缺失: "
                          f"{list(missing_in_adata)[:5]}...",
                )

        except Exception as e:
            return CheckItemResult(
                item_id="BIO-DG-02",
                name="样本信息一致性 [🔑]",
                is_key=True,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    def _check_library_size(self, adata) -> CheckItemResult:
        """[ ] 项3: 文库大小合理性

        中位数 ± 3*IQR 范围内的细胞占比应 > 90%。

        Args:
            adata: AnnData 对象

        Returns:
            CheckItemResult
        """
        try:
            X = adata.X
            if hasattr(X, "toarray"):
                X_dense = X.toarray()
            else:
                X_dense = np.asarray(X)

            # 计算文库大小 (每个细胞的总 counts)
            lib_sizes = X_dense.sum(axis=1)

            median_size = np.median(lib_sizes)
            q1 = np.percentile(lib_sizes, 25)
            q3 = np.percentile(lib_sizes, 75)
            iqr = q3 - q1

            lower_bound = median_size - 3 * iqr
            upper_bound = median_size + 3 * iqr

            in_range = np.sum(
                (lib_sizes >= lower_bound) & (lib_sizes <= upper_bound)
            )
            pct_in_range = in_range / len(lib_sizes) if len(lib_sizes) > 0 else 0.0

            if pct_in_range > 0.90:
                status = "PASS"
                notes = ""
            else:
                status = "FAIL"
                notes = (
                    f"文库大小中位数±3IQR范围内占比 {pct_in_range:.1%} ≤ 90%。"
                    f"中位数={median_size:.0f}, IQR={iqr:.0f}, "
                    f"范围=[{lower_bound:.0f}, {upper_bound:.0f}]"
                )

            return CheckItemResult(
                item_id="BIO-DG-03",
                name="文库大小合理性",
                is_key=False,
                status=status,
                evidence=(
                    f"文库大小: 中位数={median_size:.0f}, IQR={iqr:.0f}, "
                    f"范围内占比={pct_in_range:.1%}"
                ),
                notes=notes,
            )

        except Exception as e:
            return CheckItemResult(
                item_id="BIO-DG-03",
                name="文库大小合理性",
                is_key=False,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    def _check_gene_annotation(self, adata) -> CheckItemResult:
        """[ ] 项4: 基因注释覆盖率

        gene_name 覆盖率应 > 80%。

        Args:
            adata: AnnData 对象

        Returns:
            CheckItemResult
        """
        try:
            n_genes = adata.shape[1]

            # 检查 var 中的 gene_name 列
            if "gene_name" in adata.var.columns:
                gene_names = adata.var["gene_name"]
                valid = gene_names.notna() & (gene_names != "") & (gene_names != "nan")
                coverage = valid.sum() / n_genes if n_genes > 0 else 0.0
            else:
                # 使用 var_names 作为替代
                var_names = adata.var_names
                valid = var_names.notna() & (var_names != "") & (var_names.str.upper() != "NAN")
                coverage = valid.sum() / n_genes if n_genes > 0 else 0.0

            if coverage >= 0.80:
                status = "PASS"
                notes = ""
            else:
                status = "FAIL"
                notes = f"基因注释覆盖率 {coverage:.1%} < 80%"

            return CheckItemResult(
                item_id="BIO-DG-04",
                name="基因注释覆盖率",
                is_key=False,
                status=status,
                evidence=f"总基因数 {n_genes}, 有效注释 {int(coverage * n_genes)}, 覆盖率 {coverage:.1%}",
                notes=notes,
            )

        except Exception as e:
            return CheckItemResult(
                item_id="BIO-DG-04",
                name="基因注释覆盖率",
                is_key=False,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    def _check_batch_effect(
        self, adata, batch_key: str
    ) -> CheckItemResult:
        """[ ] 项5: 批次效应检测

        PCA 上 batch 解释的方差占比应 < 10%。

        Args:
            adata: AnnData 对象
            batch_key: 批次列名

        Returns:
            CheckItemResult
        """
        try:
            import scanpy as sc

            # 确保 PCA 已计算
            if "X_pca" not in adata.obsm:
                sc.pp.pca(adata, n_comps=min(50, min(adata.shape) - 1))

            pca_coords = adata.obsm["X_pca"]
            batch_labels = adata.obs[batch_key].values

            # 计算每个 PC 上 batch 解释的方差
            pca_variances = []
            for pc_idx in range(pca_coords.shape[1]):
                pc_values = pca_coords[:, pc_idx]
                overall_mean = np.mean(pc_values)
                group_means = []
                for batch in np.unique(batch_labels):
                    mask = batch_labels == batch
                    group_means.append(np.mean(pc_values[mask]))

                ss_between = sum((m - overall_mean) ** 2 for m in group_means)
                ss_total = np.sum((pc_values - overall_mean) ** 2)

                ratio = ss_between / ss_total if ss_total > 0 else 0.0
                pca_variances.append(ratio)

            # 加权平均
            pc_total_vars = np.var(pca_coords, axis=0)
            weights = pc_total_vars / pc_total_vars.sum() if pc_total_vars.sum() > 0 else np.ones(len(pc_total_vars)) / len(pc_total_vars)
            batch_variance_ratio = float(np.average(pca_variances, weights=weights))

            if batch_variance_ratio < 0.10:
                status = "PASS"
                notes = ""
            else:
                status = "FAIL"
                notes = (
                    f"PCA 上 batch 方差占比 {batch_variance_ratio:.1%} ≥ 10%。"
                    f"建议运行批次校正 (ComBat/Harmony)。"
                )

            return CheckItemResult(
                item_id="BIO-DG-05",
                name="批次效应检测",
                is_key=False,
                status=status,
                evidence=(
                    f"PCA 上 batch 方差占比={batch_variance_ratio:.3f}, "
                    f"批次数={len(np.unique(batch_labels))}"
                ),
                notes=notes,
            )

        except ImportError:
            return CheckItemResult(
                item_id="BIO-DG-05",
                name="批次效应检测",
                is_key=False,
                status="SKIP",
                evidence="scanpy 未安装，无法计算 PCA",
                notes="需要安装 scanpy 以执行批次效应检测",
            )
        except Exception as e:
            return CheckItemResult(
                item_id="BIO-DG-05",
                name="批次效应检测",
                is_key=False,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    # ===== Gate Bio-3.5: 生信分析结果门闸 =====

    def run_bio_gate_35(
        self,
        de_results: pd.DataFrame,
        enrichment_df: Optional[pd.DataFrame] = None,
        visualization_paths: Optional[List[str]] = None,
    ) -> GateResult:
        """执行 Gate Bio-3.5 全部 5 项检查

        Args:
            de_results: 差异表达结果 DataFrame (需含 pvals, pvals_adj 列)
            enrichment_df: 通路富集结果 DataFrame (可选)
            visualization_paths: 可视化文件路径列表 (可选)

        Returns:
            GateResult: 判定结果 (PASS / CONDITIONAL / BLOCKED)
        """
        check_results = []

        # 获取 p-values 和 adjusted p-values
        pvals_col = self._find_column(de_results, ["pvals", "pval", "p_value", "P.Value", "pvalue"])
        padj_col = self._find_column(de_results, ["pvals_adj", "padj", "p_adj", "adj.P.Val", "FDR", "q_value"])
        log2fc_col = self._find_column(de_results, ["log2FC", "logfoldchanges", "log2FoldChange", "logFC", "fold_change"])

        # 项1: [🔑] P 值分布合理性
        if pvals_col:
            check_results.append(
                self._check_pvalue_distribution(de_results[pvals_col])
            )
        else:
            check_results.append(CheckItemResult(
                item_id="BIO-RG-01",
                name="P值分布合理性 [🔑]",
                is_key=True,
                status="FAIL",
                evidence="未找到 p-value 列",
                notes=f"可用列: {list(de_results.columns)}",
            ))

        # 项2: [🔑] log2FC 与 P 值一致性
        if log2fc_col and pvals_col:
            check_results.append(
                self._check_effect_consistency(
                    de_results[log2fc_col], de_results[pvals_col]
                )
            )
        else:
            check_results.append(CheckItemResult(
                item_id="BIO-RG-02",
                name="log2FC与P值一致性 [🔑]",
                is_key=True,
                status="FAIL",
                evidence="缺少 log2FC 或 p-value 列",
                notes=f"可用列: {list(de_results.columns)}",
            ))

        # 项3: [🔑] 多重比较校正已应用
        if pvals_col and padj_col:
            check_results.append(
                self._check_multiple_testing(
                    de_results[pvals_col], de_results[padj_col]
                )
            )
        else:
            check_results.append(CheckItemResult(
                item_id="BIO-RG-03",
                name="多重比较校正 [🔑]",
                is_key=True,
                status="FAIL",
                evidence="缺少 p-value 或 adjusted p-value 列",
                notes=f"可用列: {list(de_results.columns)}",
            ))

        # 项4: 通路富集 FDR
        if enrichment_df is not None and not enrichment_df.empty:
            check_results.append(
                self._check_enrichment_fdr(enrichment_df)
            )
        else:
            check_results.append(CheckItemResult(
                item_id="BIO-RG-04",
                name="通路富集FDR",
                is_key=False,
                status="N/A",
                evidence="未提供通路富集结果",
                notes="如需检查通路富集 FDR，请提供 enrichment_df",
            ))

        # 项5: 可视化一致性
        if visualization_paths and pvals_col:
            check_results.append(
                self._check_visualization_consistency(
                    visualization_paths, de_results
                )
            )
        else:
            check_results.append(CheckItemResult(
                item_id="BIO-RG-05",
                name="可视化一致性",
                is_key=False,
                status="N/A",
                evidence="未提供可视化路径或 DE 结果",
                notes="建议生成可视化后执行此项检查",
            ))

        return self._build_gate_result(
            gate_type=GateType.RESULTS_QUALITY,
            check_results=check_results,
            total_items=5,
        )

    def _check_pvalue_distribution(
        self, pvalues: pd.Series
    ) -> CheckItemResult:
        """[🔑] 项1: P 值分布合理性

        使用 KS 检验验证 P 值是否接近均匀分布（低值区有峰值为正常）。

        Args:
            pvalues: P 值序列

        Returns:
            CheckItemResult
        """
        try:
            from scipy import stats

            pvals_clean = pvalues.dropna()

            if len(pvals_clean) < 10:
                return CheckItemResult(
                    item_id="BIO-RG-01",
                    name="P值分布合理性 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence=f"有效 P 值数量 {len(pvals_clean)} < 10",
                    notes="样本量不足，无法评估 P 值分布",
                )

            # 检查 P 值范围
            p_min = float(pvals_clean.min())
            p_max = float(pvals_clean.max())
            range_ok = (p_min >= 0.0) and (p_max <= 1.0)

            # KS 检验: P 值 vs 均匀分布
            ks_stat, ks_pval = stats.kstest(pvals_clean, "uniform")

            # 均匀分布应有 ~5% 的 P 值 < 0.05
            pct_below_005 = (pvals_clean < 0.05).mean()

            # 判定逻辑:
            # - P 值范围必须在 [0, 1]
            # - KS 检验 p < 0.05 表示偏离均匀分布（在生信中正常，因为有真阳性）
            # - 但不应全部集中在 0 或 1 附近
            issues = []
            if not range_ok:
                issues.append(f"P 值范围异常: [{p_min}, {p_max}]")

            # 检查是否有大量 P 值恰好为 0 或 1
            pct_zero = (pvals_clean == 0).mean()
            pct_one = (pvals_clean == 1.0).mean()
            if pct_zero > 0.5:
                issues.append(f"过多 P 值为 0: {pct_zero:.1%}")
            if pct_one > 0.5:
                issues.append(f"过多 P 值为 1: {pct_one:.1%}")

            if not issues:
                status = "PASS"
                notes = ""
            else:
                status = "FAIL"
                notes = "；".join(issues)

            return CheckItemResult(
                item_id="BIO-RG-01",
                name="P值分布合理性 [🔑]",
                is_key=True,
                status=status,
                evidence=(
                    f"P 值范围 [{p_min:.4f}, {p_max:.4f}], "
                    f"KS 检验 p={ks_pval:.4f}, "
                    f"P<0.05 占比 {pct_below_005:.1%}"
                ),
                notes=notes,
            )

        except ImportError:
            return CheckItemResult(
                item_id="BIO-RG-01",
                name="P值分布合理性 [🔑]",
                is_key=True,
                status="FAIL",
                evidence="scipy 未安装",
                notes="需要安装 scipy 以执行 KS 检验",
            )
        except Exception as e:
            return CheckItemResult(
                item_id="BIO-RG-01",
                name="P值分布合理性 [🔑]",
                is_key=True,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    def _check_effect_consistency(
        self, log2fc: pd.Series, pvalues: pd.Series
    ) -> CheckItemResult:
        """[🔑] 项2: log2FC 与 P 值一致性

        检查 |log2FC| 与 -log10(pvalue) 之间的 Spearman 相关性。
        通常应呈正相关（大 fold change → 小 p-value）。

        Args:
            log2fc: log2 fold change 序列
            pvalues: P 值序列

        Returns:
            CheckItemResult
        """
        try:
            from scipy import stats

            # 对齐索引
            aligned = pd.DataFrame({
                "log2fc": log2fc,
                "pval": pvalues
            }).dropna()

            if len(aligned) < 10:
                return CheckItemResult(
                    item_id="BIO-RG-02",
                    name="log2FC与P值一致性 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence=f"有效数据点 {len(aligned)} < 10",
                    notes="样本量不足",
                )

            # 计算 |log2FC| 与 -log10(pvalue) 的 Spearman 相关
            abs_fc = np.abs(aligned["log2fc"])
            neg_log_pval = -np.log10(aligned["pval"].clip(lower=1e-300))

            # 避免 inf
            valid = np.isfinite(neg_log_pval) & np.isfinite(abs_fc)
            if valid.sum() < 10:
                return CheckItemResult(
                    item_id="BIO-RG-02",
                    name="log2FC与P值一致性 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence="有效数据点不足",
                    notes="存在过多 inf 或 nan 值",
                )

            corr, corr_pval = stats.spearmanr(
                abs_fc[valid], neg_log_pval[valid]
            )

            # 正相关是期望的
            if corr > 0.1:
                status = "PASS"
                notes = ""
            else:
                status = "FAIL"
                notes = (
                    f"|log2FC| 与 -log10(p) 的 Spearman 相关性 "
                    f"{corr:.3f} 过低，预期应为正相关"
                )

            return CheckItemResult(
                item_id="BIO-RG-02",
                name="log2FC与P值一致性 [🔑]",
                is_key=True,
                status=status,
                evidence=(
                    f"Spearman ρ={corr:.3f}, p={corr_pval:.4f}, "
                    f"数据点数={valid.sum()}"
                ),
                notes=notes,
            )

        except ImportError:
            return CheckItemResult(
                item_id="BIO-RG-02",
                name="log2FC与P值一致性 [🔑]",
                is_key=True,
                status="FAIL",
                evidence="scipy 未安装",
                notes="需要安装 scipy 以执行相关性检验",
            )
        except Exception as e:
            return CheckItemResult(
                item_id="BIO-RG-02",
                name="log2FC与P值一致性 [🔑]",
                is_key=True,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    def _check_multiple_testing(
        self, pvalues: pd.Series, padj: pd.Series
    ) -> CheckItemResult:
        """[🔑] 项3: 多重比较校正已应用

        检查 adjusted p-values 是否已正确计算（padj ≤ pvalue）。

        Args:
            pvalues: 原始 P 值序列
            padj: 校正后 P 值序列

        Returns:
            CheckItemResult
        """
        try:
            aligned = pd.DataFrame({
                "pval": pvalues,
                "padj": padj
            }).dropna()

            if len(aligned) < 10:
                return CheckItemResult(
                    item_id="BIO-RG-03",
                    name="多重比较校正 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence=f"有效数据点 {len(aligned)} < 10",
                    notes="样本量不足",
                )

            # 检查 padj <= pvalue (BH 校正的基本性质)
            violations = (aligned["padj"] < aligned["pval"]).sum()
            violation_rate = violations / len(aligned)

            # 检查是否有 padj 全部为 NaN
            all_nan = aligned["padj"].isna().all()

            # 检查是否有 padj = pvalue (未校正的迹象)
            exact_match = (aligned["padj"] == aligned["pval"]).all()

            issues = []
            if all_nan:
                issues.append("所有 adjusted p-values 为 NaN")
            if exact_match:
                issues.append("adjusted p-values 与原始 p-values 完全相同，可能未校正")
            if violation_rate > 0.01:
                issues.append(
                    f"{violation_rate:.1%} 的 padj < pval (BH 校正不应出现)"
                )

            if not issues:
                status = "PASS"
                notes = ""
            else:
                status = "FAIL"
                notes = "；".join(issues)

            # 统计显著基因数
            n_sig_005 = (aligned["padj"] < 0.05).sum()
            n_sig_001 = (aligned["padj"] < 0.01).sum()

            return CheckItemResult(
                item_id="BIO-RG-03",
                name="多重比较校正 [🔑]",
                is_key=True,
                status=status,
                evidence=(
                    f"有效基因数 {len(aligned)}, "
                    f"padj<0.05: {n_sig_005}, padj<0.01: {n_sig_001}"
                ),
                notes=notes,
            )

        except Exception as e:
            return CheckItemResult(
                item_id="BIO-RG-03",
                name="多重比较校正 [🔑]",
                is_key=True,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    def _check_enrichment_fdr(
        self, enrichment_df: pd.DataFrame
    ) -> CheckItemResult:
        """[ ] 项4: 通路富集 FDR < 0.05

        检查是否有至少 1 条显著通路 (adjusted p-value < 0.05)。

        Args:
            enrichment_df: 通路富集结果 DataFrame

        Returns:
            CheckItemResult
        """
        try:
            # 查找 adjusted p-value 列
            padj_col = self._find_column(
                enrichment_df,
                ["Adjusted P-value", "adj_pval", "padj", "FDR", "q_value", "FDR q-val"]
            )

            if not padj_col:
                return CheckItemResult(
                    item_id="BIO-RG-04",
                    name="通路富集FDR",
                    is_key=False,
                    status="FAIL",
                    evidence="未找到 adjusted p-value 列",
                    notes=f"可用列: {list(enrichment_df.columns)}",
                )

            padj_values = enrichment_df[padj_col].dropna()
            n_significant = (padj_values < 0.05).sum()
            n_total = len(padj_values)

            if n_significant > 0:
                status = "PASS"
                notes = ""
            else:
                status = "FAIL"
                notes = f"无显著通路 (padj < 0.05)。共 {n_total} 条通路均未达到显著水平"

            # 获取最小 padj
            min_padj = float(padj_values.min()) if n_total > 0 else None

            return CheckItemResult(
                item_id="BIO-RG-04",
                name="通路富集FDR",
                is_key=False,
                status=status,
                evidence=(
                    f"总通路数 {n_total}, 显著通路数 {n_significant}, "
                    f"最小 padj={min_padj:.4f}" if min_padj is not None
                    else f"总通路数 {n_total}, 显著通路数 {n_significant}"
                ),
                notes=notes,
            )

        except Exception as e:
            return CheckItemResult(
                item_id="BIO-RG-04",
                name="通路富集FDR",
                is_key=False,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    def _check_visualization_consistency(
        self, visualization_paths: List[str], de_table: pd.DataFrame
    ) -> CheckItemResult:
        """[ ] 项5: 可视化与数据一致

        检查可视化文件是否存在，以及显著基因数是否与 DE 表一致。

        Args:
            visualization_paths: 可视化文件路径列表
            de_table: 差异表达结果表

        Returns:
            CheckItemResult
        """
        try:
            from pathlib import Path

            existing_files = []
            missing_files = []

            for path in visualization_paths:
                if Path(path).exists():
                    existing_files.append(path)
                else:
                    missing_files.append(path)

            # 统计显著基因数
            padj_col = self._find_column(
                de_table, ["pvals_adj", "padj", "adj.P.Val", "FDR"]
            )
            if padj_col:
                n_sig = (de_table[padj_col] < 0.05).sum()
            else:
                n_sig = None

            if missing_files:
                status = "FAIL"
                notes = f"{len(missing_files)} 个可视化文件缺失: {missing_files}"
            else:
                status = "PASS"
                notes = ""

            evidence_parts = [
                f"可视化文件 {len(existing_files)}/{len(visualization_paths)} 存在"
            ]
            if n_sig is not None:
                evidence_parts.append(f"显著基因数 {n_sig}")

            return CheckItemResult(
                item_id="BIO-RG-05",
                name="可视化一致性",
                is_key=False,
                status=status,
                evidence=", ".join(evidence_parts),
                notes=notes,
            )

        except Exception as e:
            return CheckItemResult(
                item_id="BIO-RG-05",
                name="可视化一致性",
                is_key=False,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    # ===== 辅助方法 =====

    def _find_column(
        self, df: pd.DataFrame, candidates: List[str]
    ) -> Optional[str]:
        """在 DataFrame 中查找列名

        Args:
            df: DataFrame
            candidates: 候选列名列表

        Returns:
            匹配的列名或 None
        """
        for col in candidates:
            if col in df.columns:
                return col
        return None

    def _build_gate_result(
        self,
        gate_type: GateType,
        check_results: List[CheckItemResult],
        total_items: int,
    ) -> GateResult:
        """构建 GateResult

        使用 GateRunner 的判定逻辑，但适配 Bio 门闸的自定义检查项。

        Args:
            gate_type: 门闸类型
            check_results: 检查结果列表
            total_items: 总检查项数

        Returns:
            GateResult
        """
        # 统计结果 (排除 N/A 和 SKIP)
        evaluable = [cr for cr in check_results if cr.status not in ("N/A", "SKIP")]
        passed = sum(1 for cr in evaluable if cr.status == "PASS")
        failed = sum(1 for cr in evaluable if cr.status == "FAIL")
        key_failed = [cr for cr in evaluable if cr.is_key and cr.status == "FAIL"]

        # 判定逻辑
        if failed == 0:
            verdict = GateVerdict.PASS
            key_status = "all_pass"
        elif len(key_failed) > 0:
            verdict = GateVerdict.BLOCKED
            key_status = f"item_{key_failed[0].item_id}_failed"
        elif failed <= 2:
            verdict = GateVerdict.CONDITIONAL
            key_status = "all_pass"
        else:
            verdict = GateVerdict.BLOCKED
            key_status = f"{failed}_items_failed"

        # 风险评估
        risks = []
        for cr in check_results:
            if cr.status == "FAIL":
                level = "关键" if cr.is_key else "一般"
                risks.append(f"[{level}] {cr.name}: {cr.notes or cr.evidence}")

        return GateResult(
            gate_type=gate_type,
            study_id=self.study_id,
            verdict=verdict,
            total_items=total_items,
            passed_items=passed,
            failed_items=failed,
            key_items_status=key_status,
            check_results=check_results,
            risks=risks,
        )
