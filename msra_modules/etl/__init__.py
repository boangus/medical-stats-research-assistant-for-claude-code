"""批量 ETL 工具模块。

从 EHR 批量拉取 → 转 FHIR Bundle → 转 OMOP CDM 表 → 导出 CSV/Parquet。
"""

from .workflow import ETLResult, ETLStageError, ETLStats, ETLWorkflow

__version__ = "0.1.0"
__all__ = ["ETLWorkflow", "ETLResult", "ETLStats", "ETLStageError"]
