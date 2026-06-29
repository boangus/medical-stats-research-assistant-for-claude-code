"""Tests for FHIRPatient parser."""

import json
import sys
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from msra_modules.fhir import FHIRParseError
from msra_modules.fhir.patient import FHIRPatient


@pytest.fixture
def patient_json():
    return {
        "resourceType": "Patient",
        "id": "pat-001",
        "name": [
            {"family": "Zhang", "given": ["San"], "use": "official"}
        ],
        "gender": "male",
        "birthDate": "1980-05-15",
        "identifier": [
            {"system": "http://hospital.org/mrn", "value": "MRN-12345"}
        ],
    }


class TestFromDict:
    def test_parse_valid_patient(self, patient_json):
        patient = FHIRPatient.from_dict(patient_json)
        assert patient.id == "pat-001"
        assert patient.gender == "male"
        assert patient.birth_date == "1980-05-15"

    def test_extract_name(self, patient_json):
        patient = FHIRPatient.from_dict(patient_json)
        assert patient.family_name == "Zhang"
        assert patient.given_names == ["San"]

    def test_extract_identifier(self, patient_json):
        patient = FHIRPatient.from_dict(patient_json)
        assert patient.mrn == "MRN-12345"

    def test_missing_id_raises(self):
        with pytest.raises(FHIRParseError):
            FHIRPatient.from_dict({"resourceType": "Patient"})

    def test_wrong_resource_type_raises(self):
        with pytest.raises(FHIRParseError):
            FHIRPatient.from_dict({"resourceType": "Observation", "id": "x"})


class TestFromJson:
    def test_parse_json_string(self, patient_json):
        json_str = json.dumps(patient_json)
        patient = FHIRPatient.from_json(json_str)
        assert patient.id == "pat-001"

    def test_invalid_json_raises(self):
        with pytest.raises(FHIRParseError):
            FHIRPatient.from_json("not valid json")


class TestToOmopPerson:
    def test_to_person_dict(self, patient_json):
        patient = FHIRPatient.from_dict(patient_json)
        person = patient.to_omop_person()
        assert person["person_id"] == "pat-001"
        assert person["year_of_birth"] == 1980
        assert person["month_of_birth"] == 5
        assert person["gender_concept_id"] == 8507  # OMOP male concept


class TestOptionalFields:
    def test_patient_without_name(self):
        data = {
            "resourceType": "Patient",
            "id": "p1",
            "gender": "female",
            "birthDate": "1990-01-01",
        }
        patient = FHIRPatient.from_dict(data)
        assert patient.family_name is None
        assert patient.given_names == []

    def test_female_gender_maps_to_8532(self):
        data = {
            "resourceType": "Patient",
            "id": "p2",
            "gender": "female",
            "birthDate": "1990-01-01",
        }
        patient = FHIRPatient.from_dict(data)
        person = patient.to_omop_person()
        assert person["gender_concept_id"] == 8532
