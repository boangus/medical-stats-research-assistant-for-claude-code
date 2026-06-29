"""Tests for FHIR exception hierarchy."""

import sys
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from msra_modules.fhir.exceptions import (
    FHIRBundleError,
    FHIRError,
    FHIRMappingError,
    FHIRParseError,
    FHIRResourceNotFoundError,
    FHIRValidationError,
)


class TestExceptionHierarchy:
    def test_all_inherit_from_fhir_error(self):
        for exc_class in [
            FHIRParseError,
            FHIRValidationError,
            FHIRResourceNotFoundError,
            FHIRBundleError,
            FHIRMappingError,
        ]:
            assert issubclass(exc_class, FHIRError)

    def test_fhir_error_is_exception(self):
        assert issubclass(FHIRError, Exception)


class TestFHIRParseError:
    def test_message_and_fields(self):
        err = FHIRParseError(
            "missing id", resource_type="Patient", field="id"
        )
        assert "missing id" in str(err)
        assert err.resource_type == "Patient"
        assert err.field == "id"


class TestFHIRValidationError:
    def test_message_and_fields(self):
        err = FHIRValidationError(
            "invalid gender", resource_type="Patient", field="gender"
        )
        assert err.field == "gender"
        assert err.resource_type == "Patient"


class TestFHIRResourceNotFoundError:
    def test_message_includes_id(self):
        err = FHIRResourceNotFoundError("pat-123", resource_type="Patient")
        assert "pat-123" in str(err)
        assert err.resource_id == "pat-123"
        assert err.resource_type == "Patient"


class TestFHIRBundleError:
    def test_bundle_type(self):
        err = FHIRBundleError("unsupported type", bundle_type="batch")
        assert err.bundle_type == "batch"
        assert "unsupported type" in str(err)


class TestFHIRMappingError:
    def test_source_and_target(self):
        err = FHIRMappingError(
            "no mapping",
            source_resource="Observation",
            target_table="measurement",
        )
        assert err.source_resource == "Observation"
        assert err.target_table == "measurement"
