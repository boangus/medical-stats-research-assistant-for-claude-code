"""Mock EHR 连接器实现。

用于测试和本地开发：所有数据来自内存，无网络依赖。
所有资源返回 FHIR R4 格式。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import EHRConnectorBase, PatientQuery


class MockEHRConnector(EHRConnectorBase):
    """内存版 EHR 连接器（用于测试/演示）。

    Args:
        patients: Patient 资源 dict 列表
        observations: Observation 资源 dict 列表
    """

    def __init__(
        self,
        patients: Optional[List[Dict[str, Any]]] = None,
        observations: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self._patients = list(patients or [])
        self._observations = list(observations or [])
        self._connected = False

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        self._ensure_connected()
        for p in self._patients:
            if p.get("id") == patient_id:
                return p
        return None

    def get_observations(
        self, patient_id: str
    ) -> List[Dict[str, Any]]:
        self._ensure_connected()
        ref = f"Patient/{patient_id}"
        return [
            obs
            for obs in self._observations
            if obs.get("subject", {}).get("reference") == ref
        ]

    def search_patients(
        self, query: PatientQuery
    ) -> List[Dict[str, Any]]:
        self._ensure_connected()
        results = []
        for p in self._patients:
            if not self._matches(p, query):
                continue
            results.append(p)
        return results

    def count_patients(self) -> int:
        self._ensure_connected()
        return len(self._patients)

    @staticmethod
    def _matches(patient: Dict[str, Any], query: PatientQuery) -> bool:
        """检查单个 patient 是否匹配查询条件。"""
        if query.gender is not None:
            if patient.get("gender") != query.gender:
                return False

        if query.family_name is not None:
            names = patient.get("name", [])
            family = next(
                (n.get("family") for n in names if n.get("family")),
                None,
            )
            if family != query.family_name:
                return False

        if query.given_name is not None:
            names = patient.get("name", [])
            givens = [
                g
                for n in names
                for g in (n.get("given") or [])
            ]
            if query.given_name not in givens:
                return False

        if query.birth_date_from is not None:
            if patient.get("birthDate", "") < query.birth_date_from:
                return False

        if query.birth_date_to is not None:
            if patient.get("birthDate", "") > query.birth_date_to:
                return False

        return True
