"""Metadata Catalog — 变量级元数据目录。

提供跨阶段元数据查询和变量血缘追踪。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


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
