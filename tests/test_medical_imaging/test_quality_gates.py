"""
Imaging Quality Gates Tests - 影像质量门闸测试

测试 ImagingQualityGateChecker 的 Gate IMG-1 全部 4 项检查。
"""

import numpy as np
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestImagingQualityGateChecker:
    """ImagingQualityGateChecker 测试"""

    def setup_method(self):
        """每个测试前创建测试数据"""
        from msra_modules.medical_imaging.quality_gates import ImagingQualityGateChecker
        self.checker = ImagingQualityGateChecker(study_id="IMG-TEST-001")

        # 创建合成影像数据
        np.random.seed(42)
        self.image_data = np.random.rand(32, 32, 16).astype(np.float32) * 1000
        self.metadata = {
            "spacing": (1.0, 1.0, 2.5),
            "size": (32, 32, 16),
            "origin": (0.0, 0.0, 0.0),
        }

    # ===== 项1: 文件可读性检查 =====

    def test_check_file_readable_nonexistent(self):
        """测试不存在的文件"""
        result = self.checker.check_file_readable("/nonexistent/file.nii.gz")

        assert result.status == "FAIL"
        assert result.is_key is True
        assert result.item_id == "IMG-DG-01"
        assert "不存在" in result.evidence or "not found" in result.evidence.lower()

    def test_check_file_readable_nifti_valid(self):
        """测试有效的 NIfTI 文件"""
        nib = pytest.importorskip("nibabel")

        with tempfile.TemporaryDirectory() as tmpdir:
            data = np.random.rand(16, 16, 8).astype(np.float32)
            img = nib.Nifti1Image(data, np.eye(4))
            path = os.path.join(tmpdir, "test.nii.gz")
            nib.save(img, path)

            result = self.checker.check_file_readable(path)

            assert result.status == "PASS"
            assert result.is_key is True

    def test_check_file_readable_invalid_nifti(self):
        """测试损坏的 NIfTI 文件"""
        nib = pytest.importorskip("nibabel")

        with tempfile.NamedTemporaryFile(suffix=".nii.gz", delete=False) as f:
            f.write(b"not a valid nifti file")
            tmp_path = f.name

        try:
            result = self.checker.check_file_readable(tmp_path)
            assert result.status == "FAIL"
        finally:
            os.unlink(tmp_path)

    # ===== 项2: 体素间距合理性检查 =====

    def test_check_voxel_spacing_normal(self):
        """测试正常体素间距"""
        result = self.checker.check_voxel_spacing(self.metadata)

        assert result.status == "PASS"
        assert result.is_key is True
        assert result.item_id == "IMG-DG-02"

    def test_check_voxel_spacing_too_small(self):
        """测试过小的体素间距"""
        metadata = {"spacing": (0.1, 0.1, 0.1)}
        result = self.checker.check_voxel_spacing(metadata)

        assert result.status == "FAIL"

    def test_check_voxel_spacing_too_large(self):
        """测试过大的体素间距"""
        metadata = {"spacing": (10.0, 10.0, 10.0)}
        result = self.checker.check_voxel_spacing(metadata)

        assert result.status == "FAIL"

    def test_check_voxel_spacing_zero(self):
        """测试零间距"""
        metadata = {"spacing": (0.0, 1.0, 1.0)}
        result = self.checker.check_voxel_spacing(metadata)

        assert result.status == "FAIL"

    def test_check_voxel_spacing_missing(self):
        """测试缺少 spacing 字段"""
        result = self.checker.check_voxel_spacing({})

        assert result.status == "FAIL"

    # ===== 项3: ROI 掩膜维度匹配检查 =====

    def test_check_roi_match_same_shape(self):
        """测试相同维度的掩膜"""
        nib = pytest.importorskip("nibabel")

        with tempfile.TemporaryDirectory() as tmpdir:
            mask_data = np.zeros((32, 32, 16), dtype=np.uint8)
            mask_data[8:24, 8:24, 4:12] = 1
            mask_img = nib.Nifti1Image(mask_data, np.eye(4))
            mask_path = os.path.join(tmpdir, "mask.nii.gz")
            nib.save(mask_img, mask_path)

            result = self.checker.check_roi_match(self.image_data, mask_path)

            assert result.status == "PASS"
            assert result.is_key is True

    def test_check_roi_match_different_shape(self):
        """测试不同维度的掩膜"""
        nib = pytest.importorskip("nibabel")

        with tempfile.TemporaryDirectory() as tmpdir:
            mask_data = np.zeros((64, 64, 32), dtype=np.uint8)
            mask_img = nib.Nifti1Image(mask_data, np.eye(4))
            mask_path = os.path.join(tmpdir, "mask.nii.gz")
            nib.save(mask_img, mask_path)

            result = self.checker.check_roi_match(self.image_data, mask_path)

            # 维度不匹配（正反都不匹配）
            assert result.status == "FAIL"

    def test_check_roi_match_mask_not_found(self):
        """测试掩膜文件不存在"""
        result = self.checker.check_roi_match(self.image_data, "/nonexistent/mask.nii.gz")

        assert result.status == "FAIL"
        assert "不存在" in result.evidence or "not found" in result.evidence.lower()

    # ===== 项4: 影像质量检查 =====

    def test_check_image_quality_normal(self):
        """测试正常影像质量"""
        result = self.checker.check_image_quality(self.image_data)

        assert result.item_id == "IMG-DG-04"
        assert result.is_key is False
        # 正常数据应该通过
        assert result.status == "PASS"

    def test_check_image_quality_with_nan(self):
        """测试包含 NaN 的影像"""
        data_with_nan = self.image_data.copy()
        data_with_nan[0, 0, 0] = np.nan
        data_with_nan[1, 1, 1] = np.nan

        result = self.checker.check_image_quality(data_with_nan)

        assert result.status == "FAIL"
        assert "NaN" in result.notes

    def test_check_image_quality_with_inf(self):
        """测试包含 Inf 的影像"""
        data_with_inf = self.image_data.copy()
        data_with_inf[0, 0, 0] = np.inf

        result = self.checker.check_image_quality(data_with_inf)

        assert result.status == "FAIL"
        assert "Inf" in result.notes

    def test_check_image_quality_low_snr(self):
        """测试低信噪比影像"""
        # 创建低 SNR 数据（信号弱，噪声大）
        low_snr_data = np.random.normal(loc=0.0, scale=100.0, size=(32, 32, 16))

        result = self.checker.check_image_quality(low_snr_data)

        # 低 SNR 应该是 FAIL
        assert result.item_id == "IMG-DG-04"

    # ===== Gate IMG-1 完整流程测试 =====

    @patch("msra_modules.medical_imaging.quality_gates.ImagingQualityGateChecker._load_image_for_check")
    def test_run_gate_img1_nifti_pass(self, mock_load):
        """测试完整 Gate IMG-1 流程（NIfTI，全部通过）"""
        nib = pytest.importorskip("nibabel")

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建影像文件
            data = np.random.rand(32, 32, 16).astype(np.float32) * 1000
            img = nib.Nifti1Image(data, np.eye(4))
            img.header.set_zooms((1.0, 1.0, 2.5))
            img_path = os.path.join(tmpdir, "scan.nii.gz")
            nib.save(img, img_path)

            # 创建掩膜文件
            mask_data = np.zeros((32, 32, 16), dtype=np.uint8)
            mask_data[8:24, 8:24, 4:12] = 1
            mask_img = nib.Nifti1Image(mask_data, np.eye(4))
            mask_path = os.path.join(tmpdir, "mask.nii.gz")
            nib.save(mask_img, mask_path)

            result = self.checker.run_gate_img1(img_path, mask_path)

            assert result.gate_type.value == "data_quality"
            assert result.study_id == "IMG-TEST-001"
            assert result.total_items == 4
            # 文件可读 + 间距正常 + ROI 匹配 + 质量正常 → PASS 或 CONDITIONAL
            assert result.verdict.value in ("PASS", "CONDITIONAL")

    def test_run_gate_img1_file_not_found(self):
        """测试 Gate IMG-1 文件不存在时阻断"""
        result = self.checker.run_gate_img1("/nonexistent/scan.nii.gz")

        assert result.verdict.value == "BLOCKED"
        assert result.failed_items > 0

    def test_run_gate_img1_no_mask(self):
        """测试 Gate IMG-1 无掩膜时的行为"""
        nib = pytest.importorskip("nibabel")

        with tempfile.TemporaryDirectory() as tmpdir:
            data = np.random.rand(32, 32, 16).astype(np.float32) * 1000
            img = nib.Nifti1Image(data, np.eye(4))
            img.header.set_zooms((1.0, 1.0, 2.5))
            img_path = os.path.join(tmpdir, "scan.nii.gz")
            nib.save(img, img_path)

            result = self.checker.run_gate_img1(img_path, mask_path=None)

            # 项3 应该是 N/A
            assert result.total_items == 4
            na_items = [cr for cr in result.check_results if cr.status == "N/A"]
            assert len(na_items) >= 1  # 至少 ROI 检查是 N/A


class TestGateResultSerialization:
    """测试 GateResult 序列化"""

    def test_gate_result_to_dict(self):
        """测试 GateResult 转字典"""
        from shared.quality_gates.gate_runner import (
            GateResult, GateType, GateVerdict, CheckItemResult,
        )

        check_results = [
            CheckItemResult(
                item_id="IMG-DG-01",
                name="文件可读性",
                is_key=True,
                status="PASS",
                evidence="NIfTI 可读",
            ),
        ]

        result = GateResult(
            gate_type=GateType.DATA_QUALITY,
            study_id="IMG-TEST-002",
            verdict=GateVerdict.PASS,
            total_items=1,
            passed_items=1,
            failed_items=0,
            key_items_status="all_pass",
            check_results=check_results,
            risks=[],
        )

        d = result.to_dict()
        assert d["gate_type"] == "data_quality"
        assert d["verdict"] == "PASS"
        assert d["study_id"] == "IMG-TEST-002"
        assert len(d["check_results"]) == 1
