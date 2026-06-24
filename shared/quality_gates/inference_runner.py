"""
MSRA Exec Inference Runner — 独立推断验证模块

将 analysis-exec Phase 7-9 的推断检验封装为可通过 HybridModeBridge 启动的独立子 Agent。
实现 Generator-Evaluator 独立比对。

Usage:
    from shared.quality_gates.inference_runner import InferenceRunner

    runner = InferenceRunner(study_id="MSRA-2026-001")

    # Skill模式 — 生成prompt供LLM执行
    prompt = runner.generate_checklist(results_dir="/path/to/results", sap_path="/path/to/sap.md")

    # Agent模式 — 构造子Agent任务
    task_info = runner.build_agent_task(
        results_dir="/path/to/results",
        sap_path="/path/to/sap.md",
        output_path="/path/to/inference_report.md",
    )
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# 13项质量清单（与 exec_inference_agent.py 一致）
QUALITY_CHECKLIST = [
    {"id": 1, "name": "P值合理性", "name_en": "P-value Plausibility",
     "check": "0≤P≤1, 无P=0.000（应为<0.001）", "is_key": True},
    {"id": 2, "name": "效应量+CI", "name_en": "Effect Size + CI",
     "check": "主要效应量 + 95% CI 已报告", "is_key": True},
    {"id": 3, "name": "方法一致性", "name_en": "Method Consistency",
     "check": "实际方法与 SAP 一致", "is_key": True},
    {"id": 4, "name": "变量名一致性", "name_en": "Variable Name Consistency",
     "check": "变量名与标准化清单一致", "is_key": False},
    {"id": 5, "name": "样本量一致性", "name_en": "Sample Size Consistency",
     "check": "样本量与数据画像一致", "is_key": True},
    {"id": 6, "name": "P值跨表一致", "name_en": "Cross-table P-value Consistency",
     "check": "表格P值与正文一致", "is_key": True},
    {"id": 7, "name": "图表注释一致", "name_en": "Figure-Table Annotation Consistency",
     "check": "图表注释与表格一致", "is_key": False},
    {"id": 8, "name": "SKIP标注", "name_en": "SKIP Annotation",
     "check": "[SKIP] 项已标注原因", "is_key": False},
    {"id": 9, "name": "偏差记录", "name_en": "Deviation Documentation",
     "check": "偏离已记录并获批", "is_key": True},
    {"id": 10, "name": "随机种子", "name_en": "Random Seed",
     "check": "随机种子已设置", "is_key": False},
    {"id": 11, "name": "语言一致性", "name_en": "Language Consistency",
     "check": "全程R或Python", "is_key": True},
    {"id": 12, "name": "加权一致性", "name_en": "Weight Consistency",
     "check": "加权方案一致性", "is_key": False},
    {"id": 13, "name": "可复现性", "name_en": "Reproducibility",
     "check": "代码可重跑（复现验证通过）", "is_key": True},
]


@dataclass
class ChecklistResult:
    """单个检查项结果"""
    item_id: int
    name: str
    is_key: bool
    status: str  # PASS / FAIL / WARN / N/A
    detail: str = ""


@dataclass
class InferenceReport:
    """推断验证报告"""
    study_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checklist_results: List[ChecklistResult] = field(default_factory=list)
    ge_discrepancies: List[str] = field(default_factory=list)
    overall_pass: bool = False

    @property
    def pass_count(self) -> int:
        return sum(1 for r in self.checklist_results if r.status == "PASS")

    @property
    def fail_count(self) -> int:
        return sum(1 for r in self.checklist_results if r.status == "FAIL")

    @property
    def key_fail_count(self) -> int:
        return sum(1 for r in self.checklist_results if r.is_key and r.status == "FAIL")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "study_id": self.study_id,
            "timestamp": self.timestamp,
            "overall_pass": self.overall_pass,
            "pass_count": self.pass_count,
            "fail_count": self.fail_count,
            "key_fail_count": self.key_fail_count,
            "ge_discrepancies": self.ge_discrepancies,
            "checklist": [
                {
                    "id": r.item_id,
                    "name": r.name,
                    "is_key": r.is_key,
                    "status": r.status,
                    "detail": r.detail,
                }
                for r in self.checklist_results
            ],
        }


class InferenceRunner:
    """
    Exec Inference 独立推断验证执行器

    将 analysis-exec Phase 7-9 的推断检验封装为独立模块，支持：
    - Skill模式：生成13项质量清单prompt供LLM执行
    - Agent模式：通过HybridModeBridge构造Exec Inference子Agent任务
    - Generator-Evaluator比对：独立验证Exec Runner的输出
    """

    def __init__(self, study_id: str):
        self.study_id = study_id

    def generate_checklist(
        self,
        results_dir: str,
        sap_path: Optional[str] = None,
    ) -> str:
        """
        生成推断验证检查清单（Skill模式用）

        Args:
            results_dir: 分析结果目录
            sap_path: SAP文档路径

        Returns:
            Markdown 格式的检查清单 prompt
        """
        sap_section = f"- **SAP文档**: `{sap_path}`" if sap_path else "- **SAP文档**: 未提供"

        checklist_lines = []
        for item in QUALITY_CHECKLIST:
            key_marker = "🔑 " if item["is_key"] else ""
            checklist_lines.append(
                f"| {item['id']} | {key_marker}{item['name']} | {item['check']} |"
            )

        checklist_table = "\n".join(checklist_lines)

        prompt = f"""## Exec Inference 独立推断验证 — {self.study_id}

**阶段**: Stage 3 Phase 7-9 (推断检验 + Generator-Evaluator比对)
**角色**: 独立推断验证员（不看 Exec Runner 的推理过程）

### 约束

- ✅ 独立执行假设检验
- ✅ 标记P值异常、效应量缺失等问题
- ✅ Generator-Evaluator比对（你的推断 vs Exec Runner的推断）
- ❌ 修改 Exec Runner 生成的代码或结果
- ❌ 自行选择统计方法（必须遵循SAP）

### 输入产物

- **分析结果目录**: `{results_dir}`
{sap_section}

### 13项质量清单

| # | 检查项 | 检查内容 |
|---|--------|---------|
{checklist_table}

### 判定规则

- 8项以上通过 + 关键项全通过 → ✅ **PASS**
- 6-7项通过 + 关键项全通过 → ⚠️ **WARN**（记录风险）
- 关键项未通过或<6项通过 → ❌ **FAIL**（退回Stage 3）

### Generator-Evaluator比对

独立重算主要分析结果，与Exec Runner的输出比对：
1. 点估计是否一致（允许浮点误差）
2. P值是否一致（允许舍入误差）
3. 置信区间是否一致
4. 不一致项记录为discrepancies

### 期望输出

按以下格式输出推断验证报告：

## Handoff: Exec Inference

### 已完成工作
- 独立假设检验
- 13项质量清单检查
- Generator-Evaluator比对

### 质量清单结果
| # | 检查项 | 关键 | 结果 | 说明 |
|---|--------|------|------|------|
| 1 | P值合理性 | 🔑 | PASS/FAIL/WARN | ... |

### Generator-Evaluator比对
- 一致性: [是/否]
- 差异项: [列表]

### 产物路径
- 推断验证报告: [路径]

### 总体结论
- 通过: X 项
- 失败: Y 项
- 关键项失败: Z 项
- 结论: ✅ 通过 / ⚠️ 条件通过 / ❌ 退回修正
"""
        return prompt

    def build_agent_task(
        self,
        results_dir: str,
        sap_path: str,
        output_path: str,
    ) -> Dict[str, Any]:
        """
        构造子 Agent 任务（Agent模式用）

        通过 HybridModeBridge 构造可独立执行的 Exec Inference 子 Agent 任务。
        推断检验与报告生成可并行执行。

        Args:
            results_dir: 分析结果目录
            sap_path: SAP文档路径
            output_path: 推断验证报告输出路径

        Returns:
            子 Agent 任务描述 {task: SubAgentTask, prompt: str}
        """
        try:
            from agents.implementations.hybrid_mode_bridge import (
                HybridModeBridge, SubAgentType
            )
        except ImportError:
            raise RuntimeError(
                "HybridModeBridge not available. "
                "Ensure agents/ package is installed."
            )

        bridge = HybridModeBridge()

        checklist_prompt = self.generate_checklist(results_dir, sap_path)
        context = {
            "study_id": self.study_id,
            "checklist": checklist_prompt,
            "mode": "independent_verification",
        }

        task = bridge.build_subagent_task(
            agent_type=SubAgentType.EXEC_INFERENCE,
            input_files={
                "分析结果目录": results_dir,
                "SAP文档": sap_path,
            },
            output_path=output_path,
            context=context,
            run_in_background=True,  # 推断检验可与报告准备并行
        )

        return {"task": task, "prompt": task.prompt}

    def evaluate_results(
        self,
        checklist_results: List[ChecklistResult],
        ge_discrepancies: Optional[List[str]] = None,
    ) -> InferenceReport:
        """
        评估推断验证结果

        Args:
            checklist_results: 13项检查结果
            ge_discrepancies: Generator-Evaluator差异列表

        Returns:
            InferenceReport 推断验证报告
        """
        key_failures = [r for r in checklist_results if r.is_key and r.status == "FAIL"]
        total_pass = sum(1 for r in checklist_results if r.status == "PASS")

        if len(key_failures) > 0:
            overall_pass = False
        elif total_pass >= 8:
            overall_pass = True
        elif total_pass >= 6:
            overall_pass = True  # WARN but pass
        else:
            overall_pass = False

        return InferenceReport(
            study_id=self.study_id,
            checklist_results=checklist_results,
            ge_discrepancies=ge_discrepancies or [],
            overall_pass=overall_pass,
        )
