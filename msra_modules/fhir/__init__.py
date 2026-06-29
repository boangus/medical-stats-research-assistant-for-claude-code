"""FHIR (Fast Healthcare Interoperability Resources) 模块。

提供 FHIR R4 资源解析、Bundle 处理、FHIR→OMOP 映射。
官方规范: https://hl7.org/fhir/R4/
"""

from .bundle import FHIRBundle, FHIRResourceType
from .exceptions import (
    FHIRBundleError,
    FHIRError,
    FHIRMappingError,
    FHIRParseError,
    FHIRResourceNotFoundError,
    FHIRValidationError,
)
from .observation import FHIRObservation, ObservationComponent
from .patient import FHIRPatient

__version__ = "0.1.0"
__all__ = [
    "FHIRError",
    "FHIRParseError",
    "FHIRValidationError",
    "FHIRResourceNotFoundError",
    "FHIRBundleError",
    "FHIRMappingError",
    "FHIRPatient",
    "FHIRObservation",
    "ObservationComponent",
    "FHIRBundle",
    "FHIRResourceType",
]
