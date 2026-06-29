<!--
MSRA 项目专用模板 | Stage 3.5 结果质量门闸报告
================================================================
用途：analysis-exec 阶段完成后，由 QC Inspector 执行结果质量审查，输出本报告。
定位：进入 Stage 4（统计报告）前的强制门闸。
原则：只检查不修改。谁产出谁不审查自己。
依据：APA 7th、CONSORT/STROBE/STARD/PRISMA 报告规范、REPRO/OSIRIS 可重复性框架。
关键项：1/3/4（未通过强制退回 Stage 3）。
================================================================
-->

---
study_id: "[{MSRA-YYYY-NNN}]"
gate_stage: "stage_3.5"
gate_name: "结果质量门闸 / Results Quality Gate"
version: "v1.0"
assessed_at: "[{YYYY-MM-DDTHH:MM:SS+08:00}]"
assessor: "[{QC Inspector 标识}]"
assessor_role: "qc_inspector"
passport_ref: "MSRA/passport.json#gates.stage_3.5"
producer_stage: "stage_3"
consumer_stage: "stage_4"
status: "draft"  # draft / conditional / passed / blocked
total_items: 9
passed_items: "[{通过项数}]"
key_items: [1, 3, 4]
---

# 结果质量门闸报告 (Stage 3.5 Results Quality Gate Report)

> **审查对象**：Stage 3 (analysis-exec) 产出的分析结果、表格、图表、敏感性分析结果、复现日志。
> **判定规则**：全部通过 → 进入 Stage 4 / 1-2 项未过 → 条件通过 / 3+ 项未过或关键项(1/3/4)未过 → 阻断退回 Stage 3。

---

## 1. 执行摘要 (Executive Summary)

| 项目 | 内容 |
|------|------|
| 研究编号 / Study ID | [{MSRA-YYYY-NNN}] |
| 研究类型 / Study Type | [{RCT / 观察性 / 诊断 / 真实世界}] |
| SAP 版本 / SAP Version | [{v1.0}] |
| 审查时间 / Assessed At | [{YYYY-MM-DD HH:MM}] |
| 审查员 / Assessor | [{QC Inspector 标识}] |
| 通过项数 / Passed Items | [{X}] / 9 |
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
| 1 | 结果完整性 / Results Completeness (SAP 对齐) | 🔑 | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 2 | 假设验证 / Assumption Verification | | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 3 | 数值一致性 / Numerical Consistency | 🔑 | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 4 | 敏感性分析 / Sensitivity Analysis | 🔑 | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 5 | 效应量报告 / Effect Size Reporting | | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 6 | 异常结果标记 / Anomalous Results Flagging | | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 7 | 结果复现 / Results Reproducibility (3 次重跑) | | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 8 | [SKIP] 标记 / Skip Marking | | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 9 | 校准置信度 / Calibration Confidence | | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |

### 2.2 检查项 1：结果完整性 / Results Completeness 🔑

- **检查内容**：SAP 中所有计划的分析是否已全部执行并产出结果。
- **检查方法**：
  1. 读取 SAP §4 统计方法清单和 §8 分析规范表。
  2. 逐项核对 `results/` 目录下是否有对应输出（表格 .docx / 图表 .png / 数据 .csv）。
  3. 未执行的分析必须有 [SKIP] 标记和理由（见检查项 8）。
- **通过标准**：SAP 计划分析 100% 执行或合理 SKIP。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{SAP 分析清单、已执行数、缺失数}]

### 2.3 检查项 2：假设验证 / Assumption Verification

- **检查内容**：所有统计方法的假设条件是否已检验并满足。
- **检查方法**：
  1. 读取假设检验报告 `results/hypothesis_test_report.md`。
  2. 核对每个方法对应的假设（正态性、方差齐性、线性性、比例风险、多重共线性）已检验。
  3. 假设不满足时已切换备选方法（对齐 SAP Stage 2.5 检查项 5）。
- **通过标准**：所有假设已检验，不满足项有备选方案。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{假设检验报告路径、未满足假设清单}]

### 2.4 检查项 3：数值一致性 / Numerical Consistency 🔑

- **检查内容**：报告中引用的数字与分析输出原始数据一致。
- **检查方法**：
  1. 抽取报告中 10 个关键数字（p 值、效应量、CI、样本量）。
  2. 与 `results/` 下的原始输出文件逐项核对。
  3. 运行 `src/shared/reporting-guidelines/statcheck_patterns.py` 自动校验。
- **通过标准**：10/10 一致，无四舍五入错误超 0.001。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{抽样核对表、statcheck 输出}]

### 2.5 检查项 4：敏感性分析 / Sensitivity Analysis 🔑

- **检查内容**：敏感性分析结果是否与主分析结论一致。
- **检查方法**：
  1. 读取 SAP §4.x 计划的敏感性分析（至少 2 种，对齐 Stage 2.5 检查项 6）。
  2. 核对每种敏感性分析的结论方向（正向/负向/无显著差异）与主分析一致。
  3. 结论不一致时必须有详细说明。
- **通过标准**：敏感性分析结论与主分析一致，或不一致有合理解释。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{敏感性分析结果对比表}]

### 2.6 检查项 5：效应量报告 / Effect Size Reporting

- **检查内容**：所有主要结果是否报告效应量及 95% 置信区间（APA 7th 强制要求）。
- **检查方法**：
  1. 核对主要结果表含：效应量（OR/RR/HR/RD/MD/Cohen's d）+ 95% CI + p 值。
  2. 仅报告 p 值不报告效应量 = FAIL（对齐 APA 7th §6.45）。
  3. 见 §3 APA 7th 效应量强制报告矩阵。
- **通过标准**：所有主要结果含效应量 + 95% CI。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{效应量报告清单}]

### 2.7 检查项 6：异常结果标记 / Anomalous Results Flagging

- **检查内容**：意外结果（与预期方向相反、p 值极小、效应量异常大）是否已标记并说明。
- **检查方法**：
  1. 识别异常结果：效应量 > 预期 2 倍、p < 0.001 且样本量小、方向与生物学先验相反。
  2. 每个异常结果有"异常说明"段落。
  3. 异常结果未经"选择性报告"（无 p-hacking 痕迹）。
- **通过标准**：所有异常结果已标记并说明。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{异常结果清单、说明段落}]

### 2.8 检查项 7：结果复现 / Results Reproducibility

- **检查内容**：关键分析结果 3 次重跑是否一致。
- **检查方法**：
  1. 在相同环境下运行分析脚本 3 次（固定随机种子）。
  2. 比较 3 次输出的关键数值（效应量、CI、p 值）。
  3. 数值差异 < 1e-6（浮点精度误差范围内）。
- **通过标准**：3 次重跑结果一致。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{3 次重跑日志、数值比对表}]

### 2.9 检查项 8：[SKIP] 标记 / Skip Marking

- **检查内容**：跳过的分析是否有 [SKIP] 标记和合理理由。
- **检查方法**：
  1. 核对 SAP 计划分析中标记为 [SKIP] 的项。
  2. 每个 [SKIP] 含：跳过原因（数据不足 / 不适用 / 技术限制）、影响评估、替代方案。
  3. 无 [SKIP] 标记的缺失分析 = FAIL。
- **通过标准**：所有跳过分析有 [SKIP] 标记和理由。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{SKIP 清单}]

### 2.10 检查项 9：校准置信度 / Calibration Confidence

- **检查内容**：分析结果的校准置信度是否达到阈值。
- **检查方法**：
  1. 读取 `src/shared/calibration/` 校准报告。
  2. 核对校准指标：Brier Score、Calibration slope、Calibration-in-the-large。
  3. 置信度 ≥ [{阈值，如 0.8}]。
- **通过标准**：校准置信度达标。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{校准报告路径、置信度值}]

---

## 3. APA 7th 效应量 + CI 强制报告矩阵 (APA 7th Effect Size Reporting Matrix)

> APA 7th Edition §6.45 强制要求报告效应量及置信区间。仅报告 p 值不符合规范。

| 研究设计 | 推荐效应量 | 95% CI | 报告格式示例 | 本次符合性 |
|---------|-----------|--------|------------|----------|
| RCT（连续结局） | Mean Difference / Cohen's d | 是 | MD = [{X.X}]，95% CI [{X.X, X.X}]，p = [{0.XXX}] | [{符合/不符合}] |
| RCT（二分类结局） | Risk Difference / OR / RR | 是 | RD = [{X.X%}]，95% CI [{X.X%, X.X%}]，p = [{0.XXX}] | [{符合/不符合}] |
| RCT（时间-事件） | Hazard Ratio | 是 | HR = [{X.XX}]，95% CI [{X.XX, X.XX}]，p = [{0.XXX}] | [{符合/不符合}] |
| 观察性（连续） | Mean Difference / SMD | 是 | SMD = [{X.XX}]，95% CI [{X.XX, X.XX}] | [{符合/不符合}] |
| 观察性（二分类） | OR / RR | 是 | OR = [{X.XX}]，95% CI [{X.XX, X.XX}] | [{符合/不符合}] |
| 诊断研究 | Sensitivity / Specificity / AUC | 是 | AUC = [{X.XX}]，95% CI [{X.XX, X.XX}] | [{符合/不符合}] |
| Meta 分析 | Pooled Effect (MD/OR/RR/HR) | 是 | pooled OR = [{X.XX}]，95% CI [{X.XX, X.XX}]，I² = [{X%}] | [{符合/不符合}] |

**效应量报告完整率**：[{X}] / [{X}]

---

## 4. 报告规范路由表 (Reporting Guideline Routing)

> 根据研究类型路由到对应的报告规范。Stage 4 报告生成时必须遵循。

| 研究类型 | 报告规范 | Checklist 路径 | 本次适用 | 符合性预检 |
|---------|---------|---------------|---------|----------|
| RCT（两臂/多臂） | CONSORT 2010 | `src/shared/reporting-guidelines/CONSORT_checklist.md` | [{是/否}] | [{符合/不符合/N/A}] |
| RCT（非劣效） | CONSORT + 非劣效扩展 | `src/shared/reporting-guidelines/CONSORT_checklist.md` | [{是/否}] | [{符合/不符合/N/A}] |
| 观察性（队列/病例对照/横断面） | STROBE | `src/shared/reporting-guidelines/STROBE_checklist.md` | [{是/否}] | [{符合/不符合/N/A}] |
| 诊断研究 | STARD 2015 | `src/shared/reporting-guidelines/STARD_checklist.md` | [{是/否}] | [{符合/不符合/N/A}] |
| 系统综述/Meta 分析 | PRISMA 2020 | `src/shared/reporting-guidelines/PRISMA_2020_checklist.md` | [{是/否}] | [{符合/不符合/N/A}] |
| 网状 Meta 分析 | PRISMA-NMA | `src/shared/reporting-guidelines/PRISMA_NMA_checklist.md` | [{是/否}] | [{符合/不符合/N/A}] |
| 预测模型（AI/ML） | TRIPOD+AI | `src/shared/reporting-guidelines/TRIPOD_AI_checklist.md` | [{是/否}] | [{符合/不符合/N/A}] |
| 预后研究 | REMARK | `src/shared/reporting-guidelines/REMARK_checklist.md` | [{是/否}] | [{符合/不符合/N/A}] |
| 卫生经济学 | CHEERS | `src/shared/reporting-guidelines/CHEERS_checklist.md` | [{是/否}] | [{符合/不符合/N/A}] |
| 真实世界研究 | RECORD（STROBE 扩展） | `src/shared/reporting-guidelines/STROBE_checklist.md` | [{是/否}] | [{符合/不符合/N/A}] |

**本次适用规范**：[{列出适用的规范名称}]
**预检结果**：[{符合项数}] / [{适用项数}]

---

## 5. REPRO/OSIRIS 可重复性检查 (Reproducibility Check)

> 参考 REPRO（Reproducibility Project）和 OSIRIS（Open Science Reproducibility）框架。

### 5.1 可重复性维度

| 维度 | 检查内容 | 状态 | 证据 |
|------|---------|------|------|
| 代码可重复 / Code Reproducible | 分析脚本可独立运行，无外部依赖缺失 | [{PASS/FAIL}] | [{脚本路径}] |
| 数据可重复 / Data Reproducible | 输入数据已锁定且可访问 | [{PASS/FAIL}] | [{数据哈希}] |
| 环境可重复 / Environment Reproducible | 软件版本、包版本已记录 | [{PASS/FAIL}] | [{sessionInfo / requirements.txt}] |
| 结果可重复 / Results Reproducible | 3 次重跑结果一致（对齐检查项 7） | [{PASS/FAIL}] | [{重跑日志}] |
| 随机性可控 / Randomness Controlled | 随机种子已固定 | [{PASS/FAIL}] | [{种子值}] |

### 5.2 可重复性等级

| 等级 | 定义 | 本次达成 |
|------|------|---------|
| Level 1 | 代码可运行 | [{是/否}] |
| Level 2 | 代码 + 数据可重复 | [{是/否}] |
| Level 3 | 代码 + 数据 + 环境可重复 | [{是/否}] |
| Level 4 | 完全可重复（含随机种子） | [{是/否}] |

**当前可重复性等级**：[{Level X}]
**推荐等级**：Level 4（监管提交要求）

---

## 6. 阻断判定 (Block Decision)

### 6.1 判定规则

| 情形 | 判定 | 后续动作 |
|------|------|---------|
| 9 项全部 PASS | **PASS** | 进入 Stage 4，更新护照 |
| 1-2 项 FAIL（非关键项） | **CONDITIONAL** | 记录偏差，进入 Stage 4 但需限期整改 |
| 3+ 项 FAIL | **BLOCKED** | 退回 Stage 3 修订 |
| 任一关键项(1/3/4) FAIL | **BLOCKED** | 退回 Stage 3 修订 |

### 6.2 本次判定

- **判定结果**：[{PASS / CONDITIONAL / BLOCKED}]
- **未通过项**：[{列出编号，如"无"或"1, 3"}]
- **未通过原因**：[{逐项说明}]
- **偏差记录**：[{如 CONDITIONAL，记录偏差内容及整改期限}]

---

## 7. 退回路径 (Return Path)

> 仅当判定为 BLOCKED 时填写。

| 项目 | 内容 |
|------|------|
| 退回阶段 / Return To | stage_3 (analysis-exec) |
| 退回原因 / Return Reason | [{关键项未通过的具体说明}] |
| 整改要求 / Remediation Requirements | [{逐项列出需修复的内容}] |
| 预期重审时间 / Expected Re-assessment | [{YYYY-MM-DD}] |
| 责任人 / Responsible | [{analysis-exec 执行者}] |

---

## 8. 护照更新 (Passport Update)

> QC Inspector 完成审查后，更新 `MSRA/passport.json` 的 gates.stage_3.5 字段。

```json
{
  "gates": {
    "stage_3.5": {
      "status": "[{passed / conditional / blocked}]",
      "passed_items": [{X}],
      "total_items": 9,
      "assessed_at": "[{YYYY-MM-DDTHH:MM:SS+08:00}]",
      "assessor": "[{QC Inspector 标识}]",
      "report_path": "reports/gate_stage_3_5_v{N}.md",
      "key_items_failed": [{关键项未通过编号列表，如空则为 []}],
      "deviations": [{偏差记录，如空则为 []}]
    }
  },
  "checkpoints": {
    "last_verified": "[{stage_3.5 如通过，否则保留原值}]",
    "resume_point": "[{stage_4 如通过，否则 stage_3}]"
  }
}
```

---

## 9. 模板使用说明 (Template Usage Instructions)

### 9.1 使用流程

1. **触发时机**：analysis-exec 阶段（Stage 3）所有产物生成完成后，由 Pipeline 编排器调用 QC Inspector。
2. **填充方式**：复制本模板，将所有 `[{占位符}]` 替换为实际值。禁止保留占位符原样输出。
3. **文件命名**：`reports/gate_stage_3_5_v{N}.md`，每次重审递增版本号。
4. **护照联动**：审查完成后必须更新 `MSRA/passport.json` 的 `gates.stage_3.5` 字段（见 §8）。
5. **不可修改原则**：QC Inspector 只填写本报告，不修改 Stage 3 任何产物。

### 9.2 关键项说明

- **检查项 1（结果完整性）**：未执行 SAP 计划分析会导致结论不完整，监管拒绝。
- **检查项 3（数值一致性）**：报告数字与原始输出不一致属于数据完整性问题。
- **检查项 4（敏感性分析）**：敏感性分析与主分析结论矛盾会动摇主结论稳健性。

### 9.3 与其他门闸的关系

| 门闸 | Stage | 模板文件 |
|------|-------|---------|
| 数据质量门闸 | 1.5 | `data_quality_gate_report.md` |
| SAP 质量门闸 | 2.5 | `sap_quality_gate_report.md` |
| 结果质量门闸 | 3.5 | `results_quality_gate_report.md`（本文件） |

### 9.4 与 Stage 4 报告生成的衔接

本门闸通过后，Stage 4（report）将基于以下产物生成统计报告：
- `results/` 下的表格（.docx）、图表（.png）、数据（.csv）
- §4 报告规范路由表确定的 Checklist
- §3 APA 7th 效应量报告矩阵
- `src/shared/reporting-guidelines/` 下对应的报告规范文件

### 9.5 依据标准

- APA 7th Edition：Publication Manual of the American Psychological Association（§6.45 效应量报告）
- CONSORT 2010：Consolidated Standards of Reporting Trials
- STROBE：Strengthening the Reporting of Observational Studies
- STARD 2015：Standards for Reporting of Diagnostic Accuracy Studies
- PRISMA 2020：Preferred Reporting Items for Systematic Reviews and Meta-Analyses
- REPRO Framework：Reproducibility Project Standards
- OSIRIS：Open Science Reproducibility Standards
- 项目内参考：`src/shared/reporting-guidelines/`、`src/shared/reproducibility/reproducibility_guide.md`
