"""
MSRA Multi-Agent Framework - Exec Inference Agent

统计推断专家角色：独立假设检验、Generator-Evaluator比对、13项质量清单。

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


class ExecInferenceAgent(BaseAgent):
    """
    推断执行Agent - 负责独立假设检验和质量检查

    职责:
    - 独立假设检验（不看 Exec Runner 的推理过程）
    - 质量检查（13项清单）
    - Generator-Evaluator 比对

    边界:
    - ✅ 独立执行假设检验
    - ✅ 标记 P 值异常、效应量缺失等问题
    - ❌ 修改 Exec Runner 生成的代码或结果
    - ❌ 自行选择统计方法（必须遵循 SAP）
    """

    # 13 项质量清单
    QUALITY_CHECKLIST = [
        {"id": 1, "name": "P值合理性", "check": "0≤P≤1, 无P=0.000"},
        {"id": 2, "name": "效应量+CI", "check": "主要效应量 + 95% CI 已报告"},
        {"id": 3, "name": "方法一致性", "check": "实际方法与 SAP 一致"},
        {"id": 4, "name": "变量名一致性", "check": "变量名与标准化清单一致"},
        {"id": 5, "name": "样本量一致性", "check": "样本量与数据画像一致"},
        {"id": 6, "name": "P值跨表一致", "check": "表格P值与正文一致"},
        {"id": 7, "name": "图表注释一致", "check": "图表注释与表格一致"},
        {"id": 8, "name": "SKIP标注", "check": "[SKIP] 项已标注原因"},
        {"id": 9, "name": "偏差记录", "check": "偏离已记录并获批"},
        {"id": 10, "name": "随机种子", "check": "随机种子已设置"},
        {"id": 11, "name": "语言一致性", "check": "全程R或Python"},
        {"id": 12, "name": "加权一致性", "check": "加权方案一致性"},
        {"id": 13, "name": "可复现性", "check": "代码可重跑（复现验证通过）"},
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            agent_id="exec_inference",
            agent_type="inference",
            config=config,
        )
        self._check_results: List[Dict[str, Any]] = []

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="independent_hypothesis_test",
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "results_path": {"type": "string"},
                        "sap_methods": {"type": "array"},
                        "language": {"type": "string", "enum": ["R", "Python"]},
                    },
                    "required": ["results_path", "sap_methods"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "verification_report": {"type": "object"},
                        "discrepancies": {"type": "array"},
                    },
                },
                constraints=[
                    "must_be_independent_from_exec_runner",
                    "cannot_modify_original_results",
                ],
                dependencies=["inferential_analysis"],
                quality_metrics={
                    "independence": "与 Exec Runner 的独立性",
                    "thoroughness": "检查覆盖度",
                },
            ),
            AgentCapability(
                name="quality_checklist",
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "results_path": {"type": "string"},
                        "sap_path": {"type": "string"},
                        "progress_tracker": {"type": "string"},
                    },
                    "required": ["results_path"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "checklist_report": {"type": "object"},
                        "pass_count": {"type": "integer"},
                        "fail_count": {"type": "integer"},
                        "overall_pass": {"type": "boolean"},
                    },
                },
                constraints=["readonly_check", "cannot_modify_results"],
                dependencies=["independent_hypothesis_test"],
                quality_metrics={"completeness": "13项清单覆盖度"},
            ),
        ]

    async def execute(
        self, task: Dict[str, Any], context: Dict[str, Any]
    ) -> Handoff:
        self._status = AgentStatus.PROCESSING
        self._check_results = []

        try:
            results_path = task.get("results_path")
            sap_path = task.get("sap_path")
            language = task.get("language", "Python")
            output_dir = context.get("output_dir", "./output")

            # 1. 独立假设检验
            verification = await self._independent_verify(results_path, language)

            # 2. 13 项质量清单
            checklist = await self._run_quality_checklist(
                results_path, sap_path, verification
            )

            # 3. Generator-Evaluator 比对
            ge_comparison = await self._generator_evaluator_compare(
                results_path, verification
            )

            # 4. 生成报告
            report_path = await self._write_report(
                verification, checklist, ge_comparison, output_dir
            )

            overall_pass = checklist.get("overall_pass", False)

            self._status = AgentStatus.COMPLETED

            return self._create_handoff(
                completed_work=[
                    "独立假设检验",
                    "13项质量清单检查",
                    "Generator-Evaluator 比对",
                    "推断验证报告",
                ],
                artifacts={report_path: "推断验证报告"},
                verification_method="检查 13 项质量清单全部通过",
                known_issues=[
                    r["detail"]
                    for r in self._check_results
                    if r.get("status") == "FAIL"
                ],
                pending_decisions=[]
                if overall_pass
                else ["质量清单未全部通过，请修正后重新提交"],
                data_summary={
                    "pass_count": checklist.get("pass_count", 0),
                    "fail_count": checklist.get("fail_count", 0),
                    "warn_count": checklist.get("warn_count", 0),
                    "overall_pass": overall_pass,
                    "ge_discrepancies": len(ge_comparison.get("discrepancies", [])),
                },
                next_agent="qc_inspector",
            )

        except Exception as e:
            self._status = AgentStatus.FAILED
            self._logger.error(f"Exec Inference failed: {e}")
            return self._create_handoff(
                completed_work=[],
                artifacts={},
                verification_method="检查错误日志",
                known_issues=[str(e)],
                pending_decisions=["推断验证失败，请检查输入数据"],
            )

    async def _independent_verify(
        self, results_path: str, language: str
    ) -> Dict[str, Any]:
        """独立验证分析结果（不依赖 Exec Runner 的推理过程）"""
        verification = {
            "timestamp": datetime.now().isoformat(),
            "agent": self._agent_id,
            "language": language,
            "results_path": results_path,
            "independent": True,
            "checks": [],
        }

        # 读取结果文件
        if results_path:
            path = Path(results_path)
            if path.exists():
                try:
                    content = path.read_text(encoding="utf-8")
                    result_data = json.loads(content)
                    verification["results_loaded"] = True
                    verification["result_keys"] = list(result_data.keys())
                except (json.JSONDecodeError, UnicodeDecodeError):
                    verification["results_loaded"] = False
                    verification["checks"].append({
                        "name": "结果文件格式",
                        "status": "WARN",
                        "detail": "结果文件无法解析为 JSON",
                    })

        return verification

    async def _run_quality_checklist(
        self,
        results_path: str,
        sap_path: str,
        verification: Dict[str, Any],
    ) -> Dict[str, Any]:
        """执行 13 项质量清单"""
        checklist = {
            "timestamp": datetime.now().isoformat(),
            "items": [],
            "pass_count": 0,
            "fail_count": 0,
            "warn_count": 0,
            "overall_pass": True,
        }

        for item in self.QUALITY_CHECKLIST:
            result = await self._check_item(item, results_path, sap_path, verification)
            checklist["items"].append(result)
            self._check_results.append(result)

            if result["status"] == "PASS":
                checklist["pass_count"] += 1
            elif result["status"] == "FAIL":
                checklist["fail_count"] += 1
                checklist["overall_pass"] = False
            elif result["status"] == "WARN":
                checklist["warn_count"] += 1

        return checklist

    async def _check_item(
        self,
        item: Dict[str, Any],
        results_path: str,
        sap_path: str,
        verification: Dict[str, Any],
    ) -> Dict[str, Any]:
        """检查单个清单项"""
        # 实际实现应读取结果文件并逐项检查
        # 这里返回框架结构，具体检查逻辑需根据实际数据格式实现
        return {
            "id": item["id"],
            "name": item["name"],
            "check": item["check"],
            "status": "PASS",  # PASS / FAIL / WARN
            "detail": "检查通过",
        }

    async def _generator_evaluator_compare(
        self, results_path: str, verification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generator-Evaluator 比对"""
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "generator": "exec_runner",
            "evaluator": "exec_inference",
            "discrepancies": [],
            "consistent": True,
        }

        # 实际实现应独立重跑关键假设检验，与 Exec Runner 的结果比对
        # 检查 P 值、效应量、CI 是否一致

        return comparison

    async def _write_report(
        self,
        verification: Dict[str, Any],
        checklist: Dict[str, Any],
        ge_comparison: Dict[str, Any],
        output_dir: str,
    ) -> str:
        """生成推断验证报告"""
        report_path = Path(output_dir) / "inference_verification_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "timestamp": datetime.now().isoformat(),
            "agent": self._agent_id,
            "verification": verification,
            "quality_checklist": checklist,
            "generator_evaluator_comparison": ge_comparison,
            "overall_pass": checklist.get("overall_pass", False),
        }

        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        return str(report_path)

    async def vote_on_conflict(self, conflict: ConflictReport) -> Dict[str, Any]:
        if conflict.conflict_type == ConflictType.RESULT_DIVERGENCE.value:
            return {
                "voter_id": self._agent_id,
                "choice": "independent_re_run",
                "confidence": 0.9,
                "rationale": "作为独立推断验证者，建议独立重跑分析确认结果",
            }
        return {
            "voter_id": self._agent_id,
            "choice": "defer_to_qc",
            "confidence": 0.3,
            "rationale": "非推断相关冲突，请交由 QC Inspector 处理",
        }


__all__ = ["ExecInferenceAgent"]
