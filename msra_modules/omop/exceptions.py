"""OMOP CDM 异常层级。

异常分类:
- OMOPError: 所有 OMOP 相关异常的基类
- OMOPValidationError: OMOP 表数据不符合 CDM 规范（必需字段缺失、类型错误）
- OMOPMappingError: FHIR→OMOP 映射失败（编码缺失、目标表不存在）
"""

from __future__ import annotations

from typing import Optional


class OMOPError(Exception):
    """OMOP 模块所有异常的基类。"""

    def __init__(
        self, message: str, table_name: Optional[str] = None
    ) -> None:
        self.table_name = table_name
        super().__init__(message)


class OMOPValidationError(OMOPError):
    """OMOP 表数据不符合 CDM 规范。"""

    def __init__(
        self,
        message: str,
        table_name: Optional[str] = None,
        field: Optional[str] = None,
    ) -> None:
        self.field = field
        super().__init__(message, table_name=table_name)


class OMOPMappingError(OMOPError):
    """FHIR→OMOP 映射失败。"""

    def __init__(
        self,
        message: str,
        source_resource: Optional[str] = None,
        target_table: Optional[str] = None,
    ) -> None:
        self.source_resource = source_resource
        self.target_table = target_table
        super().__init__(message, table_name=target_table)
