"""
Radiomics Tests - 影像组学特征提取测试

测试 RadiomicsExtractor 的各项特征提取功能。
"""

import os
import tempfile
from pathlib import Path

import numpy as np


class TestRadiomicsExtractor:
    """RadiomicsExtractor 测试"""

    def setup_method(self):
        """每个测试前创建测试数据"""
        from msra_modules.medical_imaging.radiomics import RadiomicsExtractor
        self.extractor = RadiomicsExtractor(bin_width=25.0)

        # 创建 3D 合成影像和掩膜
        np.random.seed(42)
        self.image_3d = np.random.rand(32, 32, 32).astype(np.float32) * 1000
        self.mask_3d = np.zeros((32, 32, 32), dtype=np.uint8)
        self.mask_3d[8:24, 8:24, 8:24] = 1  # 中心 16³ ROI

    def test_init_defaults(self):
        """测试默认初始化"""
        from msra_modules.medical_imaging.radiomics import RadiomicsExtractor
        ext = RadiomicsExtractor()
        assert ext.bin_width == 25.0

    def test_extract_shape_features(self):
        """测试形状特征提取"""
        features = self.extractor.extract_shape_features(self.mask_3d)

        assert "VoxelVolume" in features
        assert "SurfaceArea" in features
        assert "Maximum3DDiameter" in features
        assert "Sphericity" in features

        # 16³ = 4096 体素
        assert features["VoxelVolume"] == 16 ** 3
        assert features["Sphericity"] > 0

    def test_extract_shape_features_empty_mask(self):
        """测试空掩膜的形状特征"""
        empty_mask = np.zeros((32, 32, 32), dtype=np.uint8)
        features = self.extractor.extract_shape_features(empty_mask)

        assert "error" in features

    def test_extract_firstorder_features(self):
        """测试一阶统计特征提取"""
        features = self.extractor.extract_firstorder_features(self.image_3d, self.mask_3d)

        expected_keys = [
            "Mean", "Median", "Std", "Variance", "Minimum", "Maximum",
            "Range", "Skewness", "Kurtosis", "Energy", "Entropy",
            "RootMeanSquared", "MeanAbsoluteDeviation",
        ]
        for key in expected_keys:
            assert key in features, f"Missing feature: {key}"

        # 基本合理性检查
        assert features["Minimum"] <= features["Mean"] <= features["Maximum"]
        assert features["Std"] >= 0
        assert features["Variance"] >= 0

    def test_extract_firstorder_empty_mask(self):
        """测试空掩膜的一阶特征"""
        empty_mask = np.zeros((32, 32, 32), dtype=np.uint8)
        features = self.extractor.extract_firstorder_features(self.image_3d, empty_mask)

        assert "error" in features

    def test_extract_texture_features(self):
        """测试纹理特征提取"""
        features = self.extractor.extract_texture_features(self.image_3d, self.mask_3d)

        # 检查是否包含 GLCM 特征
        glcm_keys = [k for k in features.keys() if k.startswith("GLCM_")]
        assert len(glcm_keys) > 0

        # 检查基本值域
        for key in glcm_keys:
            assert isinstance(features[key], float)

    def test_extract_all(self):
        """测试提取所有特征"""
        results = self.extractor.extract_all(self.image_3d, self.mask_3d)

        assert "shape" in results
        assert "firstorder" in results
        assert "texture" in results

        # 确保每个类别都有特征
        assert len(results["shape"]) > 0
        assert len(results["firstorder"]) > 0
        assert len(results["texture"]) > 0

    def test_to_dataframe(self):
        """测试转换为 DataFrame"""
        results = self.extractor.extract_all(self.image_3d, self.mask_3d)
        df = self.extractor.to_dataframe(results)

        assert "feature_class" in df.columns
        assert "feature_name" in df.columns
        assert "value" in df.columns
        assert len(df) > 0

    def test_export_v1_schema(self):
        """测试 v1 Schema 导出"""
        results = self.extractor.extract_all(self.image_3d, self.mask_3d)

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = self.extractor.export_v1_schema(results, tmpdir)

            assert "feature_matrix" in paths
            assert "feature_metadata" in paths
            assert paths["schema_version"] == "msra/imaging_features/v1"

            # 检查文件存在
            matrix_path = Path(paths["feature_matrix"])
            metadata_path = Path(paths["feature_metadata"])
            assert matrix_path.exists()
            assert metadata_path.exists()

            # 读取并验证内容
            import pandas as pd
            matrix_df = pd.read_csv(matrix_path)
            assert "sample_id" in matrix_df.columns
            assert len(matrix_df) == 1  # 单样本

            metadata_df = pd.read_csv(metadata_path)
            assert "feature_name" in metadata_df.columns
            assert "class" in metadata_df.columns
            assert "description" in metadata_df.columns
            assert len(metadata_df) > 0

    def test_export_v1_schema_creates_dir(self):
        """测试 export_v1_schema 自动创建输出目录"""
        results = self.extractor.extract_all(self.image_3d, self.mask_3d)

        with tempfile.TemporaryDirectory() as tmpdir:
            nested_dir = os.path.join(tmpdir, "deep", "nested", "output")
            paths = self.extractor.export_v1_schema(results, nested_dir)

            assert Path(paths["feature_matrix"]).exists()
            assert Path(paths["feature_metadata"]).exists()
