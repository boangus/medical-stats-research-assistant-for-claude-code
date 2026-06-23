"""
Image Registration - 医学影像配准

IMG-008: 多模态影像配准
"""

from __future__ import annotations
import numpy as np
from typing import Optional, Tuple, Dict, TYPE_CHECKING
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


class ImageRegistration:
    """医学影像配准"""

    def __init__(self, method: str = "rigid"):
        """初始化配准

        Args:
            method: 配准方法 ("rigid", "affine", "bspline")
        """
        self.method = method

    def register(self, fixed_image, moving_image,
                 fixed_mask=None, moving_mask=None) -> Dict:
        """执行配准

        Args:
            fixed_image: 固定图像 (SimpleITK Image)
            moving_image: 移动图像 (SimpleITK Image)
            fixed_mask: 固定图像掩码 (可选)
            moving_mask: 移动图像掩码 (可选)

        Returns:
            配准结果字典
        """
        sitk = _get_sitk()

        # 初始化配准方法
        registration_method = sitk.ImageRegistrationMethod()

        # 选择变换
        if self.method == "rigid":
            initial_transform = sitk.CenteredTransformInitializer(
                fixed_image, moving_image,
                sitk.Euler3DTransform(),
                sitk.CenteredTransformInitializerFilter.GEOMETRY
            )
        elif self.method == "affine":
            initial_transform = sitk.CenteredTransformInitializer(
                fixed_image, moving_image,
                sitk.AffineTransform(3),
                sitk.CenteredTransformInitializerFilter.GEOMETRY
            )
        elif self.method == "bspline":
            initial_transform = sitk.CenteredTransformInitializer(
                fixed_image, moving_image,
                sitk.BSplineTransformInitializer(3),
                sitk.CenteredTransformInitializerFilter.GEOMETRY
            )
        else:
            raise ValueError(f"Unknown method: {self.method}")

        # 设置度量
        registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)

        # 设置采样
        registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
        registration_method.SetMetricSamplingPercentage(0.01)

        # 设置插值
        registration_method.SetInterpolator(sitk.sitkLinear)

        # 设置优化器
        registration_method.SetOptimizerAsGradientDescent(
            learningRate=1.0,
            numberOfIterations=100,
            convergenceMinimumValue=1e-6,
            convergenceWindowSize=10
        )
        registration_method.SetOptimizerScalesFromPhysicalShift()

        # 设置初始变换
        registration_method.SetInitialTransform(initial_transform, inPlace=False)

        # 设置掩码
        if fixed_mask is not None:
            registration_method.SetMetricFixedMask(fixed_mask)
        if moving_mask is not None:
            registration_method.SetMetricMovingMask(moving_mask)

        # 执行配准
        try:
            final_transform = registration_method.Execute(
                fixed_image, moving_image
            )

            # 评估
            metric_value = registration_method.GetMetricValue()
            iterations = registration_method.GetOptimizerIteration()

            # 重采样
            resampled = sitk.Resample(
                moving_image,
                fixed_image,
                final_transform,
                sitk.sitkLinear,
                0.0,
                moving_image.GetPixelID()
            )

            logger.info(f"Registration complete: metric={metric_value:.4f}, "
                       f"iterations={iterations}")

            return {
                "transform": final_transform,
                "resampled_image": resampled,
                "metric_value": metric_value,
                "iterations": iterations,
                "method": self.method,
            }

        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return {
                "error": str(e),
                "method": self.method,
            }

    def evaluate(self, fixed_image, moving_image, mask=None) -> Dict:
        """评估配准质量

        Args:
            fixed_image: 固定图像
            moving_image: 移动图像
            mask: 评估区域掩码

        Returns:
            评估指标字典
        """
        sitk = _get_sitk()

        # 转换为numpy
        fixed_array = sitk.GetArrayFromImage(fixed_image)
        moving_array = sitk.GetArrayFromImage(moving_image)

        if mask is not None:
            mask_array = sitk.GetArrayFromImage(mask)
            fixed_values = fixed_array[mask_array > 0]
            moving_values = moving_array[mask_array > 0]
        else:
            fixed_values = fixed_array.flatten()
            moving_values = moving_array.flatten()

        # MSE
        mse = float(np.mean((fixed_values - moving_values) ** 2))

        # MAE
        mae = float(np.mean(np.abs(fixed_values - moving_values)))

        # 相关系数
        if len(fixed_values) > 1:
            correlation = float(np.corrcoef(fixed_values, moving_values)[0, 1])
        else:
            correlation = 0.0

        # SSIM (简化版)
        from scipy.ndimage import uniform_filter
        if fixed_array.ndim == 3:
            # 取中间切片
            mid = fixed_array.shape[0] // 2
            f2d = fixed_array[mid]
            m2d = moving_array[mid]
        else:
            f2d = fixed_array
            m2d = moving_array

        try:
            mu_f = uniform_filter(f2d.astype(float), size=7)
            mu_m = uniform_filter(m2d.astype(float), size=7)
            var_f = uniform_filter(f2d.astype(float)**2, size=7) - mu_f**2
            var_m = uniform_filter(m2d.astype(float)**2, size=7) - mu_m**2
            cov_fm = uniform_filter(
                f2d.astype(float) * m2d.astype(float), size=7
            ) - mu_f * mu_m

            c1 = (0.01 * 255) ** 2
            c2 = (0.03 * 255) ** 2
            ssim = float(np.mean(
                ((2 * mu_f * mu_m + c1) * (2 * cov_fm + c2)) /
                ((mu_f**2 + mu_m**2 + c1) * (var_f + var_m + c2))
            ))
        except Exception:
            ssim = 0.0

        return {
            "mse": mse,
            "mae": mae,
            "correlation": correlation,
            "ssim": ssim,
        }


class ImageClassifier:
    """影像分类器"""

    def __init__(self, model_type: str = "resnet18",
                 num_classes: int = 2, device: str = "cpu"):
        """初始化分类器

        Args:
            model_type: 模型类型
            num_classes: 类别数
            device: 计算设备
        """
        self.model_type = model_type
        self.num_classes = num_classes
        self.device = device
        self._model = None

    def _load_model(self):
        """加载模型"""
        if self._model is not None:
            return

        try:
            import torch
            import torchvision.models as models

            if self.model_type == "resnet18":
                self._model = models.resnet18(weights=None)
                self._model.fc = torch.nn.Linear(
                    self._model.fc.in_features, self.num_classes
                )
            elif self.model_type == "densenet121":
                self._model = models.densenet121(weights=None)
                self._model.classifier = torch.nn.Linear(
                    self._model.classifier.in_features, self.num_classes
                )
            else:
                raise ValueError(f"Unknown model: {self.model_type}")

            self._model = self._model.to(self.device)
            self._model.eval()
            logger.info(f"Loaded {self.model_type} classifier")

        except ImportError as e:
            raise ImportError(f"PyTorch required: {e}")

    def classify(self, image: np.ndarray) -> Dict:
        """分类

        Args:
            image: 输入影像

        Returns:
            分类结果
        """
        self._load_model()
        import torch

        # 预处理
        if image.ndim == 3 and image.shape[-1] != 3:
            mid = image.shape[0] // 2
            img_2d = image[mid]
        else:
            img_2d = image

        if img_2d.max() > 1.0:
            img_2d = (img_2d - img_2d.min()) / (img_2d.max() - img_2d.min() + 1e-8)

        if img_2d.ndim == 2:
            img_2d = np.stack([img_2d] * 3, axis=0)
        elif img_2d.ndim == 3 and img_2d.shape[-1] == 3:
            img_2d = img_2d.transpose(2, 0, 1)

        tensor = torch.from_numpy(img_2d).float().unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self._model(tensor)
            probs = torch.softmax(output, dim=1)
            conf, pred = torch.max(probs, dim=1)

        return {
            "prediction": int(pred.item()),
            "confidence": float(conf.item()),
            "probabilities": probs.cpu().numpy().tolist()[0]
        }
