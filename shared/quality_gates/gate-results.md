# Gate: RESULTS QUALITY (Stage 3.5)

## 元数据
- gate_id: "results_quality"
- stage: "3.5"
- blocking: true
- skill_source: "analysis-exec"
- checkpoint_id: "GATE-03 / MANDATORY-M4"

## 输入

| 参数 | 类型 | 来源 | 必填 |
|------|------|------|------|
| analysis_results | file (md/json) | Stage 3 输出 | ✅ |
| qc_report | file (md) | Stage 3 Phase 11 质检 | ✅ |
| sap | file (md/docx) | Stage 2 定稿 | ✅ |
| generator_evaluator_diff | file (md) | Stage 3 Generator-Evaluator 比对 | 否 |
| calibration_db | file (json) | `MSRA/calibration/calibration_db.json` | 否（校准联动项需要） |

## 检查清单 (14 项)

| # | 检查项 | 通过标准 | 关键项 |
|---|--------|---------|--------|
| 1 | 结果完整性 | 所有 SAP 中计划的分析都已执行 | ✅ 硬阻断 |
| 2 | 假设验证 | 所有方法的假设条件已检验并满足 | 否 |
| 3 | 数值一致性 | 报告中的关键数字在分析输出中一致 | ✅ 硬阻断 |
| 4 | 敏感性分析 | 敏感性分析结果与主分析一致 | ✅ 硬阻断 |
| 5 | 效应量报告 | 包含效应量及其置信区间 | 否 |
| 6 | 异常结果标记 | 异常/意外结果被标记说明 | 否 |
| 7 | 结果复现 | 3 次重跑关键结论一致（详见 shared/reproducibility/） | 否 |
| 8 | [SKIP] 标记 | 跳过的分析有合理记录 | 否 |
| 9 | [校准联动] 校准置信度 | 该方法类型的历史校准指标达标 | 否 |
| 10 | P 值格式合规 | 所有 P 值符合 P-R01~R07（无 P=0.000，无二元化表述） | ✅ 硬阻断 |
| 11 | 方法一致性 | 加权分析链无混用（M-R01~R08），方法一致性追踪表已填写 | ✅ 硬阻断 |
| 12 | 数据集一致性 | 数据集差异已提醒用户抉择（D-R01~D-R05），追踪表已填写 | ✅ 硬阻断 |
| 13 | 统计原则违反处理 | 所有统计原则违反已记录并经用户确认（S-R01~S-R08） | ✅ 硬阻断 |
| 14 | 图表发表级质量 | 图表符合 publication_figure_standards.md（rcParams/SVG/配色/变量名/P 值标注） | 否 |

### 检查项 9（校准联动）详细标准
- 读取 `MSRA/calibration/calibration_db.json` 中该方法类型的累积 TPR/FPR
- TPR ≥90% 且 FPR ≤10% → ✅ 高置信度
- TPR 80-90% 或 FPR 10-15% → ⚠️ 低置信度，必须人工复核
- TPR < 80% 或 FPR > 15% → ❌ 不可信，强制人工复核
- 校准数据不足（<10 条） → ⚠️ 无法评估，必须人工复核

### 检查项 10（P 值格式）详细标准
- 参考 `shared/statistics-methods/statistical_constraints.md`
- 无 P=0.000（应写为 P<0.001）
- 无二元化表述（如"显著/不显著"，应报告效应量+CI+P）

## 判定规则

- **PASS**: 全部通过 (14/14) → ✅ 进入 Stage 4
- **CONDITIONAL**: 1-2 项非关键项未通过 → ⚠️ 提示用户，记录风险后带条件进入 Stage 4
- **BLOCK**: 3+ 项未通过 **或** 关键项 1/3/4/10/11/12/13 任一未通过 → ❌ **强制退回 Stage 3 修正**

> **关键项定义**：项 1（结果完整性）、项 3（数值一致性）、项 4（敏感性分析）、项 10（P 值格式）、项 11（方法一致性）、项 12（数据集一致性）、项 13（统计原则违反）为硬阻断项，不可条件通过。

## 输出 (gate_result schema)

```json
gate_result: {
  "gate": "results_quality",
  "passed": bool,
  "total": 14,
  "passed_count": int,
  "failed_items": ["RG-0X", ...],
  "conditional": bool,
  "blocking_items": ["RG-01" | "RG-03" | "RG-04" | "RG-10" | "RG-11" | "RG-12" | "RG-13"],
  "timestamp": "ISO8601"
}
```

## 与 Pipeline 的联动

- **BLOCK** → 退回 Stage 3 修正分析
- **回退 ≥ 2 次** → 触发收敛检测（见 pipeline/SKILL.md §7.3）
- **CONDITIONAL** → 记录风险后继续 Stage 4
- **Checkpoint**: [MANDATORY-M4] 门闸通过后进入 Stage 4
- Generator-Evaluator 差异报告作为本门闸的输入项之一（来自 Stage 3）

## 执行模式

- **Skill 模式**：`analysis-exec` 复用，Mode=`quality-gate`（只检查，不修改）
- **Agent 模式**：通过 `GateRunner` 调用 QC Inspector Agent
- 参考实现：`shared/quality_gates/gate_runner.py` + `check_items.py`
