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


import pandas as pd

from .base import TerminologyEngine
from .exceptions import ICD10DataNotFoundError, ICD10LookupError

_DEFAULT_DATA_PATH = Path(__file__).parent / "data" / "icd10_cm.csv"
_SAMPLE_DATA_PATH = Path(__file__).parent / "data" / "icd10_cm_sample.csv"


class ICD10Engine(TerminologyEngine):
    """ICD-10-CM 编码引擎。

    数据源: 本地 CSV 字典
    离线可用，无 API 依赖。

    Usage:
        engine = ICD10Engine()
        concept = engine.lookup("E11.9")
        matches = engine.search("diabetes", limit=5)
    """

    def __init__(self, data_path: Optional[Path] = None) -> None:
        if data_path is None:
            data_path = _DEFAULT_DATA_PATH if _DEFAULT_DATA_PATH.exists() else _SAMPLE_DATA_PATH

        if not data_path.exists():
            raise ICD10DataNotFoundError(str(data_path))

        self._data_path = data_path
        self._df = pd.read_csv(data_path, dtype=str)
        self._df = self._df.dropna(subset=["code"])
        self._code_index = {row["code"]: i for i, row in self._df.iterrows()}

    def lookup(self, code: str) -> Optional[ICD10Concept]:
        if not code:
            return None
        idx = self._code_index.get(code)
        if idx is None:
            return None
        row = self._df.iloc[idx]
        return ICD10Concept(
            code=row["code"],
            short_description=row.get("short_description", ""),
            long_description=row.get("long_description", ""),
            category=row.get("category", ""),
            chapter=row.get("chapter", ""),
        )

    def validate(self, code: str) -> bool:
        if not code:
            return False
        return code in self._code_index

    def search(self, description: str, limit: int = 10) -> List[ICD10Concept]:
        try:
            from rapidfuzz import fuzz, process
        except ImportError:
            return self._search_substring(description, limit)

        search_texts = (
            self._df["short_description"].fillna("") + " "
            + self._df["long_description"].fillna("")
        ).tolist()

        # 使用 partial_ratio 做子串匹配:
        # - 真实医学描述查询（如 "diabetes"）通常会得到 100 分
        # - 阈值设为 60 以过滤无关查询（如随机字符串通常 ≤ 50）
        results = process.extract(
            description.lower(),
            [t.lower() for t in search_texts],
            scorer=fuzz.partial_ratio,
            limit=limit,
        )

        concepts = []
        for match, score, idx in results:
            if score < 60:
                continue
            row = self._df.iloc[idx]
            concepts.append(ICD10Concept(
                code=row["code"],
                short_description=row.get("short_description", ""),
                long_description=row.get("long_description", ""),
                category=row.get("category", ""),
                chapter=row.get("chapter", ""),
            ))
        return concepts

    def _search_substring(self, description: str, limit: int) -> List[ICD10Concept]:
        """降级搜索: 简单子串匹配（rapidfuzz 不可用时）。"""
        desc_lower = description.lower()
        concepts = []
        for _, row in self._df.iterrows():
            text = (
                str(row.get("short_description", "")).lower()
                + " "
                + str(row.get("long_description", "")).lower()
            )
            if desc_lower in text:
                concepts.append(ICD10Concept(
                    code=row["code"],
                    short_description=row.get("short_description", ""),
                    long_description=row.get("long_description", ""),
                    category=row.get("category", ""),
                    chapter=row.get("chapter", ""),
                ))
                if len(concepts) >= limit:
                    break
        return concepts

    def map_to_chapter(self, code: str) -> str:
        concept = self.lookup(code)
        if concept is None:
            raise ICD10LookupError(f"编码 {code} 不存在于字典中")
        return concept.chapter

    def list_chapters(self) -> List[str]:
        return sorted(self._df["chapter"].dropna().unique().tolist())
