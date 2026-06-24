# 统计检验决策树 — Medical Statistics Research Assistant

> **规范决策树源**: `skills/stat-method-selector/decision-tree.json`（15-goal, 112-method, 53篇文献支撑）
> **文献依据**: `skills/stat-method-selector/references.md`（53篇方法学论文结构化摘要 + 效应量解释标准）
> **方法映射**: `shared/statistics-methods/method_selector_mapping.md`（决策树方法→MSRA章节→R/Python实现）
>
> 本文档为本地速查版本。完整的多维度决策树（含因果推断、诊断试验、Meta分析、贝叶斯、缺失数据、等效/非劣效等分支）见 `stat-method-selector/decision-tree.json`。
>
> 参考：Epi R Handbook (https://epirhandbook.com/en/new_pages/stat_tests.html)
>         数据分析常用策略 — 三阶方法：base R (快速查看) → rstatix (管道处理) → gtsummary (出版级表格)

---

## 一、检验选择概览

```
                    ┌──── 数据准备 ────┐
                    │ 导入 → 清洗 → EDA │
                    └────────┬─────────┘
                             ↓
               ┌──── 变量类型判断 ────┐
               │  结局变量 × 分组变量   │
               └────────┬─────────┘
                        ↓
              ┌──── 假设条件检查 ────┐
              │  正态性 → 方差齐性    │
              │  (Shapiro-Wilk → Levene)│
              └────────┬─────────┘
                        ↓
               ┌──── 选择检验方法 ────┐
               │  参数 / 非参数 / 分类 │
               └────────┬─────────┘
                        ↓
               ┌──── 执行和解释 ────┐
               │  结果 → 效应量 → 报告 │
               └────────────────────┘
```

---

## 二、完整决策表

### 2.1 连续结局变量

| 分组情况 | 正态性 | 方差齐性 | 参数检验 | 非参数替代 | 重复测量 |
|----------|--------|----------|----------|------------|----------|
| **两组比较** | 是 | 是 | **独立 t 检验** | — | — |
| | 是 | 否 | **Welch t 检验** | — | — |
| | 否 | — | — | **Wilcoxon 秩和检验** | — |
| **配对两组** | 是 | — | **配对 t 检验** | — | — |
| | 否 | — | — | **配对 Wilcoxon** | — |
| **多组比较** | 是 | 是 | **单因素方差分析** | — | — |
| | 是 | 否 | **Welch ANOVA** | — | — |
| | 否 | — | — | **Kruskal-Wallis 检验** | — |
| **重复测量** | 是 | — | **重复测量 ANOVA** | — | — |
| | 否 | — | — | **Friedman 检验** | — |

### 2.2 分类结局变量

| 设计类型 | 推荐检验 | 适用条件 | 替代方法 |
|----------|----------|----------|----------|
| **2×2 四格表** | **χ² 检验** | 所有期望频数 ≥ 5 | Fisher 精确检验 |
| **R×C 列联表** | **χ² 检验** | <20% 单元格期望 <5 | Fisher 精确检验 / 似然比检验 |
| **配对分类** | **McNemar 检验** | 2×2 配对设计 | — |
| **分层分类** | **Cochran-Mantel-Haenszel** | 分层 χ² | — |
| **有序分类** | **Cochran-Armitage 趋势检验** | 暴露水平有序 | — |

### 2.3 相关性分析

| 变量类型 | 方法 | 相关系数 | 假设条件 |
|----------|------|----------|----------|
| 连续 × 连续 | **Pearson** | r | 双变量正态 |
| 连续 × 连续 | **Spearman** | ρ | 单调关系（无正态要求） |
| 连续 × 连续 | **Kendall τ** | τ | 小样本/有结值 |
| 分类 × 连续 | **点二列相关** | r_pb | 二分变量+连续 |
| 有序 × 有序 | **Kendall τ-b** | τ_b | 有序分类 |

---

## 三、R 函数速查表

### 3.1 base R（快速查看）

| 检验 | 函数 | 语法 |
|------|------|------|
| 独立 t 检验 | `t.test()` | `t.test(y ~ x, data = df)` |
| 配对 t 检验 | `t.test()` | `t.test(y1, y2, paired = TRUE)` |
| Wilcoxon 秩和 | `wilcox.test()` | `wilcox.test(y ~ x, data = df)` |
| 方差分析 | `aov()` | `aov(y ~ x, data = df)` |
| Kruskal-Wallis | `kruskal.test()` | `kruskal.test(y ~ x, data = df)` |
| Pearson χ² | `chisq.test()` | `chisq.test(table(df$x, df$y))` |
| Fisher 精确 | `fisher.test()` | `fisher.test(table(df$x, df$y))` |
| 正态性检验 | `shapiro.test()` | `shapiro.test(df$y)` |
| 方差齐性 | `bartlett.test()` | `bartlett.test(y ~ x, data = df)` |
| Pearson 相关 | `cor.test()` | `cor.test(x, y, method = "pearson")` |
| Spearman 相关 | `cor.test()` | `cor.test(x, y, method = "spearman")` |

### 3.2 rstatix（管道友好，输出为数据框）

| 检验 | 函数 | 特性 |
|------|------|------|
| 独立 t 检验 | `t_test()` | 支持 `group_by()` 自动分组 |
| Welch t 检验 | `t_test(var.equal = FALSE)` | 方差不齐时的替代 |
| 配对 t 检验 | `t_test(paired = TRUE)` | — |
| Wilcoxon 检验 | `wilcox_test()` | 支持配对 |
| 单因素 ANOVA | `anova_test()` | 自动输出效应量 |
| Welch ANOVA | `welch_anova_test()` | — |
| Kruskal-Wallis | `kruskal_test()` | — |
| 卡方检验 | `chisq_test()` | 对矩阵操作 |
| Fisher 检验 | `fisher_test()` | — |
| McNemar 检验 | `mcnemar_test()` | — |
| Cochran's Q | `cochran_q_test()` | 重复测量分类 |
| 正态性（批量） | `shapiro_test()` | 支持多变量 |
| 方差齐性 | `levene_test()` | — |
| Tukey HSD 事后 | `tukey_hsd()` | ANOVA 事后比较 |
| Dunn 检验事后 | `dunn_test()` | Kruskal-Wallis 事后 |
| Games-Howell 事后 | `games_howell_test()` | Welch ANOVA 事后 |
| 效应量 | `wilcox_effsize()` | Wilcoxon 效应量 |

### 3.3 gtsummary（出版级表格）

| 函数 | 用途 |
|------|------|
| `tbl_summary()` | 基线特征表 |
| `add_p()` | 自动添加 p 值 |
| `add_q()` | 多重比较校正 |
| `add_overall()` | 添加合计列 |
| `add_ci()` | 添加置信区间 |
| `tbl_regression()` | 回归结果表 |
| `tbl_uvregression()` | 单变量回归汇总 |

---

## 四、典型工作流示例

### 4.1 两步自动选择

```r
# Step 1: 检查正态性
library(rstatix)
df %>% shapiro_test(score)

# Step 2: 选择适当检验
# 正态 → t.test / anova
# 非正态 → wilcox.test / kruskal.test
df %>% t_test(score ~ group)     # 参数
df %>% wilcox_test(score ~ group) # 非参数
```

### 4.2 出版级表格 + 自动 p 值

```r
library(gtsummary)

df %>%
  tbl_summary(by = treatment,
    statistic = list(all_continuous() ~ "{median} ({p25}, {p75})",
                     all_categorical() ~ "{n} ({p}%)")) %>%
  add_p() %>%
  add_overall() %>%
  bold_labels()
```

### 4.3 分组自动检验

```r
# 按 visit 分组自动运行
df %>%
  group_by(visit) %>%
  t_test(score ~ treatment) %>%
  add_significance()
```

---

## 五、常见陷阱与注意事项

1. **多重比较**：多次检验需校正 p 值（Bonferroni / Holm / FDR）
2. **小样本**：n < 30 优先考虑非参数方法
3. **有序分类变量**：不应当作连续变量处理
4. **正态性检验在大样本下的局限**：n > 500 时 Shapiro-Wilk 过于敏感，建议结合 Q-Q 图
5. **效应量报告**：p 值不反映效应大小，始终报告 Cohen's d / r / η²
6. **Fisher 精确检验的局限**：2×2 表以外建议使用模拟 p 值 (`simulate.p.value=TRUE`)
