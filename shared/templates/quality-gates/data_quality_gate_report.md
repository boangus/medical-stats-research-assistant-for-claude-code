<!--
MSRA 项目专用模板 | Stage 1.5 数据质量门闸报告
================================================================
用途：data-prep 阶段完成后，由 QC Inspector 执行质量审查，输出本报告。
定位：进入 Stage 2（分析计划）前的强制门闸。
原则：只检查不修改。谁产出谁不审查自己。
依据：ALCOA+ 9 原则、CDISC SDTM 5 维度、ICH E6(R3) GCP、FDA 21 CFR Part 11。
关键项：5/6/7/9（未通过强制退回 Stage 1）。
================================================================
-->

---
study_id: "[{MSRA-YYYY-NNN}]"
gate_stage: "stage_1.5"
gate_name: "数据质量门闸 / Data Quality Gate"
version: "v1.0"
assessed_at: "[{YYYY-MM-DDTHH:MM:SS+08:00}]"
assessor: "[{QC Inspector 标识}]"
assessor_role: "qc_inspector"
passport_ref: "MSRA/passport.json#gates.stage_1.5"
producer_stage: "stage_1"
consumer_stage: "stage_2"
status: "draft"  # draft / conditional / passed / blocked
total_items: 9
passed_items: "[{通过项数}]"
key_items: [5, 6, 7, 9]
---

# 数据质量门闸报告 (Stage 1.5 Data Quality Gate Report)

> **审查对象**：Stage 1 (data-prep) 产出的清洗数据集、清洗日志、变量字典、缺失机制评估、数据库锁定记录。
> **判定规则**：全部通过 → 进入 Stage 2 / 1-2 项未过 → 条件通过 / 3+ 项未过或关键项(5/6/7/9)未过 → 阻断退回 Stage 1。

---

## 1. 执行摘要 (Executive Summary)

| 项目 | 内容 |
|------|------|
| 研究编号 / Study ID | [{MSRA-YYYY-NNN}] |
| 研究类型 / Study Type | [{RCT / 观察性 / 诊断 / 真实世界}] |
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
| 1 | 清洗日志完整性 / Cleaning Log Completeness | | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 2 | 变量定义明确性 / Variable Definition Clarity | | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 3 | 缺失机制评估 / Missing Data Mechanism (MCAR/MAR/MNAR) | | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 4 | 盲态审核完成 / Blinded Review Completed | | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 5 | 数据库锁定确认 / Database Lock Confirmation | 🔑 | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 6 | 逻辑一致性 / Logical Consistency | 🔑 | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 7 | 值规范化完成 / Value Normalization Completed | 🔑 | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 8 | 可重复性 / Reproducibility | | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |
| 9 | 隐私合规 (PHI) / Privacy Compliance | 🔑 | [{PASS/FAIL/N/A}] | [{证据路径或备注}] |

### 2.2 检查项 1：清洗日志完整性 / Cleaning Log Completeness

- **检查内容**：所有数据变更（删除、修改、插补、衍生）是否已记录在清洗日志中。
- **检查方法**：
  1. 读取 `reports/cleaning_log_v{N}.md`，确认每条变更含：变量名、原值、新值、变更原因、操作人、时间戳。
  2. 抽样核对 5 条变更与底层数据是否一致。
  3. 确认日志含版本号和哈希值。
- **通过标准**：日志覆盖率 100%，无未记录变更。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{日志路径、抽样核对结果}]

### 2.3 检查项 2：变量定义明确性 / Variable Definition Clarity

- **检查内容**：所有变量（含衍生变量）是否有明确定义，构造逻辑可复现。
- **检查方法**：
  1. 读取变量字典 `variable_spec_v{N}.md`，核对每个变量含：名称、角色、类型、构造公式、单位/编码、切点依据、缺失处理。
  2. 衍生变量必须有公式或切点依据，禁止"探索性"无依据切点。
- **通过标准**：所有变量定义完整，无空白字段。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{变量字典路径、缺失定义数}]

### 2.4 检查项 3：缺失机制评估 / Missing Data Mechanism

- **检查内容**：缺失数据机制是否已评估并分类为 MCAR / MAR / MNAR。
- **检查方法**：
  1. 读取缺失机制评估报告，确认含：缺失率（变量级 + 记录级）、Little's MCAR 检验结果、机制判定理由。
  2. MNAR 必须有敏感性分析计划。
- **通过标准**：机制已判定，MNAR 有应对策略。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{评估报告路径、缺失率摘要}]

### 2.5 检查项 4：盲态审核完成 / Blinded Review Completed

- **检查内容**：盲态数据审核是否完成，所有数据质疑是否已解决。
- **检查方法**：
  1. 读取盲态审核报告，确认质疑清单（query log）全部状态为"已解决"。
  2. 残留质疑数 = 0。
- **通过标准**：无未解决质疑。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{审核报告路径、未解决质疑数}]

### 2.6 检查项 5：数据库锁定确认 / Database Lock Confirmation 🔑

- **检查内容**：数据库是否已锁定，锁定版本和时间戳是否记录。
- **检查方法**：
  1. 读取数据库锁定记录，确认含：锁定类型（Freeze / Soft Lock / Hard Lock）、锁定时间、操作人、数据快照哈希。
  2. 见 §3 数据库锁定三态证据表。
- **通过标准**：至少达到 Soft Lock，推荐 Hard Lock。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{锁定记录路径、锁定类型}]

### 2.7 检查项 6：逻辑一致性 / Logical Consistency 🔑

- **检查内容**：日期顺序、数值范围、跨字段逻辑是否自洽。
- **检查方法**：
  1. 运行逻辑校验脚本，检查：入组日期 ≤ 随机化日期 ≤ 首剂日期、年龄 ∈ [18, 100]、BMI ∈ [12, 60]、衍生变量与源变量一致。
  2. 异常记录数 = 0 或全部已说明。
- **通过标准**：无未说明的逻辑冲突。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{校验脚本输出、异常记录数}]

### 2.8 检查项 7：值规范化完成 / Value Normalization Completed 🔑

- **检查内容**：TCM 术语、数值变体、单位是否已规范化。
- **检查方法**：
  1. 核对 `shared/value-normalization/` 处理结果：TCM 术语映射到 GB/T 16751 标准、数值变体（如"1.0" vs "1"）已统一、单位已转换。
  2. 抽样核对 10 条记录的规范化前后值。
- **通过标准**：规范化覆盖率 100%。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{规范化报告路径、抽样结果}]

### 2.9 检查项 8：可重复性 / Reproducibility

- **检查内容**：清洗脚本是否可独立运行，输入相同原始数据能否产出相同清洗结果。
- **检查方法**：
  1. 在干净环境中运行清洗脚本 `scripts/clean_v{N}.R`（或 `.py`）。
  2. 比较输出数据集哈希值与已锁定数据集哈希是否一致。
- **通过标准**：哈希一致，无人工干预。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{脚本路径、哈希比对结果}]

### 2.10 检查项 9：隐私合规 (PHI) / Privacy Compliance 🔑

- **检查内容**：受保护健康信息 (PHI) 是否已检测并脱敏或合规处理。
- **检查方法**：
  1. 运行 PHI 检测脚本 `shared/data_sharing/deidentification.py`，扫描 18 类 HIPAA PHI 标识符。
  2. 确认脱敏策略（删除/泛化/加密）已应用，并记录在脱敏日志中。
  3. 符合 HIPAA / GDPR / 国内《个人信息保护法》要求。
- **通过标准**：无未处理的 PHI，脱敏日志完整。
- **状态**：[{PASS/FAIL/N/A}]
- **证据**：[{PHI 扫描报告路径、残留 PHI 数}]

---

## 3. 数据库锁定三态证据表 (Database Lock Three-State Evidence)

> 数据库锁定分三态，证据要求递进。Stage 1.5 至少达到 Soft Lock。

| 锁定状态 / Lock State | 定义 | 证据要求 | 当前状态 |
|----------------------|------|---------|---------|
| Freeze（冻结） | 特定字段或记录只读，其余可编辑 | 冻结范围清单 + 时间戳 + 操作人 | [{已达成/未达成}] |
| Soft Lock（软锁定） | 整库只读，但可经授权解锁修订 | 软锁时间 + 授权人签字 + 数据快照哈希 | [{已达成/未达成}] |
| Hard Lock（硬锁定） | 整库不可逆只读，仅支持新增版本 | 硬锁时间 + 数字签名 + 不可篡改审计日志 | [{已达成/未达成}] |

**当前锁定状态**：[{Freeze / Soft Lock / Hard Lock}]
**锁定时间**：[{YYYY-MM-DD HH:MM}]
**数据快照哈希**：[{sha256:...}]
**授权人**：[{姓名/角色}]

---

## 4. ALCOA+ 9 原则矩阵 (ALCOA+ Principles Matrix)

> FDA / ICH GCP 数据完整性原则。每项原则映射到本门闸检查项。

| # | ALCOA+ 原则 | 含义 | 映射检查项 | 符合性 |
|---|------------|------|-----------|--------|
| A1 | Attributable（可归因） | 数据可追溯到产生者 | 检查项 1（清洗日志） | [{符合/不符合}] |
| A2 | Legible（清晰可读） | 数据可被人读取理解 | 检查项 2（变量定义） | [{符合/不符合}] |
| C1 | Contemporaneous（同时性） | 数据产生时即记录 | 检查项 1（日志时间戳） | [{符合/不符合}] |
| O1 | Original（原始性） | 保留原始数据或核证副本 | 检查项 8（可重复性） | [{符合/不符合}] |
| A3 | Accurate（准确性） | 数据无差错且反映真实 | 检查项 6（逻辑一致性） | [{符合/不符合}] |
| C2 | Complete（完整性） | 数据无遗漏 | 检查项 1 + 3 | [{符合/不符合}] |
| C3 | Consistent（一致性） | 数据内部自洽 | 检查项 6 + 7 | [{符合/不符合}] |
| E1 | Enduring（持久性） | 数据长期可保存 | 检查项 5（数据库锁定） | [{符合/不符合}] |
| A4 | Available（可用性） | 数据可被检索查阅 | 检查项 8（可重复性） | [{符合/不符合}] |

---

## 5. CDISC SDTM 5 维度适配性检查 (CDISC SDTM 5-Dimension Adaptability)

> 若研究需提交 FDA / NMPA，建议核对 SDTM 适配性。非注册研究可标 N/A。

| # | SDTM 维度 | 检查内容 | 状态 | 备注 |
|---|----------|---------|------|------|
| D1 | 域结构 / Domain Structure | 数据集是否映射到 SDTM 域（DM/EX/AE/LB...） | [{PASS/FAIL/N/A}] | [{域映射清单}] |
| D2 | 变量命名 / Variable Naming | 变量名是否符合 SDTM 命名规范（2 字母前缀） | [{PASS/FAIL/N/A}] | [{命名例外}] |
| D3 | 受试者层级 / Subject Level | 每条记录唯一对应一个受试者（DM 域） | [{PASS/FAIL/N/A}] | [{USUBJID 唯一性}] |
| D4 | 时间变量 / Timing Variables | 日期/时间变量格式 ISO 8601 | [{PASS/FAIL/N/A}] | [{格式例外}] |
| D5 | 衍生变量 / Derived Variables | 衍生变量有 --DTRESC 文本值或公式记录 | [{PASS/FAIL/N/A}] | [{衍生变量清单}] |

---

## 6. 阻断判定 (Block Decision)

### 6.1 判定规则

| 情形 | 判定 | 后续动作 |
|------|------|---------|
| 9 项全部 PASS | **PASS** | 进入 Stage 2，更新护照 |
| 1-2 项 FAIL（非关键项） | **CONDITIONAL** | 记录偏差，进入 Stage 2 但需限期整改 |
| 3+ 项 FAIL | **BLOCKED** | 退回 Stage 1 修订 |
| 任一关键项(5/6/7/9) FAIL | **BLOCKED** | 退回 Stage 1 修订 |

### 6.2 本次判定

- **判定结果**：[{PASS / CONDITIONAL / BLOCKED}]
- **未通过项**：[{列出编号，如"无"或"5, 7"}]
- **未通过原因**：[{逐项说明}]
- **偏差记录**：[{如 CONDITIONAL，记录偏差内容及整改期限}]

---

## 7. 退回路径 (Return Path)

> 仅当判定为 BLOCKED 时填写。

| 项目 | 内容 |
|------|------|
| 退回阶段 / Return To | stage_1 (data-prep) |
| 退回原因 / Return Reason | [{关键项未通过的具体说明}] |
| 整改要求 / Remediation Requirements | [{逐项列出需修复的内容}] |
| 预期重审时间 / Expected Re-assessment | [{YYYY-MM-DD}] |
| 责任人 / Responsible | [{data-prep 执行者}] |

---

## 8. 护照更新 (Passport Update)

> QC Inspector 完成审查后，更新 `MSRA/passport.json` 的 gates.stage_1.5 字段。

```json
{
  "gates": {
    "stage_1.5": {
      "status": "[{passed / conditional / blocked}]",
      "passed_items": [{X}],
      "total_items": 9,
      "assessed_at": "[{YYYY-MM-DDTHH:MM:SS+08:00}]",
      "assessor": "[{QC Inspector 标识}]",
      "report_path": "reports/gate_stage_1_5_v{N}.md",
      "key_items_failed": [{关键项未通过编号列表，如空则为 []}],
      "deviations": [{偏差记录，如空则为 []}]
    }
  },
  "checkpoints": {
    "last_verified": "[{stage_1.5 如通过，否则保留原值}]",
    "resume_point": "[{stage_2 如通过，否则 stage_1}]"
  }
}
```

---

## 9. 模板使用说明 (Template Usage Instructions)

### 9.1 使用流程

1. **触发时机**：data-prep 阶段（Stage 1）所有产物生成完成后，由 Pipeline 编排器调用 QC Inspector。
2. **填充方式**：复制本模板，将所有 `[{占位符}]` 替换为实际值。禁止保留占位符原样输出。
3. **文件命名**：`reports/gate_stage_1_5_v{N}.md`，每次重审递增版本号。
4. **护照联动**：审查完成后必须更新 `MSRA/passport.json` 的 `gates.stage_1.5` 字段（见 §8）。
5. **不可修改原则**：QC Inspector 只填写本报告，不修改 Stage 1 任何产物。

### 9.2 关键项说明

- **检查项 5（数据库锁定）**：未锁定的数据可能被篡改，无法保证分析结果可重复。
- **检查项 6（逻辑一致性）**：逻辑冲突会导致分析结论错误。
- **检查项 7（值规范化）**：未规范化的值会导致分组错误或统计偏差。
- **检查项 9（隐私合规）**：PHI 泄露涉及法律合规风险，必须零容忍。

### 9.3 与其他门闸的关系

| 门闸 | Stage | 模板文件 |
|------|-------|---------|
| 数据质量门闸 | 1.5 | `data_quality_gate_report.md`（本文件） |
| SAP 质量门闸 | 2.5 | `sap_quality_gate_report.md` |
| 结果质量门闸 | 3.5 | `results_quality_gate_report.md` |

### 9.4 依据标准

- ALCOA+ 原则：FDA Guidance on Data Integrity (2018)
- CDISC SDTM：Study Data Tabulation Model v2.0
- ICH E6(R3) GCP：Good Clinical Practice
- FDA 21 CFR Part 11：Electronic Records / Electronic Signatures
- HIPAA Privacy Rule：45 CFR §164.514（18 类 PHI 标识符）
