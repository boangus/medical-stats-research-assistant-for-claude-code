"""Tests for OMOP Condition Occurrence and Measurement tables."""

import sys
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from msra_modules.omop.exceptions import OMOPValidationError
from msra_modules.omop.clinical_tables import (
    OmopConditionOccurrence,
    OmopMeasurement,
    create_condition_from_fhir,
    create_measurement_from_fhir_obs,
)


class TestOmopConditionOccurrence:
    def test_create_condition(self):
        cond = OmopConditionOccurrence(
            condition_occurrence_id="cond-001",
            person_id="pat-001",
            condition_concept_id=201820,  # Diabetes mellitus
            condition_start_date="2024-01-15",
        )
        assert cond.condition_occurrence_id == "cond-001"
        assert cond.person_id == "pat-001"

    def test_missing_id_raises(self):
        with pytest.raises(OMOPValidationError):
            OmopConditionOccurrence(
                condition_occurrence_id="",
                person_id="p1",
                condition_concept_id=201820,
                condition_start_date="2024-01-15",
            )

    def test_missing_start_date_raises(self):
        with pytest.raises(OMOPValidationError):
            OmopConditionOccurrence(
                condition_occurrence_id="c1",
                person_id="p1",
                condition_concept_id=201820,
                condition_start_date=None,
            )

    def test_to_dict(self):
        cond = OmopConditionOccurrence(
            condition_occurrence_id="c1",
            person_id="p1",
            condition_concept_id=201820,
            condition_start_date="2024-01-15",
            condition_source_value="E11.9",
        )
        d = cond.to_dict()
        assert d["condition_concept_id"] == 201820
        assert d["condition_source_value"] == "E11.9"


class TestOmopMeasurement:
    def test_create_measurement(self):
        m = OmopMeasurement(
            measurement_id="meas-001",
            person_id="pat-001",
            measurement_concept_id=3023103,  # Glucose
            measurement_date="2024-01-15",
            value_as_number=5.5,
            unit_concept_id=8713,
        )
        assert m.measurement_id == "meas-001"
        assert m.value_as_number == 5.5

    def test_missing_id_raises(self):
        with pytest.raises(OMOPValidationError):
            OmopMeasurement(
                measurement_id="",
                person_id="p1",
                measurement_concept_id=3023103,
                measurement_date="2024-01-15",
            )

    def test_missing_date_raises(self):
        with pytest.raises(OMOPValidationError):
            OmopMeasurement(
                measurement_id="m1",
                person_id="p1",
                measurement_concept_id=3023103,
                measurement_date=None,
            )


class TestFhirConditionMapping:
    def test_create_condition_from_fhir(self):
        """从 FHIR Condition 资源创建 OMOP Condition。"""
        condition = {
            "resourceType": "Condition",
            "id": "cond-fhir-001",
            "clinicalStatus": {"code": "active"},
            "code": {
                "coding": [
                    {
                        "system": "http://hl7.org/fhir/sid/icd-10",
                        "code": "E11.9",
                        "display": "Type 2 diabetes mellitus",
                    }
                ]
            },
            "subject": {"reference": "Patient/pat-001"},
            "onsetDateTime": "2024-01-15",
        }
        cond = create_condition_from_fhir(condition)
        assert cond.condition_occurrence_id == "cond-fhir-001"
        assert cond.person_id == "pat-001"
        assert cond.condition_source_value == "E11.9"
        assert cond.condition_start_date == "2024-01-15"

    def test_no_icd10_code_maps_to_zero(self):
        condition = {
            "resourceType": "Condition",
            "id": "c1",
            "code": {"coding": [{"system": "http://snomed.info/sct", "code": "X"}]},
            "subject": {"reference": "Patient/p1"},
            "onsetDateTime": "2024-02-01",
        }
        cond = create_condition_from_fhir(condition)
        assert cond.condition_concept_id == 0


class TestFhirObservationToMeasurement:
    def test_create_measurement_from_observation(self):
        """从 FHIR Observation 资源创建 OMOP Measurement。"""
        obs = {
            "resourceType": "Observation",
            "id": "obs-001",
            "subject": {"reference": "Patient/pat-001"},
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "2339-0",
                        "display": "Glucose",
                    }
                ]
            },
            "valueQuantity": {"value": 5.5, "unit": "mmol/L"},
            "effectiveDateTime": "2024-01-15T10:30:00",
        }
        m = create_measurement_from_fhir_obs(obs)
        assert m.measurement_id == "obs-001"
        assert m.person_id == "pat-001"
        assert m.measurement_concept_id == 3023103
        assert m.value_as_number == 5.5
        assert m.measurement_date == "2024-01-15"
