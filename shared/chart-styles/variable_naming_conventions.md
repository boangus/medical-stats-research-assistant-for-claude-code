# 变量命名规范

> MSRA 项目专用。定义统计分析全流程中变量命名的统一规范，确保 SAP、代码、表格、图表、
> 报告中的变量名称完全一致。
> 适用范围：data-prep 变量定义、analysis-plan SAP 变量构造、analysis-exec 代码变量、
> report 表格/图表/正文变量。

---

## 设计初衷

变量命名不统一是医学统计报告中最常见的问题之一：
- SAP 中写"收缩压"，代码中用 `sbp`，表格中写"Systolic BP"，图表中写"SBP"
- 同一变量在不同位置出现不同名称，读者无法对应
- 单位标注缺失或不一致（mmHg vs mmHg vs mm Hg）
- 缩写未定义或定义不一致

本文件定义**三列命名体系**：代码变量名 | 规范显示名 | 英文显示名，确保全流程一致。

---

## 一、三列命名体系

### 1.1 命名层级

| 层级 | 用途 | 命名规则 | 示例 |
|------|------|---------|------|
| 代码变量名 | 代码中使用的变量名 | 小写+下划线，简洁 | `systolic_bp` |
| 规范显示名 | 表格/图表/报告中展示 | 中文规范名+单位 | `收缩压 (mmHg)` |
| 英文显示名 | 英文报告/国际期刊 | 英文规范名+单位 | `Systolic BP (mmHg)` |

### 1.2 命名规则

**代码变量名**：
- 全小写，下划线分隔
- 不超过 20 字符
- 不含特殊字符
- 有意义，不使用 `var1`、`x`、`temp` 等无意义名称

**规范显示名**：
- 中文优先，使用医学规范术语
- 必须包含单位（如有）
- 单位用括号包裹：`变量名 (单位)`
- 复合单位用 `/` 或 `²` 等：`kg/m²`、`mL/min`

**英文显示名**：
- 首字母大写
- 缩写在首次出现时定义
- 单位标注与中文版一致

---

## 二、常见变量命名映射表

### 2.1 人口学变量

| 代码变量名 | 规范显示名 | 英文显示名 | 说明 |
|-----------|-----------|-----------|------|
| `age` | 年龄 (岁) | Age (years) | — |
| `sex` | 性别 | Sex | 男/女 |
| `male` | 男性 | Male | 二分类 |
| `bmi` | BMI (kg/m²) | BMI (kg/m²) | 体重指数 |
| `height` | 身高 (cm) | Height (cm) | — |
| `weight` | 体重 (kg) | Weight (kg) | — |
| `ethnicity` | 民族 | Ethnicity | — |
| `education` | 受教育程度 | Education level | — |
| `occupation` | 职业 | Occupation | — |
| `marital_status` | 婚姻状况 | Marital status | — |

### 2.2 生命体征变量

| 代码变量名 | 规范显示名 | 英文显示名 | 说明 |
|-----------|-----------|-----------|------|
| `systolic_bp` | 收缩压 (mmHg) | Systolic BP (mmHg) | SBP |
| `diastolic_bp` | 舒张压 (mmHg) | Diastolic BP (mmHg) | DBP |
| `heart_rate` | 心率 (次/分) | Heart rate (bpm) | HR |
| `respiratory_rate` | 呼吸频率 (次/分) | Respiratory rate (breaths/min) | RR |
| `temperature` | 体温 (°C) | Temperature (°C) | — |
| `oxygen_saturation` | 血氧饱和度 (%) | SpO₂ (%) | — |

### 2.3 实验室检查变量

| 代码变量名 | 规范显示名 | 英文显示名 | 说明 |
|-----------|-----------|-----------|------|
| `wbc` | 白细胞计数 (×10⁹/L) | WBC (×10⁹/L) | — |
| `rbc` | 红细胞计数 (×10¹²/L) | RBC (×10¹²/L) | — |
| `hemoglobin` | 血红蛋白 (g/L) | Hemoglobin (g/L) | Hb |
| `platelet` | 血小板计数 (×10⁹/L) | Platelet (×10⁹/L) | PLT |
| `glucose_fasting` | 空腹血糖 (mmol/L) | Fasting glucose (mmol/L) | FBG |
| `hba1c` | 糖化血红蛋白 (%) | HbA1c (%) | — |
| `creatinine` | 血肌酐 (μmol/L) | Creatinine (μmol/L) | Cr |
| `alt` | 丙氨酸转氨酶 (U/L) | ALT (U/L) | — |
| `ast` | 天冬氨酸转氨酶 (U/L) | AST (U/L) | — |
| `total_cholesterol` | 总胆固醇 (mmol/L) | Total cholesterol (mmol/L) | TC |
| `ldl_cholesterol` | LDL-C (mmol/L) | LDL-C (mmol/L) | 低密度脂蛋白胆固醇 |
| `hdl_cholesterol` | HDL-C (mmol/L) | HDL-C (mmol/L) | 高密度脂蛋白胆固醇 |
| `triglycerides` | 甘油三酯 (mmol/L) | Triglycerides (mmol/L) | TG |

### 2.4 结局变量

| 代码变量名 | 规范显示名 | 英文显示名 | 说明 |
|-----------|-----------|-----------|------|
| `overall_survival` | 总生存时间 (月) | Overall survival (months) | OS |
| `progression_free_survival` | 无进展生存时间 (月) | Progression-free survival (months) | PFS |
| `event_free_survival` | 无事件生存时间 (月) | Event-free survival (months) | EFS |
| `time_to_event` | 至事件时间 (天) | Time to event (days) | — |
| `event_status` | 事件发生状态 | Event status | 0=删失, 1=事件 |
| `mortality` | 死亡 | Mortality | 二分类 |
| `remission` | 缓解 | Remission | 二分类 |
| `response_rate` | 客观缓解率 (%) | Objective response rate (%) | ORR |

### 2.5 治疗与分组变量

| 代码变量名 | 规范显示名 | 英文显示名 | 说明 |
|-----------|-----------|-----------|------|
| `treatment_group` | 治疗组 | Treatment group | — |
| `control_group` | 对照组 | Control group | — |
| `treatment_arm` | 治疗臂 | Treatment arm | — |
| `dose` | 剂量 (mg) | Dose (mg) | — |
| `duration_treatment` | 治疗持续时间 (周) | Treatment duration (weeks) | — |
| `compliance` | 依从性 (%) | Compliance (%) | — |

### 2.6 合并症变量

| 代码变量名 | 规范显示名 | 英文显示名 | 说明 |
|-----------|-----------|-----------|------|
| `hypertension` | 高血压 | Hypertension | 二分类 |
| `diabetes` | 糖尿病 | Diabetes | 二分类 |
| `coronary_heart_disease` | 冠心病 | Coronary heart disease | CHD |
| `stroke` | 脑卒中 | Stroke | — |
| `copd` | 慢性阻塞性肺疾病 | COPD | — |
| `ckd` | 慢性肾脏病 | Chronic kidney disease | CKD |
| `charlson_score` | Charlson合并症指数 | Charlson comorbidity index | CCI |

### 2.7 效应量变量

| 代码变量名 | 规范显示名 | 英文显示名 | 说明 |
|-----------|-----------|-----------|------|
| `odds_ratio` | OR | OR | 比值比 |
| `hazard_ratio` | HR | HR | 风险比 |
| `risk_ratio` | RR | RR | 风险比 |
| `mean_difference` | 均值差 | Mean difference | MD |
| `standardized_mean_diff` | 标准化均值差 | Standardized mean difference | SMD |
| `cohen_d` | Cohen's d | Cohen's d | 效应量 |
| `ci_lower` | 95% CI 下限 | 95% CI lower | — |
| `ci_upper` | 95% CI 上限 | 95% CI upper | — |
| `p_value` | P 值 | P value | 遵循 P-R01~R07 |

---

## 三、单位标注规范

### 3.1 单位格式规则

| 规则 | 正确 | 错误 |
|------|------|------|
| 单位用括号包裹 | 收缩压 (mmHg) | ~~收缩压 mmHg~~, ~~收缩压, mmHg~~ |
| 复合单位用 / | BMI (kg/m²) | ~~BMI (kg·m⁻²)~~ |
| 上标用 Unicode | ×10⁹/L | ~~x10^9/L~~ |
| 温度用 °C | 体温 (°C) | ~~体温 (摄氏度)~~ |
| 百分号紧贴数字 | 45% | ~~45 %~~ |
| 时间单位统一 | 月/周/天/小时 | 不混用 mo/mon/months |

### 3.2 常见单位速查

| 变量类型 | 单位 | 示例 |
|---------|------|------|
| 血压 | mmHg | 收缩压 (mmHg) |
| 血糖 | mmol/L | 空腹血糖 (mmol/L) |
| 血脂 | mmol/L | 总胆固醇 (mmol/L) |
| 血红蛋白 | g/L | 血红蛋白 (g/L) |
| 细胞计数 | ×10⁹/L 或 ×10¹²/L | 白细胞 (×10⁹/L) |
| 肝功能 | U/L | ALT (U/L) |
| 肾功能 | μmol/L | 血肌酐 (μmol/L) |
| BMI | kg/m² | BMI (kg/m²) |
| 时间 | 月/周/天 | 生存时间 (月) |
| 年龄 | 岁 | 年龄 (岁) |
| 剂量 | mg | 剂量 (mg) |
| 温度 | °C | 体温 (°C) |
| 比例 | % | 缓解率 (%) |

---

## 四、缩写管理规范

### 4.1 缩写使用规则

1. **首次出现定义**：缩写在正文/表格/图表中首次出现时必须给出全称
2. **定义一次原则**：同一缩写在同一文档中只定义一次
3. **图注/表注定义**：图表中的缩写在图注/表注中统一定义
4. **SAP 定义优先**：缩写定义以 SAP 中的定义为准

### 4.2 标准缩写表

| 缩写 | 全称（中文） | 全称（英文） |
|------|------------|------------|
| SBP | 收缩压 | Systolic blood pressure |
| DBP | 舒张压 | Diastolic blood pressure |
| BMI | 体重指数 | Body mass index |
| HR | 风险比 | Hazard ratio |
| OR | 比值比 | Odds ratio |
| RR | 风险比 | Risk ratio |
| CI | 置信区间 | Confidence interval |
| MD | 均值差 | Mean difference |
| SMD | 标准化均值差 | Standardized mean difference |
| IQR | 四分位距 | Interquartile range |
| SD | 标准差 | Standard deviation |
| SE | 标准误 | Standard error |
| ITT | 意向性治疗 | Intention-to-treat |
| PP | 符合方案 | Per-protocol |
| AE | 不良事件 | Adverse event |
| SAE | 严重不良事件 | Serious adverse event |
| OS | 总生存 | Overall survival |
| PFS | 无进展生存 | Progression-free survival |
| IPTW | 逆概率处理加权 | Inverse probability of treatment weighting |
| PS | 倾向性评分 | Propensity score |
| RCS | 限制性立方样条 | Restricted cubic spline |
| KM | Kaplan-Meier | Kaplan-Meier |
| ROC | 受试者工作特征 | Receiver operating characteristic |
| AUC | 曲线下面积 | Area under the curve |
| VIF | 方差膨胀因子 | Variance inflation factor |
| PH | 比例风险 | Proportional hazards |
| MCID | 最小临床重要差异 | Minimal clinically important difference |
| NNT | 需治疗人数 | Number needed to treat |

---

## 五、变量命名一致性检查

### 5.1 检查流程

```
SAP 变量定义 → 代码变量名 → Table 1 变量名 → 结果表变量名 → 图表标签 → 正文解读
     │              │              │               │              │            │
     └──────────────┴──────────────┴───────────────┴──────────────┴────────────┘
                              一致性检查
```

### 5.2 检查规则

| 规则编号 | 检查内容 | 违反后果 |
|---------|---------|---------|
| V-R01 | 代码变量名在所有脚本中一致 | 代码审查不通过 |
| V-R02 | 规范显示名在所有表格中一致 | 质检不通过 |
| V-R03 | 图表标签与表格变量名一致 | 质检不通过 |
| V-R04 | 正文解读中的变量名与表格一致 | 质检不通过 |
| V-R05 | 单位标注在所有位置一致 | 质检警告 |
| V-R06 | 缩写在首次出现时定义 | 质检警告 |
| V-R07 | 同一缩写只定义一次 | 质检警告 |

### 5.3 自动化检查脚本

```python
def check_variable_naming_consistency(sap_vars, code_vars, table_vars, figure_vars, text_vars):
    """
    检查变量命名一致性。

    Parameters
    ----------
    sap_vars : dict
        SAP 中定义的变量映射 {code_name: display_name}
    code_vars : list[str]
        代码中使用的变量名列表
    table_vars : list[str]
        表格中使用的变量名列表
    figure_vars : list[str]
        图表中使用的变量名列表
    text_vars : list[str]
        正文中使用的变量名列表

    Returns
    -------
    list[dict]
        不一致项列表
    """
    violations = []

    # V-R01: 代码变量名一致性
    for var in code_vars:
        if var not in sap_vars:
            violations.append({
                "rule": "V-R01",
                "variable": var,
                "issue": f"代码变量 '{var}' 不在SAP变量定义中"
            })

    # V-R02: 表格变量名一致性
    for var in table_vars:
        if var not in sap_vars.values():
            violations.append({
                "rule": "V-R02",
                "variable": var,
                "issue": f"表格变量 '{var}' 不在SAP规范显示名中"
            })

    # V-R03: 图表标签一致性
    for var in figure_vars:
        if var not in sap_vars.values():
            violations.append({
                "rule": "V-R03",
                "variable": var,
                "issue": f"图表标签 '{var}' 不在SAP规范显示名中"
            })

    # V-R04: 正文变量名一致性
    for var in text_vars:
        if var not in sap_vars.values():
            violations.append({
                "rule": "V-R04",
                "variable": var,
                "issue": f"正文变量 '{var}' 不在SAP规范显示名中"
            })

    return violations
```

---

## 六、变量字典模板

每个项目应维护一份变量字典，作为全流程变量命名的唯一来源：

```yaml
# variable_dictionary.yaml
# 项目变量字典 — 全流程变量命名的唯一来源

demographics:
  age:
    code_name: age
    display_name_zh: 年龄 (岁)
    display_name_en: Age (years)
    type: continuous
    unit: years
    description: 受试者入组时年龄

  sex:
    code_name: sex
    display_name_zh: 性别
    display_name_en: Sex
    type: categorical
    categories: [男, 女]
    description: 受试者生物学性别

vital_signs:
  systolic_bp:
    code_name: systolic_bp
    display_name_zh: 收缩压 (mmHg)
    display_name_en: Systolic BP (mmHg)
    type: continuous
    unit: mmHg
    abbreviation: SBP
    description: 动脉收缩压

outcomes:
  overall_survival:
    code_name: overall_survival
    display_name_zh: 总生存时间 (月)
    display_name_en: Overall survival (months)
    type: time_to_event
    unit: months
    abbreviation: OS
    description: 从随机化到任何原因死亡的时间
```

---

## 七、各 SKILL 集成点

| SKILL | 集成方式 | 检查时机 |
|-------|---------|---------|
| data-prep | 变量清洗时使用代码变量名 | Phase 2 变量清洗 |
| analysis-plan | SAP 中定义变量字典 | Phase 6 变量构造规格书 |
| analysis-exec | 代码中使用代码变量名，输出中使用规范显示名 | Phase 1 变量构造 + Phase 9 输出 |
| report | 表格/图表/正文中使用规范显示名 | Phase 3 表格 + Phase 4 图表 + Phase 1 解读 |
| pipeline | 质量门闸中检查变量命名一致性 | Stage 3.5 门闸 |
