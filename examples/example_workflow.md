# MSRA 使用示例

## 示例 1: RCT 完整流程

### 场景
评估新药 X 对高血压患者的疗效。

### 启动流水线

```
用户: /msra 我有一份 RCT 原始数据，想完成整个分析

Pipeline: 检测到原始数据 → 研究类型: RCT → 从 Stage 1 开始

Stage 1: 数据准备
  Phase 1: 数据验证（结构、类型、缺失、逻辑、范围）
  Phase 2: 清洗策略讨论（交互式）🔴 [MANDATORY]
  Phase 2.5: 值规范化（TCM 术语/数值变体，如有）
  Phase 3: 执行清洗
  Phase 4: EDA 数据质量检查
  Phase 5: 盲态审核（RCT 启用盲法审核）
  Phase 6: 数据库锁定 🔴 [MANDATORY]

  → 进入 Stage 1.5 质量门闸（8 项检查）
```

```
Stage 2: 分析计划
  Phase 1: 深度 EDA（为方法选择服务）
  Phase 2+3: Estimands 定义 + 方法探讨 + 参数确认（合并）
  → 推荐: ANCOVA（RCT 连续终点首选）
  Phase 4: 制定 SAP
  Phase 5: 计划审查

  → 进入 Stage 2.5 质量门闸（7 项检查）
```

```
Stage 3: 分析执行
  Phase 0: SAP验证 + 执行前检查
  Phase 1: 变量构造
  Phase 2: 描述性统计(Table1) + 依从性 + 安全性
  Phase 3: 推断分析（ANCOVA → 假设检验 → 敏感性分析）
  Step 3.1: （RCT 跳过）
  🔴 [MANDATORY-ME1] 主要分析结果确认
  Phase 4-6: 质检 + 输出 + 审计

  → 进入 Stage 3.5 质量门闸（8 项检查）
```

```
Stage 4: 报告生成
  Phase 1: 结果解读（统计显著性 vs 临床意义）
  (报告规范选择已移至 Paper Track Stage 5.0)
  Phase 2: 表格生成与导出（Markdown + .docx 三线表）
  Phase 3: 图表整合（KM 曲线、森林图等）
  Phase 4: 方法学描述
  Phase 5: 一致性校验 🔴 [MANDATORY]
  Phase 6: 报告组装（HTML + MD + PNG + DOCX）

  → 输出最终报告
```

### 中途切入

```
# 已有清洗数据，直接制定分析计划
用户: /msra 我的数据已经清洗好了，帮我制定分析计划
→ 从 Stage 2 开始（前置检查：确认 Stage 1.5 门闸通过）

# 已有 SAP，直接执行分析
用户: /msra-exec --sap plan.md --data cleaned.csv
→ 从 Stage 3 开始（需先审查 SAP）

# 分析完成，生成 CONSORT 报告
用户: /msra-report CONSORT
→ 从 Stage 4 开始
```

---

## 示例 2: 观察性研究完整流程

### 场景
基于 SEER 数据库分析前列腺癌 ADT 治疗与心血管事件的关系。

### 启动流水线

```
用户: /msra 我有一份队列研究数据，想分析 ADT 与心血管事件的关系

Pipeline: 检测到原始数据 → 研究类型: 观察性(队列) → 从 Stage 1 开始
```

```
Stage 1: 数据准备
  Phase 1: 数据验证
  Phase 2: 清洗策略讨论
  → 特别关注: 混杂因素变量的完整性（年龄、分期、合并症等）
  Phase 2.5: 值规范化（编码变体、诊断术语标准化）
  Phase 3-6: 清洗 → EDA → 锁定

  → Stage 1.5 质量门闸
```

```
Stage 2: 分析计划
  Phase 1: 深度 EDA
  → 关键: 检查暴露组和对照组基线差异
  → 关键: 评估混杂因素分布

  Phase 2+3: Estimands + 方法探讨
  → 方法选择: 倾向性评分匹配(PSM) + IPTW + Cox 回归
  → 混杂控制: DAG 识别混杂 → PSM 匹配 → 协变量平衡性检验
  → 观察性研究高级方法: IPTW/RCS/E-value/亚组分析
  → SAP 参数: 截断百分位(95th)、PS 模型(logit)、Bootstrap(500次)

  Phase 4: 制定 SAP
  Phase 5: 审查
```

```
Stage 3: 分析执行
  Phase 0: SAP 验证 + 样本量验证
  Phase 1: 变量构造（按 SAP 定义的变量构造规则）
  Phase 2: Table 1 + 依从性 + 安全性
  Phase 3: Cox 回归（主要分析）
  Step 3.1: 观察性研究高级方法
    → IPTW 加权（WeightIt + cobalt 平衡性诊断）
    → RCS 剂量-反应曲线（rms 包）
    → E-value 敏感性分析
    → 亚组分析（森林图）
  🔴 [MANDATORY-ME1] 主要分析结果确认
  Phase 4-6: 质检 + 输出 + 审计
```

```
Stage 4: 报告生成
  Phase 1: 结果解读
  → 必须讨论: 残留混杂的可能性
  → 必须讨论: E-value 解释
  (报告规范选择已移至 Paper Track Stage 5.0)
  Phase 2-6: 表格 + 图表 + 方法学描述 + 一致性校验 + 报告组装
```

### 关键差异（vs RCT）

| 维度 | RCT | 观察性 |
|------|-----|--------|
| 混杂控制 | 随机化（不调整） | PSM + IPTW + 多变量 |
| 主要分析 | ANCOVA | Cox 回归 |
| 敏感性分析 | 偏离 ITT | E-value / 未测量混杂 |
| 报告规范 | CONSORT | STROBE |
| Step 3.1 | 跳过 | IPTW/RCS/E-value/亚组 |

---

## 示例 3: 诊断试验分析

### 场景
评估 AI 模型对糖尿病视网膜病变的诊断性能。

### 启动流水线

```
用户: /msra 我有一份诊断试验数据，想分析 AI 模型的诊断性能

Pipeline: 检测到原始数据 → 研究类型: 诊断试验 → 从 Stage 1 开始
```

```
Stage 2: 分析计划
  Phase 2+3: 方法探讨
  → 方法选择: ROC 分析 + 敏感度/特异度 + AUC + DCA
  → 金标准: 眼底照相 + 专家阅片
  → 切点选择: Youden 指数 + 成本-效益分析
  → 不同切点分析: 敏感度优先 vs 特异度优先
```

```
Stage 3: 分析执行
  Phase 3: ROC 分析
  → 生成 ROC 曲线 + AUC + 95%CI
  → 最优切点 + 敏感度/特异度
  Step 3.1: （可选）决策曲线分析(DCA)
  Phase 3: 诊断性能总结
```

```
Stage 4: 报告生成
  (报告规范选择已移至 Paper Track Stage 5.0)
  Phase 3: 图表整合
  → ROC 曲线（ggplot2）
  → 校准曲线
  → DCA 决策曲线
  → Bland-Altman 图（如适用）
```

---

## 示例 4: 快速图表生成

```
用户: /msra-report --type table1
→ 仅生成 Table 1（三线表，.docx 输出）

用户: /msra-report --type figure
→ 仅生成所有图表

用户: /msra-report --type methods
→ 仅生成方法学描述段落

用户: /msra-report --type table1 --format docx
→ 生成 Table 1 并导出为 Word 三线表
```

### 支持的图表类型

| 类型 | R 模板 | Python 模板 |
|------|--------|-------------|
| 基线特征表 | table1_template.R (gtsummary) | — |
| 基线特征表 | table1_pharmaverse.R | — |
| 生存曲线 | survival_ggsurvfit.R | survival_lifelines.py |
| ROC 曲线 | roc_visualization_template.R | roc_template.py |
| 森林图 | forest_plot_template.R | forest_plot_template.py |
| 校准曲线 | calibration_plot_template.R | — |
| Bland-Altman | bland_altman_template.R | bland_altman_template.py |
| 增强图表 | enhanced_chart_template.R | enhanced_chart_template.py |

---

## 示例 5: 通用提示

```
/msra 我有一份原始数据 → 自动检测研究类型，从 Stage 1 开始
/msra --from plan → 从 Stage 2 开始（假设数据已清洗）
/msra --from exec → 从 Stage 3 开始（假设 SAP 已就绪）
/msra --from report → 从 Stage 4 开始（假设分析已完成）
/msra --status → 查看当前流水线状态
```

### 研究类型自动检测

Pipeline 根据数据特征和用户描述自动识别研究类型：
- **RCT**: 随机分组变量存在、实验设计描述
- **观察性**: 队列/病例对照/横断面、无随机化、暴露-结局结构
- **诊断试验**: 金标准变量、诊断测试结果、敏感度/特异度指标



