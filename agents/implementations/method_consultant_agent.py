"""
MSRA Multi-Agent Framework - Method Consultant Agent

资深生物统计学家角色：EDA、Estimands定义、方法选择、SAP制定与审查。

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


class MethodConsultantAgent(BaseAgent):
    """
    方法顾问Agent - 负责统计分析计划制定

    职责:
    - 探索性数据分析 (EDA)
    - 估计目标定义 (ICH E9(R1) 五要素)
    - 统计方法选择决策树
    - SAP 撰写与审查
    - 样本量计算

    边界:
    - ✅ 独立完成 EDA → 生成 EDA 报告
    - ✅ 提供多种合理方法选项 → 等待用户选择
    - ❌ 在未讨论的情况下单方面选择统计方法
    - ❌ 跳过敏感性分析计划
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            agent_id="method_consultant",
            agent_type="consultant",
            config=config,
        )
        self._sap_sections: Dict[str, Any] = {}
        self._estimands: Dict[str, Any] = {}

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="eda_analysis",
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data_path": {"type": "string"},
                        "research_question": {"type": "string"},
                    },
                    "required": ["data_path"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "eda_report": {"type": "object"},
                        "distribution_plots": {"type": "array"},
                        "correlation_matrix": {"type": "object"},
                    },
                },
                constraints=["must_report_normality_test", "must_handle_missing"],
                dependencies=["data_validation"],
                quality_metrics={
                    "completeness": "EDA 覆盖度",
                    "correctness": "统计方法正确性",
                },
            ),
            AgentCapability(
                name="sap_generation",
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pico": {"type": "object"},
                        "eda_results": {"type": "object"},
                        "study_type": {
                            "type": "string",
                            "enum": ["rct", "observational", "diagnostic"],
                        },
                    },
                    "required": ["pico", "study_type"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "sap_document": {"type": "object"},
                        "estimands": {"type": "object"},
                        "analysis_methods": {"type": "array"},
                    },
                },
                constraints=["must_define_estimands", "must_include_sensitivity"],
                dependencies=["eda_analysis"],
                quality_metrics={
                    "completeness": "SAP 完整性",
                    "ich_e9r1_compliance": "ICH E9(R1) 合规性",
                },
            ),
            AgentCapability(
                name="sample_size_calculation",
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "effect_size": {"type": "number"},
                        "alpha": {"type": "number"},
                        "power": {"type": "number"},
                        "method": {"type": "string"},
                    },
                    "required": ["effect_size", "alpha", "power"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "required_n": {"type": "integer"},
                        "assumptions": {"type": "array"},
                        "sensitivity_table": {"type": "array"},
                    },
                },
                constraints=[],
                dependencies=[],
                quality_metrics={"accuracy": "样本量计算准确性"},
            ),
        ]

    async def execute(
        self, task: Dict[str, Any], context: Dict[str, Any]
    ) -> Handoff:
        self._status = AgentStatus.PROCESSING

        try:
            task_type = task.get("task_type", "full_planning")

            if task_type == "eda":
                return await self._run_eda(task, context)
            elif task_type == "sap":
                return await self._generate_sap(task, context)
            elif task_type == "sample_size":
                return await self._calculate_sample_size(task, context)
            else:
                return await self._full_planning(task, context)

        except Exception as e:
            self._status = AgentStatus.FAILED
            self._logger.error(f"Method Consultant execution failed: {e}")
            return self._create_handoff(
                completed_work=[],
                artifacts={},
                verification_method="检查错误日志",
                known_issues=[str(e)],
                pending_decisions=["是否重试或人工介入"],
            )

    async def _full_planning(
        self, task: Dict[str, Any], context: Dict[str, Any]
    ) -> Handoff:
        """完整分析计划流程：EDA → Estimands → SAP"""
        data_path = task.get("data_path")
        pico = task.get("pico", {})
        study_type = task.get("study_type", "observational")
        output_dir = context.get("output_dir", "./output")

        # 1. EDA
        eda_result = await self._perform_eda(data_path)

        # 2. 定义 Estimands
        estimands = await self._define_estimands(pico, study_type)

        # 3. 选择分析方法
        methods = await self._select_methods(study_type, eda_result, estimands)

        # 4. 生成 SAP
        sap_path = await self._write_sap(
            pico, estimands, methods, eda_result, output_dir
        )

        self._status = AgentStatus.COMPLETED

        return self._create_handoff(
            completed_work=[
                "探索性数据分析 (EDA)",
                "估计目标定义 (Estimands)",
                "统计方法选择",
                "SAP 文档生成",
            ],
            artifacts={sap_path: "统计分析计划 (SAP)"},
            verification_method="检查 SAP 是否包含 ICH E9(R1) 五要素",
            known_issues=eda_result.get("warnings", []),
            pending_decisions=[
                "请确认分析方法选择",
                "请确认敏感性分析方案",
            ],
            data_summary={
                "study_type": study_type,
                "n_methods": len(methods),
                "sap_sections": list(self._sap_sections.keys()),
            },
            next_agent="exec_runner",
        )

    async def _perform_eda(self, data_path: str) -> Dict[str, Any]:
        """执行探索性数据分析"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "data_path": data_path,
            "distributions": {},
            "correlations": {},
            "missing_summary": {},
            "warnings": [],
        }

        path = Path(data_path) if data_path else None
        if path and path.exists():
            result["file_size"] = path.stat().st_size

        return result

    async def _define_estimands(
        self, pico: Dict[str, Any], study_type: str
    ) -> Dict[str, Any]:
        """定义 ICH E9(R1) 估计目标五要素"""
        estimands = {
            "population": pico.get("population", "待定义"),
            "treatment": pico.get("intervention", "待定义"),
            "endpoint": pico.get("outcome", "待定义"),
            "summary_measure": "待选择",
            "intercurrent_events": {
                "treatment_discontinuation": "待讨论",
                "rescue_medication": "待讨论",
                "death": "待讨论",
            },
        }
        self._estimands = estimands
        return estimands

    async def _select_methods(
        self, study_type: str, eda_result: Dict[str, Any], estimands: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """根据研究类型和数据特征选择分析方法"""
        method_tree = {
            "rct": [
                {"name": "ANCOVA", "priority": 1, "description": "协方差分析"},
                {"name": "MMRM", "priority": 2, "description": "混合模型重复测量"},
                {"name": "ITT", "priority": 1, "description": "意向治疗分析"},
            ],
            "observational": [
                {"name": "PSM", "priority": 1, "description": "倾向性评分匹配"},
                {"name": "IPTW", "priority": 2, "description": "逆概率加权"},
                {"name": "AIPW", "priority": 3, "description": "增强逆概率加权"},
            ],
            "diagnostic": [
                {"name": "ROC", "priority": 1, "description": "受试者工作特征"},
                {"name": "DeLong", "priority": 2, "description": "DeLong 检验"},
                {"name": "Bland-Altman", "priority": 3, "description": "Bland-Altman 一致性"},
            ],
        }
        return method_tree.get(study_type, method_tree["observational"])

    async def _write_sap(
        self,
        pico: Dict[str, Any],
        estimands: Dict[str, Any],
        methods: List[Dict[str, Any]],
        eda_result: Dict[str, Any],
        output_dir: str,
    ) -> str:
        """生成 SAP 文档"""
        output_path = Path(output_dir) / "sap_document.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        sap = {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "agent": self._agent_id,
            "sections": {
                "1_objectives": pico,
                "2_estimands": estimands,
                "3_analysis_methods": methods,
                "4_eda_summary": eda_result,
                "5_sensitivity_analysis": ["待定义"],
                "6_missing_data_strategy": "待讨论",
            },
            "analysis_language": "待锁定",
        }

        self._sap_sections = sap["sections"]
        output_path.write_text(json.dumps(sap, indent=2, ensure_ascii=False))
        return str(output_path)

    async def _run_eda(self, task: Dict[str, Any], context: Dict[str, Any]) -> Handoff:
        """单独执行 EDA"""
        data_path = task.get("data_path")
        eda_result = await self._perform_eda(data_path)

        output_dir = context.get("output_dir", "./output")
        report_path = Path(output_dir) / "eda_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(eda_result, indent=2, ensure_ascii=False))

        self._status = AgentStatus.COMPLETED
        return self._create_handoff(
            completed_work=["探索性数据分析 (EDA)"],
            artifacts={str(report_path): "EDA 报告"},
            verification_method="检查 EDA 报告完整性",
            next_agent="method_consultant",
        )

    async def _generate_sap(
        self, task: Dict[str, Any], context: Dict[str, Any]
    ) -> Handoff:
        """单独生成 SAP"""
        pico = task.get("pico", {})
        study_type = task.get("study_type", "observational")
        estimands = await self._define_estimands(pico, study_type)
        methods = await self._select_methods(study_type, {}, estimands)

        output_dir = context.get("output_dir", "./output")
        sap_path = await self._write_sap(pico, estimands, methods, {}, output_dir)

        self._status = AgentStatus.COMPLETED
        return self._create_handoff(
            completed_work=["估计目标定义", "统计方法选择", "SAP 文档生成"],
            artifacts={sap_path: "SAP 文档"},
            verification_method="检查 SAP 五要素完整性",
            next_agent="exec_runner",
        )

    async def _calculate_sample_size(
        self, task: Dict[str, Any], context: Dict[str, Any]
    ) -> Handoff:
        """样本量计算"""
        effect_size = task.get("effect_size", 0.5)
        alpha = task.get("alpha", 0.05)
        power = task.get("power", 0.8)

        result = {
            "effect_size": effect_size,
            "alpha": alpha,
            "power": power,
            "required_n": "需调用 shared/sample-size/ 计算",
            "assumptions": ["正态分布", "等方差"],
        }

        output_dir = context.get("output_dir", "./output")
        report_path = Path(output_dir) / "sample_size_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))

        self._status = AgentStatus.COMPLETED
        return self._create_handoff(
            completed_work=["样本量计算"],
            artifacts={str(report_path): "样本量报告"},
            verification_method="检查样本量计算假设",
            next_agent="exec_runner",
        )

    async def vote_on_conflict(self, conflict: ConflictReport) -> Dict[str, Any]:
        if conflict.conflict_type == ConflictType.METHOD_DISAGREEMENT.value:
            return {
                "voter_id": self._agent_id,
                "choice": conflict.resolution_suggestions[0]
                if conflict.resolution_suggestions
                else "consult_literature",
                "confidence": 0.85,
                "rationale": "作为统计方法专家，建议参考文献选择最稳健的方法",
            }
        return {
            "voter_id": self._agent_id,
            "choice": "defer_to_expert",
            "confidence": 0.3,
            "rationale": "此冲突类型不在我的专业范围内",
        }


__all__ = ["MethodConsultantAgent"]
