"""EHR (Electronic Health Record) 连接器模块。

提供统一的 EHR 数据访问抽象层，支持多种 EHR 系统（OpenMRS / OpenEHR / 自定义）。
所有连接器实现都返回 FHIR R4 格式的资源，与 fhir 模块兼容。
"""

from .base import EHRConnectorBase, EHRConnectionError, PatientQuery
from .mock_connector import MockEHRConnector
from .openmrs_connector import OpenMRSConnector

__version__ = "0.1.0"
__all__ = [
    "EHRConnectorBase",
    "EHRConnectionError",
    "PatientQuery",
    "MockEHRConnector",
    "OpenMRSConnector",
]
