# Gate: SAP QUALITY (Stage 2.5)

## 元数据
- gate_id: "sap_quality"
- stage: "2.5"
- blocking: true
- skill_source: "analysis-plan"
- checkpoint_id: "GATE-02 / MANDATORY-M3"

## 输入

| 参数 | 类型 | 来源 | 必填 |
|------|------|------|------|
| sap | file (md/docx) | Stage 2 输出（已审查） | ✅ |
| eda_report | file (md) | Stage 1 Phase 4 | ✅ |
| estimand_definition | file (md) | Stage 2 Step 1 | 否 |
| method_decision | file (md) | Stage 2 Step 2 | 否 |

## 检查清单 (8 项)

| # | 检查项 | 通过标准 | 关键项 |
|---|--------|---------|--------|
| 1 | SAP 结构完整 | 所有必需章节是否存在 | 否 |
| 2 | 研究目标明确 | 主要/次要目标清晰定义 | 否 |
| 3 | 估计目标完整 | ICH E9(R1) 五要素齐全（人群/治疗/伴发事件/人群层面汇总/疗效变量） | ✅ 硬阻断 |
| 4 | 方法选择合理 | 统计方法与研究设计及研究类型（RCT/观察性/诊断试验）匹配 | 否 |
| 5 | 假设条件验证 | 数据特征支持所选方法的假设 | ✅ 硬阻断 |
| 6 | 敏感性分析计划 | 包含足够的敏感性分析 | 否 |
| 7 | 变量构造逻辑 | 所有分析变量的构造公式、切点、依据在 SAP 中预定义 | ✅ 硬阻断 |
| 8 | 可重复性 | SAP 足够详细以便独立复现 | 否 |

## 判定规则

- **PASS**: 全部通过 → ✅ 进入 Stage 3
- **CONDITIONAL**: 1-2 项未通过（非关键项） → ⚠️ 提示用户，可带条件进入 Stage 3（记录偏差）
- **BLOCK**: 3+ 项未通过 **或** 关键项 3/5/7 任一未通过 → ❌ **强制退回 Stage 2 修订**

> **关键项定义**：项 3（估计目标完整）、项 5（假设条件验证）、项 7（变量构造逻辑）为硬阻断项，不可条件通过。

## 输出 (gate_result schema)

```json
gate_result: {
  "gate": "sap_quality",
  "passed": bool,
  "total": 8,
  "passed_count": int,
  "failed_items": ["SG-0X", ...],
  "conditional": bool,
  "blocking_items": ["SG-03" | "SG-05" | "SG-07"],
  "timestamp": "ISO8601"
}
```

## 与 Pipeline 的联动

- **BLOCK** → 退回 Stage 2 修订 SAP
- **回退 ≥ 2 次** → 触发收敛检测（见 pipeline/SKILL.md §7.3）
- **CONDITIONAL** → 记录偏差后继续 Stage 3
- **Checkpoint**: [MANDATORY-M3] 门闸通过后进入 Stage 3

## 执行模式

- **Skill 模式**：`analysis-plan` 复用，Mode=`quality-gate`（只检查，不修改）
- **Agent 模式**：通过 `GateRunner` 调用 QC Inspector Agent
- 参考实现：`src/shared/quality_gates/gate_runner.py` + `check_items.py`
