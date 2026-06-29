"""Tests for FHIR Server client."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from msra_modules.fhir_server import (
    FHIRServerClient,
    FHIRServerError,
)
from msra_modules.fhir.bundle import FHIRBundle


@pytest.fixture
def fhir_server():
    return FHIRServerClient(
        base_url="http://localhost:8080/fhir",
        bearer_token="test-token-123",
    )


@pytest.fixture
def search_bundle_json():
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "p1",
                    "gender": "male",
                    "birthDate": "1980-01-01",
                }
            }
        ],
    }


class TestInit:
    def test_init(self, fhir_server):
        assert fhir_server.base_url.endswith("/fhir")
        assert fhir_server.bearer_token == "test-token-123"

    def test_default_bearer_token_none(self):
        client = FHIRServerClient(base_url="http://x/fhir")
        assert client.bearer_token is None


class TestConnectivity:
    def test_ping_success(self, fhir_server):
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"resourceType": "CapabilityStatement"}
        mock_req.get.return_value = mock_resp
        fhir_server._get_requests = lambda: mock_req

        assert fhir_server.ping() is True

    def test_ping_failure(self, fhir_server):
        mock_req = MagicMock()
        mock_req.get.side_effect = ConnectionError("down")
        fhir_server._get_requests = lambda: mock_req

        assert fhir_server.ping() is False


class TestSearchPatients:
    def test_search_patients(self, fhir_server, search_bundle_json):
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = search_bundle_json
        mock_req.get.return_value = mock_resp
        fhir_server._get_requests = lambda: mock_req

        bundle = fhir_server.search_patients(name="Zhang")
        assert isinstance(bundle, FHIRBundle)
        assert len(bundle) == 1
        patients = bundle.get_patients()
        assert patients[0].id == "p1"

    def test_search_with_count(self, fhir_server):
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": 42,
            "entry": [],
        }
        mock_req.get.return_value = mock_resp
        fhir_server._get_requests = lambda: mock_req

        bundle = fhir_server.search_patients(count=10)
        assert bundle.total == 42

    def test_search_http_error_raises(self, fhir_server):
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "internal error"
        mock_req.get.return_value = mock_resp
        fhir_server._get_requests = lambda: mock_req

        with pytest.raises(FHIRServerError):
            fhir_server.search_patients()


class TestGetPatient:
    def test_get_patient(self, fhir_server):
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "resourceType": "Patient",
            "id": "p2",
            "gender": "female",
        }
        mock_req.get.return_value = mock_resp
        fhir_server._get_requests = lambda: mock_req

        patient = fhir_server.get_patient("p2")
        assert patient["id"] == "p2"
        assert patient["gender"] == "female"

    def test_get_patient_not_found(self, fhir_server):
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_req.get.return_value = mock_resp
        fhir_server._get_requests = lambda: mock_req

        assert fhir_server.get_patient("missing") is None


class TestSearchObservations:
    def test_search_observations(self, fhir_server):
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "resourceType": "Bundle",
            "type": "searchset",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": "o1",
                        "status": "final",
                    }
                }
            ],
        }
        mock_req.get.return_value = mock_resp
        fhir_server._get_requests = lambda: mock_req

        bundle = fhir_server.search_observations(patient_id="p1")
        assert len(bundle.get_observations()) == 1


class TestCreatePatient:
    def test_create_patient(self, fhir_server):
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {
            "resourceType": "Patient",
            "id": "new-001",
        }
        mock_req.post.return_value = mock_resp
        fhir_server._get_requests = lambda: mock_req

        patient_data = {
            "resourceType": "Patient",
            "gender": "male",
            "birthDate": "1990-01-01",
        }
        result = fhir_server.create_patient(patient_data)
        assert result["id"] == "new-001"

    def test_create_patient_conflict(self, fhir_server):
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 409
        mock_resp.text = "conflict"
        mock_req.post.return_value = mock_resp
        fhir_server._get_requests = lambda: mock_req

        with pytest.raises(FHIRServerError):
            fhir_server.create_patient({"resourceType": "Patient"})
