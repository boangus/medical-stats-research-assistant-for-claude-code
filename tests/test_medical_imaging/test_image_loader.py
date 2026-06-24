"""
Image Loader Tests - 影像加载器测试

测试 DICOMLoader、load_nifti、load_nrrd 的功能。
使用 mock 隔离 SimpleITK/nibabel 依赖。
"""

import numpy as np
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import os


# ===== DICOMLoader 测试 =====

class TestDICOMLoader:
    """DICOMLoader 测试"""

    def test_init_defaults(self):
        """测试默认初始化参数"""
        from msra_modules.medical_imaging.image_loader import DICOMLoader

        loader = DICOMLoader()
        assert loader.window_level is None
        assert loader.window_width is None

    def test_init_with_window_params(self):
        """测试带窗宽窗位参数初始化"""
        from msra_modules.medical_imaging.image_loader import DICOMLoader

        loader = DICOMLoader(window_level=40, window_width=400)
        assert loader.window_level == 40
        assert loader.window_width == 400

    @patch("msra_modules.medical_imaging.image_loader._get_sitk")
    def test_load_dicom_series_not_found(self, mock_sitk):
        """测试加载不存在的 DICOM 目录"""
        from msra_modules.medical_imaging.image_loader import DICOMLoader

        loader = DICOMLoader()
        with pytest.raises(FileNotFoundError, match="DICOM directory not found"):
            loader.load_dicom_series("/nonexistent/path")

    @patch("msra_modules.medical_imaging.image_loader._get_sitk")
    def test_load_dicom_file_not_found(self, mock_sitk):
        """测试加载不存在的 DICOM 文件"""
        from msra_modules.medical_imaging.image_loader import DICOMLoader

        loader = DICOMLoader()
        with pytest.raises(FileNotFoundError, match="DICOM file not found"):
            loader.load_dicom("/nonexistent/file.dcm")

    @patch("msra_modules.medical_imaging.image_loader._get_sitk")
    def test_to_numpy(self, mock_sitk):
        """测试 SimpleITK Image 到 numpy 转换"""
        from msra_modules.medical_imaging.image_loader import DICOMLoader

        mock_sitk_module = MagicMock()
        mock_sitk.return_value = mock_sitk_module
        mock_sitk_module.GetArrayFromImage.return_value = np.zeros((10, 64, 64))

        loader = DICOMLoader()
        mock_image = MagicMock()
        result = loader.to_numpy(mock_image)

        assert result.shape == (10, 64, 64)
        mock_sitk_module.GetArrayFromImage.assert_called_once_with(mock_image)


# ===== load_nifti 测试 =====

class TestLoadNifti:
    """load_nifti 函数测试"""

    def test_load_nifti_nibabel_not_installed(self):
        """测试 nibabel 未安装时的错误提示"""
        with patch.dict("sys.modules", {"nibabel": None}):
            with pytest.raises(ImportError, match="nibabel is required"):
                from msra_modules.medical_imaging.image_loader import load_nifti
                load_nifti("test.nii.gz")

    def test_load_nifti_file_not_found(self):
        """测试加载不存在的 NIfTI 文件"""
        # 确保 nibabel 可用
        nib = pytest.importorskip("nibabel")
        from msra_modules.medical_imaging.image_loader import load_nifti

        with pytest.raises(FileNotFoundError, match="NIfTI file not found"):
            load_nifti("/nonexistent/scan.nii.gz")

    def test_load_nifti_valid_file(self):
        """测试加载有效的 NIfTI 文件"""
        nib = pytest.importorskip("nibabel")
        from msra_modules.medical_imaging.image_loader import load_nifti

        # 创建临时 NIfTI 文件
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建 3D 测试数据
            data = np.random.rand(32, 32, 16).astype(np.float32)
            affine = np.eye(4)
            img = nib.Nifti1Image(data, affine)
            nifti_path = os.path.join(tmpdir, "test_scan.nii.gz")
            nib.save(img, nifti_path)

            # 加载并验证
            array, metadata = load_nifti(nifti_path)

            assert array.shape == (32, 32, 16)
            assert "spacing" in metadata
            assert "size" in metadata
            assert "dtype" in metadata
            assert "dimensions" in metadata
            assert metadata["dimensions"] == 3
            np.testing.assert_array_almost_equal(array, data)

    def test_load_nifti_4d_data(self):
        """测试加载 4D NIfTI 文件"""
        nib = pytest.importorskip("nibabel")
        from msra_modules.medical_imaging.image_loader import load_nifti

        with tempfile.TemporaryDirectory() as tmpdir:
            data = np.random.rand(32, 32, 16, 3).astype(np.float32)
            affine = np.eye(4)
            img = nib.Nifti1Image(data, affine)
            nifti_path = os.path.join(tmpdir, "test_4d.nii.gz")
            nib.save(img, nifti_path)

            array, metadata = load_nifti(nifti_path)

            assert array.shape == (32, 32, 16, 3)
            assert metadata["dimensions"] == 4


# ===== load_nrrd 测试 =====

class TestLoadNrrd:
    """load_nrrd 函数测试"""

    def test_load_nrrd_sitk_not_installed(self):
        """测试 SimpleITK 未安装时的错误提示"""
        with patch("msra_modules.medical_imaging.image_loader._get_sitk") as mock_get:
            mock_get.side_effect = ImportError("SimpleITK not installed")
            from msra_modules.medical_imaging.image_loader import load_nrrd

            with pytest.raises(ImportError, match="SimpleITK"):
                load_nrrd("test.nrrd")

    def test_load_nrrd_file_not_found(self):
        """测试加载不存在的 NRRD 文件"""
        sitk = pytest.importorskip("SimpleITK")
        from msra_modules.medical_imaging.image_loader import load_nrrd

        with pytest.raises(FileNotFoundError, match="NRRD file not found"):
            load_nrrd("/nonexistent/scan.nrrd")

    @patch("msra_modules.medical_imaging.image_loader._get_sitk")
    def test_load_nrrd_mock(self, mock_sitk):
        """测试 NRRD 加载（mock SimpleITK）"""
        from msra_modules.medical_imaging.image_loader import load_nrrd

        mock_sitk_module = MagicMock()
        mock_sitk.return_value = mock_sitk_module

        mock_image = MagicMock()
        mock_image.GetSize.return_value = (64, 64, 32)
        mock_image.GetSpacing.return_value = (1.0, 1.0, 2.5)
        mock_image.GetOrigin.return_value = (0.0, 0.0, 0.0)
        mock_image.GetDirection.return_value = (1, 0, 0, 0, 1, 0, 0, 0, 1)
        mock_image.GetPixelIDTypeAsString.return_value = "32-bit float"
        mock_image.GetDimension.return_value = 3
        mock_image.GetMetaData.return_value = ""

        mock_sitk_module.ReadImage.return_value = mock_image
        mock_sitk_module.GetArrayFromImage.return_value = np.zeros((32, 64, 64))

        with tempfile.NamedTemporaryFile(suffix=".nrrd", delete=False) as f:
            f.write(b"fake nrrd")
            tmp_path = f.name

        try:
            array, metadata = load_nrrd(tmp_path)

            assert array.shape == (32, 64, 64)
            assert metadata["size"] == (64, 64, 32)
            assert metadata["spacing"] == (1.0, 1.0, 2.5)
            assert metadata["dimensions"] == 3
        finally:
            os.unlink(tmp_path)


# ===== 便捷函数测试 =====

class TestLoadDicomSeries:
    """load_dicom_series 便捷函数测试"""

    @patch("msra_modules.medical_imaging.image_loader.DICOMLoader")
    def test_load_dicom_series(self, MockLoader):
        """测试 load_dicom_series 便捷函数"""
        from msra_modules.medical_imaging.image_loader import load_dicom_series

        mock_instance = MagicMock()
        MockLoader.return_value = mock_instance
        mock_instance.load_dicom_series.return_value = MagicMock()
        mock_instance.to_numpy.return_value = np.zeros((10, 64, 64))
        mock_instance.extract_metadata.return_value = {"size": (64, 64, 10)}

        array, metadata = load_dicom_series("/fake/dicom/dir")

        assert array.shape == (10, 64, 64)
        assert metadata["size"] == (64, 64, 10)
        mock_instance.load_dicom_series.assert_called_once_with("/fake/dicom/dir")
