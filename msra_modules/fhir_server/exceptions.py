"""FHIR Server 客户端异常。"""

from __future__ import annotations


class FHIRServerError(Exception):
    """FHIR 服务器操作错误（HTTP 错误、连接失败、解析错误等）。"""

    pass
