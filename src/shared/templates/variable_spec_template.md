# 变量构造规格书模板 (Variable Construction Spec)

> MSRA 项目专用。供 `analysis-plan` Phase 6 输出、`analysis-exec` Phase 1 消费。
> 定义所有分析衍生变量的构造逻辑，作为 SAP 与执行之间的契约，确保构造可复现、可审计。
>
> 设计依据：ICH E9(R1) Estimands 框架要求衍生变量在 SAP 中预定义；
> FDA 21 CFR Part 11 要求变量构造可追溯（公式、依据、版本）。

---

## 使用方式

1. `analysis-plan` Phase 6 审查 SAP 通过后，复制本模板填入实际变量定义
2. 将填充后的规格书作为 SAP 的附录或独立文件提交（文件名建议 `variable_spec_v{版本}.md`）
3. `analysis-exec` Phase 1 读取本规格书，**严格按定义构造，不得自行修改切点或公式**
4. 任何偏差必须记录为 deviation 并征得用户同意

---

## 1. 元数据

```yaml
study_id: MSRA-{YYYY}-{NNN}
sap_version: v1.0
spec_version: v1.0
created: YYYY-MM-DD
author: [统计分析师生成 / 用户审核]
status: draft | approved | superseded
```

---

## 2. 变量构造定义表（核心）

> 每个衍生变量一行。**禁止留空**——无依据的切点必须标注"探索性"。

| 变量名 | 角色 | 类型 | 构造公式 | 单位/编码 | 切点/参考依据 | 缺失处理 | 验证规则 |
|--------|------|------|---------|----------|--------------|---------|---------|
| age | 协变量 | 连续 | 入组日期 - 出生日期（年） | 岁 | 标准人口学 | 关键变量，缺失删除 | 范围 [18, 100] |
| age_group | 亚组 | 分类（3级） | age < 60 / 60-70 / ≥70 | <60 / 60-70 / ≥70 | 临床惯例 | 归入 missing 组 | 与 age 一致性校验 |
| bmi | 协变量 | 连续 | 体重(kg) / (身高(m))² | kg/m² | WHO 标准 | 标记缺失，不插补 | 范围 [12, 60] |
| bmi_group | 亚组 | 分类（4级） | bmi < 18.5 / 18.5-24 / 24-28 / ≥28 | underweight / normal / overweight / obese | WHO 中国标准（WS/T 428） | 归入 missing 组 | 与 bmi 一致性校验 |
| treatment_response | 终点 | 二分类 | RECIST v1.1: CR+PR vs SD+PD | responder / non-responder | RECIST v1.1（实体瘤） | 无评估归为 non-responder | 仅肿瘤研究适用 |
| charlson | 协变量 | 连续 | Charlson 合并症指数求和 | 分（0-33） | Charlson 1987 | 缺失记为 0（标注假设） | 整数 |

---

## 3. 字段说明

### 3.1 角色

| 角色 | 说明 | 示例 |
|------|------|------|
| 暴露/治疗 | 研究核心变量 | treatment |
| 终点 | 主要/次要结局 | os_time, treatment_response |
| 协变量 | 调整变量 | age, sex, bmi, 基线 HbA1c |
| 亚组 | 分层/异质性分析 | age_group, sex |
| 权重 | 加权分析用 | iptw_weight |

### 3.2 类型

- **连续 (continuous)** — 数值型，报告 mean(SD) 或 median(IQR)
- **分类 (categorical)** — 离散，报告 n(%)
- **二分类 (binary)** — 0/1 编码
- **有序 (ordinal)** — 有等级的分类（如 I-II-III-IV 期）
- **生存 (survival)** — time + event 双变量
- **计数 (count)** — 非负整数（如住院次数）

### 3.3 切点依据等级（必须标注）

| 等级 | 含义 | 示例 |
|------|------|------|
| 🟢 **标准** | 国际/国家指南明确 | WHO BMI 分组、RECIST v1.1 |
| 🟡 **惯例** | 学界常用但无强制标准 | 年龄 <60/60-70/≥70 |
| 🟠 **数据驱动** | 基于本研究数据（如中位数、X-tile） | 必须标注"探索性"，不能用于主分析 |
| 🔴 **自定义** | 无文献依据 | 必须在局限性中讨论 |

### 3.4 缺失处理策略

| 策略 | 适用场景 | 备注 |
|------|---------|------|
| 删除 | 关键变量（暴露/终点） | 减少样本量，记录影响 |
| 归入 missing 组 | 分层分析 | 保留样本量 |
| 标记缺失，不插补 | 一般协变量 | 由模型自行处理 |
| 多重插补 (MICE) | MAR 缺失 | 必须在 SAP 中预定义 |
| 单一插补 | 仅当缺失率 <5% | 标注假设 |

---

## 4. 构造顺序（依赖关系）

> 后构造的变量可能依赖前面的。按编号顺序执行，避免引用未定义变量。

```
Step 0: 原始变量验证（类型、范围、缺失）
   │
   ▼
Step 1: 基础衍生（无依赖）
   ├── age（基于 BRTHDTC + RFICDTC）
   ├── bmi（基于 WEIGHT + HEIGHT）
   └── charlson（基于合并症求和）
   │
   ▼
Step 2: 分组衍生（依赖 Step 1）
   ├── age_group（依赖 age）
   └── bmi_group（依赖 bmi）
   │
   ▼
Step 3: 终点衍生（依赖原始变量 + 时间）
   ├── treatment_response（依赖 RECIST 评估）
   ├── os_time / os_event（依赖死亡日期/末次随访）
   └── pfs_time / pfs_event（依赖进展日期）
   │
   ▼
Step 4: 权重衍生（仅观察性研究）
   ├── ps_score（倾向性评分）
   └── iptw_weight（逆概率权重）
   │
   ▼
Step 5: 分析数据集合并（所有变量 → analysis_dataset.rda）
```

---

## 5. 验证规则（构造后必须检查）

> 每个变量构造完成后，运行以下验证。任何违反必须修正或记录为 deviation。

```r
# 1. 范围验证（连续变量）
stopifnot(all(data$age >= 18 & data$age <= 100, na.rm = TRUE))
stopifnot(all(data$bmi >= 12 & data$bmi <= 60, na.rm = TRUE))

# 2. 一致性验证（衍生 vs 原始）
stopifnot(all(data$age_group == cut(data$age, c(0,60,70,Inf),
                                     labels=c("<60","60-70","≥70")), na.rm = TRUE))

# 3. 缺失率报告
missing_report <- sapply(data, function(x) mean(is.na(x)))
print(missing_report[missing_report > 0])

# 4. 异常值传播检查（如 bmi = weight/height²，weight 或 height 缺失时 bmi 应为 NA）
stopifnot(all(is.na(data$bmi[is.na(data$weight) | is.na(data$height)])))
```

---

## 6. 变更日志

| 版本 | 日期 | 修改内容 | 修改人 | 理由 |
|------|------|---------|--------|------|
| v1.0 | YYYY-MM-DD | 初始版本 | — | — |
| | | | | |

---

## 7. 与其他文档的关系

- **上游**：`src/shared/sap/sap_standard.md` — SAP §7 引用本规格书
- **下游**：`skills/analysis-exec/SKILL.md` Phase 1 — 严格按本规格书构造
- **关联**：`src/shared/sap/variable_selection_guide.md` — "选哪些变量"（本规格书定义"怎么构造"）
- **审计**：构造日志 + 哈希写入 `audit_log.jsonl`（见 analysis-exec Phase 10）

---

## 8. 反例（不要做什么）

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 1 | 切点无依据直接写死 | 不可复现，审稿人无法判断 | 必须标注切点等级（标准/惯例/数据驱动/自定义） |
| 2 | 构造公式引用不存在的原始变量 | 执行时报错，无法复现 | 构造前先验证原始变量存在 |
| 3 | 数据驱动切点用于主分析 | 哲学问题——切点由数据拟合，主分析"显著"是过拟合 | 数据驱动切点只能用于探索性亚组分析 |
| 4 | 缺失值传播未处理（如分母为 0） | 产生 NaN/Inf，污染模型 | 构造公式中嵌入缺失处理规则 |
| 5 | 构造顺序混乱（先构造分组，后构造连续） | 引用未定义变量，报错 | 严格按 §4 构造顺序执行 |
| 6 | 构造后不验证一致性 | 衍生变量与原始变量不符，结果错误 | 构造后必须运行 §5 验证规则 |
