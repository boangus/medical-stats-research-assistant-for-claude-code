"""Metadata Catalog — 变量级元数据目录。

提供跨阶段元数据查询和变量血缘追踪。
"""

from .exceptions import (
    InvalidLineageError,
    MetadataCatalogError,
    VariableAlreadyExistsError,
    VariableNotFoundError,
)
from .registry import (
    LineageGraph,
    LineageNode,
    MetadataEntry,
    MetadataRegistry,
    VariableType,
)

__version__ = "0.1.0"
__all__ = [
    "MetadataRegistry",
    "MetadataEntry",
    "VariableType",
    "LineageGraph",
    "LineageNode",
    "MetadataCatalogError",
    "VariableNotFoundError",
    "VariableAlreadyExistsError",
    "InvalidLineageError",
]
