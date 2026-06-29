"""Tests for batch ETL pipeline."""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from msra_modules.ehr import MockEHRConnector
from msra_modules.etl import (
    ETLResult,
    ETLStageError,
    ETLStats,
    ETLWorkflow,
)


@pytest.fixture
def mock_ehr():
    """构造 Mock EHR：2 病人 + 2 观察。"""
    return MockEHRConnector(
        patients=[
            {
                "resourceType": "Patient",
                "id": "p1",
                "gender": "male",
                "birthDate": "1980-01-01",
            },
            {
                "resourceType": "Patient",
                "id": "p2",
                "gender": "female",
                "birthDate": "1990-02-02",
            },
        ],
        observations=[
            {
                "resourceType": "Observation",
                "id": "o1",
                "subject": {"reference": "Patient/p1"},
                "status": "final",
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
                "effectiveDateTime": "2024-01-15T10:00:00",
            },
            {
                "resourceType": "Observation",
                "id": "o2",
                "subject": {"reference": "Patient/p2"},
                "status": "final",
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "8480-6",
                            "display": "Systolic BP",
                        }
                    ]
                },
                "valueQuantity": {"value": 120, "unit": "mmHg"},
                "effectiveDateTime": "2024-01-16T10:00:00",
            },
        ],
    )


class TestETLStats:
    def test_create_stats(self):
        stats = ETLStats()
        assert stats.patients_extracted == 0
        assert stats.observations_extracted == 0
        assert stats.omop_records_created == 0

    def test_increment(self):
        stats = ETLStats()
        stats.patients_extracted = 5
        stats.observations_extracted = 10
        stats.omop_records_created = 15
        assert stats.patients_extracted == 5


class TestETLWorkflow:
    def test_init(self, mock_ehr):
        wf = ETLWorkflow(ehr_connector=mock_ehr)
        assert wf is not None

    def test_extract_patients(self, mock_ehr):
        wf = ETLWorkflow(ehr_connector=mock_ehr)
        mock_ehr.connect()
        patients = wf.extract_patients()
        assert len(patients) == 2

    def test_extract_all(self, mock_ehr):
        wf = ETLWorkflow(ehr_connector=mock_ehr)
        mock_ehr.connect()
        wf.extract_all()
        assert wf.stats.patients_extracted == 2
        assert wf.stats.observations_extracted == 2

    def test_transform_to_omop(self, mock_ehr):
        wf = ETLWorkflow(ehr_connector=mock_ehr)
        mock_ehr.connect()
        wf.extract_all()
        wf.transform_to_omop()
        assert wf.stats.omop_records_created >= 2  # 至少 2 个 measurement

    def test_transform_creates_person_records(self, mock_ehr):
        wf = ETLWorkflow(ehr_connector=mock_ehr)
        mock_ehr.connect()
        wf.extract_all()
        wf.transform_to_omop()
        assert len(wf.omop_data["person"]) == 2

    def test_load_to_csv(self, mock_ehr, tmp_path):
        wf = ETLWorkflow(ehr_connector=mock_ehr)
        mock_ehr.connect()
        wf.extract_all()
        wf.transform_to_omop()
        output_dir = wf.load_to_csv(output_dir=str(tmp_path))

        # 应生成 4 个 CSV 文件
        csv_files = list(Path(output_dir).glob("*.csv"))
        assert len(csv_files) >= 4
        # 检查 person.csv 存在
        assert (Path(output_dir) / "person.csv").exists()

    def test_run_full_pipeline(self, mock_ehr, tmp_path):
        """完整 ETL 流程：extract → transform → load。"""
        wf = ETLWorkflow(ehr_connector=mock_ehr)
        mock_ehr.connect()
        result = wf.run(output_dir=str(tmp_path))

        assert isinstance(result, ETLResult)
        assert result.success
        assert result.stats.patients_extracted == 2
        assert result.output_dir.exists()

    def test_run_with_no_data(self, tmp_path):
        """空 EHR 也应正常完成。"""
        empty_ehr = MockEHRConnector()
        wf = ETLWorkflow(ehr_connector=empty_ehr)
        empty_ehr.connect()
        result = wf.run(output_dir=str(tmp_path))
        assert result.success
        assert result.stats.patients_extracted == 0


class TestETLStageError:
    def test_etl_stage_error(self):
        err = ETLStageError("extract failed", stage="extract")
        assert "extract failed" in str(err)
        assert err.stage == "extract"
