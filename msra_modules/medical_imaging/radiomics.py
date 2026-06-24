"""
Radiomics Feature Extraction - 影像组学特征提取

IMG-007: Radiomics特征提取
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RadiomicsFeature:
    """影像组学特征"""
    name: str
    value: float
    feature_class: str


class RadiomicsExtractor:
    """影像组学特征提取器"""

    # 标准特征类别
    FEATURE_CLASSES = [
        "shape",
        "firstorder",
        "glcm",
        "glrlm",
        "glszm",
        "gldm",
        "ngtdm"
    ]

    def __init__(self, bin_width: float = 25.0):
        """初始化特征提取器

        Args:
            bin_width: 灰度直方图bin宽度
        """
        self.bin_width = bin_width

    def extract_shape_features(self, mask: np.ndarray) -> Dict[str, float]:
        """提取形状特征

        Args:
            mask: 分割掩码 (二值化)

        Returns:
            形状特征字典
        """
        from scipy import ndimage

        features = {}
        voxel_count = int(np.sum(mask > 0))

        if voxel_count == 0:
            return {"error": "Empty mask"}

        # 体积
        features["VoxelVolume"] = float(voxel_count)

        # 表面积 (简化计算)
        eroded = ndimage.binary_erosion(mask)
        surface_voxels = np.sum(mask > 0) - np.sum(eroded > 0)
        features["SurfaceArea"] = float(surface_voxels)

        # 最大3D直径
        coords = np.argwhere(mask > 0)
        if len(coords) > 1:
            from scipy.spatial.distance import pdist
            distances = pdist(coords)
            features["Maximum3DDiameter"] = float(np.max(distances))
        else:
            features["Maximum3DDiameter"] = 0.0

        # 主轴长度
        if len(coords) > 2:
            try:
                from sklearn.decomposition import PCA
                pca = PCA(n_components=3)
                pca.fit(coords)
                features["MajorAxisLength"] = float(pca.explained_variance_[0])
                features["MinorAxisLength"] = float(pca.explained_variance_[1])
                features["LeastAxisLength"] = float(pca.explained_variance_[2])
            except Exception:
                features["MajorAxisLength"] = 0.0
                features["MinorAxisLength"] = 0.0
                features["LeastAxisLength"] = 0.0
        else:
            features["MajorAxisLength"] = 0.0
            features["MinorAxisLength"] = 0.0
            features["LeastAxisLength"] = 0.0

        # 球度
        volume = features["VoxelVolume"]
        surface = features["SurfaceArea"]
        if surface > 0:
            features["Sphericity"] = float(
                (np.pi ** (1/3) * (6 * volume) ** (2/3)) / surface
            )
        else:
            features["Sphericity"] = 0.0

        return features

    def extract_firstorder_features(self,
                                    image: np.ndarray,
                                    mask: np.ndarray) -> Dict[str, float]:
        """提取一阶统计特征

        Args:
            image: 影像数据
            mask: 分割掩码

        Returns:
            一阶统计特征字典
        """
        features = {}
        values = image[mask > 0]

        if len(values) == 0:
            return {"error": "Empty mask region"}

        # 基本统计
        features["Mean"] = float(np.mean(values))
        features["Median"] = float(np.median(values))
        features["Std"] = float(np.std(values))
        features["Variance"] = float(np.var(values))
        features["Minimum"] = float(np.min(values))
        features["Maximum"] = float(np.max(values))
        features["Range"] = features["Maximum"] - features["Minimum"]

        # 百分位数
        features["Percentile10"] = float(np.percentile(values, 10))
        features["Percentile25"] = float(np.percentile(values, 25))
        features["Percentile75"] = float(np.percentile(values, 75))
        features["Percentile90"] = float(np.percentile(values, 90))
        features["IQR"] = features["Percentile75"] - features["Percentile25"]

        # 偏度和峰度
        from scipy.stats import skew, kurtosis
        features["Skewness"] = float(skew(values))
        features["Kurtosis"] = float(kurtosis(values))

        # 能量
        features["Energy"] = float(np.sum(values ** 2))

        # 熵
        hist, _ = np.histogram(values, bins=32, density=True)
        hist = hist[hist > 0]
        features["Entropy"] = float(-np.sum(hist * np.log2(hist)))

        # 均方根
        features["RootMeanSquared"] = float(np.sqrt(np.mean(values ** 2)))

        # 绝对偏差
        features["MeanAbsoluteDeviation"] = float(np.mean(np.abs(values - np.mean(values))))

        return features

    def extract_texture_features(self,
                                 image: np.ndarray,
                                 mask: np.ndarray) -> Dict[str, float]:
        """提取纹理特征 (简化版GLCM)

        Args:
            image: 影像数据
            mask: 分割掩码

        Returns:
            纹理特征字典
        """
        features = {}

        # 量化图像
        masked = image[mask > 0]
        if len(masked) == 0:
            return {"error": "Empty mask"}

        # 量化到指定bin数
        min_val = masked.min()
        max_val = masked.max()
        if max_val > min_val:
            quantized = np.floor(
                (image - min_val) / (max_val - min_val) * (self.bin_width - 1)
            ).astype(int)
            quantized = np.clip(quantized, 0, int(self.bin_width) - 1)
        else:
            return {"error": "Constant intensity"}

        # 计算简化的GLCM特征
        try:
            from skimage.feature import graycomatrix, graycoprops

            # 取中间切片进行2D GLCM计算
            mid_slice = image.shape[0] // 2
            img_2d = quantized[mid_slice].astype(np.uint8)
            mask_2d = mask[mid_slice] > 0

            if mask_2d.sum() > 0:
                glcm = graycomatrix(
                    img_2d,
                    distances=[1],
                    angles=[0, np.pi/4, np.pi/2, 3*np.pi/4],
                    levels=int(self.bin_width),
                    symmetric=True,
                    normed=True
                )

                features["GLCM_Contrast"] = float(np.mean(graycoprops(glcm, 'contrast')))
                features["GLCM_Dissimilarity"] = float(np.mean(graycoprops(glcm, 'dissimilarity')))
                features["GLCM_Homogeneity"] = float(np.mean(graycoprops(glcm, 'homogeneity')))
                features["GLCM_Energy"] = float(np.mean(graycoprops(glcm, 'energy')))
                features["GLCM_Correlation"] = float(np.mean(graycoprops(glcm, 'correlation')))
                features["GLCM_ASM"] = float(np.mean(graycoprops(glcm, 'ASM')))
            else:
                for prop in ["Contrast", "Dissimilarity", "Homogeneity",
                             "Energy", "Correlation", "ASM"]:
                    features[f"GLCM_{prop}"] = 0.0

        except ImportError:
            logger.warning("scikit-image not available, texture features limited")
            for prop in ["Contrast", "Dissimilarity", "Homogeneity",
                         "Energy", "Correlation", "ASM"]:
                features[f"GLCM_{prop}"] = 0.0

        return features

    def extract_all(self,
                    image: np.ndarray,
                    mask: np.ndarray) -> Dict[str, Dict[str, float]]:
        """提取所有影像组学特征

        Args:
            image: 影像数据
            mask: 分割掩码

        Returns:
            所有特征字典
        """
        logger.info("Extracting radiomics features...")

        results = {
            "shape": self.extract_shape_features(mask),
            "firstorder": self.extract_firstorder_features(image, mask),
            "texture": self.extract_texture_features(image, mask),
        }

        total_features = sum(len(v) for v in results.values())
        logger.info(f"Extracted {total_features} features")

        return results

    def to_dataframe(self, features: Dict) -> "pandas.DataFrame":
        """转换为DataFrame格式

        Args:
            features: 特征字典

        Returns:
            pandas DataFrame
        """
        import pandas as pd

        rows = []
        for feature_class, class_features in features.items():
            for name, value in class_features.items():
                rows.append({
                    "feature_class": feature_class,
                    "feature_name": name,
                    "value": value
                })

        return pd.DataFrame(rows)

    def export_v1_schema(
        self,
        features: Dict,
        output_dir: str,
    ) -> Dict[str, str]:
        """导出 msra/imaging_features/v1 标准格式

        输出两个文件:
        - feature_matrix.csv: sample_id + 所有特征列（一行一个样本）
        - feature_metadata.csv: feature_name, class, description

        Args:
            features: 特征字典 (extract_all 的输出)
            output_dir: 输出目录

        Returns:
            dict: 文件路径映射
                {
                    "feature_matrix": "path/to/feature_matrix.csv",
                    "feature_metadata": "path/to/feature_metadata.csv",
                    "schema_version": "msra/imaging_features/v1",
                }
        """
        import pandas as pd
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 构建特征矩阵（单样本场景）
        feature_data: Dict[str, float] = {}
        metadata_rows: List[Dict[str, str]] = []

        for feature_class, class_features in features.items():
            for name, value in class_features.items():
                # 生成标准化的特征列名
                col_name = f"{feature_class}_{name}"
                feature_data[col_name] = float(value) if isinstance(value, (int, float)) else np.nan

                # 特征元数据
                description = self._generate_feature_description(name, feature_class)
                metadata_rows.append({
                    "feature_name": col_name,
                    "class": feature_class,
                    "description": description,
                })

        # 写入 feature_matrix.csv
        matrix_path = output_path / "feature_matrix.csv"
        matrix_df = pd.DataFrame([feature_data])
        matrix_df.insert(0, "sample_id", "sample_001")
        matrix_df.to_csv(matrix_path, index=False, encoding="utf-8")

        # 写入 feature_metadata.csv
        metadata_path = output_path / "feature_metadata.csv"
        metadata_df = pd.DataFrame(metadata_rows)
        metadata_df.to_csv(metadata_path, index=False, encoding="utf-8")

        logger.info(
            f"Exported v1 schema: {len(feature_data)} features, "
            f"matrix={matrix_path}, metadata={metadata_path}"
        )

        return {
            "feature_matrix": str(matrix_path),
            "feature_metadata": str(metadata_path),
            "schema_version": "msra/imaging_features/v1",
        }

    def _generate_feature_description(self, name: str, feature_class: str) -> str:
        """生成特征的描述文本

        Args:
            name: 特征名
            feature_class: 特征类别

        Returns:
            描述文本
        """
        descriptions: Dict[str, Dict[str, str]] = {
            "shape": {
                "VoxelVolume": "ROI 体素体积",
                "SurfaceArea": "ROI 表面积（体素计数）",
                "Maximum3DDiameter": "ROI 最大3D直径",
                "MajorAxisLength": "主轴长度（PCA第一主成分方差）",
                "MinorAxisLength": "次轴长度（PCA第二主成分方差）",
                "LeastAxisLength": "最短轴长度（PCA第三主成分方差）",
                "Sphericity": "球度（接近1表示更接近球形）",
            },
            "firstorder": {
                "Mean": "ROI 区域均值",
                "Median": "ROI 区域中位数",
                "Std": "ROI 区域标准差",
                "Variance": "ROI 区域方差",
                "Minimum": "ROI 区域最小值",
                "Maximum": "ROI 区域最大值",
                "Range": "ROI 区域值域范围",
                "Percentile10": "10百分位数",
                "Percentile25": "25百分位数",
                "Percentile75": "75百分位数",
                "Percentile90": "90百分位数",
                "IQR": "四分位距",
                "Skewness": "偏度",
                "Kurtosis": "峰度",
                "Energy": "能量（像素值平方和）",
                "Entropy": "熵（信息量）",
                "RootMeanSquared": "均方根",
                "MeanAbsoluteDeviation": "平均绝对偏差",
            },
            "texture": {
                "GLCM_Contrast": "GLCM 对比度",
                "GLCM_Dissimilarity": "GLCM 不相似性",
                "GLCM_Homogeneity": "GLCM 同质性",
                "GLCM_Energy": "GLCM 能量",
                "GLCM_Correlation": "GLCM 相关性",
                "GLCM_ASM": "GLCM 角二阶矩",
            },
        }

        class_descriptions = descriptions.get(feature_class, {})
        return class_descriptions.get(name, f"{feature_class} 特征: {name}")
