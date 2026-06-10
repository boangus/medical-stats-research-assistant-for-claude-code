# MSRA 项目整合分析报告

> 生成日期：2026-06-10
> 参考来源：AI4Research 综述论文、rio/janitor R 包、Epi R Handbook 统计检验章节

---

## 一、概览

本报告评估了四个外部参考源与 MSRA（Medical Statistics Research Assistant）项目的整合潜力：

| 参考源 | 类型 | 核心价值 |
|--------|------|----------|
| Chen et al. (2025) AI4Research Survey | 学术综述 | AI4Research 全流程框架、多Agent协作范式、自愈与反思机制 |
| rio R 包 | 数据 I/O 工具 | 统一 import/export/convert 接口，自动文件格式识别 |
| janitor R 包 | 数据清洗 + 制表 | clean_names + tabyl/adorn 流水线，直接对应 Table1/基线表 |
| Epi R Handbook stat_tests | 统计检验指南 | 三阶策略（base R → rstatix → gtsummary）、检验决策树 |

---

## 二、AI4Research 论文整合建议

### 2.1 多Agent协作深度优化（高优先级）

**现状**：MSRA 已定义 5 个 Agent 角色（Data Validator / Method Consultant / Exec Runner / Exec Inference / QC Inspector），采用 Generator-Evaluator 模式。

**论文参考**：
- Section 5.1.3: Team-Discussion-guided Mining — 多 Agent 角色扮演研究团队
- Section 5.4.4: Multi-Agent Interaction + External Tool Integration

**建议整合**：
1. **新增「文献检索Agent」**：作为独立 Agent 角色，在分析计划阶段（Stage 2）自动检索最新方法学文献和基准
2. **引入「审查讨论环」**：Exec Runner 和 Exec Inference 之间增加多轮讨论机制（如 VirSci 的迭代提案-批评模式）
3. **Agent 接棒协议升级**：在现有 handoff 消息基础上，增加 Agent 间的「分歧记录」和「方法降级提案」

### 2.2 实验预估与样本量验证增强（中优先级）

**现状**：MSRA Phase 0 包含样本量验证（≥90%通过、70-89%警告、<70%不足）。

**论文参考**：
- Section 5.4.2: Pre-Experiment Estimation — 评估性预测 + 探索性预测
- Section 5.4.1: Experiment Design — 半自动 + 全自动实验设计

**建议整合**：
1. **事前效应量预估**：在 SAP 阶段增加基于文献数据的效应量预估模块
2. **模拟实验（Simulated Experiment）**：在正式分析前，可先对模拟数据进行预分析，验证代码正确性
3. **事后功效再评估**：如果分析时发现某假设检验不显著，自动进行事后功效计算辅助解读

### 2.3 自愈 Debug 循环升级（中优先级）

**现状**：MSRA 已有 5 轮自愈 Debug（语法→运行时→统计诊断→数据检查→标记 SKIP）。

**论文参考**：
- Section 5.4.4: Self-Improvement — 迭代式自我改进
- Section 3.1.2: Self-Questioning & Self-Reflection — 自我提问与反思

**建议整合**：
1. **增加事前检查**：在 Phase 2（执行前检查）中增加代码静态分析，提前发现潜在问题
2. **事后反思摘要**：在 5 轮 Debug 后，自动生成分析偏差报告（做了什么修改、为什么、是否影响结果）

### 2.4 结果解读增强（低优先级）

**论文参考**：
- Section 6.1.2: Drawing Figures and Charts — 自动图表生成
- Section 7.3.2: Promotion Enhancement — 推广材料自动生成

**建议整合**：
1. **自动图形解读**：生成的图表（KM曲线/森林图/ROC）自动附带文字解读
2. **结果摘要生成**：在最终报告中增加面向非专业读者的「研究摘要」段落

---

## 三、rio R 包整合建议

### 3.1 统一数据导入接口（高优先级）

**概念**：rio 的 `import()` 函数根据文件扩展名自动选择合适的读取器。

**MSRA 整合**：
1. **复用 `shared/templates/00_config_template.R`**：增加自动格式识别逻辑
2. **新增数据导入模板**：在 `shared/templates/` 中新增 `import_data_template.R`，支持以下格式自动识别：

| 扩展名 | 格式 | 依赖包 |
|--------|------|--------|
| .csv | CSV | readr |
| .xlsx/.xls | Excel | readxl |
| .sav/.zsav | SPSS | haven |
| .dta | Stata | haven |
| .sas7bdat | SAS | haven |
| .rda/.rds | R 对象 | base |
| .json | JSON | jsonlite |
| .tsv | TSV | readr |
| .parquet | Parquet | arrow |

### 3.2 数据格式互转工具（低优先级）

**概念**：rio 的 `convert()` 函数实现格式转换。

**MSRA 整合**：在 `shared/data_sharing/` 中添加 `convert_template.R`，支持在数据库锁定后导出为标准格式包（CSV + SPSS + Stata）。

### 3.3 批量导入支持（低优先级）

**概念**：rio 的 `import_list()` 支持多对象文件（如 Excel 多工作表）。

**MSRA 整合**：在数据准备阶段（Stage 1）支持 Excel 多工作表导入，自动识别每个工作表的数据结构。

---

## 四、janitor R 包整合建议

### 4.1 数据清洗整合（高优先级）

**概念**：janitor 的 `clean_names()`、`remove_empty()`、`remove_constant()`、`convert_to_date()`。

**MSRA 整合**：
1. **Phase 1（数据验证）中增加列名清洗**：
   ```
   data_raw → clean_names() → remove_empty() → remove_constant() → data_clean
   ```
2. **Phase 3（执行清洗）的增强**：在现有清洗逻辑基础上，自动应用以下 janitor 功能：
   - `row_to_names()` — 将第一行提升为列名
   - `convert_to_date()` — 处理混合格式日期（MM/DD/YYYY 与数值格式共存）
3. **Phase 4（EDA）中增加数据质量检查**：
   - `get_dupes()` — 识别重复记录并输出详情
   - `compare_df_cols()` — 清洗前后对比列类型/列名变化

4. **建议代码模板**（放入 `shared/templates/`）：
```r
library(janitor)
library(dplyr)

# 清洗流水线
df_clean <- df_raw %>%
  clean_names() %>%
  remove_empty(c("rows", "cols")) %>%
  remove_constant() %>%
  mutate(across(where(is.character), ~na_if(., ""))) %>%
  mutate(across(contains("date"), ~convert_to_date(., character_fun = lubridate::ymd)))

# 检查重复
df_clean %>% get_dupes(id_col)

# 清洗前后对比
compare_df_cols(df_raw, df_clean)
```

### 4.2 Tabyl 制表整合（高优先级）

**概念**：janitor 的 `tabyl()` + `adorn_*()` 系列函数生成格式化频数表和交叉表。

**MSRA 整合** — 这是最直接、最有价值的整合领域！

**当前 MSRA Table 1 模板**（`shared/templates/table1_template.R`）可直接集成 janitor 流水线。

**具体建议**：

#### 4.2.1 单变量频数表（Phase 3-5 描述性统计）
现有代码可替换为：
```r
# 分类变量
df %>% tabyl(trt_group, gender) %>%
  adorn_totals("row") %>%
  adorn_percentages("col") %>%
  adorn_pct_formatting(digits = 1) %>%
  adorn_ns() %>%
  adorn_title("combined")
```

#### 4.2.2 基线特征表（Table 1）直接替换
直接嵌入 janitor 流水线替代当前复杂的 dplyr/tidyr 组合：
```r
# 自动化 Table 1
df %>%
  tabyl(trt_group, var1, var2) %>%
  adorn_totals("row") %>%
  adorn_percentages("col") %>%
  adorn_pct_formatting(digits = 1) %>%
  adorn_ns()
```

#### 4.2.3 三变量分层分析
```r
df %>% tabyl(race, outcome, gender) %>%
  adorn_percentages("row") %>%
  adorn_pct_formatting(digits = 2) %>%
  adorn_ns() %>%
  adorn_title("combined")
```

#### 4.2.4 在 `shared/templates/` 新增 `tabyl_template.R`
专用模板文件，覆盖以下场景：
- 双变量交叉表（2×2、R×C）
- 三变量分层表
- 带统计检验的输出（`chisq.test()` / `fisher.test()` 直接作用于 tabyl）
- Kable 输出（直接用于 R Markdown 报告）

```r
# 示例：带检验的双变量交叉表
library(janitor)
library(knitr)

df %>%
  tabyl(treatment, response) %>%
  adorn_totals(c("row", "col")) %>%
  adorn_percentages("row") %>%
  adorn_pct_formatting(digits = 1) %>%
  adorn_ns() %>%
  adorn_title("combined") %>%
  kable(caption = "Treatment Response by Group")

# 统计检验
chisq.test(df$treatment, df$response)
```

### 4.3 质量报告模板（低优先级）

**概念**：janitor 的 `compare_df_cols()` 用于数据框对比。

**MSRA 整合**：在数据质量门闸（Stage 1.5）中增加清洗前后对比报告生成。

---

## 五、Epi R Handbook 整合建议

### 5.1 统计检验三阶策略（高优先级）

**概念**：Epi R Handbook 的 stat_tests 章节提出三阶策略：
1. **base R** — 快速查看（`t.test()`, `chisq.test()`）
2. **rstatix** — 管道友好（`t_test()`, `wilcox_test()`, `chisq_test()`）
3. **gtsummary** — 出版级表格（`tbl_summary()` + `add_p()`）

**MSRA 整合**：MSRA 的 `analysis-exec/` 当前主要使用 base R。建议在 `shared/templates/` 中新增以下模板：

#### 5.1.1 新增 rstatix 模板（`rstatix_template.R`）
```r
library(rstatix)
library(dplyr)

# 分组 t 检验（自动输出数据框）
df %>%
  group_by(outcome) %>%
  t_test(age ~ gender) %>%
  add_significance()

# 多组比较
df %>% kruskal_test(score ~ group)

# 自动运行多个变量
df %>%
  select(numeric_vars) %>%
  map(~shapiro_test(.)) %>%
  bind_rows(.id = "variable")
```

#### 5.1.2 新增 gtsummary 模板（`gtsummary_template.R`）
```r
library(gtsummary)

# 基线特征表 + 自动 p 值
df %>%
  tbl_summary(
    by = treatment,
    statistic = list(all_continuous() ~ "{median} ({p25}, {p75})",
                     all_categorical() ~ "{n} ({p}%)"),
    digits = all_continuous() ~ 1
  ) %>%
  add_p() %>%
  add_overall() %>%
  bold_labels()
```

### 5.2 统计检验决策树形式化（中优先级）

**概念**：Epi R Handbook 提供了直观的检验选择逻辑：
```
连续vs分类 → 正态? → t检验 / Wilcoxon
分类vs分类 → 卡方检验
两组vs多组 → t检验或方差分析 / Kruskal-Wallis
```

**MSRA 整合**：
1. 在 `shared/statistics-methods/` 中新增 `stat_test_decision_tree.md`
2. 在 `analysis-plan/` 的 Phase 3（方法探讨）中，根据 EDA 结果自动建议合适的检验方法
3. 结构化决策表：

| 结局类型 | 分组类型 | 正态性 | 方差齐性 | 推荐检验 | rstatix 函数 |
|----------|----------|--------|----------|----------|-------------|
| 连续 | 两组 | 是 | 是 | 独立 t 检验 | `t_test()` |
| 连续 | 两组 | 否 | — | Wilcoxon | `wilcox_test()` |
| 连续 | 多组 | 是 | 是 | 方差分析 | `anova_test()` |
| 连续 | 多组 | 否 | — | Kruskal-Wallis | `kruskal_test()` |
| 分类 | 两组/多组 | — | — | 卡方/Fisher | `chisq_test()` / `fisher_test()` |
| 配对连续 | 两组 | 是 | — | 配对 t | `t_test(paired=TRUE)` |
| 配对连续 | 两组 | 否 | — | Wilcoxon 符号秩 | `wilcox_test(paired=TRUE)` |

### 5.3 corrr 相关性分析模板（低优先级）

**概念**：Epi R Handbook 推荐的 corrr 包提供 `correlate()` + `rplot()` 一站式相关性分析。

**MSRA 整合**：在 `shared/templates/` 新增 `correlation_template.R`：
```r
library(corrr)

df %>%
  select(continuous_vars) %>%
  correlate(method = "spearman") %>%
  shave() %>%
  fashion(decimals = 2) %>%
  rplot(shape = 15, colours = c("red", "white", "blue"))

# 网络图
df %>%
  correlate() %>%
  network_plot(min_cor = 0.3)
```

---

## 六、整合优先级总表

| 优先级 | 来源 | 建议内容 | 影响模块 | 预估工作量 |
|--------|------|----------|----------|-----------|
| **P0** | janitor | tabyl + adorn 制表流水线 | report/templates | 小（新增1个模板） |
| **P0** | Epi Hdbk + janitor | gtsummary Table 1 + janitor 基线表 | analysis-exec/templates | 小（新增2个模板） |
| **P0** | janitor | data-prep 清洗增强 | data-prep/shared | 中（修改SKILL.md+模板） |
| **P1** | rio | 统一数据导入 | data-prep/templates | 小（新增1个模板） |
| **P1** | Epi Hdbk | rstatix 统计检验模板 | analysis-exec/templates | 小（新增1个模板） |
| **P1** | AI4Research | 多Agent讨论环 | pipeline/agents | 中（修改协议文档） |
| **P1** | Epi Hdbk | 统计检验决策树 | analysis-plan/stats-methods | 中（新增1个md文档） |
| **P2** | AI4Research | 事前效应量预估 | analysis-plan | 中（新增模块） |
| **P2** | AI4Research | 事后反思/偏差报告 | analysis-exec | 中（修改Phase逻辑） |
| **P3** | AI4Research | 自动图形解读 | report | 大（需要LLM调用） |
| **P3** | rio | 格式互转/批量导入 | data-sharing | 小 |
| **P3** | Epi Hdbk | corrr 相关性分析 | templates | 小 |

---

## 七、建议实施路线

### Sprint 1（基础整合）
1. 新增 `shared/templates/janitor_tabyl_template.R` — tabyl 制表流水线
2. 新增 `shared/templates/rstatix_template.R` — rstatix 统计检验模板
3. 新增 `shared/templates/gtsummary_template.R` — gtsummary 基线表模板
4. 修改 `shared/templates/table1_template.R` — 集成 janitor 流水线

### Sprint 2（数据准备增强）
1. 修改 `skills/data-prep/SKILL.md` — 在清洗阶段增加 janitor 功能
2. 新增 `shared/templates/import_data_template.R` — rio 风格导入
3. 新增 `shared/statistics-methods/stat_test_decision_tree.md` — 检验决策树

### Sprint 3（高级功能）
1. 修改 `agents/protocol.md` — 增加 Agent 讨论环机制
2. 修改 `skills/analysis-exec/SKILL.md` — 增加事后反思摘要
3. 新增 `shared/templates/correlation_template.R` — corrr 相关性分析

---

## 附录：代码示例对比

### 现有 MSRA Table 1 代码（简化） vs 集成 janitor 后

**当前（dplyr/tidyr 组合）**：
```r
df %>%
  group_by(trt) %>%
  summarise(
    n = n(),
    age_mean = mean(age, na.rm = TRUE),
    age_sd = sd(age, na.rm = TRUE),
    male_pct = mean(gender == "Male", na.rm = TRUE) * 100
  ) %>%
  pivot_wider(names_from = trt, values_from = c(n, age_mean, age_sd, male_pct))
```

**集成 janitor + gtsummary 后（推荐）**：
```r
# 方式1：gtsummary（出版级）
df %>%
  tbl_summary(by = trt,
    statistic = list(all_continuous() ~ "{mean} ({sd})",
                     all_categorical() ~ "{n} ({p}%)")) %>%
  add_p() %>%
  add_overall()

# 方式2：janitor tabyl（快速交叉表）
df %>%
  tabyl(gender, trt) %>%
  adorn_percentages("col") %>%
  adorn_pct_formatting(digits = 1) %>%
  adorn_ns() %>%
  adorn_title("combined")
```

### 现有 MSRA 统计检验 vs 集成 rstatix 后

**当前（base R）**：
```r
t.test(age ~ gender, data = df)
wilcox.test(age ~ gender, data = df)
chisq.test(df$gender, df$outcome)
```

**集成 rstatix 后**：
```r
# 输出为数据框，便于后续处理
df %>% t_test(age ~ gender)
df %>% wilcox_test(age ~ gender)
df %>% chisq_test(gender, outcome)

# 分组自动运行
df %>%
  group_by(visit) %>%
  t_test(score ~ treatment)
```
