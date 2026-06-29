"""Tests for EHR connector abstraction."""

import sys
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from msra_modules.ehr import (
    EHRConnectorBase,
    EHRConnectionError,
    MockEHRConnector,
    PatientQuery,
)


@pytest.fixture
def mock_connector():
    return MockEHRConnector(
        patients=[
            {"resourceType": "Patient", "id": "p1", "gender": "male"},
            {"resourceType": "Patient", "id": "p2", "gender": "female"},
        ],
        observations=[
            {
                "resourceType": "Observation",
                "id": "obs-001",
                "subject": {"reference": "Patient/p1"},
                "status": "final",
            }
        ],
    )


class TestMockEHRConnector:
    def test_inherits_base(self):
        assert issubclass(MockEHRConnector, EHRConnectorBase)

    def test_connect(self, mock_connector):
        mock_connector.connect()
        assert mock_connector.is_connected()

    def test_disconnect(self, mock_connector):
        mock_connector.connect()
        mock_connector.disconnect()
        assert not mock_connector.is_connected()

    def test_get_patient_before_connect_raises(self, mock_connector):
        with pytest.raises(EHRConnectionError):
            mock_connector.get_patient("p1")

    def test_get_patient(self, mock_connector):
        mock_connector.connect()
        patient = mock_connector.get_patient("p1")
        assert patient["id"] == "p1"
        assert patient["gender"] == "male"

    def test_get_missing_patient_returns_none(self, mock_connector):
        mock_connector.connect()
        assert mock_connector.get_patient("missing") is None

    def test_get_observations_for_patient(self, mock_connector):
        mock_connector.connect()
        observations = mock_connector.get_observations("p1")
        assert len(observations) == 1
        assert observations[0]["id"] == "obs-001"

    def test_search_patients(self, mock_connector):
        mock_connector.connect()
        query = PatientQuery(gender="female")
        patients = mock_connector.search_patients(query)
        assert len(patients) == 1
        assert patients[0]["id"] == "p2"

    def test_search_patients_no_filter(self, mock_connector):
        mock_connector.connect()
        query = PatientQuery()
        patients = mock_connector.search_patients(query)
        assert len(patients) == 2

    def test_count_patients(self, mock_connector):
        mock_connector.connect()
        assert mock_connector.count_patients() == 2


class TestPatientQuery:
    def test_empty_query(self):
        query = PatientQuery()
        assert query.gender is None
        assert query.family_name is None

    def test_with_filters(self):
        query = PatientQuery(gender="male", family_name="Zhang")
        assert query.gender == "male"
        assert query.family_name == "Zhang"
