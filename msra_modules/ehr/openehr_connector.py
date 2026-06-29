"""OpenEHR REST API 连接器实现。

OpenEHR 使用 reference model + archetypes 表达临床数据。
本连接器实现到 EHRbase REST API 的适配，并把 OpenEHR composition 转换为 FHIR R4。

依赖: requests (HTTP 客户端)
官方文档: https://ehrbase.readthedocs.io/
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import EHRConnectorBase, PatientQuery
from .exceptions import EHRConnectionError

try:
    import requests as _requests  # type: ignore
except ImportError:
    _requests = None  # type: ignore


class OpenEHRConnector(EHRConnectorBase):
    """OpenEHR (EHRbase) REST API 连接器。

    Args:
        base_url: EHRbase REST API 根 URL
        username: Basic Auth 用户名
        password: Basic Auth 密码
        timeout: HTTP 超时（秒）
    """

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        timeout: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.timeout = timeout
        self._connected = False

    def connect(self) -> None:
        requests = self._get_requests()
        try:
            resp = requests.get(
                f"{self.base_url}/definition/template/adl1.4",
                auth=(self.username, self.password),
                timeout=self.timeout,
            )
            if resp.status_code >= 500:
                raise EHRConnectionError(
                    f"OpenEHR 服务器错误: {resp.status_code}"
                )
            self._connected = True
        except Exception as e:
            raise EHRConnectionError(f"OpenEHR 连接失败: {e}") from e

    def disconnect(self) -> None:
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """通过 subject external_ref.id 查询 EHR，构造 FHIR Patient。

        OpenEHR 中"患者"信息存储在 EHR_STATUS 的 subject 字段。
        """
        self._ensure_connected()
        requests = self._get_requests()

        # 通过查询参数找 EHR（subject external_ref.id = patient_id）
        resp = requests.get(
            f"{self.base_url}/ehr",
            auth=(self.username, self.password),
            params={"subject_external_ref": patient_id},
            timeout=self.timeout,
        )
        if resp.status_code == 404:
            return None
        if resp.status_code != 200:
            raise EHRConnectionError(
                f"OpenEHR EHR 查询失败: {resp.status_code}"
            )

        ehr_data = resp.json()
        return self._ehr_to_fhir_patient(ehr_data, patient_id)

    def get_observations(
        self, patient_id: str
    ) -> List[Dict[str, Any]]:
        """从 OpenEHR compositions 提取 OBSERVATION 并转换为 FHIR Observation。"""
        self._ensure_connected()
        requests = self._get_requests()

        # 先查 ehr_id（通过 subject）
        ehr_resp = requests.get(
            f"{self.base_url}/ehr",
            auth=(self.username, self.password),
            params={"subject_external_ref": patient_id},
            timeout=self.timeout,
        )
        if ehr_resp.status_code != 200:
            return []
        ehr_id = ehr_resp.json().get("ehr_id")
        if not ehr_id:
            return []

        # 查询该 EHR 的所有 composition
        comp_resp = requests.get(
            f"{self.base_url}/ehr/{ehr_id}/composition",
            auth=(self.username, self.password),
            timeout=self.timeout,
        )
        if comp_resp.status_code != 200:
            return []

        compositions = comp_resp.json().get("compositions", [])
        observations: List[Dict[str, Any]] = []
        for comp in compositions:
            observations.extend(self._composition_to_observations(comp, patient_id))
        return observations

    def search_patients(
        self, query: PatientQuery
    ) -> List[Dict[str, Any]]:
        """OpenEHR 不直接支持按 gender/name 搜索 patient，需要遍历 EHR 列表。

        注意：此操作在大规模部署中性能较差，建议缓存或使用专用索引。
        """
        self._ensure_connected()
        requests = self._get_requests()

        resp = requests.get(
            f"{self.base_url}/ehr",
            auth=(self.username, self.password),
            timeout=self.timeout,
        )
        if resp.status_code != 200:
            raise EHRConnectionError(
                f"OpenEHR EHR 列表查询失败: {resp.status_code}"
            )

        ehrs = resp.json().get("ehr", [])
        results: List[Dict[str, Any]] = []
        for ehr in ehrs:
            subject_ref = (
                ehr.get("ehr_status", {})
                .get("subject", {})
                .get("external_ref", {})
                .get("id")
            )
            if not subject_ref:
                continue
            patient = self._ehr_to_fhir_patient(ehr, subject_ref)
            if self._matches_fhir(patient, query):
                results.append(patient)
        return results

    def count_patients(self) -> int:
        self._ensure_connected()
        requests = self._get_requests()

        resp = requests.get(
            f"{self.base_url}/ehr",
            auth=(self.username, self.password),
            timeout=self.timeout,
        )
        if resp.status_code != 200:
            raise EHRConnectionError(
                f"OpenEHR 计数失败: {resp.status_code}"
            )
        return len(resp.json().get("ehr", []))

    def _get_requests(self):
        if _requests is None:
            raise EHRConnectionError(
                "requests 未安装。请运行: pip install requests"
            )
        return _requests

    @staticmethod
    def _ehr_to_fhir_patient(
        ehr: Dict[str, Any], patient_id: str
    ) -> Dict[str, Any]:
        """OpenEHR EHR → FHIR R4 Patient。"""
        # 从 ehr_status.subject.party_additional_info 提取 gender/birthdate
        gender = None
        birthdate = None
        additional_info = (
            ehr.get("ehr_status", {})
            .get("subject", {})
            .get("party_additional_info", [])
        )
        for info in additional_info:
            name = info.get("name")
            value = info.get("value")
            if name == "gender":
                gender = value
            elif name == "birthdate":
                birthdate = value

        return {
            "resourceType": "Patient",
            "id": patient_id,
            "gender": gender,
            "birthDate": birthdate,
        }

    @staticmethod
    def _composition_to_observations(
        composition: Dict[str, Any], patient_id: str
    ) -> List[Dict[str, Any]]:
        """从 OpenEHR composition 提取 OBSERVATION 节点并转为 FHIR Observation。"""
        observations: List[Dict[str, Any]] = []
        comp_uid = composition.get("uid", "")
        # 提取 context.start_time 作为 effectiveDateTime
        effective_dt = (
            composition.get("context", {})
            .get("start_time", {})
            .get("value")
        )

        for content in composition.get("content", []):
            if content.get("@type") != "OBSERVATION":
                continue

            # 从 events → data → items 提取 value
            events = content.get("data", {}).get("events", [])
            for event in events:
                items = event.get("data", {}).get("items", [])
                for item in items:
                    name = item.get("name", {}).get("value", "")
                    value_block = item.get("value", {})
                    if not value_block:
                        continue
                    observations.append(
                        {
                            "resourceType": "Observation",
                            "id": f"{comp_uid}::{name}".replace(" ", "_"),
                            "status": "final",
                            "subject": {"reference": f"Patient/{patient_id}"},
                            "code": {
                                "coding": [
                                    {
                                        "system": "http://loinc.org",
                                        "code": "unknown",
                                        "display": name,
                                    }
                                ]
                            },
                            "valueQuantity": {
                                "value": value_block.get("magnitude"),
                                "unit": value_block.get("units"),
                            },
                            "effectiveDateTime": effective_dt,
                        }
                    )
        return observations

    @staticmethod
    def _matches_fhir(
        patient: Dict[str, Any], query: PatientQuery
    ) -> bool:
        if query.gender is not None:
            if patient.get("gender") != query.gender:
                return False
        return True
