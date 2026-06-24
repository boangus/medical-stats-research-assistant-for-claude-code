---
description: "MSRA 状态查看 — 显示 Pipeline 进度、门闸状态、产物清单"
argument-hint: "[--verbose] [--json]"
allowed-tools: Read, Bash, Grep, Glob
---

# MSRA Status

显示当前 Pipeline 的执行状态和进度。

## 行为

1. **扫描产物目录**: 检查 `.msra/` 目录下的产物文件
2. **读取 Passport**: 解析 Material Passport 获取阶段完成状态
3. **检查质量门闸**: 显示各 Gate 的通过/失败状态
4. **生成报告**: 输出结构化的状态摘要

## 输出格式

### 默认输出

```
📊 MSRA Pipeline 状态

当前阶段: Stage 3 - 分析执行
已完成: [1] [1.5] [2] [2.5] → ✅
进行中: [3]                    → 🔄
待执行: [3.5] [4] [5]         → ⏳

质量门闸:
  Gate 1.5 (数据质量): ✅ 通过 (9/9)
  Gate 2.5 (SAP质量):  ✅ 通过 (8/8)
  Gate 3.5 (结果质量): ⏳ 待执行

产物清单:
  .msra/passport.json          ✅
  .msra/data_profile.json      ✅
  .msra/analysis_plan.json     ✅
  .msra/execution_results/     🔄 (3/5 完成)
```

### 详细输出 (`--verbose`)

包含每个产物的详细信息（文件大小、生成时间、SHA256 哈希）。

### JSON 输出 (`--json`)

```json
{
  "current_stage": "analysis-exec",
  "completed_stages": ["data-prep", "data-quality-gate", "analysis-plan", "sap-quality-gate"],
  "gates": {
    "gate_1_5": {"status": "pass", "items_passed": 9, "items_total": 9},
    "gate_2_5": {"status": "pass", "items_passed": 8, "items_total": 8},
    "gate_3_5": {"status": "pending"}
  },
  "artifacts": [
    {"path": ".msra/passport.json", "status": "present", "size": 1234, "sha256": "..."}
  ]
}
```

## 实现方式

1. 扫描工作目录下的 `.msra/` 文件夹
2. 读取 `passport.json`（如存在）
3. 检查各阶段产物文件是否存在
4. 汇总质量门闸状态
5. 输出格式化报告
