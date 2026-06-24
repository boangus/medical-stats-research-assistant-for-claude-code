# 医学影像模块 API 参考

> **版本**: v1.0.0 | **日期**: 2026-06-26 | **状态**: Stable
> **模块**: Medical Imaging | **命令**: `/imaging`

---

## 目录

- [load_dicom_series() — DICOM 加载](#load_dicom_series)
- [load_nifti() — NIfTI 加载](#load_nifti)
- [load_nrrd() — NRRD 加载](#load_nrrd)
- [preprocess_image() — 预处理](#preprocess_image)
- [SegmentationPipeline — 分割](#segmentationpipeline)
- [ImageRegistration — 配准](#imageregistration)
- [RadiomicsExtractor — 放射组学特征](#radiomicsextractor)
- [FeatureSelector — 特征选择](#featureselector)
- [ImagingQualityGateChecker — 质量门闸](#imagingqualitygatechecker)

---

## load_dicom_series

> 便捷函数：加载 DICOM 序列并返回 numpy 数组和元数据。

**签名**:

```python
load_dicom_series(dicom_dir: str) -> Tuple[np.ndarray, Dict]
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| dicom_dir | str | — | 必填，DICOM 文件目录 |

**返回值**: `Tuple[np.ndarray, Dict]` — (numpy 数组, 元数据字典)

**示例**:

```python
from msra_modules.medical_imaging import load_dicom_series

array, metadata = load_dicom_series("data/CT_scans/")
print(f"影像维度: {array.shape}, 体素间距: {metadata['spacing']}")
```

**异常**: `FileNotFoundError` — 目录不存在或无 DICOM 文件；`ImportError` — SimpleITK 未安装

---

## load_nifti

> 便捷函数：加载 NIfTI 文件（.nii / .nii.gz）并返回 numpy 数组和元数据。

**签名**:

```python
load_nifti(nifti_path: str) -> Tuple[np.ndarray, Dict]
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| nifti_path | str | — | 必填，NIfTI 文件路径 |

**返回值**: `Tuple[np.ndarray, Dict]` — (numpy 数组, 元数据字典含 size、spacing、dtype、dimensions、affine)

**异常**: `ImportError` — nibabel 未安装；`FileNotFoundError` — 文件不存在

---

## load_nrrd

> 便捷函数：加载 NRRD 文件并返回 numpy 数组和元数据。

**签名**:

```python
load_nrrd(nrrd_path: str) -> Tuple[np.ndarray, Dict]
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| nrrd_path | str | — | 必填，NRRD 文件路径 |

**返回值**: `Tuple[np.ndarray, Dict]` — (numpy 数组, 元数据字典含 size、spacing、origin、direction、pixel_type、dimensions)

**异常**: `ImportError` — SimpleITK 未安装；`FileNotFoundError` — 文件不存在

---

## preprocess_image

> 便捷函数：标准化 numpy 数组强度（支持 min_max 和 z_score 方法）。

**签名**:

```python
normalize_intensity(array: np.ndarray, method: str = "min_max") -> np.ndarray
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| array | np.ndarray | — | 必填，输入数组 |
| method | str | "min_max" | 标准化方法（"min_max" 或 "z_score"） |

**返回值**: `np.ndarray` — 标准化后的数组

**异常**: `ValueError` — 未知方法

### DICOMLoader 类

对于更细粒度的控制，可使用 `DICOMLoader` 类：

```python
from msra_modules.medical_imaging import DICOMLoader

loader = DICOMLoader(window_level=40, window_width=400)
image = loader.load_dicom_series("data/CT_scans/")
array = loader.to_numpy(image)
metadata = loader.extract_metadata(image)
windowed = loader.apply_window(image)
```

**DICOMLoader 签名**:

```python
DICOMLoader(window_level: Optional[float] = None, window_width: Optional[float] = None)
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| window_level | Optional[float] | None | 窗位（HU 中心值） |
| window_width | Optional[float] | None | 窗宽（HU 范围） |

### ImagePreprocessor 类

```python
from msra_modules.medical_imaging import ImagePreprocessor

preprocessor = ImagePreprocessor(target_spacing=(1.0, 1.0, 1.0), normalize=True)
processed = preprocessor.preprocess_pipeline(image)
```

**ImagePreprocessor 签名**:

```python
ImagePreprocessor(target_spacing: Optional[Tuple[float, float, float]] = None, normalize: bool = True)
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| target_spacing | Optional[Tuple[float, float, float]] | None | 目标体素间距 (x, y, z) |
| normalize | bool | True | 是否标准化到 [0,1] |

**方法**: `resample()`, `normalize_intensity()`, `denoise()`, `bias_correction()`, `preprocess_pipeline()`

---

## SegmentationPipeline

> 影像分割 Pipeline，基于 MONAI 的 3D U-Net 模型。

**签名**:

```python
SegmentationPipeline(model_name: str = "spleen_ct", device: str = "cpu")
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| model_name | str | "spleen_ct" | MONAI 预训练模型名称 |
| device | str | "cpu" | 计算设备（"cpu" 或 "cuda"） |

**方法**:

### `segment`

```python
segment(image: np.ndarray) -> np.ndarray
```

执行分割。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| image | np.ndarray | — | 必填，输入影像 (D, H, W) 或 (1, D, H, W) |

**返回值**: `np.ndarray` — 分割掩码 (D, H, W)

**异常**: `ImportError` — MONAI 未安装

### `segment_with_confidence`

```python
segment_with_confidence(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]
```

分割并返回置信度图。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| image | np.ndarray | — | 必填，输入影像 |

**返回值**: `Tuple[np.ndarray, np.ndarray]` — (分割掩码, 置信度图)

### `preprocess`

```python
preprocess(image: np.ndarray) -> np.ndarray
```

预处理影像（标准化 + 添加通道维度）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| image | np.ndarray | — | 必填，输入影像 (D, H, W) |

**返回值**: `np.ndarray` — 预处理后的影像 (1, D, H, W)

**示例**:

```python
from msra_modules.medical_imaging import SegmentationPipeline

seg = SegmentationPipeline(model_name="spleen_ct", device="cuda")
mask = seg.segment(image_array)
mask, confidence = seg.segment_with_confidence(image_array)
```

---

## ImageRegistration

> 医学影像配准，支持 rigid、affine 和 bspline 变换方法。

**签名**:

```python
ImageRegistration(method: str = "rigid")
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| method | str | "rigid" | 配准方法（"rigid"、"affine"、"bspline"） |

**方法**:

### `register`

```python
register(fixed_image, moving_image, fixed_mask=None, moving_mask=None) -> Dict
```

执行配准。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| fixed_image | SimpleITK.Image | — | 必填，固定图像 |
| moving_image | SimpleITK.Image | — | 必填，移动图像 |
| fixed_mask | SimpleITK.Image | None | 固定图像掩码（可选） |
| moving_mask | SimpleITK.Image | None | 移动图像掩码（可选） |

**返回值**: `Dict` — 含 `transform`、`resampled_image`、`metric_value`、`iterations`、`method`

**异常**: `ValueError` — 未知方法

### `evaluate`

```python
evaluate(fixed_image, moving_image, mask=None) -> Dict
```

评估配准质量。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| fixed_image | SimpleITK.Image | — | 必填，固定图像 |
| moving_image | SimpleITK.Image | — | 必填，移动图像 |
| mask | SimpleITK.Image | None | 评估区域掩码（可选） |

**返回值**: `Dict` — 含 `mse`、`mae`、`correlation`、`ssim`

**示例**:

```python
from msra_modules.medical_imaging import ImageRegistration

reg = ImageRegistration(method="rigid")
result = reg.register(fixed_img, moving_img)
print(f"配准指标: {result['metric_value']:.4f}, 迭代次数: {result['iterations']}")

metrics = reg.evaluate(fixed_img, result["resampled_image"])
print(f"MSE: {metrics['mse']:.4f}, SSIM: {metrics['ssim']:.4f}")
```

---

## RadiomicsExtractor

> 影像组学特征提取器，提取形状、一阶统计和纹理特征。

**签名**:

```python
RadiomicsExtractor(bin_width: float = 25.0)
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| bin_width | float | 25.0 | 灰度直方图 bin 宽度 |

**方法**:

### `extract_shape_features`

```python
extract_shape_features(mask: np.ndarray) -> Dict[str, float]
```

提取形状特征（体积、表面积、最大 3D 直径、主轴长度、球度等）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| mask | np.ndarray | — | 必填，分割掩码（二值化） |

**返回值**: `Dict[str, float]` — 形状特征字典（VoxelVolume、SurfaceArea、Maximum3DDiameter、MajorAxisLength、MinorAxisLength、LeastAxisLength、Sphericity）

### `extract_firstorder_features`

```python
extract_firstorder_features(image: np.ndarray, mask: np.ndarray) -> Dict[str, float]
```

提取一阶统计特征（均值、中位数、标准差、偏度、峰度、能量、熵等）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| image | np.ndarray | — | 必填，影像数据 |
| mask | np.ndarray | — | 必填，分割掩码 |

**返回值**: `Dict[str, float]` — 一阶统计特征字典（Mean、Median、Std、Variance、Minimum、Maximum、Range、Percentile10/25/75/90、IQR、Skewness、Kurtosis、Energy、Entropy、RootMeanSquared、MeanAbsoluteDeviation）

### `extract_texture_features`

```python
extract_texture_features(image: np.ndarray, mask: np.ndarray) -> Dict[str, float]
```

提取纹理特征（简化版 GLCM）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| image | np.ndarray | — | 必填，影像数据 |
| mask | np.ndarray | — | 必填，分割掩码 |

**返回值**: `Dict[str, float]` — 纹理特征字典（GLCM_Contrast、GLCM_Dissimilarity、GLCM_Homogeneity、GLCM_Energy、GLCM_Correlation、GLCM_ASM）

### `extract_all`

```python
extract_all(image: np.ndarray, mask: np.ndarray) -> Dict[str, Dict[str, float]]
```

提取所有影像组学特征。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| image | np.ndarray | — | 必填，影像数据 |
| mask | np.ndarray | — | 必填，分割掩码 |

**返回值**: `Dict[str, Dict[str, float]]` — 所有特征（含 "shape"、"firstorder"、"texture" 三类）

### `to_dataframe`

```python
to_dataframe(features: Dict) -> pd.DataFrame
```

转换为 DataFrame 格式。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| features | Dict | — | 必填，特征字典（extract_all 的输出） |

**返回值**: `pd.DataFrame` — 含 feature_class、feature_name、value 列

### `export_v1_schema`

```python
export_v1_schema(features: Dict, output_dir: str) -> Dict[str, str]
```

导出 msra/imaging_features/v1 标准格式（feature_matrix.csv + feature_metadata.csv）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| features | Dict | — | 必填，特征字典（extract_all 的输出） |
| output_dir | str | — | 必填，输出目录 |

**返回值**: `Dict[str, str]` — 文件路径映射（含 feature_matrix、feature_metadata、schema_version）

**示例**:

```python
from msra_modules.medical_imaging import RadiomicsExtractor

extractor = RadiomicsExtractor(bin_width=25.0)
features = extractor.extract_all(image_array, mask_array)
print(f"特征数: {sum(len(v) for v in features.values())}")

df = extractor.to_dataframe(features)
extractor.export_v1_schema(features, "output/radiomics/")
```

---

## FeatureSelector

> 影像组学特征选择器，支持方差阈值、K-best、互信息、递归特征消除和高相关性过滤等 7 种方法。

**签名**:

```python
FeatureSelector()
```

**方法**:

### `select`

```python
select(features_df: pd.DataFrame, labels: Optional[np.ndarray] = None, method: str = "auto", n_features: int = 20) -> pd.DataFrame
```

执行特征选择。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| features_df | pd.DataFrame | — | 必填，特征 DataFrame（每行一个样本，每列一个特征） |
| labels | Optional[np.ndarray] | None | 标签数组（可选，用于有监督方法） |
| method | str | "auto" | 选择方法（"auto"、"variance"、"k_best"、"mutual_info"、"rfe"、"correlation"） |
| n_features | int | 20 | 期望保留的特征数 |

**返回值**: `pd.DataFrame` — 筛选后的特征 DataFrame

**异常**: `ValueError` — 有监督方法缺少 labels，或未知方法

### `variance_threshold`

```python
variance_threshold(features_df: pd.DataFrame, threshold: float = 0.01) -> pd.DataFrame
```

方差阈值过滤（移除方差低于阈值的特征）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| features_df | pd.DataFrame | — | 必填，特征 DataFrame |
| threshold | float | 0.01 | 方差阈值 |

**返回值**: `pd.DataFrame` — 过滤后的特征 DataFrame

### `k_best`

```python
k_best(features_df: pd.DataFrame, labels: np.ndarray, k: int = 20) -> pd.DataFrame
```

K-best 特征选择（F-test）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| features_df | pd.DataFrame | — | 必填，特征 DataFrame |
| labels | np.ndarray | — | 必填，标签数组 |
| k | int | 20 | 选择的特征数 |

**返回值**: `pd.DataFrame` — 筛选后的特征 DataFrame

### `mutual_info`

```python
mutual_info(features_df: pd.DataFrame, labels: np.ndarray, k: int = 20) -> pd.DataFrame
```

互信息特征选择。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| features_df | pd.DataFrame | — | 必填，特征 DataFrame |
| labels | np.ndarray | — | 必填，标签数组 |
| k | int | 20 | 选择的特征数 |

**返回值**: `pd.DataFrame` — 筛选后的特征 DataFrame

### `rfe`

```python
rfe(features_df: pd.DataFrame, labels: np.ndarray, n_features: int = 20) -> pd.DataFrame
```

递归特征消除（RFE + RandomForest）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| features_df | pd.DataFrame | — | 必填，特征 DataFrame |
| labels | np.ndarray | — | 必填，标签数组 |
| n_features | int | 20 | 期望保留的特征数 |

**返回值**: `pd.DataFrame` — 筛选后的特征 DataFrame

### `correlation_filter`

```python
correlation_filter(features_df: pd.DataFrame, threshold: float = 0.95) -> pd.DataFrame
```

高相关性过滤（移除高度相关的特征）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| features_df | pd.DataFrame | — | 必填，特征 DataFrame |
| threshold | float | 0.95 | 相关系数阈值 |

**返回值**: `pd.DataFrame` — 过滤后的特征 DataFrame

### `auto_select`

```python
auto_select(features_df: pd.DataFrame, labels: Optional[np.ndarray] = None, n_features: int = 20) -> pd.DataFrame
```

自动选择管线（无标签: variance → correlation；有标签: variance → correlation → k_best/mutual_info）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| features_df | pd.DataFrame | — | 必填，特征 DataFrame |
| labels | Optional[np.ndarray] | None | 标签数组（可选） |
| n_features | int | 20 | 期望保留的特征数 |

**返回值**: `pd.DataFrame` — 筛选后的特征 DataFrame

### `get_selected_feature_names`

```python
get_selected_feature_names() -> List[str]
```

获取最近一次选择的特征名列表。

**返回值**: `List[str]` — 选中的特征名列表

**示例**:

```python
from msra_modules.medical_imaging import FeatureSelector

selector = FeatureSelector()

# 无标签场景
selected = selector.select(features_df, method="auto", n_features=20)

# 有标签场景
selected = selector.select(features_df, labels=labels, method="auto", n_features=20)
print(f"选中特征: {selector.get_selected_feature_names()}")
```

---

## ImagingQualityGateChecker

> 影像质量门闸检查器，封装 Gate IMG-1 的检查逻辑。

**签名**:

```python
ImagingQualityGateChecker(study_id: str, project_root: Optional[str] = None)
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| study_id | str | — | 必填，研究编号 |
| project_root | Optional[str] | None | 项目根目录（可选） |

**方法**:

### `run_gate_img1`

```python
run_gate_img1(image_path: str, mask_path: Optional[str] = None) -> GateResult
```

执行 Gate IMG-1 全部 4 项检查：文件可读性、体素间距合理性、ROI 掩膜维度匹配、影像质量（SNR + NaN/Inf）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| image_path | str | — | 必填，影像文件路径（DICOM/NIfTI/NRRD） |
| mask_path | Optional[str] | None | ROI 掩膜文件路径（可选） |

**返回值**: `GateResult` — 判定结果（PASS / CONDITIONAL / BLOCKED）

### `check_file_readable`

```python
check_file_readable(file_path: str) -> CheckItemResult
```

公开接口：检查文件可读性。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| file_path | str | — | 必填，文件路径 |

**返回值**: `CheckItemResult`

### `check_voxel_spacing`

```python
check_voxel_spacing(image_metadata: Dict[str, Any], min_spacing: float = 0.5, max_spacing: float = 5.0) -> CheckItemResult
```

公开接口：检查体素间距合理性。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| image_metadata | Dict[str, Any] | — | 必填，影像元数据（需含 spacing 字段） |
| min_spacing | float | 0.5 | 最小允许间距 (mm) |
| max_spacing | float | 5.0 | 最大允许间距 (mm) |

**返回值**: `CheckItemResult`

### `check_roi_match`

```python
check_roi_match(image_data: np.ndarray, mask_path: str) -> CheckItemResult
```

公开接口：检查 ROI 掩膜与影像维度匹配。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| image_data | np.ndarray | — | 必填，影像 numpy 数组 |
| mask_path | str | — | 必填，掩膜文件路径 |

**返回值**: `CheckItemResult`

### `check_image_quality`

```python
check_image_quality(image_data: np.ndarray) -> CheckItemResult
```

公开接口：检查影像质量（SNR + NaN/Inf）。

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| image_data | np.ndarray | — | 必填，影像 numpy 数组 |

**返回值**: `CheckItemResult`

**示例**:

```python
from msra_modules.medical_imaging import ImagingQualityGateChecker

checker = ImagingQualityGateChecker(study_id="IMG-2026-001")
gate_result = checker.run_gate_img1(
    image_path="data/scan.nii.gz",
    mask_path="data/mask.nii.gz"
)
print(f"IMG-1 判定: {gate_result.verdict.value}")
print(f"通过率: {gate_result.pass_rate:.1%}")
```

---

## 共享类型参考

### CheckItemResult

| 属性 | 类型 | 说明 |
|------|------|------|
| item_id | str | 检查项编号 |
| name | str | 检查项名称 |
| is_key | bool | 是否为关键项 |
| status | str | 状态（PASS / FAIL / N/A / SKIP） |
| evidence | str | 证据描述 |
| notes | str | 备注 |

### GateVerdict

| 值 | 说明 |
|----|------|
| PASS | 全部通过 |
| CONDITIONAL | 条件通过 |
| BLOCKED | 阻断 |
