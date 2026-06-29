"""Terminology engine abstract base class.

所有术语编码引擎（ICD-10, SNOMED CT, LOINC, ...）实现此接口。
Sprint B 扩展新编码体系时复用此抽象。
"""

from abc import ABC, abstractmethod
from typing import Any, List


class TerminologyEngine(ABC):
    """术语编码引擎抽象基类。"""

    @abstractmethod
    def lookup(self, code: str) -> Any:
        """精确查询编码，返回概念对象；不存在返回 None。"""

    @abstractmethod
    def validate(self, code: str) -> bool:
        """验证编码是否合法存在。"""

    @abstractmethod
    def search(self, description: str, limit: int = 10) -> List[Any]:
        """按描述模糊匹配，返回 top-N 候选。"""
