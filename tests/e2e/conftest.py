"""E2E public fixtures for MSRA cross-domain module.

All mock data uses seed=42 for reproducibility.
Provides large-scale mock data generators for end-to-end testing.
"""

import sys
import os
import numpy as np
import pandas as pd
import pytest
from pathlib import Path

# Ensure project root is on sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Use non-interactive matplotlib backend
import matplotlib
matplotlib.use("Agg")

# Import fixture generators
from tests.e2e.fixtures.generate_mock_counts import (
    generate_mock_counts,
    generate_sample_info,
)
from tests.e2e.fixtures.generate_mock_nifti import generate_mock_nifti
from tests.e2e.fixtures.generate_mock_vitals import (
    generate_mock_vitals,
    generate_mock_vitals_dataframe,
)
from tests.e2e.fixtures.generate_mock_clinical import generate_mock_clinical
from tests.e2e.fixtures.generate_mock_labels import (
    generate_mock_labels,
    generate_mock_labels_from_vitals,
)


# ===== Seed control =====

@pytest.fixture(autouse=True)
def _set_e2e_seed():
    """Fix random seed for reproducibility (seed=42)."""
    np.random.seed(42)


# ===== Bioinformatics fixtures =====

@pytest.fixture
def e2e_counts_matrix():
    """Mock count matrix: 50 samples x 2000 genes (seed=42).

    Returns:
        pd.DataFrame: count matrix with sample index and gene columns.
    """
    return generate_mock_counts(n_samples=50, n_genes=2000, seed=42)


@pytest.fixture
def e2e_sample_info():
    """Mock sample info with condition and batch labels (seed=42)."""
    return generate_sample_info(n_samples=50, seed=42)


@pytest.fixture
def e2e_anndata(e2e_counts_matrix, e2e_sample_info):
    """Create an AnnData object from mock counts (requires anndata).

    Skips if anndata is not installed.
    """
    pytest.importorskip("anndata")
    import anndata as ad

    adata = ad.AnnData(
        X=e2e_counts_matrix.values.astype(np.float32),
        obs=e2e_sample_info.copy(),
        var=pd.DataFrame(index=e2e_counts_matrix.columns),
    )
    adata.obs_names = e2e_counts_matrix.index.tolist()
    adata.var_names = e2e_counts_matrix.columns.tolist()
    return adata


# ===== Medical imaging fixtures =====

@pytest.fixture
def e2e_nifti_image():
    """Mock 3D NIfTI image array (64x64x32, seed=42)."""
    image, _ = generate_mock_nifti(shape=(64, 64, 32), seed=42)
    return image


@pytest.fixture
def e2e_nifti_mask():
    """Mock binary mask array (64x64x32, seed=42)."""
    _, mask = generate_mock_nifti(shape=(64, 64, 32), seed=42)
    return mask


@pytest.fixture
def e2e_nifti_files(tmp_path):
    """Mock NIfTI files on disk (requires nibabel)."""
    nib = pytest.importorskip("nibabel")
    image, mask = generate_mock_nifti(
        shape=(64, 64, 32), seed=42, output_dir=str(tmp_path)
    )
    image_path = str(tmp_path / "mock_image.nii.gz")
    mask_path = str(tmp_path / "mock_mask.nii.gz")
    return image_path, mask_path


@pytest.fixture
def e2e_radiomics_features():
    """Mock radiomics feature matrix for 20 samples x 30 features (seed=42).

    Used as E2E-IMG-01 output and E2E-CD-01 input.
    Also serves as the base for e2e_expression_matrix correlation injection.
    """
    np.random.seed(42)
    n_samples = 20
    n_features = 30
    samples = [f"IMG_S{i:03d}" for i in range(n_samples)]
    feature_names = [f"radiomics_feat_{j:02d}" for j in range(n_features)]
    data = np.random.randn(n_samples, n_features) * 10 + 50
    return pd.DataFrame(data, index=samples, columns=feature_names)


# ===== Realtime analytics fixtures =====

@pytest.fixture
def e2e_vitals_dict():
    """Mock vital signs dict: 60s x 6 metrics (seed=42)."""
    return generate_mock_vitals(duration=60, interval=1.0, seed=42)


@pytest.fixture
def e2e_vitals_dict_anomaly():
    """Mock vital signs dict with injected anomalies: 120s (seed=42)."""
    return generate_mock_vitals(
        duration=120, interval=1.0, seed=42, inject_anomaly=True
    )


@pytest.fixture
def e2e_vitals_dataframe():
    """Mock vital signs DataFrame: 60s x 6 metrics (seed=42)."""
    return generate_mock_vitals_dataframe(duration=60, interval=1.0, seed=42)


@pytest.fixture
def e2e_vitals_dataframe_anomaly():
    """Mock vital signs DataFrame with anomalies: 120s (seed=42)."""
    return generate_mock_vitals_dataframe(
        duration=120, interval=1.0, seed=42, inject_anomaly=True
    )


# ===== Cross-domain fixtures =====

@pytest.fixture
def e2e_clinical_data():
    """Mock clinical data: 50 samples x 10 variables (seed=42)."""
    return generate_mock_clinical(n_samples=50, seed=42)


@pytest.fixture
def e2e_labels():
    """Mock binary labels for 50 samples (seed=42)."""
    return generate_mock_labels(n_samples=50, seed=42)


@pytest.fixture
def e2e_expression_matrix(e2e_radiomics_features):
    """Mock expression matrix: 20 samples x 50 genes (seed=42).

    Used as E2E-BIO-01 output and E2E-CD-01 input.
    Index aligns with e2e_radiomics_features for cross-domain testing.

    The first 10 genes are injected with strong correlation to the first
    10 radiomics features (r >= 0.8) to ensure Gate CD-3.5 significance
    checks pass with mock data.
    """
    np.random.seed(42)
    n_samples = 20
    n_genes = 50
    samples = list(e2e_radiomics_features.index)
    gene_names = [f"GENE{i:04d}" for i in range(n_genes)]

    # Base random expression
    data = np.random.randn(n_samples, n_genes) * 2 + 8

    # Inject strong correlation: first 10 genes = linear function of first 10 features
    radiomics_vals = e2e_radiomics_features.values
    for i in range(10):
        # gene_i = 0.8 * normalized(feature_i) + small_noise
        feat = radiomics_vals[:, i]
        feat_norm = (feat - feat.mean()) / (feat.std() + 1e-10)
        data[:, i] = feat_norm * 3 + 8 + np.random.randn(n_samples) * 0.1

    return pd.DataFrame(data, index=samples, columns=gene_names)


@pytest.fixture
def e2e_historical_vitals():
    """Mock historical vitals DataFrame for prediction model training.

    20 samples x 60 timepoints. Data is structured so that samples with
    higher mean values tend to have label=1, ensuring the model can learn
    meaningful patterns (AUROC >= 0.55).
    """
    np.random.seed(42)
    n_samples = 20
    n_timepoints = 60
    # Create two groups: "high risk" (higher values) and "low risk" (lower values)
    n_high = n_samples // 2
    data = np.zeros((n_samples, n_timepoints))
    # High-risk group: mean ~90 with higher variance
    data[:n_high] = np.random.randn(n_high, n_timepoints) * 4 + 90
    # Low-risk group: mean ~70 with lower variance
    data[n_high:] = np.random.randn(n_samples - n_high, n_timepoints) * 3 + 70
    return pd.DataFrame(data, columns=[f"t{i}" for i in range(n_timepoints)])


@pytest.fixture
def e2e_prediction_labels(e2e_historical_vitals):
    """Mock prediction labels for 20 samples, correlated with vitals data.

    Labels are assigned based on mean vitals value: samples with mean > 80
    get label=1 (high risk), others get label=0. This ensures the model
    can learn a meaningful pattern.
    """
    mean_vals = e2e_historical_vitals.mean(axis=1).values
    labels = (mean_vals > 80).astype(int)
    # Ensure both classes are present
    if labels.sum() == 0:
        labels[:len(labels) // 2] = 1
    elif labels.sum() == len(labels):
        labels[len(labels) // 2:] = 0
    return labels


# ===== Output directory fixture =====

@pytest.fixture
def e2e_output_dir(tmp_path):
    """Clean output directory for E2E test artifacts."""
    out = tmp_path / "e2e_output"
    out.mkdir(parents=True, exist_ok=True)
    return str(out)
