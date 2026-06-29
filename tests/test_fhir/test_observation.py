"""Tests for FHIRObservation parser."""

import json
import sys
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from msra_modules.fhir import FHIRParseError
from msra_modules.fhir.observation import FHIRObservation


@pytest.fixture
def lab_observation_json():
    """实验室检查（带 LOINC 编码和数值）。"""
    return {
        "resourceType": "Observation",
        "id": "obs-lab-001",
        "status": "final",
        "subject": {"reference": "Patient/pat-001"},
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "2339-0",
                    "display": "Glucose [Mass/volume] in Blood",
                }
            ]
        },
        "valueQuantity": {
            "value": 5.5,
            "unit": "mmol/L",
            "system": "http://unitsofmeasure.org",
            "code": "mmol/L",
        },
        "effectiveDateTime": "2024-01-15T10:30:00Z",
    }


@pytest.fixture
def vital_signs_observation_json():
    """生命体征（带组件）。"""
    return {
        "resourceType": "Observation",
        "id": "obs-vs-001",
        "status": "final",
        "subject": {"reference": "Patient/pat-001"},
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "85354-9",
                    "display": "Blood pressure panel",
                }
            ]
        },
        "component": [
            {
                "code": {
                    "coding": [
                        {"system": "http://loinc.org", "code": "8480-6"}
                    ]
                },
                "valueQuantity": {"value": 120, "unit": "mmHg"},
            },
            {
                "code": {
                    "coding": [
                        {"system": "http://loinc.org", "code": "8462-4"}
                    ]
                },
                "valueQuantity": {"value": 80, "unit": "mmHg"},
            },
        ],
        "effectiveDateTime": "2024-01-15T10:30:00Z",
    }


class TestFromDict:
    def test_parse_lab_observation(self, lab_observation_json):
        obs = FHIRObservation.from_dict(lab_observation_json)
        assert obs.id == "obs-lab-001"
        assert obs.status == "final"
        assert obs.patient_id == "pat-001"

    def test_extract_loinc_code(self, lab_observation_json):
        obs = FHIRObservation.from_dict(lab_observation_json)
        assert obs.loinc_code == "2339-0"
        assert "Glucose" in obs.display

    def test_extract_value_quantity(self, lab_observation_json):
        obs = FHIRObservation.from_dict(lab_observation_json)
        assert obs.value == 5.5
        assert obs.unit == "mmol/L"

    def test_extract_effective_date(self, lab_observation_json):
        obs = FHIRObservation.from_dict(lab_observation_json)
        assert obs.effective_date == "2024-01-15T10:30:00Z"

    def test_missing_id_raises(self):
        with pytest.raises(FHIRParseError):
            FHIRObservation.from_dict(
                {"resourceType": "Observation", "status": "final"}
            )

    def test_wrong_resource_type_raises(self):
        with pytest.raises(FHIRParseError):
            FHIRObservation.from_dict({"resourceType": "Patient", "id": "x"})


class TestComponents:
    def test_extract_components(self, vital_signs_observation_json):
        obs = FHIRObservation.from_dict(vital_signs_observation_json)
        assert len(obs.components) == 2
        assert obs.components[0].loinc_code == "8480-6"
        assert obs.components[0].value == 120
        assert obs.components[1].loinc_code == "8462-4"

    def test_lab_observation_has_no_components(self, lab_observation_json):
        obs = FHIRObservation.from_dict(lab_observation_json)
        assert obs.components == []


class TestFromJson:
    def test_parse_json_string(self, lab_observation_json):
        json_str = json.dumps(lab_observation_json)
        obs = FHIRObservation.from_json(json_str)
        assert obs.id == "obs-lab-001"


class TestToOmopMeasurement:
    def test_to_measurement_dict(self, lab_observation_json):
        obs = FHIRObservation.from_dict(lab_observation_json)
        measurement = obs.to_omop_measurement()
        assert measurement["observation_id"] == "obs-lab-001"
        assert measurement["person_id"] == "pat-001"
        assert measurement["measurement_concept_id"] == 3023103  # Glucose mass/volume
        assert measurement["value_as_number"] == 5.5
        assert measurement["unit_concept_id"] is not None

    def test_component_to_measurement(self, vital_signs_observation_json):
        obs = FHIRObservation.from_dict(vital_signs_observation_json)
        measurements = obs.to_omop_measurements()
        # 一个带组件的 Observation 应生成多个 measurement
        assert len(measurements) == 2
        assert measurements[0]["measurement_concept_id"] == 3012888  # Systolic BP
        assert measurements[1]["measurement_concept_id"] == 3035476  # Diastolic BP
