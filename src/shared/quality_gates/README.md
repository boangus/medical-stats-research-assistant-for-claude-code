# MSRA Quality Gates — 独立质量门闸模块

## 概述

将原本分散在各 SKILL.md 中的质量门闸检查逻辑抽取为独立模块，支持两种运行模式：

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| **Skill模式** | 生成检查清单prompt，由LLM按清单执行 | 日常使用、快速迭代 |
| **Agent模式** | 通过HybridModeBridge启动独立QC Inspector Agent | 需要上下文隔离、并行执行 |

## 模块结构

```
src/shared/quality_gates/
├── __init__.py          # 模块入口，统一导出
├── gate_runner.py       # 门闸执行器（GateRunner）
├── check_items.py       # 检查项定义（3个门闸，共26项）
└── README.md            # 本文件
```

## 使用方式

### Skill模式（默认）

```python
from shared.quality_gates import GateRunner, GateType

runner = GateRunner(study_id="MSRA-2026-001")

# 生成检查清单prompt
prompt = runner.generate_checklist(
    GateType.DATA_QUALITY,
    artifacts={
        "cleaned_data": "MSRA/data/cleaned.csv",
        "cleaning_log": "MSRA/data/cleaning_log.md",
        "variable_list": "MSRA/data/variable_list.md",
    }
)
# prompt 可直接发送给LLM执行检查
```

### Agent模式（QC Inspector子Agent化）

```python
from shared.quality_gates import GateRunner, GateType

runner = GateRunner(study_id="MSRA-2026-001")

# 构造子Agent任务（通过HybridModeBridge）
task_info = runner.build_agent_task(
    GateType.DATA_QUALITY,
    artifacts={"cleaned_data": "MSRA/data/cleaned.csv"},
    output_path="MSRA/reports/gate_1_5_report.md",
)

# task_info["task"] 为 SubAgentTask，可传递给 Agent 工具执行
# task_info["prompt"] 为完整的子Agent prompt
# run_in_background=True，Gate检查可与下一阶段准备并行
```

### 预填模式（LLM完成检查后判定）

```python
from shared.quality_gates import GateRunner, GateType, RunMode, CheckItemResult

runner = GateRunner(study_id="MSRA-2026-001")

# 假设LLM已完成检查，传入结果
check_results = [
    CheckItemResult(item_id="DG-01", name="清洗日志完整性", is_key=False, status="PASS"),
    CheckItemResult(item_id="DG-05", name="数据完整性", is_key=True, status="PASS"),
    # ... 其他检查项
]

result = runner.run_gate(
    GateType.DATA_QUALITY,
    artifacts={},
    mode=RunMode.SKILL,
    check_results=check_results,
)

print(result.verdict)  # GateVerdict.PASS / CONDITIONAL / BLOCKED
print(result.pass_rate)  # 1.0
```

## 门闸定义

| 门闸 | 阶段 | 检查项数 | 关键项 | 关键项编号 |
|------|------|---------|--------|-----------|
| **Gate 1.5** | 数据质量 | 9 | 4项 | 5, 6, 7, 9 |
| **Gate 2.5** | SAP质量 | 8 | 3项 | 4, 6, 8 |
| **Gate 3.5** | 结果质量 | 9 | 5项 | 1, 2, 7, 8, 9 |

## 判定规则

- **PASS**: 全部通过
- **CONDITIONAL**: 1-2项未过（非关键项）
- **BLOCKED**: 3+项未过，或任意关键项未过

## 与现有系统的关系

- **检查清单模板**: `src/shared/templates/quality-gates/` 中的 Markdown 模板继续作为LLM执行的详细指引
- **JSON Schema**: `resources/contracts/passport/` 中的门闸Schema定义产物契约
- **本模块**: 提供结构化的检查项定义和统一的执行接口

三者互补，不互相替代。
