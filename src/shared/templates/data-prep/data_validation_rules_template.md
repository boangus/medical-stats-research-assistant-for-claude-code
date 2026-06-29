# 数据验证规则定义模板 (Data Validation Rules Template)

> MSRA 项目专用。供 `data-prep` Phase 1（7项深度验证）输出、Phase 7 质量门闸消费。
> 定义结构化数据验证规则体系，确保验证过程可复现、可审计、可追溯。
>
> 设计依据：
> - CDISC SDTM（Study Data Tabulation Model）—— 监管提交数据标准
> - GCDMP（Good Clinical Data Management Practices）—— 临床数据管理规范
> - ALCOA+ 原则（Attributable / Legible / Contemporaneous / Original / Accurate + Complete / Consistent / Enduring / Available）
> - FDA 21 CFR Part 11 —— 电子记录与电子签名
>
> ⚠️ **重要声明**：验证规则必须在数据清洗前（Phase 1）定义完成，
> 不得根据清洗结果反向调整规则。任何事后修改必须记录为 deviation。

---

```yaml
# YAML Frontmatter
study_id: MSRA-{YYYY}-{NNN}
version: v1.0
created_date: 2026-06-19
status: draft | approved | superseded
template_type: data_validation_rules
```

---

## 1. 元数据 (Metadata)

| 字段 | 值 | 说明 |
|------|-----|------|
| study_id (研究ID) | [{MSRA-YYYY-NNN}] | 唯一研究标识 |
| dataset_version (数据集版本) | [{v1.0}] | 对应锁定数据库版本 |
| validation_phase (验证阶段) | [{Phase 1}] | data-prep 工作流阶段 |
| operator (操作人) | [{姓名/数据管理员}] | 实际执行验证人员 |
| timestamp (时间戳) | [{YYYY-MM-DDTHH:MM:SS}] | 验证执行时间（ISO 8601） |
| sap_version (SAP版本) | [{v1.0}] | 对应统计分析计划版本 |
| source_data_hash (源数据哈希) | [{SHA256}] | 原始数据快照哈希值 |
| rules_version (规则版本) | [{v1.0}] | 验证规则集版本号 |
| environment (运行环境) | [{R 4.3.0 / Python 3.11}] | 软件环境记录 |
| standard_ref (参考标准) | [{CDISC SDTM IG 3.2 / GCDMP v5}] | 验证依据标准 |

---

## 2. 验证规则分类体系 (Validation Rule Classification)

> 所有验证规则按以下 8 类分类。每条规则必须归入唯一类别，不得跨类。
> 严重级别定义见 §2.9。

### 2.1 范围检查 (Range Check)

> 验证数值变量是否在预定义的合理范围内。范围依据来自方案、实验室正常值、临床常识。

| 规则ID | 规则描述 | 验证变量 | 最小值 | 最大值 | 合理范围依据 | 严重级别 | 处理方式 |
|--------|---------|---------|--------|--------|------------|---------|---------|
| RC-001 | 年龄必须在成人范围内 | age | 18 | 89 | 方案入组标准 §3.1 | P1 | 标记质疑，核对源文件 |
| RC-002 | 收缩压生理范围 | sbp | 70 | 250 | 临床生理学常识 | P1 | 标记质疑，核对源文件 |
| RC-003 | 舒张压生理范围 | dbp | 40 | 150 | 临床生理学常识 | P1 | 标记质疑，核对源文件 |
| RC-004 | BMI 合理范围 | bmi | 10 | 60 | WHO 分级标准 | P1 | 标记质疑，核对源文件 |
| RC-005 | 心率生理范围 | hr | 30 | 220 | 临床生理学常识 | P1 | 标记质疑，核对源文件 |
| RC-006 | 体温生理范围（℃） | temp | 34 | 42 | 临床生理学常识 | P1 | 标记质疑，核对源文件 |
| RC-007 | 血红蛋白范围（g/L） | hb | 30 | 250 | 实验室正常值范围 | P1 | 标记质疑，核对源文件 |
| RC-008 | [{变量}] | [{值}] | [{值}] | [{值}] | [{依据}] | [{P0-P3}] | [{处理方式}] |

### 2.2 类型检查 (Type Check)

> 验证数据类型是否符合变量字典定义。类型不匹配通常为录入错误或导入错误。

| 规则ID | 规则描述 | 验证变量 | 期望类型 | 验证逻辑 | 严重级别 | 处理方式 |
|--------|---------|---------|---------|---------|---------|---------|
| TC-001 | 年龄必须为整数 | age | integer | `is.integer(age) & age >= 0` | P0 | 阻断，要求修正 |
| TC-002 | 性别必须为分类值 | sex | categorical | `sex %in% c("M", "F")` | P0 | 阻断，要求修正 |
| TC-003 | 日期必须为 Date 类型 | enrollment_date | Date | `inherits(enrollment_date, "Date")` | P0 | 阻断，要求修正 |
| TC-004 | 实验室值必须为数值 | lab_wbc | numeric | `is.numeric(lab_wbc)` | P0 | 阻断，要求修正 |
| TC-005 | 受试者ID必须为字符 | subject_id | character | `is.character(subject_id)` | P0 | 阻断，要求修正 |
| TC-006 | [{变量}] | [{变量}] | [{类型}] | [{逻辑}] | [{P0-P3}] | [{处理方式}] |

### 2.3 格式检查 (Format Check)

> 验证数据格式是否符合标准。包括日期格式、编码格式、单位格式等。

| 规则ID | 规则描述 | 验证变量 | 期望格式 | 验证逻辑（正则/规则） | 严重级别 | 处理方式 |
|--------|---------|---------|---------|---------------------|---------|---------|
| FC-001 | 日期格式统一为 ISO 8601 | all_date_vars | YYYY-MM-DD | `^\d{4}-\d{2}-\d{2}$` | P1 | 格式修正，记录日志 |
| FC-002 | 受试者ID格式 | subject_id | SUBJ-NNN | `^SUBJ-\d{3}$` | P1 | 标记质疑 |
| FC-003 | 性别编码为 CDISC 标准值 | sex | M / F | `sex %in% c("M", "F")` | P1 | 值规范化 |
| FC-004 | AE 严重程度编码 | ae_severity | MILD/MODERATE/SEVERE | `ae_severity %in% c("MILD","MODERATE","SEVERE")` | P1 | 值规范化 |
| FC-005 | 实验室单位统一 | lab_unit | 标准单位词表 | `lab_unit %in% unit_dictionary` | P1 | 单位转换 |
| FC-006 | 时间戳格式 | timestamp | ISO 8601 datetime | `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}` | P1 | 格式修正 |
| FC-007 | [{变量}] | [{变量}] | [{格式}] | [{正则/规则}] | [{P0-P3}] | [{处理方式}] |

### 2.4 一致性检查 (Consistency Check)

> 验证跨变量逻辑关系。不一致通常为录入错误或逻辑错误。

| 规则ID | 规则描述 | 涉及变量 | 验证逻辑 | 严重级别 | 处理方式 |
|--------|---------|---------|---------|---------|---------|
| CC-001 | BMI = weight / height² | bmi, weight, height | `abs(bmi - weight/height^2) < 0.1` | P1 | 标记质疑，核对源文件 |
| CC-002 | 舒张压 < 收缩压 | sbp, dbp | `dbp < sbp` | P0 | 阻断，要求修正 |
| CC-003 | 出院日期 ≥ 入院日期 | admission_date, discharge_date | `discharge_date >= admission_date` | P0 | 阻断，要求修正 |
| CC-004 | 死亡日期 ≤ 末次随访 | death_date, last_followup | `death_date <= last_followup` | P0 | 阻断，要求修正 |
| CC-005 | 随机化日期 ≥ 知情同意日期 | randomization_date, icf_date | `randomization_date >= icf_date` | P0 | 阻断，要求修正 |
| CC-006 | 男性无妊娠记录 | sex, pregnant | `!(sex == "M" & pregnant == TRUE)` | P0 | 阻断，要求修正 |
| CC-007 | AE 发生日期 ≥ 入组日期 | ae_start_date, enrollment_date | `ae_start_date >= enrollment_date` | P1 | 标记质疑 |
| CC-008 | 年龄 ≥ 入组标准下限 | age, eligibility_min_age | `age >= eligibility_min_age` | P0 | 阻断，要求修正 |
| CC-009 | 总评分 = 各分项之和 | total_score, item_scores | `total_score == sum(item_scores)` | P1 | 标记质疑 |
| CC-010 | [{规则描述}] | [{变量}] | [{逻辑}] | [{P0-P3}] | [{处理方式}] |

### 2.5 完整性检查 (Completeness Check)

> 验证必填字段是否完整，识别缺失模式。

| 规则ID | 规则描述 | 验证变量 | 必填性 | 验证逻辑 | 严重级别 | 处理方式 |
|--------|---------|---------|--------|---------|---------|---------|
| CP-001 | 受试者ID不可缺失 | subject_id | 必填 | `!is.na(subject_id)` | P0 | 阻断，要求补录 |
| CP-002 | 入组日期不可缺失 | enrollment_date | 必填 | `!is.na(enrollment_date)` | P0 | 阻断，要求补录 |
| CP-003 | 主要终点不可缺失 | primary_endpoint | 必填 | `!is.na(primary_endpoint)` | P0 | 阻断，要求补录 |
| CP-004 | 分组变量不可缺失 | treatment_arm | 必填 | `!is.na(treatment_arm)` | P0 | 阻断，要求补录 |
| CP-005 | 关键协变量缺失率 | key_covariates | 建议 | `missing_rate < 5%` | P2 | 标记，进入缺失处理流程 |
| CP-006 | 缺失模式识别 | all_vars | — | Little's MCAR 检验 | P2 | 记录机制判断 |
| CP-007 | [{变量}] | [{变量}] | [{必填/建议}] | [{逻辑}] | [{P0-P3}] | [{处理方式}] |

### 2.6 唯一性检查 (Uniqueness Check)

> 验证主键唯一性和重复记录检测。

| 规则ID | 规则描述 | 验证变量 | 验证逻辑 | 严重级别 | 处理方式 |
|--------|---------|---------|---------|---------|---------|
| UC-001 | 受试者ID唯一 | subject_id | `length(unique(subject_id)) == length(subject_id)` | P0 | 阻断，去重（需用户确认） |
| UC-002 | 重复记录检测 | all_vars | `duplicated(data)` | P0 | 阻断，标记重复（需用户确认） |
| UC-003 | 同一受试者同一访期不重复 | subject_id, visit | `!duplicated(data[, c("subject_id","visit")])` | P0 | 阻断，标记重复 |
| UC-004 | AE 记录不重复 | subject_id, ae_term, ae_start | `!duplicated(data[, c("subject_id","ae_term","ae_start")])` | P1 | 标记质疑 |
| UC-005 | [{规则描述}] | [{变量}] | [{逻辑}] | [{P0-P3}] | [{处理方式}] |

### 2.7 交叉验证 (Cross-Validation)

> 与外部标准或参考数据比对，验证数据准确性。

| 规则ID | 规则描述 | 验证变量 | 外部参考源 | 验证逻辑 | 严重级别 | 处理方式 |
|--------|---------|---------|-----------|---------|---------|---------|
| CV-001 | 实验室正常值范围比对 | lab_values | 实验室正常值表 | `lab_value within reference_range` | P1 | 标记异常值 |
| CV-002 | 诊断编码比对 | diagnosis_code | ICD-10 编码库 | `diagnosis_code %in% icd10_dict` | P1 | 标记无效编码 |
| CV-003 | 药物编码比对 | drug_code | WHO Drug Dictionary | `drug_code %in% who_drug_dict` | P1 | 标记无效编码 |
| CV-004 | AE 编码比对 | ae_term | MedDRA 术语集 | `ae_term mapped to MedDRA PT` | P1 | 编码标准化 |
| CV-005 | 中心编号比对 | center_id | 中心注册表 | `center_id %in% center_registry` | P1 | 标记无效中心 |
| CV-006 | [{规则描述}] | [{变量}] | [{参考源}] | [{逻辑}] | [{P0-P3}] | [{处理方式}] |

### 2.8 业务规则检查 (Business Rule)

> 医学逻辑验证，确保数据符合临床/研究方案逻辑。

| 规则ID | 规则描述 | 涉及变量 | 验证逻辑 | 严重级别 | 处理方式 |
|--------|---------|---------|---------|---------|---------|
| BR-001 | 知情同意时年龄 ≥ 18 | icf_date, birth_date | `as.numeric(icf_date - birth_date) / 365.25 >= 18` | P0 | 阻断，要求修正 |
| BR-002 | 基线测量在随机化前 | baseline_date, randomization_date | `baseline_date <= randomization_date` | P0 | 阻断，要求修正 |
| BR-003 | 排除标准与入组状态一致 | exclusion_criteria, enrolled | `!(exclusion_criteria == TRUE & enrolled == TRUE)` | P0 | 阻断，要求修正 |
| BR-004 | SAE 必须有详细记录 | sae_flag, sae_narrative | `if(sae_flag) !is.na(sae_narrative)` | P0 | 阻断，要求补录 |
| BR-005 | 合并用药与 AE 时间关系 | conmed_start, ae_start | 记录时间关系供医学审核 | P2 | 标记供医学审核 |
| BR-006 | 妊娠期排除标准 | pregnant, enrollment | `!(pregnant == TRUE & enrolled == TRUE)` | P0 | 阻断，要求修正 |
| BR-007 | [{规则描述}] | [{变量}] | [{逻辑}] | [{P0-P3}] | [{处理方式}] |

### 2.9 严重级别定义 (Severity Level Definition)

| 级别 | 名称 | 定义 | 处理方式 | 门闸影响 |
|------|------|------|---------|---------|
| **P0** | 阻断级 (Critical) | 数据错误导致无法分析或违反方案 | 立即阻断，必须修正后方可继续 | 🔑 阻断式检查，未通过强制退回 |
| **P1** | 严重级 (Major) | 数据错误可能影响分析结论 | 标记质疑，限期修正 | 需在锁定前解决 |
| **P2** | 警告级 (Minor) | 数据质量问题需关注但不阻断 | 记录并跟踪，可后续处理 | 记录但不阻断 |
| **P3** | 提示级 (Info) | 潜在问题提示，供参考 | 记录备查 | 不影响门闸 |

---

## 3. 规则注册表 (Rule Registry — YAML)

> 所有验证规则注册为 YAML 格式，供验证脚本自动加载和执行。
> 规则ID全局唯一，命名规则：`{类别缩写}-{序号}`。

```yaml
# validation_rules_registry.yaml
# 验证规则注册表 — 自动加载执行
registry_version: v1.0
study_id: "[{MSRA-YYYY-NNN}]"
last_updated: "[{YYYY-MM-DDTHH:MM:SS}]"

rules:
  # ===== 范围检查 (Range Check) =====
  - id: RC-001
    category: range_check
    description: "年龄必须在成人范围内"
    variables: [age]
    severity: P1
    logic:
      type: range
      min: 18
      max: 89
    basis: "方案入组标准 §3.1"
    action: flag_query

  - id: RC-002
    category: range_check
    description: "收缩压生理范围"
    variables: [sbp]
    severity: P1
    logic:
      type: range
      min: 70
      max: 250
    basis: "临床生理学常识"
    action: flag_query

  # ===== 类型检查 (Type Check) =====
  - id: TC-001
    category: type_check
    description: "年龄必须为整数"
    variables: [age]
    severity: P0
    logic:
      type: type_assertion
      expected: integer
    action: block

  # ===== 格式检查 (Format Check) =====
  - id: FC-001
    category: format_check
    description: "日期格式统一为 ISO 8601"
    variables: [enrollment_date, icf_date, randomization_date]
    severity: P1
    logic:
      type: regex
      pattern: "^\\d{4}-\\d{2}-\\d{2}$"
    action: format_fix

  # ===== 一致性检查 (Consistency Check) =====
  - id: CC-001
    category: consistency_check
    description: "BMI = weight / height²"
    variables: [bmi, weight, height]
    severity: P1
    logic:
      type: formula
      formula: "abs(bmi - weight/height^2) < 0.1"
    action: flag_query

  - id: CC-002
    category: consistency_check
    description: "舒张压 < 收缩压"
    variables: [sbp, dbp]
    severity: P0
    logic:
      type: comparison
      rule: "dbp < sbp"
    action: block

  # ===== 完整性检查 (Completeness Check) =====
  - id: CP-001
    category: completeness_check
    description: "受试者ID不可缺失"
    variables: [subject_id]
    severity: P0
    logic:
      type: not_null
    action: block

  # ===== 唯一性检查 (Uniqueness Check) =====
  - id: UC-001
    category: uniqueness_check
    description: "受试者ID唯一"
    variables: [subject_id]
    severity: P0
    logic:
      type: unique
    action: block

  # ===== 交叉验证 (Cross-Validation) =====
  - id: CV-001
    category: cross_validation
    description: "实验室正常值范围比对"
    variables: [lab_values]
    severity: P1
    logic:
      type: external_reference
      reference: "lab_reference_ranges.csv"
    action: flag_query

  # ===== 业务规则检查 (Business Rule) =====
  - id: BR-001
    category: business_rule
    description: "知情同意时年龄 ≥ 18"
    variables: [icf_date, birth_date]
    severity: P0
    logic:
      type: formula
      formula: "as.numeric(icf_date - birth_date) / 365.25 >= 18"
    action: block

# ===== 规则统计 =====
rule_count:
  total: "[{N}]"
  range_check: "[{N}]"
  type_check: "[{N}]"
  format_check: "[{N}]"
  consistency_check: "[{N}]"
  completeness_check: "[{N}]"
  uniqueness_check: "[{N}]"
  cross_validation: "[{N}]"
  business_rule: "[{N}]"
  by_severity:
    P0: "[{N}]"
    P1: "[{N}]"
    P2: "[{N}]"
    P3: "[{N}]"
```

---

## 4. 验证结果汇总报告 (Validation Summary Report)

> 验证执行完成后，生成本汇总报告。P0 级问题未全部解决前，不得进入清洗阶段。

### 4.1 验证执行概要

| 字段 | 值 | 说明 |
|------|-----|------|
| 验证执行时间 (Executed At) | [{YYYY-MM-DDTHH:MM:SS}] | 验证脚本执行时间戳 |
| 验证脚本版本 (Script Version) | [{v1.0}] | 验证脚本版本号 |
| 数据集维度 (Dataset Shape) | [{N}] 行 × [{N}] 列 | 验证时数据集维度 |
| 规则总数 (Total Rules) | [{N}] | 已注册规则总数 |
| 执行规则数 (Rules Executed) | [{N}] | 实际执行规则数 |
| 规则覆盖率 (Rule Coverage) | [{%}] | 执行/总数 × 100% |
| 发现问题总数 (Total Issues) | [{N}] | 所有级别问题总数 |
| P0 问题数 (P0 Issues) | [{N}] | 阻断级问题数 |
| P1 问题数 (P1 Issues) | [{N}] | 严重级问题数 |

### 4.2 按规则类别汇总

| 规则类别 | 规则数 | 执行数 | 通过数 | 失败数 | P0 问题 | P1 问题 | P2 问题 | P3 问题 |
|---------|--------|--------|--------|--------|---------|---------|---------|---------|
| 范围检查 (Range Check) | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] |
| 类型检查 (Type Check) | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] |
| 格式检查 (Format Check) | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] |
| 一致性检查 (Consistency) | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] |
| 完整性检查 (Completeness) | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] |
| 唯一性检查 (Uniqueness) | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] |
| 交叉验证 (Cross-Validation) | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] |
| 业务规则 (Business Rule) | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] | [{N}] |
| **合计** | **[{N}]** | **[{N}]** | **[{N}]** | **[{N}]** | **[{N}]** | **[{N}]** | **[{N}]** | **[{N}]** |

### 4.3 问题详情清单

| # | 规则ID | 规则类别 | 规则描述 | 严重级别 | 影响记录数 | 影响记录示例 | 状态 |
|---|--------|---------|---------|---------|-----------|------------|------|
| 1 | [{RC-001}] | 范围检查 | [{年龄范围}] | [{P1}] | [{N}] | [{SUBJ-005: age=250}] | ✅已解决 / ❌未解决 |
| 2 | [{CC-002}] | 一致性检查 | [{舒张压<收缩压}] | [{P0}] | [{N}] | [{SUBJ-012: sbp=110, dbp=130}] | ✅已解决 / ❌未解决 |
| 3 | [{UC-001}] | 唯一性检查 | [{ID唯一}] | [{P0}] | [{N}] | [{SUBJ-099 重复}] | ✅已解决 / ❌未解决 |
| [{N}] | [{规则ID}] | [{类别}] | [{描述}] | [{级别}] | [{N}] | [{示例}] | [{状态}] |

### 4.4 验证结论

| 评估维度 | 结果 | 说明 |
|---------|------|------|
| P0 问题全部解决 | ✅是 / ❌否 | [{N}] 个 P0 问题待解决 |
| P1 问题处理计划 | ✅已有 / ❌缺失 | [{说明}] |
| 规则覆盖率 | ✅100% / ⚠️[{%}] | [{说明}] |
| **验证结论** | **✅通过 / ❌阻断** | [{综合说明}] |

---

## 5. 与 Stage 1.5 数据质量门控的映射关系 (Quality Gate Mapping)

> 本验证规则定义的执行结果为 Pipeline Stage 1.5 数据质量门闸的核心输入。
> 门闸检查清单详见 `skills/data-prep/SKILL.md` Phase 7 及 `src/shared/templates/quality-gates/data_quality_gate_report.md`。

| 门闸检查项 | 本规则对应类别 | 通过标准 | 门闸级别 | 当前状态 |
|-----------|--------------|---------|---------|---------|
| □1 清洗日志完整性 | —（验证先于清洗） | 验证问题已记录后方可清洗 | 非阻断 | ✅通过 / ❌阻断 |
| □2 变量定义明确性 | 类型检查 (TC) | 所有变量类型验证通过 | 非阻断 | ✅通过 / ❌阻断 |
| □3 缺失机制评估 | 完整性检查 (CP) | 缺失模式识别完成，机制已判定 | 非阻断 | ✅通过 / ❌阻断 |
| □5 数据库锁定确认 | —（锁定前验证完成） | 所有 P0 问题已解决 | 🔑阻断 | ✅通过 / ❌阻断 |
| □6 逻辑一致性 | 一致性检查 (CC) + 业务规则 (BR) | 所有 P0 级逻辑规则通过 | 🔑阻断 | ✅通过 / ❌阻断 |
| □7 值规范化完成 | 格式检查 (FC) | 所有格式规则已执行并修正 | 🔑阻断 | ✅通过 / ❌阻断 |
| □8 可重复性 | 全部规则 | 规则可脚本化复现 | 非阻断 | ✅通过 / ❌阻断 |
| □9 隐私合规 (PHI) | 交叉验证 (CV) | PHI 检测规则通过 | 🔑阻断 | ✅通过 / ❌阻断 |

**门闸判定逻辑**：
- P0 级规则（阻断级）未全部通过时，Stage 1.5 门闸直接阻断，不得进入 Stage 2 分析计划
- 第 6 项（逻辑一致性）为**阻断式检查**——一致性检查 (CC) 和业务规则 (BR) 中 P0 级规则必须全部通过
- 第 7 项（值规范化完成）要求格式检查 (FC) 中所有规则已执行并修正
- 第 9 项（隐私合规）要求 PHI 检测规则（交叉验证类别）通过，未通过强制阻断

---

## 6. 参考标准映射 (Reference Standards Mapping)

| 标准 | 适用规则类别 | 映射说明 |
|------|------------|---------|
| **CDISC SDTM** | 格式检查、类型检查 | SDTM 域结构、变量命名、控制术语 |
| **GCDMP** | 全部类别 | 临床数据管理全流程规范 |
| **ALCOA+** | 全部类别 | 数据完整性 9 原则（Attributable / Legible / Contemporaneous / Original / Accurate / Complete / Consistent / Enduring / Available） |
| **FDA 21 CFR Part 11** | 全部类别 | 电子记录审计追踪要求 |
| **ICH E6(R3) GCP** | 业务规则 | 临床试验质量管理规范 |
| **ICH E9(R1)** | 完整性检查 | 缺失数据机制评估要求 |

### 6.1 ALCOA+ 原则映射

| ALCOA+ 原则 | 对应验证规则 | 验证要求 |
|------------|------------|---------|
| Attributable（可归因） | UC-001 唯一性 | 每条记录可追溯至受试者 |
| Legible（可读） | FC-001~FC-006 格式检查 | 数据格式清晰可读 |
| Contemporaneous（同时性） | CC-003~CC-005 日期逻辑 | 时间序列逻辑一致 |
| Original（原始性） | CV-001~CV-005 交叉验证 | 与源数据可比对 |
| Accurate（准确性） | RC-001~RC-008 范围检查 | 数值在合理范围内 |
| Complete（完整性） | CP-001~CP-007 完整性检查 | 必填字段无缺失 |
| Consistent（一致性） | CC-001~CC-010 一致性检查 | 跨变量逻辑一致 |
| Enduring（持久性） | —（审计追踪） | 验证结果持久记录 |
| Available（可用性） | —（规则注册表） | 规则可随时加载执行 |

---

## 7. 变更记录 (Change Log)

| 版本 | 日期 | 修改内容 | 修改人 | 理由 |
|------|------|---------|--------|------|
| v1.0 | 2026-06-19 | 初始版本 | [{姓名}] | — |
| [{v}] | [{YYYY-MM-DD}] | [{描述}] | [{姓名}] | [{理由}] |

> 🔴 **重要**：验证规则定义一旦在 Phase 1 确定并经用户批准，不得根据清洗结果反向调整。
> 任何事后修改必须记录为 deviation。

---

## 模板使用说明 (Template Usage Instructions)

### 适用场景
- `data-prep` Phase 1（7项深度验证）规则定义与执行
- `data-prep` Phase 7（质量门闸）输入产物
- 任何需要结构化数据验证的场景

### 填写步骤
1. **复制模板**：将本模板复制为 `data_validation_rules_v{版本}.md`，填入 YAML frontmatter
2. **定义元数据**：填写 §1 所有字段，确保 study_id、dataset_version 与项目一致
3. **逐类定义规则**：
   - 范围检查（§2.1）：为每个数值变量定义合理范围
   - 类型检查（§2.2）：为每个变量定义期望类型
   - 格式检查（§2.3）：为日期、编码、单位等定义格式规则
   - 一致性检查（§2.4）：定义跨变量逻辑规则
   - 完整性检查（§2.5）：定义必填字段和缺失检测
   - 唯一性检查（§2.6）：定义主键和重复检测
   - 交叉验证（§2.7）：定义外部标准比对规则
   - 业务规则（§2.8）：定义医学逻辑验证规则
4. **注册规则**：将所有规则写入 §3 YAML 注册表，供脚本自动加载
5. **执行验证**：运行验证脚本，生成 §4 验证结果汇总报告
6. **门闸自检**：对照 §5 检查门闸第 2、5、6、7、9 项是否满足
7. **标准映射**：确认 §6 参考标准映射完整

### 注意事项
- 🔴 **禁止事后修改规则**：验证规则必须在清洗前定义，不得根据结果反向调整
- 🔴 **P0 问题必须解决**：阻断级问题未解决前，不得进入清洗阶段
- 🔴 **规则ID全局唯一**：命名规则 `{类别缩写}-{序号}`，不得重复
- 🟡 **范围依据可追溯**：范围检查的最小/最大值必须有方案、标准或文献依据
- 🟡 **规则可脚本化**：所有规则必须可表达为可执行逻辑（公式、正则、比较等）
- 🟢 **规则覆盖率**：建议规则覆盖所有关键变量，覆盖率 ≥ 90%

### 与其他文档的关系
- **上游**：`src/shared/sap/sap_standard.md` — SAP 定义变量角色，驱动验证规则
- **下游**：`src/shared/templates/data-prep/cleaning_log_template.md` — 验证发现的问题驱动清洗
- **下游**：`src/shared/templates/quality-gates/data_quality_gate_report.md` — Stage 1.5 门闸消费验证结果
- **关联**：`src/shared/templates/data-prep/eda_report_template.md` — EDA 报告补充验证发现
- **关联**：`src/shared/templates/variable_spec_template.md` — 变量字典定义类型和格式依据
- **关联**：`skills/data-prep/SKILL.md` Phase 1 — 7项深度验证执行流程

### 反例（不要做什么）

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 1 | 根据清洗结果反向修改验证规则 | 偏向结果，破坏验证独立性 | Phase 1 定义后不得修改，修改记为 deviation |
| 2 | P0 问题未解决即进入清洗 | 阻断级问题影响数据完整性 | P0 全部解决后方可进入 Phase 2 |
| 3 | 规则无依据来源 | 审稿人无法判断规则合理性 | 每条规则必须有方案/标准/文献依据 |
| 4 | 规则不可脚本化 | 无法自动执行和复现 | 所有规则必须可表达为可执行逻辑 |
| 5 | 规则ID重复或命名不规范 | 注册表加载冲突 | 严格按 `{类别缩写}-{序号}` 命名 |
