# MSRA Medical Imaging Module User Tutorial

> **Module Version**: v1.2.0 | **Document Date**: 2026-06-25 | **Status**: Stable
> **Command Entry**: `/msra-imaging` | **MSRA Version**: v1.0.0+

---

## 1. Module Overview & Use Cases

### Overview

The MSRA Medical Imaging module provides a standardized analysis pipeline for extracting quantitative radiomics features from medical imaging data. It supports DICOM, NIfTI, and NRRD formats, covering the complete chain from image loading, preprocessing, segmentation, feature extraction, to feature selection.

### Core Capabilities

| Capability | Description |
|------------|-------------|
| Image Loading | DICOM series / NIfTI / NRRD via `load_dicom_series`, `load_nifti`, `load_nrrd` |
| Preprocessing | Intensity normalization, resampling, denoising via `ImagePreprocessor` |
| Segmentation | MONAI 3D U-Net via `SegmentationPipeline` |
| Feature Extraction | Shape/first-order/texture (GLCM/GLRLM/GLSZM/GLDM/NGTDM) via `RadiomicsExtractor` |
| Feature Selection | Variance/K-best/mutual info/RFE/correlation filter via `FeatureSelector` |
| Registration | Elastic registration via `ImageRegistration` |
| Quality Gate | Gate IMG-1 (data quality) via `ImagingQualityGateChecker` |

### Use Cases

- Tumor imaging radiomics feature extraction and modeling
- Batch processing of DICOM CT/MRI series
- ROI mask-based radiomics feature extraction
- Feature selection and dimensionality reduction (supervised and unsupervised)
- Integrating imaging feature matrices into the MSRA main Pipeline for joint modeling

---

## 2. Installation

### Install medical_imaging extra dependencies

```bash
pip install -e ".[medical_imaging]"
```

### Core Dependencies

```toml
nibabel >= 4.0         # NIfTI file I/O
SimpleITK >= 2.3       # DICOM reading and image processing
pyradiomics >= 3.1     # Radiomics feature extraction
scikit-image >= 0.20   # Image processing utilities
```

### Verify Installation

```bash
python -c "from msra_modules.medical_imaging import load_nifti, RadiomicsExtractor, FeatureSelector, ImagingQualityGateChecker; print('OK')"
```

---

## 3. Data Preparation

### Supported Image Formats

| Format | Extension | Description | Typical Source |
|--------|-----------|-------------|----------------|
| DICOM | `.dcm` | Directory with multiple slice files | CT/MRI scanners |
| NIfTI | `.nii` / `.nii.gz` | Single file with complete 3D/4D data | Preprocessed images |
| NRRD | `.nrrd` | Near Raw Raster Data | Slicer and similar tools |

### ROI Mask File

Feature extraction requires an ROI (Region of Interest) mask file. The mask should be a binarized file matching the image dimensions (1 for ROI, 0 for background):

```
Image file: scan.nii.gz      (512×512×200)
Mask file:  mask.nii.gz      (512×512×200, binary)
```

### Example: Prepare Mock Data

```python
import numpy as np
import nibabel as nib

# Generate mock CT volume (64×64×32)
np.random.seed(42)
volume = np.random.randint(0, 100, size=(64, 64, 32), dtype=np.int16)
# Simulate tumor in center region
volume[20:44, 20:44, 10:22] = np.random.randint(80, 200, size=(24, 24, 12))
nib.save(nib.Nifti1Image(volume, np.eye(4)), "mock_scan.nii.gz")

# Generate corresponding mask
mask = np.zeros((64, 64, 32), dtype=np.int8)
mask[20:44, 20:44, 10:22] = 1
nib.save(nib.Nifti1Image(mask, np.eye(4)), "mock_mask.nii.gz")
print("Mock data created: mock_scan.nii.gz, mock_mask.nii.gz")
```

---

## 4. Image Loading & Preprocessing

### Image Loading

```python
from msra_modules.medical_imaging import (
    load_dicom_series, load_nifti, load_nrrd, DICOMLoader,
)

# Method 1: Load DICOM series
dicom_loader = DICOMLoader(window_level=40, window_width=400)  # CT lung window
sitk_image = dicom_loader.load_dicom_series("/path/to/dicom/")

# Method 2: Load NIfTI file
nifti_data = load_nifti("scan.nii.gz")  # Returns numpy array

# Method 3: Load NRRD file
nrrd_data = load_nrrd("scan.nrrd")
```

### Preprocessing

```python
from msra_modules.medical_imaging import ImagePreprocessor

preprocessor = ImagePreprocessor(
    target_spacing=(1.0, 1.0, 1.0),  # Resample to 1mm isotropic
    normalize_method="z_score",       # Normalization method
)

# Preprocess image
processed_image = preprocessor.preprocess(sitk_image)
```

### Gate IMG-1 Data Quality Gate

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

## 5. Radiomics Feature Extraction

### Complete Feature Extraction Pipeline

```python
from msra_modules.medical_imaging import RadiomicsExtractor

# Initialize feature extractor
extractor = RadiomicsExtractor(bin_width=25.0)

# Extract shape features (based on mask)
shape_features = extractor.extract_shape_features(mask_array)
print(f"Shape features: {len(shape_features)}")
# Includes: VoxelVolume, SurfaceArea, Maximum3DDiameter, etc.

# Extract first-order statistics features
firstorder_features = extractor.extract_firstorder_features(image_array, mask_array)
print(f"First-order features: {len(firstorder_features)}")
# Includes: Mean, Median, Std, Skewness, Kurtosis, Energy, Entropy, etc.

# Extract texture features
glcm_features = extractor.extract_glcm_features(image_array, mask_array)
print(f"GLCM features: {len(glcm_features)}")
# Includes: Contrast, Correlation, Homogeneity, Energy, etc.

# Combine into feature matrix
all_features = {**shape_features, **firstorder_features, **glcm_features}
```

### Batch Feature Extraction

```python
import pandas as pd

# Batch extraction for multiple samples
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

# Build feature matrix (sample × feature)
feature_df = pd.DataFrame(feature_rows).set_index("sample_id")
feature_df.to_csv("radiomics_features.csv")
print(f"Feature matrix: {feature_df.shape}")
```

---

## 6. Feature Selection Methods Comparison

### Supported Methods

| Method | Parameter | Use Case | Requires Labels |
|--------|-----------|----------|-----------------|
| `auto` | Automatic combination | General purpose | Optional |
| `variance` | Variance threshold | Remove low-variance features | No |
| `k_best` | K-best features | Supervised selection | Yes |
| `mutual_info` | Mutual information | Non-linear relationships | Yes |
| `rfe` | Recursive feature elimination | Fine-grained selection | Yes |
| `correlation` | Correlation filter | Remove redundant features | No |

### Method Comparison Example

```python
from msra_modules.medical_imaging import FeatureSelector
import pandas as pd

# Load feature matrix
features_df = pd.read_csv("radiomics_features.csv", index_col=0)
labels = pd.read_csv("labels.csv")["label"].values  # 0/1

selector = FeatureSelector()

# Method 1: Unsupervised — auto (variance + correlation filter)
selected_auto = selector.select(features_df, labels=None, method="auto", n_features=20)
print(f"Auto selected: {selected_auto.shape[1]} features")

# Method 2: Supervised — K-Best (F-test)
selected_kbest = selector.select(features_df, labels=labels, method="k_best", n_features=15)
print(f"K-Best selected: {selected_kbest.shape[1]} features")

# Method 3: Supervised — Mutual Information
selected_mi = selector.select(features_df, labels=labels, method="mutual_info", n_features=15)
print(f"Mutual info selected: {selected_mi.shape[1]} features")

# Method 4: Supervised — Recursive Feature Elimination (RFE)
selected_rfe = selector.select(features_df, labels=labels, method="rfe", n_features=10)
print(f"RFE selected: {selected_rfe.shape[1]} features")

# Method 5: Unsupervised — Correlation filter
selected_corr = selector.select(features_df, labels=None, method="correlation")
print(f"Correlation filtered: {selected_corr.shape[1]} features")
```

### Recommended Strategy

- **Exploration phase (unsupervised)**: Use `auto` method (variance filter + correlation deduplication)
- **Modeling phase (supervised)**: First use `correlation` to remove redundancy, then `k_best` or `mutual_info`
- **Fine optimization**: Use `rfe` for stepwise elimination, but note higher computational cost

---

## 7. Quality Gates

### Gate IMG-1 — Data Quality Gate

> Executed in Phase 1 (after data loading), blocks unqualified data from entering the analysis pipeline.
> Implementation: `msra_modules/medical_imaging/quality_gates.py` → `ImagingQualityGateChecker`

| # | Check Item | Critical | Pass Criteria |
|---|------------|----------|---------------|
| 1 | File readability | 🔑 | DICOM/NIfTI file can be successfully read |
| 2 | Voxel spacing合理性 | 🔑 | spacing ∈ [0.5, 5.0] mm |
| 3 | ROI mask dimension match | 🔑 | image.shape == mask.shape |
| 4 | Image quality | | SNR > 5, no NaN/Inf |

**Verdict Rules**:
- **PASS**: 4/4 checks passed
- **CONDITIONAL**: 2-3/4 passed and all 🔑 passed
- **BLOCKED**: ≤ 1/4 passed or any 🔑 failed (**blocks the pipeline**)

### Python Usage Example

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

## 8. Integration with Main Pipeline

### Export Feature Matrix for Main Pipeline

```python
import pandas as pd

# Export standard format feature matrix
selected_features.to_csv(
    "MSRA/data/imaging_features_v1.csv",
    index_label="sample_id",
)
```

### Automatic Pipeline Integration

In Phase 4, select the "Integrate with Pipeline" option. The system will:
1. Write the feature matrix to `MSRA/data/imaging_features_v1.csv`
2. Automatically trigger `/msra-exec` to incorporate it as predictor variables in Stage 3

### Command-Line Direct Invocation

```
/msra-imaging --nifti scan.nii.gz --roi mask.nii.gz --mode radiomics --integrate-pipeline
```

---

## 9. FAQ

### Q1: SimpleITK installation fails?

SimpleITK may need to be compiled from source on some systems. We recommend using conda:

```bash
conda install -c conda-forge simpleitk
```

### Q2: DICOM directory is detected as empty?

Ensure the directory contains `.dcm` files. Some DICOM files have no extension. You can verify using:

```python
import SimpleITK as sitk
series_ids = sitk.ImageSeriesReader.GetGDCMSeriesIDs("dicom_dir/")
print(f"Found {len(series_ids)} series")
```

### Q3: ROI mask dimensions don't match the image?

This is a critical check in Gate IMG-1. Please ensure:
1. Mask and image use the same voxel spacing
2. Mask and image dimensions are exactly identical
3. Use `ImagePreprocessor` to apply the same resampling to both image and mask

### Q4: Feature matrix contains many NaN values?

Possible causes:
1. ROI region is empty or too small → Check mask file
2. Some texture features cannot be computed in uniform regions → Use `FeatureSelector`'s `variance` method to filter

### Q5: MONAI segmentation model fails to load?

MONAI is an optional dependency. If not installed, the system falls back to threshold-based segmentation:

```bash
pip install monai  # Install MONAI for deep learning segmentation
```

### Q6: How to choose an appropriate bin_width?

`bin_width` affects the discretization of the gray-level histogram:
- CT images: 25 HU recommended (default)
- MRI images: 5-10 recommended
- PET images: 0.1 recommended

---

> **Related Docs**: [SKILL.md](../../skills/imaging-analysis/SKILL.md) | [MSRA Docs Home](../system_design.md)
