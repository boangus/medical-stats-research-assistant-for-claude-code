"""Tests for OpenMRS connector.

使用 monkeypatch 替换 requests 调用，无需真实 OpenMRS 服务器。
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from msra_modules.ehr import EHRConnectionError, OpenMRSConnector, PatientQuery


@pytest.fixture
def openmrs_connector():
    return OpenMRSConnector(
        base_url="http://localhost:8080/openmrs/ws/rest/v1",
        username="admin",
        password="Admin123",
    )


@pytest.fixture
def openmrs_patient_response():
    """OpenMRS 原生 patient 响应（非 FHIR 格式）。"""
    return {
        "results": [
            {
                "uuid": "pat-001",
                "gender": "M",
                "birthdate": "1980-05-15",
                "personName": {
                    "familyName": "Zhang",
                    "givenName": "San",
                },
                "identifiers": [
                    {
                        "identifier": "MRN-12345",
                        "identifierType": {"display": "Medical Record Number"},
                    }
                ],
            }
        ]
    }


@pytest.fixture
def fhir_patient_json():
    """OpenMRS FHIR 模块返回的 Patient。"""
    return {
        "resourceType": "Patient",
        "id": "pat-fhir-001",
        "gender": "male",
        "birthDate": "1980-05-15",
        "name": [
            {"family": "Zhang", "given": ["San"], "use": "official"}
        ],
    }


class TestOpenMRSConnectorInit:
    def test_init(self, openmrs_connector):
        assert openmrs_connector.base_url.endswith("/rest/v1")
        assert openmrs_connector.username == "admin"

    def test_not_connected_by_default(self, openmrs_connector):
        assert not openmrs_connector.is_connected()


class TestConnect:
    def test_connect_success(self, openmrs_connector):
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"results": []}
        mock_req.get.return_value = mock_resp
        openmrs_connector._get_requests = lambda: mock_req  # type: ignore

        openmrs_connector.connect()
        assert openmrs_connector.is_connected()

    def test_connect_http_error_raises(self, openmrs_connector):
        mock_req = MagicMock()
        mock_req.get.side_effect = ConnectionError("network down")
        openmrs_connector._get_requests = lambda: mock_req  # type: ignore

        with pytest.raises(EHRConnectionError):
            openmrs_connector.connect()
        assert not openmrs_connector.is_connected()


class TestGetPatient:
    def test_get_patient_via_fhir_endpoint(self, openmrs_connector, fhir_patient_json):
        """OpenMRS FHIR 模块返回 FHIR R4 格式。"""
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"results": []}
        mock_req.get.return_value = mock_resp
        openmrs_connector._get_requests = lambda: mock_req  # type: ignore
        openmrs_connector.connect()

        # 第二次 get 返回 patient
        mock_req.get.return_value = MagicMock(
            status_code=200, json=lambda: fhir_patient_json
        )
        patient = openmrs_connector.get_patient("pat-fhir-001")
        assert patient["id"] == "pat-fhir-001"
        assert patient["resourceType"] == "Patient"

    def test_get_patient_not_found(self, openmrs_connector):
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"results": []}
        mock_req.get.return_value = mock_resp
        openmrs_connector._get_requests = lambda: mock_req  # type: ignore
        openmrs_connector.connect()

        mock_resp_404 = MagicMock()
        mock_resp_404.status_code = 404
        mock_req.get.return_value = mock_resp_404
        assert openmrs_connector.get_patient("missing") is None


class TestSearchPatients:
    def test_search_with_query(self, openmrs_connector, openmrs_patient_response):
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"results": []}
        mock_req.get.return_value = mock_resp
        openmrs_connector._get_requests = lambda: mock_req  # type: ignore
        openmrs_connector.connect()

        mock_req.get.return_value = MagicMock(
            status_code=200,
            json=lambda: openmrs_patient_response,
        )
        results = openmrs_connector.search_patients(PatientQuery())
        assert len(results) == 1
        assert results[0]["resourceType"] == "Patient"
        assert results[0]["id"] == "pat-001"
        assert results[0]["gender"] == "male"  # M → male 转换

    def test_count_patients(self, openmrs_connector):
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"results": []}
        mock_req.get.return_value = mock_resp
        openmrs_connector._get_requests = lambda: mock_req  # type: ignore
        openmrs_connector.connect()

        mock_req.get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"count": 42},
        )
        assert openmrs_connector.count_patients() == 42


class TestDisconnect:
    def test_disconnect(self, openmrs_connector):
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"results": []}
        mock_req.get.return_value = mock_resp
        openmrs_connector._get_requests = lambda: mock_req  # type: ignore
        openmrs_connector.connect()
        openmrs_connector.disconnect()
        assert not openmrs_connector.is_connected()
