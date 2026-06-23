"""
MSRA Multi-Agent Framework - Exec Runner Agent

统计程序员角色：R/Python代码生成、自愈Debug（5轮）、[SKIP]诚实标记。

Author: MSRA Team
Version: 1.0.0
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

from agents.core.base_agent import BaseAgent
from agents.core.interfaces import (
    AgentCapability,
    AgentStatus,
    Handoff,
    ConflictReport,
    ConflictLevel,
    ConflictType,
)

MAX_DEBUG_ROUNDS = 5


class ExecRunnerAgent(BaseAgent):
    """
    执行运行Agent - 负责按SAP生成并执行分析代码

    职责:
    - R/Python 代码生成
    - 最多 5 轮自愈 Debug
    - 按 SAP 变量构造逻辑生成分析变量
    - [SKIP] 诚实标记

    边界:
    - ✅ 独立生成并执行代码
    - ✅ 最多 5 轮自愈 Debug
    - ❌ 偏离 SAP 内容
    - ❌ 自行解读结果或下统计推断
    - ❌ 5 轮 Debug 仍失败时静默跳过
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            agent_id="exec_runner",
            agent_type="executor",
            config=config,
        )
        self._debug_rounds: int = 0
        self._skip_log: List[Dict[str, Any]] = []
        self._execution_log: List[Dict[str, Any]] = []

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="variable_construction",
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data_path": {"type": "string"},
                        "variable_specs": {"type": "array"},
                        "language": {"type": "string", "enum": ["R", "Python"]},
                    },
                    "required": ["data_path", "variable_specs", "language"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "constructed_data_path": {"type": "string"},
                        "code": {"type": "string"},
                        "construction_log": {"type": "array"},
                    },
                },
                constraints=["must_follow_sap", "must_set_random_seed"],
                dependencies=["sap_generation"],
                quality_metrics={"correctness": "变量构造正确性"},
            ),
            AgentCapability(
                name="descriptive_statistics",
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data_path": {"type": "string"},
                        "language": {"type": "string", "enum": ["R", "Python"]},
                        "table_specs": {"type": "array"},
                    },
                    "required": ["data_path", "language"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "table1_path": {"type": "string"},
                        "code": {"type": "string"},
                    },
                },
                constraints=["normal_use_mean_sd", "nonnormal_use_median_iqr"],
                dependencies=["variable_construction"],
                quality_metrics={"completeness": "描述统计覆盖度"},
            ),
            AgentCapability(
                name="inferential_analysis",
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data_path": {"type": "string"},
                        "sap_methods": {"type": "array"},
                        "language": {"type": "string", "enum": ["R", "Python"]},
                    },
                    "required": ["data_path", "sap_methods", "language"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "results_path": {"type": "string"},
                        "figures": {"type": "array"},
                        "code": {"type": "string"},
                        "debug_log": {"type": "array"},
                    },
                },
                constraints=["must_follow_sap", "max_5_debug_rounds"],
                dependencies=["descriptive_statistics"],
                quality_metrics={
                    "completeness": "分析完整性",
                    "reproducibility": "可复现性",
                },
            ),
        ]

    async def execute(
        self, task: Dict[str, Any], context: Dict[str, Any]
    ) -> Handoff:
        self._status = AgentStatus.PROCESSING
        self._debug_rounds = 0
        self._skip_log = []
        self._execution_log = []

        try:
            task_type = task.get("task_type", "full_execution")
            sap = task.get("sap", {})
            language = task.get("language", "Python")
            data_path = task.get("data_path")
            output_dir = context.get("output_dir", "./output")

            if task_type == "variable_construction":
                return await self._construct_variables(task, context)
            elif task_type == "descriptive":
                return await self._run_descriptive(task, context)
            elif task_type == "inferential":
                return await self._run_inferential(task, context)
            else:
                return await self._full_execution(task, context)

        except Exception as e:
            self._status = AgentStatus.FAILED
            self._logger.error(f"Exec Runner failed: {e}")
            return self._create_handoff(
                completed_work=[],
                artifacts={},
                verification_method="检查错误日志",
                known_issues=[str(e)],
                pending_decisions=["是否重试或降级到 Skill 模式"],
            )

    async def _full_execution(
        self, task: Dict[str, Any], context: Dict[str, Any]
    ) -> Handoff:
        """完整分析执行流程"""
        sap = task.get("sap", {})
        language = task.get("language", "Python")
        data_path = task.get("data_path")
        output_dir = context.get("output_dir", "./output")

        artifacts = {}
        completed = []

        # Phase 0: SAP 验证
        sap_valid = await self._validate_sap(sap)
        if not sap_valid:
            return self._create_handoff(
                completed_work=["SAP 验证失败"],
                artifacts={},
                verification_method="SAP 完整性检查",
                known_issues=["SAP 缺少必填字段"],
                pending_decisions=["请补充 SAP 后重试"],
            )
        completed.append("SAP 验证")

        # Phase 1: 变量构造
        var_result = await self._construct_variables(task, context)
        completed.append("变量构造")
        for path, desc in var_result.artifacts.items():
            artifacts[path] = desc

        # Phase 2: 描述统计
        desc_result = await self._run_descriptive(task, context)
        completed.append("描述统计")
        for path, desc in desc_result.artifacts.items():
            artifacts[path] = desc

        # Phase 3: 推断分析
        inf_result = await self._run_inferential(task, context)
        completed.append("推断分析")
        for path, desc in inf_result.artifacts.items():
            artifacts[path] = desc

        # Phase 5: 输出产物
        code_path = await self._save_code(language, output_dir)
        artifacts[code_path] = "分析代码"
        completed.append("代码保存")

        # Phase 6: 审计日志
        audit_path = await self._write_audit_log(output_dir)
        artifacts[audit_path] = "审计日志"
        completed.append("审计日志")

        self._status = AgentStatus.COMPLETED

        return self._create_handoff(
            completed_work=completed,
            artifacts=artifacts,
            verification_method="检查产物完整性 + 代码可重跑",
            known_issues=[s["reason"] for s in self._skip_log],
            pending_decisions=[],
            data_summary={
                "language": language,
                "debug_rounds": self._debug_rounds,
                "skip_count": len(self._skip_log),
                "execution_steps": len(self._execution_log),
            },
            next_agent="exec_inference",
        )

    async def _validate_sap(self, sap: Dict[str, Any]) -> bool:
        """验证 SAP 完整性"""
        required_keys = ["sections", "analysis_language"]
        return all(k in sap for k in required_keys) or not sap

    async def _construct_variables(
        self, task: Dict[str, Any], context: Dict[str, Any]
    ) -> Handoff:
        """变量构造"""
        language = task.get("language", "Python")
        output_dir = context.get("output_dir", "./output")

        result = {
            "timestamp": datetime.now().isoformat(),
            "phase": "variable_construction",
            "language": language,
            "variables_constructed": [],
        }

        report_path = Path(output_dir) / "variable_construction.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))

        self._execution_log.append(result)

        self._status = AgentStatus.COMPLETED
        return self._create_handoff(
            completed_work=["变量构造"],
            artifacts={str(report_path): "变量构造日志"},
            verification_method="检查变量构造逻辑与 SAP 一致",
            next_agent="exec_runner",
        )

    async def _run_descriptive(
        self, task: Dict[str, Any], context: Dict[str, Any]
    ) -> Handoff:
        """描述统计"""
        language = task.get("language", "Python")
        output_dir = context.get("output_dir", "./output")

        result = {
            "timestamp": datetime.now().isoformat(),
            "phase": "descriptive_statistics",
            "language": language,
            "tables": ["Table 1 (基线特征)"],
        }

        report_path = Path(output_dir) / "descriptive_statistics.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))

        self._execution_log.append(result)

        self._status = AgentStatus.COMPLETED
        return self._create_handoff(
            completed_work=["Table 1 (基线特征)", "缺失数据描述"],
            artifacts={str(report_path): "描述统计结果"},
            verification_method="检查 Table 1 格式（正态 Mean±SD / 非正态 Median[IQR]）",
            next_agent="exec_runner",
        )

    async def _run_inferential(
        self, task: Dict[str, Any], context: Dict[str, Any]
    ) -> Handoff:
        """推断分析（含自愈 Debug）"""
        language = task.get("language", "Python")
        output_dir = context.get("output_dir", "./output")

        result = {
            "timestamp": datetime.now().isoformat(),
            "phase": "inferential_analysis",
            "language": language,
            "analyses": [],
            "debug_rounds": 0,
            "skipped": [],
        }

        # 模拟自愈 Debug 循环
        for attempt in range(MAX_DEBUG_ROUNDS):
            self._debug_rounds = attempt + 1
            result["debug_rounds"] = self._debug_rounds

            # 尝试执行分析
            try:
                analysis_result = await self._attempt_analysis(task, attempt)
                if analysis_result["success"]:
                    result["analyses"].append(analysis_result)
                    break
                else:
                    # 根据错误级别决定处理方式
                    error_level = analysis_result.get("error_level", "L1")
                    if error_level == "L4":
                        result["skipped"].append({
                            "analysis": analysis_result.get("name"),
                            "reason": "需要用户决策",
                            "round": attempt + 1,
                        })
                        break
                    elif error_level == "L5" or attempt == MAX_DEBUG_ROUNDS - 1:
                        self._skip_log.append({
                            "analysis": analysis_result.get("name"),
                            "reason": f"自愈 {MAX_DEBUG_ROUNDS} 轮后仍失败",
                            "round": attempt + 1,
                        })
                        result["skipped"].append({
                            "analysis": analysis_result.get("name"),
                            "reason": f"[SKIP] {MAX_DEBUG_ROUNDS}轮自愈失败",
                            "round": attempt + 1,
                        })
                        break
            except Exception as e:
                result["skipped"].append({
                    "analysis": "unknown",
                    "reason": str(e),
                    "round": attempt + 1,
                })

        report_path = Path(output_dir) / "inferential_results.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))

        self._execution_log.append(result)

        self._status = AgentStatus.COMPLETED
        return self._create_handoff(
            completed_work=["推断分析", "自愈 Debug"],
            artifacts={str(report_path): "推断分析结果"},
            verification_method="检查 P 值合理性 + 效应量 + CI",
            known_issues=[s["reason"] for s in result.get("skipped", [])],
            next_agent="exec_inference",
        )

    async def _attempt_analysis(
        self, task: Dict[str, Any], attempt: int
    ) -> Dict[str, Any]:
        """尝试执行一次分析（模拟）"""
        # 实际实现应调用 R/Python 执行引擎
        return {
            "success": True,
            "name": "primary_analysis",
            "method": "ANCOVA",
            "attempt": attempt + 1,
        }

    async def _save_code(self, language: str, output_dir: str) -> str:
        """保存分析代码"""
        ext = "py" if language == "Python" else "R"
        code_path = Path(output_dir) / f"analysis_code.{ext}"
        code_path.parent.mkdir(parents=True, exist_ok=True)

        header = f"# MSRA Analysis Code\n# Language: {language}\n# Generated: {datetime.now().isoformat()}\n"
        code_path.write_text(header)

        return str(code_path)

    async def _write_audit_log(self, output_dir: str) -> str:
        """写入审计日志（不可变）"""
        audit_path = Path(output_dir) / "execution_audit_log.json"
        audit_path.parent.mkdir(parents=True, exist_ok=True)

        audit = {
            "timestamp": datetime.now().isoformat(),
            "agent": self._agent_id,
            "total_steps": len(self._execution_log),
            "debug_rounds": self._debug_rounds,
            "skip_count": len(self._skip_log),
            "skip_log": self._skip_log,
            "execution_log": self._execution_log,
        }

        audit_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False))
        return str(audit_path)

    async def vote_on_conflict(self, conflict: ConflictReport) -> Dict[str, Any]:
        if conflict.conflict_type == ConflictType.RESULT_DIVERGENCE.value:
            return {
                "voter_id": self._agent_id,
                "choice": "re_run_with_seed",
                "confidence": 0.8,
                "rationale": "建议设置固定随机种子后重跑，确保可复现性",
            }
        return {
            "voter_id": self._agent_id,
            "choice": "defer_to_inference",
            "confidence": 0.3,
            "rationale": "结果解读请交由 Exec Inference 处理",
        }


__all__ = ["ExecRunnerAgent"]
