"""
Medical Imaging Quality Gates - 医学影像质量门闸

实现 Gate IMG-1（数据质量门闸）。
复用 shared/quality_gates/ 框架的 GateRunner + CheckItemResult 模式。
"""

import numpy as np
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging
import sys

logger = logging.getLogger(__name__)

# 确保 shared 目录在 import 路径中
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from shared.quality_gates.gate_runner import (
    GateRunner,
    GateType,
    GateResult,
    GateVerdict,
    CheckItemResult,
    RunMode,
)


class ImagingQualityGateChecker:
    """影像质量门闸检查器

    封装 Gate IMG-1 的具体检查逻辑，
    产出 CheckItemResult 列表供 GateRunner 消费。

    Usage:
        checker = ImagingQualityGateChecker(study_id="IMG-2026-001")

        # Gate IMG-1: 数据质量检查
        gate_result = checker.run_gate_img1(
            image_path="/path/to/scan.nii.gz",
            mask_path="/path/to/mask.nii.gz"
        )
    """

    def __init__(
        self,
        study_id: str,
        project_root: Optional[str] = None,
    ):
        """初始化影像质量门闸检查器

        Args:
            study_id: 研究编号
            project_root: 项目根目录 (可选)
        """
        self.study_id = study_id
        self._runner = GateRunner(
            study_id=study_id,
            project_root=project_root,
        )

    # ===== Gate IMG-1: 影像数据质量门闸 =====

    def run_gate_img1(
        self,
        image_path: str,
        mask_path: Optional[str] = None,
    ) -> GateResult:
        """执行 Gate IMG-1 全部 4 项检查

        Args:
            image_path: 影像文件路径 (DICOM/NIfTI/NRRD)
            mask_path: ROI 掩膜文件路径 (可选)

        Returns:
            GateResult: 判定结果 (PASS / CONDITIONAL / BLOCKED)
        """
        check_results: List[CheckItemResult] = []

        # 项1: [🔑] 文件可读性检查
        check_results.append(self._check_file_readable(image_path))

        # 尝试加载影像以供后续检查
        image_data = None
        image_metadata: Dict[str, Any] = {}
        if check_results[-1].status == "PASS":
            try:
                image_data, image_metadata = self._load_image_for_check(image_path)
            except Exception:
                pass

        # 项2: [🔑] 体素间距合理性
        if image_metadata:
            check_results.append(
                self._check_voxel_spacing(image_metadata)
            )
        else:
            check_results.append(CheckItemResult(
                item_id="IMG-DG-02",
                name="体素间距合理性 [🔑]",
                is_key=True,
                status="N/A",
                evidence="影像文件无法读取，跳过体素间距检查",
                notes="请先修复文件可读性问题",
            ))

        # 项3: [🔑] ROI 掩膜与影像维度匹配
        if mask_path is not None and image_data is not None:
            check_results.append(
                self._check_roi_match(image_data, mask_path)
            )
        elif mask_path is None:
            check_results.append(CheckItemResult(
                item_id="IMG-DG-03",
                name="ROI掩膜维度匹配 [🔑]",
                is_key=True,
                status="N/A",
                evidence="未提供 mask_path，跳过 ROI 维度检查",
                notes="如使用分割模式，可跳过此项",
            ))
        else:
            check_results.append(CheckItemResult(
                item_id="IMG-DG-03",
                name="ROI掩膜维度匹配 [🔑]",
                is_key=True,
                status="N/A",
                evidence="影像文件无法读取，跳过 ROI 维度检查",
                notes="请先修复文件可读性问题",
            ))

        # 项4: [ ] 影像质量 (SNR + NaN/Inf)
        if image_data is not None:
            check_results.append(
                self._check_image_quality(image_data)
            )
        else:
            check_results.append(CheckItemResult(
                item_id="IMG-DG-04",
                name="影像质量",
                is_key=False,
                status="N/A",
                evidence="影像数据无法获取，跳过质量检查",
                notes="请先修复文件可读性问题",
            ))

        return self._build_gate_result(
            gate_type=GateType.DATA_QUALITY,
            check_results=check_results,
            total_items=4,
        )

    def check_file_readable(self, file_path: str) -> CheckItemResult:
        """公开接口: 检查文件可读性

        Args:
            file_path: 文件路径

        Returns:
            CheckItemResult
        """
        return self._check_file_readable(file_path)

    def check_voxel_spacing(
        self,
        image_metadata: Dict[str, Any],
        min_spacing: float = 0.5,
        max_spacing: float = 5.0,
    ) -> CheckItemResult:
        """公开接口: 检查体素间距合理性

        Args:
            image_metadata: 影像元数据 (需含 spacing 字段)
            min_spacing: 最小允许间距 (mm)
            max_spacing: 最大允许间距 (mm)

        Returns:
            CheckItemResult
        """
        return self._check_voxel_spacing(image_metadata, min_spacing, max_spacing)

    def check_roi_match(
        self,
        image_data: np.ndarray,
        mask_path: str,
    ) -> CheckItemResult:
        """公开接口: 检查 ROI 掩膜与影像维度匹配

        Args:
            image_data: 影像 numpy 数组
            mask_path: 掩膜文件路径

        Returns:
            CheckItemResult
        """
        return self._check_roi_match(image_data, mask_path)

    def check_image_quality(
        self,
        image_data: np.ndarray,
    ) -> CheckItemResult:
        """公开接口: 检查影像质量

        Args:
            image_data: 影像 numpy 数组

        Returns:
            CheckItemResult
        """
        return self._check_image_quality(image_data)

    def _check_file_readable(self, file_path: str) -> CheckItemResult:
        """[🔑] 项1: 文件可读性检查

        检查文件是否存在且可以被相应库读取。

        Args:
            file_path: 影像文件路径

        Returns:
            CheckItemResult
        """
        path = Path(file_path)

        # 检查文件是否存在
        if not path.exists():
            return CheckItemResult(
                item_id="IMG-DG-01",
                name="文件可读性 [🔑]",
                is_key=True,
                status="FAIL",
                evidence=f"文件不存在: {file_path}",
                notes="请检查文件路径是否正确",
            )

        if path.is_dir():
            # DICOM 目录：检查是否包含 DICOM 文件
            try:
                sitk = self._get_sitk()
                series_ids = sitk.ImageSeriesReader.GetGDCMSeriesIDs(str(path))
                if not series_ids:
                    return CheckItemResult(
                        item_id="IMG-DG-01",
                        name="文件可读性 [🔑]",
                        is_key=True,
                        status="FAIL",
                        evidence=f"目录中无 DICOM 序列: {file_path}",
                        notes="请确认目录包含有效的 DICOM 文件",
                    )
                return CheckItemResult(
                    item_id="IMG-DG-01",
                    name="文件可读性 [🔑]",
                    is_key=True,
                    status="PASS",
                    evidence=f"DICOM 目录可读，包含 {len(series_ids)} 个序列",
                )
            except ImportError:
                return CheckItemResult(
                    item_id="IMG-DG-01",
                    name="文件可读性 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence="SimpleITK 未安装，无法读取 DICOM",
                    notes="请安装: pip install SimpleITK",
                )
            except Exception as e:
                return CheckItemResult(
                    item_id="IMG-DG-01",
                    name="文件可读性 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence=f"DICOM 目录读取失败: {file_path}",
                    notes=str(e),
                )

        # 文件：检查后缀
        suffix = path.suffix.lower()
        if suffix in (".nii", ".gz"):
            # NIfTI
            try:
                import nibabel as nib
                img = nib.load(str(path))
                # 尝试读取 header 确认文件完整
                _ = img.header
                _ = img.shape
                return CheckItemResult(
                    item_id="IMG-DG-01",
                    name="文件可读性 [🔑]",
                    is_key=True,
                    status="PASS",
                    evidence=f"NIfTI 文件可读: shape={img.shape}",
                )
            except ImportError:
                return CheckItemResult(
                    item_id="IMG-DG-01",
                    name="文件可读性 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence="nibabel 未安装，无法读取 NIfTI",
                    notes="请安装: pip install nibabel",
                )
            except Exception as e:
                return CheckItemResult(
                    item_id="IMG-DG-01",
                    name="文件可读性 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence=f"NIfTI 文件读取失败: {file_path}",
                    notes=str(e),
                )
        elif suffix == ".nrrd":
            # NRRD
            try:
                sitk = self._get_sitk()
                img = sitk.ReadImage(str(path))
                return CheckItemResult(
                    item_id="IMG-DG-01",
                    name="文件可读性 [🔑]",
                    is_key=True,
                    status="PASS",
                    evidence=f"NRRD 文件可读: size={img.GetSize()}",
                )
            except ImportError:
                return CheckItemResult(
                    item_id="IMG-DG-01",
                    name="文件可读性 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence="SimpleITK 未安装，无法读取 NRRD",
                    notes="请安装: pip install SimpleITK",
                )
            except Exception as e:
                return CheckItemResult(
                    item_id="IMG-DG-01",
                    name="文件可读性 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence=f"NRRD 文件读取失败: {file_path}",
                    notes=str(e),
                )
        else:
            # 其他格式，尝试 SimpleITK
            try:
                sitk = self._get_sitk()
                img = sitk.ReadImage(str(path))
                return CheckItemResult(
                    item_id="IMG-DG-01",
                    name="文件可读性 [🔑]",
                    is_key=True,
                    status="PASS",
                    evidence=f"文件可读 ({suffix}): size={img.GetSize()}",
                )
            except Exception as e:
                return CheckItemResult(
                    item_id="IMG-DG-01",
                    name="文件可读性 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence=f"文件读取失败: {file_path}",
                    notes=str(e),
                )

    def _check_voxel_spacing(
        self,
        image_metadata: Dict[str, Any],
        min_spacing: float = 0.5,
        max_spacing: float = 5.0,
    ) -> CheckItemResult:
        """[🔑] 项2: 体素间距合理性

        检查影像的体素间距是否在合理范围内。

        Args:
            image_metadata: 影像元数据 (需含 spacing 字段)
            min_spacing: 最小允许间距 (mm)
            max_spacing: 最大允许间距 (mm)

        Returns:
            CheckItemResult
        """
        try:
            spacing = image_metadata.get("spacing")
            if spacing is None:
                return CheckItemResult(
                    item_id="IMG-DG-02",
                    name="体素间距合理性 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence="元数据中无 spacing 字段",
                    notes="无法提取体素间距信息",
                )

            # spacing 可能是 tuple/list
            if isinstance(spacing, (tuple, list)):
                spacings = [float(s) for s in spacing]
            else:
                spacings = [float(spacing)]

            issues: List[str] = []
            for i, s in enumerate(spacings):
                if s < min_spacing:
                    issues.append(f"轴{i} 间距 {s:.2f}mm < {min_spacing}mm")
                if s > max_spacing:
                    issues.append(f"轴{i} 间距 {s:.2f}mm > {max_spacing}mm")
                if s <= 0:
                    issues.append(f"轴{i} 间距 {s:.2f}mm ≤ 0")

            if not issues:
                return CheckItemResult(
                    item_id="IMG-DG-02",
                    name="体素间距合理性 [🔑]",
                    is_key=True,
                    status="PASS",
                    evidence=f"体素间距: {spacings}，均在 [{min_spacing}, {max_spacing}]mm 范围内",
                )
            else:
                return CheckItemResult(
                    item_id="IMG-DG-02",
                    name="体素间距合理性 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence=f"体素间距: {spacings}",
                    notes="；".join(issues),
                )

        except Exception as e:
            return CheckItemResult(
                item_id="IMG-DG-02",
                name="体素间距合理性 [🔑]",
                is_key=True,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    def _check_roi_match(
        self,
        image_data: np.ndarray,
        mask_path: str,
    ) -> CheckItemResult:
        """[🔑] 项3: ROI 掩膜与影像维度匹配

        Args:
            image_data: 影像 numpy 数组
            mask_path: 掩膜文件路径

        Returns:
            CheckItemResult
        """
        try:
            mask_path_obj = Path(mask_path)

            if not mask_path_obj.exists():
                return CheckItemResult(
                    item_id="IMG-DG-03",
                    name="ROI掩膜维度匹配 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence=f"掩膜文件不存在: {mask_path}",
                    notes="请检查掩膜文件路径",
                )

            # 加载掩膜
            suffix = mask_path_obj.suffix.lower()
            mask_data = None

            if suffix in (".nii", ".gz"):
                import nibabel as nib
                mask_img = nib.load(str(mask_path_obj))
                mask_data = np.asarray(mask_img.dataobj)
            elif suffix == ".nrrd":
                sitk = self._get_sitk()
                mask_img = sitk.ReadImage(str(mask_path_obj))
                mask_data = sitk.GetArrayFromImage(mask_img)
            else:
                sitk = self._get_sitk()
                mask_img = sitk.ReadImage(str(mask_path_obj))
                mask_data = sitk.GetArrayFromImage(mask_img)

            # 比较维度
            image_shape = image_data.shape
            mask_shape = mask_data.shape

            # SimpleITK 的 GetArrayFromImage 返回 (z, y, x)，
            # 而 nibabel 返回 (x, y, z)，需要考虑维度对齐
            if image_shape == mask_shape:
                return CheckItemResult(
                    item_id="IMG-DG-03",
                    name="ROI掩膜维度匹配 [🔑]",
                    is_key=True,
                    status="PASS",
                    evidence=f"影像维度 {image_shape}，掩膜维度 {mask_shape}，完全匹配",
                )
            elif image_shape == mask_shape[::-1]:
                return CheckItemResult(
                    item_id="IMG-DG-03",
                    name="ROI掩膜维度匹配 [🔑]",
                    is_key=True,
                    status="PASS",
                    evidence=(
                        f"影像维度 {image_shape}，掩膜维度 {mask_shape}，"
                        f"反转后匹配（可能为不同坐标系约定）"
                    ),
                )
            else:
                return CheckItemResult(
                    item_id="IMG-DG-03",
                    name="ROI掩膜维度匹配 [🔑]",
                    is_key=True,
                    status="FAIL",
                    evidence=f"影像维度 {image_shape}，掩膜维度 {mask_shape}",
                    notes="ROI 掩膜与影像维度不匹配，请使用相同空间的掩膜",
                )

        except ImportError as e:
            return CheckItemResult(
                item_id="IMG-DG-03",
                name="ROI掩膜维度匹配 [🔑]",
                is_key=True,
                status="FAIL",
                evidence="缺少必要的影像加载库",
                notes=str(e),
            )
        except Exception as e:
            return CheckItemResult(
                item_id="IMG-DG-03",
                name="ROI掩膜维度匹配 [🔑]",
                is_key=True,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    def _check_image_quality(
        self,
        image_data: np.ndarray,
    ) -> CheckItemResult:
        """[ ] 项4: 影像质量检查

        检查 SNR（信噪比）和 NaN/Inf 异常值。

        Args:
            image_data: 影像 numpy 数组

        Returns:
            CheckItemResult
        """
        try:
            issues: List[str] = []

            # 检查 NaN
            has_nan = bool(np.any(np.isnan(image_data)))
            if has_nan:
                nan_count = int(np.sum(np.isnan(image_data)))
                issues.append(f"包含 {nan_count} 个 NaN 值")

            # 检查 Inf
            has_inf = bool(np.any(np.isinf(image_data)))
            if has_inf:
                inf_count = int(np.sum(np.isinf(image_data)))
                issues.append(f"包含 {inf_count} 个 Inf 值")

            # 计算 SNR（简化版：信号均值 / 背景标准差）
            # 假设信号为前景（高于中位数的区域），背景为低于 5 百分位的区域
            snr = 0.0
            try:
                valid_data = image_data[np.isfinite(image_data)]
                if len(valid_data) > 0:
                    signal_mask = valid_data > np.median(valid_data)
                    background_mask = valid_data < np.percentile(valid_data, 5)

                    if np.sum(background_mask) > 0:
                        signal_mean = float(np.mean(valid_data[signal_mask]))
                        background_std = float(np.std(valid_data[background_mask]))
                        if background_std > 0:
                            snr = signal_mean / background_std

                    if snr < 5.0:
                        issues.append(f"信噪比 SNR={snr:.2f} < 5.0")
            except Exception:
                snr = -1.0
                issues.append("SNR 计算失败")

            if not issues:
                return CheckItemResult(
                    item_id="IMG-DG-04",
                    name="影像质量",
                    is_key=False,
                    status="PASS",
                    evidence=f"无 NaN/Inf，SNR={snr:.2f}",
                )
            else:
                return CheckItemResult(
                    item_id="IMG-DG-04",
                    name="影像质量",
                    is_key=False,
                    status="FAIL",
                    evidence=f"SNR={snr:.2f}",
                    notes="；".join(issues),
                )

        except Exception as e:
            return CheckItemResult(
                item_id="IMG-DG-04",
                name="影像质量",
                is_key=False,
                status="FAIL",
                evidence="检查过程中发生错误",
                notes=str(e),
            )

    def _load_image_for_check(self, image_path: str) -> tuple:
        """加载影像用于门闸检查

        Args:
            image_path: 影像文件路径

        Returns:
            (numpy_array, metadata_dict)
        """
        path = Path(image_path)
        suffix = path.suffix.lower()

        if suffix in (".nii", ".gz"):
            from .image_loader import load_nifti
            return load_nifti(image_path)
        elif suffix == ".nrrd":
            from .image_loader import load_nrrd
            return load_nrrd(image_path)
        elif path.is_dir():
            from .image_loader import DICOMLoader
            loader = DICOMLoader()
            image = loader.load_dicom_series(image_path)
            array = loader.to_numpy(image)
            metadata = loader.extract_metadata(image)
            return array, metadata
        else:
            # 尝试 SimpleITK
            sitk = self._get_sitk()
            image = sitk.ReadImage(str(path))
            array = sitk.GetArrayFromImage(image)
            metadata = {
                "size": image.GetSize(),
                "spacing": image.GetSpacing(),
                "origin": image.GetOrigin(),
                "direction": image.GetDirection(),
            }
            return array, metadata

    def _get_sitk(self):
        """延迟导入 SimpleITK"""
        try:
            import SimpleITK as sitk
            return sitk
        except ImportError as e:
            raise ImportError(
                f"SimpleITK is required: {e}. "
                "Install with: pip install SimpleITK"
            )

    def _build_gate_result(
        self,
        gate_type: GateType,
        check_results: List[CheckItemResult],
        total_items: int,
    ) -> GateResult:
        """构建 GateResult

        使用与 BioQualityGateChecker 相同的判定逻辑，
        适配 IMG 门闸的自定义检查项。

        Args:
            gate_type: 门闸类型
            check_results: 检查结果列表
            total_items: 总检查项数

        Returns:
            GateResult
        """
        # 统计结果 (排除 N/A 和 SKIP)
        evaluable = [cr for cr in check_results if cr.status not in ("N/A", "SKIP")]
        passed = sum(1 for cr in evaluable if cr.status == "PASS")
        failed = sum(1 for cr in evaluable if cr.status == "FAIL")
        key_failed = [cr for cr in evaluable if cr.is_key and cr.status == "FAIL"]

        # 判定逻辑
        if failed == 0:
            verdict = GateVerdict.PASS
            key_status = "all_pass"
        elif len(key_failed) > 0:
            verdict = GateVerdict.BLOCKED
            key_status = f"item_{key_failed[0].item_id}_failed"
        elif failed <= 2:
            verdict = GateVerdict.CONDITIONAL
            key_status = "all_pass"
        else:
            verdict = GateVerdict.BLOCKED
            key_status = f"{failed}_items_failed"

        # 风险评估
        risks: List[str] = []
        for cr in check_results:
            if cr.status == "FAIL":
                level = "关键" if cr.is_key else "一般"
                risks.append(f"[{level}] {cr.name}: {cr.notes or cr.evidence}")

        return GateResult(
            gate_type=gate_type,
            study_id=self.study_id,
            verdict=verdict,
            total_items=total_items,
            passed_items=passed,
            failed_items=failed,
            key_items_status=key_status,
            check_results=check_results,
            risks=risks,
        )
