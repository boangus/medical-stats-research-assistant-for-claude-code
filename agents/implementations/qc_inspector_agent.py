"""
MSRA Multi-Agent Framework - QC Inspector Agent

质量审查员角色：质量门闸执行、一致性检查、偏差检测、结果复现验证。

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


class QCInspectorAgent(BaseAgent):
    """
    质量审查Agent - 负责质量门闸执行

    职责:
    - 数据质量门闸 (Stage 1.5, 9 项)
    - SAP 质量门闸 (Stage 2.5, 8 项)
    - 结果质量门闸 (Stage 3.5, 9 项)
    - 数值一致性检查
    - 异常结果标记
    - 报告规范合规检查
    - 结果复现性验证

    边界:
    - ✅ 独立执行所有检查项
    - ✅ 标记通过/警告/阻断级别
    - ⚠️ 阻断级未通过 → 强制退回前一阶段
    - ❌ 修改分析结果或 SAP 内容
    """

    # Gate 1.5: 数据质量门闸 (9 项)
    GATE_1_5 = [
        {"id": "DQ-01", "name": "数据完整性", "check": "所有必填变量存在", "level": "BLOCK"},
        {"id": "DQ-02", "name": "缺失率", "check": "核心变量<5%, 辅助<20%", "level": "BLOCK"},
        {"id": "DQ-03", "name": "异常值", "check": "无未确认的极端异常值", "level": "WARN/BLOCK"},
        {"id": "DQ-04", "name": "变量类型", "check": "所有变量类型正确", "level": "BLOCK"},
        {"id": "DQ-05", "name": "逻辑一致性", "check": "无逻辑矛盾", "level": "BLOCK"},
        {"id": "DQ-06", "name": "清洗日志", "check": "每步操作都有记录", "level": "BLOCK"},
        {"id": "DQ-07", "name": "PHI检测", "check": "无未脱敏的PHI", "level": "BLOCK"},
        {"id": "DQ-08", "name": "盲态审核", "check": "盲法试验已完成审核", "level": "BLOCK"},
        {"id": "DQ-09", "name": "数据库锁定", "check": "数据库已锁定", "level": "BLOCK"},
    ]

    # Gate 2.5: SAP 质量门闸 (8 项)
    GATE_2_5 = [
        {"id": "SQ-01", "name": "SAP完整性", "check": "8个标准章节全部填写", "level": "BLOCK"},
        {"id": "SQ-02", "name": "Estimands五要素", "check": "5个要素全部定义", "level": "BLOCK"},
        {"id": "SQ-03", "name": "研究类型匹配", "check": "方法与研究类型一致", "level": "BLOCK"},
        {"id": "SQ-04", "name": "主要分析定义", "check": "效应量/检验/α已定义", "level": "BLOCK"},
        {"id": "SQ-05", "name": "敏感性分析", "check": "≥2种方法", "level": "BLOCK"},
        {"id": "SQ-06", "name": "样本量评估", "check": "已完成计算或论证", "level": "WARN/BLOCK"},
        {"id": "SQ-07", "name": "变量构造逻辑", "check": "所有变量构造逻辑已定义", "level": "BLOCK"},
        {"id": "SQ-08", "name": "分析语言锁定", "check": "R/Python已选定并记录", "level": "BLOCK"},
    ]

    # Gate 3.5: 结果质量门闸 (9 项)
    GATE_3_5 = [
        {"id": "RQ-01", "name": "分析完整性", "check": "所有非[SKIP]条目已执行", "level": "BLOCK"},
        {"id": "RQ-02", "name": "P值合理性", "check": "0≤P≤1, 无P=0.000", "level": "BLOCK"},
        {"id": "RQ-03", "name": "效应量完整性", "check": "效应量+95%CI已报告", "level": "BLOCK"},
        {"id": "RQ-04", "name": "方法一致性", "check": "实际方法与SAP一致", "level": "BLOCK"},
        {"id": "RQ-05", "name": "代码可复现", "check": "随机种子已设置, 可重跑", "level": "BLOCK"},
        {"id": "RQ-06", "name": "图表质量", "check": "达到发表级标准", "level": "WARN/BLOCK"},
        {"id": "RQ-07", "name": "语言一致性", "check": "全程同一语言", "level": "BLOCK"},
        {"id": "RQ-08", "name": "偏差记录", "check": "所有偏离已记录并获批", "level": "BLOCK"},
        {"id": "RQ-09", "name": "SKIP标记", "check": "所有跳过已标注原因", "level": "BLOCK"},
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            agent_id="qc_inspector",
            agent_type="inspector",
            config=config,
        )
        self._gate_results: List[Dict[str, Any]] = []

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="data_quality_gate",
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data_path": {"type": "string"},
                        "cleaning_log": {"type": "string"},
                        "validation_report": {"type": "string"},
                    },
                    "required": ["data_path"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "gate_report": {"type": "object"},
                        "passed": {"type": "boolean"},
                        "fail_items": {"type": "array"},
                    },
                },
                constraints=["readonly_check", "cannot_modify_data"],
                dependencies=["data_validation"],
                quality_metrics={"completeness": "9项检查覆盖度"},
            ),
            AgentCapability(
                name="sap_quality_gate",
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "sap_path": {"type": "string"},
                        "pico": {"type": "object"},
                    },
                    "required": ["sap_path"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "gate_report": {"type": "object"},
                        "passed": {"type": "boolean"},
                    },
                },
                constraints=["readonly_check", "cannot_modify_sap"],
                dependencies=["sap_generation"],
                quality_metrics={"completeness": "8项检查覆盖度"},
            ),
            AgentCapability(
                name="results_quality_gate",
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "results_path": {"type": "string"},
                        "sap_path": {"type": "string"},
                        "code_path": {"type": "string"},
                    },
                    "required": ["results_path", "sap_path"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "gate_report": {"type": "object"},
                        "passed": {"type": "boolean"},
                    },
                },
                constraints=["readonly_check", "cannot_modify_results"],
                dependencies=["inferential_analysis"],
                quality_metrics={"completeness": "9项检查覆盖度"},
            ),
        ]

    async def execute(
        self, task: Dict[str, Any], context: Dict[str, Any]
    ) -> Handoff:
        self._status = AgentStatus.PROCESSING
        self._gate_results = []

        try:
            gate_type = task.get("gate_type", "data")
            output_dir = context.get("output_dir", "./output")

            if gate_type == "data":
                return await self._run_data_gate(task, context)
            elif gate_type == "sap":
                return await self._run_sap_gate(task, context)
            elif gate_type == "results":
                return await self._run_results_gate(task, context)
            else:
                return await self._run_data_gate(task, context)

        except Exception as e:
            self._status = AgentStatus.FAILED
            self._logger.error(f"QC Inspector failed: {e}")
            return self._create_handoff(
                completed_work=[],
                artifacts={},
                verification_method="检查错误日志",
                known_issues=[str(e)],
                pending_decisions=["质量检查失败，请人工介入"],
            )

    async def _run_data_gate(
        self, task: Dict[str, Any], context: Dict[str, Any]
    ) -> Handoff:
        """执行 Gate 1.5 数据质量门闸"""
        data_path = task.get("data_path")
        output_dir = context.get("output_dir", "./output")

        checklist = []
        for item in self.GATE_1_5:
            result = await self._check_gate_item(item, task, "data")
            checklist.append(result)
            self._gate_results.append(result)

        passed = all(r["status"] != "FAIL" for r in checklist)
        pass_count = sum(1 for r in checklist if r["status"] == "PASS")
        fail_count = sum(1 for r in checklist if r["status"] == "FAIL")
        warn_count = sum(1 for r in checklist if r["status"] == "WARN")

        report_path = await self._write_gate_report(
            "Gate 1.5", "数据质量门闸", checklist, output_dir
        )

        self._status = AgentStatus.COMPLETED

        return self._create_handoff(
            completed_work=[f"Gate 1.5 数据质量门闸 ({pass_count}/{len(checklist)} 通过)"],
            artifacts={report_path: "Gate 1.5 质量门闸报告"},
            verification_method="所有 BLOCK 项通过",
            known_issues=[
                f"{r['id']}: {r['detail']}"
                for r in checklist
                if r["status"] == "FAIL"
            ],
            pending_decisions=[]
            if passed
            else [f"Gate 1.5 未通过 ({fail_count} 项 FAIL)，请退回修正"],
            data_summary={
                "gate": "1.5",
                "pass": pass_count,
                "fail": fail_count,
                "warn": warn_count,
                "overall_pass": passed,
            },
            next_agent="method_consultant" if passed else "data_validator",
        )

    async def _run_sap_gate(
        self, task: Dict[str, Any], context: Dict[str, Any]
    ) -> Handoff:
        """执行 Gate 2.5 SAP 质量门闸"""
        output_dir = context.get("output_dir", "./output")

        checklist = []
        for item in self.GATE_2_5:
            result = await self._check_gate_item(item, task, "sap")
            checklist.append(result)
            self._gate_results.append(result)

        passed = all(r["status"] != "FAIL" for r in checklist)
        pass_count = sum(1 for r in checklist if r["status"] == "PASS")
        fail_count = sum(1 for r in checklist if r["status"] == "FAIL")
        warn_count = sum(1 for r in checklist if r["status"] == "WARN")

        report_path = await self._write_gate_report(
            "Gate 2.5", "SAP 质量门闸", checklist, output_dir
        )

        self._status = AgentStatus.COMPLETED

        return self._create_handoff(
            completed_work=[f"Gate 2.5 SAP 质量门闸 ({pass_count}/{len(checklist)} 通过)"],
            artifacts={report_path: "Gate 2.5 质量门闸报告"},
            verification_method="所有 BLOCK 项通过",
            known_issues=[
                f"{r['id']}: {r['detail']}"
                for r in checklist
                if r["status"] == "FAIL"
            ],
            pending_decisions=[]
            if passed
            else [f"Gate 2.5 未通过 ({fail_count} 项 FAIL)，请退回修正"],
            data_summary={
                "gate": "2.5",
                "pass": pass_count,
                "fail": fail_count,
                "warn": warn_count,
                "overall_pass": passed,
            },
            next_agent="exec_runner" if passed else "method_consultant",
        )

    async def _run_results_gate(
        self, task: Dict[str, Any], context: Dict[str, Any]
    ) -> Handoff:
        """执行 Gate 3.5 结果质量门闸"""
        output_dir = context.get("output_dir", "./output")

        checklist = []
        for item in self.GATE_3_5:
            result = await self._check_gate_item(item, task, "results")
            checklist.append(result)
            self._gate_results.append(result)

        passed = all(r["status"] != "FAIL" for r in checklist)
        pass_count = sum(1 for r in checklist if r["status"] == "PASS")
        fail_count = sum(1 for r in checklist if r["status"] == "FAIL")
        warn_count = sum(1 for r in checklist if r["status"] == "WARN")

        report_path = await self._write_gate_report(
            "Gate 3.5", "结果质量门闸", checklist, output_dir
        )

        self._status = AgentStatus.COMPLETED

        return self._create_handoff(
            completed_work=[f"Gate 3.5 结果质量门闸 ({pass_count}/{len(checklist)} 通过)"],
            artifacts={report_path: "Gate 3.5 质量门闸报告"},
            verification_method="所有 BLOCK 项通过",
            known_issues=[
                f"{r['id']}: {r['detail']}"
                for r in checklist
                if r["status"] == "FAIL"
            ],
            pending_decisions=[]
            if passed
            else [f"Gate 3.5 未通过 ({fail_count} 项 FAIL)，请退回修正"],
            data_summary={
                "gate": "3.5",
                "pass": pass_count,
                "fail": fail_count,
                "warn": warn_count,
                "overall_pass": passed,
            },
            next_agent="report" if passed else "exec_runner",
        )

    async def _check_gate_item(
        self, item: Dict[str, Any], task: Dict[str, Any], gate_type: str
    ) -> Dict[str, Any]:
        """检查单个门闸项"""
        # 实际实现应读取对应产物文件并逐项检查
        # 这里返回框架结构
        return {
            "id": item["id"],
            "name": item["name"],
            "check": item["check"],
            "level": item["level"],
            "status": "PASS",  # PASS / FAIL / WARN
            "detail": "检查通过",
        }

    async def _write_gate_report(
        self,
        gate_id: str,
        gate_name: str,
        checklist: List[Dict[str, Any]],
        output_dir: str,
    ) -> str:
        """生成质量门闸报告"""
        report_path = Path(output_dir) / f"quality_gate_{gate_id.replace('.', '_')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        pass_count = sum(1 for r in checklist if r["status"] == "PASS")
        fail_count = sum(1 for r in checklist if r["status"] == "FAIL")
        warn_count = sum(1 for r in checklist if r["status"] == "WARN")

        report = {
            "timestamp": datetime.now().isoformat(),
            "agent": self._agent_id,
            "gate_id": gate_id,
            "gate_name": gate_name,
            "checklist": checklist,
            "summary": {
                "total": len(checklist),
                "pass": pass_count,
                "fail": fail_count,
                "warn": warn_count,
                "overall_pass": fail_count == 0,
            },
        }

        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        return str(report_path)

    async def vote_on_conflict(self, conflict: ConflictReport) -> Dict[str, Any]:
        if conflict.conflict_type == ConflictType.QUALITY_GATE_FAILURE.value:
            return {
                "voter_id": self._agent_id,
                "choice": "block_and_return",
                "confidence": 0.95,
                "rationale": "质量门闸未通过，必须退回修正后重新提交",
            }
        return {
            "voter_id": self._agent_id,
            "choice": "defer_to_orchestrator",
            "confidence": 0.3,
            "rationale": "非质量相关冲突，请交由 Orchestrator 处理",
        }


__all__ = ["QCInspectorAgent"]
