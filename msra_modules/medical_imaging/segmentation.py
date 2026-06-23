"""
Segmentation Pipeline - 影像分割Pipeline

IMG-005: 影像分割pipeline (3D U-Net)
IMG-006: 影像分类pipeline
"""

import numpy as np
import logging
from typing import Tuple, Optional, Dict, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class SegmentationPipeline:
    """影像分割Pipeline"""

    def __init__(self,
                 model_name: str = "spleen_ct",
                 device: str = "cpu"):
        """初始化分割pipeline

        Args:
            model_name: MONAI预训练模型名称
            device: 计算设备 ("cpu" 或 "cuda")
        """
        self.model_name = model_name
        self.device = device
        self._model = None
        self._transform = None

    def _load_model(self):
        """延迟加载MONAI模型"""
        if self._model is not None:
            return

        try:
            import monai
            from monai.networks.nets import UNet
            from monai.bundle import download, load

            # 尝试加载预训练模型
            try:
                self._model = load(
                    name=self.model_name,
                    bundle_dir=str(Path.home() / ".cache" / "monai"),
                    device=self.device
                )
                logger.info(f"Loaded pretrained model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Could not load pretrained model: {e}")
                # 使用默认3D U-Net
                self._model = UNet(
                    spatial_dims=3,
                    in_channels=1,
                    out_channels=2,
                    channels=(16, 32, 64, 128, 256),
                    strides=(2, 2, 2, 2),
                    num_res_units=2,
                ).to(self.device)
                logger.info("Initialized default 3D U-Net")

        except ImportError as e:
            raise ImportError(
                f"MONAI is required for segmentation: {e}. "
                "Install with: pip install monai"
            )

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """预处理影像

        Args:
            image: 输入影像 (D, H, W)

        Returns:
            预处理后的影像
        """
        # 标准化
        if image.max() > 1.0:
            image = (image - image.min()) / (image.max() - image.min() + 1e-8)

        # 添加通道维度
        if image.ndim == 3:
            image = image[np.newaxis, ...]  # (1, D, H, W)

        return image.astype(np.float32)

    def segment(self, image: np.ndarray) -> np.ndarray:
        """执行分割

        Args:
            image: 输入影像 (D, H, W) 或 (1, D, H, W)

        Returns:
            分割掩码 (D, H, W)
        """
        self._load_model()

        # 预处理
        input_tensor = self.preprocess(image)

        # 推理
        import torch
        with torch.no_grad():
            input_tensor = torch.from_numpy(input_tensor).to(self.device)
            output = self._model(input_tensor)
            if isinstance(output, (list, tuple)):
                output = output[0]
            pred = torch.argmax(output, dim=1)
            pred = pred.cpu().numpy()

        # 移除batch维度
        if pred.ndim == 4:
            pred = pred[0]

        logger.info(f"Segmentation complete, shape: {pred.shape}")
        return pred

    def segment_with_confidence(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """分割并返回置信度

        Args:
            image: 输入影像

        Returns:
            (分割掩码, 置信度图)
        """
        self._load_model()
        input_tensor = self.preprocess(image)

        import torch
        with torch.no_grad():
            input_tensor = torch.from_numpy(input_tensor).to(self.device)
            output = self._model(input_tensor)
            if isinstance(output, (list, tuple)):
                output = output[0]
            probs = torch.softmax(output, dim=1)
            confidence, pred = torch.max(probs, dim=1)
            pred = pred.cpu().numpy()
            confidence = confidence.cpu().numpy()

        if pred.ndim == 4:
            pred = pred[0]
            confidence = confidence[0]

        return pred, confidence


class ClassificationPipeline:
    """影像分类Pipeline"""

    def __init__(self,
                 model_name: str = "resnet18",
                 num_classes: int = 2,
                 device: str = "cpu"):
        """初始化分类pipeline

        Args:
            model_name: 模型名称
            num_classes: 类别数
            device: 计算设备
        """
        self.model_name = model_name
        self.num_classes = num_classes
        self.device = device
        self._model = None

    def _load_model(self):
        """加载分类模型"""
        if self._model is not None:
            return

        try:
            import torch
            import torchvision.models as models

            if self.model_name == "resnet18":
                self._model = models.resnet18(pretrained=False)
                # 修改最后一层
                self._model.fc = torch.nn.Linear(
                    self._model.fc.in_features, self.num_classes
                )
            elif self.model_name == "densenet121":
                self._model = models.densenet121(pretrained=False)
                self._model.classifier = torch.nn.Linear(
                    self._model.classifier.in_features, self.num_classes
                )
            else:
                raise ValueError(f"Unknown model: {self.model_name}")

            self._model = self._model.to(self.device)
            self._model.eval()
            logger.info(f"Loaded classification model: {self.model_name}")

        except ImportError as e:
            raise ImportError(
                f"PyTorch is required for classification: {e}"
            )

    def classify(self, image: np.ndarray) -> Dict:
        """执行分类

        Args:
            image: 输入影像 (D, H, W) 或 (H, W, C)

        Returns:
            分类结果字典
        """
        self._load_model()

        import torch

        # 预处理
        if image.ndim == 3 and image.shape[-1] != 3:
            # 3D影像取中间切片
            mid_slice = image.shape[0] // 2
            image_2d = image[mid_slice]
        else:
            image_2d = image

        # 标准化
        if image_2d.max() > 1.0:
            image_2d = (image_2d - image_2d.min()) / (image_2d.max() - image_2d.min() + 1e-8)

        # 转换为 (1, 3, H, W)
        if image_2d.ndim == 2:
            image_2d = np.stack([image_2d] * 3, axis=0)
        elif image_2d.ndim == 3 and image_2d.shape[-1] == 3:
            image_2d = image_2d.transpose(2, 0, 1)

        input_tensor = torch.from_numpy(image_2d).float().unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self._model(input_tensor)
            probs = torch.softmax(output, dim=1)
            confidence, pred = torch.max(probs, dim=1)

        return {
            "prediction": int(pred.item()),
            "confidence": float(confidence.item()),
            "probabilities": probs.cpu().numpy().tolist()[0]
        }
