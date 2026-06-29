"""Terminology module — 临床术语编码引擎。

提供 ICD-10-CM 本地查询/验证/模糊匹配。
"""

from .base import TerminologyEngine
from .exceptions import (
    ICD10DataNotFoundError,
    ICD10LookupError,
    TerminologyError,
)
from .icd10_engine import ICD10Concept, ICD10Engine

__version__ = "0.1.0"
__all__ = [
    "TerminologyEngine",
    "ICD10Engine",
    "ICD10Concept",
    "TerminologyError",
    "ICD10LookupError",
    "ICD10DataNotFoundError",
]
