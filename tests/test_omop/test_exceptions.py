"""Tests for OMOP exception hierarchy."""

import sys
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from msra_modules.omop.exceptions import (
    OMOPError,
    OMOPMappingError,
    OMOPValidationError,
)


class TestExceptionHierarchy:
    def test_all_inherit_from_omop_error(self):
        for exc_class in [OMOPValidationError, OMOPMappingError]:
            assert issubclass(exc_class, OMOPError)

    def test_omop_error_is_exception(self):
        assert issubclass(OMOPError, Exception)


class TestOMOPValidationError:
    def test_message_and_table(self):
        err = OMOPValidationError(
            "missing person_id", table_name="person", field="person_id"
        )
        assert "missing person_id" in str(err)
        assert err.table_name == "person"
        assert err.field == "person_id"


class TestOMOPMappingError:
    def test_source_and_target(self):
        err = OMOPMappingError(
            "no concept mapping",
            source_resource="Observation",
            target_table="measurement",
        )
        assert err.source_resource == "Observation"
        assert err.target_table == "measurement"
        assert err.table_name == "measurement"
