"""
Imaging Visualization - 影像可视化

IMG-009: 分割结果可视化
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ImagingVisualizer:
    """影像可视化工具"""

    def __init__(self, figsize: Tuple[int, int] = (12, 8),
                 dpi: int = 100):
        """初始化可视化器

        Args:
            figsize: 图像大小
            dpi: 分辨率
        """
        self.figsize = figsize
        self.dpi = dpi

    def plot_slice(self,
                   image: np.ndarray,
                   mask: Optional[np.ndarray] = None,
                   slice_idx: Optional[int] = None,
                   title: str = "",
                   save_path: Optional[str] = None) -> plt.Figure:
        """绘制单个切片

        Args:
            image: 影像数据 (D, H, W)
            mask: 分割掩码 (可选)
            slice_idx: 切片索引 (默认中间)
            title: 标题
            save_path: 保存路径

        Returns:
            matplotlib Figure
        """
        if slice_idx is None:
            slice_idx = image.shape[0] // 2

        fig, axes = plt.subplots(1, 3 if mask is not None else 1,
                                  figsize=self.figsize, dpi=self.dpi)

        if mask is None:
            axes = [axes]

        # 原始图像
        axes[0].imshow(image[slice_idx], cmap='gray')
        axes[0].set_title(f"Original (slice {slice_idx})")
        axes[0].axis('off')

        if mask is not None:
            # 掩码
            axes[1].imshow(mask[slice_idx], cmap='jet', alpha=0.5)
            axes[1].set_title(f"Mask (slice {slice_idx})")
            axes[1].axis('off')

            # 叠加
            axes[2].imshow(image[slice_idx], cmap='gray')
            axes[2].imshow(mask[slice_idx], cmap='jet', alpha=0.3)
            axes[2].set_title(f"Overlay (slice {slice_idx})")
            axes[2].axis('off')

        plt.suptitle(title)
        plt.tight_layout()

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, bbox_inches='tight', dpi=self.dpi)
            logger.info(f"Saved visualization to: {save_path}")

        return fig

    def plot_multi_slice(self,
                         image: np.ndarray,
                         mask: Optional[np.ndarray] = None,
                         num_slices: int = 4,
                         title: str = "",
                         save_path: Optional[str] = None) -> plt.Figure:
        """绘制多个切片

        Args:
            image: 影像数据
            mask: 分割掩码
            num_slices: 切片数
            title: 标题
            save_path: 保存路径

        Returns:
            matplotlib Figure
        """
        depth = image.shape[0]
        indices = np.linspace(depth * 0.2, depth * 0.8, num_slices, dtype=int)

        cols = num_slices
        rows = 2 if mask is not None else 1

        fig, axes = plt.subplots(rows, cols,
                                  figsize=(cols * 3, rows * 3),
                                  dpi=self.dpi)

        if rows == 1:
            axes = axes[np.newaxis, :]

        for i, idx in enumerate(indices):
            axes[0, i].imshow(image[idx], cmap='gray')
            axes[0, i].set_title(f"Slice {idx}")
            axes[0, i].axis('off')

            if mask is not None:
                axes[1, i].imshow(image[idx], cmap='gray')
                axes[1, i].imshow(mask[idx], cmap='jet', alpha=0.3)
                axes[1, i].set_title(f"Overlay {idx}")
                axes[1, i].axis('off')

        plt.suptitle(title)
        plt.tight_layout()

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, bbox_inches='tight', dpi=self.dpi)
            logger.info(f"Saved multi-slice view to: {save_path}")

        return fig

    def plot_3d_volume(self,
                       image: np.ndarray,
                       mask: Optional[np.ndarray] = None,
                       threshold: Optional[float] = None,
                       title: str = "3D Volume Rendering",
                       save_path: Optional[str] = None) -> plt.Figure:
        """3D体绘制

        Args:
            image: 影像数据
            mask: 分割掩码
            threshold: 阈值
            title: 标题
            save_path: 保存路径

        Returns:
            matplotlib Figure
        """
        fig = plt.figure(figsize=self.figsize, dpi=self.dpi)
        ax = fig.add_subplot(111, projection='3d')

        # 降采样以加速
        step = max(1, image.shape[0] // 50)

        if mask is not None:
            # 使用掩码
            coords = np.argwhere(mask[::step, ::step, ::step] > 0)
            if len(coords) > 0:
                ax.scatter(
                    coords[:, 2], coords[:, 1], coords[:, 0],
                    c='red', alpha=0.1, s=1
                )
        else:
            # 使用阈值
            if threshold is None:
                threshold = np.percentile(image, 90)

            coords = np.argwhere(image[::step, ::step, ::step] > threshold)
            if len(coords) > 0:
                ax.scatter(
                    coords[:, 2], coords[:, 1], coords[:, 0],
                    c=image[::step, ::step, ::step][image[::step, ::step, ::step] > threshold],
                    alpha=0.1, s=1, cmap='gray'
                )

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(title)

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, bbox_inches='tight', dpi=self.dpi)
            logger.info(f"Saved 3D visualization to: {save_path}")

        return fig
