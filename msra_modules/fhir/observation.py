"""FHIR Observation 资源解析器。

将 FHIR R4 Observation 资源解析为 Python 数据类，并提供 OMOP Measurement 表映射。

FHIR R4 Observation 规范: https://hl7.org/fhir/R4/observation.html
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .exceptions import FHIRParseError


# LOINC → OMOP CDM v5.4 Measurement Concept ID 映射（常用项）
# 完整映射应使用 OMOP Vocabulary
_LOINC_TO_MEASUREMENT_CONCEPT = {
    "2339-0": 3023103,   # Glucose [Mass/volume] in Blood
    "8480-6": 3012888,   # Systolic blood pressure
    "8462-4": 3035476,   # Diastolic blood pressure
    "85354-9": 0,        # Blood pressure panel（本身无单一值）
    "2951-2": 3013652,   # Sodium [Moles/volume] in Serum
    "3094-0": 3003710,   # Urea nitrogen [Mass/volume] in Blood
    "33914-3": 3024629,  # eGFR
    "4548-4": 3023504,   # HbA1c
    "2160-0": 3004410,   # Creatinine [Mass/volume] in Blood
    "33747-0": 3000963,  # Total cholesterol
}

# 常用 unit → OMOP Unit Concept ID（UCUM 编码）
# 完整映射应使用 OMOP Vocabulary
_UNIT_TO_CONCEPT = {
    "mmol/L": 8713,    # millimole per liter
    "mg/dL": 8840,      # milligram per deciliter
    "mmHg": 8580,       # millimeter of mercury
    "kg/m2": 9534,      # kilogram per square meter
    "%": 8554,          # percent
}


@dataclass
class ObservationComponent:
    """Observation 的组件（如血压的收缩压/舒张压）。"""

    loinc_code: Optional[str] = None
    display: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None


@dataclass
class FHIRObservation:
    """FHIR Observation 资源数据类。

    Attributes:
        id: 观察记录唯一 ID
        status: 状态（final/amended/corrected/...）
        patient_id: 关联的患者 ID
        loinc_code: LOINC 编码（实验室/生命体征标准）
        display: 人类可读名称
        value: 数值结果
        unit: 单位
        effective_date: 生效日期时间
        components: 多组件观测的子项列表
    """

    id: str
    status: Optional[str] = None
    patient_id: Optional[str] = None
    loinc_code: Optional[str] = None
    display: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    effective_date: Optional[str] = None
    components: List[ObservationComponent] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FHIRObservation":
        """从 FHIR R4 Observation dict 构造。"""
        if data.get("resourceType") != "Observation":
            raise FHIRParseError(
                f"资源类型不是 Observation: {data.get('resourceType', 'missing')}",
                resource_type=data.get("resourceType"),
            )

        obs_id = data.get("id")
        if not obs_id:
            raise FHIRParseError(
                "Observation 缺少必需字段: id",
                resource_type="Observation",
                field="id",
            )

        # 提取 patient_id（从 subject.reference 中提取 ID 部分）
        patient_id = None
        subject = data.get("subject", {})
        ref = subject.get("reference") if subject else None
        if ref and "/" in ref:
            patient_id = ref.split("/", 1)[1]

        # 提取 LOINC 编码（从 code.coding 中找 loinc.org 系统）
        loinc_code = None
        display = None
        code_block = data.get("code", {})
        for coding in code_block.get("coding", []):
            if (coding.get("system") or "").endswith("loinc.org"):
                loinc_code = coding.get("code")
                display = coding.get("display")
                break

        # 提取 valueQuantity
        value = None
        unit = None
        vq = data.get("valueQuantity", {})
        if vq:
            value = vq.get("value")
            unit = vq.get("unit") or vq.get("code")

        # 提取 components
        components: List[ObservationComponent] = []
        for comp in data.get("component", []):
            comp_loinc = None
            comp_display = None
            comp_code = comp.get("code", {})
            for coding in comp_code.get("coding", []):
                if (coding.get("system") or "").endswith("loinc.org"):
                    comp_loinc = coding.get("code")
                    comp_display = coding.get("display")
                    break
            comp_vq = comp.get("valueQuantity", {})
            comp_value = comp_vq.get("value") if comp_vq else None
            comp_unit = (
                (comp_vq.get("unit") or comp_vq.get("code"))
                if comp_vq
                else None
            )
            components.append(
                ObservationComponent(
                    loinc_code=comp_loinc,
                    display=comp_display,
                    value=comp_value,
                    unit=comp_unit,
                )
            )

        return cls(
            id=obs_id,
            status=data.get("status"),
            patient_id=patient_id,
            loinc_code=loinc_code,
            display=display,
            value=value,
            unit=unit,
            effective_date=data.get("effectiveDateTime"),
            components=components,
        )

    @classmethod
    def from_json(cls, json_str: str) -> "FHIRObservation":
        """从 JSON 字符串构造。"""
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise FHIRParseError(
                f"JSON 解析失败: {e}", resource_type="Observation"
            ) from e
        return cls.from_dict(data)

    def to_omop_measurement(self) -> Dict[str, Any]:
        """转换为单条 OMOP Measurement 记录（用于无组件的 Observation）。"""
        return {
            "observation_id": self.id,
            "person_id": self.patient_id,
            "measurement_concept_id": _LOINC_TO_MEASUREMENT_CONCEPT.get(
                self.loinc_code, 0
            ),
            "measurement_source_value": self.loinc_code,
            "value_as_number": self.value,
            "unit_concept_id": _UNIT_TO_CONCEPT.get(self.unit, 0)
            if self.unit
            else 0,
            "unit_source_value": self.unit,
            "measurement_date": self._extract_date(self.effective_date),
        }

    def to_omop_measurements(self) -> List[Dict[str, Any]]:
        """转换为多条 OMOP Measurement 记录（用于带组件的 Observation）。

        无组件时返回单元素列表。
        """
        if not self.components:
            return [self.to_omop_measurement()]

        measurements: List[Dict[str, Any]] = []
        for comp in self.components:
            measurements.append(
                {
                    "observation_id": self.id,
                    "person_id": self.patient_id,
                    "measurement_concept_id": _LOINC_TO_MEASUREMENT_CONCEPT.get(
                        comp.loinc_code, 0
                    ),
                    "measurement_source_value": comp.loinc_code,
                    "value_as_number": comp.value,
                    "unit_concept_id": _UNIT_TO_CONCEPT.get(comp.unit, 0)
                    if comp.unit
                    else 0,
                    "unit_source_value": comp.unit,
                    "measurement_date": self._extract_date(
                        self.effective_date
                    ),
                }
            )
        return measurements

    @staticmethod
    def _extract_date(dt: Optional[str]) -> Optional[str]:
        """从 ISO datetime 提取日期部分。"""
        if not dt:
            return None
        # 处理 "2024-01-15T10:30:00Z" → "2024-01-15"
        return dt.split("T", 1)[0] if "T" in dt else dt
