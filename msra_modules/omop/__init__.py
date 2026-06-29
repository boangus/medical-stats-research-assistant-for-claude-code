"""OMOP CDM (Observational Medical Outcomes Partnership Common Data Model) 模块。

提供 OMOP CDM v5.4 表结构定义、FHIR→OMOP 映射、数据校验。
官方规范: https://www.ohdsi.org/data-standardization/
"""

from .clinical_tables import (
    OmopConditionOccurrence,
    OmopMeasurement,
    create_condition_from_fhir,
    create_measurement_from_fhir_obs,
)
from .exceptions import (
    OMOPError,
    OMOPMappingError,
    OMOPValidationError,
)
from .mapper import FhirToOmopMapper
from .tables import (
    OmopPerson,
    OmopVisitOccurrence,
    create_visit_from_encounter,
)

__version__ = "0.1.0"
__all__ = [
    "OMOPError",
    "OMOPValidationError",
    "OMOPMappingError",
    "OmopPerson",
    "OmopVisitOccurrence",
    "OmopConditionOccurrence",
    "OmopMeasurement",
    "create_visit_from_encounter",
    "create_condition_from_fhir",
    "create_measurement_from_fhir_obs",
    "FhirToOmopMapper",
]
