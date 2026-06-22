"""
DICOM Image Loader - DICOM影像加载器

IMG-002: SimpleITK图像加载器
IMG-003: DICOM元数据提取器
"""

from __future__ import annotations
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple, List, TYPE_CHECKING
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
            f"SimpleITK is required for DICOM loading: {e}. "
            "Install with: pip install SimpleITK"
        )


class DICOMLoader:
    """DICOM影像加载器"""

    def __init__(self, window_level: Optional[float] = None,
                 window_width: Optional[float] = None):
        """初始化DICOM加载器

        Args:
            window_level: 窗位 (HU中心值)
            window_width: 窗宽 (HU范围)
        """
        self.window_level = window_level
        self.window_width = window_width

    def load_dicom_series(self, dicom_dir: str):
        """加载DICOM序列

        Args:
            dicom_dir: DICOM文件目录

        Returns:
            SimpleITK Image对象

        Raises:
            FileNotFoundError: 目录不存在或无DICOM文件
        """
        sitk = _get_sitk()
        dicom_path = Path(dicom_dir)
        if not dicom_path.exists():
            raise FileNotFoundError(f"DICOM directory not found: {dicom_dir}")

        # 获取DICOM文件列表
        series_ids = sitk.ImageSeriesReader.GetGDCMSeriesIDs(str(dicom_path))
        if not series_ids:
            raise FileNotFoundError(f"No DICOM series found in: {dicom_dir}")

        # 使用第一个序列
        series_id = series_ids[0]
        file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(
            str(dicom_path), series_id
        )

        reader = sitk.ImageSeriesReader()
        reader.SetFileNames(file_names)
        image = reader.Execute()

        logger.info(f"Loaded DICOM series: {len(file_names)} slices, "
                    f"size={image.GetSize()}")
        return image

    def load_dicom(self, dicom_path: str):
        """加载单个DICOM文件

        Args:
            dicom_path: DICOM文件路径

        Returns:
            SimpleITK Image对象
        """
        sitk = _get_sitk()
        path = Path(dicom_path)
        if not path.exists():
            raise FileNotFoundError(f"DICOM file not found: {dicom_path}")

        image = sitk.ReadImage(str(path))
        logger.info(f"Loaded DICOM: size={image.GetSize()}, "
                    f"spacing={image.GetSpacing()}")
        return image

    def to_numpy(self, image) -> np.ndarray:
        """将SimpleITK Image转换为numpy数组

        Args:
            image: SimpleITK Image

        Returns:
            numpy数组 (D, H, W) 或 (H, W)
        """
        sitk = _get_sitk()
        array = sitk.GetArrayFromImage(image)
        return array

    def extract_metadata(self, image) -> Dict:
        """提取DICOM元数据

        Args:
            image: SimpleITK Image

        Returns:
            元数据字典
        """
        metadata = {
            "size": image.GetSize(),
            "spacing": image.GetSpacing(),
            "origin": image.GetOrigin(),
            "direction": image.GetDirection(),
            "pixel_type": image.GetPixelIDTypeAsString(),
            "dimensions": image.GetDimension(),
        }

        # 尝试提取DICOM标签
        dicom_tags = {
            "0010|0010": "patient_name",
            "0010|0020": "patient_id",
            "0010|0030": "patient_birth_date",
            "0010|0040": "patient_sex",
            "0008|0020": "study_date",
            "0008|0030": "study_time",
            "0008|0060": "modality",
            "0008|0070": "manufacturer",
            "0018|0050": "slice_thickness",
            "0018|0060": "kvp",
            "0018|0088": "spacing_between_slices",
            "0028|0010": "rows",
            "0028|0011": "columns",
            "0028|0030": "pixel_spacing",
        }

        for tag, name in dicom_tags.items():
            value = image.GetMetaData(tag, "")
            if value:
                metadata[name] = value

        return metadata

    def apply_window(self, image,
                     window_level: Optional[float] = None,
                     window_width: Optional[float] = None):
        """应用窗宽窗位

        Args:
            image: 输入图像
            window_level: 窗位 (默认使用初始化值)
            window_width: 窗宽 (默认使用初始化值)

        Returns:
            窗宽窗位调整后的图像
        """
        sitk = _get_sitk()
        wl = window_level if window_level is not None else self.window_level
        ww = window_width if window_width is not None else self.window_width

        if wl is None or ww is None:
            return image

        # 使用IntensityWindowing
        lower = wl - ww / 2
        upper = wl + ww / 2
        return sitk.IntensityWindowing(
            image,
            windowMinimum=lower,
            windowMaximum=upper,
            outputMinimum=0,
            outputMaximum=255
        )


def load_dicom_series(dicom_dir: str) -> Tuple[np.ndarray, Dict]:
    """便捷函数：加载DICOM序列并返回numpy数组和元数据

    Args:
        dicom_dir: DICOM目录

    Returns:
        (numpy_array, metadata_dict)
    """
    loader = DICOMLoader()
    image = loader.load_dicom_series(dicom_dir)
    array = loader.to_numpy(image)
    metadata = loader.extract_metadata(image)
    return array, metadata
