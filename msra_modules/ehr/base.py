"""EHR 连接器抽象基类与查询数据类。

定义统一接口，所有 EHR 连接器实现都返回 FHIR R4 格式的资源 dict。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .exceptions import EHRConnectionError


@dataclass
class PatientQuery:
    """患者查询参数（任意字段可空，空字段表示不参与过滤）。

    Attributes:
        gender: 性别过滤（male/female/other）
        family_name: 姓氏过滤
        given_name: 名字过滤
        birth_date_from: 出生日期下限（ISO 格式）
        birth_date_to: 出生日期上限
    """

    gender: Optional[str] = None
    family_name: Optional[str] = None
    given_name: Optional[str] = None
    birth_date_from: Optional[str] = None
    birth_date_to: Optional[str] = None


class EHRConnectorBase(ABC):
    """EHR 连接器抽象基类。

    所有具体连接器（OpenMRS、OpenEHR、自定义）必须实现以下方法：
        - connect() / disconnect() / is_connected()
        - get_patient(id) / get_observations(patient_id)
        - search_patients(query) / count_patients()

    所有返回的资源都遵循 FHIR R4 格式。
    """

    @abstractmethod
    def connect(self) -> None:
        """建立与 EHR 的连接。"""
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """断开连接。"""
        ...

    @abstractmethod
    def is_connected(self) -> bool:
        """返回当前是否已连接。"""
        ...

    @abstractmethod
    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """按 ID 获取单个 Patient 资源。

        Returns:
            FHIR R4 Patient dict，或 None（不存在时）
        """
        ...

    @abstractmethod
    def get_observations(
        self, patient_id: str
    ) -> List[Dict[str, Any]]:
        """获取指定患者的所有 Observation 资源。"""
        ...

    @abstractmethod
    def search_patients(
        self, query: PatientQuery
    ) -> List[Dict[str, Any]]:
        """按条件搜索 Patient 列表。"""
        ...

    @abstractmethod
    def count_patients(self) -> int:
        """返回 EHR 中的患者总数。"""
        ...

    def _ensure_connected(self) -> None:
        """内部工具：确保已连接，否则抛 EHRConnectionError。"""
        if not self.is_connected():
            raise EHRConnectionError(
                "EHR 未连接，请先调用 connect()"
            )
