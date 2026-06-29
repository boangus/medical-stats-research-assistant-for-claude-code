"""ICD-10-CM 编码引擎。

数据源: shared/terminology/data/icd10_cm.csv (本地字典)
依赖: pandas, rapidfuzz
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True)
class ICD10Concept:
    """ICD-10-CM 编码概念。

    Attributes:
        code: 完整编码, 如 "E11.9"
        short_description: 短描述
        long_description: 长描述
        category: 3位类别, 如 "E11"
        chapter: 章节名, 如 "Endocrine, Nutritional and Metabolic Diseases"
    """

    code: str
    short_description: str
    long_description: str
    category: str
    chapter: str
