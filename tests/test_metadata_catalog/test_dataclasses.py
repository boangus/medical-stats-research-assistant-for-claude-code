"""Tests for metadata_catalog exceptions and data classes."""

import sys
from datetime import datetime
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from shared.metadata_catalog.exceptions import (
    MetadataCatalogError,
    VariableNotFoundError,
    VariableAlreadyExistsError,
    InvalidLineageError,
)
from shared.metadata_catalog.registry import MetadataEntry, VariableType


def test_metadata_catalog_error_is_exception():
    err = MetadataCatalogError("msg")
    assert isinstance(err, Exception)


def test_exception_hierarchy():
    assert issubclass(VariableNotFoundError, MetadataCatalogError)
    assert issubclass(VariableAlreadyExistsError, MetadataCatalogError)
    assert issubclass(InvalidLineageError, MetadataCatalogError)


def test_metadata_entry_creation():
    entry = MetadataEntry(
        variable="bmi",
        description="Body Mass Index",
        variable_type=VariableType.DERIVED,
        source_variables=["weight", "height"],
        unit="kg/m^2",
    )
    assert entry.variable == "bmi"
    assert entry.source_variables == ["weight", "height"]
    assert entry.unit == "kg/m^2"


def test_metadata_entry_default_timestamps():
    entry = MetadataEntry(
        variable="age",
        description="Patient age",
        variable_type=VariableType.DEMOGRAPHIC,
    )
    assert isinstance(entry.created_at, datetime)
    assert isinstance(entry.updated_at, datetime)


def test_variable_type_enum_values():
    assert VariableType.DEMOGRAPHIC
    assert VariableType.CLINICAL
    assert VariableType.LAB
    assert VariableType.DERIVED
    assert VariableType.OUTCOME


def test_metadata_entry_is_immutable():
    entry = MetadataEntry(
        variable="x",
        description="x",
        variable_type=VariableType.CLINICAL,
    )
    with pytest.raises(Exception):
        entry.variable = "y"


def test_metadata_entry_to_dict():
    entry = MetadataEntry(
        variable="bmi",
        description="BMI",
        variable_type=VariableType.DERIVED,
        source_variables=["weight", "height"],
        unit="kg/m^2",
    )
    d = entry.to_dict()
    assert d["variable"] == "bmi"
    assert d["variable_type"] == VariableType.DERIVED.value or d["variable_type"] == VariableType.DERIVED
    assert d["source_variables"] == ["weight", "height"]
