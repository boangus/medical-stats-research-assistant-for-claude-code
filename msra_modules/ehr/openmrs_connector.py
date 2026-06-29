"""OpenMRS REST API 连接器实现。

OpenMRS 同时提供原生 REST API 和 FHIR 模块（/ws/fhir2/R4）。
本连接器优先使用 FHIR 模块（返回 FHIR R4 格式），否则用原生 API 并转换。

依赖: requests (HTTP 客户端)
官方文档: https://wiki.openmrs.org/display/docs/REST+Module+Web+Services
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import EHRConnectorBase, PatientQuery
from .exceptions import EHRConnectionError

try:
    import requests as _requests  # type: ignore
except ImportError:
    _requests = None  # type: ignore


class OpenMRSConnector(EHRConnectorBase):
    """OpenMRS REST API 连接器。

    优先使用 FHIR 模块端点；当 FHIR 模块不可用时降级到原生 API 并转换。

    Args:
        base_url: OpenMRS REST API 根 URL（如 http://host/openmrs/ws/rest/v1）
        username: Basic Auth 用户名
        password: Basic Auth 密码
        fhir_endpoint: FHIR 模块路径（默认 /ws/fhir2/R4）
        timeout: HTTP 超时（秒）
    """

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        fhir_endpoint: str = "/ws/fhir2/R4",
        timeout: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.fhir_endpoint = fhir_endpoint.rstrip("/")
        self.timeout = timeout
        self._connected = False
        self._session = None

    def connect(self) -> None:
        requests = self._get_requests()

        try:
            # 验证连接可达（GET /patient 测试）
            resp = requests.get(
                f"{self.base_url}/patient",
                auth=(self.username, self.password),
                timeout=self.timeout,
                params={"v": "default", "limit": 1},
            )
            if resp.status_code >= 500:
                raise EHRConnectionError(
                    f"OpenMRS 服务器错误: {resp.status_code}"
                )
            # 401/403 表示认证失败，但也算"可达"
            self._connected = True
        except Exception as e:
            raise EHRConnectionError(f"OpenMRS 连接失败: {e}") from e

    def disconnect(self) -> None:
        self._connected = False
        self._session = None

    def is_connected(self) -> bool:
        return self._connected

    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        self._ensure_connected()
        requests = self._get_requests()

        # 优先用 FHIR 模块
        fhir_url = (
            f"{self.base_url}{self.fhir_endpoint}/Patient/{patient_id}"
        )
        try:
            resp = requests.get(
                fhir_url,
                auth=(self.username, self.password),
                timeout=self.timeout,
            )
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 404:
                return None
        except Exception:
            pass

        # 降级：原生 API + 转换
        native_url = f"{self.base_url}/patient/{patient_id}"
        resp = requests.get(
            native_url,
            auth=(self.username, self.password),
            timeout=self.timeout,
        )
        if resp.status_code == 404:
            return None
        if resp.status_code != 200:
            raise EHRConnectionError(
                f"OpenMRS 查询失败: {resp.status_code}"
            )
        return self._native_to_fhir_patient(resp.json())

    def get_observations(
        self, patient_id: str
    ) -> List[Dict[str, Any]]:
        self._ensure_connected()
        requests = self._get_requests()

        url = (
            f"{self.base_url}{self.fhir_endpoint}/Observation"
            f"?subject=Patient/{patient_id}"
        )
        try:
            resp = requests.get(
                url,
                auth=(self.username, self.password),
                timeout=self.timeout,
            )
            if resp.status_code == 200:
                bundle = resp.json()
                return [
                    e.get("resource", {})
                    for e in bundle.get("entry", [])
                ]
        except Exception:
            pass
        return []

    def search_patients(
        self, query: PatientQuery
    ) -> List[Dict[str, Any]]:
        self._ensure_connected()
        requests = self._get_requests()

        # 原生 API 搜索（更灵活）
        params: Dict[str, Any] = {"v": "full"}
        if query.family_name:
            params["q"] = query.family_name

        resp = requests.get(
            f"{self.base_url}/patient",
            auth=(self.username, self.password),
            params=params,
            timeout=self.timeout,
        )
        if resp.status_code != 200:
            raise EHRConnectionError(
                f"OpenMRS 搜索失败: {resp.status_code}"
            )

        data = resp.json()
        results: List[Dict[str, Any]] = []
        for raw in data.get("results", []):
            fhir_patient = self._native_to_fhir_patient(raw)
            # 在客户端过滤 FHIR 字段
            if self._matches_fhir(fhir_patient, query):
                results.append(fhir_patient)
        return results

    def count_patients(self) -> int:
        self._ensure_connected()
        requests = self._get_requests()

        resp = requests.get(
            f"{self.base_url}/patient",
            auth=(self.username, self.password),
            params={"v": "count"},
            timeout=self.timeout,
        )
        if resp.status_code != 200:
            raise EHRConnectionError(
                f"OpenMRS 计数失败: {resp.status_code}"
            )
        return int(resp.json().get("count", 0))

    def _get_requests(self):
        """获取 requests 模块，未安装时抛 EHRConnectionError。

        暴露为方法以便测试时替换。
        """
        if _requests is None:
            raise EHRConnectionError(
                "requests 未安装。请运行: pip install requests"
            )
        return _requests

    @staticmethod
    def _native_to_fhir_patient(
        native: Dict[str, Any],
    ) -> Dict[str, Any]:
        """OpenMRS 原生 patient → FHIR R4 Patient dict。"""
        gender_raw = native.get("gender", "")
        # M/F/O → male/female/other
        gender_map = {"M": "male", "F": "female", "O": "other"}
        gender = gender_map.get(gender_raw, gender_raw.lower() if gender_raw else None)

        # 提取姓名
        name_block = native.get("personName", {})
        family = name_block.get("familyName")
        given = name_block.get("givenName")
        names = []
        if family or given:
            names.append(
                {
                    "family": family,
                    "given": [given] if given else [],
                    "use": "official",
                }
            )

        # 提取 MRN
        identifiers = []
        for ident in native.get("identifiers", []):
            identifiers.append(
                {
                    "system": "http://openmrs.org/mrn",
                    "value": ident.get("identifier"),
                }
            )

        return {
            "resourceType": "Patient",
            "id": native.get("uuid"),
            "gender": gender,
            "birthDate": native.get("birthdate"),
            "name": names,
            "identifier": identifiers,
        }

    @staticmethod
    def _matches_fhir(
        patient: Dict[str, Any], query: PatientQuery
    ) -> bool:
        """在客户端对 FHIR patient dict 应用过滤条件。"""
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
        return True
