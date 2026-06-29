"""FHIR Server 客户端模块。

连接到符合 FHIR R4 规范的服务器（HAPI FHIR / Microsoft FHIR Server / IBM / etc），
提供查询、创建、更新等操作。

依赖: requests
"""

from .client import FHIRServerClient, FHIRServerError

__version__ = "0.1.0"
__all__ = ["FHIRServerClient", "FHIRServerError"]
