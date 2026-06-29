"""Tests for FHIRBundle parser."""

import json
import sys
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from msra_modules.fhir import FHIRBundleError, FHIRParseError
from msra_modules.fhir.bundle import FHIRBundle, FHIRResourceType
from msra_modules.fhir.observation import FHIRObservation
from msra_modules.fhir.patient import FHIRPatient


@pytest.fixture
def bundle_json():
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [
            {
                "fullUrl": "http://fhir.server/Patient/pat-001",
                "resource": {
                    "resourceType": "Patient",
                    "id": "pat-001",
                    "gender": "male",
                    "birthDate": "1980-05-15",
                },
            },
            {
                "fullUrl": "http://fhir.server/Observation/obs-001",
                "resource": {
                    "resourceType": "Observation",
                    "id": "obs-001",
                    "status": "final",
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
                },
            },
        ],
    }


class TestFromDict:
    def test_parse_bundle(self, bundle_json):
        bundle = FHIRBundle.from_dict(bundle_json)
        assert bundle.bundle_type == "searchset"
        assert len(bundle.entries) == 2

    def test_wrong_resource_type_raises(self):
        with pytest.raises(FHIRParseError):
            FHIRBundle.from_dict({"resourceType": "Patient", "id": "x"})

    def test_missing_type_raises(self):
        with pytest.raises(FHIRBundleError):
            FHIRBundle.from_dict(
                {"resourceType": "Bundle", "entry": []}
            )

    def test_empty_bundle_allowed(self):
        bundle = FHIRBundle.from_dict(
            {"resourceType": "Bundle", "type": "searchset", "entry": []}
        )
        assert bundle.entries == []


class TestEntryAccess:
    def test_get_patients(self, bundle_json):
        bundle = FHIRBundle.from_dict(bundle_json)
        patients = bundle.get_patients()
        assert len(patients) == 1
        assert patients[0].id == "pat-001"

    def test_get_observations(self, bundle_json):
        bundle = FHIRBundle.from_dict(bundle_json)
        observations = bundle.get_observations()
        assert len(observations) == 1
        assert observations[0].id == "obs-001"

    def test_get_by_type(self, bundle_json):
        bundle = FHIRBundle.from_dict(bundle_json)
        resources = bundle.get_resources_by_type(FHIRResourceType.PATIENT)
        assert len(resources) == 1

    def test_get_by_type_string(self, bundle_json):
        bundle = FHIRBundle.from_dict(bundle_json)
        resources = bundle.get_resources_by_type("Patient")
        assert len(resources) == 1


class TestFindResource:
    def test_find_patient_by_id(self, bundle_json):
        bundle = FHIRBundle.from_dict(bundle_json)
        patient = bundle.find_resource("pat-001", "Patient")
        assert patient["id"] == "pat-001"

    def test_find_missing_raises(self, bundle_json):
        from msra_modules.fhir import FHIRResourceNotFoundError

        bundle = FHIRBundle.from_dict(bundle_json)
        with pytest.raises(FHIRResourceNotFoundError):
            bundle.find_resource("missing-id", "Patient")


class TestFromJson:
    def test_parse_json_string(self, bundle_json):
        json_str = json.dumps(bundle_json)
        bundle = FHIRBundle.from_json(json_str)
        assert len(bundle.entries) == 2

    def test_invalid_json_raises(self):
        with pytest.raises(FHIRParseError):
            FHIRBundle.from_json("not json")


class TestIteration:
    def test_iterate_entries(self, bundle_json):
        bundle = FHIRBundle.from_dict(bundle_json)
        types = [entry["resource"]["resourceType"] for entry in bundle]
        assert "Patient" in types
        assert "Observation" in types
