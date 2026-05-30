# MSRA 使用示例

## 示例 1: RCT 完整流程

### 场景
评估新药 X 对高血压患者的疗效。

### 启动流水线

```
用户: /msra 我有一份 RCT 原始数据，想完成整个分析

Pipeline: 检测到原始数据 → 从 Stage 1 开始

Stage 1: 数据准备
  Phase 1: 数据验证（结构、类型、缺失、逻辑、范围）
  Phase 2: 清洗策略讨论（交互式）
  Phase 3: 执行清洗
  Phase 4: 变量构造（从出生日期计算年龄、BMI 等）
  Phase 5: 盲态审核（如适用）
  Phase 6: 数据库锁定

  🔴 CHECKPOINT: 清洗摘要 + 变量清单 + 审核记录
  → 用户确认后进入 Stage 2
```

```
Stage 2: 分析计划
  Phase 1: EDA（分布、相关性、异常值、缺失模式）
  Phase 2: Estimands 定义（ICH E9(R1) 五要素）
  Phase 3: 方法探讨（基于 EDA，推荐 ANCOVA）
  Phase 4: 制定 SAP
  Phase 5: 计划审查

  🔴 CHECKPOINT: SAP 审查通过后进入 Stage 3
```

```
Stage 3: 分析执行
  Phase 1: 执行前检查
  Phase 2: 描述性统计（Table 1）
  Phase 3: 依从性 & 合并用药分析
  Phase 4: 安全性分析
  Phase 5: 代码生成与执行（ANCOVA → 假设检验 → 敏感性分析）
  Phase 6: 质量检查

  🔴 CHECKPOINT: 质检通过后进入 Stage 4
```

```
Stage 4: 报告生成
  Phase 1: 结果解读（统计显著性 vs 临床意义）
  Phase 2: 确定报告规范（CONSORT）
  Phase 3: 生成表格
  Phase 4: 生成图表
  Phase 5: 方法学描述
  Phase 6: 合规检查（CONSORT 检查清单）

  🔴 CHECKPOINT: 合规检查通过 → 输出最终报告
```

### 中途切入

```
# 已有清洗数据，直接制定分析计划
用户: /msra 我的数据已经清洗好了，帮我制定分析计划
→ 从 Stage 2 开始（前置检查：确认清洗日志）

# 已有 SAP，直接执行分析
用户: /msra-exec --sap plan.md --data cleaned.csv
→ 从 Stage 3 开始

# 分析完成，生成 CONSORT 报告
用户: /msra-report CONSORT
→ 从 Stage 4 开始
```

## 示例 2: 观察性研究中的混杂控制

```
用户: /msra 我有一份队列研究数据，想分析吸烟与肺癌的关系

Stage 1: 数据准备
  → 验证数据完整性、检查缺失模式

Stage 2: 分析计划
  → EDA → Estimands → 方法探讨
  → 推荐: Kaplan-Meier + Cox 回归（调整混杂）
  → 混杂控制: 倾向性评分匹配 (PSM) 或 DAG 方法

Stage 3: 分析执行
  → KM 曲线 + Log-rank 检验
  → Cox 回归（检查比例风险假设）
  → 敏感性分析

Stage 4: 报告生成
  → STROBE 规范检查
  → 森林图（亚组分析）
```

## 示例 3: 诊断试验分析

```
用户: /msra-report --type figure
→ 快速模式：仅生成图表，跳过其他 Phase

支持输出:
  - Kaplan-Meier 曲线 (survminer)
  - 森林图 (ggforestplot)
  - ROC 曲线 (pROC)
  - 瀑布图 (ggplot2)
  - Bland-Altman 图 (ggplot2)
```

---

> 💡 提示: 通过 `--type` 参数可快速生成单个元素
> `/msra-report --type table1` → 仅生成 Table 1
> `/msra-report --type methods` → 仅生成方法学描述



