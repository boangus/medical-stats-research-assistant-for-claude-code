<!--
MSRA 项目专用模板 | Stage 2.5 SAP 质量门闸报告
================================================================
用途：analysis-plan 阶段完成后，由 QC Inspector 执行 SAP 质量审查，输出本报告。
定位：进入 Stage 3（分析执行）前的强制门闸。
原则：只检查不修改。谁产出谁不审查自己。
依据：ICH E9(R1) Estimands 框架、FDA SAP Guidance、CDISC ADaM。
关键项：3/5/7（未通过强制退回 Stage 2）。
================================================================
-->

---
study_id: "[{MSRA-YYYY-NNN}]"
gate_stage: "stage_2.5"
gate_name: "SAP 质量门闸 / SAP Quality Gate"
version: "v1.0"
assessed_at: "[{YYYY-MM-DDTHH:MM:SS+08:00}]"
assessor: "[{QC Inspector 标识}]"
assessor_role: "qc_inspector"
passport_ref: "MSRA/passport.json#gates.stage_2.5"
producer_stage: "stage_2"
consumer_stage: "stage_3"
status: "draft"  # draft / conditional / passed / blocked
total_items: 8
passed_items: "[{通过项数}]"
key_items: [3, 5, 7]
---

# SAP 质量门闸报告 (Stage 2.5 SAP Quality Gate Report)

> **审查对象**：Stage 2 (analysis-plan) 产出的统计分析计划 (SAP)、变量构造规格书、估计目标定义。
> **判定规则**：全部通过 → 进入 Stage 3 / 1-2 项未过 → 条件通过 / 3+ 项未过或关键项(3/5/7)未过 → 阻断退回 Stage 2。

---

## 1. 执行摘要 (Executive Summary)

| 项目 | 内容 |
|------|------|
| 研究编号 / Study ID | [{MSRA-YYYY-NNN}] |
| 研究类型 / Study Type | [{RCT / 观察性 / 诊断 / 真实世界}] |
| SAP 版本 / SAP Version | [{v1.0}] |
| 审查时间 / Assessed At | [{YYYY-MM-DD HH:MM}] |
| 审查员 / Assessor | [{QC Inspector 标识}] |
| 通过项数 / Passed Items | [{X}] / 8 |
| 关键项状态 / Key Items Status | [{全部通过 / 第 N 项未通过}] |
| 判定结果 / Verdict | [{PASS / CONDITIONAL / BLOCKED}] |
| 关键风险 / Key Risks | [{风险描述，无则填"无"}] |

---

## 2. 检查项详情 (Check Items Detail)

> 状态取值：PASS（通过）/ FAIL（未通过）/ N/A（不适用）/ SKIP（已跳过并记录）
> 关键项标记：🔑 = 关键项（未通过强制阻断）

### 2.1 检查项总览表

| # | 检查项 / Check Item | 关键 | 状态 | 证据/备注 |
|---|---------------------|------|------|----------|
| 1 | SAP 结构完整性 / SAP Structure Completeness (8 章节) | | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 2 | 研究目标明确性 / Research Objective Clarity | | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 3 | 估计目标完整性 / Estimand Completeness (ICH E9 R1 五要素) | 🔑 | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 4 | 方法选择合理性 / Method Selection Appropriateness | | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 5 | 假设条件验证 / Assumption Verification | 🔑 | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 6 | 敏感性分析计划 / Sensitivity Analysis Plan | | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 7 | 变量构造逻辑 / Variable Construction Logic | 🔑 | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 8 | 可重复性 / Reproducibility | | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |

### 2.2 检查项 1：SAP 结构完整性 / SAP Structure Completeness

- **检查内容**：SAP 是否包含全部 8 个必需章节。
- **检查方法**：
  1. 读取 SAP 文件 `reports/SAP_v{N}.md`。
  2. 核对以下 8 章节是否齐全：
     - §1 研究概述 / Study Overview
     - §2 分析人群 / Analysis Populations
     - §3 终点定义 / Endpoint Definitions
     - §4 统计方法 / Statistical Methods
     - §5 多重比较控制 / Multiplicity Control
     - §6 期中分析 / Interim Analysis（无则标注 N/A）
     - §7 变量构造定义 / Variable Construction
     - §8 分析规范表 / Analysis Specifications
- **通过标准**：8 章节齐全（§6 可为 N/A 但需说明）。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{SAP 路径、缺失章节列表}]

### 2.3 检查项 2：研究目标明确性 / Research Objective Clarity

- **检查内容**：主要目标和次要目标是否清晰、可量化、可检验。
- **检查方法**：
  1. 读取 SAP §1.1，确认主要目标含：目标人群、干预、对照、结局、时间框架（PICOT）。
  2. 确认每个目标对应明确的统计假设（H₀ / H₁）。
  3. 次要目标与主要目标不冲突。
- **通过标准**：主要目标 PICOT 完整，假设可检验。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{目标陈述摘要、假设清单}]

### 2.4 检查项 3：估计目标完整性 / Estimand Completeness 🔑

- **检查内容**：每个研究目标是否定义了完整的估计目标（ICH E9(R1) 五要素）。
- **检查方法**：
  1. 读取 SAP 估计目标章节，核对每个估计目标含 5 要素（见 §3 ICH E9(R1) 估计目标五属性表）。
  2. 伴发事件处理策略已明确（见 §4 伴发事件策略矩阵）。
  3. 估计目标与统计假设一一对应。
- **通过标准**：所有估计目标五要素齐全，伴发事件策略已定义。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{估计目标清单、缺失要素}]

### 2.5 检查项 4：方法选择合理性 / Method Selection Appropriateness

- **检查内容**：统计方法是否与研究设计、数据类型、目标人群匹配。
- **检查方法**：
  1. 核对方法选择与 `resources/statistics-methods/stat_test_decision_tree.md` 一致。
  2. RCT → ANCOVA / MMRM / Cox；观察性 → PS 加权 / DiD；诊断 → ROC / Bland-Altman。
  3. 方法选择依据已记录。
- **通过标准**：方法与设计匹配，依据明确。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{方法清单、决策树路径}]

### 2.6 检查项 5：假设条件验证 / Assumption Verification 🔑

- **检查内容**：所选统计方法的假设条件是否有验证计划。
- **检查方法**：
  1. 核对 SAP §4 是否包含假设验证计划：
     - 正态性（Shapiro-Wilk / Q-Q 图）
     - 方差齐性（Levene）
     - 线性性（残差图）
     - 比例风险（Schoenfeld 残差）
     - 多重共线性（VIF < 5）
  2. 假设不满足时有备选方法（非参数 / 稳健方法）。
- **通过标准**：假设验证计划完整，备选方法已定义。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{假设验证清单、备选方法}]

### 2.7 检查项 6：敏感性分析计划 / Sensitivity Analysis Plan

- **检查内容**：是否计划了至少 2 种敏感性分析。
- **检查方法**：
  1. 读取 SAP §4.x 敏感性分析章节。
  2. 核对包含至少 2 种：缺失数据（Tipping Point / 多重插补）、人群定义（PP vs ITT）、离群值（trimming）、模型假设（不同分布）。
  3. 每种敏感性分析有明确的预期目的。
- **通过标准**：≥ 2 种敏感性分析，目的明确。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{敏感性分析清单}]

### 2.8 检查项 7：变量构造逻辑 / Variable Construction Logic 🔑

- **检查内容**：衍生变量的构造公式、切点、依据是否在 SAP 中预定义。
- **检查方法**：
  1. 读取 SAP §7 和 `variable_spec_v{N}.md`。
  2. 每个衍生变量含：构造公式、切点依据（临床指南 / 文献 / 探索性）、缺失处理、验证规则。
  3. 禁止无依据切点（探索性切点必须标注）。
- **通过标准**：所有衍生变量定义完整，无空白字段。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{变量规格书路径、缺失定义数}]

### 2.9 检查项 8：可重复性 / Reproducibility

- **检查内容**：SAP 是否足够详细，使独立统计师可复现分析。
- **检查方法**：
  1. 评估 SAP 是否包含：软件版本、随机种子、代码模板引用、参数取值。
  2. 引用 `src/shared/templates/` 中的代码模板是否明确。
  3. 分析步骤是否可转化为可执行脚本。
- **通过标准**：SAP 可独立复现，无歧义步骤。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{SAP 复现性评估、歧义点}]

---

## 3. ICH E9(R1) 估计目标五属性表 (Estimand 5 Attributes)

> ICH E9(R1) 估计目标框架要求每个研究目标定义 5 个属性。本表逐估计目标核对。

### 3.1 估计目标清单

| 估计目标 ID | 描述 | A1 治疗 | A2 人群 | A3 变量 | A4 伴发事件 | A5 总结 | 完整性 |
|------------|------|--------|--------|--------|-----------|--------|--------|
| [{E1}] | [{主要估计目标描述}] | [{Treatment}] | [{Population}] | [{Endpoint}] | [{Intercurrent Event 策略}] | [{Population-level summary}] | [{完整/不完整}] |
| [{E2}] | [{次要估计目标描述}] | [{Treatment}] | [{Population}] | [{Endpoint}] | [{Intercurrent Event 策略}] | [{Population-level summary}] | [{完整/不完整}] |

### 3.2 五属性说明

| 属性 | 英文 | 含义 | 示例 |
|------|------|------|------|
| A1 治疗 | Treatment | 感兴趣的治疗条件 | 干预组 vs 对照组 |
| A2 人群 | Population | 目标患者群体 | ITT 人群 |
| A3 变量 | Variable | 结局变量（终点） | 治疗反应（CR+PR） |
| A4 伴发事件 | Intercurrent Event | 影响终点解释的事件 | 退出、转换治疗、死亡 |
| A5 总结 | Population-level Summary | 群体层面汇总指标 | 风险差（RD）及 95% CI |

---

## 4. 伴发事件策略矩阵 (Intercurrent Event Strategy Matrix)

> ICH E9(R1) 定义 5 种伴发事件处理策略。每个估计目标必须明确所用策略。

| 策略 | 英文 | 含义 | 适用场景 | 本次使用 |
|------|------|------|---------|---------|
| 治疗策略 | Treatment Policy Strategy | 无论是否发生伴发事件，均纳入分析 | 意向性治疗（ITT） | [{是/否}] |
| 复合策略 | Composite Strategy | 伴发事件视为不良结局 | 不良结局为终点时 | [{是/否}] |
| 假想策略 | Hypothetical Strategy | 假设未发生伴发事件时的情景 | 假设持续治疗 | [{是/否}] |
| 主要发生时策略 | While on Treatment Strategy | 仅分析伴发事件发生前的数据 | 治疗期间效应 | [{是/否}] |
| 主要层策略 | Principal Stratum Strategy | 仅分析不会发生伴发事件的层 | 选择性人群 | [{是/否}] |

**估计目标-策略映射**：

| 估计目标 ID | 伴发事件 | 所用策略 | 理由 |
|------------|---------|---------|------|
| [{E1}] | [{退出/转换治疗/死亡}] | [{Treatment Policy}] | [{ITT 原则}] |
| [{E2}] | [{退出}] | [{Composite}] | [{退出视为不良结局}] |

---

## 5. Protocol-SAP 一致性横断检查 (Protocol-SAP Consistency Cross-Check)

> SAP 必须与研究方案（Protocol）一致。不一致项需在 SAP 中说明并记录为偏差。

| 检查维度 | Protocol 内容 | SAP 内容 | 一致性 | 偏差说明 |
|---------|--------------|---------|--------|---------|
| 研究目的 / Objectives | [{Protocol §1}] | [{SAP §1.1}] | [{一致/不一致}] | [{如不一致，说明}] |
| 主要终点 / Primary Endpoint | [{Protocol §2}] | [{SAP §3}] | [{一致/不一致}] | [{如不一致，说明}] |
| 样本量 / Sample Size | [{Protocol §3}] | [{SAP §1.2}] | [{一致/不一致}] | [{如不一致，说明}] |
| 分析人群 / Analysis Populations | [{Protocol §4}] | [{SAP §2}] | [{一致/不一致}] | [{如不一致，说明}] |
| 主要分析方法 / Primary Analysis | [{Protocol §5}] | [{SAP §4}] | [{一致/不一致}] | [{如不一致，说明}] |
| 亚组分析 / Subgroup Analysis | [{Protocol §6}] | [{SAP §4.x}] | [{一致/不一致}] | [{如不一致，说明}] |
| 期中分析 / Interim Analysis | [{Protocol §7}] | [{SAP §6}] | [{一致/不一致}] | [{如不一致，说明}] |

**一致性总结**：[{一致项数}] / 7
**偏差清单**：[{列出所有偏差，无则填"无"}]

---

## 6. 阻断判定 (Block Decision)

### 6.1 判定规则

| 情形 | 判定 | 后续动作 |
|------|------|---------|
| 8 项全部 PASS | **PASS** | 进入 Stage 3，更新护照 |
| 1-2 项 FAIL（非关键项） | **CONDITIONAL** | 记录偏差，进入 Stage 3 但需限期整改 |
| 3+ 项 FAIL | **BLOCKED** | 退回 Stage 2 修订 |
| 任一关键项(3/5/7) FAIL | **BLOCKED** | 退回 Stage 2 修订 |

### 6.2 本次判定

- **判定结果**：[{PASS / CONDITIONAL / BLOCKED}]
- **未通过项**：[{列出编号，如"无"或"3, 5"}]
- **未通过原因**：[{逐项说明}]
- **偏差记录**：[{如 CONDITIONAL，记录偏差内容及整改期限}]

---

## 7. 退回路径 (Return Path)

> 仅当判定为 BLOCKED 时填写。

| 项目 | 内容 |
|------|------|
| 退回阶段 / Return To | stage_2 (analysis-plan) |
| 退回原因 / Return Reason | [{关键项未通过的具体说明}] |
| 整改要求 / Remediation Requirements | [{逐项列出需修复的内容}] |
| 预期重审时间 / Expected Re-assessment | [{YYYY-MM-DD}] |
| 责任人 / Responsible | [{analysis-plan 执行者}] |

---

## 8. 护照更新 (Passport Update)

> QC Inspector 完成审查后，更新 `MSRA/passport.json` 的 gates.stage_2.5 字段。

```json
{
  "gates": {
    "stage_2.5": {
      "status": "[{passed / conditional / blocked}]",
      "passed_items": [{X}],
      "total_items": 8,
      "assessed_at": "[{YYYY-MM-DDTHH:MM:SS+08:00}]",
      "assessor": "[{QC Inspector 标识}]",
      "report_path": "reports/gate_stage_2_5_v{N}.md",
      "key_items_failed": [{关键项未通过编号列表，如空则为 []}],
      "deviations": [{偏差记录，如空则为 []}]
    }
  },
  "checkpoints": {
    "last_verified": "[{stage_2.5 如通过，否则保留原值}]",
    "resume_point": "[{stage_3 如通过，否则 stage_2}]"
  }
}
```

---

## 9. 模板使用说明 (Template Usage Instructions)

### 9.1 使用流程

1. **触发时机**：analysis-plan 阶段（Stage 2）所有产物生成完成后，由 Pipeline 编排器调用 QC Inspector。
2. **填充方式**：复制本模板，将所有 `[{占位符}]` 替换为实际值。禁止保留占位符原样输出。
3. **文件命名**：`reports/gate_stage_2_5_v{N}.md`，每次重审递增版本号。
4. **护照联动**：审查完成后必须更新 `MSRA/passport.json` 的 `gates.stage_2.5` 字段（见 §8）。
5. **不可修改原则**：QC Inspector 只填写本报告，不修改 Stage 2 任何产物。

### 9.2 关键项说明

- **检查项 3（估计目标完整性）**：ICH E9(R1) 强制要求，缺失会导致监管拒绝。
- **检查项 5（假设条件验证）**：未验证假设的方法可能产生错误结论。
- **检查项 7（变量构造逻辑）**：未预定义的切点属于数据驱动的 P-hacking。

### 9.3 与其他门闸的关系

| 门闸 | Stage | 模板文件 |
|------|-------|---------|
| 数据质量门闸 | 1.5 | `data_quality_gate_report.md` |
| SAP 质量门闸 | 2.5 | `sap_quality_gate_report.md`（本文件） |
| 结果质量门闸 | 3.5 | `results_quality_gate_report.md` |

### 9.4 依据标准

- ICH E9(R1)：Statistical Principles for Clinical Trials (Addendum on Estimands)
- FDA Guidance：Statistical Analysis Plan Guidance (2022)
- CDISC ADaM：Analysis Data Model v2.1
- ICH E6(R3) GCP：Good Clinical Practice
- 项目内参考：`src/shared/sap/sap_standard.md`、`resources/statistics-methods/INDEX.md`
