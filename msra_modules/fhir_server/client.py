"""FHIR R4 Server 客户端实现。

支持任何符合 FHIR R4 规范的服务器（HAPI FHIR / Microsoft FHIR Server / etc）。
通过 Bearer Token 认证。

官方规范: https://hl7.org/fhir/R4/http.html
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..fhir.bundle import FHIRBundle
from .exceptions import FHIRServerError

try:
    import requests as _requests  # type: ignore
except ImportError:
    _requests = None  # type: ignore


class FHIRServerClient:
    """FHIR R4 Server 客户端。

    Args:
        base_url: FHIR 服务器根 URL（如 https://hapi.fhir.org/baseR4）
        bearer_token: Bearer Token（无认证时为 None）
        timeout: HTTP 超时（秒）
    """

    def __init__(
        self,
        base_url: str,
        bearer_token: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.bearer_token = bearer_token
        self.timeout = timeout

    def ping(self) -> bool:
        """检查服务器可达性（GET /metadata）。"""
        try:
            requests = self._get_requests()
            resp = requests.get(
                f"{self.base_url}/metadata",
                headers=self._headers(),
                timeout=self.timeout,
            )
            return resp.status_code == 200
        except Exception:
            return False

    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """按 ID 获取 Patient 资源。

        Returns:
            FHIR Patient dict，或 None（不存在）
        """
        requests = self._get_requests()
        resp = requests.get(
            f"{self.base_url}/Patient/{patient_id}",
            headers=self._headers(),
            timeout=self.timeout,
        )
        if resp.status_code == 404:
            return None
        if resp.status_code != 200:
            raise FHIRServerError(
                f"获取 Patient 失败: {resp.status_code} {resp.text}"
            )
        return resp.json()

    def search_patients(
        self,
        name: Optional[str] = None,
        gender: Optional[str] = None,
        birth_date: Optional[str] = None,
        count: Optional[int] = None,
    ) -> FHIRBundle:
        """按条件搜索 Patient 资源。

        Args:
            name: 姓名（部分匹配）
            gender: 性别（male/female/other）
            birth_date: 出生日期（如 "1990-01-01" 或 "gt1980"）
            count: 返回数量上限

        Returns:
            FHIRBundle 实例
        """
        params: Dict[str, Any] = {}
        if name:
            params["name"] = name
        if gender:
            params["gender"] = gender
        if birth_date:
            params["birthdate"] = birth_date
        if count:
            params["_count"] = count

        return self._search("Patient", params)

    def search_observations(
        self,
        patient_id: Optional[str] = None,
        code: Optional[str] = None,
        date: Optional[str] = None,
        count: Optional[int] = None,
    ) -> FHIRBundle:
        """搜索 Observation 资源。"""
        params: Dict[str, Any] = {}
        if patient_id:
            params["subject"] = f"Patient/{patient_id}"
        if code:
            params["code"] = code
        if date:
            params["date"] = date
        if count:
            params["_count"] = count

        return self._search("Observation", params)

    def create_patient(
        self, patient: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建新的 Patient 资源（POST /Patient）。

        Returns:
            服务器返回的 Patient dict（含新分配的 id）

        Raises:
            FHIRServerError: 创建失败（409 冲突等）
        """
        return self._create("Patient", patient)

    def create_observation(
        self, observation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建新的 Observation 资源。"""
        return self._create("Observation", observation)

    def _search(
        self, resource_type: str, params: Dict[str, Any]
    ) -> FHIRBundle:
        requests = self._get_requests()
        resp = requests.get(
            f"{self.base_url}/{resource_type}",
            headers=self._headers(),
            params=params,
            timeout=self.timeout,
        )
        if resp.status_code != 200:
            raise FHIRServerError(
                f"搜索 {resource_type} 失败: {resp.status_code} {resp.text}"
            )
        bundle_data = resp.json()
        # 包装为 FHIRBundle，可能缺少 entry 时补 []
        bundle_data.setdefault("entry", [])
        return FHIRBundle.from_dict(bundle_data)

    def _create(
        self, resource_type: str, resource: Dict[str, Any]
    ) -> Dict[str, Any]:
        requests = self._get_requests()
        headers = self._headers()
        headers["Content-Type"] = "application/fhir+json"
        resp = requests.post(
            f"{self.base_url}/{resource_type}",
            headers=headers,
            json=resource,
            timeout=self.timeout,
        )
        if resp.status_code not in (200, 201):
            raise FHIRServerError(
                f"创建 {resource_type} 失败: {resp.status_code} {resp.text}"
            )
        return resp.json()

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/fhir+json"}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        return headers

    def _get_requests(self):
        if _requests is None:
            raise FHIRServerError(
                "requests 未安装。请运行: pip install requests"
            )
        return _requests
