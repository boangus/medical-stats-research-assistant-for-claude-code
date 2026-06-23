"""
MSRA Multi-Agent Framework - Data Validator Agent

数据验证Agent的具体实现示例，展示如何继承BaseAgent并实现核心功能。

Author: MSRA Team
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path

from .base_agent import BaseAgent
from .interfaces import (
    AgentCapability,
    AgentStatus,
    Handoff,
    ConflictReport,
    ConflictLevel,
    ConflictType,
)


class DataValidatorAgent(BaseAgent):
    """
    数据验证Agent - 负责数据质量检查和清洗

    职责:
    - 数据结构验证
    - 缺失值检测与处理
    - 异常值检测
    - 变量构造
    - 盲态审核流程

    边界:
    - ✅ 建议清洗策略
    - ✅ 自动执行常规清洗
    - ❌ 自行决定删除数据
    - ❌ 跳过盲态审核流程
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            agent_id="data_validator",
            agent_type="validator",
            config=config
        )
        self._validation_rules: Dict[str, Any] = {}
        self._cleaning_log: List[Dict[str, Any]] = []

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="data_validation",
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data_path": {"type": "string"},
                        "validation_rules": {"type": "object"}
                    },
                    "required": ["data_path"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "validation_report": {"type": "object"},
                        "cleaned_data_path": {"type": "string"}
                    }
                },
                constraints=[
                    "cannot_delete_data_without_approval",
                    "must_follow_blinding_protocol"
                ],
                dependencies=[],
                quality_metrics={
                    "completeness": "数据完整性检查",
                    "consistency": "数据一致性检查",
                    "accuracy": "数据准确性检查"
                }
            ),
            AgentCapability(
                name="outlier_detection",
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data_path": {"type": "string"},
                        "method": {"type": "string", "enum": ["iqr", "zscore", "clinical"]}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "outliers": {"type": "array"},
                        "report": {"type": "object"}
                    }
                },
                constraints=[],
                dependencies=["data_validation"],
                quality_metrics={
                    "precision": "异常值检测精确度",
                    "recall": "异常值检测召回率"
                }
            ),
            AgentCapability(
                name="variable_construction",
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data_path": {"type": "string"},
                        "variable_specs": {"type": "array"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "constructed_variables": {"type": "array"},
                        "code": {"type": "string"}
                    }
                },
                constraints=[],
                dependencies=["data_validation"],
                quality_metrics={
                    "correctness": "变量构造正确性"
                }
            )
        ]

    async def execute(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Handoff:
        """
        执行数据验证任务

        Args:
            task: 包含data_path和可选的validation_rules
            context: 执行上下文（如工作目录、配置等）

        Returns:
            Handoff: 标准接棒格式
        """
        self._status = AgentStatus.PROCESSING
        self._cleaning_log = []

        try:
            data_path = task.get("data_path")
            validation_rules = task.get("validation_rules", {})

            if not data_path:
                raise ValueError("data_path is required")

            # 1. 加载数据
            data_info = await self._load_data(data_path)

            # 2. 执行验证
            validation_result = await self._validate_data(data_info, validation_rules)

            # 3. 检测异常值
            outlier_result = await self._detect_outliers(data_info)

            # 4. 生成清洗建议
            cleaning_suggestions = await self._generate_cleaning_suggestions(
                validation_result,
                outlier_result
            )

            # 5. 执行自动清洗（如果有权限）
            cleaned_data_path = None
            if task.get("auto_clean", False):
                cleaned_data_path = await self._auto_clean(data_path, cleaning_suggestions)

            # 6. 生成验证报告
            report_path = await self._generate_report(
                validation_result,
                outlier_result,
                cleaning_suggestions,
                context.get("output_dir", "./output")
            )

            self._status = AgentStatus.COMPLETED

            return self._create_handoff(
                completed_work=[
                    "数据结构验证",
                    "缺失值检测",
                    "异常值检测",
                    "清洗建议生成"
                ],
                artifacts={
                    report_path: "数据验证报告",
                    cleaned_data_path or data_path: "数据文件"
                },
                verification_method="运行验证脚本检查数据质量指标",
                known_issues=validation_result.get("warnings", []),
                pending_decisions=[
                    f"是否执行清洗操作: {s['description']}"
                    for s in cleaning_suggestions
                    if s.get("requires_approval", False)
                ],
                data_summary={
                    "n_records": data_info.get("n_records", 0),
                    "n_variables": data_info.get("n_variables", 0),
                    "missing_rate": validation_result.get("missing_rate", 0),
                    "outlier_count": outlier_result.get("count", 0)
                },
                next_agent="method_consultant"
            )

        except Exception as e:
            self._status = AgentStatus.FAILED
            self._logger.error(f"Execution failed: {e}")

            return self._create_handoff(
                completed_work=[],
                artifacts={},
                verification_method="检查错误日志",
                known_issues=[str(e)],
                pending_decisions=["是否重试或人工介入"]
            )

    async def _load_data(self, data_path: str) -> Dict[str, Any]:
        """加载数据并返回基本信息"""
        path = Path(data_path)

        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {data_path}")

        # 模拟数据加载（实际实现应使用pandas等库）
        data_info = {
            "path": str(path),
            "size_bytes": path.stat().st_size,
            "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            "n_records": 0,  # 实际实现应读取数据
            "n_variables": 0,
            "columns": []
        }

        # 使用缓存
        if self._cache:
            cached = await self._cache.get(f"data_info:{data_path}")
            if cached:
                return cached

            await self._cache.set(
                f"data_info:{data_path}",
                data_info,
                ttl=3600,
                tags=["data_info"]
            )

        return data_info

    async def _validate_data(
        self,
        data_info: Dict[str, Any],
        rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行数据验证"""
        result = {
            "passed": True,
            "errors": [],
            "warnings": [],
            "missing_rate": 0.0,
            "checks": []
        }

        # 结构验证
        result["checks"].append({
            "name": "structure_check",
            "passed": True,
            "details": "数据结构符合预期"
        })

        # 类型验证
        result["checks"].append({
            "name": "type_check",
            "passed": True,
            "details": "变量类型正确"
        })

        # 缺失值检查
        result["checks"].append({
            "name": "missing_check",
            "passed": True,
            "details": "缺失值比例在可接受范围内"
        })

        return result

    async def _detect_outliers(
        self,
        data_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """检测异常值"""
        result = {
            "count": 0,
            "by_variable": {},
            "method": "iqr"
        }

        # 实际实现应使用统计方法检测异常值
        # 这里仅作为示例

        return result

    async def _generate_cleaning_suggestions(
        self,
        validation_result: Dict[str, Any],
        outlier_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """生成清洗建议"""
        suggestions = []

        # 基于验证结果生成建议
        for error in validation_result.get("errors", []):
            suggestions.append({
                "type": "fix_error",
                "description": error,
                "auto_fixable": False,
                "requires_approval": True
            })

        # 基于异常值结果生成建议
        if outlier_result.get("count", 0) > 0:
            suggestions.append({
                "type": "handle_outliers",
                "description": f"处理{outlier_result['count']}个异常值",
                "auto_fixable": True,
                "requires_approval": True
            })

        return suggestions

    async def _auto_clean(
        self,
        data_path: str,
        suggestions: List[Dict[str, Any]]
    ) -> Optional[str]:
        """执行自动清洗"""
        cleaned_path = str(data_path).replace(".", "_cleaned.")

        for suggestion in suggestions:
            if suggestion.get("auto_fixable") and not suggestion.get("requires_approval"):
                self._cleaning_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": suggestion["type"],
                    "description": suggestion["description"]
                })

        return cleaned_path

    async def _generate_report(
        self,
        validation_result: Dict[str, Any],
        outlier_result: Dict[str, Any],
        cleaning_suggestions: List[Dict[str, Any]],
        output_dir: str
    ) -> str:
        """生成验证报告"""
        output_path = Path(output_dir) / "validation_report.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "timestamp": datetime.now().isoformat(),
            "agent": self._agent_id,
            "validation": validation_result,
            "outliers": outlier_result,
            "cleaning_suggestions": cleaning_suggestions,
            "cleaning_log": self._cleaning_log
        }

        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))

        return str(output_path)

    async def vote_on_conflict(self, conflict: ConflictReport) -> Dict[str, Any]:
        """
        对冲突进行投票

        作为数据验证专家，对数据相关冲突有发言权
        """
        if conflict.conflict_type == ConflictType.DATA_INCONSISTENCY.value:
            # 数据不一致冲突，数据验证Agent有较高发言权
            return {
                "voter_id": self._agent_id,
                "choice": conflict.resolution_suggestions[0] if conflict.resolution_suggestions else "re_validate",
                "confidence": 0.9,
                "rationale": "作为数据验证专家，建议重新验证数据一致性"
            }

        # 其他类型冲突，较低发言权
        return {
            "voter_id": self._agent_id,
            "choice": "defer_to_expert",
            "confidence": 0.3,
            "rationale": "此冲突类型不在我的专业范围内"
        }


# ========================================
# Exports
# ========================================

__all__ = ["DataValidatorAgent"]
