"""
MSRA Quality Gates — 独立质量门闸模块

支持两种运行模式：
- Skill模式：LLM按Markdown检查清单执行
- 子Agent模式：通过HybridModeBridge启动独立QC Inspector Agent

Usage:
    from shared.quality_gates import GateRunner, GateType

    runner = GateRunner(study_id="MSRA-2026-001")
    result = runner.run_gate(GateType.DATA_QUALITY, artifacts={...})
    print(result.verdict)  # PASS / CONDITIONAL / BLOCKED
"""

from .gate_runner import GateRunner, GateResult, GateType, GateVerdict, RunMode, CheckItemResult
from .check_items import (
    CheckItem,
    CheckItemCollection,
    DataQualityCheckItems,
    SapQualityCheckItems,
    ResultsQualityCheckItems,
)

__all__ = [
    "GateRunner",
    "GateResult",
    "GateType",
    "GateVerdict",
    "RunMode",
    "CheckItemResult",
    "CheckItem",
    "CheckItemCollection",
    "DataQualityCheckItems",
    "SapQualityCheckItems",
    "ResultsQualityCheckItems",
]
