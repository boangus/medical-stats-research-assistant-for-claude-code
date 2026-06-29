"""Tests for ICD10Concept dataclass."""

import sys
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from shared.terminology.icd10_engine import ICD10Concept


def test_icd10_concept_creation():
    concept = ICD10Concept(
        code="E11.9",
        short_description="Type 2 diabetes mellitus without complications",
        long_description="Type 2 diabetes mellitus without complications",
        category="E11",
        chapter="Endocrine Nutritional and Metabolic Diseases",
    )
    assert concept.code == "E11.9"
    assert concept.category == "E11"
    assert "Endocrine" in concept.chapter


def test_icd10_concept_equality():
    c1 = ICD10Concept("I10", "htn", "htn", "I10", "Circulatory")
    c2 = ICD10Concept("I10", "htn", "htn", "I10", "Circulatory")
    assert c1 == c2


def test_icd10_concept_repr():
    concept = ICD10Concept("A00.0", "cholera", "cholera", "A00", "Infectious")
    repr_str = repr(concept)
    assert "A00.0" in repr_str
    assert "cholera" in repr_str
