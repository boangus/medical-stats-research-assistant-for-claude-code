"""FHIR Patient 资源解析器。

将 FHIR R4 Patient 资源解析为 Python 数据类，并提供 OMOP Person 表映射。

FHIR R4 Patient 规范: https://hl7.org/fhir/R4/patient.html
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .exceptions import FHIRParseError


# OMOP CDM v5.4 性别概念 ID（标准）
# 8507 = Male, 8532 = Female, 0 = Unknown
_GENDER_CONCEPT_MAP = {
    "male": 8507,
    "female": 8532,
    "other": 0,
    "unknown": 0,
    None: 0,
}


@dataclass
class FHIRPatient:
    """FHIR Patient 资源的数据类。

    Attributes:
        id: 患者唯一 ID
        family_name: 姓
        given_names: 名列表
        gender: 性别（male/female/other/unknown）
        birth_date: 出生日期（ISO 格式 YYYY-MM-DD）
        mrn: 医疗记录号（Medical Record Number）
    """

    id: str
    family_name: Optional[str] = None
    given_names: List[str] = field(default_factory=list)
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    mrn: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FHIRPatient":
        """从 FHIR R4 Patient dict 构造 FHIRPatient。

        Args:
            data: FHIR Patient 资源字典

        Returns:
            FHIRPatient 实例

        Raises:
            FHIRParseError: 资源类型错误或缺少必需字段
        """
        if data.get("resourceType") != "Patient":
            raise FHIRParseError(
                f"资源类型不是 Patient: {data.get('resourceType', 'missing')}",
                resource_type=data.get("resourceType"),
            )

        patient_id = data.get("id")
        if not patient_id:
            raise FHIRParseError(
                "Patient 缺少必需字段: id", resource_type="Patient", field="id"
            )

        # 提取姓名（取 use=official 的，否则取第一个）
        family_name = None
        given_names: List[str] = []
        names = data.get("name", [])
        if names:
            official = next(
                (n for n in names if n.get("use") == "official"), names[0]
            )
            family_name = official.get("family")
            given_names = list(official.get("given", []))

        # 提取 MRN（system 含 "mrn" 的 identifier）
        mrn = None
        for ident in data.get("identifier", []):
            system = (ident.get("system") or "").lower()
            if "mrn" in system:
                mrn = ident.get("value")
                break

        return cls(
            id=patient_id,
            family_name=family_name,
            given_names=given_names,
            gender=data.get("gender"),
            birth_date=data.get("birthDate"),
            mrn=mrn,
        )

    @classmethod
    def from_json(cls, json_str: str) -> "FHIRPatient":
        """从 JSON 字符串构造 FHIRPatient。

        Raises:
            FHIRParseError: JSON 解析失败
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise FHIRParseError(
                f"JSON 解析失败: {e}", resource_type="Patient"
            ) from e
        return cls.from_dict(data)

    def to_omop_person(self) -> Dict[str, Any]:
        """转换为 OMOP CDM Person 表记录。

        Returns:
            包含 person_id/year_of_birth/month_of_birth/gender_concept_id 的字典
        """
        year_of_birth = None
        month_of_birth = None
        if self.birth_date:
            parts = self.birth_date.split("-")
            if len(parts) >= 1 and parts[0]:
                year_of_birth = int(parts[0])
            if len(parts) >= 2 and parts[1]:
                month_of_birth = int(parts[1])

        return {
            "person_id": self.id,
            "year_of_birth": year_of_birth,
            "month_of_birth": month_of_birth,
            "gender_concept_id": _GENDER_CONCEPT_MAP.get(
                self.gender, 0
            ),
            "gender_source_value": self.gender,
        }
