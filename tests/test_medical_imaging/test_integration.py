"""
Integration Tests - 医学影像模块集成测试

测试完整的分析流程：加载 → 门闸 → 特征提取 → 特征选择 → 导出。
使用 numpy 合成数据和 nibabel 临时文件。
"""

import numpy as np
import pandas as pd
import pytest
import tempfile
import os
from pathlib import Path


class TestFullPipelineIntegration:
    """完整流程集成测试"""

    def setup_method(self):
        """创建测试用的 NIfTI 文件"""
        nib = pytest.importorskip("nibabel")

        self.tmpdir = tempfile.mkdtemp()

        # 创建 3D 影像
        np.random.seed(42)
        self.image_data = np.random.rand(32, 32, 16).astype(np.float32) * 1000
        affine = np.diag([1.0, 1.0, 2.5, 1.0])

        img = nib.Nifti1Image(self.image_data, affine)
        img.header.set_zooms((1.0, 1.0, 2.5))
        self.image_path = os.path.join(self.tmpdir, "scan.nii.gz")
        nib.save(img, self.image_path)

        # 创建掩膜
        mask_data = np.zeros((32, 32, 16), dtype=np.uint8)
        mask_data[8:24, 8:24, 4:12] = 1
        self.mask_data = mask_data

        mask_img = nib.Nifti1Image(mask_data, affine)
        self.mask_path = os.path.join(self.tmpdir, "mask.nii.gz")
        nib.save(mask_img, self.mask_path)

    def teardown_method(self):
        """清理临时文件"""
        import shutil
        if os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)

    def test_load_gate_extract_select_export(self):
        """测试完整流程：加载 → 门闸 → 特征提取 → 特征选择 → 导出"""
        from msra_modules.medical_imaging.image_loader import load_nifti
        from msra_modules.medical_imaging.quality_gates import ImagingQualityGateChecker
        from msra_modules.medical_imaging.radiomics import RadiomicsExtractor
        from msra_modules.medical_imaging.feature_selection import FeatureSelector

        # Step 1: 加载影像
        image_array, metadata = load_nifti(self.image_path)
        assert image_array.shape == (32, 32, 16)
        assert "spacing" in metadata

        # Step 2: 加载掩膜
        mask_array, _ = load_nifti(self.mask_path)
        assert mask_array.shape == (32, 32, 16)

        # Step 3: 质量门闸
        checker = ImagingQualityGateChecker(study_id="INT-TEST-001")
        gate_result = checker.run_gate_img1(self.image_path, self.mask_path)
        assert gate_result.verdict.value in ("PASS", "CONDITIONAL")

        # Step 4: 特征提取
        extractor = RadiomicsExtractor()
        features = extractor.extract_all(image_array, mask_array)
        assert "shape" in features
        assert "firstorder" in features
        assert "texture" in features

        # Step 5: 转换为 DataFrame
        feature_df = extractor.to_dataframe(features)
        assert len(feature_df) > 0

        # 重塑为样本×特征格式
        feature_matrix = pd.DataFrame(
            [{row["feature_name"]: row["value"] for _, row in feature_df.iterrows()}]
        )

        # Step 6: 特征选择
        selector = FeatureSelector()
        selected = selector.auto_select(feature_matrix, labels=None, n_features=20)
        assert selected.shape[1] <= 20
        assert selected.shape[0] == 1

        # Step 7: 导出 Schema
        output_dir = os.path.join(self.tmpdir, "output")
        schema_paths = extractor.export_v1_schema(features, output_dir)
        assert Path(schema_paths["feature_matrix"]).exists()
        assert Path(schema_paths["feature_metadata"]).exists()

    def test_gate_blocked_for_bad_file(self):
        """测试门闸阻断无效文件"""
        from msra_modules.medical_imaging.quality_gates import ImagingQualityGateChecker

        checker = ImagingQualityGateChecker(study_id="INT-TEST-002")
        result = checker.run_gate_img1("/nonexistent/bad.nii.gz")

        assert result.verdict.value == "BLOCKED"

    def test_radiomics_with_synthetic_data(self):
        """测试特征提取在合成数据上的基本功能"""
        from msra_modules.medical_imaging.radiomics import RadiomicsExtractor

        extractor = RadiomicsExtractor()

        # 使用 setup_method 中创建的数据
        features = extractor.extract_all(self.image_data, self.mask_data)

        # 验证特征数量
        total_features = sum(len(v) for v in features.values())
        assert total_features > 10  # 至少应有 10+ 个特征

        # 验证特征值类型
        for class_name, class_features in features.items():
            for fname, fval in class_features.items():
                assert isinstance(fval, (int, float)), (
                    f"Feature {class_name}.{fname} has type {type(fval)}"
                )

    def test_feature_selection_methods(self):
        """测试多种特征选择方法的一致性"""
        from msra_modules.medical_imaging.radiomics import RadiomicsExtractor
        from msra_modules.medical_imaging.feature_selection import FeatureSelector

        extractor = RadiomicsExtractor()
        features = extractor.extract_all(self.image_data, self.mask_data)
        feature_df = extractor.to_dataframe(features)

        # 重塑
        feature_matrix = pd.DataFrame(
            [{row["feature_name"]: row["value"] for _, row in feature_df.iterrows()}]
        )

        selector = FeatureSelector()

        # 方差过滤
        result_var = selector.variance_threshold(feature_matrix)
        assert result_var.shape[1] <= feature_matrix.shape[1]

        # 相关性过滤
        result_corr = selector.correlation_filter(feature_matrix)
        assert result_corr.shape[1] <= feature_matrix.shape[1]

        # 自动选择（无标签）
        result_auto = selector.auto_select(feature_matrix, labels=None, n_features=10)
        assert result_auto.shape[1] <= 10
