"""Tests for OpenEHR connector."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from msra_modules.ehr import EHRConnectionError, OpenEHRConnector, PatientQuery


@pytest.fixture
def openehr_connector():
    return OpenEHRConnector(
        base_url="http://localhost:8080/ehrbase/rest/openehr/v1",
        username="ehrbase",
        password="ehrbase",
    )


@pytest.fixture
def openehr_ehr_response():
    """OpenEHR EHR 资源响应。"""
    return {
        "ehr_id": "ehr-001",
        "ehr_status": {
            "subject": {
                "external_ref": {
                    "id": "patient-001",
                    "namespace": "demo",
                },
                "party_additional_info": [
                    {"name": "gender", "value": "male"},
                    {"name": "birthdate", "value": "1980-05-15"},
                ],
            }
        }
    }


@pytest.fixture
def openehr_composition_response():
    """OpenEHR composition（包含观察数据）。"""
    return {
        "composition": {
            "uid": "comp-001::local::1",
            "context": {
                "start_time": {"value": "2024-01-15T10:30:00"},
            },
            "content": [
                {
                    "@type": "OBSERVATION",
                    "name": {"value": "Glucose"},
                    "data": {
                        "events": [
                            {
                                "data": {
                                    "items": [
                                        {
                                            "name": {"value": "Glucose"},
                                            "value": {
                                                "magnitude": 5.5,
                                                "units": "mmol/L",
                                            },
                                        }
                                    ]
                                }
                            }
                        ]
                    },
                }
            ],
        }
    }


class TestOpenEHRConnectorInit:
    def test_init(self, openehr_connector):
        assert openehr_connector.username == "ehrbase"

    def test_not_connected_by_default(self, openehr_connector):
        assert not openehr_connector.is_connected()


class TestConnect:
    def test_connect_success(self, openehr_connector):
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {}
        mock_req.get.return_value = mock_resp
        openehr_connector._get_requests = lambda: mock_req

        openehr_connector.connect()
        assert openehr_connector.is_connected()

    def test_connect_failure_raises(self, openehr_connector):
        mock_req = MagicMock()
        mock_req.get.side_effect = ConnectionError("network error")
        openehr_connector._get_requests = lambda: mock_req

        with pytest.raises(EHRConnectionError):
            openehr_connector.connect()


class TestGetPatient:
    def test_get_patient_from_ehr(self, openehr_connector, openehr_ehr_response):
        """通过 ehr_id 查询 EHR，提取 subject info 转换为 FHIR Patient。"""
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {}
        mock_req.get.return_value = mock_resp
        openehr_connector._get_requests = lambda: mock_req
        openehr_connector.connect()

        # EHR 查询返回
        ehr_resp = MagicMock()
        ehr_resp.status_code = 200
        ehr_resp.json.return_value = openehr_ehr_response
        mock_req.get.return_value = ehr_resp
        patient = openehr_connector.get_patient("patient-001")
        assert patient is not None
        assert patient["resourceType"] == "Patient"
        assert patient["id"] == "patient-001"
        assert patient["gender"] == "male"
        assert patient["birthDate"] == "1980-05-15"

    def test_get_missing_patient_returns_none(self, openehr_connector):
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {}
        mock_req.get.return_value = mock_resp
        openehr_connector._get_requests = lambda: mock_req
        openehr_connector.connect()

        mock_req.get.return_value = MagicMock(status_code=404)
        assert openehr_connector.get_patient("missing") is None


class TestGetObservations:
    def test_get_observations_from_compositions(
        self, openehr_connector, openehr_composition_response
    ):
        """从 OpenEHR composition 提取观察数据并转为 FHIR Observation。"""
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {}
        mock_req.get.return_value = mock_resp
        openehr_connector._get_requests = lambda: mock_req
        openehr_connector.connect()

        # 第一次 GET（ehr 查询）返回带 ehr_id 的响应
        ehr_resp = MagicMock()
        ehr_resp.status_code = 200
        ehr_resp.json.return_value = {"ehr_id": "ehr-001"}
        # 第二次 GET（composition 查询）返回 compositions
        comp_resp = MagicMock()
        comp_resp.status_code = 200
        comp_resp.json.return_value = {
            "compositions": [openehr_composition_response["composition"]]
        }
        mock_req.get.side_effect = [ehr_resp, comp_resp]
        observations = openehr_connector.get_observations("patient-001")
        assert len(observations) >= 1
        assert observations[0]["resourceType"] == "Observation"


class TestCountPatients:
    def test_count(self, openehr_connector):
        mock_req = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {}
        mock_req.get.return_value = mock_resp
        openehr_connector._get_requests = lambda: mock_req
        openehr_connector.connect()

        # 简化：查询 EHR 列表并计数
        mock_req.get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"ehr": [{"ehr_id": "e1"}, {"ehr_id": "e2"}]},
        )
        assert openehr_connector.count_patients() == 2
