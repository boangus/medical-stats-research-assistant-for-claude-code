"""
MSRA Quality Gate Runner — 门闸执行器

统一的门闸执行接口，支持 Skill 模式和子 Agent 模式。

运行模式:
- MODE_SKILL (默认): 生成检查清单 prompt，由 LLM 执行检查
- MODE_AGENT: 通过 HybridModeBridge 启动独立 QC Inspector Agent
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class GateType(str, Enum):
    """门闸类型枚举"""
    DATA_QUALITY = "data_quality"          # Gate 1.5
    SAP_QUALITY = "sap_quality"            # Gate 2.5
    RESULTS_QUALITY = "results_quality"    # Gate 3.5


class GateVerdict(str, Enum):
    """门闸判定结果"""
    PASS = "PASS"              # 全部通过
    CONDITIONAL = "CONDITIONAL"  # 条件通过（1-2项未过，非关键项）
    BLOCKED = "BLOCKED"        # 阻断（3+项未过或关键项未过）


class RunMode(str, Enum):
    """执行模式"""
    SKILL = "skill"    # LLM 按检查清单执行
    AGENT = "agent"    # 独立 QC Inspector Agent 执行（通过 HybridModeBridge）


@dataclass
class CheckItemResult:
    """单个检查项结果"""
    item_id: str
    name: str
    is_key: bool
    status: str  # PASS / FAIL / N/A / SKIP
    evidence: str = ""
    notes: str = ""


@dataclass
class GateResult:
    """门闸执行结果"""
    gate_type: GateType
    study_id: str
    verdict: GateVerdict
    total_items: int
    passed_items: int
    failed_items: int
    key_items_status: str  # "all_pass" 或 "item_N_failed"
    check_results: List[CheckItemResult] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    mode: RunMode = RunMode.SKILL

    @property
    def pass_rate(self) -> float:
        return self.passed_items / self.total_items if self.total_items > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate_type": self.gate_type.value,
            "study_id": self.study_id,
            "verdict": self.verdict.value,
            "total_items": self.total_items,
            "passed_items": self.passed_items,
            "failed_items": self.failed_items,
            "key_items_status": self.key_items_status,
            "pass_rate": f"{self.pass_rate:.1%}",
            "risks": self.risks,
            "timestamp": self.timestamp,
            "mode": self.mode.value,
            "check_results": [
                {
                    "item_id": cr.item_id,
                    "name": cr.name,
                    "is_key": cr.is_key,
                    "status": cr.status,
                    "evidence": cr.evidence,
                    "notes": cr.notes,
                }
                for cr in self.check_results
            ],
        }


@dataclass
class GateDefinition:
    """门闸定义"""
    gate_type: GateType
    name: str
    stage_number: str
    total_items: int
    key_items: List[int]  # 关键项编号列表
    checklist_template: str  # Markdown 检查清单模板路径
    report_template: str     # 报告模板路径


# 门闸注册表
GATE_REGISTRY: Dict[GateType, GateDefinition] = {
    GateType.DATA_QUALITY: GateDefinition(
        gate_type=GateType.DATA_QUALITY,
        name="数据质量门闸 / Data Quality Gate",
        stage_number="1.5",
        total_items=9,
        key_items=[5, 6, 7, 9],
        checklist_template="shared/templates/quality-gates/data_quality_gate_report.md",
        report_template="shared/templates/quality-gates/data_quality_gate_report.md",
    ),
    GateType.SAP_QUALITY: GateDefinition(
        gate_type=GateType.SAP_QUALITY,
        name="SAP质量门闸 / SAP Quality Gate",
        stage_number="2.5",
        total_items=8,
        key_items=[4, 6, 8],
        checklist_template="shared/templates/quality-gates/sap_quality_gate_report.md",
        report_template="shared/templates/quality-gates/sap_quality_gate_report.md",
    ),
    GateType.RESULTS_QUALITY: GateDefinition(
        gate_type=GateType.RESULTS_QUALITY,
        name="结果质量门闸 / Results Quality Gate",
        stage_number="3.5",
        total_items=9,
        key_items=[1, 2, 7, 8, 9],
        checklist_template="shared/templates/quality-gates/results_quality_gate_report.md",
        report_template="shared/templates/quality-gates/results_quality_gate_report.md",
    ),
}


class GateRunner:
    """
    门闸执行器

    支持三种模式：
    - Skill模式：生成检查清单prompt供LLM执行
    - Agent模式：通过HybridModeBridge启动QC Inspector子Agent（可后台并行）
    - 预填模式：传入已有的check_results直接判定

    Usage:
        runner = GateRunner(study_id="MSRA-2026-001")

        # Skill模式（默认）— 生成prompt供LLM执行
        prompt = runner.generate_checklist(GateType.DATA_QUALITY, artifacts={...})

        # Agent模式 — 构造子Agent任务，可后台并行执行
        task_info = runner.build_agent_task(GateType.DATA_QUALITY, artifacts={...}, output_path="/tmp/report.md")

        # 预填模式 — 传入LLM已完成的检查结果，直接判定
        result = runner.run_gate(GateType.DATA_QUALITY, artifacts={}, mode=RunMode.SKILL, check_results=[...])
    """

    def __init__(self, study_id: str, project_root: Optional[str] = None):
        self.study_id = study_id
        self.project_root = Path(project_root) if project_root else Path.cwd()

    def get_gate_definition(self, gate_type: GateType) -> GateDefinition:
        """获取门闸定义"""
        if gate_type not in GATE_REGISTRY:
            raise ValueError(f"Unknown gate type: {gate_type}")
        return GATE_REGISTRY[gate_type]

    def generate_checklist(
        self,
        gate_type: GateType,
        artifacts: Dict[str, str],
    ) -> str:
        """
        生成门闸检查清单（Skill模式用）

        Args:
            gate_type: 门闸类型
            artifacts: 产物路径映射 {artifact_id: file_path}

        Returns:
            Markdown 格式的检查清单 prompt
        """
        gate_def = self.get_gate_definition(gate_type)

        artifact_section = "\n".join(
            f"- **{aid}**: `{path}`" for aid, path in artifacts.items()
        )

        key_items_str = ", ".join(str(i) for i in gate_def.key_items)

        prompt = f"""## 质量门闸检查 — {gate_def.name}

**研究编号**: {self.study_id}
**门闸阶段**: Stage {gate_def.stage_number}
**检查项数**: {gate_def.total_items} 项
**关键项**: 第 {key_items_str} 项（未通过强制阻断）

### 待检查产物

{artifact_section}

### 判定规则

- 全部通过 ({gate_def.total_items}/{gate_def.total_items}) → ✅ **PASS** → 进入下一阶段
- 条件通过 ({gate_def.total_items - 2}-{gate_def.total_items - 1}/{gate_def.total_items}) → ⚠️ **CONDITIONAL** → 记录风险后进入
- 阻断 (< {gate_def.total_items - 2}/{gate_def.total_items} 或关键项未通过) → ❌ **BLOCKED** → 退回前一阶段

### 检查清单模板

请参照 `{gate_def.report_template}` 执行逐项检查，输出完整的门闸报告。
"""
        return prompt

    def build_agent_task(
        self,
        gate_type: GateType,
        artifacts: Dict[str, str],
        output_path: str,
    ) -> Dict[str, Any]:
        """
        构造子 Agent 任务（Agent模式用）

        通过 HybridModeBridge 构造可独立执行的 QC Inspector 子 Agent 任务。
        Gate 检查可与下一阶段准备并行执行。

        Args:
            gate_type: 门闸类型
            artifacts: 产物路径映射 {artifact_id: file_path}
            output_path: 门闸报告输出路径

        Returns:
            子 Agent 任务描述 {task: SubAgentTask, prompt: str}
        """
        try:
            from agents.implementations.hybrid_mode_bridge import HybridModeBridge, SubAgentType
        except ImportError:
            raise RuntimeError(
                "HybridModeBridge not available. "
                "Ensure agents/ package is installed."
            )

        gate_def = self.get_gate_definition(gate_type)
        bridge = HybridModeBridge()

        # 构造包含检查清单的完整上下文
        checklist_prompt = self.generate_checklist(gate_type, artifacts)
        context = {
            "gate_type": gate_type.value,
            "gate_name": gate_def.name,
            "study_id": self.study_id,
            "checklist": checklist_prompt,
        }

        task = bridge.build_subagent_task(
            agent_type=SubAgentType.QC_INSPECTOR,
            input_files=artifacts,
            output_path=output_path,
            context=context,
            run_in_background=True,  # Gate 检查默认后台并行
        )

        return {"task": task, "prompt": task.prompt}

    def run_gate(
        self,
        gate_type: GateType,
        artifacts: Dict[str, str],
        mode: RunMode = RunMode.SKILL,
        check_results: Optional[List[CheckItemResult]] = None,
    ) -> GateResult:
        """
        执行门闸检查

        Args:
            gate_type: 门闸类型
            artifacts: 产物路径映射
            mode: 执行模式
            check_results: 预先完成的检查结果（Skill模式下由LLM填充）

        Returns:
            GateResult 门闸执行结果
        """
        gate_def = self.get_gate_definition(gate_type)

        if mode == RunMode.SKILL and check_results is None:
            # Skill模式：返回prompt，实际检查由LLM执行
            raise ValueError(
                "Skill mode requires check_results to be provided by LLM. "
                "Use generate_checklist() to get the prompt first."
            )

        if check_results is None:
            check_results = []

        # 统计结果
        passed = sum(1 for cr in check_results if cr.status == "PASS")
        failed = sum(1 for cr in check_results if cr.status == "FAIL")
        key_failed = [
            cr for cr in check_results
            if cr.is_key and cr.status == "FAIL"
        ]

        # 判定
        if failed == 0:
            verdict = GateVerdict.PASS
            key_status = "all_pass"
        elif len(key_failed) > 0:
            verdict = GateVerdict.BLOCKED
            key_status = f"item_{key_failed[0].item_id}_failed"
        elif failed <= 2:
            verdict = GateVerdict.CONDITIONAL
            key_status = "all_pass"
        else:
            verdict = GateVerdict.BLOCKED
            key_status = f"{failed}_items_failed"

        # 风险评估
        risks = []
        for cr in check_results:
            if cr.status == "FAIL":
                level = "关键" if cr.is_key else "一般"
                risks.append(f"[{level}] {cr.name}: {cr.notes or cr.evidence}")

        return GateResult(
            gate_type=gate_type,
            study_id=self.study_id,
            verdict=verdict,
            total_items=gate_def.total_items,
            passed_items=passed,
            failed_items=failed,
            key_items_status=key_status,
            check_results=check_results,
            risks=risks,
            mode=mode,
        )

    def load_gate_report(self, report_path: str) -> GateResult:
        """
        从文件加载门闸报告

        Args:
            report_path: 门闸报告JSON文件路径

        Returns:
            GateResult 门闸执行结果
        """
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        gate_type = GateType(data["gate_type"])
        check_results = [
            CheckItemResult(**cr) for cr in data.get("check_results", [])
        ]

        return GateResult(
            gate_type=gate_type,
            study_id=data["study_id"],
            verdict=GateVerdict(data["verdict"]),
            total_items=data["total_items"],
            passed_items=data["passed_items"],
            failed_items=data["failed_items"],
            key_items_status=data["key_items_status"],
            check_results=check_results,
            risks=data.get("risks", []),
            timestamp=data.get("timestamp", ""),
            mode=RunMode(data.get("mode", "skill")),
        )

    def save_gate_report(self, result: GateResult, output_path: str) -> str:
        """
        保存门闸报告到文件

        Args:
            result: 门闸执行结果
            output_path: 输出文件路径

        Returns:
            保存的文件路径
        """
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with open(output, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)

        logger.info("Gate report saved: %s (verdict=%s)", output, result.verdict.value)
        return str(output)
