"""OMOP CDM (Observational Medical Outcomes Partnership Common Data Model) 模块。

提供 OMOP CDM v5.4 表结构定义、FHIR→OMOP 映射、数据校验。
官方规范: https://www.ohdsi.org/data-standardization/
"""

from .exceptions import (
    OMOPError,
    OMOPMappingError,
    OMOPValidationError,
)

__version__ = "0.1.0"
__all__ = [
    "OMOPError",
    "OMOPValidationError",
    "OMOPMappingError",
]
