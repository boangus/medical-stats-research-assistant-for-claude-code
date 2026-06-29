"""Tests for FHIR → OMOP cross-standard mapper."""

import sys
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from msra_modules.fhir import FHIRBundle
from msra_modules.omop.mapper import FhirToOmopMapper


@pytest.fixture
def clinical_bundle_json():
    """一个完整的临床场景 Bundle：1 个病人 + 1 次就诊 + 1 个病情 + 1 个测量。"""
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "pat-001",
                    "gender": "male",
                    "birthDate": "1980-05-15",
                }
            },
            {
                "resource": {
                    "resourceType": "Encounter",
                    "id": "enc-001",
                    "class": {"code": "IMP"},
                    "subject": {"reference": "Patient/pat-001"},
                    "period": {
                        "start": "2024-01-15",
                        "end": "2024-01-20",
                    },
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "cond-001",
                    "code": {
                        "coding": [
                            {
                                "system": "http://hl7.org/fhir/sid/icd-10",
                                "code": "E11.9",
                                "display": "T2DM",
                            }
                        ]
                    },
                    "subject": {"reference": "Patient/pat-001"},
                    "onsetDateTime": "2024-01-16",
                }
            },
            {
                "resource": {
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
                    "valueQuantity": {"value": 8.2, "unit": "mmol/L"},
                    "effectiveDateTime": "2024-01-17T09:00:00",
                }
            },
        ],
    }


class TestFhirToOmopMapper:
    def test_map_bundle(self, clinical_bundle_json):
        bundle = FHIRBundle.from_dict(clinical_bundle_json)
        mapper = FhirToOmopMapper()
        omop_data = mapper.map_bundle(bundle)

        # 应包含所有 4 个 OMOP 表
        assert "person" in omop_data
        assert "visit_occurrence" in omop_data
        assert "condition_occurrence" in omop_data
        assert "measurement" in omop_data

    def test_person_extracted(self, clinical_bundle_json):
        bundle = FHIRBundle.from_dict(clinical_bundle_json)
        mapper = FhirToOmopMapper()
        omop_data = mapper.map_bundle(bundle)

        assert len(omop_data["person"]) == 1
        assert omop_data["person"][0].person_id == "pat-001"
        assert omop_data["person"][0].year_of_birth == 1980
        assert omop_data["person"][0].gender_concept_id == 8507

    def test_visit_extracted(self, clinical_bundle_json):
        bundle = FHIRBundle.from_dict(clinical_bundle_json)
        mapper = FhirToOmopMapper()
        omop_data = mapper.map_bundle(bundle)

        assert len(omop_data["visit_occurrence"]) == 1
        visit = omop_data["visit_occurrence"][0]
        assert visit.visit_occurrence_id == "enc-001"
        assert visit.visit_concept_id == 9201  # Inpatient

    def test_condition_extracted(self, clinical_bundle_json):
        bundle = FHIRBundle.from_dict(clinical_bundle_json)
        mapper = FhirToOmopMapper()
        omop_data = mapper.map_bundle(bundle)

        assert len(omop_data["condition_occurrence"]) == 1
        cond = omop_data["condition_occurrence"][0]
        assert cond.condition_occurrence_id == "cond-001"
        assert cond.condition_source_value == "E11.9"
        assert cond.condition_concept_id == 201820  # Diabetes

    def test_measurement_extracted(self, clinical_bundle_json):
        bundle = FHIRBundle.from_dict(clinical_bundle_json)
        mapper = FhirToOmopMapper()
        omop_data = mapper.map_bundle(bundle)

        assert len(omop_data["measurement"]) == 1
        m = omop_data["measurement"][0]
        assert m.measurement_id == "obs-001"
        assert m.value_as_number == 8.2
        assert m.unit_concept_id == 8713  # mmol/L

    def test_empty_bundle(self):
        bundle = FHIRBundle.from_dict(
            {"resourceType": "Bundle", "type": "searchset", "entry": []}
        )
        mapper = FhirToOmopMapper()
        omop_data = mapper.map_bundle(bundle)
        for table in ["person", "visit_occurrence", "condition_occurrence", "measurement"]:
            assert omop_data[table] == []

    def test_bundle_with_only_patients(self):
        bundle = FHIRBundle.from_dict(
            {
                "resourceType": "Bundle",
                "type": "searchset",
                "entry": [
                    {
                        "resource": {
                            "resourceType": "Patient",
                            "id": "p1",
                            "gender": "female",
                            "birthDate": "1990-01-01",
                        }
                    }
                ],
            }
        )
        mapper = FhirToOmopMapper()
        omop_data = mapper.map_bundle(bundle)
        assert len(omop_data["person"]) == 1
        assert omop_data["visit_occurrence"] == []
        assert omop_data["condition_occurrence"] == []
        assert omop_data["measurement"] == []

    def test_get_summary(self, clinical_bundle_json):
        bundle = FHIRBundle.from_dict(clinical_bundle_json)
        mapper = FhirToOmopMapper()
        mapper.map_bundle(bundle)
        summary = mapper.get_summary()
        assert summary["patients"] == 1
        assert summary["visits"] == 1
        assert summary["conditions"] == 1
        assert summary["measurements"] == 1
