"""
Differential Expression and Trajectory Analysis - 差异表达与轨迹分析

BIO-006: 降维与聚类
BIO-007: 差异表达分析
BIO-009: 轨迹分析
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class DimensionalityReduction:
    """降维分析"""

    def __init__(self, n_pcs: int = 50, n_neighbors: int = 15):
        """初始化降维参数

        Args:
            n_pcs: PCA主成分数
            n_neighbors: 邻居数
        """
        self.n_pcs = n_pcs
        self.n_neighbors = n_neighbors

    def normalize_and_log(self, adata, target_sum: int = 1e4):
        """标准化和对数转换

        Args:
            adata: AnnData对象
            target_sum: 目标总和

        Returns:
            标准化后的AnnData
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        sc.pp.normalize_total(adata, target_sum=target_sum)
        sc.pp.log1p(adata)
        logger.info("Normalized and log-transformed")
        return adata

    def find_hvg(self, adata, n_top_genes: int = 2000):
        """寻找高变基因

        Args:
            adata: AnnData对象
            n_top_genes: 高变基因数

        Returns:
            带有高变基因标记的AnnData
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        sc.pp.highly_variable_genes(adata, n_top_genes=n_top_genes)
        logger.info(f"Found {n_top_genes} highly variable genes")
        return adata

    def run_pca(self, adata):
        """运行PCA

        Args:
            adata: AnnData对象

        Returns:
            带有PCA结果的AnnData
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        sc.pp.pca(adata, n_comps=self.n_pcs)
        logger.info(f"PCA complete with {self.n_pcs} components")
        return adata

    def run_umap(self, adata):
        """运行UMAP

        Args:
            adata: AnnData对象

        Returns:
            带有UMAP结果的AnnData
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        sc.pp.neighbors(adata, n_neighbors=self.n_neighbors, n_pcs=self.n_pcs)
        sc.tl.umap(adata)
        logger.info("UMAP complete")
        return adata

    def cluster(self, adata, resolution: float = 1.0):
        """聚类分析

        Args:
            adata: AnnData对象
            resolution: 聚类分辨率

        Returns:
            带有聚类结果的AnnData
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        sc.tl.leiden(adata, resolution=resolution)
        logger.info(f"Leiden clustering complete (resolution={resolution})")
        return adata

    def run_full_pipeline(self, adata, resolution: float = 1.0):
        """运行完整降维聚类pipeline

        Args:
            adata: AnnData对象
            resolution: 聚类分辨率

        Returns:
            处理后的AnnData
        """
        adata = self.normalize_and_log(adata)
        adata = self.find_hvg(adata)
        adata = self.run_pca(adata)
        adata = self.run_umap(adata)
        adata = self.cluster(adata, resolution=resolution)
        logger.info("Full dimensionality reduction pipeline complete")
        return adata


class DifferentialExpression:
    """差异表达分析"""

    def __init__(self, method: str = "wilcoxon"):
        """初始化差异分析

        Args:
            method: 差异分析方法 ("wilcoxon", "t-test", "logreg")
        """
        self.method = method

    def find_markers(self, adata, groupby: str = "leiden",
                     use_raw: bool = True):
        """寻找标记基因

        Args:
            adata: AnnData对象
            groupby: 分组列名
            use_raw: 是否使用原始数据

        Returns:
            标记基因DataFrame
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        sc.tl.rank_genes_groups(
            adata,
            groupby=groupby,
            method=self.method,
            use_raw=use_raw
        )

        # 获取结果
        result = adata.uns['rank_genes_groups']
        markers = pd.DataFrame({
            group: result['names'][group]
            for group in result['names'].dtype.names
        })

        logger.info(f"Found markers for {len(markers.columns)} groups")
        return markers

    def get_de_table(self, adata, group: str, n_genes: int = 100) -> pd.DataFrame:
        """获取差异表达表格

        Args:
            adata: AnnData对象
            group: 分组名
            n_genes: 返回的基因数

        Returns:
            差异表达表格
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        result = sc.get.rank_genes_groups_df(adata, group=group)

        # 添加log2FC
        if 'logfoldchanges' in result.columns:
            result['log2FC'] = result['logfoldchanges']

        # 按p值排序
        result = result.sort_values('pvals_adj')
        result = result.head(n_genes)

        logger.info(f"Got {len(result)} DE genes for group {group}")
        return result

    def filter_de_genes(self, de_table: pd.DataFrame,
                        log2fc_threshold: float = 1.0,
                        pval_threshold: float = 0.05) -> pd.DataFrame:
        """过滤差异基因

        Args:
            de_table: 差异表达表
            log2fc_threshold: log2FC阈值
            pval_threshold: p值阈值

        Returns:
            过滤后的差异基因表
        """
        filtered = de_table[
            (abs(de_table['log2FC']) >= log2fc_threshold) &
            (de_table['pvals_adj'] < pval_threshold)
        ].copy()

        # 添加方向
        filtered['direction'] = filtered['log2FC'].apply(
            lambda x: 'up' if x > 0 else 'down'
        )

        logger.info(f"Filtered to {len(filtered)} significant DE genes")
        return filtered


class TrajectoryAnalysis:
    """轨迹分析"""

    def __init__(self, method: str = "paga"):
        """初始化轨迹分析

        Args:
            method: 方法 ("paga" 或 "dpt")
        """
        self.method = method

    def run_paga(self, adata, groups: str = "leiden"):
        """运行PAGA轨迹分析

        Args:
            adata: AnnData对象
            groups: 分组列名

        Returns:
            带有PAGA结果的AnnData
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        sc.tl.paga(adata, groups=groups)
        sc.pl.paga(adata, plot=False)  # 初始化绘图
        sc.tl.draw_graph(adata)

        logger.info("PAGA trajectory analysis complete")
        return adata

    def run_dpt(self, adata, root_key: str = "xroot"):
        """运行DPT (Diffusion Pseudotime)

        Args:
            adata: AnnData对象
            root_key: 根细胞键名

        Returns:
            带有DPT结果的AnnData
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        # 确保有diffusion map
        if 'X_diffmap' not in adata.obsm.keys():
            sc.tl.diffmap(adata)

        sc.tl.dpt(adata)

        logger.info("DPT analysis complete")
        return adata
