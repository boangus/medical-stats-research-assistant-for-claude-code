"""CDISC module — SDTM/ADaM 数据处理。

提供 SAS XPT 文件读取、SDTM 校验、ADaM 转换。
"""

from .exceptions import (
    ADaMNotFoundError,
    CDISCError,
    SDTMParseError,
    SDTMValidationError,
)
from .sdtm import SDTMReader

__version__ = "0.1.0"
__all__ = [
    "CDISCError",
    "SDTMParseError",
    "SDTMValidationError",
    "ADaMNotFoundError",
    "SDTMReader",
]
