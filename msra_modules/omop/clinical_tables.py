"""OMOP CDM v5.4 临床事件表（Condition Occurrence, Measurement）。

规范: https://ohdsi.github.io/CommonDataModel/
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from .exceptions import OMOPValidationError


# ICD-10 → OMOP Condition Concept ID 映射（常用疾病）
# 完整映射应使用 OMOP Vocabulary 中的 SOURCE_TO_CONCEPT_MAP 表
_ICD10_TO_CONDITION_CONCEPT = {
    "E11.9": 201820,   # Type 2 diabetes mellitus without complications
    "E11.65": 201820,  # Type 2 diabetes with hyperglycemia
    "I10": 320128,    # Essential hypertension
    "I21.3": 4299892, # STEMI
    "I50.9": 316139,  # Heart failure
    "J45.909": 256456, # Asthma
    "N18.6": 46271031, # End stage renal disease
    "C50.9": 4113849, # Breast cancer
    "C61": 4168488,   # Prostate cancer
    "F32.9": 4268206, # Major depressive disorder
    "F41.1": 440383,  # Generalized anxiety disorder
    "G40.909": 375031, # Epilepsy
    "M17.9": 81390,   # Knee osteoarthritis
}

# LOINC → OMOP Measurement Concept ID
# 完整映射应使用 OMOP Vocabulary
_LOINC_TO_MEASUREMENT_CONCEPT = {
    "2339-0": 3023103,  # Glucose
    "8480-6": 3012888,  # Systolic BP
    "8462-4": 3035476,  # Diastolic BP
    "2951-2": 3013652,  # Sodium
    "3094-0": 3003710,  # BUN
    "33914-3": 3024629,  # eGFR
    "4548-4": 3023504,  # HbA1c
    "2160-0": 3004410,  # Creatinine
    "33747-0": 3000963,  # Total cholesterol
}

# 常用 unit → OMOP Unit Concept ID
_UNIT_TO_CONCEPT = {
    "mmol/L": 8713,
    "mg/dL": 8840,
    "mmHg": 8580,
    "kg/m2": 9534,
    "%": 8554,
}

# 默认 Condition Type Concept（Source = EHR record）
_CONDITION_TYPE_FROM_EHR = 32879

# 默认 Measurement Type Concept
_MEASUREMENT_TYPE_FROM_EHR = 5001


@dataclass
class OmopConditionOccurrence:
    """OMOP CDM CONDITION_OCCURRENCE 表记录。

    Attributes:
        condition_occurrence_id: 病情记录 ID
        person_id: 患者 ID
        condition_concept_id: 病情概念 ID
        condition_start_date: 起始日期
        condition_end_date: 结束日期（可选）
        condition_type_concept_id: 类型概念 ID
        condition_source_value: 源编码（如 ICD-10）
    """

    condition_occurrence_id: str
    person_id: str
    condition_concept_id: int
    condition_start_date: str
    condition_end_date: Optional[str] = None
    condition_type_concept_id: int = _CONDITION_TYPE_FROM_EHR
    condition_source_value: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.condition_occurrence_id:
            raise OMOPValidationError(
                "condition_occurrence_id 不能为空",
                table_name="condition_occurrence",
                field="condition_occurrence_id",
            )
        if not self.person_id:
            raise OMOPValidationError(
                "person_id 不能为空",
                table_name="condition_occurrence",
                field="person_id",
            )
        if not self.condition_start_date:
            raise OMOPValidationError(
                "condition_start_date 不能为空",
                table_name="condition_occurrence",
                field="condition_start_date",
            )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OmopMeasurement:
    """OMOP CDM MEASUREMENT 表记录。

    Attributes:
        measurement_id: 测量记录 ID
        person_id: 患者 ID
        measurement_concept_id: 测量概念 ID（来自 LOINC）
        measurement_date: 测量日期
        value_as_number: 数值结果
        unit_concept_id: 单位概念 ID
        measurement_type_concept_id: 类型概念 ID
        measurement_source_value: 源编码（如 LOINC code）
        unit_source_value: 单位源值
    """

    measurement_id: str
    person_id: str
    measurement_concept_id: int
    measurement_date: str
    value_as_number: Optional[float] = None
    unit_concept_id: int = 0
    measurement_type_concept_id: int = _MEASUREMENT_TYPE_FROM_EHR
    measurement_source_value: Optional[str] = None
    unit_source_value: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.measurement_id:
            raise OMOPValidationError(
                "measurement_id 不能为空",
                table_name="measurement",
                field="measurement_id",
            )
        if not self.person_id:
            raise OMOPValidationError(
                "person_id 不能为空",
                table_name="measurement",
                field="person_id",
            )
        if not self.measurement_date:
            raise OMOPValidationError(
                "measurement_date 不能为空",
                table_name="measurement",
                field="measurement_date",
            )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def create_condition_from_fhir(
    condition: Dict[str, Any],
) -> OmopConditionOccurrence:
    """从 FHIR Condition 资源创建 OMOP Condition Occurrence。

    Args:
        condition: FHIR R4 Condition 资源字典

    Returns:
        OmopConditionOccurrence 实例

    Raises:
        OMOPValidationError: 必需字段缺失
    """
    cond_id = condition.get("id", "")
    if not cond_id:
        raise OMOPValidationError(
            "Condition 缺少 id",
            table_name="condition_occurrence",
            field="condition_occurrence_id",
        )

    # 提取 patient_id
    subject = condition.get("subject", {})
    ref = subject.get("reference") if subject else None
    person_id = ref.split("/", 1)[1] if ref and "/" in ref else ""

    # 提取 ICD-10 编码并映射
    icd10_code = None
    condition_concept_id = 0
    code_block = condition.get("code", {})
    for coding in code_block.get("coding", []):
        system = coding.get("system", "")
        code = coding.get("code")
        if "icd-10" in system.lower() or "icd10" in system.lower():
            icd10_code = code
            condition_concept_id = _ICD10_TO_CONDITION_CONCEPT.get(code, 0)
            break

    # 提取日期
    start_date = (
        condition.get("onsetDateTime")
        or condition.get("recordedDate")
    )
    end_date = condition.get("abatementDateTime")

    return OmopConditionOccurrence(
        condition_occurrence_id=cond_id,
        person_id=person_id,
        condition_concept_id=condition_concept_id,
        condition_start_date=start_date,
        condition_end_date=end_date,
        condition_source_value=icd10_code,
    )


def create_measurement_from_fhir_obs(
    observation: Dict[str, Any],
) -> OmopMeasurement:
    """从 FHIR Observation 资源创建 OMOP Measurement。

    Args:
        observation: FHIR R4 Observation 资源字典

    Returns:
        OmopMeasurement 实例

    Raises:
        OMOPValidationError: 必需字段缺失
    """
    obs_id = observation.get("id", "")
    if not obs_id:
        raise OMOPValidationError(
            "Observation 缺少 id",
            table_name="measurement",
            field="measurement_id",
        )

    # 提取 patient_id
    subject = observation.get("subject", {})
    ref = subject.get("reference") if subject else None
    person_id = ref.split("/", 1)[1] if ref and "/" in ref else ""

    # 提取 LOINC 编码并映射
    loinc_code = None
    measurement_concept_id = 0
    code_block = observation.get("code", {})
    for coding in code_block.get("coding", []):
        if (coding.get("system") or "").endswith("loinc.org"):
            loinc_code = coding.get("code")
            measurement_concept_id = _LOINC_TO_MEASUREMENT_CONCEPT.get(
                loinc_code, 0
            )
            break

    # 提取 valueQuantity
    vq = observation.get("valueQuantity", {})
    value = vq.get("value") if vq else None
    unit = (vq.get("unit") or vq.get("code")) if vq else None
    unit_concept_id = _UNIT_TO_CONCEPT.get(unit, 0) if unit else 0

    # 提取日期（datetime → date）
    effective_dt = observation.get("effectiveDateTime")
    measurement_date = effective_dt.split("T", 1)[0] if effective_dt and "T" in effective_dt else effective_dt

    return OmopMeasurement(
        measurement_id=obs_id,
        person_id=person_id,
        measurement_concept_id=measurement_concept_id,
        measurement_date=measurement_date,
        value_as_number=value,
        unit_concept_id=unit_concept_id,
        measurement_source_value=loinc_code,
        unit_source_value=unit,
    )
