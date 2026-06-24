# Medical Imaging Module API Reference

> **Version**: v1.0.0 | **Date**: 2026-06-26 | **Status**: Stable
> **Module**: Medical Imaging | **Command**: `/imaging`

---

## Table of Contents

- [load_dicom_series() — DICOM Loading](#load_dicom_series)
- [load_nifti() — NIfTI Loading](#load_nifti)
- [load_nrrd() — NRRD Loading](#load_nrrd)
- [preprocess_image() — Preprocessing](#preprocess_image)
- [SegmentationPipeline — Segmentation](#segmentationpipeline)
- [ImageRegistration — Registration](#imageregistration)
- [RadiomicsExtractor — Radiomics Features](#radiomicsextractor)
- [FeatureSelector — Feature Selection](#featureselector)
- [ImagingQualityGateChecker — Quality Gate](#imagingqualitygatechecker)

---

## load_dicom_series

> Convenience function: load a DICOM series and return numpy array with metadata.

**Signature**:

```python
load_dicom_series(dicom_dir: str) -> Tuple[np.ndarray, Dict]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| dicom_dir | str | — | Required. DICOM file directory |

**Returns**: `Tuple[np.ndarray, Dict]` — (numpy array, metadata dict)

**Example**:

```python
from msra_modules.medical_imaging import load_dicom_series

array, metadata = load_dicom_series("data/CT_scans/")
print(f"Image shape: {array.shape}, spacing: {metadata['spacing']}")
```

**Exceptions**: `FileNotFoundError` — directory not found or no DICOM files; `ImportError` — SimpleITK not installed

---

## load_nifti

> Convenience function: load a NIfTI file (.nii / .nii.gz) and return numpy array with metadata.

**Signature**:

```python
load_nifti(nifti_path: str) -> Tuple[np.ndarray, Dict]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| nifti_path | str | — | Required. NIfTI file path |

**Returns**: `Tuple[np.ndarray, Dict]` — (numpy array, metadata dict with size, spacing, dtype, dimensions, affine)

**Exceptions**: `ImportError` — nibabel not installed; `FileNotFoundError` — file not found

---

## load_nrrd

> Convenience function: load a NRRD file and return numpy array with metadata.

**Signature**:

```python
load_nrrd(nrrd_path: str) -> Tuple[np.ndarray, Dict]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| nrrd_path | str | — | Required. NRRD file path |

**Returns**: `Tuple[np.ndarray, Dict]` — (numpy array, metadata dict with size, spacing, origin, direction, pixel_type, dimensions)

**Exceptions**: `ImportError` — SimpleITK not installed; `FileNotFoundError` — file not found

---

## preprocess_image

> Convenience function: normalize numpy array intensity (supports min_max and z_score methods).

**Signature**:

```python
normalize_intensity(array: np.ndarray, method: str = "min_max") -> np.ndarray
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| array | np.ndarray | — | Required. Input array |
| method | str | "min_max" | Normalization method ("min_max" or "z_score") |

**Returns**: `np.ndarray` — Normalized array

**Exceptions**: `ValueError` — unknown method

### DICOMLoader Class

For finer-grained control, use the `DICOMLoader` class:

```python
from msra_modules.medical_imaging import DICOMLoader

loader = DICOMLoader(window_level=40, window_width=400)
image = loader.load_dicom_series("data/CT_scans/")
array = loader.to_numpy(image)
metadata = loader.extract_metadata(image)
windowed = loader.apply_window(image)
```

**DICOMLoader Signature**:

```python
DICOMLoader(window_level: Optional[float] = None, window_width: Optional[float] = None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| window_level | Optional[float] | None | Window level (HU center) |
| window_width | Optional[float] | None | Window width (HU range) |

### ImagePreprocessor Class

```python
from msra_modules.medical_imaging import ImagePreprocessor

preprocessor = ImagePreprocessor(target_spacing=(1.0, 1.0, 1.0), normalize=True)
processed = preprocessor.preprocess_pipeline(image)
```

**ImagePreprocessor Signature**:

```python
ImagePreprocessor(target_spacing: Optional[Tuple[float, float, float]] = None, normalize: bool = True)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| target_spacing | Optional[Tuple[float, float, float]] | None | Target voxel spacing (x, y, z) |
| normalize | bool | True | Whether to normalize to [0, 1] |

**Methods**: `resample()`, `normalize_intensity()`, `denoise()`, `bias_correction()`, `preprocess_pipeline()`

---

## SegmentationPipeline

> Image segmentation pipeline based on MONAI's 3D U-Net model.

**Signature**:

```python
SegmentationPipeline(model_name: str = "spleen_ct", device: str = "cpu")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| model_name | str | "spleen_ct" | MONAI pretrained model name |
| device | str | "cpu" | Compute device ("cpu" or "cuda") |

**Methods**:

### `segment`

```python
segment(image: np.ndarray) -> np.ndarray
```

Execute segmentation.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| image | np.ndarray | — | Required. Input image (D, H, W) or (1, D, H, W) |

**Returns**: `np.ndarray` — Segmentation mask (D, H, W)

**Exceptions**: `ImportError` — MONAI not installed

### `segment_with_confidence`

```python
segment_with_confidence(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]
```

Segment and return confidence map.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| image | np.ndarray | — | Required. Input image |

**Returns**: `Tuple[np.ndarray, np.ndarray]` — (segmentation mask, confidence map)

### `preprocess`

```python
preprocess(image: np.ndarray) -> np.ndarray
```

Preprocess image (normalize + add channel dimension).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| image | np.ndarray | — | Required. Input image (D, H, W) |

**Returns**: `np.ndarray` — Preprocessed image (1, D, H, W)

**Example**:

```python
from msra_modules.medical_imaging import SegmentationPipeline

seg = SegmentationPipeline(model_name="spleen_ct", device="cuda")
mask = seg.segment(image_array)
mask, confidence = seg.segment_with_confidence(image_array)
```

---

## ImageRegistration

> Medical image registration supporting rigid, affine, and bspline transformation methods.

**Signature**:

```python
ImageRegistration(method: str = "rigid")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| method | str | "rigid" | Registration method ("rigid", "affine", "bspline") |

**Methods**:

### `register`

```python
register(fixed_image, moving_image, fixed_mask=None, moving_mask=None) -> Dict
```

Execute registration.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| fixed_image | SimpleITK.Image | — | Required. Fixed image |
| moving_image | SimpleITK.Image | — | Required. Moving image |
| fixed_mask | SimpleITK.Image | None | Fixed image mask (optional) |
| moving_mask | SimpleITK.Image | None | Moving image mask (optional) |

**Returns**: `Dict` — Contains `transform`, `resampled_image`, `metric_value`, `iterations`, `method`

**Exceptions**: `ValueError` — unknown method

### `evaluate`

```python
evaluate(fixed_image, moving_image, mask=None) -> Dict
```

Evaluate registration quality.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| fixed_image | SimpleITK.Image | — | Required. Fixed image |
| moving_image | SimpleITK.Image | — | Required. Moving image |
| mask | SimpleITK.Image | None | Evaluation region mask (optional) |

**Returns**: `Dict` — Contains `mse`, `mae`, `correlation`, `ssim`

**Example**:

```python
from msra_modules.medical_imaging import ImageRegistration

reg = ImageRegistration(method="rigid")
result = reg.register(fixed_img, moving_img)
print(f"Metric: {result['metric_value']:.4f}, iterations: {result['iterations']}")

metrics = reg.evaluate(fixed_img, result["resampled_image"])
print(f"MSE: {metrics['mse']:.4f}, SSIM: {metrics['ssim']:.4f}")
```

---

## RadiomicsExtractor

> Radiomics feature extractor for shape, first-order statistics, and texture features.

**Signature**:

```python
RadiomicsExtractor(bin_width: float = 25.0)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| bin_width | float | 25.0 | Gray-level histogram bin width |

**Methods**:

### `extract_shape_features`

```python
extract_shape_features(mask: np.ndarray) -> Dict[str, float]
```

Extract shape features (volume, surface area, max 3D diameter, axis lengths, sphericity).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| mask | np.ndarray | — | Required. Segmentation mask (binary) |

**Returns**: `Dict[str, float]` — Shape features (VoxelVolume, SurfaceArea, Maximum3DDiameter, MajorAxisLength, MinorAxisLength, LeastAxisLength, Sphericity)

### `extract_firstorder_features`

```python
extract_firstorder_features(image: np.ndarray, mask: np.ndarray) -> Dict[str, float]
```

Extract first-order statistics features (mean, median, std, skewness, kurtosis, energy, entropy).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| image | np.ndarray | — | Required. Image data |
| mask | np.ndarray | — | Required. Segmentation mask |

**Returns**: `Dict[str, float]` — First-order features (Mean, Median, Std, Variance, Minimum, Maximum, Range, Percentile10/25/75/90, IQR, Skewness, Kurtosis, Energy, Entropy, RootMeanSquared, MeanAbsoluteDeviation)

### `extract_texture_features`

```python
extract_texture_features(image: np.ndarray, mask: np.ndarray) -> Dict[str, float]
```

Extract texture features (simplified GLCM).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| image | np.ndarray | — | Required. Image data |
| mask | np.ndarray | — | Required. Segmentation mask |

**Returns**: `Dict[str, float]` — Texture features (GLCM_Contrast, GLCM_Dissimilarity, GLCM_Homogeneity, GLCM_Energy, GLCM_Correlation, GLCM_ASM)

### `extract_all`

```python
extract_all(image: np.ndarray, mask: np.ndarray) -> Dict[str, Dict[str, float]]
```

Extract all radiomics features.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| image | np.ndarray | — | Required. Image data |
| mask | np.ndarray | — | Required. Segmentation mask |

**Returns**: `Dict[str, Dict[str, float]]` — All features (contains "shape", "firstorder", "texture" categories)

### `to_dataframe`

```python
to_dataframe(features: Dict) -> pd.DataFrame
```

Convert to DataFrame format.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| features | Dict | — | Required. Features dict (output of extract_all) |

**Returns**: `pd.DataFrame` — With feature_class, feature_name, value columns

### `export_v1_schema`

```python
export_v1_schema(features: Dict, output_dir: str) -> Dict[str, str]
```

Export msra/imaging_features/v1 standard format (feature_matrix.csv + feature_metadata.csv).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| features | Dict | — | Required. Features dict (output of extract_all) |
| output_dir | str | — | Required. Output directory |

**Returns**: `Dict[str, str]` — File path mapping (feature_matrix, feature_metadata, schema_version)

**Example**:

```python
from msra_modules.medical_imaging import RadiomicsExtractor

extractor = RadiomicsExtractor(bin_width=25.0)
features = extractor.extract_all(image_array, mask_array)
print(f"Total features: {sum(len(v) for v in features.values())}")

df = extractor.to_dataframe(features)
extractor.export_v1_schema(features, "output/radiomics/")
```

---

## FeatureSelector

> Radiomics feature selector supporting 7 methods: variance threshold, K-best, mutual info, RFE, and correlation filter.

**Signature**:

```python
FeatureSelector()
```

**Methods**:

### `select`

```python
select(features_df: pd.DataFrame, labels: Optional[np.ndarray] = None, method: str = "auto", n_features: int = 20) -> pd.DataFrame
```

Execute feature selection.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| features_df | pd.DataFrame | — | Required. Feature DataFrame (rows=samples, cols=features) |
| labels | Optional[np.ndarray] | None | Labels array (optional, for supervised methods) |
| method | str | "auto" | Selection method ("auto", "variance", "k_best", "mutual_info", "rfe", "correlation") |
| n_features | int | 20 | Desired number of features to keep |

**Returns**: `pd.DataFrame` — Selected features DataFrame

**Exceptions**: `ValueError` — supervised method without labels, or unknown method

### `variance_threshold`

```python
variance_threshold(features_df: pd.DataFrame, threshold: float = 0.01) -> pd.DataFrame
```

Variance threshold filtering (remove features with variance below threshold).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| features_df | pd.DataFrame | — | Required. Feature DataFrame |
| threshold | float | 0.01 | Variance threshold |

**Returns**: `pd.DataFrame` — Filtered features DataFrame

### `k_best`

```python
k_best(features_df: pd.DataFrame, labels: np.ndarray, k: int = 20) -> pd.DataFrame
```

K-best feature selection (F-test).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| features_df | pd.DataFrame | — | Required. Feature DataFrame |
| labels | np.ndarray | — | Required. Labels array |
| k | int | 20 | Number of features to select |

**Returns**: `pd.DataFrame` — Selected features DataFrame

### `mutual_info`

```python
mutual_info(features_df: pd.DataFrame, labels: np.ndarray, k: int = 20) -> pd.DataFrame
```

Mutual information feature selection.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| features_df | pd.DataFrame | — | Required. Feature DataFrame |
| labels | np.ndarray | — | Required. Labels array |
| k | int | 20 | Number of features to select |

**Returns**: `pd.DataFrame` — Selected features DataFrame

### `rfe`

```python
rfe(features_df: pd.DataFrame, labels: np.ndarray, n_features: int = 20) -> pd.DataFrame
```

Recursive feature elimination (RFE + RandomForest).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| features_df | pd.DataFrame | — | Required. Feature DataFrame |
| labels | np.ndarray | — | Required. Labels array |
| n_features | int | 20 | Desired number of features to keep |

**Returns**: `pd.DataFrame` — Selected features DataFrame

### `correlation_filter`

```python
correlation_filter(features_df: pd.DataFrame, threshold: float = 0.95) -> pd.DataFrame
```

High correlation filtering (remove highly correlated features).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| features_df | pd.DataFrame | — | Required. Feature DataFrame |
| threshold | float | 0.95 | Correlation coefficient threshold |

**Returns**: `pd.DataFrame` — Filtered features DataFrame

### `auto_select`

```python
auto_select(features_df: pd.DataFrame, labels: Optional[np.ndarray] = None, n_features: int = 20) -> pd.DataFrame
```

Auto selection pipeline (unsupervised: variance → correlation; supervised: variance → correlation → k_best/mutual_info).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| features_df | pd.DataFrame | — | Required. Feature DataFrame |
| labels | Optional[np.ndarray] | None | Labels array (optional) |
| n_features | int | 20 | Desired number of features to keep |

**Returns**: `pd.DataFrame` — Selected features DataFrame

### `get_selected_feature_names`

```python
get_selected_feature_names() -> List[str]
```

Get feature names from the most recent selection.

**Returns**: `List[str]` — Selected feature names

**Example**:

```python
from msra_modules.medical_imaging import FeatureSelector

selector = FeatureSelector()

# Unsupervised
selected = selector.select(features_df, method="auto", n_features=20)

# Supervised
selected = selector.select(features_df, labels=labels, method="auto", n_features=20)
print(f"Selected: {selector.get_selected_feature_names()}")
```

---

## ImagingQualityGateChecker

> Imaging quality gate checker encapsulating Gate IMG-1 check logic.

**Signature**:

```python
ImagingQualityGateChecker(study_id: str, project_root: Optional[str] = None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| study_id | str | — | Required. Study ID |
| project_root | Optional[str] | None | Project root directory (optional) |

**Methods**:

### `run_gate_img1`

```python
run_gate_img1(image_path: str, mask_path: Optional[str] = None) -> GateResult
```

Execute Gate IMG-1 with 4 checks: file readability, voxel spacing, ROI mask dimension match, image quality (SNR + NaN/Inf).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| image_path | str | — | Required. Image file path (DICOM/NIfTI/NRRD) |
| mask_path | Optional[str] | None | ROI mask file path (optional) |

**Returns**: `GateResult` — Verdict (PASS / CONDITIONAL / BLOCKED)

### `check_file_readable`

```python
check_file_readable(file_path: str) -> CheckItemResult
```

Public interface: check file readability.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| file_path | str | — | Required. File path |

**Returns**: `CheckItemResult`

### `check_voxel_spacing`

```python
check_voxel_spacing(image_metadata: Dict[str, Any], min_spacing: float = 0.5, max_spacing: float = 5.0) -> CheckItemResult
```

Public interface: check voxel spacing validity.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| image_metadata | Dict[str, Any] | — | Required. Image metadata (must contain spacing field) |
| min_spacing | float | 0.5 | Minimum allowed spacing (mm) |
| max_spacing | float | 5.0 | Maximum allowed spacing (mm) |

**Returns**: `CheckItemResult`

### `check_roi_match`

```python
check_roi_match(image_data: np.ndarray, mask_path: str) -> CheckItemResult
```

Public interface: check ROI mask dimension match with image.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| image_data | np.ndarray | — | Required. Image numpy array |
| mask_path | str | — | Required. Mask file path |

**Returns**: `CheckItemResult`

### `check_image_quality`

```python
check_image_quality(image_data: np.ndarray) -> CheckItemResult
```

Public interface: check image quality (SNR + NaN/Inf).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| image_data | np.ndarray | — | Required. Image numpy array |

**Returns**: `CheckItemResult`

**Example**:

```python
from msra_modules.medical_imaging import ImagingQualityGateChecker

checker = ImagingQualityGateChecker(study_id="IMG-2026-001")
gate_result = checker.run_gate_img1(
    image_path="data/scan.nii.gz",
    mask_path="data/mask.nii.gz"
)
print(f"IMG-1 verdict: {gate_result.verdict.value}")
print(f"Pass rate: {gate_result.pass_rate:.1%}")
```

---

## Shared Types Reference

### CheckItemResult

| Property | Type | Description |
|----------|------|-------------|
| item_id | str | Check item ID |
| name | str | Check item name |
| is_key | bool | Whether it is a key item |
| status | str | Status (PASS / FAIL / N/A / SKIP) |
| evidence | str | Evidence description |
| notes | str | Notes |

### GateVerdict

| Value | Description |
|-------|-------------|
| PASS | All passed |
| CONDITIONAL | Conditional pass |
| BLOCKED | Blocked |
