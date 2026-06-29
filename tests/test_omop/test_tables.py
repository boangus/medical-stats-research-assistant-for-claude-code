"""Tests for OMOP Person and Visit Occurrence tables."""

import sys
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from msra_modules.omop.exceptions import OMOPValidationError
from msra_modules.omop.tables import (
    OmopPerson,
    OmopVisitOccurrence,
    create_visit_from_encounter,
)


class TestOmopPerson:
    def test_create_person(self):
        person = OmopPerson(
            person_id="pat-001",
            year_of_birth=1980,
            month_of_birth=5,
            gender_concept_id=8507,
        )
        assert person.person_id == "pat-001"
        assert person.year_of_birth == 1980
        assert person.gender_concept_id == 8507

    def test_missing_person_id_raises(self):
        with pytest.raises(OMOPValidationError):
            OmopPerson(
                person_id="",
                year_of_birth=1980,
                gender_concept_id=8507,
            )

    def test_invalid_year_raises(self):
        with pytest.raises(OMOPValidationError):
            OmopPerson(
                person_id="p1",
                year_of_birth=1800,  # 太早
                gender_concept_id=8507,
            )

    def test_to_dict(self):
        person = OmopPerson(
            person_id="p1",
            year_of_birth=1990,
            month_of_birth=3,
            gender_concept_id=8532,
            gender_source_value="female",
        )
        d = person.to_dict()
        assert d["person_id"] == "p1"
        assert d["year_of_birth"] == 1990
        assert d["gender_concept_id"] == 8532


class TestOmopVisitOccurrence:
    def test_create_visit(self):
        visit = OmopVisitOccurrence(
            visit_occurrence_id="visit-001",
            person_id="pat-001",
            visit_concept_id=9201,  # Inpatient visit
            visit_start_date="2024-01-15",
            visit_type_concept_id=44818517,  # Visit derived from EHR
        )
        assert visit.visit_occurrence_id == "visit-001"
        assert visit.person_id == "pat-001"

    def test_missing_visit_id_raises(self):
        with pytest.raises(OMOPValidationError):
            OmopVisitOccurrence(
                visit_occurrence_id="",
                person_id="p1",
                visit_concept_id=9201,
                visit_start_date="2024-01-15",
                visit_type_concept_id=44818517,
            )

    def test_missing_start_date_raises(self):
        with pytest.raises(OMOPValidationError):
            OmopVisitOccurrence(
                visit_occurrence_id="v1",
                person_id="p1",
                visit_concept_id=9201,
                visit_start_date=None,
                visit_type_concept_id=44818517,
            )


class TestEncounterMapping:
    def test_create_visit_from_encounter(self):
        """从 FHIR Encounter 资源创建 Visit。"""
        encounter = {
            "resourceType": "Encounter",
            "id": "enc-001",
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "IMP",
                "display": "inpatient encounter",
            },
            "subject": {"reference": "Patient/pat-001"},
            "period": {
                "start": "2024-01-15",
                "end": "2024-01-20",
            },
        }
        visit = create_visit_from_encounter(encounter)
        assert visit.visit_occurrence_id == "enc-001"
        assert visit.person_id == "pat-001"
        assert visit.visit_concept_id == 9201  # IMP → Inpatient
        assert visit.visit_start_date == "2024-01-15"
        assert visit.visit_end_date == "2024-01-20"

    def test_unknown_class_maps_to_0(self):
        encounter = {
            "resourceType": "Encounter",
            "id": "enc-002",
            "class": {"code": "UNKNOWN"},
            "subject": {"reference": "Patient/p1"},
            "period": {"start": "2024-02-01"},
        }
        visit = create_visit_from_encounter(encounter)
        assert visit.visit_concept_id == 0
