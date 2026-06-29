# 变量命名与统计展示标准

> MSRA 项目专用。定义所有学术图表和表格中变量命名、统计术语格式、数据完整性的统一标准。
> 适用范围：Stage 3 (analysis-exec) 统计输出、Stage 4 (report) 图表与表格、
> Stage 5 (report/论文模式) 正文与结果展示。
>
> 与本文件的关系：
> - `resources/chart-styles/variable_naming_conventions.md` — 代码层三列命名体系（代码变量名 → 显示名映射）
> - `resources/chart-styles/publication_figure_standards.md` — 图表视觉规范（配色、布局、导出）
> - **本文件** — 学术展示层的命名、术语格式、数据完整性标准

---

## 一、变量命名总则

### 原则 1：使用学术标准全称

变量名应使用学术论文中的标准全称，不使用随意缩写。

- 首次出现时给出全称 + 括号缩写，后续可直接使用缩写
- 例外：国际通用缩写无需全称定义，如 HR、OR、RR、CI、P 值
- **禁止**：使用代码缩写作为展示名（如 `sbp`、`hba1c`）

```
正确：去势抵抗性前列腺癌（CRPC） / Castration-resistant prostate cancer (CRPC)
错误：CRPC（无全称）/ 前列腺癌（缩写未定义）
```

### 原则 2：括号规范

| 语境 | 括号类型 | 示例 |
|------|---------|------|
| 中文变量名 | 中文全角括号 `（）` | 前列腺特异性抗原（PSA） |
| 英文变量名 | 半角括号 `()` | Prostate-specific antigen (PSA) |
| 单位标注 | 半角括号 `()` | 身高 (cm) / Height (cm) |
| 置信区间 | 半角括号 `()` | HR=1.23 (95%CI: 1.05-1.45) |
| 统计检验结果 | 半角括号 `()` | F(2, 98) = 4.56, P = 0.013 |

### 原则 3：单位紧跟变量名

- 单位用半角括号包裹，紧接变量名后
- 变量名与括号之间保留一个空格
- 复合单位使用 Unicode 上标和斜杠

```
正确：体质指数 (BMI, kg/m²) / Body mass index (BMI, kg/m²)
错误：BMI (kg/m2) / BMI kg/m² / 体质指数, kg/m²
```

### 原则 4：统计学术语使用国际标准写法

遵循 APA、AMA、ICMJE 等国际出版规范：

- P 为大写斜体（`*P*`），后接精确值或不等号
- CI 格式为 `95%CI: 下限-上限`
- 效应量名称与数值之间无空格：`HR=1.23`
- 统计检验名称使用标准缩写：`t`、`F`、`χ²`、`Z`

---

## 二、变量名称转换规则

### 2.1 转换总则

原始数据中的变量名（通常为代码格式）在进入学术展示时，必须按照以下规则转换：

| 转换操作 | 说明 | 示例 |
|---------|------|------|
| 下划线 → 空格 | 代码中的下划线替换为空格 | `crpc_月` → `CRPC 时间（月）` |
| 缩写 → 全称 | 专业缩写首次出现需给出全称 | `psa` → `前列腺特异性抗原（PSA）` |
| 单位提取 | 尾部单位标记提取为括号单位 | `身高_cm` → `身高（cm）` |
| 首字母大写 | 英文显示名每个实词首字母大写 | `progression_free_survival` → `Progression-free survival (months)` |
| 类型标注 | 明确变量的分析类型（连续/分类/时间） | 用于指导展示格式 |

### 2.2 肿瘤学与泌尿外科变量

| 原始名称 | 标准名称（中文） | 标准名称（英文） | 说明 |
|---------|----------------|----------------|------|
| crpc_月 | CRPC 时间（月） | CRPC duration (months) | 下划线→空格，缩写→全称 |
| mcrpc | 转移性去势抵抗性前列腺癌（mCRPC） | Metastatic castration-resistant prostate cancer (mCRPC) | 疾病全称 |
| psa | 前列腺特异性抗原（PSA） (ng/mL) | Prostate-specific antigen (PSA) (ng/mL) | 检验指标 |
| gs | Gleason 评分（GS） | Gleason score (GS) | 病理评分 |
| tnm_stage | TNM 分期 | TNM staging | 分期系统 |
| gleason_score | Gleason 评分 | Gleason score | 病理评分 |
| bone_scan | 骨扫描结果 | Bone scan result | 影像学 |
| metastasis_site | 转移部位 | Site of metastasis | — |
| docetaxel_line | 多西他赛治疗线数 | Docetaxel treatment line | 治疗线数 |
| enzalutamide | 恩扎卢胺 | Enzalutamide | 药物名称 |
| abiraterone | 阿比特龙 | Abiraterone | 药物名称 |
| radium_223 | 镭-223 | Radium-223 | 药物名称 |
| alkaline_phosphatase | 碱性磷酸酶 (U/L) | Alkaline phosphatase (U/L) | 检验指标 |
| lactate_dehydrogenase | 乳酸脱氢酶 (U/L) | Lactate dehydrogenase (U/L) | 检验指标 |

### 2.3 人口学与体格检查变量

| 原始名称 | 标准名称（中文） | 标准名称（英文） | 说明 |
|---------|----------------|----------------|------|
| 身高_cm | 身高（cm） | Height (cm) | 下划线→括号 |
| 体重_kg | 体重（kg） | Weight (kg) | 同上 |
| bmi | 体质指数（BMI） (kg/m²) | Body mass index (BMI) (kg/m²) | 首次出现给出全称 |
| 年龄 | 年龄（岁） | Age (years) | — |
| 性别 | 性别 | Sex | 二分类变量 |
| 民族 | 民族 | Ethnicity | — |
| 受教育程度 | 受教育程度 | Education level | — |
| 婚姻状况 | 婚姻状况 | Marital status | — |
| 吸烟史 | 吸烟史 | Smoking history | 二分类或多分类 |
| 饮酒史 | 饮酒史 | Alcohol use history | — |

### 2.4 生命体征变量

| 原始名称 | 标准名称（中文） | 标准名称（英文） | 说明 |
|---------|----------------|----------------|------|
| 收缩压_mmHg | 收缩压 (mmHg) | Systolic blood pressure (mmHg) | — |
| 舒张压_mmHg | 舒张压 (mmHg) | Diastolic blood pressure (mmHg) | — |
| 心率_次每分 | 心率 (次/分) | Heart rate (beats/min) | — |
| 呼吸频率 | 呼吸频率 (次/分) | Respiratory rate (breaths/min) | — |
| 体温_℃ | 体温 (°C) | Temperature (°C) | — |
| 血氧饱和度 | 血氧饱和度 (%) | Oxygen saturation (SpO₂) (%) | — |

### 2.5 实验室检查变量

| 原始名称 | 标准名称（中文） | 标准名称（英文） | 说明 |
|---------|----------------|----------------|------|
| HbA1c | 糖化血红蛋白（HbA1c） (%) | Glycated hemoglobin (HbA1c) (%) | 检验指标 |
| eGFR | 估算肾小球滤过率（eGFR） (mL/min/1.73m²) | Estimated glomerular filtration rate (eGFR) (mL/min/1.73m²) | 同上 |
| 空腹血糖 | 空腹血糖 (mmol/L) | Fasting blood glucose (mmol/L) | — |
| 血肌酐 | 血肌酐 (μmol/L) | Serum creatinine (μmol/L) | — |
| 总胆固醇 | 总胆固醇 (mmol/L) | Total cholesterol (mmol/L) | — |
| 甘油三酯 | 甘油三酯 (mmol/L) | Triglycerides (mmol/L) | — |
| LDL胆固醇 | 低密度脂蛋白胆固醇 (mmol/L) | Low-density lipoprotein cholesterol (mmol/L) | LDL-C |
| HDL胆固醇 | 高密度脂蛋白胆固醇 (mmol/L) | High-density lipoprotein cholesterol (mmol/L) | HDL-C |
| 白细胞计数 | 白细胞计数 (×10⁹/L) | White blood cell count (×10⁹/L) | — |
| 血红蛋白 | 血红蛋白 (g/L) | Hemoglobin (g/L) | — |
| 血小板计数 | 血小板计数 (×10⁹/L) | Platelet count (×10⁹/L) | — |
| ALT | 丙氨酸氨基转移酶 (U/L) | Alanine aminotransferase (U/L) | ALT |
| AST | 天冬氨酸氨基转移酶 (U/L) | Aspartate aminotransferase (U/L) | AST |

### 2.6 安全性变量

| 原始名称 | 标准名称（中文） | 标准名称（英文） | 说明 |
|---------|----------------|----------------|------|
| AE | 不良事件（AE） | Adverse event (AE) | 安全性术语 |
| SAE | 严重不良事件（SAE） | Serious adverse event (SAE) | 同上 |
| TRAE | 治疗相关不良事件（TRAE） | Treatment-related adverse event (TRAE) | 同上 |
| G3_AE | 3级不良事件 | Grade 3 adverse event | CTCAE 分级 |
| AESI | 特别关注不良事件（AESI） | Adverse event of special interest (AESI) | 同上 |
| DLT | 剂量限制性毒性（DLT） | Dose-limiting toxicity (DLT) | 同上 |
| discontinuation | 因不良事件停药 | Discontinuation due to AE | — |
| dose_reduction | 剂量调整 | Dose reduction | — |

### 2.7 生存与疗效变量

| 原始名称 | 标准名称（中文） | 标准名称（英文） | 说明 |
|---------|----------------|----------------|------|
| OS | 总生存期（OS） (月) | Overall survival (OS) (months) | 生存指标 |
| PFS | 无进展生存期（PFS） (月) | Progression-free survival (PFS) (months) | 同上 |
| EFS | 无事件生存期（EFS） (月) | Event-free survival (EFS) (months) | 同上 |
| DSS | 疾病特异性生存期（DSS） (月) | Disease-specific survival (DSS) (months) | 同上 |
| TTP | 至进展时间（TTP） (月) | Time to progression (TTP) (months) | 同上 |
| ORR | 客观缓解率（ORR） (%) | Objective response rate (ORR) (%) | 疗效指标 |
| DCR | 疾病控制率（DCR） (%) | Disease control rate (DCR) (%) | 同上 |
| DOR | 缓解持续时间（DOR） (月) | Duration of response (DOR) (months) | 同上 |
| TTR | 至缓解时间（TTR） (月) | Time to response (TTR) (months) | 同上 |
| TTD | 至停药时间（TTD） (月) | Time to discontinuation (TTD) (months) | 同上 |

### 2.8 统计效应量变量

| 原始名称 | 标准名称（中文） | 标准名称（英文） | 说明 |
|---------|----------------|----------------|------|
| HR | 风险比（HR） | Hazard ratio (HR) | 效应量 |
| OR | 比值比（OR） | Odds ratio (OR) | 同上 |
| RR | 相对危险度（RR） | Relative risk (RR) | 同上 |
| RD | 风险差（RD） | Risk difference (RD) | 同上 |
| NNT | 需治疗人数（NNT） | Number needed to treat (NNT) | 同上 |
| AUC | 曲线下面积（AUC） | Area under the curve (AUC) | 诊断/预测 |
| C_statistic | C 统计量（C-statistic） | C-statistic | 同上 |
| Brier_score | Brier 评分 | Brier score | 校准指标 |
| VIF | 方差膨胀因子（VIF） | Variance inflation factor (VIF) | 共线性诊断 |
| ICC | 组内相关系数（ICC） | Intraclass correlation coefficient (ICC) | 一致性 |

---

## 三、统计学术语标准写法

### 3.1 置信区间

| 项目 | 标准写法 | 错误写法 | 说明 |
|------|---------|---------|------|
| 格式 | 95%CI: 1.2-3.4 | ~~CI 95% (1.2,3.4)~~ / ~~95% CI (1.2 to 3.4)~~ | 冒号分隔，短横线连接上下限 |
| 位置 | 紧跟点估计值后 | 置于句末 | HR=1.23, 95%CI: 1.05-1.45 |
| 非默认置信水平 | 99%CI: 1.1-3.5 | ~~99% CI~~ | 同格式，仅改百分比 |
| 多个 CI | 分别标注 | 合并 | 各效应量各自附 CI |

```
正确：HR=1.23, 95%CI: 1.05-1.45, P=0.013
错误：HR 1.23 (95% CI: 1.05-1.45), p=0.013
错误：Hazard ratio = 1.23 (95 percent confidence interval: 1.05-1.45)
```

### 3.2 P 值

| 项目 | 标准写法 | 错误写法 | 说明 |
|------|---------|---------|------|
| 精确值 | P=0.023 | ~~p=0.023~~ / ~~P = 0.023~~ | P 大写无空格 |
| 小值 | P<0.001 | ~~P=0.000~~ / ~~P<0.0001~~ | 不展示超过 3 位的精确值 |
| 无显著性 | P=0.342 | ~~P=NS~~ / ~~P>0.05~~ | 始终报告精确值 |
| 边界显著 | P=0.051 | ~~P≈0.05~~ / ~~P~0.05~~ | 不使用约等号 |
| 检验方法 | Log-rank P=0.023 | ~~p=0.023 (logrank)~~ | 检验方法前置于 P 之前 |

### 3.3 描述性统计量

| 项目 | 标准写法（中文表格） | 标准写法（英文表格） | 错误写法 |
|------|-------------------|-------------------|---------|
| 均数 ± 标准差 | 23.5 ± 4.2 | 23.5 ± 4.2 (或 23.5 [4.2]) | ~~23.5 + 4.2~~ / ~~23.5(SD 4.2)~~ |
| 中位数 (IQR) | 中位数 45.2 (Q1: 32.1, Q3: 58.3) | Median 45.2 (IQR: 32.1-58.3) | ~~Median (IQR) 45.2 (32.1, 58.3)~~ |
| 中位数 [范围] | 45.2 [18.3-72.1] | 45.2 [18.3-72.1] | ~~45.2 (range 18.3-72.1)~~ |
| 频数 (百分比) | 123 (45.6%) | 123 (45.6%) | ~~45.6% (n=123)~~ / ~~123/270~~ |
| 分子/分母 | 123/270 (45.6%) | 123/270 (45.6%) | ~~123 (45.6%) [无分母]~~ |

### 3.4 效应量

| 项目 | 标准写法 | 错误写法 | 说明 |
|------|---------|---------|------|
| 风险比 | HR=1.23, 95%CI: 1.05-1.45 | ~~HR 1.23 (1.05-1.45)~~ / ~~Hazard ratio: 1.23~~ | 必须附 CI |
| 比值比 | OR=2.1, 95%CI: 1.3-3.4 | ~~OR 2.1~~ | 同上 |
| 相对危险度 | RR=0.8, 95%CI: 0.6-1.0 | ~~RR 0.8~~ | 同上 |
| 均值差 | MD=-3.2, 95%CI: -5.1--1.3 | ~~Mean diff -3.2~~ | 同上 |
| 标准化均值差 | SMD=0.45, 95%CI: 0.12-0.78 | ~~SMD 0.45~~ | 同上 |

### 3.5 生存分析

| 项目 | 标准写法 | 错误写法 | 说明 |
|------|---------|---------|------|
| 生存率 | 5年生存率: 78.5% (95%CI: 72.1-84.9%) | ~~5yr OS 78.5%~~ | 完整格式 |
| 中位生存时间 | 中位生存时间: 24.5个月 (95%CI: 18.3-30.7) | ~~MST 24.5~~ / ~~mOS 24.5mo~~ | 必须附 CI |
| Log-rank 检验 | Log-rank P=0.023 | ~~p=0.023~~ | 标注检验方法 |
| Cox 回归 | HR=1.23, 95%CI: 1.05-1.45, P=0.013 | ~~Cox: HR 1.23~~ | 标注模型类型 |
| 竞争风险 | 竞争风险模型: SHR=1.10, 95%CI: 0.85-1.42 | ~~Fine-Gray HR 1.10~~ | 标注模型类型 |

### 3.6 检验统计量

| 检验方法 | 标准写法 | 说明 |
|---------|---------|------|
| t 检验 | t(98) = 2.34, P = 0.021 | 报告自由度 |
| F 检验 | F(2, 98) = 4.56, P = 0.013 | 报告两组自由度 |
| 卡方检验 | χ²(1) = 5.67, P = 0.017 | 希腊字母 χ |
| Wilcoxon 检验 | Z = -2.34, P = 0.019 | 报告 Z 值 |
| Mann-Whitney U | U = 1234, P = 0.025 | — |
| Kruskal-Wallis | H(2) = 7.89, P = 0.019 | 报告自由度 |
| Fisher 精确检验 | P = 0.034 | 无检验统计量 |

---

## 四、统计数据完整性要求

### 4.1 必须展示的统计量

| 数据类型 | 必须展示 | 格式示例 | 禁止省略 |
|---------|---------|---------|---------|
| 中位生存时间 | 中位数 + [Q1, Q3] 或 95%CI | 24.5个月 (Q1: 18.3, Q3: 30.7) | 不得只展示中位数 |
| 连续变量（非正态） | 中位数 (IQR) | 45.2 (32.1, 58.3) | 不得只展示中位数 |
| 连续变量（正态） | 均数 ± 标准差 | 23.5 ± 4.2 | 不得省略标准差 |
| 分类变量 | 频数 (百分比) | 123 (45.6%) | 不得只展示频数或只展示百分比 |
| 效应量 (HR/OR/RR) | 点估计 + 95%CI | HR=1.23 (95%CI: 1.05-1.45) | 不得省略 CI |
| P 值 | 精确值或界限 | P=0.023 或 P<0.001 | 不得写 P=0.000 或 P=NS |
| 诊断准确性 | 敏感度 + 特异度 + AUC + 95%CI | 敏感度: 85.2% (95%CI: 78.3-90.5%) | 不得只报 AUC |
| 预测模型 | AUC + Brier Score + 校准截距/斜率 | AUC=0.82 (95%CI: 0.76-0.88) | 不得只报 AUC |

### 4.2 分子/分母规范

- 分类变量的频数必须包含总数（分母）
- 百分比基于有效分析人数（排除缺失值后）
- 亚组分析的分母必须明确

```
正确：完全缓解 45/120 (37.5%)
正确：完全缓解 45 (37.5%)*  *n=120
错误：完全缓解 37.5%（无分子分母）
错误：完全缓解 45/120（无百分比）
```

### 4.3 表格注释要求

每个统计表格必须包含以下脚注（按顺序）：

| 脚注类型 | 内容 | 示例 |
|---------|------|------|
| 统计量说明 | 定义各列展示的统计量 | 连续变量以均数 ± 标准差或中位数 (Q1, Q3) 表示；分类变量以频数 (百分比) 表示 |
| 置信水平 | 统一说明 CI 水平 | 95%CI 表示 95% 置信区间 |
| 检验方法 | 说明组间比较所用检验 | 组间比较使用 t 检验、Mann-Whitney U 检验、χ² 检验或 Fisher 精确检验 |
| 缺失值 | 说明缺失值处理方式 | * 有缺失值，总分析人数 < 总随机化人数 |
| ITT/PP | 说明分析人群 | 分析基于意向性治疗（ITT）人群 |
| 特殊标注 | 说明脚注标记 | 与对照组比较，*P<0.05, **P<0.01, ***P<0.001 |

### 4.4 数值精度标准

| 数据类型 | 精度要求 | 示例 |
|---------|---------|------|
| P 值 | 3 位小数（<0.001 时用不等号） | P=0.023 / P<0.001 |
| 百分比 | 1 位小数 | 45.6% |
| 均数 | 与原始数据精度一致或多 1 位 | 原始 23.5 → 展示 23.5 |
| 标准差 | 与均数相同精度 | 23.5 ± 4.2 |
| 效应量 (HR/OR/RR) | 2 位小数 | HR=1.23 |
| 置信区间 | 2 位小数 | 95%CI: 1.05-1.45 |
| AUC | 2 位小数 | AUC=0.82 |
| 样本量 | 整数 | n=120 |

---

## 五、图表规范

### 5.1 图表标题格式

| 元素 | 英文格式 | 中文格式 |
|------|---------|---------|
| 图标题 | Figure 1. Kaplan-Meier Curve of Overall Survival | 图 1 总生存期的 Kaplan-Meier 曲线 |
| 表标题 | Table 1. Baseline Characteristics of Study Population | 表 1 研究人群基线特征 |
| 补充图 | Supplementary Figure S1. Subgroup Analysis of Progression-Free Survival | 补充图 S1 无进展生存期的亚组分析 |
| 补充表 | Supplementary Table S1. Sensitivity Analysis Results | 补充表 S1 敏感性分析结果 |

标题规则：
- 图标题以 "Figure N." 开头，表标题以 "Table N." 开头
- 中文格式为 "图 N" 或 "表 N"（数字后无句号）
- 标题首字母大写（英文）
- 标题简洁完整，不含缩写

### 5.2 坐标轴标签

| 图表类型 | X 轴 | Y 轴 |
|---------|------|------|
| KM 生存曲线 | 随机化后时间 (月) / Time since randomization (months) | 生存概率 / Survival probability |
| 森林图 | 效应量 (HR 或 OR) / Effect estimate (HR or OR) | 变量名称 / Variable |
| ROC 曲线 | 1 - 特异度 / 1 - Specificity | 敏感度 / Sensitivity |
| 校准曲线 | 预测概率 / Predicted probability | 观测概率 / Observed probability |
| 决策曲线 | 阈值概率 (%) / Threshold probability (%) | 净获益 / Net benefit |
| RCS 曲线 | 暴露变量值 / Exposure value | 结局的 log(OR) / log(OR) of outcome |
| 柱状图 | 变量名 (含单位) / Variable (unit) | 频数或百分比 / Frequency or percentage |
| 散点图 | X 变量名 (单位) / X variable (unit) | Y 变量名 (单位) / Y variable (unit) |

禁止事项：
- 不得将 OS、PFS 等缩写直接作为坐标轴标签
- 不得使用代码变量名作为坐标轴标签
- 不得省略坐标轴标签

### 5.3 图例规范

| 规则 | 要求 |
|------|------|
| 名称 | 使用完整变量名称（不缩写），如"治疗组"而非"Trt" |
| 位置 | 统一置于图内右上或右下（避免遮挡数据） |
| 语言 | 中文图例用中文，英文图例用英文，不混用 |
| 排序 | 与图中数据顺序一致 |
| 格式 | 无边框（`frameon=False`），线条+标记与图中一致 |

### 5.4 P 值标注规范

| 规则 | 要求 |
|------|------|
| 格式 | P=0.023（精确值）或 P<0.001（界限值） |
| 位置 | 比较组之间的连线正上方 |
| 方法标注 | Log-rank P=0.023、Fisher P=0.034 等 |
| 禁止 | 仅使用星号（*）标注，不给精确值 |
| 星号约定 | 如需星号：*P<0.05, **P<0.01, ***P<0.001 |

### 5.5 KM 生存曲线专项

KM 曲线必须包含以下元素：

| 元素 | 要求 |
|------|------|
| 曲线 | 各组分别绘制，线宽一致 |
| 删失标记 | 竖线标记删失事件（`+` 标记） |
| 风险人数表 | 图下方对齐时间点，标注各组 At risk 人数 |
| 中位数标注 | 图内或图注中报告各组中位生存时间 + 95%CI |
| P 值 | Log-rank 检验 P 值标注于图内 |
| 样本量 | 图注中注明各组样本量 |

```
图注示例（中文）：
风险人数表显示各时间点仍处于风险中的人数。各组中位生存时间（95%CI）：
治疗组 24.5个月 (18.3-30.7)，对照组 16.2个月 (12.1-20.3)。
Log-rank P=0.023。

图注示例（英文）：
Numbers at risk indicate participants still at risk at each time point.
Median OS (95%CI): Treatment 24.5 months (18.3-30.7),
Control 16.2 months (12.1-20.3). Log-rank P=0.023.
```

---

## 六、变量名称映射表模板

项目变量字典应使用以下 YAML 格式维护，作为全流程变量命名的唯一来源：

```yaml
# variable_mapping.yaml
# 变量命名映射表 — MSRA 项目全流程变量标准化

# ── 元信息 ──────────────────────────────────────────────
metadata:
  version: "1.0.0"
  last_updated: "2026-06-21"
  description: "变量命名映射表，用于标准化所有学术图表和表格中的变量展示"

# ── 映射条目 ────────────────────────────────────────────
variable_mapping:

  # ── 肿瘤学变量 ──
  - raw: "crpc_月"
    zh: "CRPC 时间（月）"
    en: "CRPC duration (months)"
    category: "时间变量"
    unit: "月"
    type: "continuous"
    abbreviation: "CRPC"
    abbreviation_full_zh: "去势抵抗性前列腺癌"
    abbreviation_full_en: "Castration-resistant prostate cancer"

  - raw: "psa"
    zh: "前列腺特异性抗原（PSA） (ng/mL)"
    en: "Prostate-specific antigen (PSA) (ng/mL)"
    category: "实验室检查"
    unit: "ng/mL"
    type: "continuous"
    abbreviation: "PSA"
    abbreviation_full_zh: "前列腺特异性抗原"
    abbreviation_full_en: "Prostate-specific antigen"

  - raw: "gs"
    zh: "Gleason 评分（GS）"
    en: "Gleason score (GS)"
    category: "病理评分"
    unit: null
    type: "ordinal"
    abbreviation: "GS"
    abbreviation_full_zh: "Gleason 评分"
    abbreviation_full_en: "Gleason score"

  # ── 体格检查变量 ──
  - raw: "身高_cm"
    zh: "身高 (cm)"
    en: "Height (cm)"
    category: "体格检查"
    unit: "cm"
    type: "continuous"
    abbreviation: null
    abbreviation_full_zh: null
    abbreviation_full_en: null

  - raw: "体重_kg"
    zh: "体重 (kg)"
    en: "Weight (kg)"
    category: "体格检查"
    unit: "kg"
    type: "continuous"
    abbreviation: null
    abbreviation_full_zh: null
    abbreviation_full_en: null

  - raw: "bmi"
    zh: "体质指数 (BMI, kg/m²)"
    en: "Body mass index (BMI, kg/m²)"
    category: "体格检查"
    unit: "kg/m²"
    type: "continuous"
    abbreviation: "BMI"
    abbreviation_full_zh: "体质指数"
    abbreviation_full_en: "Body mass index"

  # ── 实验室检查变量 ──
  - raw: "HbA1c"
    zh: "糖化血红蛋白 (HbA1c) (%)"
    en: "Glycated hemoglobin (HbA1c) (%)"
    category: "实验室检查"
    unit: "%"
    type: "continuous"
    abbreviation: "HbA1c"
    abbreviation_full_zh: "糖化血红蛋白"
    abbreviation_full_en: "Glycated hemoglobin"

  - raw: "eGFR"
    zh: "估算肾小球滤过率 (eGFR) (mL/min/1.73m²)"
    en: "Estimated glomerular filtration rate (eGFR) (mL/min/1.73m²)"
    category: "实验室检查"
    unit: "mL/min/1.73m²"
    type: "continuous"
    abbreviation: "eGFR"
    abbreviation_full_zh: "估算肾小球滤过率"
    abbreviation_full_en: "Estimated glomerular filtration rate"

  # ── 安全性变量 ──
  - raw: "AE"
    zh: "不良事件 (AE)"
    en: "Adverse event (AE)"
    category: "安全性"
    unit: null
    type: "categorical"
    abbreviation: "AE"
    abbreviation_full_zh: "不良事件"
    abbreviation_full_en: "Adverse event"

  - raw: "SAE"
    zh: "严重不良事件 (SAE)"
    en: "Serious adverse event (SAE)"
    category: "安全性"
    unit: null
    type: "categorical"
    abbreviation: "SAE"
    abbreviation_full_zh: "严重不良事件"
    abbreviation_full_en: "Serious adverse event"

  # ── 生存与疗效变量 ──
  - raw: "OS"
    zh: "总生存期 (OS) (月)"
    en: "Overall survival (OS) (months)"
    category: "生存指标"
    unit: "月"
    type: "time_to_event"
    abbreviation: "OS"
    abbreviation_full_zh: "总生存期"
    abbreviation_full_en: "Overall survival"

  - raw: "PFS"
    zh: "无进展生存期 (PFS) (月)"
    en: "Progression-free survival (PFS) (months)"
    category: "生存指标"
    unit: "月"
    type: "time_to_event"
    abbreviation: "PFS"
    abbreviation_full_zh: "无进展生存期"
    abbreviation_full_en: "Progression-free survival"

  # ── 效应量变量 ──
  - raw: "HR"
    zh: "风险比 (HR)"
    en: "Hazard ratio (HR)"
    category: "效应量"
    unit: null
    type: "effect_measure"
    abbreviation: "HR"
    abbreviation_full_zh: "风险比"
    abbreviation_full_en: "Hazard ratio"

  - raw: "OR"
    zh: "比值比 (OR)"
    en: "Odds ratio (OR)"
    category: "效应量"
    unit: null
    type: "effect_measure"
    abbreviation: "OR"
    abbreviation_full_zh: "比值比"
    abbreviation_full_en: "Odds ratio"
```

---

## 七、各 Stage 集成指南

本标准在 MSRA 统一流水线中的集成点：

### 7.1 Stage 1 (data-prep) — 变量名称标准化检查

**集成时机**：Phase 2 变量清洗完成后

**检查内容**：
- 原始变量名是否已映射到标准名称
- 单位标注是否一致
- 缩写是否在变量字典中注册

**执行方式**：
```
对照 variable_mapping.yaml 检查清洗后数据集的变量名 →
输出不一致项列表 →
data-prep 修正变量标签
```

### 7.2 Stage 3 (analysis-exec) — 统计输出格式标准化

**集成时机**：Phase 9 统计输出生成时

**检查内容**：
- 效应量是否附带 95%CI
- P 值格式是否符合标准
- 描述性统计量格式是否正确（均数 ± SD / 中位数 IQR）

**执行方式**：
```
分析脚本输出 → 自动格式化函数处理 →
检查完整性（禁止省略 CI/SD/IQR） →
输出符合标准的统计结果表
```

**格式化函数模板**：
```python
def format_effect_size(estimate, ci_lower, ci_upper, effect_type="HR"):
    """格式化效应量输出。"""
    return f"{effect_type}={estimate:.2f}, 95%CI: {ci_lower:.2f}-{ci_upper:.2f}"

def format_p_value(p_val):
    """格式化 P 值输出。"""
    if p_val < 0.001:
        return "P<0.001"
    elif p_val < 0.01:
        return f"P={p_val:.3f}"
    else:
        return f"P={p_val:.3f}"

def format_continuous_normal(mean, sd):
    """格式化正态分布连续变量。"""
    return f"{mean:.1f} ± {sd:.1f}"

def format_continuous_skewed(median, q1, q3):
    """格式化偏态分布连续变量。"""
    return f"{median:.1f} (Q1: {q1:.1f}, Q3: {q3:.1f})"
```

### 7.3 Stage 4 (report) — 图表标注标准化

**集成时机**：Phase 3 表格生成 + Phase 4 图表生成

**检查内容**：
- 表格标题是否符合命名格式
- 坐标轴标签是否包含变量名和单位
- 图例是否使用完整变量名称
- 表注是否包含统计方法、置信水平、缺失值说明
- 缩写是否在首次出现时定义

**执行方式**：
```
report 生成图表/表格 → 自动检查脚本验证 →
对照本标准第 3-5 节逐项检查 →
输出合规报告 → 修正后重新生成
```

### 7.4 质量门闸集成

Stage 3.5 质量门闸报告中增加变量命名一致性检查项：

| 检查项 | 通过条件 | 违反后果 |
|-------|---------|---------|
| 变量名一致性 | SAP → 代码 → 表格 → 图表 → 正文完全一致 | 质检不通过 |
| 单位完整性 | 所有连续变量均标注单位 | 质检警告 |
| 缩写定义 | 所有缩写首次出现时给出全称 | 质检警告 |
| 统计量完整性 | 效应量附 CI，连续变量附 SD 或 IQR | 质检不通过 |
| P 值格式 | 无 P=0.000，无 P=NS | 质检警告 |
| 表注完整性 | 含统计方法、置信水平、缺失值说明 | 质检警告 |

---

## 八、常见错误与修正

| # | 常见错误 | 正确写法 | 说明 |
|---|---------|---------|------|
| 1 | P=0.000 | P<0.001 | 不报告超过 3 位的精确 P 值 |
| 2 | HR 1.23 (1.05-1.45) | HR=1.23, 95%CI: 1.05-1.45 | 效应量与数值之间用等号，CI 标注置信水平 |
| 3 | 45.6 | 45.6% | 百分比必须带百分号 |
| 4 | 123 例 | 123 (45.6%) | 频数必须附百分比 |
| 5 | median (IQR) = 45.2 (32.1, 58.3) | 中位数 45.2 (Q1: 32.1, Q3: 58.3) | 使用 Q1/Q3 而非 IQR |
| 6 | 收缩压 mmHg | 收缩压 (mmHg) | 单位用括号包裹 |
| 7 | BMI (kg.m-2) | BMI (kg/m²) | 使用斜杠和 Unicode 上标 |
| 8 | P=NS | P=0.342 | 始终报告精确 P 值 |
| 9 | OS (5yr) 78.5% | 5年生存率: 78.5% (95%CI: 72.1-84.9%) | 使用中文全称，附 CI |
| 10 | Figure 1: KM curve | Figure 1. Kaplan-Meier Curve of Overall Survival | 标题完整，不缩写 |

---

## 九、文件关联索引

| 文件 | 用途 | 与本文件关系 |
|------|------|------------|
| `resources/chart-styles/variable_naming_conventions.md` | 代码层三列命名体系 | 互补：该文件定义代码变量名映射，本文件定义学术展示标准 |
| `resources/chart-styles/publication_figure_standards.md` | 图表视觉规范 | 互补：该文件定义配色/布局/导出，本文件定义内容命名/术语格式 |
| `resources/statistics-methods/cheatsheet.md` | 统计方法速查 | 参考：统计术语的使用场景 |
| `src/shared/reporting-guidelines/` | 报告规范清单 | 参考：各指南对变量命名的要求 |
| `src/shared/sap/sap_standard.md` | SAP 标准 | 前置：SAP 中的变量定义应与本标准一致 |
| `resources/anti-patterns/medical_stats_anti_patterns.md` | 反模式 | 参考：变量命名相关的常见错误 |
