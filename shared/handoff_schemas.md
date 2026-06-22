# 临床数据交接规范 — Cross-Stage Data Contracts

## Purpose

定义临床研究流水线各阶段之间传递的每一个 artifact 的精确数据结构。
所有产生或消费这些 artifact 的 agent 必须严格遵守本规范中的 schema 定义。
消费方 agent 应在接收时验证输入，若发现 schema 违规则要求重新生成。

> **约定**：所有 schema 采用 Markdown 结构化输出。Agent 在接受交接前必须验证所有必填字段。
> 缺失必填字段将触发 `HANDOFF_INCOMPLETE` 失败路径。

---

## Schema 1: 研究问题定义 — PICO/PICOS Framework

**生产者**: `data-prep` (Stage 1) / `analysis-plan` (Stage 2)
**消费者**: `analysis-plan` (Stage 2) / `report` (Stage 5)

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `research_question` | string | 经 PICO/PICOS 框架结构化的研究问题（单句疑问形式） |
| `pico` | object | PICO/PICOS 各要素，详见下方 |
| `study_registration` | object | 临床试验注册信息（如适用） |
| `hypothesis` | object | `{primary: string, secondary: list[string]}` |
| `study_type` | enum | `"RCT"` / `"cohort"` / `"case_control"` / `"cross_sectional"` / `"systematic_review"` / `"meta_analysis"` / `"diagnostic_accuracy"` / `"observational"` |
| `target_population` | object | `{description: string, n_expected: integer, inclusion_criteria: list[string], exclusion_criteria: list[string]}` |
| `primary_endpoint` | string | 主要终点指标及其定义 |
| `secondary_endpoints` | list[string] | 次要终点指标列表 |
| `follow_up_duration` | string | 随访时长（如 "12 months", "5 years"） |

### PICO/PICOS 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `population` | string | 目标人群描述（疾病、分期、年龄、性别等） |
| `intervention` | string | 干预措施（含剂量、频次、给药途径） |
| `comparator` | string | 对照措施（安慰剂、标准治疗、空白对照等） |
| `outcome` | string | 主要结局指标（含测量方法和时间点） |
| `study_design` | string | 研究设计类型（如 "parallel group", "crossover"） |
| `timeframe` | string | 评估时间框架 |

### 研究注册对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `registry` | enum | `"ClinicalTrials.gov"` / `"ChiCTR"` / `"ISRCTN"` / `"EUDRA"` / `"UMIN"` / `"ANZCTR"` / `"other"` |
| `registration_id` | string | 注册号（如 NCT00000000） |
| `registration_date` | string | 注册日期（ISO 8601） |
| `enrollment_status` | enum | `"recruiting"` / `"active_not_recruiting"` / `"completed"` / `"terminated"` / `"withdrawn"` |

### 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `subgroup_hypotheses` | list[string] | 预设亚组分析假设 |
| `safety_endpoints` | list[string] | 安全性终点（如不良事件、SAE） |
| `interim_analysis_plan` | string | 中期分析计划描述 |
| `dsmb_provisions` | string | 数据安全监查委员会设置 |
| `regulatory_classification` | enum | `"drug"` / `"device"` / `"procedure"` / `"behavioral"` / `"diagnostic"` |

### 示例

```markdown
## 研究问题定义

**Research Question**: In patients with newly diagnosed stage II-III colorectal cancer (P), does adjuvant CAPOX chemotherapy (I) compared to FOLFOX4 (C) result in non-inferior 3-year disease-free survival (O) in a randomized controlled non-inferiority trial (S)?

**PICO**:
- Population: Adults ≥18 years with stage II-III colorectal cancer post-curative resection, ECOG PS 0-1
- Intervention: CAPOX (capecitabine 1000 mg/m² bid d1-14 + oxaliplatin 130 mg/m² d1, q3w × 8 cycles)
- Comparator: FOLFOX4 (oxaliplatin 85 mg/m² d1 + leucovorin 200 mg/m² + 5-FU 400 mg/m² bolus + 46h infusion, q2w × 12 cycles)
- Outcome: 3-year disease-free survival (DFS)
- Study Design: Open-label, randomized, non-inferiority, multicenter

**Study Registration**: ClinicalTrials.gov NCT00000001, registered 2024-03-15, status: recruiting

**Hypothesis**:
- Primary: CAPOX is non-inferior to FOLFOX4 in 3-year DFS (non-inferiority margin: HR 1.20)
- Secondary: (1) Overall survival; (2) Grade ≥3 toxicity incidence; (3) Quality of life (EORTC QLQ-C30)

**Target Population**: N_expected = 1200; Inclusion: stage II-III CRC, age 18-75, ECOG 0-1, adequate organ function; Exclusion: prior chemotherapy, synchronous malignancy, pregnancy

**Primary Endpoint**: Disease-free survival (DFS), defined as time from randomization to first recurrence, second primary cancer, or death from any cause

**Follow-up**: 5 years (DFS), 6 years (OS)
```

---

## Schema 2: 分析计划交接 — SAP Elements & Estimands

**生产者**: `analysis-plan` (Stage 2)
**消费者**: `analysis-exec` (Stage 3) / `calibration` / `report` (Stage 4/5)

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `sap_version` | string | 统计分析计划版本号（如 "SAP v2.0 — 2026-03-15"） |
| `estimands` | list[Estimand] | ICH E9(R1) estimand 框架定义的每个主要/次要 estimand |
| `analysis_population` | object | 各分析人群定义 |
| `primary_analysis` | object | 主要统计分析方法描述 |
| `sample_size_justification` | object | 样本量论证 |
| `multiplicity_control` | object | 多重性控制策略 |
| `missing_data_strategy` | object | 缺失数据处理策略 |
| `interim_analyses` | object | 中期分析计划（如有） |

### Estimand 对象 (ICH E9(R1))

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 唯一标识（如 `EST-01`） |
| `endpoint` | string | 对应的结局变量 |
| `population` | string | 目标人群 |
| `treatment` | string | 处理因素 |
| `summary_measure` | string | 汇总指标（如 hazard ratio, risk difference, mean difference） |
| `intercurrent_events` | object | `{strategy: string, description: string}` — ICH E9(R1) 五种策略之一 |
| `population_level` | object | `{level: string, definition: string}` — overall / principal stratum / hypothetical 等 |

### 分析人群对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `intention_to_treat` | string | ITT 人群定义及统计集 |
| `modified_it` | string | mITT 人群定义 |
| `per_protocol` | string | PP 人群定义 |
| `safety_population` | string | 安全性分析人群定义 |
| `pharmacokinetic` | string | PK 分析人群定义（如适用） |

### 示例

```markdown
## 分析计划交接 — SAP v2.0

### Estimand 01 (Primary)
- Endpoint: 3-year DFS
- Population: All randomized patients with stage II-III CRC
- Treatment: CAPOX vs FOLFOX4
- Summary Measure: Hazard Ratio (Cox PH, non-inferiority test)
- Intercurrent Events Strategy: treatment policy composite — recurrence, second primary, and death all counted as events regardless of treatment discontinuation
- Population Level: overall

### Analysis Population
- ITT: All randomized patients, analyzed as randomized
- mITT: All randomized patients who received ≥1 cycle and had post-baseline efficacy assessment
- PP: All ITT patients with no major protocol deviations (>85% planned dose, no non-eligible enrollment)
- Safety: All patients who received ≥1 dose of study treatment

### Primary Analysis
- Method: Stratified log-rank test (strata: stage [II vs III], center)
- Effect estimate: Stratified Cox proportional hazards model, HR (95% CI)
- Non-inferiority margin: HR < 1.20 (one-sided α = 0.025)
- Software: R v4.3+ with survival package; SAS v9.4 PROC PHREG

### Sample Size Justification
- N = 1200 (600 per arm), 2-sided α = 0.05, power 80%
- Assumed 3-year DFS: 75% (FOLFOX4), non-inferiority margin 70% (HR 1.20)
- Dropout rate: 15%, events needed: 330

### Missing Data Strategy
- Primary: Complete case analysis under MAR assumption
- Sensitivity: (1) Multiple imputation (m = 50, predictive mean matching); (2) Tipping-point analysis (worst-case imputation); (3) Pattern-mixture models
- Missing NOTAR (non-responder at time of analysis) for responder analyses

### Multiplicity Control
- Hierarchical testing: DFS → OS → Safety → QoL
- If non-inferiority for DFS is rejected, proceed to OS; otherwise stop
- No alpha adjustment for secondary endpoints within each test
```

---

## Schema 3: 分析结果包 — Effect Sizes, CIs, P-values, Safety Events

**生产者**: `analysis-exec` (Stage 3)
**消费者**: `calibration` (校准) / `report` (Stage 4) / `pipeline` (checkpoint)

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `analysis_id` | string | 分析标识（如 `ANA-01-ITT-DFS`） |
| `estimand_id` | string | 对应 Schema 2 的 estimand ID |
| `analysis_population` | enum | `"ITT"` / `"mITT"` / `"PP"` / `"safety"` / `"PK"` |
| `effect_estimate` | object | 效应量估计值 |
| `confidence_interval` | object | 置信区间 |
| `p_value` | float | 假设检验 p 值 |
| `conclusion` | enum | `"significant_favor_intervention"` / `"significant_favor_comparator"` / `"non_significant"` / `"non_inferiority_met"` / `"non_inferiority_not_met"` |
| `assumption_checks` | object | 模型假设验证结果 |
| `software` | object | 软件版本及包信息 |
| `timestamp` | string | ISO 8601 时间戳 |

### 效应量对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `measure` | enum | `"HR"` / `"OR"` / `"RR"` / `"RD"` / `"MD"` / `"SMD"` / `"AUC"` / `"sensitivity"` / `"specificity"` / `"NNT"` / `"ARR"` |
| `point_estimate` | float | 点估计值 |
| `ci_lower` | float | 置信区间下限 |
| `ci_upper` | float | 置信区间上限 |
| `ci_level` | float | 置信水平（通常 0.95） |

### 假设检验结果

| 字段 | 类型 | 说明 |
|------|------|------|
| `test_name` | string | 检验名称（如 "Log-rank test (stratified)", "Cox PH (stratified)"） |
| `statistic_name` | string | 检验统计量名称（"z", "χ²", "F", "t"） |
| `statistic_value` | float | 检验统计量值 |
| `df` | float | 自由度 |
| `assumption_violations` | list[string] | 假设违反项（如 "PH assumption violated at p=0.03; time-varying coefficients used"） |

### 安全性数据包（如适用）

| 字段 | 类型 | 说明 |
|------|------|------|
| `treatment_related_ae` | list[AE] | 治疗相关不良事件 |
| `serious_ae` | list[AE] | 严重不良事件 (SAE) |
| `deaths` | integer | 死亡人数 |
| `sae_deaths` | integer | SAE 相关死亡 |
| `dose_modifications` | object | 剂量调整汇总 |
| `discontinuations` | object | 因 AE 停药汇总 |

### AE 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `term` | string | 不良事件名称（MedDRA PT） |
| `grade` | enum | `"1"` / `"2"` / `"3"` / `"4"` / `"5"` (CTCAE v5.0) |
| `organ_system` | string | 器官系统分类 |
| `intervention_related` | boolean | 是否与试验药物相关 |
| `n_events` | integer | 事件数 |
| `n_patients` | integer | 发生患者数 |
| `incidence_rate` | float | 发生率（%） |

### 示例

```markdown
## 分析结果包 — ANA-01-ITT-DFS

**Analysis ID**: ANA-01-ITT-DFS
**Estimand**: EST-01 (3-year DFS, treatment policy composite)
**Population**: ITT (N = 1182, CAPOX 591, FOLFOX4 591)

### Primary Result
- **Measure**: Hazard Ratio
- **Point Estimate**: 0.88 (95% CI: 0.72–1.08)
- **P-value**: 0.22 (one-sided, non-inferiority test)
- **Conclusion**: Non-inferiority met (HR upper CI bound 1.08 < margin 1.20)

### Secondary Results
| Endpoint | HR/OR/RR | 95% CI | p-value | Conclusion |
|----------|----------|--------|---------|------------|
| Overall Survival | HR 0.91 | 0.68–1.21 | 0.52 | Non-significant |
| Grade ≥3 TEAE | OR 0.95 | 0.71–1.27 | 0.73 | Non-significant |

### Assumption Checks
- PH assumption: Schoenfeld residuals p = 0.31 (met)
- Proportionality: Scaled Schoenfeld residuals show no time-dependent trend
- Collinearity: VIF < 2.0 for all covariates

### Safety Summary (CTCAE v5.0)
- Treatment-related AE: CAPOX 82.4% vs FOLFOX4 85.1% (p=0.21)
- Grade ≥3 TEAE: CAPOX 41.2% vs FOLFOX4 43.8% (p=0.38)
- SAE: CAPOX 12.3% vs FOLFOX4 14.1% (p=0.35)
- Deaths: CAPOX 3.2% vs FOLFOX4 3.7% (p=0.64)

### Software
- R 4.3.2 with survival 3.5-7, survminer 0.4.9
- SAS 9.4 PROC PHREG (primary confirmation)
```

---

## Schema 4: 临床报告包 — CONSORT/STROBE Tables, Figures, Methods

**生产者**: `report` (Stage 4) / `report` (Stage 5, 论文写作模式)
**消费者**: `pipeline` (Stage 4 checkpoint) / `report` (Stage 5)

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `report_type` | enum | `"CONSORT"` / `"STROBE"` / `"PRISMA"` / `"STARD"` / `"TRIPOD"` / `"PRISMA-SR"` / `"statistical_report"` |
| `title` | string | 报告标题 |
| `sections` | list[ReportSection] | 报告各节内容 |
| `tables` | list[Table] | 统计表格 |
| `figures` | list[Figure] | 统计图表 |
| `flow_diagram` | object | 流程图数据（CONSORT 流程图等） |
| `word_count` | integer | 总字数 |
| `reporting_guideline` | enum | 报告规范名称（同 report_type） |
| `checklist_compliance` | object | 报告规范条目合规状态 |

### ReportSection 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `heading` | string | 节标题 |
| `level` | integer | 标题级别（1-3） |
| `content` | string | 完整节内容 |
| `word_count` | integer | 该节字数 |
| `checklist_items` | list[string] | 对应报告规范的条目编号（如 "CONSORT-1", "STROBE-4a"） |

### Table 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 表格唯一 ID（如 `T1`, `T2`） |
| `title` | string | 表格标题 |
| `type` | enum | `"demographic"` / `"efficacy"` / `"safety"` / `"subgroup"` / `"sensitivity"` / `"p_value_multiplicity"` |
| `footnotes` | list[string] | 表注（统计符号、定义、注释） |
| `reporting_guideline_ref` | string | 对应报告规范条目 |
| `cross_validation_status` | enum | `"verified"` / `"discrepancy"` / `"pending"` |

### Figure 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 图表唯一 ID（如 `F1`, `F2`） |
| `title` | string | 图表标题 |
| `type` | enum | `"kaplan_meier"` / `"forest_plot"` / `"funnel_plot"` / `"bar_chart"` / `"box_plot"` / `"waterfall"` / `"swimmer_plot"` / `"calibration_curve"` / `"roc_curve"` |
| `file_path` | string | 图表文件路径 |
| `panel_count` | integer | 图表 panel 数量 |

### 流程图对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | enum | `"consort"` / `"prisma"` / `"stard"` / `"tripod"` |
| `enrollment` | object | `{screened: int, eligible: int, randomized: int}` |
| `allocation` | object | `{intervention: int, comparator: int}` |
| `follow_up` | object | `{lost_to_followup_intervention: int, lost_to_followup_comparator: int}` |
| `analysis` | object | `{analyzed_intervention: int, analyzed_comparator: int, excluded_intervention: int, excluded_comparator: int}` |

### Checklist 合规对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `total_items` | integer | 规范总条目数 |
| `addressed` | integer | 已报告条目数 |
| `partially_addressed` | integer | 部分报告条目数 |
| `not_addressed` | integer | 未报告条目数 |
| `compliance_rate` | float | 合规率（%） |
| `missing_items` | list[string] | 未报告的条目编号列表 |

### 示例

```markdown
## 临床报告包

**Report Type**: CONSORT 2010
**Title**: CAPOX versus FOLFOX4 as Adjuvant Chemotherapy for Stage II-III Colorectal Cancer: A Randomized Non-Inferiority Trial

### Flow Diagram (CONSORT)
- Screened: 1580
- Eligible: 1340
- Randomized: 1200 (CAPOX 600, FOLFOX4 600)
- Lost to follow-up: CAPOX 9 (1.5%), FOLFOX4 19 (3.2%)
- Analyzed ITT: CAPOX 591, FOLFOX4 591

### Tables
- T1: Baseline Demographics (STROBE-4a)
- T2: Primary Efficacy Analysis (ITT) (CONSORT-17a)
- T3: Secondary Efficacy Analysis (CONSORT-17a)
- T4: Summary of TEAEs by System Organ Class (CONSORT-19a)
- T5: Grade ≥3 TEAEs (CONSORT-19a)
- T6: Subgroup Analysis (Forest Plot Data)
- T7: Sensitivity Analysis (Missing Data)

### Figures
- F1: Kaplan-Meier Curve — DFS (ITT)
- F2: Forest Plot — Subgroup Analysis DFS
- F3: CONSORT Flow Diagram

### Checklist Compliance
- Total items: 25 (CONSORT 2010)
- Addressed: 23 (92.0%)
- Partially addressed: 1 (4.0%)
- Not addressed: 1 (4.0%) — Item 24 (Trial registration number)
- Compliance Rate: 96.0%
```

---

## Schema 5: 校准报告 — Gold Standard Comparison & Confusion Matrix

**生产者**: `calibration` (Utility skill)
**消费者**: `analysis-exec` (Stage 3) / `report` (Stage 4)

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `calibration_id` | string | 校准报告 ID |
| `target_software` | string | 被校准软件（如 "R v4.3 survival"） |
| `gold_standard` | string | 金标准软件/参考结果（如 "SAS v9.4 PROC PHREG"） |
| `test_cases` | list[TestCase] | 测试用例列表 |
| `confusion_matrix` | object | 分类一致性矩阵 |
| `numerical_precision` | object | 数值精度评估 |
| `overall_verdict` | enum | `"CONCORDANT"` / `"MINOR_DISCREPANCY"` / `"MATERIAL_DISCREPANCY"` |
| `timestamp` | string | ISO 8601 时间戳 |

### 测试用例对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `test_id` | string | 测试用例 ID |
| `description` | string | 用例描述 |
| `target_result` | object | `{point_estimate: float, ci_lower: float, ci_upper: float, p_value: float}` |
| `gold_result` | object | 同上 |
| `abs_diff` | object | 绝对差值（同结构） |
| `relative_diff` | float | 相对差值（%） |
| `verdict` | enum | `"match"` / `"minor_diff"` / `"mismatch"` |

### 混淆矩阵对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `true_positive` | integer | 金标准阳性 & 本软件阳性 |
| `false_positive` | integer | 金标准阴性 & 本软件阳性 |
| `true_negative` | integer | 金标准阴性 & 本软件阴性 |
| `false_negative` | integer | 金标准阳性 & 本软件阴性 |
| `sensitivity` | float | 灵敏度 |
| `specificity` | float | 特异度 |
| `ppv` | float | 阳性预测值 |
| `npv` | float | 阴性预测值 |
| `kappa` | float | Cohen's Kappa 一致性系数 |
| `accuracy` | float | 总体准确率 |

### 数值精度对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `max_abs_error` | float | 最大绝对误差 |
| `mean_abs_error` | float | 平均绝对误差 |
| `max_rel_error` | float | 最大相对误差 |
| `within_tolerance` | float | 在预设容差范围内的比例（%） |
| `tolerance_threshold` | string | 容差阈值（如 "1e-6 for p-values, 1e-4 for estimates"） |

### 示例

```markdown
## 校准报告 — CAL-2026-001

**Target Software**: R v4.3.2 survival::coxph
**Gold Standard**: SAS v9.4 PROC PHREG

### Test Cases
| Test ID | Description | R (HR) | SAS (HR) | Abs Diff | Verdict |
|---------|-------------|--------|----------|----------|---------|
| TC-01 | Primary Cox, stratified | 0.88 (0.72,1.08) | 0.88 (0.72,1.08) | 0.000 | match |
| TC-02 | Unadjusted Cox | 0.91 (0.75,1.11) | 0.91 (0.75,1.11) | 0.000 | match |
| TC-03 | Subgroup: stage III | 0.82 (0.65,1.04) | 0.82 (0.65,1.04) | 0.000 | match |
| TC-04 | Fine-Gray competing risk | 0.89 (0.72,1.09) | 0.89 (0.72,1.10) | 0.001 | match |

### Confusion Matrix (Recurrence Classification)
- Sensitivity: 98.2% | Specificity: 97.5%
- PPV: 96.8% | NPV: 98.7%
- Kappa: 0.956 | Accuracy: 97.8%

### Numerical Precision
- Max absolute error: 0.002
- Mean absolute error: 0.0003
- Within 1e-6 tolerance: 99.7% of estimates
- Within 1e-4 tolerance: 100% of estimates

**Overall Verdict**: CONCORDANT
```

---

## Schema 6: 论文手稿 — IMRaD Structure, Bilingual Abstract, References

**生产者**: `report` (Stage 5, 论文写作模式)
**消费者**: `peer-review` (评审) / `pipeline` (handoff)

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | object | `{en: string, zh: string}` 双语标题 |
| `abstract` | object | `{en: BilingualAbstract, zh: BilingualAbstract}` 双语结构化摘要 |
| `keywords` | object | `{en: list[string], zh: list[string]}` 各 3-6 个关键词 |
| `sections` | list[Section] | IMRaD 结构化的论文各节 |
| `references` | list[Reference] | 完整参考文献列表 |
| `total_word_count` | integer | 总字数（不含参考文献） |
| `citation_format` | enum | `"Vancouver"` / `"APA7"` / `"AMA"` |
| `target_journal` | object | 目标期刊信息 |
| `icmje_compliance` | object | ICMJE 条目合规状态 |

### 结构化摘要对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `background` | string | 背景（≤150 词） |
| `methods` | string | 方法（≤150 词） |
| `results` | string | 结果（≤150 词） |
| `conclusions` | string | 结论（≤150 词） |
| `trial_registration` | string | 试验注册信息 |
| `funding` | string | 资助信息 |
| `word_count` | integer | 摘要总词数 |

### Section 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `heading` | string | 节标题 |
| `level` | integer | 标题级别（1-3） |
| `content` | string | 完整节内容 |
| `word_count` | integer | 该节字数 |
| `citation_count` | integer | 节内引用数 |
| `checklist_items` | list[string] | 对应 EQUATOR 清单条目 |

### 参考文献对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 唯一 ID（如 `REF-01`） |
| `full_citation` | string | 完整引用 |
| `doi` | string | DOI（如有） |
| `cited_in_sections` | list[string] | 引用所在节 |
| `retraction_checked` | boolean | 是否经 Retraction Watch 核查 |

### 目标期刊对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 期刊名称 |
| `issn` | string | ISSN |
| `impact_factor` | float | 影响因子 |
| `category` | string | JCR 分区 |
| `word_limit` | integer | 字数限制 |
| `reference_format` | string | 引用格式要求 |
| `structured_abstract` | boolean | 是否要求结构化摘要 |

### ICMJE 合规对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `authorship_criteria` | list[string] | ICMJE 四条作者标准满足状态 |
| `icmje_form_completed` | boolean | ICMJE 作者贡献表是否完成 |
| `conflict_of_interest` | string | 利益冲突声明 |
| `data_sharing_statement` | string | 数据共享声明 |
| `ethics_approval` | string | 伦理审批信息（IRB 编号） |
| `informed_consent` | string | 知情同意声明 |

### 示例

```markdown
## 论文手稿

**Title (EN)**: Adjuvant CAPOX versus FOLFOX4 in Stage II-III Colorectal Cancer: A Randomized Non-Inferiority Trial
**Title (ZH)**: CAPOX与FOLFOX4辅助化疗治疗II-III期结直肠癌的随机非劣效性试验

**Structured Abstract (EN)**:
- Background: The optimal adjuvant regimen for stage II-III CRC remains debated.
- Methods: Multicenter, open-label, randomized, non-inferiority trial (NCT00000001). Primary endpoint: 3-year DFS.
- Results: 1182 patients analyzed (ITT). 3-year DFS: 72.1% (CAPOX) vs 69.8% (FOLFOX4). HR 0.88 (95% CI: 0.72–1.08). Non-inferiority met.
- Conclusions: CAPOX is non-inferior to FOLFOX4 with comparable safety, supporting CAPOX as a preferred option for convenience.

**Target Journal**: Journal of Clinical Oncology (JCO)
- ISSN: 0732-183X | Impact Factor: 45.3 | Category: Q1 Oncology
- Word Limit: 4000 | Reference Format: Vancouver | Structured Abstract: Yes

**ICMJE Compliance**:
- Authorship criteria: All 4 criteria met
- ICMJE form: Completed
- COI: All authors declare no conflicts
- Ethics: IRB approved (Center 1: IRB-2024-001; Center 2: IRB-2024-002)
- Informed consent: Written informed consent obtained from all participants
```

---

## Schema 7: 审稿意见 — ICMJE Standards & Revision Roadmap

**生产者**: `peer-review` (5 审稿人模式)
**消费者**: `report` (revision mode) / `pipeline` (checkpoint)

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `editorial_decision` | enum | `"Accept"` / `"Minor Revision"` / `"Major Revision"` / `"Reject"` |
| `reviewer_reports` | list[ReviewerReport] | 各审稿人报告 |
| `consensus` | enum | `"CONSENSUS-4"` / `"CONSENSUS-3"` / `"SPLIT"` / `"DA-CRITICAL"` |
| `revision_roadmap` | list[RoadmapItem] | 按优先级排列的修改事项 |
| `icmje_compliance_review` | object | ICMJE 条目审查结果 |

### ReviewerReport 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `reviewer_id` | string | 审稿人标识（`EIC`, `R1`, `R2`, `R3`, `DA`） |
| `role` | string | 角色描述（如 "统计学审稿人", "方法学审稿人", "临床审稿人"） |
| `dimension_scores` | object | 各维度评分（临床研究特异性维度） |
| `strengths` | list[string] | 论文优势 |
| `weaknesses` | list[Weakness] | 论文不足 |
| `questions` | list[string] | 要求作者回答的问题 |
| `icmje_flags` | list[string] | ICMJE 合规问题标记 |

### 临床研究特异性审稿维度

| 维度 | 说明 |
|------|------|
| `study_design` | 研究设计合理性 |
| `statistical_rigor` | 统计方法严谨性 |
| `clinical_relevance` | 临床相关性与重要性 |
| `safety_reporting` | 安全性报告完整性 |
| `ethical_compliance` | 伦理合规（知情同意、IRB、注册） |
| `reporting_transparency` | 报告透明度（CONSORT/STROBE 合规） |
| `overall` | 总体评分 |

### Weakness 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `description` | string | 不足描述 |
| `severity` | enum | `"critical"` / `"major"` / `"minor"` |
| `type` | enum | `"design"` / `"statistics"` / `"safety"` / `"ethics"` / `"reporting"` / `"clinical"` |

### RoadmapItem 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 唯一 ID（如 `REV-001`） |
| `description` | string | 修改事项描述 |
| `reviewer` | string | 提出者（如 `R1, R3`） |
| `type` | enum | `"Major"` / `"Minor"` / `"Editorial"` |
| `priority` | enum | `"must_fix"` / `"should_fix"` / `"consider"` |
| `target_section` | string | 目标节段 |
| `suggested_action` | string | 建议修改方式 |
| `consensus_level` | enum | `"CONSENSUS-4"` / `"CONSENSUS-3"` / `"SPLIT"` / `"DA-CRITICAL"` |
| `verification_criteria` | string | 验证修改是否充分的标准 |

### ICMJE 审查对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `total_flags` | integer | ICMJE 合规问题总数 |
| `critical_flags` | list[string] | 严重合规问题（如缺 IRB 审批、缺注册号） |
| `moderate_flags` | list[string] | 中等合规问题 |
| `minor_flags` | list[string] | 轻微合规问题 |

### 示例

```markdown
## 审稿意见

**Editorial Decision**: Major Revision
**Consensus**: CONSENSUS-4

### ICMJE Compliance Review
- Critical flags: None
- Moderate flags: Data sharing statement missing; Protocol not publicly available
- Minor flags: Author contributions table uses non-standard format

### Revision Roadmap

| ID | Priority | Reviewer | Section | Issue | Action |
|----|----------|----------|---------|-------|--------|
| REV-001 | must_fix | R1, R2 | Methods | Sample size calculation not reported | Add formal power analysis |
| REV-002 | must_fix | R1, R3 | Methods | Missing sensitivity analyses for missing data | Add MI + tipping-point analyses |
| REV-003 | must_fix | EIC | Methods | IRB approval numbers not listed | Add IRB approval for each center |
| REV-004 | should_fix | R2, DA | Discussion | No comparison with recent meta-analysis | Add comparison with Chen 2025 meta-analysis |
| REV-005 | should_fix | R1 | Results | Subgroup analysis p-values not adjusted | Add Bonferroni correction or hierarchical testing |
| REV-006 | minor | R3 | Abstract | Word count exceeds 350 | Reduce to ≤350 words |
```

---

## Schema 8: 交接完整性 — HANDOFF_INCOMPLETE Failure Convention

**生产者**: 任何 stage 的 agent
**消费者**: `pipeline` (orchestrator) / 下游 stage 的 agent

### HANDOFF_INCOMPLETE 触发条件

当消费方 agent 在接收上游 artifact 时发现以下任一情况，必须立即触发 `HANDOFF_INCOMPLETE` 失败路径，不得使用不完整数据继续：

| # | 失败条件 | 说明 |
|---|----------|------|
| F1 | 必填字段缺失 | Schema 中标记为必填的字段未出现 |
| F2 | 类型不匹配 | 字段值类型与 schema 定义不符 |
| F3 | 枚举值非法 | enum 类型字段的值不在允许集合中 |
| F4 | 跨引用断裂 | 引用的 ID 在上游 artifact 中不存在（如 estimand_id 在 SAP 中找不到） |
| F5 | 临床数据缺失 | 临床研究关键数据缺失（如样本量、主要终点、p 值、效应量） |
| F6 | 安全性数据缺失 | 安全性分析结果缺失（如 AE 汇总、SAE 数据） |
| F7 | 注册信息缺失 | 临床试验注册信息缺失（适用于 RCT） |
| F8 | 伦理审批缺失 | IRB/伦理委员会审批信息缺失 |
| F9 | Material Passport 缺失 | 交接 artifact 未携带 passport 或 passport 必填字段缺失 |
| F10 | 版本不一致 | passport 中 version_label 与实际内容不匹配 |

### HANDOFF_INCOMPLETE 消息格式

```markdown
## HANDOFF_INCOMPLETE

**Source Stage**: Stage <N>
**Target Stage**: Stage <M>
**Producer**: <agent_name>
**Consumer**: <agent_name>
**Timestamp**: <ISO 8601>

### Missing Fields
- `<schema_field_1>`: <reason_for_missing>
- `<schema_field_2>`: <reason_for_missing>

### Type Violations
- `<field>`: expected `<type>`, got `<actual_type>`

### Cross-Reference Errors
- `<reference_id>` referenced in <field> not found in upstream artifact

### Required Actions
1. Producer must regenerate the artifact with all missing fields
2. Consumer must NOT proceed with partial data
3. Pipeline orchestrator is notified and halts downstream progress
```

### 失败处理流程

```
Agent 发现 HANDOFF_INCOMPLETE
  ↓
向 pipeline orchestrator 报告失败
  ↓
Orchestrator 通知生产方 agent
  ↓
生产方 agent 重新生成完整 artifact
  ↓
消费方 agent 重新验证
  ├── 通过 → 继续流水线
  └── 再次失败 → 第二次 HANDOFF_INCOMPLETE
        ↓
      连续 3 次失败 → 人工干预
        ↓
      人工检查 → 修改或中止
```

---

## 验证规则

1. **必填字段检查**: 所有 schema 中标记为必填的字段必须存在。消费方 agent 在继续前必须验证所有必填字段
2. **类型检查**: 字段值必须匹配声明的类型（如 enum 值必须来自允许集合）
3. **跨引用检查**: 分析结果中引用的 estimand_id 必须在 SAP (Schema 2) 中存在；论文中的引用 ID 必须在参考文献列表中存在
4. **版本跟踪**: 每个交接 artifact 必须携带 Material Passport（Schema 9）并包含 version_label。版本标签在同一次流水线运行中必须单调递增
5. **缺失时失败**: 必填字段缺失时返回 `HANDOFF_INCOMPLETE` 并列出缺失字段；不得使用不完整数据继续
6. **生产方验证**: 生产方 agent 在交接前必须对照 schema 验证输出
7. **消费方验证**: 消费方 agent 在接收时应验证输入，发现违规则要求重新生成
8. **完整性门控**: 通过校准验证（Schema 5）的 artifact，其 Material Passport 必须更新 `verification_status: "VERIFIED"` 和 `integrity_pass_date`
9. **时效检测**: 若上游 artifact 在下游 artifact 生成后被修改，下游 artifact 的 Material Passport 应更新为 `verification_status: "STALE"`
10. **Passport 时效**: Material Passport 的校准结果在 `integrity_pass_date` 超过 24 小时后视为 STALE。过期 passport 需重新验证后方可继续
11. **临床试验注册强制**: 涉及 RCT 的研究，Schema 1 的 `study_registration` 和 Schema 6 的 `trial_registration` 均为强制字段，缺失将触发 F7
12. **安全性数据完整性**: Schema 3 的安全性数据包（如适用）必须包含 CTCAE 分级汇总。缺失将触发 F6

## 数据访问级别 (data_access_level)

每个顶级 `SKILL.md` 声明 `metadata.data_access_level`：

- `raw` — 消费未验证来源；必须假设数据可能含有错误
- `redacted` — 操作脱敏后的材料；不引入新的原始数据
- `verified_only` — 仅在上游完整性门控通过后运行

这是声明性信号（非运行时权限系统）。由 CI 中的 `scripts/check_data_access_level.py` 执行。添加新 skill 时，选择与其合法消费的"最脏"输入匹配的值。

## 任务类型 (task_type)

每个顶级 `SKILL.md` 声明 `metadata.task_type`：

- `outcome-gradable` — 任务有客观的标量指标；第三方可在不依赖深度上下文的情况下评分
- `open-ended` — 任务质量取决于领域判断、解释性工作或指标无法捕获的上下文
