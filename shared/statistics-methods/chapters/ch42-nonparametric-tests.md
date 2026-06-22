# 非参数检验方法

> 版本: 1.0 | 2026-06-13
> MSRA 关联: `analysis-plan` Phase 3 方法选择, `analysis-exec` Phase 7 假设检验

---

## 概述

非参数检验不依赖总体分布假设，适用于：
- 样本量小（n < 30）且分布未知
- 数据明显偏态分布
- 等级/有序数据
- 存在无法忽略的离群值

**核心权衡**: 非参数检验对分布无要求，但统计功效低于参数检验（约 95% 效率当正态假设成立时）。

---

## 一、方法选择决策树

```
数据类型?
├── 独立两组
│   ├── 正态 + 等方差 → 独立 t 检验
│   ├── 非正态 / 等级数据 → Mann-Whitney U (Wilcoxon rank-sum)
│   └── 配对设计 → 见下方
│
├── 独立多组 (≥3)
│   ├── 正态 + 等方差 → 单因素 ANOVA
│   ├── 非正态 / 等级数据 → Kruskal-Wallis
│   └── 事后比较 → Dunn 检验 (Bonferroni/BH 校正)
│
├── 配对两组
│   ├── 正态 → 配对 t 检验
│   └── 非正态 → Wilcoxon 符号秩检验
│
└── 重复测量 (≥3 时间点)
    ├── 正态 + 球形性 → 重复测量 ANOVA
    ├── 违反球形性 / 非正态 → Friedman 检验
    └── 事后比较 → Nemenyi 检验
```

---

## 二、Mann-Whitney U 检验 (Wilcoxon Rank-Sum)

### 适用场景
- 两独立组的连续/有序变量比较
- 不假设正态分布
- 原假设: 两组的分布相同（严格来说是 P(X>Y) = 0.5）

### 检验统计量

$$U = n_1 n_2 + \frac{n_1(n_1+1)}{2} - R_1$$

其中 $R_1$ 为第一组的秩和。

### 效应量

$$r = \frac{Z}{\sqrt{N}}$$

| r 值 | 效应大小 |
|------|---------|
| 0.10 | 小 |
| 0.30 | 中 |
| 0.50 | 大 |

### R 实现

```r
# 基础检验
wilcox.test(outcome ~ group, data = df, exact = FALSE)

# 效应量 (rstatix)
library(rstatix)
df %>% wilcox_effsize(outcome ~ group)
```

### 报告模板

> 采用 Mann-Whitney U 检验比较两组 {变量名} 的差异。{组1} 的中位数为 {M1} [IQR: {Q1}, {Q3}]，{组2} 的中位数为 {M2} [IQR: {Q1}, {Q3}]。两组差异具有{统计学意义/无统计学意义}（U = {U值}, p = {p值}, r = {r值}）。

---

## 三、Kruskal-Wallis 检验

### 适用场景
- 多独立组（≥3）的连续/有序变量比较
- 单因素 ANOVA 的非参数替代

### 检验统计量

$$H = \frac{12}{N(N+1)} \sum_{i=1}^{k} \frac{R_i^2}{n_i} - 3(N+1)$$

### 效应量 (Epsilon-squared)

$$\varepsilon^2 = \frac{H}{N-1}$$

| ε² 值 | 效应大小 |
|-------|---------|
| 0.01 | 小 |
| 0.06 | 中 |
| 0.14 | 大 |

### 事后比较: Dunn 检验

Kruskal-Wallis 显著后，使用 **Dunn 检验** 进行两两比较：
- 使用 Bonferroni 或 Benjamini-Hochberg 校正
- 不使用 Wilcoxon 作为事后检验（会导致 I 类错误膨胀）

```r
library(dunn.test)
dunn.test(df$outcome, df$group, method = "bonferroni")

# 或 rstatix
df %>% dunn_test(outcome ~ group, p.adjust.method = "bonferroni")
```

---

## 四、Wilcoxon 符号秩检验

### 适用场景
- 配对/前后设计的非参数检验
- 原假设: 差值的中位数为 0

### 效应量

$$r = \frac{Z}{\sqrt{N}}$$

其中 N 为配对数（非零差值的配对数）。

### R 实现

```r
wilcox.test(df$after, df$before, paired = TRUE)

# 效应量
df %>% wilcox_effsize(after ~ before, paired = TRUE)
```

---

## 五、Friedman 检验

### 适用场景
- 重复测量设计（≥3 时间点/条件）的非参数检验
- 每个受试者在所有条件下测量

### 检验统计量

$$\chi^2_F = \frac{12}{nk(k+1)} \sum_{j=1}^{k} R_j^2 - 3n(k+1)$$

其中 n = 受试者数, k = 条件数, $R_j$ = 第 j 个条件的秩和。

### 效应量 (Kendall's W)

$$W = \frac{\chi^2_F}{n(k-1)}$$

| W 值 | 效应大小 |
|------|---------|
| 0.10 | 小 |
| 0.30 | 中 |
| 0.50 | 大 |

### 事后比较: Nemenyi 检验

```r
library(PMCMRplus)
frdAllPairsNemenyiTest(outcome ~ condition | subject, data = df)
```

---

## 六、非参数检验的 Table 1

使用中位数 [IQR] 而非 均值 ± SD:

| 变量 | 组1 (n=X) | 组2 (n=Y) | p 值† |
|------|----------|----------|-------|
| 年龄 | 55 [45, 65] | 58 [48, 68] | 0.032‡ |
| 住院天数 | 7 [4, 12] | 5 [3, 9] | 0.008‡ |

† 非参数检验; ‡ Mann-Whitney U 检验

---

## 七、常见错误与反模式

| 错误 | 正确做法 |
|------|---------|
| Kruskal-Wallis 后用 Wilcoxon 做两两比较 | 用 Dunn 检验 |
| 对配对数据用 Mann-Whitney | 用 Wilcoxon 符号秩检验 |
| 非正态数据直接用对数转换后 t 检验 | 优先考虑非参数检验 |
| 所有数据都用非参数检验（保守过度） | 正态数据用参数检验（功效更高） |
| 样本量极小(n<5)时报告精确 p 值 | 使用精确检验或蒙特卡洛方法 |

---

## 八、样本量与功效

非参数检验在小样本时需要注意：
- n < 5 per group: 大多数非参数检验的功效很低，考虑精确检验
- n ≥ 20: 渐近近似足够准确
- 配对设计: 至少需要 6 对非零差值

---

## 九、参考资源

- **书籍**: Hollander, Wolfe & Chicken. *Nonparametric Statistical Methods* (3rd ed.)
- **R 包**: `rstatix` (tidy-friendly), `coin` (exact tests), `dunn.test`, `PMCMRplus`
- **Python**: `scipy.stats.mannwhitneyu`, `scipy.stats.kruskal`, `scipy.stats.wilcoxon`, `scipy.stats.friedmanchisquare`
- **MSRA 模板**: `shared/templates/nonparametric_template.R`
