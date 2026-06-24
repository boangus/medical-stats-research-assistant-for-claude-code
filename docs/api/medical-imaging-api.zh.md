# MSRA Medical Imaging 模块 API 参考

| 字段 | 值 |
|------|-----|
| **模块** | `msra_modules.medical_imaging` |
| **版本** | 1.2.0 |
| **日期** | 2026-07-13 |
| **状态** | Released (v1.0.0) |
| **语言** | 中文 |

---

## 概述

Medical Imaging 模块提供基于 MONAI 和 SimpleITK 的医学影像分析功能，包括 DICOM/NIfTI/NRRD 加载、预处理（重采样、归一化、去噪、N4 偏置场校正）、分割（3D U-Net）、分类、配准、影像组学特征提取、特征选择和质量门闸检查。

### 依赖

- `SimpleITK` — 影像加载与处理
- `nibabel` — NIfTI 文件读取
- `MONAI` — 深度学习分割
- `torch` / `torchvision` — 深度学习模型
- `scipy` — 科学计算
- `scikit-image` — GLCM 纹理特征
- `scikit-learn` — PCA、特征选择
- `matplotlib` — 可视化

---

## 公开 API

### `DICOMLoader`

**描述**: DICOM 影像加载器，支持 DICOM 序列加载、元数据提取和窗宽窗位调整。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `window_level` | `float` | 否 | `None` | 窗位（HU 中心值） |
| `window_width` | `float` | 否 | `None` | 窗宽（HU 范围） |

**方法**:

#### `load_dicom_series(dicom_dir)`

加载 DICOM 序列。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `dicom_dir` | `str` | 是 | — | DICOM 文件目录 |

- **返回值**: `SimpleITK.Image`
- **异常**: `FileNotFoundError`（目录不存在或无 DICOM 文件）

#### `load_dicom(dicom_path)`

加载单个 DICOM 文件。

- **返回值**: `SimpleITK.Image`

#### `to_numpy(image)`

将 SimpleITK Image 转换为 numpy 数组。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `image` | `SimpleITK.Image` | 是 | — | SimpleITK Image |

- **返回值**: `np.ndarray` — (D, H, W) 或 (H, W)

#### `extract_metadata(image)`

提取 DICOM 元数据。

- **返回值**: `dict` — 含 `size`, `spacing`, `origin`, `direction`, `pixel_type`, `dimensions` 及 DICOM 标签（如 `patient_name`, `modality` 等）

#### `apply_window(image, window_level=None, window_width=None)`

应用窗宽窗位。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `image` | `SimpleITK.Image` | 是 | — | 输入图像 |
| `window_level` | `float` | 否 | `None` | 窗位（默认使用初始化值） |
| `window_width` | `float` | 否 | `None` | 窗宽（默认使用初始化值） |

- **返回值**: `SimpleITK.Image`

**异常**: `ImportError`（SimpleITK 未安装）、`FileNotFoundError`

---

### `load_dicom_series(dicom_dir)`

**描述**: 便捷函数，加载 DICOM 序列并返回 numpy 数组和元数据。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `dicom_dir` | `str` | 是 | — | DICOM 目录 |

- **返回值**: `tuple[np.ndarray, dict]` — (numpy_array, metadata_dict)
- **示例**:

```python
from msra_modules.medical_imaging import load_dicom_series

array, metadata = load_dicom_series("/data/dicom/")
print(array.shape, metadata["spacing"])
```

---

### `load_nifti(nifti_path)`

**描述**: 便捷函数，使用 nibabel 加载 NIfTI 文件（`.nii` / `.nii.gz`）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `nifti_path` | `str` | 是 | — | NIfTI 文件路径 |

- **返回值**: `tuple[np.ndarray, dict]` — (numpy_array, metadata_dict)，元数据含 `size`, `spacing`, `dtype`, `dimensions`, `affine`, `sform`, `qform`
- **异常**: `ImportError`（nibabel 未安装）、`FileNotFoundError`

---

### `load_nrrd(nrrd_path)`

**描述**: 便捷函数，使用 SimpleITK 加载 NRRD 文件。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `nrrd_path` | `str` | 是 | — | NRRD 文件路径 |

- **返回值**: `tuple[np.ndarray, dict]` — (numpy_array, metadata_dict)
- **异常**: `ImportError`（SimpleITK 未安装）、`FileNotFoundError`

---

### `ImagePreprocessor`

**描述**: 医学影像预处理器，支持重采样、强度标准化、去噪和 N4 偏置场校正。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `target_spacing` | `tuple[float, float, float]` | 否 | `None` | 目标体素间距 (x, y, z) |
| `normalize` | `bool` | 否 | `True` | 是否标准化到 [0, 1] |

**方法**:

#### `resample(image, target_spacing=None)`

重采样图像到目标间距。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `image` | `SimpleITK.Image` | 是 | — | 输入图像 |
| `target_spacing` | `tuple` | 否 | `None` | 目标间距（覆盖默认值） |

- **返回值**: `SimpleITK.Image`

#### `normalize_intensity(image, method="min_max")`

标准化图像强度。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `image` | `SimpleITK.Image` | 是 | — | 输入图像 |
| `method` | `str` | 否 | `"min_max"` | 方法（`"min_max"` 或 `"z_score"`） |

- **返回值**: `SimpleITK.Image`

#### `denoise(image, method="curvature_flow")`

图像去噪。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `image` | `SimpleITK.Image` | 是 | — | 输入图像 |
| `method` | `str` | 否 | `"curvature_flow"` | 去噪方法（`"curvature_flow"` 或 `"median"`） |

- **返回值**: `SimpleITK.Image`

#### `bias_correction(image)`

N4 偏置场校正。

- **返回值**: `SimpleITK.Image`

#### `preprocess_pipeline(image)`

完整预处理 pipeline（重采样 → 去噪 → 标准化）。

- **返回值**: `SimpleITK.Image`
- **示例**:

```python
from msra_modules.medical_imaging import ImagePreprocessor, load_nifti

array, meta = load_nifti("/data/scan.nii.gz")
preprocessor = ImagePreprocessor(target_spacing=(1.0, 1.0, 1.0), normalize=True)
# 注意：preprocess_pipeline 接受 SimpleITK.Image
```

**异常**: `ImportError`（SimpleITK 未安装）、`ValueError`（未知方法）

---

### `normalize_intensity(array, method="min_max")`

**描述**: 便捷函数，标准化 numpy 数组强度。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `array` | `np.ndarray` | 是 | — | 输入数组 |
| `method` | `str` | 否 | `"min_max"` | 方法（`"min_max"` 或 `"z_score"`） |

- **返回值**: `np.ndarray`

---

### `SegmentationPipeline`

**描述**: 影像分割 Pipeline，基于 MONAI 3D U-Net 预训练模型。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `model_name` | `str` | 否 | `"spleen_ct"` | MONAI 预训练模型名称 |
| `device` | `str` | 否 | `"cpu"` | 计算设备（`"cpu"` 或 `"cuda"`） |

**方法**:

#### `preprocess(image)`

预处理影像（标准化 + 添加通道维度）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `image` | `np.ndarray` | 是 | — | 输入影像 (D, H, W) |

- **返回值**: `np.ndarray` — (1, D, H, W) float32

#### `segment(image)`

执行分割。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `image` | `np.ndarray` | 是 | — | 输入影像 (D, H, W) 或 (1, D, H, W) |

- **返回值**: `np.ndarray` — 分割掩码 (D, H, W)

#### `segment_with_confidence(image)`

分割并返回置信度。

- **返回值**: `tuple[np.ndarray, np.ndarray]` — (分割掩码, 置信度图)

- **示例**:

```python
from msra_modules.medical_imaging import SegmentationPipeline

pipeline = SegmentationPipeline(model_name="spleen_ct", device="cpu")
mask = pipeline.segment(image_array)
mask, confidence = pipeline.segment_with_confidence(image_array)
```

**异常**: `ImportError`（MONAI/torch 未安装）

---

### `ClassificationPipeline`

**描述**: 影像分类 Pipeline，支持 ResNet18 / DenseNet121。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `model_name` | `str` | 否 | `"resnet18"` | 模型名称 |
| `num_classes` | `int` | 否 | `2` | 类别数 |
| `device` | `str` | 否 | `"cpu"` | 计算设备 |

**方法**:

#### `classify(image)`

执行分类。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `image` | `np.ndarray` | 是 | — | 输入影像 (D, H, W) 或 (H, W, C) |

- **返回值**: `dict` — 含 `prediction` (int), `confidence` (float), `probabilities` (list)

**异常**: `ImportError`（PyTorch 未安装）

---

### `RadiomicsExtractor`

**描述**: 影像组学特征提取器，提取形状、一阶统计和纹理（GLCM）特征，支持 v1 Schema 导出。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `bin_width` | `float` | 否 | `25.0` | 灰度直方图 bin 宽度 |

**方法**:

#### `extract_shape_features(mask)`

提取形状特征。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `mask` | `np.ndarray` | 是 | — | 分割掩码（二值化） |

- **返回值**: `dict[str, float]` — 含 `VoxelVolume`, `SurfaceArea`, `Maximum3DDiameter`, `MajorAxisLength`, `MinorAxisLength`, `LeastAxisLength`, `Sphericity`

#### `extract_firstorder_features(image, mask)`

提取一阶统计特征。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `image` | `np.ndarray` | 是 | — | 影像数据 |
| `mask` | `np.ndarray` | 是 | — | 分割掩码 |

- **返回值**: `dict[str, float]` — 含 `Mean`, `Median`, `Std`, `Variance`, `Minimum`, `Maximum`, `Range`, `Percentile10/25/75/90`, `IQR`, `Skewness`, `Kurtosis`, `Energy`, `Entropy`, `RootMeanSquared`, `MeanAbsoluteDeviation`

#### `extract_texture_features(image, mask)`

提取纹理特征（简化版 GLCM）。

- **返回值**: `dict[str, float]` — 含 `GLCM_Contrast`, `GLCM_Dissimilarity`, `GLCM_Homogeneity`, `GLCM_Energy`, `GLCM_Correlation`, `GLCM_ASM`

#### `extract_all(image, mask)`

提取所有影像组学特征。

- **返回值**: `dict[str, dict[str, float]]` — 含 `shape`, `firstorder`, `texture` 三个类别的特征字典

#### `to_dataframe(features)`

转换为 DataFrame 格式。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `features` | `dict` | 是 | — | 特征字典（`extract_all` 的输出） |

- **返回值**: `pd.DataFrame` — 列含 `feature_class`, `feature_name`, `value`

#### `export_v1_schema(features, output_dir)`

导出 `msra/imaging_features/v1` 标准格式，输出两个文件：
- `feature_matrix.csv`: sample_id + 所有特征列
- `feature_metadata.csv`: feature_name, class, description

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `features` | `dict` | 是 | — | 特征字典（`extract_all` 的输出） |
| `output_dir` | `str` | 是 | — | 输出目录 |

- **返回值**: `dict[str, str]` — 含 `feature_matrix`, `feature_metadata`, `schema_version`（`"msra/imaging_features/v1"`）
- **示例**:

```python
from msra_modules.medical_imaging import RadiomicsExtractor

extractor = RadiomicsExtractor(bin_width=25.0)
features = extractor.extract_all(image_array, mask_array)
paths = extractor.export_v1_schema(features, "/output/radiomics/")
```

---

### `ImagingVisualizer`

**描述**: 影像可视化工具，支持切片绘制、多切片视图和 3D 体绘制。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `figsize` | `tuple` | 否 | `(12, 8)` | 图像大小 |
| `dpi` | `int` | 否 | `100` | 分辨率 |

**方法**:

#### `plot_slice(image, mask=None, slice_idx=None, title="", save_path=None)`

绘制单个切片（原图 + 掩码 + 叠加）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `image` | `np.ndarray` | 是 | — | 影像数据 (D, H, W) |
| `mask` | `np.ndarray` | 否 | `None` | 分割掩码 |
| `slice_idx` | `int` | 否 | `None` | 切片索引（默认中间） |
| `title` | `str` | 否 | `""` | 标题 |
| `save_path` | `str` | 否 | `None` | 保存路径 |

- **返回值**: `matplotlib.figure.Figure`

#### `plot_multi_slice(image, mask=None, num_slices=4, title="", save_path=None)`

绘制多个切片。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `image` | `np.ndarray` | 是 | — | 影像数据 |
| `mask` | `np.ndarray` | 否 | `None` | 分割掩码 |
| `num_slices` | `int` | 否 | `4` | 切片数 |
| `title` | `str` | 否 | `""` | 标题 |
| `save_path` | `str` | 否 | `None` | 保存路径 |

- **返回值**: `matplotlib.figure.Figure`

#### `plot_3d_volume(image, mask=None, threshold=None, title="3D Volume Rendering", save_path=None)`

3D 体绘制。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `image` | `np.ndarray` | 是 | — | 影像数据 |
| `mask` | `np.ndarray` | 否 | `None` | 分割掩码 |
| `threshold` | `float` | 否 | `None` | 阈值（默认 90 百分位） |
| `title` | `str` | 否 | `"3D Volume Rendering"` | 标题 |
| `save_path` | `str` | 否 | `None` | 保存路径 |

- **返回值**: `matplotlib.figure.Figure`

---

### `ImageRegistration`

**描述**: 医学影像配准，支持刚性（rigid）、仿射（affine）和 B 样条（bspline）变换。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `method` | `str` | 否 | `"rigid"` | 配准方法（`"rigid"`, `"affine"`, `"bspline"`） |

**方法**:

#### `register(fixed_image, moving_image, fixed_mask=None, moving_mask=None)`

执行配准。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `fixed_image` | `SimpleITK.Image` | 是 | — | 固定图像 |
| `moving_image` | `SimpleITK.Image` | 是 | — | 移动图像 |
| `fixed_mask` | `SimpleITK.Image` | 否 | `None` | 固定图像掩码 |
| `moving_mask` | `SimpleITK.Image` | 否 | `None` | 移动图像掩码 |

- **返回值**: `dict` — 含 `transform`, `resampled_image`, `metric_value`, `iterations`, `method`

#### `evaluate(fixed_image, moving_image, mask=None)`

评估配准质量。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `fixed_image` | `SimpleITK.Image` | 是 | — | 固定图像 |
| `moving_image` | `SimpleITK.Image` | 是 | — | 移动图像 |
| `mask` | `SimpleITK.Image` | 否 | `None` | 评估区域掩码 |

- **返回值**: `dict` — 含 `mse`, `mae`, `correlation`, `ssim`

**异常**: `ImportError`（SimpleITK 未安装）、`ValueError`（未知方法）

---

### `ImageClassifier`

**描述**: 影像分类器，支持 ResNet18 / DenseNet121。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `model_type` | `str` | 否 | `"resnet18"` | 模型类型 |
| `num_classes` | `int` | 否 | `2` | 类别数 |
| `device` | `str` | 否 | `"cpu"` | 计算设备 |

**方法**:

#### `classify(image)`

执行分类。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `image` | `np.ndarray` | 是 | — | 输入影像 |

- **返回值**: `dict` — 含 `prediction` (int), `confidence` (float), `probabilities` (list)

**异常**: `ImportError`（PyTorch 未安装）、`ValueError`（未知模型）

---

### `FeatureSelector`

**描述**: 影像组学特征选择器，支持 7 种选择方法。无标签时自动使用 variance_threshold + correlation_filter；有标签时可使用所有方法。

**参数**: 无构造参数。

**方法**:

#### `select(features_df, labels=None, method="auto", n_features=20)`

执行特征选择（统一入口）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `features_df` | `pd.DataFrame` | 是 | — | 特征 DataFrame（行=样本，列=特征） |
| `labels` | `np.ndarray` | 否 | `None` | 标签数组（用于有监督方法） |
| `method` | `str` | 否 | `"auto"` | 方法（`"auto"`, `"variance"`, `"k_best"`, `"mutual_info"`, `"rfe"`, `"correlation"`） |
| `n_features` | `int` | 否 | `20` | 期望保留的特征数 |

- **返回值**: `pd.DataFrame` — 筛选后的特征 DataFrame

#### `variance_threshold(features_df, threshold=0.01)`

方差阈值过滤。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `features_df` | `pd.DataFrame` | 是 | — | 特征 DataFrame |
| `threshold` | `float` | 否 | `0.01` | 方差阈值 |

- **返回值**: `pd.DataFrame`

#### `k_best(features_df, labels, k=20)`

K-best 特征选择（F-test）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `features_df` | `pd.DataFrame` | 是 | — | 特征 DataFrame |
| `labels` | `np.ndarray` | 是 | — | 标签数组 |
| `k` | `int` | 否 | `20` | 选择的特征数 |

- **返回值**: `pd.DataFrame`

#### `mutual_info(features_df, labels, k=20)`

互信息特征选择。

- **返回值**: `pd.DataFrame`

#### `rfe(features_df, labels, n_features=20)`

递归特征消除（RFE，基于 RandomForest）。

- **返回值**: `pd.DataFrame`

#### `correlation_filter(features_df, threshold=0.95)`

高相关性过滤。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `features_df` | `pd.DataFrame` | 是 | — | 特征 DataFrame |
| `threshold` | `float` | 否 | `0.95` | 相关系数阈值 |

- **返回值**: `pd.DataFrame`

#### `auto_select(features_df, labels=None, n_features=20)`

自动选择管线。无标签：variance_threshold → correlation_filter；有标签：variance_threshold → correlation_filter → mutual_info/k_best。

- **返回值**: `pd.DataFrame`

#### `get_selected_feature_names()`

获取最近一次选择的特征名列表。

- **返回值**: `list[str]`
- **示例**:

```python
from msra_modules.medical_imaging import FeatureSelector

selector = FeatureSelector()
# 无标签场景
selected = selector.select(features_df, labels=None, method="auto", n_features=20)
# 有标签场景
selected = selector.select(features_df, labels=labels, method="auto", n_features=20)
print(selector.get_selected_feature_names())
```

**异常**: `ValueError`（有监督方法缺少 labels、未知方法）

---

### `ImagingQualityGateChecker`

**描述**: 影像质量门闸检查器，封装 Gate IMG-1（数据质量门闸）。

**参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `study_id` | `str` | 是 | — | 研究编号 |
| `project_root` | `str` | 否 | `None` | 项目根目录 |

**方法**:

#### `run_gate_img1(image_path, mask_path=None)`

执行 Gate IMG-1 全部 4 项检查：文件可读性、体素间距合理性、ROI 掩膜维度匹配、影像质量（SNR + NaN/Inf）。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `image_path` | `str` | 是 | — | 影像文件路径（DICOM/NIfTI/NRRD） |
| `mask_path` | `str` | 否 | `None` | ROI 掩膜文件路径 |

- **返回值**: `GateResult` — 判定结果（`PASS` / `CONDITIONAL` / `BLOCKED`）
- **示例**:

```python
from msra_modules.medical_imaging import ImagingQualityGateChecker

checker = ImagingQualityGateChecker(study_id="IMG-2026-001")
result = checker.run_gate_img1(
    image_path="/data/scan.nii.gz",
    mask_path="/data/mask.nii.gz"
)
print(result.verdict)
```

**异常**: `ImportError`（SimpleITK/nibabel 未安装时对应检查项标记为 FAIL）

---

## 完整使用示例

```python
from msra_modules.medical_imaging import (
    load_nifti, ImagePreprocessor, RadiomicsExtractor,
    FeatureSelector, ImagingQualityGateChecker,
)
import SimpleITK as sitk

# 1. 加载影像
array, metadata = load_nifti("/data/scan.nii.gz")

# 2. 质量门闸
checker = ImagingQualityGateChecker(study_id="IMG-2026-001")
gate_result = checker.run_gate_img1("/data/scan.nii.gz", "/data/mask.nii.gz")

# 3. 特征提取
extractor = RadiomicsExtractor(bin_width=25.0)
features = extractor.extract_all(array, mask_array)

# 4. 导出 v1 Schema
paths = extractor.export_v1_schema(features, "/output/radiomics/")

# 5. 特征选择（多样本场景）
selector = FeatureSelector()
selected = selector.select(features_df, labels=labels, method="auto", n_features=20)
```
