"""
MSRA Multi-Agent Framework - Hybrid Mode Bridge

混合模式桥接层：Skill 编排层调用独立子 Agent 的桥接机制。
实现模式 C（Skill + 子 Agent 混合模式）的核心调度逻辑。

Author: MSRA Team
Version: 1.0.0
"""

from __future__ import annotations

import json
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class SubAgentType(str, Enum):
    """可拆分为子 Agent 的角色类型"""
    QC_INSPECTOR = "qc_inspector"
    EXEC_INFERENCE = "exec_inference"
    DATA_VALIDATOR = "data_validator"
    METHOD_CONSULTANT = "method_consultant"


class AgentMode(str, Enum):
    """Agent 运行模式"""
    SKILL = "skill"          # 模式 A: Skill 调度（主对话内角色扮演）
    PYTHON = "python"        # 模式 B: Python Agent（独立进程）
    HYBRID = "hybrid"        # 模式 C: 混合模式（Skill + 子 Agent）


@dataclass
class SubAgentConfig:
    """子 Agent 配置"""
    agent_type: SubAgentType
    timeout: int = 300           # 超时阈值（秒）
    max_retries: int = 1         # 最大重试次数
    fallback_to_skill: bool = True  # 失败时降级到 Skill 模式
    run_in_background: bool = False # 是否后台并行运行


@dataclass
class SubAgentTask:
    """子 Agent 任务描述"""
    task_id: str
    agent_type: SubAgentType
    prompt: str                  # 角色定义 + 输入数据 + 期望输出格式
    input_files: Dict[str, str] = field(default_factory=dict)  # 描述 → 文件路径
    expected_output: str = ""    # 期望输出格式说明
    output_path: str = ""        # 输出文件路径
    timeout: int = 300
    run_in_background: bool = False


@dataclass
class SubAgentResult:
    """子 Agent 执行结果"""
    task_id: str
    agent_type: SubAgentType
    success: bool
    output_path: Optional[str] = None
    handoff: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    degraded: bool = False       # 是否降级到 Skill 模式


# ============================================================
# 各子 Agent 的 Prompt 模板
# ============================================================

AGENT_PROMPTS = {
    SubAgentType.QC_INSPECTOR: {
        "role": """你是 MSRA 的质量审查员（QC Inspector Agent）。你的职责是独立审查分析产物的质量。

**关键约束**：
- 你只审查产物文件，不修改任何文件
- 你不参与分析代码的生成过程
- 你必须严格按照检查清单逐项检查
- 检查结果分为 PASS / WARN / FAIL 三级""",
        "handoff_format": """请按以下格式输出结果：

## Handoff: QC Inspector

### 已完成工作
- [Gate 类型] 质量门闸检查：[X/Y 通过]

### 检查结果
| # | 检查项 | 结果 | 说明 |
|---|--------|------|------|
| 1 | ... | PASS/WARN/FAIL | ... |

### 产物路径
- 质量门闸报告: [路径]

### 总体结论
- 通过: X 项
- 警告: Y 项
- 阻断: Z 项
- 结论: ✅ 通过 / ❌ 退回修正""",
    },
    SubAgentType.EXEC_INFERENCE: {
        "role": """你是 MSRA 的统计推断专家（Exec Inference Agent）。你的职责是独立验证分析结果。

**关键约束**：
- 你独立于 Exec Runner 运行，看不到代码生成过程
- 你只审查产物（结果表、图表、代码），不修改
- 你必须执行 13 项质量清单
- 你执行独立假设检验，与 Exec Runner 的结果比对""",
        "handoff_format": """请按以下格式输出结果：

## Handoff: Exec Inference

### 已完成工作
- 独立假设检验
- 13 项质量清单检查
- Generator-Evaluator 比对

### 质量清单结果
| # | 检查项 | 结果 | 说明 |
|---|--------|------|------|
| 1 | P值合理性 | PASS/FAIL | ... |
...

### Generator-Evaluator 比对
- 一致性: [是/否]
- 差异项: [列表]

### 产物路径
- 推断验证报告: [路径]

### 总体结论
- 结论: ✅ 通过 / ❌ 需修正""",
    },
    SubAgentType.DATA_VALIDATOR: {
        "role": """你是 MSRA 的数据质量专家（Data Validator Agent）。你的职责是验证和清洗数据。

**关键约束**：
- 永远不自动清洗数据——先验证、再讨论、获批准后执行
- 静默删除数据绝对禁止
- 值规范化日志必须完整记录
- 盲法试验数据审核必须在盲态下进行""",
        "handoff_format": """请按以下格式输出结果：

## Handoff: Data Validator

### 已完成工作
- [列表]

### 产物路径
- [文件]: [路径]

### 数据摘要
- 记录数: X
- 变量数: Y
- 缺失率: Z%

### 待决策项
- [需要用户批准的清洗操作]""",
    },
    SubAgentType.METHOD_CONSULTANT: {
        "role": """你是 MSRA 的资深生物统计学家（Method Consultant Agent）。你的职责是制定统计分析计划。

**关键约束**：
- 提供多种合理方法选项，等待用户选择
- 必须定义 ICH E9(R1) 估计目标五要素
- 不能跳过敏感性分析计划
- 研究类型-方法必须匹配""",
        "handoff_format": """请按以下格式输出结果：

## Handoff: Method Consultant

### 已完成工作
- [列表]

### 产物路径
- SAP 文档: [路径]

### 分析方法
| 方法 | 优先级 | 说明 |
|------|--------|------|
| ... | ... | ... |

### 待决策项
- [需要用户确认的方法选择]""",
    },
}


# ============================================================
# 超时配置
# ============================================================

TIMEOUT_CONFIG = {
    SubAgentType.QC_INSPECTOR: 180,
    SubAgentType.EXEC_INFERENCE: 300,
    SubAgentType.DATA_VALIDATOR: 300,
    SubAgentType.METHOD_CONSULTANT: 240,
}


class HybridModeBridge:
    """
    混合模式桥接器

    负责在 Skill 编排层和子 Agent 之间建立调用通道。
    当子 Agent 不可用时，自动降级到 Skill 模式。
    """

    def __init__(self, mode: AgentMode = AgentMode.HYBRID):
        self._mode = mode
        self._task_history: List[SubAgentResult] = []

    @property
    def mode(self) -> AgentMode:
        return self._mode

    def build_subagent_task(
        self,
        agent_type: SubAgentType,
        input_files: Dict[str, str],
        output_path: str,
        context: Optional[Dict[str, Any]] = None,
        run_in_background: bool = False,
    ) -> SubAgentTask:
        """
        构造子 Agent 任务

        Args:
            agent_type: 子 Agent 类型
            input_files: 输入文件 {描述: 路径}
            output_path: 输出文件路径
            context: 额外上下文
            run_in_background: 是否后台运行

        Returns:
            SubAgentTask: 构造好的任务描述
        """
        template = AGENT_PROMPTS.get(agent_type, {})
        role = template.get("role", "")
        handoff_format = template.get("handoff_format", "")
        timeout = TIMEOUT_CONFIG.get(agent_type, 300)

        # 构造完整 prompt
        prompt_parts = [role, "", "## 输入产物"]
        for desc, path in input_files.items():
            prompt_parts.append(f"- {desc}: `{path}`")

        if context:
            prompt_parts.extend(["", "## 额外上下文"])
            for key, value in context.items():
                prompt_parts.append(f"- {key}: {value}")

        prompt_parts.extend([
            "",
            "## 期望输出",
            f"请将结果写入: `{output_path}`",
            "",
            handoff_format,
        ])

        task_id = f"{agent_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return SubAgentTask(
            task_id=task_id,
            agent_type=agent_type,
            prompt="\n".join(prompt_parts),
            input_files=input_files,
            expected_output=handoff_format,
            output_path=output_path,
            timeout=timeout,
            run_in_background=run_in_background,
        )

    def validate_handoff(self, output_path: str) -> Dict[str, Any]:
        """
        验证子 Agent 输出的 Handoff 格式

        Args:
            output_path: 子 Agent 输出文件路径

        Returns:
            验证结果 {valid: bool, errors: list, handoff: dict}
        """
        result = {"valid": False, "errors": [], "handoff": None}

        path = Path(output_path)
        if not path.exists():
            result["errors"].append(f"输出文件不存在: {output_path}")
            return result

        try:
            content = path.read_text(encoding="utf-8")

            # 检查 Handoff 格式关键字段
            required_sections = ["## Handoff:", "### 已完成工作", "### 产物路径"]
            for section in required_sections:
                if section not in content:
                    result["errors"].append(f"缺少必要章节: {section}")

            if not result["errors"]:
                result["valid"] = True
                result["handoff"] = {"raw_content": content}

        except Exception as e:
            result["errors"].append(f"读取输出文件失败: {e}")

        return result

    def should_degrade(self, result: SubAgentResult) -> bool:
        """判断是否需要降级到 Skill 模式"""
        if result.success:
            return False
        if result.error and "timeout" in result.error.lower():
            return True
        if result.error and "启动失败" in result.error:
            return True
        return False

    def get_degradation_message(self, agent_type: SubAgentType) -> str:
        """获取降级提示消息"""
        return (
            f"子 Agent ({agent_type.value}) 不可用，已降级到兼容模式（Skill 调度）。"
            f"功能不受影响，仅失去上下文隔离和并行执行优势。"
        )

    def get_parallel_tasks(
        self, stage: str
    ) -> List[List[SubAgentType]]:
        """
        获取可并行执行的子 Agent 组合

        Returns:
            可并行的任务组列表
        """
        parallel_map = {
            "stage_1_complete": [
                [SubAgentType.QC_INSPECTOR],   # Gate 1.5
                # 可与 Stage 1.8 探索性分析准备并行
            ],
            "stage_2_complete": [
                [SubAgentType.QC_INSPECTOR],   # Gate 2.5
                # 可与 Stage 3 环境准备并行
            ],
            "stage_3_phase6_complete": [
                [SubAgentType.EXEC_INFERENCE], # Phase 7-9
                # 可与报告模板准备并行
            ],
            "stage_3_complete": [
                [SubAgentType.QC_INSPECTOR],   # Gate 3.5
                # 可与 Stage 4 报告准备并行
            ],
        }
        return parallel_map.get(stage, [])

    def get_task_history(self) -> List[SubAgentResult]:
        """获取任务执行历史"""
        return self._task_history.copy()

    def record_result(self, result: SubAgentResult):
        """记录任务执行结果"""
        self._task_history.append(result)


# ============================================================
# 便捷函数
# ============================================================

def create_bridge(mode: AgentMode = AgentMode.HYBRID) -> HybridModeBridge:
    """创建混合模式桥接器实例"""
    return HybridModeBridge(mode=mode)


def build_qc_task(
    gate_type: str,
    artifacts: Dict[str, str],
    output_dir: str,
) -> SubAgentTask:
    """快速构建 QC Inspector 任务"""
    bridge = HybridModeBridge()
    return bridge.build_subagent_task(
        agent_type=SubAgentType.QC_INSPECTOR,
        input_files=artifacts,
        output_path=str(Path(output_dir) / f"gate_{gate_type}_report.md"),
        context={"gate_type": gate_type},
    )


def build_inference_task(
    results_path: str,
    sap_path: str,
    output_dir: str,
    background: bool = True,
) -> SubAgentTask:
    """快速构建 Exec Inference 任务"""
    bridge = HybridModeBridge()
    return bridge.build_subagent_task(
        agent_type=SubAgentType.EXEC_INFERENCE,
        input_files={
            "分析结果": results_path,
            "SAP 文档": sap_path,
        },
        output_path=str(Path(output_dir) / "inference_verification.md"),
        run_in_background=background,
    )


__all__ = [
    "SubAgentType",
    "AgentMode",
    "SubAgentConfig",
    "SubAgentTask",
    "SubAgentResult",
    "HybridModeBridge",
    "AGENT_PROMPTS",
    "TIMEOUT_CONFIG",
    "create_bridge",
    "build_qc_task",
    "build_inference_task",
]
