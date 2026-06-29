"""Pytest fixtures for terminology tests."""

import sys
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


@pytest.fixture
def sample_data_path() -> Path:
    """样本 ICD-10-CM CSV 路径"""
    return (
        _project_root
        / "shared"
        / "terminology"
        / "data"
        / "icd10_cm_sample.csv"
    )
