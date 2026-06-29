"""FHIR → OMOP CDM 跨标准映射器。

将 FHIR Bundle 中的资源转换为 OMOP CDM v5.4 表记录。

支持映射:
- Patient       → PERSON
- Encounter     → VISIT_OCCURRENCE
- Condition     → CONDITION_OCCURRENCE
- Observation   → MEASUREMENT

Usage:
    bundle = FHIRBundle.from_dict(...)
    mapper = FhirToOmopMapper()
    omop_data = mapper.map_bundle(bundle)
    # omop_data = {"person": [...], "visit_occurrence": [...], ...}
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..fhir.bundle import FHIRBundle
from ..fhir.observation import FHIRObservation
from ..fhir.patient import FHIRPatient
from .clinical_tables import (
    OmopConditionOccurrence,
    OmopMeasurement,
    create_condition_from_fhir,
    create_measurement_from_fhir_obs,
)
from .exceptions import OMOPMappingError
from .tables import (
    OmopPerson,
    OmopVisitOccurrence,
    create_visit_from_encounter,
)


class FhirToOmopMapper:
    """FHIR → OMOP CDM 跨标准映射器。

    状态化设计：map_bundle 后可通过 get_summary 获取统计信息。
    """

    def __init__(self) -> None:
        self._persons: List[OmopPerson] = []
        self._visits: List[OmopVisitOccurrence] = []
        self._conditions: List[OmopConditionOccurrence] = []
        self._measurements: List[OmopMeasurement] = []

    def map_bundle(
        self, bundle: FHIRBundle
    ) -> Dict[str, List[Any]]:
        """将 FHIR Bundle 转换为 OMOP 表字典。

        Args:
            bundle: 已解析的 FHIRBundle

        Returns:
            {"person": [...], "visit_occurrence": [...],
             "condition_occurrence": [...], "measurement": [...]}
        """
        self._reset_state()

        for entry in bundle:
            resource = entry.get("resource", {})
            resource_type = resource.get("resourceType")

            if resource_type == "Patient":
                self._map_patient(resource)
            elif resource_type == "Encounter":
                self._map_encounter(resource)
            elif resource_type == "Condition":
                self._map_condition(resource)
            elif resource_type == "Observation":
                self._map_observation(resource)

        return {
            "person": self._persons,
            "visit_occurrence": self._visits,
            "condition_occurrence": self._conditions,
            "measurement": self._measurements,
        }

    def get_summary(self) -> Dict[str, int]:
        """获取最近一次 map_bundle 的统计信息。"""
        return {
            "patients": len(self._persons),
            "visits": len(self._visits),
            "conditions": len(self._conditions),
            "measurements": len(self._measurements),
        }

    def _reset_state(self) -> None:
        self._persons = []
        self._visits = []
        self._conditions = []
        self._measurements = []

    def _map_patient(self, resource: Dict[str, Any]) -> None:
        try:
            patient = FHIRPatient.from_dict(resource)
            person_dict = patient.to_omop_person()
            self._persons.append(
                OmopPerson(
                    person_id=person_dict["person_id"],
                    year_of_birth=person_dict["year_of_birth"],
                    month_of_birth=person_dict["month_of_birth"],
                    gender_concept_id=person_dict["gender_concept_id"],
                    gender_source_value=person_dict["gender_source_value"],
                )
            )
        except Exception as e:
            raise OMOPMappingError(
                f"Patient → Person 映射失败: {e}",
                source_resource="Patient",
                target_table="person",
            ) from e

    def _map_encounter(self, resource: Dict[str, Any]) -> None:
        try:
            visit = create_visit_from_encounter(resource)
            self._visits.append(visit)
        except Exception as e:
            raise OMOPMappingError(
                f"Encounter → Visit Occurrence 映射失败: {e}",
                source_resource="Encounter",
                target_table="visit_occurrence",
            ) from e

    def _map_condition(self, resource: Dict[str, Any]) -> None:
        try:
            cond = create_condition_from_fhir(resource)
            self._conditions.append(cond)
        except Exception as e:
            raise OMOPMappingError(
                f"Condition → Condition Occurrence 映射失败: {e}",
                source_resource="Condition",
                target_table="condition_occurrence",
            ) from e

    def _map_observation(self, resource: Dict[str, Any]) -> None:
        try:
            measurement = create_measurement_from_fhir_obs(resource)
            self._measurements.append(measurement)
        except Exception as e:
            raise OMOPMappingError(
                f"Observation → Measurement 映射失败: {e}",
                source_resource="Observation",
                target_table="measurement",
            ) from e
