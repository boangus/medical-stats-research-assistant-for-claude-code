# MSRA 医学影像模块用户教程

> **模块版本**: v1.2.0 | **文档日期**: 2026-06-25 | **状态**: Stable
> **命令入口**: `/msra-imaging` | **适用 MSRA 版本**: v1.0.0+

---

## 1. 模块简介与适用场景

### 模块概述

MSRA Medical Imaging（医学影像）模块提供从医学影像数据中提取定量放射组学特征的标准化分析流程。支持 DICOM、NIfTI、NRRD 三种主流医学影像格式，覆盖影像加载、预处理、分割、特征提取和特征选择的完整链路。

### 核心能力

| 能力 | 说明 |
|------|------|
| 影像加载 | DICOM 序列 / NIfTI / NRRD，`load_dicom_series`, `load_nifti`, `load_nrrd` |
| 预处理 | 强度归一化、重采样、去噪，`ImagePreprocessor` |
| 影像分割 | MONAI 3D U-Net 分割，`SegmentationPipeline` |
| 特征提取 | 形状/一阶/纹理（GLCM/GLRLM/GLSZM/GLDM/NGTDM），`RadiomicsExtractor` |
| 特征选择 | 方差/K-best/互信息/RFE/相关性过滤，`FeatureSelector` |
| 配准 | 弹性配准，`ImageRegistration` |
| 质量门闸 | Gate IMG-1（数据质量），`ImagingQualityGateChecker` |

### 适用场景

- 肿瘤影像放射组学特征提取与建模
- DICOM CT/MRI 序列批量处理
- 基于 ROI 掩码的影像组学特征提取
- 特征选择与降维（支持有标签和无标签场景）
- 将影像特征矩阵接入 MSRA 主 Pipeline 进行联合建模

---

## 2. 安装依赖

### 安装 medical_imaging 扩展依赖

```bash
pip install -e ".[medical_imaging]"
```

### 核心依赖列表

```toml
nibabel >= 4.0         # NIfTI 文件读写
SimpleITK >= 2.3       # DICOM 读取与影像处理
pyradiomics >= 3.1     # 放射组学特征提取
scikit-image >= 0.20   # 图像处理工具
```

### 验证安装

```bash
python -c "from msra_modules.medical_imaging import load_nifti, RadiomicsExtractor, FeatureSelector, ImagingQualityGateChecker; print('OK')"
```

---

## 3. 数据准备

### 支持的影像格式

| 格式 | 扩展名 | 说明 | 典型来源 |
|------|--------|------|---------|
| DICOM | `.dcm` | 目录形式，含多个切片文件 | CT/MRI 扫描仪 |
| NIfTI | `.nii` / `.nii.gz` | 单文件，含完整 3D/4D 数据 | 预处理后的影像 |
| NRRD | `.nrrd` | 近原始栅格数据 | Slicer 等工具 |

### ROI 掩码文件

特征提取需要提供 ROI（感兴趣区域）掩码文件。掩码应为与影像维度一致的二值化文件（ROI 区域为 1，背景为 0）：

```
影像文件: scan.nii.gz      (512×512×200)
掩码文件: mask.nii.gz      (512×512×200, 二值化)
```

### 示例：准备模拟数据

```python
import numpy as np
import nibabel as nib

# 生成模拟 CT 影像 (64×64×32)
np.random.seed(42)
volume = np.random.randint(0, 100, size=(64, 64, 32), dtype=np.int16)
# 中心区域模拟肿瘤
volume[20:44, 20:44, 10:22] = np.random.randint(80, 200, size=(24, 24, 12))
nib.save(nib.Nifti1Image(volume, np.eye(4)), "mock_scan.nii.gz")

# 生成对应掩码
mask = np.zeros((64, 64, 32), dtype=np.int8)
mask[20:44, 20:44, 10:22] = 1
nib.save(nib.Nifti1Image(mask, np.eye(4)), "mock_mask.nii.gz")
print("Mock data created: mock_scan.nii.gz, mock_mask.nii.gz")
```

---

## 4. 影像加载与预处理

### 影像加载

```python
from msra_modules.medical_imaging import (
    load_dicom_series, load_nifti, load_nrrd, DICOMLoader,
)

# 方式 1: 加载 DICOM 序列
dicom_loader = DICOMLoader(window_level=40, window_width=400)  # CT 肺窗
sitk_image = dicom_loader.load_dicom_series("/path/to/dicom/")

# 方式 2: 加载 NIfTI 文件
nifti_data = load_nifti("scan.nii.gz")  # 返回 numpy array

# 方式 3: 加载 NRRD 文件
nrrd_data = load_nrrd("scan.nrrd")
```

### 预处理

```python
from msra_modules.medical_imaging import ImagePreprocessor

preprocessor = ImagePreprocessor(
    target_spacing=(1.0, 1.0, 1.0),  # 重采样到 1mm 各向同性
    normalize_method="z_score",       # 标准化方法
)

# 预处理影像
processed_image = preprocessor.preprocess(sitk_image)
```

### Gate IMG-1 数据质量门闸

```python
from msra_modules.medical_imaging import ImagingQualityGateChecker

checker = ImagingQualityGateChecker(study_id="IMG-2026-001")
gate_result = checker.run_gate_img1(
    image_path="scan.nii.gz",
    mask_path="mask.nii.gz",
)
print(f"Gate IMG-1: {gate_result.verdict}")  # PASS / CONDITIONAL / BLOCKED
```

---

## 5. 放射组学特征提取

### 完整特征提取流程

```python
from msra_modules.medical_imaging import RadiomicsExtractor

# 初始化特征提取器
extractor = RadiomicsExtractor(bin_width=25.0)

# 提取形状特征（基于掩码）
shape_features = extractor.extract_shape_features(mask_array)
print(f"Shape features: {len(shape_features)}")
# 包含: VoxelVolume, SurfaceArea, Maximum3DDiameter, 等

# 提取一阶统计特征
firstorder_features = extractor.extract_firstorder_features(image_array, mask_array)
print(f"First-order features: {len(firstorder_features)}")
# 包含: Mean, Median, Std, Skewness, Kurtosis, Energy, Entropy, 等

# 提取纹理特征
glcm_features = extractor.extract_glcm_features(image_array, mask_array)
print(f"GLCM features: {len(glcm_features)}")
# 包含: Contrast, Correlation, Homogeneity, Energy, 等

# 合并为特征矩阵
all_features = {**shape_features, **firstorder_features, **glcm_features}
```

### 批量特征提取

```python
import pandas as pd

# 多个样本批量提取
samples = ["patient_01", "patient_02", "patient_03"]
feature_rows = []

for sample_id in samples:
    image = load_nifti(f"data/{sample_id}_scan.nii.gz")
    mask = load_nifti(f"data/{sample_id}_mask.nii.gz")

    extractor = RadiomicsExtractor(bin_width=25.0)
    features = {}
    features.update(extractor.extract_shape_features(mask))
    features.update(extractor.extract_firstorder_features(image, mask))
    features.update(extractor.extract_glcm_features(image, mask))
    features["sample_id"] = sample_id
    feature_rows.append(features)

# 构建特征矩阵 (sample × feature)
feature_df = pd.DataFrame(feature_rows).set_index("sample_id")
feature_df.to_csv("radiomics_features.csv")
print(f"Feature matrix: {feature_df.shape}")
```

---

## 6. 特征选择方法对比

### 支持的选择方法

| 方法 | 参数 | 适用场景 | 需要标签 |
|------|------|---------|---------|
| `auto` | 自动组合 | 通用场景 | 可选 |
| `variance` | 方差阈值 | 去除低方差特征 | 否 |
| `k_best` | K 个最佳 | 有监督选择 | 是 |
| `mutual_info` | 互信息 | 非线性关系 | 是 |
| `rfe` | 递归特征消除 | 精细选择 | 是 |
| `correlation` | 相关性过滤 | 去除冗余特征 | 否 |

### 方法对比示例

```python
from msra_modules.medical_imaging import FeatureSelector
import pandas as pd

# 加载特征矩阵
features_df = pd.read_csv("radiomics_features.csv", index_col=0)
labels = pd.read_csv("labels.csv")["label"].values  # 0/1

selector = FeatureSelector()

# 方法 1: 无标签 — 自动选择（方差 + 相关性过滤）
selected_auto = selector.select(features_df, labels=None, method="auto", n_features=20)
print(f"Auto selected: {selected_auto.shape[1]} features")

# 方法 2: 有标签 — K-Best (F-test)
selected_kbest = selector.select(features_df, labels=labels, method="k_best", n_features=15)
print(f"K-Best selected: {selected_kbest.shape[1]} features")

# 方法 3: 有标签 — 互信息
selected_mi = selector.select(features_df, labels=labels, method="mutual_info", n_features=15)
print(f"Mutual info selected: {selected_mi.shape[1]} features")

# 方法 4: 有标签 — 递归特征消除 (RFE)
selected_rfe = selector.select(features_df, labels=labels, method="rfe", n_features=10)
print(f"RFE selected: {selected_rfe.shape[1]} features")

# 方法 5: 无标签 — 相关性过滤
selected_corr = selector.select(features_df, labels=None, method="correlation")
print(f"Correlation filtered: {selected_corr.shape[1]} features")
```

### 推荐策略

- **探索阶段（无标签）**: 使用 `auto` 方法（方差过滤 + 相关性去冗余）
- **建模阶段（有标签）**: 先用 `correlation` 去冗余，再用 `k_best` 或 `mutual_info` 选择
- **精细优化**: 使用 `rfe` 逐步消除，但计算量较大

---

## 7. 质量门闸说明

### Gate IMG-1 — 数据质量门闸

> 位于 Phase 1（数据加载后），阻断不合格数据进入分析流程。
> 实现: `msra_modules/medical_imaging/quality_gates.py` → `ImagingQualityGateChecker`

| # | 检查项 | 关键项 | 通过标准 |
|---|--------|--------|---------|
| 1 | 文件可读性 | 🔑 | DICOM/NIfTI 文件可成功读取 |
| 2 | 体素间距合理性 | 🔑 | spacing ∈ [0.5, 5.0] mm |
| 3 | ROI 掩膜维度匹配 | 🔑 | image.shape == mask.shape |
| 4 | 影像质量 | | SNR > 5，无 NaN/Inf |

**判定规则**:
- **PASS**: 4/4 通过
- **CONDITIONAL**: 2-3/4 通过且 🔑 全通过
- **BLOCKED**: ≤ 1/4 通过 或 🔑 任一未通过（**阻断流程**）

### Python 调用示例

```python
from msra_modules.medical_imaging import ImagingQualityGateChecker

checker = ImagingQualityGateChecker(study_id="IMG-2026-001")
gate_result = checker.run_gate_img1(
    image_path="scan.nii.gz",
    mask_path="mask.nii.gz",
)

print(f"IMG-1 verdict: {gate_result.verdict}")
for item in gate_result.items:
    print(f"  [{item.status}] {item.name}: {item.message}")
```

---

## 8. 与主 Pipeline 集成

### 导出特征矩阵供主 Pipeline 使用

```python
import pandas as pd

# 导出标准格式特征矩阵
selected_features.to_csv(
    "MSRA/data/imaging_features_v1.csv",
    index_label="sample_id",
)
```

### 自动接入主 Pipeline

在 Phase 4 中选择"接入主 Pipeline"选项，系统将：
1. 将特征矩阵写入 `MSRA/data/imaging_features_v1.csv`
2. 自动触发 `/msra-exec` 将其作为预测变量纳入 Stage 3

### 命令行直接调用

```
/msra-imaging --nifti scan.nii.gz --roi mask.nii.gz --mode radiomics --integrate-pipeline
```

---

## 9. 常见问题 FAQ

### Q1: SimpleITK 安装失败怎么办？

SimpleITK 在某些系统上需要从源码编译。建议使用 conda：

```bash
conda install -c conda-forge simpleitk
```

### Q2: DICOM 目录被识别为空怎么办？

确认目录中包含 `.dcm` 文件。某些 DICOM 文件没有扩展名，可以使用工具验证：

```python
import SimpleITK as sitk
series_ids = sitk.ImageSeriesReader.GetGDCMSeriesIDs("dicom_dir/")
print(f"Found {len(series_ids)} series")
```

### Q3: ROI 掩码维度与影像不匹配怎么办？

这是 Gate IMG-1 的关键项检查。请确保：
1. 掩码和影像使用相同的体素间距
2. 掩码和影像的维度完全一致
3. 使用 `ImagePreprocessor` 对影像和掩码进行相同的重采样

### Q4: 特征矩阵中包含大量 NaN 怎么办？

可能原因：
1. ROI 区域为空或过小 → 检查掩码文件
2. 某些纹理特征在均匀区域无法计算 → 使用 `FeatureSelector` 的 `variance` 方法过滤

### Q5: MONAI 分割模型加载失败怎么办？

MONAI 是可选依赖。如果未安装，系统会降级为阈值分割：

```bash
pip install monai  # 安装 MONAI 以使用深度学习分割
```

### Q6: 如何选择合适的 bin_width？

`bin_width` 影响灰度直方图的离散化程度：
- CT 影像推荐 25 HU（默认）
- MRI 影像推荐 5-10
- PET 影像推荐 0.1

---

> **相关文档**: [SKILL.md](../../skills/imaging-analysis/SKILL.md) | [MSRA 文档主页](../system_design.md)
