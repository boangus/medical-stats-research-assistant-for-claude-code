"""Tests for terminology exceptions and abstract base."""

import sys
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from shared.terminology.exceptions import (
    TerminologyError,
    ICD10LookupError,
    ICD10DataNotFoundError,
)
from shared.terminology.base import TerminologyEngine


def test_terminology_error_is_exception():
    err = TerminologyError("msg")
    assert isinstance(err, Exception)
    assert str(err) == "msg"


def test_icd10_lookup_error_inherits_terminology():
    err = ICD10LookupError("bad code")
    assert isinstance(err, TerminologyError)


def test_icd10_data_not_found_error_inherits_terminology():
    err = ICD10DataNotFoundError("/path/to/missing.csv")
    assert isinstance(err, TerminologyError)
    assert "/path/to/missing.csv" in str(err)


def test_exception_hierarchy():
    assert issubclass(ICD10LookupError, TerminologyError)
    assert issubclass(ICD10DataNotFoundError, TerminologyError)


def test_terminology_engine_is_abstract():
    """TerminologyEngine 不能直接实例化"""
    with pytest.raises(TypeError):
        TerminologyEngine()


def test_terminology_engine_subclass_must_implement_methods():
    class ConcreteEngine(TerminologyEngine):
        def lookup(self, code): return None
        def validate(self, code): return False
        def search(self, description, limit=10): return []

    engine = ConcreteEngine()
    assert engine.lookup("X") is None
    assert engine.validate("X") is False
    assert engine.search("X") == []
