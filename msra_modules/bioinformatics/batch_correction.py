"""
Batch Effect Detection and Correction - 批次效应检测与校正

提供 ComBat 和 Harmony 批次校正方法，以及批次效应检测功能。
基于 scanpy 生态系统。
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class BatchCorrector:
    """批次效应检测与校正

    支持 ComBat (scanpy.pp.combat) 和 Harmony (scanpy.external.tl.harmony)。

    Usage:
        corrector = BatchCorrector(batch_key="batch")

        # 检测批次效应
        detection = corrector.detect_batch_effect(adata)

        # ComBat 校正
        adata_corrected = corrector.run_combat(adata)

        # Harmony 校正
        adata_corrected = corrector.run_harmony(adata)

        # 比较校正效果
        comparison = corrector.compare_before_after(adata_raw, adata_corrected)
    """

    def __init__(
        self,
        batch_key: str = "batch",
        method: str = "combat",
    ):
        """初始化批次校正器

        Args:
            batch_key: obs 中批次列名
            method: 默认校正方法 ("combat" 或 "harmony")
        """
        self.batch_key = batch_key
        self.method = method.lower()

    def _check_scanpy(self) -> None:
        """检查 scanpy 是否已安装"""
        try:
            import scanpy  # noqa: F401
        except ImportError:
            raise ImportError(
                "scanpy is required for batch correction. "
                "Install with: pip install scanpy"
            )

    def _validate_batch_key(self, adata) -> None:
        """验证批次列是否存在

        Args:
            adata: AnnData 对象

        Raises:
            ValueError: 批次列不存在或信息不足
        """
        if self.batch_key not in adata.obs.columns:
            raise ValueError(
                f"Batch key '{self.batch_key}' not found in adata.obs. "
                f"Available columns: {list(adata.obs.columns)}. "
                f"Please provide batch information in adata.obs."
            )

        n_batches = adata.obs[self.batch_key].nunique()
        if n_batches < 2:
            raise ValueError(
                f"Batch key '{self.batch_key}' has only {n_batches} unique value(s). "
                f"At least 2 batches are required for batch correction."
            )

    def _compute_pca_variance_by_batch(
        self,
        adata,
        n_pcs: int = 50,
    ) -> Dict[str, Any]:
        """计算 PCA 上 batch 解释的方差占比

        Args:
            adata: AnnData 对象 (需含 X_pca)
            n_pcs: PCA 主成分数

        Returns:
            字典含方差信息
        """
        import scanpy as sc

        # 确保 PCA 已计算
        if "X_pca" not in adata.obsm:
            sc.pp.pca(adata, n_comps=n_pcs)

        pca_coords = adata.obsm["X_pca"]
        batch_labels = adata.obs[self.batch_key].values

        # 计算每个 PC 上 batch 解释的方差
        pca_variances = []
        total_variance = np.var(pca_coords, axis=0).sum()

        for pc_idx in range(pca_coords.shape[1]):
            pc_values = pca_coords[:, pc_idx]
            # 计算 batch 间方差
            group_means = []
            overall_mean = np.mean(pc_values)
            for batch in np.unique(batch_labels):
                mask = batch_labels == batch
                group_mean = np.mean(pc_values[mask])
                group_means.append(group_mean)

            # Batch 解释的方差 (SS_between / SS_total)
            ss_between = sum(
                (m - overall_mean) ** 2 for m in group_means
            )
            ss_total = np.sum((pc_values - overall_mean) ** 2)

            if ss_total > 0:
                ratio = ss_between / ss_total
            else:
                ratio = 0.0

            pca_variances.append(ratio)

        # 加权平均 (按每个 PC 的总方差加权)
        pc_total_vars = np.var(pca_coords, axis=0)
        weights = pc_total_vars / pc_total_vars.sum() if pc_total_vars.sum() > 0 else np.ones(len(pc_total_vars)) / len(pc_total_vars)
        batch_variance_ratio = float(np.average(pca_variances, weights=weights))

        return {
            "batch_variance_ratio": batch_variance_ratio,
            "per_pc_variance": pca_variances,
            "n_pcs": pca_coords.shape[1],
            "n_batches": len(np.unique(batch_labels)),
        }

    def detect_batch_effect(
        self,
        adata,
        n_pcs: int = 50,
        threshold: float = 0.10,
    ) -> Dict[str, Any]:
        """检测批次效应强度

        通过 PCA 上 batch 解释的方差占比来量化。
        方差占比 > threshold 视为存在批次效应。

        Args:
            adata: AnnData 对象
            n_pcs: PCA 主成分数
            threshold: 批次效应判定阈值 (默认 10%)

        Returns:
            dict: {
                "batch_variance_ratio": float,
                "has_batch_effect": bool,
                "recommendation": str,
                "pca_variance_explained": List[float],
            }
        """
        self._check_scanpy()
        self._validate_batch_key(adata)

        result = self._compute_pca_variance_by_batch(adata, n_pcs)
        batch_var_ratio = result["batch_variance_ratio"]
        has_batch_effect = batch_var_ratio > threshold

        if has_batch_effect:
            recommendation = (
                f"Batch effect detected (variance explained: {batch_var_ratio:.1%}). "
                f"Recommend running ComBat or Harmony correction."
            )
        else:
            recommendation = (
                f"No significant batch effect detected (variance explained: {batch_var_ratio:.1%}). "
                f"Batch correction may not be necessary."
            )

        logger.info(
            f"Batch effect detection: ratio={batch_var_ratio:.3f}, "
            f"detected={has_batch_effect}"
        )

        return {
            "batch_variance_ratio": batch_var_ratio,
            "has_batch_effect": has_batch_effect,
            "recommendation": recommendation,
            "pca_variance_explained": result["per_pc_variance"],
            "n_batches": result["n_batches"],
        }

    def run_combat(
        self,
        adata,
        key: Optional[str] = None,
    ):
        """运行 ComBat 批次校正

        使用 scanpy.pp.combat，直接修改 adata.X 中的表达矩阵。

        Args:
            adata: AnnData 对象
            key: 要校正的 obs 列名 (默认使用 self.batch_key)

        Returns:
            AnnData: 校正后的数据 (原地修改 adata.X 并返回)
        """
        self._check_scanpy()
        import scanpy as sc

        batch_col = key or self.batch_key
        self._validate_batch_key(adata)

        n_cells = adata.shape[0]
        n_genes = adata.shape[1]
        n_batches = adata.obs[batch_col].nunique()

        logger.info(
            f"Running ComBat correction: {n_cells} cells, {n_genes} genes, "
            f"{n_batches} batches"
        )

        # ComBat 原地修改 adata.X
        sc.pp.combat(adata, key=batch_col)

        logger.info("ComBat correction complete")
        return adata

    def run_harmony(
        self,
        adata,
        basis: str = "X_pca",
        adjusted_basis: str = "X_pca_harmony",
    ):
        """运行 Harmony 批次校正

        使用 harmonypy，在 PCA 嵌入空间进行批次校正。

        Args:
            adata: AnnData 对象
            basis: 输入嵌入键名 (默认 "X_pca")
            adjusted_basis: 校正后的嵌入键名 (默认 "X_pca_harmony")

        Returns:
            AnnData: 校正后的数据 (新增 obsm[adjusted_basis])
        """
        self._check_scanpy()
        self._validate_batch_key(adata)

        # 确保 PCA 已计算
        if basis not in adata.obsm:
            import scanpy as sc
            sc.pp.pca(adata)

        try:
            import harmonypy
        except ImportError:
            raise ImportError(
                "harmonypy is required for Harmony correction. "
                "Install with: pip install harmonypy"
            )

        from harmonypy import run_harmony

        pca_coords = adata.obsm[basis]
        batch_labels = adata.obs[self.batch_key].values

        logger.info(
            f"Running Harmony correction: {pca_coords.shape[0]} cells, "
            f"{pca_coords.shape[1]} PCs, {len(np.unique(batch_labels))} batches"
        )

        # 运行 Harmony
        harmony_out = run_harmony(
            pca_coords,
            adata.obs,
            vars_use=[self.batch_key],
        )

        # 提取校正后的嵌入
        adata.obsm[adjusted_basis] = harmony_out.Z_corr.T

        logger.info(f"Harmony correction complete. Result stored in obsm['{adjusted_basis}']")
        return adata

    def compare_before_after(
        self,
        adata_raw,
        adata_corrected,
        n_pcs: int = 50,
    ) -> Dict[str, Any]:
        """比较校正前后效果

        Args:
            adata_raw: 校正前 AnnData
            adata_corrected: 校正后 AnnData
            n_pcs: PCA 主成分数

        Returns:
            dict: {
                "raw_batch_variance_ratio": float,
                "corrected_batch_variance_ratio": float,
                "improvement": float,
            }
        """
        self._check_scanpy()

        # 保存原始 batch_key 用于恢复
        raw_result = self._compute_pca_variance_by_batch(adata_raw, n_pcs)

        # 对校正后数据重新计算 PCA
        import scanpy as sc

        # 如果有 Harmony 校正的嵌入，使用它
        if "X_pca_harmony" in adata_corrected.obsm:
            # 临时使用 Harmony 嵌入作为 PCA
            original_pca = adata_corrected.obsm.get("X_pca_backup", None)
            adata_corrected.obsm["X_pca_backup"] = adata_corrected.obsm.get(
                "X_pca", np.array([])
            )
            adata_corrected.obsm["X_pca"] = adata_corrected.obsm["X_pca_harmony"]
        else:
            # ComBat 校正后重新计算 PCA
            sc.pp.pca(adata_corrected, n_comps=n_pcs)

        corrected_result = self._compute_pca_variance_by_batch(adata_corrected, n_pcs)

        # 恢复原始 PCA（如果使用了 Harmony）
        if "X_pca_backup" in adata_corrected.obsm:
            if original_pca is not None and len(original_pca) > 0:
                adata_corrected.obsm["X_pca"] = original_pca
            del adata_corrected.obsm["X_pca_backup"]

        raw_ratio = raw_result["batch_variance_ratio"]
        corrected_ratio = corrected_result["batch_variance_ratio"]
        improvement = raw_ratio - corrected_ratio

        logger.info(
            f"Batch correction comparison: "
            f"raw={raw_ratio:.3f}, corrected={corrected_ratio:.3f}, "
            f"improvement={improvement:.3f}"
        )

        return {
            "raw_batch_variance_ratio": raw_ratio,
            "corrected_batch_variance_ratio": corrected_ratio,
            "improvement": improvement,
            "raw_per_pc_variance": raw_result["per_pc_variance"],
            "corrected_per_pc_variance": corrected_result["per_pc_variance"],
        }
