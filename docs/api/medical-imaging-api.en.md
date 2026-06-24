# MSRA Medical Imaging Module API Reference

| Field | Value |
|-------|-------|
| **Module** | `msra_modules.medical_imaging` |
| **Version** | 1.2.0 |
| **Date** | 2026-07-13 |
| **Status** | Released (v1.0.0) |
| **Language** | English |

---

## Overview

The Medical Imaging module provides medical image analysis powered by MONAI and SimpleITK, including DICOM/NIfTI/NRRD loading, preprocessing (resampling, normalization, denoising, N4 bias field correction), segmentation (3D U-Net), classification, registration, radiomics feature extraction, feature selection, and quality gate checks.

### Dependencies

- `SimpleITK` — Image loading and processing
- `nibabel` — NIfTI file reading
- `MONAI` — Deep learning segmentation
- `torch` / `torchvision` — Deep learning models
- `scipy` — Scientific computing
- `scikit-image` — GLCM texture features
- `scikit-learn` — PCA, feature selection
- `matplotlib` — Visualization

---

## Public API

### `DICOMLoader`

**Description**: DICOM image loader supporting DICOM series loading, metadata extraction, and window level/width adjustment.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `window_level` | `float` | No | `None` | Window level (HU center) |
| `window_width` | `float` | No | `None` | Window width (HU range) |

**Methods**:

#### `load_dicom_series(dicom_dir)`

Load a DICOM series.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `dicom_dir` | `str` | Yes | — | DICOM file directory |

- **Returns**: `SimpleITK.Image`
- **Exceptions**: `FileNotFoundError` (directory not found or no DICOM files)

#### `load_dicom(dicom_path)`

Load a single DICOM file.

- **Returns**: `SimpleITK.Image`

#### `to_numpy(image)`

Convert SimpleITK Image to numpy array.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | `SimpleITK.Image` | Yes | — | SimpleITK Image |

- **Returns**: `np.ndarray` — (D, H, W) or (H, W)

#### `extract_metadata(image)`

Extract DICOM metadata.

- **Returns**: `dict` — contains `size`, `spacing`, `origin`, `direction`, `pixel_type`, `dimensions`, and DICOM tags (e.g., `patient_name`, `modality`)

#### `apply_window(image, window_level=None, window_width=None)`

Apply window level/width.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | `SimpleITK.Image` | Yes | — | Input image |
| `window_level` | `float` | No | `None` | Window level (defaults to init value) |
| `window_width` | `float` | No | `None` | Window width (defaults to init value) |

- **Returns**: `SimpleITK.Image`

**Exceptions**: `ImportError` (SimpleITK not installed), `FileNotFoundError`

---

### `load_dicom_series(dicom_dir)`

**Description**: Convenience function that loads a DICOM series and returns numpy array and metadata.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `dicom_dir` | `str` | Yes | — | DICOM directory |

- **Returns**: `tuple[np.ndarray, dict]` — (numpy_array, metadata_dict)
- **Example**:

```python
from msra_modules.medical_imaging import load_dicom_series

array, metadata = load_dicom_series("/data/dicom/")
print(array.shape, metadata["spacing"])
```

---

### `load_nifti(nifti_path)`

**Description**: Convenience function that loads a NIfTI file (`.nii` / `.nii.gz`) using nibabel.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `nifti_path` | `str` | Yes | — | NIfTI file path |

- **Returns**: `tuple[np.ndarray, dict]` — (numpy_array, metadata_dict), metadata contains `size`, `spacing`, `dtype`, `dimensions`, `affine`, `sform`, `qform`
- **Exceptions**: `ImportError` (nibabel not installed), `FileNotFoundError`

---

### `load_nrrd(nrrd_path)`

**Description**: Convenience function that loads a NRRD file using SimpleITK.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `nrrd_path` | `str` | Yes | — | NRRD file path |

- **Returns**: `tuple[np.ndarray, dict]` — (numpy_array, metadata_dict)
- **Exceptions**: `ImportError` (SimpleITK not installed), `FileNotFoundError`

---

### `ImagePreprocessor`

**Description**: Medical image preprocessor supporting resampling, intensity normalization, denoising, and N4 bias field correction.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `target_spacing` | `tuple[float, float, float]` | No | `None` | Target voxel spacing (x, y, z) |
| `normalize` | `bool` | No | `True` | Whether to normalize to [0, 1] |

**Methods**:

#### `resample(image, target_spacing=None)`

Resample image to target spacing.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | `SimpleITK.Image` | Yes | — | Input image |
| `target_spacing` | `tuple` | No | `None` | Target spacing (overrides default) |

- **Returns**: `SimpleITK.Image`

#### `normalize_intensity(image, method="min_max")`

Normalize image intensity.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | `SimpleITK.Image` | Yes | — | Input image |
| `method` | `str` | No | `"min_max"` | Method (`"min_max"` or `"z_score"`) |

- **Returns**: `SimpleITK.Image`

#### `denoise(image, method="curvature_flow")`

Denoise image.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | `SimpleITK.Image` | Yes | — | Input image |
| `method` | `str` | No | `"curvature_flow"` | Denoise method (`"curvature_flow"` or `"median"`) |

- **Returns**: `SimpleITK.Image`

#### `bias_correction(image)`

N4 bias field correction.

- **Returns**: `SimpleITK.Image`

#### `preprocess_pipeline(image)`

Complete preprocessing pipeline (resample -> denoise -> normalize).

- **Returns**: `SimpleITK.Image`
- **Example**:

```python
from msra_modules.medical_imaging import ImagePreprocessor, load_nifti

array, meta = load_nifti("/data/scan.nii.gz")
preprocessor = ImagePreprocessor(target_spacing=(1.0, 1.0, 1.0), normalize=True)
# Note: preprocess_pipeline accepts SimpleITK.Image
```

**Exceptions**: `ImportError` (SimpleITK not installed), `ValueError` (unknown method)

---

### `normalize_intensity(array, method="min_max")`

**Description**: Convenience function that normalizes numpy array intensity.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `array` | `np.ndarray` | Yes | — | Input array |
| `method` | `str` | No | `"min_max"` | Method (`"min_max"` or `"z_score"`) |

- **Returns**: `np.ndarray`

---

### `SegmentationPipeline`

**Description**: Image segmentation pipeline based on MONAI 3D U-Net pretrained models.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model_name` | `str` | No | `"spleen_ct"` | MONAI pretrained model name |
| `device` | `str` | No | `"cpu"` | Compute device (`"cpu"` or `"cuda"`) |

**Methods**:

#### `preprocess(image)`

Preprocess image (normalize + add channel dimension).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | `np.ndarray` | Yes | — | Input image (D, H, W) |

- **Returns**: `np.ndarray` — (1, D, H, W) float32

#### `segment(image)`

Perform segmentation.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | `np.ndarray` | Yes | — | Input image (D, H, W) or (1, D, H, W) |

- **Returns**: `np.ndarray` — segmentation mask (D, H, W)

#### `segment_with_confidence(image)`

Segment and return confidence map.

- **Returns**: `tuple[np.ndarray, np.ndarray]` — (segmentation mask, confidence map)

- **Example**:

```python
from msra_modules.medical_imaging import SegmentationPipeline

pipeline = SegmentationPipeline(model_name="spleen_ct", device="cpu")
mask = pipeline.segment(image_array)
mask, confidence = pipeline.segment_with_confidence(image_array)
```

**Exceptions**: `ImportError` (MONAI/torch not installed)

---

### `ClassificationPipeline`

**Description**: Image classification pipeline supporting ResNet18 / DenseNet121.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model_name` | `str` | No | `"resnet18"` | Model name |
| `num_classes` | `int` | No | `2` | Number of classes |
| `device` | `str` | No | `"cpu"` | Compute device |

**Methods**:

#### `classify(image)`

Perform classification.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | `np.ndarray` | Yes | — | Input image (D, H, W) or (H, W, C) |

- **Returns**: `dict` — contains `prediction` (int), `confidence` (float), `probabilities` (list)

**Exceptions**: `ImportError` (PyTorch not installed)

---

### `RadiomicsExtractor`

**Description**: Radiomics feature extractor for shape, first-order statistics, and texture (GLCM) features, with v1 schema export support.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `bin_width` | `float` | No | `25.0` | Grayscale histogram bin width |

**Methods**:

#### `extract_shape_features(mask)`

Extract shape features.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `mask` | `np.ndarray` | Yes | — | Segmentation mask (binary) |

- **Returns**: `dict[str, float]` — contains `VoxelVolume`, `SurfaceArea`, `Maximum3DDiameter`, `MajorAxisLength`, `MinorAxisLength`, `LeastAxisLength`, `Sphericity`

#### `extract_firstorder_features(image, mask)`

Extract first-order statistical features.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | `np.ndarray` | Yes | — | Image data |
| `mask` | `np.ndarray` | Yes | — | Segmentation mask |

- **Returns**: `dict[str, float]` — contains `Mean`, `Median`, `Std`, `Variance`, `Minimum`, `Maximum`, `Range`, `Percentile10/25/75/90`, `IQR`, `Skewness`, `Kurtosis`, `Energy`, `Entropy`, `RootMeanSquared`, `MeanAbsoluteDeviation`

#### `extract_texture_features(image, mask)`

Extract texture features (simplified GLCM).

- **Returns**: `dict[str, float]` — contains `GLCM_Contrast`, `GLCM_Dissimilarity`, `GLCM_Homogeneity`, `GLCM_Energy`, `GLCM_Correlation`, `GLCM_ASM`

#### `extract_all(image, mask)`

Extract all radiomics features.

- **Returns**: `dict[str, dict[str, float]]` — contains `shape`, `firstorder`, `texture` feature categories

#### `to_dataframe(features)`

Convert to DataFrame format.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `features` | `dict` | Yes | — | Feature dict (output of `extract_all`) |

- **Returns**: `pd.DataFrame` — columns: `feature_class`, `feature_name`, `value`

#### `export_v1_schema(features, output_dir)`

Export `msra/imaging_features/v1` standard format, outputs two files:
- `feature_matrix.csv`: sample_id + all feature columns
- `feature_metadata.csv`: feature_name, class, description

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `features` | `dict` | Yes | — | Feature dict (output of `extract_all`) |
| `output_dir` | `str` | Yes | — | Output directory |

- **Returns**: `dict[str, str]` — contains `feature_matrix`, `feature_metadata`, `schema_version` (`"msra/imaging_features/v1"`)
- **Example**:

```python
from msra_modules.medical_imaging import RadiomicsExtractor

extractor = RadiomicsExtractor(bin_width=25.0)
features = extractor.extract_all(image_array, mask_array)
paths = extractor.export_v1_schema(features, "/output/radiomics/")
```

---

### `ImagingVisualizer`

**Description**: Image visualization tool supporting slice plotting, multi-slice views, and 3D volume rendering.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `figsize` | `tuple` | No | `(12, 8)` | Figure size |
| `dpi` | `int` | No | `100` | Resolution |

**Methods**:

#### `plot_slice(image, mask=None, slice_idx=None, title="", save_path=None)`

Plot a single slice (original + mask + overlay).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | `np.ndarray` | Yes | — | Image data (D, H, W) |
| `mask` | `np.ndarray` | No | `None` | Segmentation mask |
| `slice_idx` | `int` | No | `None` | Slice index (defaults to middle) |
| `title` | `str` | No | `""` | Title |
| `save_path` | `str` | No | `None` | Save path |

- **Returns**: `matplotlib.figure.Figure`

#### `plot_multi_slice(image, mask=None, num_slices=4, title="", save_path=None)`

Plot multiple slices.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | `np.ndarray` | Yes | — | Image data |
| `mask` | `np.ndarray` | No | `None` | Segmentation mask |
| `num_slices` | `int` | No | `4` | Number of slices |
| `title` | `str` | No | `""` | Title |
| `save_path` | `str` | No | `None` | Save path |

- **Returns**: `matplotlib.figure.Figure`

#### `plot_3d_volume(image, mask=None, threshold=None, title="3D Volume Rendering", save_path=None)`

3D volume rendering.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | `np.ndarray` | Yes | — | Image data |
| `mask` | `np.ndarray` | No | `None` | Segmentation mask |
| `threshold` | `float` | No | `None` | Threshold (defaults to 90th percentile) |
| `title` | `str` | No | `"3D Volume Rendering"` | Title |
| `save_path` | `str` | No | `None` | Save path |

- **Returns**: `matplotlib.figure.Figure`

---

### `ImageRegistration`

**Description**: Medical image registration supporting rigid, affine, and B-spline transforms.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `method` | `str` | No | `"rigid"` | Registration method (`"rigid"`, `"affine"`, `"bspline"`) |

**Methods**:

#### `register(fixed_image, moving_image, fixed_mask=None, moving_mask=None)`

Perform registration.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `fixed_image` | `SimpleITK.Image` | Yes | — | Fixed image |
| `moving_image` | `SimpleITK.Image` | Yes | — | Moving image |
| `fixed_mask` | `SimpleITK.Image` | No | `None` | Fixed image mask |
| `moving_mask` | `SimpleITK.Image` | No | `None` | Moving image mask |

- **Returns**: `dict` — contains `transform`, `resampled_image`, `metric_value`, `iterations`, `method`

#### `evaluate(fixed_image, moving_image, mask=None)`

Evaluate registration quality.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `fixed_image` | `SimpleITK.Image` | Yes | — | Fixed image |
| `moving_image` | `SimpleITK.Image` | Yes | — | Moving image |
| `mask` | `SimpleITK.Image` | No | `None` | Evaluation region mask |

- **Returns**: `dict` — contains `mse`, `mae`, `correlation`, `ssim`

**Exceptions**: `ImportError` (SimpleITK not installed), `ValueError` (unknown method)

---

### `ImageClassifier`

**Description**: Image classifier supporting ResNet18 / DenseNet121.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model_type` | `str` | No | `"resnet18"` | Model type |
| `num_classes` | `int` | No | `2` | Number of classes |
| `device` | `str` | No | `"cpu"` | Compute device |

**Methods**:

#### `classify(image)`

Perform classification.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | `np.ndarray` | Yes | — | Input image |

- **Returns**: `dict` — contains `prediction` (int), `confidence` (float), `probabilities` (list)

**Exceptions**: `ImportError` (PyTorch not installed), `ValueError` (unknown model)

---

### `FeatureSelector`

**Description**: Radiomics feature selector supporting 7 selection methods. Unsupervised: auto-uses variance_threshold + correlation_filter; supervised: all methods available.

**Parameters**: None.

**Methods**:

#### `select(features_df, labels=None, method="auto", n_features=20)`

Execute feature selection (unified entry point).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `features_df` | `pd.DataFrame` | Yes | — | Feature DataFrame (rows=samples, cols=features) |
| `labels` | `np.ndarray` | No | `None` | Label array (for supervised methods) |
| `method` | `str` | No | `"auto"` | Method (`"auto"`, `"variance"`, `"k_best"`, `"mutual_info"`, `"rfe"`, `"correlation"`) |
| `n_features` | `int` | No | `20` | Desired number of features to retain |

- **Returns**: `pd.DataFrame` — selected feature DataFrame

#### `variance_threshold(features_df, threshold=0.01)`

Variance threshold filtering.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `features_df` | `pd.DataFrame` | Yes | — | Feature DataFrame |
| `threshold` | `float` | No | `0.01` | Variance threshold |

- **Returns**: `pd.DataFrame`

#### `k_best(features_df, labels, k=20)`

K-best feature selection (F-test).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `features_df` | `pd.DataFrame` | Yes | — | Feature DataFrame |
| `labels` | `np.ndarray` | Yes | — | Label array |
| `k` | `int` | No | `20` | Number of features to select |

- **Returns**: `pd.DataFrame`

#### `mutual_info(features_df, labels, k=20)`

Mutual information feature selection.

- **Returns**: `pd.DataFrame`

#### `rfe(features_df, labels, n_features=20)`

Recursive feature elimination (RFE, based on RandomForest).

- **Returns**: `pd.DataFrame`

#### `correlation_filter(features_df, threshold=0.95)`

High correlation filtering.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `features_df` | `pd.DataFrame` | Yes | — | Feature DataFrame |
| `threshold` | `float` | No | `0.95` | Correlation coefficient threshold |

- **Returns**: `pd.DataFrame`

#### `auto_select(features_df, labels=None, n_features=20)`

Automatic selection pipeline. Unsupervised: variance_threshold -> correlation_filter; Supervised: variance_threshold -> correlation_filter -> mutual_info/k_best.

- **Returns**: `pd.DataFrame`

#### `get_selected_feature_names()`

Get the feature names from the most recent selection.

- **Returns**: `list[str]`
- **Example**:

```python
from msra_modules.medical_imaging import FeatureSelector

selector = FeatureSelector()
# Unsupervised
selected = selector.select(features_df, labels=None, method="auto", n_features=20)
# Supervised
selected = selector.select(features_df, labels=labels, method="auto", n_features=20)
print(selector.get_selected_feature_names())
```

**Exceptions**: `ValueError` (supervised method missing labels, unknown method)

---

### `ImagingQualityGateChecker`

**Description**: Imaging quality gate checker implementing Gate IMG-1 (data quality gate).

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `study_id` | `str` | Yes | — | Study ID |
| `project_root` | `str` | No | `None` | Project root directory |

**Methods**:

#### `run_gate_img1(image_path, mask_path=None)`

Execute Gate IMG-1 with all 4 checks: file readability, voxel spacing validity, ROI mask dimension match, image quality (SNR + NaN/Inf).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image_path` | `str` | Yes | — | Image file path (DICOM/NIfTI/NRRD) |
| `mask_path` | `str` | No | `None` | ROI mask file path |

- **Returns**: `GateResult` — verdict (`PASS` / `CONDITIONAL` / `BLOCKED`)
- **Example**:

```python
from msra_modules.medical_imaging import ImagingQualityGateChecker

checker = ImagingQualityGateChecker(study_id="IMG-2026-001")
result = checker.run_gate_img1(
    image_path="/data/scan.nii.gz",
    mask_path="/data/mask.nii.gz"
)
print(result.verdict)
```

**Exceptions**: `ImportError` (SimpleITK/nibabel not installed — corresponding check items marked as FAIL)

---

## Full Usage Example

```python
from msra_modules.medical_imaging import (
    load_nifti, ImagePreprocessor, RadiomicsExtractor,
    FeatureSelector, ImagingQualityGateChecker,
)
import SimpleITK as sitk

# 1. Load image
array, metadata = load_nifti("/data/scan.nii.gz")

# 2. Quality gate
checker = ImagingQualityGateChecker(study_id="IMG-2026-001")
gate_result = checker.run_gate_img1("/data/scan.nii.gz", "/data/mask.nii.gz")

# 3. Feature extraction
extractor = RadiomicsExtractor(bin_width=25.0)
features = extractor.extract_all(array, mask_array)

# 4. Export v1 schema
paths = extractor.export_v1_schema(features, "/output/radiomics/")

# 5. Feature selection (multi-sample scenario)
selector = FeatureSelector()
selected = selector.select(features_df, labels=labels, method="auto", n_features=20)
```
