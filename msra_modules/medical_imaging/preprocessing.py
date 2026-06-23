"""
Image Preprocessing - 影像预处理

IMG-004: 医学影像标准化预处理
"""

from __future__ import annotations
import numpy as np
from typing import Tuple, Optional, Dict, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    import SimpleITK as sitk

logger = logging.getLogger(__name__)


def _get_sitk():
    """延迟导入SimpleITK"""
    try:
        import SimpleITK as sitk
        return sitk
    except ImportError as e:
        raise ImportError(
            f"SimpleITK is required: {e}. "
            "Install with: pip install SimpleITK"
        )


class ImagePreprocessor:
    """医学影像预处理器"""

    def __init__(self,
                 target_spacing: Optional[Tuple[float, float, float]] = None,
                 normalize: bool = True):
        """初始化预处理器

        Args:
            target_spacing: 目标体素间距 (x, y, z)
            normalize: 是否标准化到[0,1]
        """
        self.target_spacing = target_spacing
        self.normalize = normalize

    def resample(self, image,
                 target_spacing: Optional[Tuple[float, float, float]] = None
                 ):
        """重采样图像到目标间距

        Args:
            image: 输入图像
            target_spacing: 目标间距

        Returns:
            重采样后的图像
        """
        sitk = _get_sitk()
        spacing = target_spacing or self.target_spacing
        if spacing is None:
            return image

        original_spacing = image.GetSpacing()
        original_size = image.GetSize()

        # 计算新尺寸
        new_size = [
            int(round(osz * osp / nsp))
            for osz, osp, nsp in zip(original_size, original_spacing, spacing)
        ]

        resampler = sitk.ResampleImageFilter()
        resampler.SetOutputSpacing(spacing)
        resampler.SetSize(new_size)
        resampler.SetOutputOrigin(image.GetOrigin())
        resampler.SetOutputDirection(image.GetDirection())
        resampler.SetTransform(sitk.Transform())
        resampler.SetDefaultPixelValue(0)
        resampler.SetInterpolator(sitk.sitkBSpline)

        return resampler.Execute(image)

    def normalize_intensity(self, image, method: str = "min_max"):
        """标准化图像强度

        Args:
            image: 输入图像
            method: 标准化方法 ("min_max" 或 "z_score")

        Returns:
            标准化后的图像
        """
        sitk = _get_sitk()
        if method == "min_max":
            return sitk.RescaleIntensity(image, 0, 1)
        elif method == "z_score":
            stats = sitk.StatisticsImageFilter()
            stats.Execute(image)
            mean = stats.GetMean()
            std = stats.GetSigma()
            if std > 0:
                return sitk.ShiftScale(
                    sitk.ShiftScale(image, -mean, 1.0),
                    0, 1.0/std
                )
            return image
        else:
            raise ValueError(f"Unknown normalization method: {method}")

    def denoise(self, image, method: str = "curvature_flow"):
        """图像去噪

        Args:
            image: 输入图像
            method: 去噪方法 ("curvature_flow" 或 "median")

        Returns:
            去噪后的图像
        """
        sitk = _get_sitk()
        if method == "curvature_flow":
            return sitk.CurvatureFlow(image1=image, timeStep=0.125, numberOfIterations=5)
        elif method == "median":
            return sitk.Median(image1=image, radius=[1, 1, 1])
        else:
            raise ValueError(f"Unknown denoise method: {method}")

    def bias_correction(self, image):
        """N4偏置场校正

        Args:
            image: 输入图像

        Returns:
            校正后的图像
        """
        sitk = _get_sitk()
        # 创建mask (Otsu阈值)
        mask = sitk.OtsuThreshold(image, 0, 1, 200)

        corrector = sitk.N4BiasFieldCorrectionImageFilter()
        return corrector.Execute(image, mask)

    def preprocess_pipeline(self, image):
        """完整预处理pipeline

        Args:
            image: 输入图像

        Returns:
            预处理后的图像
        """
        logger.info("Starting preprocessing pipeline...")

        # 1. 重采样
        if self.target_spacing:
            image = self.resample(image)
            logger.info(f"Resampled to spacing: {image.GetSpacing()}")

        # 2. 去噪
        image = self.denoise(image)
        logger.info("Denoised")

        # 3. 标准化
        if self.normalize:
            image = self.normalize_intensity(image)
            logger.info("Normalized")

        return image


def normalize_intensity(array: np.ndarray,
                        method: str = "min_max") -> np.ndarray:
    """便捷函数：标准化numpy数组强度

    Args:
        array: 输入数组
        method: 标准化方法

    Returns:
        标准化后的数组
    """
    if method == "min_max":
        min_val = np.min(array)
        max_val = np.max(array)
        if max_val > min_val:
            return (array - min_val) / (max_val - min_val)
        return array
    elif method == "z_score":
        mean = np.mean(array)
        std = np.std(array)
        if std > 0:
            return (array - mean) / std
        return array
    else:
        raise ValueError(f"Unknown method: {method}")
