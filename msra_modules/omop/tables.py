"""OMOP CDM v5.4 表结构数据类。

实现 Person、Visit Occurrence 等核心临床表的 Python dataclass，
提供字段校验和 FHIR Encounter → OMOP Visit 映射。

规范: https://ohdsi.github.io/CommonDataModel/
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional

from .exceptions import OMOPValidationError


# FHIR Encounter.class → OMOP Visit Concept ID 映射
# OMOP 标准概念:
#   9201 = Inpatient Visit
#   9202 = Outpatient Visit
#   9203 = Emergency Room Visit
#   0    = Unknown
_ENCOUNTER_CLASS_TO_VISIT_CONCEPT = {
    "IMP": 9201,   # Inpatient Encounter
    "AMB": 9202,   # Ambulatory / Outpatient
    "EMER": 9203,  # Emergency
    "ACUTE": 9201,
    "NONAC": 9201,
}

# Visit Type Concept（默认使用 Visit derived from EHR record）
_VISIT_TYPE_FROM_EHR = 44818517

# 允许的年份范围（CDM v5.4 推荐）
_MIN_YEAR = 1900
_MAX_YEAR = 2100


@dataclass
class OmopPerson:
    """OMOP CDM PERSON 表记录。

    Attributes:
        person_id: 患者 ID（来自源系统）
        year_of_birth: 出生年
        month_of_birth: 出生月（可选）
        day_of_birth: 出生日（可选）
        gender_concept_id: 性别概念 ID
        race_concept_id: 种族概念 ID（默认 0 = Unknown）
        ethnicity_concept_id: 民族概念 ID（默认 0 = Unknown）
        gender_source_value: 性别源值
    """

    person_id: str
    year_of_birth: Optional[int]
    gender_concept_id: int = 0
    month_of_birth: Optional[int] = None
    day_of_birth: Optional[int] = None
    race_concept_id: int = 0
    ethnicity_concept_id: int = 0
    gender_source_value: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.person_id:
            raise OMOPValidationError(
                "person_id 不能为空", table_name="person", field="person_id"
            )
        if self.year_of_birth is not None:
            if not isinstance(self.year_of_birth, int):
                raise OMOPValidationError(
                    "year_of_birth 必须是整数",
                    table_name="person",
                    field="year_of_birth",
                )
            if not (_MIN_YEAR <= self.year_of_birth <= _MAX_YEAR):
                raise OMOPValidationError(
                    f"year_of_birth 超出范围 [{_MIN_YEAR}, {_MAX_YEAR}]: "
                    f"{self.year_of_birth}",
                    table_name="person",
                    field="year_of_birth",
                )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OmopVisitOccurrence:
    """OMOP CDM VISIT_OCCURRENCE 表记录。

    Attributes:
        visit_occurrence_id: 就诊 ID
        person_id: 患者 ID
        visit_concept_id: 就诊类型概念 ID
        visit_start_date: 开始日期（YYYY-MM-DD）
        visit_end_date: 结束日期（可选）
        visit_type_concept_id: 类型来源概念 ID
    """

    visit_occurrence_id: str
    person_id: str
    visit_concept_id: int
    visit_start_date: str
    visit_end_date: Optional[str] = None
    visit_type_concept_id: int = _VISIT_TYPE_FROM_EHR

    def __post_init__(self) -> None:
        if not self.visit_occurrence_id:
            raise OMOPValidationError(
                "visit_occurrence_id 不能为空",
                table_name="visit_occurrence",
                field="visit_occurrence_id",
            )
        if not self.person_id:
            raise OMOPValidationError(
                "person_id 不能为空",
                table_name="visit_occurrence",
                field="person_id",
            )
        if not self.visit_start_date:
            raise OMOPValidationError(
                "visit_start_date 不能为空",
                table_name="visit_occurrence",
                field="visit_start_date",
            )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def create_visit_from_encounter(
    encounter: Dict[str, Any],
) -> OmopVisitOccurrence:
    """从 FHIR Encounter 资源创建 OmopVisitOccurrence。

    Args:
        encounter: FHIR R4 Encounter 资源字典

    Returns:
        OmopVisitOccurrence 实例

    Raises:
        OMOPValidationError: 必需字段缺失
    """
    visit_id = encounter.get("id", "")
    if not visit_id:
        raise OMOPValidationError(
            "Encounter 缺少 id",
            table_name="visit_occurrence",
            field="visit_occurrence_id",
        )

    # 提取 patient_id
    subject = encounter.get("subject", {})
    ref = subject.get("reference") if subject else None
    person_id = ref.split("/", 1)[1] if ref and "/" in ref else ""

    # 提取 visit_concept_id（从 Encounter.class.code）
    class_block = encounter.get("class", {})
    class_code = class_block.get("code") if class_block else None
    visit_concept_id = _ENCOUNTER_CLASS_TO_VISIT_CONCEPT.get(class_code, 0)

    # 提取日期
    period = encounter.get("period", {})
    start_date = period.get("start") if period else None
    end_date = period.get("end") if period else None

    return OmopVisitOccurrence(
        visit_occurrence_id=visit_id,
        person_id=person_id,
        visit_concept_id=visit_concept_id,
        visit_start_date=start_date,
        visit_end_date=end_date,
        visit_type_concept_id=_VISIT_TYPE_FROM_EHR,
    )
