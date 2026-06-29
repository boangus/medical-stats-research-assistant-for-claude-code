"""EHR 连接器异常。"""

from __future__ import annotations


class EHRConnectionError(Exception):
    """EHR 连接器相关错误（未连接、连接断开、查询超时等）。"""

    pass
