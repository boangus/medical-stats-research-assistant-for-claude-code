"""FHIR Bundle 批处理解析器。

FHIR R4 Bundle 规范: https://hl7.org/fhir/R4/bundle.html

Bundle 是 FHIR 中用于聚合多个资源的容器，常见类型:
- searchset: 搜索结果
- batch / transaction: 批量操作
- document: 文档
- collection: 资源集合
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterator, List, Optional

from .exceptions import (
    FHIRBundleError,
    FHIRParseError,
    FHIRResourceNotFoundError,
)
from .observation import FHIRObservation
from .patient import FHIRPatient


class FHIRResourceType(str, Enum):
    """FHIR 资源类型枚举（仅列出医学数据互操作常用的）。"""

    PATIENT = "Patient"
    OBSERVATION = "Observation"
    CONDITION = "Condition"
    MEDICATION_REQUEST = "MedicationRequest"
    ENCOUNTER = "Encounter"
    PROCEDURE = "Procedure"
    ALLERGY_INTOLERANCE = "AllergyIntolerance"
    IMMUNIZATION = "Immunization"


@dataclass
class FHIRBundle:
    """FHIR Bundle 数据类。

    Attributes:
        bundle_type: Bundle 类型（searchset/batch/transaction/...）
        entries: Bundle entry 列表（每个 entry 含 resource + fullUrl）
        total: 搜索结果总数（仅 searchset，FHIR R4 标准字段，可选）
    """

    bundle_type: str
    entries: List[Dict[str, Any]] = field(default_factory=list)
    total: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FHIRBundle":
        """从 FHIR R4 Bundle dict 构造。

        Raises:
            FHIRParseError: 资源类型错误
            FHIRBundleError: 缺少 type 字段
        """
        if data.get("resourceType") != "Bundle":
            raise FHIRParseError(
                f"资源类型不是 Bundle: {data.get('resourceType', 'missing')}",
                resource_type=data.get("resourceType"),
            )

        bundle_type = data.get("type")
        if not bundle_type:
            raise FHIRBundleError("Bundle 缺少必需字段: type")

        entries = data.get("entry", [])
        if not isinstance(entries, list):
            raise FHIRBundleError(
                "Bundle.entry 不是数组", bundle_type=bundle_type
            )

        # 过滤掉没有 resource 的 entry
        valid_entries = [e for e in entries if isinstance(e, dict) and "resource" in e]

        # total 是 FHIR R4 searchset 的可选字段
        total = data.get("total")
        if total is not None and not isinstance(total, int):
            try:
                total = int(total)
            except (TypeError, ValueError):
                total = None

        return cls(bundle_type=bundle_type, entries=valid_entries, total=total)

    @classmethod
    def from_json(cls, json_str: str) -> "FHIRBundle":
        """从 JSON 字符串构造。"""
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise FHIRParseError(
                f"JSON 解析失败: {e}", resource_type="Bundle"
            ) from e
        return cls.from_dict(data)

    def get_patients(self) -> List[FHIRPatient]:
        """提取所有 Patient 资源，解析为 FHIRPatient 列表。"""
        patients: List[FHIRPatient] = []
        for entry in self.entries:
            resource = entry.get("resource", {})
            if resource.get("resourceType") == FHIRResourceType.PATIENT.value:
                patients.append(FHIRPatient.from_dict(resource))
        return patients

    def get_observations(self) -> List[FHIRObservation]:
        """提取所有 Observation 资源，解析为 FHIRObservation 列表。"""
        observations: List[FHIRObservation] = []
        for entry in self.entries:
            resource = entry.get("resource", {})
            if (
                resource.get("resourceType")
                == FHIRResourceType.OBSERVATION.value
            ):
                observations.append(FHIRObservation.from_dict(resource))
        return observations

    def get_resources_by_type(
        self, resource_type: FHIRResourceType | str
    ) -> List[Dict[str, Any]]:
        """按资源类型筛选原始 resource dict。

        Args:
            resource_type: FHIRResourceType 枚举或字符串

        Returns:
            匹配的原始 resource 字典列表
        """
        type_value = (
            resource_type.value
            if isinstance(resource_type, FHIRResourceType)
            else resource_type
        )
        return [
            entry["resource"]
            for entry in self.entries
            if entry.get("resource", {}).get("resourceType") == type_value
        ]

    def find_resource(
        self, resource_id: str, resource_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """按 ID（可选类型）查找资源。

        Raises:
            FHIRResourceNotFoundError: 资源不存在
        """
        for entry in self.entries:
            resource = entry.get("resource", {})
            if resource.get("id") != resource_id:
                continue
            if resource_type and resource.get("resourceType") != resource_type:
                continue
            return resource

        raise FHIRResourceNotFoundError(resource_id, resource_type)

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """迭代 entries。"""
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)
