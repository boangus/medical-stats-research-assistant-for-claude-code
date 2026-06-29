"""FHIR 异常层级。

异常分类:
- FHIRError: 所有 FHIR 相关异常的基类
- FHIRParseError: JSON 解析失败 / 资源格式错误
- FHIRValidationError: 资源结构存在但不符合 FHIR 规范
- FHIRResourceNotFoundError: Bundle 中找不到指定资源
- FHIRBundleError: Bundle 处理错误（entry 缺失、type 不支持等）
- FHIRMappingError: FHIR→OMOP 映射失败
"""

from __future__ import annotations

from typing import Optional


class FHIRError(Exception):
    """FHIR 模块所有异常的基类。"""

    def __init__(self, message: str, resource_type: Optional[str] = None) -> None:
        self.resource_type = resource_type
        super().__init__(message)


class FHIRParseError(FHIRError):
    """JSON 解析失败或资源缺少必需字段。"""

    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        field: Optional[str] = None,
    ) -> None:
        self.field = field
        super().__init__(message, resource_type=resource_type)


class FHIRValidationError(FHIRError):
    """资源字段值不符合 FHIR R4 规范（如错误的枚举值）。"""

    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        field: Optional[str] = None,
    ) -> None:
        self.field = field
        super().__init__(message, resource_type=resource_type)


class FHIRResourceNotFoundError(FHIRError):
    """在 Bundle 中按 ID/类型查找资源失败。"""

    def __init__(self, resource_id: str, resource_type: Optional[str] = None) -> None:
        self.resource_id = resource_id
        msg = f"资源不存在: {resource_type or 'Unknown'}/{resource_id}"
        super().__init__(msg, resource_type=resource_type)


class FHIRBundleError(FHIRError):
    """Bundle 结构错误（非 entry 缺失、type 不支持等）。"""

    def __init__(self, message: str, bundle_type: Optional[str] = None) -> None:
        self.bundle_type = bundle_type
        super().__init__(message)


class FHIRMappingError(FHIRError):
    """FHIR→OMOP 映射失败（编码缺失、目标表不存在等）。"""

    def __init__(
        self,
        message: str,
        source_resource: Optional[str] = None,
        target_table: Optional[str] = None,
    ) -> None:
        self.source_resource = source_resource
        self.target_table = target_table
        super().__init__(message)
