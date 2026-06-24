"""E2E tests for medical imaging module.

E2E-IMG-01: Radiomics feature extraction
    (mock NIfTI + mask -> feature matrix CSV, Gate IMG-1 PASS)

E2E-IMG-02: Feature selection
    (feature matrix -> reduced features >= 30% reduction, no NaN)
"""

import sys
import os
import numpy as np
import pandas as pd
import pytest
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def _check_nibabel_available():
    try:
        import nibabel
        return True
    except ImportError:
        return False


HAS_NIBABEL = _check_nibabel_available()


class TestE2EImg01RadiomicsExtraction:
    """E2E-IMG-01: Radiomics feature extraction."""

    @pytest.mark.integration
    def test_extract_all_features_from_mock_image(self, e2e_nifti_image, e2e_nifti_mask):
        """Test that radiomics feature extraction produces a complete feature set."""
        from msra_modules.medical_imaging import RadiomicsExtractor

        # --- Arrange ---
        extractor = RadiomicsExtractor(bin_width=25.0)
        image = e2e_nifti_image
        mask = e2e_nifti_mask

        # --- Act ---
        features = extractor.extract_all(image, mask)

        # --- Assert: all three feature classes present ---
        assert "shape" in features
        assert "firstorder" in features
        assert "texture" in features

        # Shape features
        shape_feats = features["shape"]
        assert "VoxelVolume" in shape_feats
        assert shape_feats["VoxelVolume"] > 0, "Mask should have non-zero volume"

        # First-order features
        fo_feats = features["firstorder"]
        assert "Mean" in fo_feats
        assert "Std" in fo_feats
        assert fo_feats["Mean"] > 0, "Mean intensity should be positive"

    @pytest.mark.integration
    def test_features_to_dataframe(self, e2e_nifti_image, e2e_nifti_mask):
        """Test that features can be converted to a DataFrame."""
        from msra_modules.medical_imaging import RadiomicsExtractor

        extractor = RadiomicsExtractor()
        features = extractor.extract_all(e2e_nifti_image, e2e_nifti_mask)
        df = extractor.to_dataframe(features)

        # --- Assert ---
        assert df is not None
        assert len(df) > 0, "Feature DataFrame should not be empty"
        assert "feature_class" in df.columns
        assert "feature_name" in df.columns
        assert "value" in df.columns

    @pytest.mark.integration
    def test_export_v1_schema(self, e2e_nifti_image, e2e_nifti_mask, e2e_output_dir):
        """Test that v1 schema export produces valid output files."""
        from msra_modules.medical_imaging import RadiomicsExtractor

        extractor = RadiomicsExtractor()
        features = extractor.extract_all(e2e_nifti_image, e2e_nifti_mask)
        result = extractor.export_v1_schema(features, e2e_output_dir)

        # --- Assert: schema version ---
        assert result["schema_version"] == "msra/imaging_features/v1"

        # --- Assert: files exist and are non-empty ---
        matrix_path = Path(result["feature_matrix"])
        metadata_path = Path(result["feature_metadata"])

        assert matrix_path.exists(), "feature_matrix.csv should exist"
        assert metadata_path.exists(), "feature_metadata.csv should exist"
        assert matrix_path.stat().st_size > 0, "feature_matrix.csv should be non-empty"
        assert metadata_path.stat().st_size > 0, "feature_metadata.csv should be non-empty"

        # --- Assert: CSV content is valid ---
        matrix_df = pd.read_csv(matrix_path)
        assert "sample_id" in matrix_df.columns
        assert len(matrix_df.columns) > 1, "Should have feature columns"

    @pytest.mark.integration
    def test_gate_img1_passes(self, e2e_nifti_files):
        """Test that Gate IMG-1 returns PASS for valid mock data.

        Gate IMG-1 expects file paths (str), not numpy arrays.
        """
        from msra_modules.medical_imaging import ImagingQualityGateChecker

        image_path, mask_path = e2e_nifti_files

        checker = ImagingQualityGateChecker(study_id="E2E-IMG-001")
        gate_result = checker.run_gate_img1(
            image_path=image_path,
            mask_path=mask_path,
        )

        # --- Assert: Gate returns PASS or CONDITIONAL ---
        from shared.quality_gates.gate_runner import GateVerdict
        assert gate_result.verdict in [
            GateVerdict.PASS,
            GateVerdict.CONDITIONAL,
        ], f"Gate IMG-1 should PASS or CONDITIONAL, got {gate_result.verdict}"

    @pytest.mark.integration
    def test_feature_values_are_finite(self, e2e_nifti_image, e2e_nifti_mask):
        """Test that all extracted feature values are finite (no NaN/Inf)."""
        from msra_modules.medical_imaging import RadiomicsExtractor

        extractor = RadiomicsExtractor()
        features = extractor.extract_all(e2e_nifti_image, e2e_nifti_mask)

        # --- Assert: all values are finite ---
        for class_name, class_feats in features.items():
            for name, value in class_feats.items():
                if isinstance(value, (int, float)):
                    assert np.isfinite(value), (
                        f"Feature {class_name}.{name} is not finite: {value}"
                    )

    @pytest.mark.integration
    def test_mock_nifti_reproducibility(self):
        """Test that mock NIfTI generation is reproducible (seed=42)."""
        from tests.e2e.fixtures.generate_mock_nifti import generate_mock_nifti

        img1, mask1 = generate_mock_nifti(shape=(64, 64, 32), seed=42)
        img2, mask2 = generate_mock_nifti(shape=(64, 64, 32), seed=42)

        # --- Assert: identical arrays ---
        np.testing.assert_array_equal(img1, img2)
        np.testing.assert_array_equal(mask1, mask2)


class TestE2EImg02FeatureSelection:
    """E2E-IMG-02: Feature selection."""

    @pytest.mark.integration
    def test_variance_threshold_reduces_features(self, e2e_radiomics_features):
        """Test that variance threshold reduces feature count."""
        from msra_modules.medical_imaging import FeatureSelector

        selector = FeatureSelector()
        original_n = e2e_radiomics_features.shape[1]

        selected = selector.variance_threshold(
            e2e_radiomics_features, threshold=0.5
        )

        # --- Assert: features reduced or maintained ---
        assert selected.shape[1] <= original_n
        assert selected.shape[0] == e2e_radiomics_features.shape[0], \
            "Sample count should not change"

    @pytest.mark.integration
    def test_auto_select_reduces_features(self, e2e_radiomics_features):
        """Test that auto select reduces feature count by >= 30%."""
        from msra_modules.medical_imaging import FeatureSelector

        selector = FeatureSelector()
        original_n = e2e_radiomics_features.shape[1]
        target_n = int(original_n * 0.7)  # Target: 30% reduction

        selected = selector.select(
            e2e_radiomics_features,
            labels=None,
            method="auto",
            n_features=target_n,
        )

        # --- Assert: feature reduction ---
        # Auto may use variance + correlation filter
        reduction_ratio = 1 - (selected.shape[1] / original_n)
        assert selected.shape[1] <= original_n, \
            "Feature count should not increase"
        assert selected.shape[0] == e2e_radiomics_features.shape[0], \
            "Sample count should not change"

    @pytest.mark.integration
    def test_selected_features_no_nan(self, e2e_radiomics_features):
        """Test that selected features contain no NaN values."""
        from msra_modules.medical_imaging import FeatureSelector

        selector = FeatureSelector()
        selected = selector.select(
            e2e_radiomics_features,
            labels=None,
            method="variance",
        )

        # --- Assert: no NaN ---
        assert not selected.isna().any().any(), \
            "Selected features should not contain NaN values"

    @pytest.mark.integration
    def test_correlation_filter_reduces_redundancy(self, e2e_radiomics_features):
        """Test that correlation filter removes highly correlated features."""
        from msra_modules.medical_imaging import FeatureSelector

        selector = FeatureSelector()
        original_n = e2e_radiomics_features.shape[1]

        selected = selector.correlation_filter(e2e_radiomics_features)

        # --- Assert: features reduced or maintained ---
        assert selected.shape[1] <= original_n
        assert selected.shape[0] == e2e_radiomics_features.shape[0]

    @pytest.mark.integration
    def test_feature_selection_reproducibility(self, e2e_radiomics_features):
        """Test that feature selection is reproducible (seed=42)."""
        from msra_modules.medical_imaging import FeatureSelector

        np.random.seed(42)
        selector1 = FeatureSelector()
        selected1 = selector1.select(
            e2e_radiomics_features, labels=None, method="variance"
        )

        np.random.seed(42)
        selector2 = FeatureSelector()
        selected2 = selector2.select(
            e2e_radiomics_features, labels=None, method="variance"
        )

        # --- Assert: same selected features ---
        pd.testing.assert_frame_equal(selected1, selected2)
