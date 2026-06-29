# Gate: DATA QUALITY (Stage 1.5)

## 元数据
- gate_id: "data_quality"
- stage: "1.5"
- blocking: true
- skill_source: "data-prep"
- checkpoint_id: "GATE-01 / MANDATORY-M2"

## 输入

| 参数 | 类型 | 来源 | 必填 |
|------|------|------|------|
| cleaned_data | file (csv/xlsx) | Stage 1 输出 | ✅ |
| cleaning_log | file (md) | Stage 1 Phase 3 | ✅ |
| blind_audit_record | file (md) | Stage 1 Phase 4 | ✅ |
| db_lock_record | file (md) | Stage 1 Phase 5 | ✅ |
| normalization_log | file (md) | Stage 1 Phase 2 Step 2.5 | ✅ |
| data_dictionary | file (md) | Stage 1 Phase 1 | 否 |

## 检查清单 (9 项)

| # | 检查项 | 通过标准 | 关键项 |
|---|--------|---------|--------|
| 1 | 清洗日志完整 | 所有数据变更记录在案（变更原因、影响记录数） | 否 |
| 2 | 变量定义明确 | 所有衍生变量的构造逻辑清晰、可复现 | 否 |
| 3 | 缺失机制评估 | 已评估缺失模式（MCAR/MAR/MNAR）并选择处理策略 | 否 |
| 4 | 盲态审核完成 | 盲态审核记录完整，无未解决的质疑 | 否 |
| 5 | 数据库锁定确认 | 锁定版本号和锁定时间已记录 | ✅ 硬阻断 |
| 6 | 逻辑一致性验证 | 清洗后数据的关键逻辑关系自洽（日期顺序、范围约束） | ✅ 硬阻断 |
| 7 | 值规范化完成 | 无遗留非标准值；规范化日志完整（含原值、规范值、处理策略、影响记录数） | ✅ 硬阻断 |
| 8 | 可重复性 | 清洗脚本可独立运行并复现相同结果 | 否 |
| 9 | 隐私合规完成 | 无未处理的直接标识字段；准标识符已泛化或用户确认接受风险 | ✅ 硬阻断 |

### 检查项 7（值规范化）详细标准
- 中医术语变体（后缀变体、同义变体）已检测并规范化（GB/T 16751.2）
- 数值截断标记（<、>、小于、大于等）已处理
- 逗号多值已处理
- 规范化日志完整（含原值、规范值、处理策略、影响记录数）
- 通过标准：无遗留非标准值；如含自定义术语已征得用户确认

### 检查项 9（隐私合规）详细标准
- 直接标识字段（姓名、身份证、电话等）已脱敏或删除
- 准标识符字段（精确日期、邮编等）已泛化处理
- 自由文本 PII 已检测并替换
- 通过标准：无未处理的直接标识字段；准标识符已泛化或用户确认接受风险

## 判定规则

- **PASS**: 全部通过 (9/9) → ✅ 进入 Stage 2
- **CONDITIONAL**: 7-8/9 通过（即 ≤2 项非关键项未通过） → ⚠️ 记录风险后进入 Stage 2
- **BLOCK**: <7/9 通过 **或** 关键项 5/6/7/9 任一未通过 → ❌ **强制退回 Stage 1 修订**

> **关键项定义**：项 5（数据库锁定）、项 6（逻辑一致性）、项 7（值规范化）、项 9（隐私合规）为硬阻断项，不可条件通过。

## 输出 (gate_result schema)

```json
gate_result: {
  "gate": "data_quality",
  "passed": bool,
  "total": 9,
  "passed_count": int,
  "failed_items": ["DG-0X", ...],
  "conditional": bool,
  "blocking_items": ["DG-05" | "DG-06" | "DG-07" | "DG-09"],
  "timestamp": "ISO8601"
}
```

## 与 Pipeline 的联动

- **BLOCK** → 退回 Stage 1 修订清洗流程
- **回退 ≥ 2 次** → 触发收敛检测（见 pipeline/SKILL.md §7.3）
- **CONDITIONAL** → 记录风险后继续 Stage 2
- **Checkpoint**: [MANDATORY-M2] 门闸通过后进入 Stage 2

## 执行模式

- **Skill 模式**：`data-prep` 复用，Mode=`quality-gate`（只检查，不修改）
- **Agent 模式**：通过 `GateRunner` 调用 QC Inspector Agent
- 参考实现：`src/shared/quality_gates/gate_runner.py` + `check_items.py`
