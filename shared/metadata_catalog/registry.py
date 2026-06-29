"""Metadata Catalog — 变量级元数据目录。

提供跨阶段元数据查询和变量血缘追踪。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import json


class VariableType(str, Enum):
    """变量类型枚举。"""

    DEMOGRAPHIC = "demographic"
    CLINICAL = "clinical"
    LAB = "lab"
    DERIVED = "derived"
    OUTCOME = "outcome"
    COVARIATE = "covariate"
    EXPOSURE = "exposure"


@dataclass(frozen=True)
class MetadataEntry:
    """变量元数据条目。

    Attributes:
        variable: 变量名（如 "bmi"）
        description: 人类可读描述
        variable_type: 变量类型
        source_variables: 派生自的源变量列表（原始变量为空列表）
        unit: 单位（如 "kg/m^2"）
        value_range: 值域 [min, max] 或 None
        coding: 编码映射 {code: label}，分类变量使用
        created_at: 创建时间戳
        updated_at: 最近更新时间戳
        stage: 来源阶段（如 "stage1", "stage2"）
        notes: 自由文本备注
    """

    variable: str
    description: str
    variable_type: VariableType
    source_variables: List[str] = field(default_factory=list)
    unit: Optional[str] = None
    value_range: Optional[List[float]] = None
    coding: Optional[Dict[str, str]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    stage: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典（用于 JSON 导出）。"""
        return {
            "variable": self.variable,
            "description": self.description,
            "variable_type": self.variable_type.value
            if isinstance(self.variable_type, VariableType)
            else self.variable_type,
            "source_variables": self.source_variables,
            "unit": self.unit,
            "value_range": self.value_range,
            "coding": self.coding,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "stage": self.stage,
            "notes": self.notes,
        }


from .exceptions import (
    InvalidLineageError,
    VariableAlreadyExistsError,
    VariableNotFoundError,
)


@dataclass(frozen=True)
class LineageNode:
    """血缘图节点 — 引用 MetadataEntry。

    提供 `variable` 便利属性以直接访问变量名。
    """

    entry: MetadataEntry
    depth: int = 0

    @property
    def variable(self) -> str:
        return self.entry.variable


@dataclass(frozen=True)
class LineageGraph:
    """变量血缘图。

    Attributes:
        variable: 目标变量名
        upstream: 上游所有依赖（含传递依赖），按拓扑深度排序
        downstream: 下游所有依赖此变量的派生变量
    """

    variable: str
    upstream: List[LineageNode] = field(default_factory=list)
    downstream: List[LineageNode] = field(default_factory=list)


class MetadataRegistry:
    """变量级元数据目录。

    支持跨阶段元数据查询、变量血缘追踪、循环依赖检测。

    使用方式:
        registry = MetadataRegistry()
        registry.register(entry)
        graph = registry.lineage("bmi")
        registry.export_json("metadata.json")
    """

    def __init__(self) -> None:
        self._entries: Dict[str, MetadataEntry] = {}

    def register(self, entry: MetadataEntry, overwrite: bool = False) -> None:
        """注册新变量。

        Args:
            entry: 元数据条目
            overwrite: True 时允许覆盖已存在的变量

        Raises:
            VariableAlreadyExistsError: 变量已注册且 overwrite=False
            InvalidLineageError: 注册后检测到循环依赖
            VariableNotFoundError: source_variables 引用未注册的变量
        """
        if not overwrite and entry.variable in self._entries:
            raise VariableAlreadyExistsError(entry.variable)

        # 注意: source_variables 不强制预先注册 — 允许前向引用（迭代注册场景）。
        # 循环依赖通过 _detect_cycle 在图闭合时检测。
        self._entries[entry.variable] = entry

        # 检测循环依赖
        cycle = self._detect_cycle(entry.variable)
        if cycle:
            del self._entries[entry.variable]
            raise InvalidLineageError(cycle)

    def lookup(self, variable: str) -> MetadataEntry:
        """查询变量元数据。

        Raises:
            VariableNotFoundError: 变量未注册
        """
        if variable not in self._entries:
            raise VariableNotFoundError(variable)
        return self._entries[variable]

    def list_all(self) -> List[MetadataEntry]:
        """列出所有变量元数据（返回副本列表）。"""
        return list(self._entries.values())

    def lineage(self, variable: str) -> LineageGraph:
        """获取变量血缘图（上游 + 下游）。

        Args:
            variable: 目标变量名

        Returns:
            LineageGraph 包含 upstream（所有上游）和 downstream（所有下游）

        Raises:
            VariableNotFoundError: 变量未注册
        """
        if variable not in self._entries:
            raise VariableNotFoundError(variable)

        upstream = self._collect_upstream(variable)
        downstream = self._collect_downstream(variable)

        return LineageGraph(
            variable=variable,
            upstream=upstream,
            downstream=downstream,
        )

    def export_json(self, path: Path) -> None:
        """导出所有元数据到 JSON 文件。"""
        data = {
            "variables": [e.to_dict() for e in self._entries.values()],
            "exported_at": datetime.now().isoformat(),
            "count": len(self._entries),
        }
        Path(path).write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _collect_upstream(self, variable: str) -> List[LineageNode]:
        """递归收集所有上游依赖（含传递依赖），按拓扑深度排序。"""
        visited = set()
        result: List[LineageNode] = []

        def _walk(var: str, depth: int) -> None:
            entry = self._entries.get(var)
            if entry is None:
                return
            for src in entry.source_variables:
                if src in visited:
                    continue
                visited.add(src)
                src_entry = self._entries.get(src)
                if src_entry is not None:
                    result.append(LineageNode(entry=src_entry, depth=depth))
                    _walk(src, depth + 1)

        _walk(variable, 1)
        result.sort(key=lambda n: n.depth)
        return result

    def _collect_downstream(self, variable: str) -> List[LineageNode]:
        """递归收集所有下游派生变量。"""
        visited = set()
        result: List[LineageNode] = []

        def _walk(var: str, depth: int) -> None:
            for entry in self._entries.values():
                if var in entry.source_variables and entry.variable not in visited:
                    visited.add(entry.variable)
                    result.append(LineageNode(entry=entry, depth=depth))
                    _walk(entry.variable, depth + 1)

        _walk(variable, 1)
        result.sort(key=lambda n: n.depth)
        return result

    def _detect_cycle(self, start: str) -> Optional[list]:
        """检测从 start 出发是否存在循环依赖。返回循环路径或 None。"""
        WHITE, GRAY, BLACK = 0, 1, 2
        color: Dict[str, int] = {}
        path: List[str] = []

        def _dfs(node: str) -> Optional[list]:
            color[node] = GRAY
            path.append(node)
            entry = self._entries.get(node)
            if entry is not None:
                for src in entry.source_variables:
                    if color.get(src, WHITE) == GRAY:
                        # 找到循环
                        cycle_start = path.index(src)
                        return path[cycle_start:] + [src]
                    if color.get(src, WHITE) == WHITE:
                        result = _dfs(src)
                        if result is not None:
                            return result
            path.pop()
            color[node] = BLACK
            return None

        return _dfs(start)
