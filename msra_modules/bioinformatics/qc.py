"""
Single-cell Quality Control - 单细胞质量控制

BIO-005: 单细胞QC流程
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class SingleCellQC:
    """单细胞质量控制"""

    def __init__(self,
                 min_genes: int = 200,
                 max_genes: int = 5000,
                 max_pct_mito: float = 20.0,
                 min_cells: int = 3):
        """初始化QC参数

        Args:
            min_genes: 每个细胞最少基因数
            max_genes: 每个细胞最多基因数
            max_pct_mito: 最大线粒体基因百分比
            min_cells: 每个基因最少细胞数
        """
        self.min_genes = min_genes
        self.max_genes = max_genes
        self.max_pct_mito = max_pct_mito
        self.min_cells = min_cells

    def compute_qc_metrics(self, adata):
        """计算QC指标

        Args:
            adata: AnnData对象

        Returns:
            带有QC指标的AnnData
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        # 标记线粒体基因
        adata.var['mt'] = adata.var_names.str.startswith('MT-')

        # 计算QC指标
        sc.pp.calculate_qc_metrics(
            adata,
            qc_vars=['mt'],
            percent_top=None,
            log1p=False,
            inplace=True
        )

        logger.info("QC metrics computed")
        return adata

    def filter_cells(self, adata, verbose: bool = True):
        """过滤低质量细胞

        Args:
            adata: AnnData对象
            verbose: 是否打印信息

        Returns:
            过滤后的AnnData
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        n_before = adata.shape[0]

        # 基于基因数过滤
        sc.pp.filter_cells(adata, min_genes=self.min_genes)
        sc.pp.filter_cells(adata, max_genes=self.max_genes)

        # 基于线粒体百分比过滤
        if 'pct_counts_mt' in adata.obs.columns:
            adata = adata[adata.obs['pct_counts_mt'] < self.max_pct_mito].copy()

        n_after = adata.shape[0]

        if verbose:
            logger.info(f"Filtered cells: {n_before} -> {n_after} "
                       f"(removed {n_before - n_after})")

        return adata

    def filter_genes(self, adata, verbose: bool = True):
        """过滤低表达基因

        Args:
            adata: AnnData对象
            verbose: 是否打印信息

        Returns:
            过滤后的AnnData
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        n_before = adata.shape[1]
        sc.pp.filter_genes(adata, min_cells=self.min_cells)
        n_after = adata.shape[1]

        if verbose:
            logger.info(f"Filtered genes: {n_before} -> {n_after} "
                       f"(removed {n_before - n_after})")

        return adata

    def run_qc(self, adata, verbose: bool = True):
        """运行完整QC流程

        Args:
            adata: AnnData对象
            verbose: 是否打印信息

        Returns:
            QC后的AnnData
        """
        if verbose:
            logger.info(f"Starting QC: {adata.shape[0]} cells, {adata.shape[1]} genes")

        # 1. 计算QC指标
        adata = self.compute_qc_metrics(adata)

        # 2. 过滤细胞
        adata = self.filter_cells(adata, verbose)

        # 3. 过滤基因
        adata = self.filter_genes(adata, verbose)

        if verbose:
            logger.info(f"QC complete: {adata.shape[0]} cells, {adata.shape[1]} genes")

        return adata

    def get_qc_summary(self, adata) -> Dict:
        """获取QC摘要

        Args:
            adata: AnnData对象

        Returns:
            QC摘要字典
        """
        summary = {
            "n_cells": adata.shape[0],
            "n_genes": adata.shape[1],
        }

        if 'n_genes_by_counts' in adata.obs.columns:
            summary["mean_genes_per_cell"] = float(
                adata.obs['n_genes_by_counts'].mean()
            )
            summary["median_genes_per_cell"] = float(
                adata.obs['n_genes_by_counts'].median()
            )

        if 'total_counts' in adata.obs.columns:
            summary["mean_counts_per_cell"] = float(
                adata.obs['total_counts'].mean()
            )

        if 'pct_counts_mt' in adata.obs.columns:
            summary["mean_pct_mito"] = float(
                adata.obs['pct_counts_mt'].mean()
            )
            summary["max_pct_mito"] = float(
                adata.obs['pct_counts_mt'].max()
            )

        return summary
