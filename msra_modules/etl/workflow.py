"""ETL 工作流：EHR → FHIR Bundle → OMOP CDM → CSV。

支持任意实现了 EHRConnectorBase 的连接器作为数据源。

Usage:
    from msra_modules.ehr import MockEHRConnector
    from msra_modules.etl import ETLWorkflow

    ehr = MockEHRConnector(patients=[...], observations=[...])
    ehr.connect()
    wf = ETLWorkflow(ehr_connector=ehr)
    result = wf.run(output_dir="./output")
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..ehr.base import EHRConnectorBase
from ..fhir.bundle import FHIRBundle
from ..omop.mapper import FhirToOmopMapper
from .exceptions import ETLStageError


_OMOP_TABLES = ["person", "visit_occurrence", "condition_occurrence", "measurement"]


@dataclass
class ETLStats:
    """ETL 流程统计信息。"""

    patients_extracted: int = 0
    observations_extracted: int = 0
    omop_records_created: int = 0


@dataclass
class ETLResult:
    """ETL run 的最终结果。"""

    success: bool
    stats: ETLStats
    output_dir: Path
    errors: List[str] = field(default_factory=list)


class ETLWorkflow:
    """批量 ETL 工作流编排器。

    Args:
        ehr_connector: 已实现的 EHR 连接器实例（未连接状态）
        batch_size: 每次批量提取的记录数（默认 100）
    """

    def __init__(
        self,
        ehr_connector: EHRConnectorBase,
        batch_size: int = 100,
    ) -> None:
        self.ehr = ehr_connector
        self.batch_size = batch_size
        self._patients: List[Dict[str, Any]] = []
        self._observations: List[Dict[str, Any]] = []
        self._bundle: Optional[FHIRBundle] = None
        self.omop_data: Dict[str, List[Any]] = {
            table: [] for table in _OMOP_TABLES
        }
        self.stats = ETLStats()

    def extract_all(self) -> None:
        """从 EHR 提取所有 Patient 和 Observation 资源。"""
        try:
            # 提取所有 Patient（用空 query 表示不过滤）
            from ..ehr.base import PatientQuery
            self._patients = list(self.ehr.search_patients(PatientQuery()))

            # 提取每个 Patient 的 Observation
            self._observations = []
            for patient in self._patients:
                patient_id = patient.get("id")
                if not patient_id:
                    continue
                obs_list = self.ehr.get_observations(patient_id)
                self._observations.extend(obs_list)

            self.stats.patients_extracted = len(self._patients)
            self.stats.observations_extracted = len(self._observations)
        except Exception as e:
            raise ETLStageError(
                f"Extract 阶段失败: {e}", stage="extract"
            ) from e

    def extract_patients(self) -> List[Dict[str, Any]]:
        """仅提取 Patient 列表（供测试用）。"""
        from ..ehr.base import PatientQuery
        self._patients = list(self.ehr.search_patients(PatientQuery()))
        self.stats.patients_extracted = len(self._patients)
        return self._patients

    def transform_to_omop(self) -> Dict[str, List[Any]]:
        """将 FHIR 资源转换为 OMOP CDM 表字典。"""
        try:
            # 构造 FHIR Bundle
            entries = []
            for p in self._patients:
                entries.append({"resource": p})
            for o in self._observations:
                entries.append({"resource": o})
            bundle_dict = {
                "resourceType": "Bundle",
                "type": "collection",
                "entry": entries,
            }
            self._bundle = FHIRBundle.from_dict(bundle_dict)

            # 转 OMOP
            mapper = FhirToOmopMapper()
            self.omop_data = mapper.map_bundle(self._bundle)

            self.stats.omop_records_created = sum(
                len(v) for v in self.omop_data.values()
            )
            return self.omop_data
        except Exception as e:
            raise ETLStageError(
                f"Transform 阶段失败: {e}", stage="transform"
            ) from e

    def load_to_csv(self, output_dir: str) -> str:
        """将 OMOP 表导出为 CSV。

        Args:
            output_dir: 输出目录路径

        Returns:
            实际输出目录路径
        """
        try:
            out = Path(output_dir)
            out.mkdir(parents=True, exist_ok=True)

            for table_name in _OMOP_TABLES:
                records = self.omop_data.get(table_name, [])
                if not records:
                    # 写空 CSV（仅表头）以表示该表无数据
                    self._write_empty_csv(out / f"{table_name}.csv")
                    continue

                # 从第一条记录的字段提取列名
                first = records[0].to_dict() if hasattr(records[0], "to_dict") else records[0]
                fieldnames = list(first.keys())

                csv_path = out / f"{table_name}.csv"
                with open(csv_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for record in records:
                        row = record.to_dict() if hasattr(record, "to_dict") else record
                        # 处理 None 值
                        row = {k: ("" if v is None else v) for k, v in row.items()}
                        writer.writerow(row)
            return str(out)
        except Exception as e:
            raise ETLStageError(
                f"Load 阶段失败: {e}", stage="load"
            ) from e

    @staticmethod
    def _write_empty_csv(csv_path: Path) -> None:
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write("")

    def run(self, output_dir: str) -> ETLResult:
        """完整执行 ETL 流程：extract → transform → load。

        Args:
            output_dir: CSV 输出目录

        Returns:
            ETLResult 实例（含统计和错误列表）
        """
        errors: List[str] = []
        success = True

        try:
            self.extract_all()
        except ETLStageError as e:
            errors.append(str(e))
            success = False

        if success:
            try:
                self.transform_to_omop()
            except ETLStageError as e:
                errors.append(str(e))
                success = False

        if success:
            try:
                self.load_to_csv(output_dir)
            except ETLStageError as e:
                errors.append(str(e))
                success = False

        return ETLResult(
            success=success,
            stats=self.stats,
            output_dir=Path(output_dir),
            errors=errors,
        )
