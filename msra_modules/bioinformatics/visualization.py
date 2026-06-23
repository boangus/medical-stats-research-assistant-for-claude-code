"""
Bioinformatics Visualization - 生物信息可视化

BIO-011: 单细胞可视化
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class BioVisualizer:
    """生物信息可视化工具"""

    def __init__(self, figsize: tuple = (8, 6), dpi: int = 100):
        """初始化

        Args:
            figsize: 图像大小
            dpi: 分辨率
        """
        self.figsize = figsize
        self.dpi = dpi

    def plot_umap(self, adata, color: Optional[str] = None,
                  save_path: Optional[str] = None) -> plt.Figure:
        """绘制UMAP图

        Args:
            adata: AnnData对象
            color: 着色列名
            save_path: 保存路径

        Returns:
            matplotlib Figure
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        if 'X_umap' not in adata.obsm.keys():
            raise ValueError("UMAP not computed. Run run_umap first.")

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        if color:
            sc.pl.umap(adata, color=color, ax=ax, show=False)
        else:
            sc.pl.umap(adata, ax=ax, show=False)

        if save_path:
            from pathlib import Path
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, bbox_inches='tight', dpi=self.dpi)
            logger.info(f"Saved UMAP to: {save_path}")

        return fig

    def plot_violin(self, adata, keys: List[str],
                    groupby: Optional[str] = None,
                    save_path: Optional[str] = None) -> plt.Figure:
        """绘制小提琴图

        Args:
            adata: AnnData对象
            keys: 基因名列表
            groupby: 分组列名
            save_path: 保存路径

        Returns:
            matplotlib Figure
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        n_plots = len(keys)
        fig, axes = plt.subplots(1, n_plots,
                                  figsize=(n_plots * 4, 6),
                                  dpi=self.dpi)

        if n_plots == 1:
            axes = [axes]

        for i, key in enumerate(keys):
            sc.pl.violin(adata, keys=key, groupby=groupby,
                        ax=axes[i], show=False)

        plt.tight_layout()

        if save_path:
            from pathlib import Path
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, bbox_inches='tight', dpi=self.dpi)
            logger.info(f"Saved violin plot to: {save_path}")

        return fig

    def plot_dotplot(self, adata, var_names: List[str],
                     groupby: str = "leiden",
                     save_path: Optional[str] = None) -> plt.Figure:
        """绘制点图

        Args:
            adata: AnnData对象
            var_names: 基因名列表
            groupby: 分组列名
            save_path: 保存路径

        Returns:
            matplotlib Figure
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        sc.pl.dotplot(adata, var_names=var_names, groupby=groupby,
                     ax=ax, show=False)

        if save_path:
            from pathlib import Path
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, bbox_inches='tight', dpi=self.dpi)
            logger.info(f"Saved dotplot to: {save_path}")

        return fig

    def plot_heatmap(self, adata, var_names: List[str],
                     groupby: str = "leiden",
                     save_path: Optional[str] = None) -> plt.Figure:
        """绘制热图

        Args:
            adata: AnnData对象
            var_names: 基因名列表
            groupby: 分组列名
            save_path: 保存路径

        Returns:
            matplotlib Figure
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        fig = plt.figure(figsize=self.figsize, dpi=self.dpi)

        sc.pl.heatmap(adata, var_names=var_names, groupby=groupby,
                     show=False)

        if save_path:
            from pathlib import Path
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, bbox_inches='tight', dpi=self.dpi)
            logger.info(f"Saved heatmap to: {save_path}")

        return fig

    def plot_paga(self, adata, color: Optional[str] = None,
                  save_path: Optional[str] = None) -> plt.Figure:
        """绘制PAGA轨迹图

        Args:
            adata: AnnData对象
            color: 着色列名
            save_path: 保存路径

        Returns:
            matplotlib Figure
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        sc.pl.paga(adata, color=color, ax=ax, show=False)

        if save_path:
            from pathlib import Path
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, bbox_inches='tight', dpi=self.dpi)
            logger.info(f"Saved PAGA plot to: {save_path}")

        return fig
