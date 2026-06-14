# 多重比较法

**作者**: Jing Cao, Song Zhang | **主译**: 龙宇琴

---

本章解释了什么时候对多重比较进行调整是合适的，列出了调整方法的局限性、如何解读和注意事项。

## 为什么要使用多重比较调整？

当在 5% 显著性水平上进行单个统计检验时，有 5% 的概率得出错误的结论（假阳性）。如果进行多次检验，每次检验有 5% 的假阳性风险，因此至少发生 1 次假阳性的概率（族错误率，FWER）随检验次数增加而急剧增大。

**FWER 计算示例**（假设 IER=5%）：
- K=1：FWER = 5%
- K=2：FWER = 1 − 0.95² = 10%
- K=3：FWER = 1 − 0.95³ = 14%
- K=20：FWER = 1 − 0.95²⁰ = 64%

## 常用校正方法

### 1. Bonferroni 校正
将显著性阈值按检验次数分割：IER = α / K。简单易操作，但过于保守，检验效能低。

### 2. Hochberg 序贯法
将 P 值从高到低排列，逐步放宽阈值。比 Bonferroni 检验效能更高。

**示例**（6 次检验，α=0.05）：
| 检验 | P值 | Bonferroni阈值 | Bonferroni结果 | Hochberg阈值 | Hochberg结果 |
|------|-----|---------------|---------------|-------------|-------------|
| 1 | 0.400 | 0.008 | 不显著 | 0.050 | 不显著 |
| 2 | 0.027 | 0.008 | 不显著 | 0.025 | 不显著 |
| 3 | 0.020 | 0.008 | 不显著 | 0.017 | 不显著 |
| 4 | 0.012 | 0.008 | 不显著 | 0.013 | 显著 |
| 5 | 0.005 | 0.008 | 显著 | 0.010 | 显著 |
| 6 | 0.003 | 0.008 | 显著 | 0.008 | 显著 |

### 3. FDR 控制（Benjamini-Hochberg）
控制假发现率（FDR）而非 FWER，适用于探索性分析中大量检验的场景，检验效能更高。

### 4. 关口策略（Gatekeeping）
分层控制：先检验主要终点，通过后再检验次要终点，依此类推。适用于多终点临床试验。

### 5. 图形化方法（Bretz Graphical Approach）🆕

> 现代 FWER 控制的主流方法（FDA/EMA 推荐），用**有向加权图**直观表达假设间的 α 分配与传递规则。
> 借鉴 Bretz F, Maurer W, Brannath W, Posch M. *A graphical approach to sequentially rejective multiple test procedures.* Stat Med 2009;28:586-604。

**核心思想**：每个假设 H_i 是图的一个节点，初始分配权重 w_i（总和=α）。当 H_i 被拒绝后，其 α 传递给未拒绝的假设（按边的权重比例分配）。

```
例：双主要终点 + 单次要终点，α=0.05

    H1 (主要, w=0.5)  ──0.5──>  H2 (主要, w=0.5)
         │  ^                       │  ^
        0.5 0.5                    0.5 0.5
         │  │                       │  │
         v  │                       v  │
         H3 (次要, w=0) <──────────────┘

规则：
  - H1 拒绝 → 其 α(0.05×0.5=0.025) 按 0.5/0.5 传给 H2 和 H3
  - H2 拒绝 → 其 α 同理传递
  - H3 初始无 α（w=0），只能通过 H1/H2 拒绝获得 α
```

**优势**：
1. **直观性**：图形化表达比权重矩阵更易与临床团队沟通
2. **灵活性**：可表达简单 Bonferroni、Holm、固定序列、关口策略等所有经典程序
3. **效能**：α 传递机制使后续假设获得更大检验效能（比固定 Bonferroni 高）
4. **可优化**：可通过算法搜索最优权重配置（参考 gMCP / gMCPLite R 包）

**实施（R）**：

```r
# 使用 gMCP 或 gMCPLite 包实现 Bretz 图形化方法
# install.packages("gMCPLite")
library(gMCPLite)

# 定义权重矩阵 W（W[i,j] = H_i 拒绝后传给 H_j 的比例）
# 定义初始权重向量 weights（各假设的初始 α 分配）
m <- matrix(c(0,   0.5, 0.5,
              0.5, 0,   0.5,
              0,   1,   0), nrow=3, byrow=TRUE)
weights <- c(0.5, 0.5, 0)  # H1=0.5, H2=0.5, H3=0
graph <- new("graphMCP", m=m, weights=weights)

# 输入 p 值，执行图形化检验
pvalues <- c(0.012, 0.041, 0.008)  # H1, H2, H3 的 p 值
result <- gMCP(graph, pvalues, alpha=0.05)
print(result)  # 输出每个假设的拒绝决策
```

**何时使用**（决策）：参见下方"临床研究建议"表的完整场景对照。核心判断：**多层级终点（主要→次要）且需控制 FWER 时，图形化方法优于固定关口策略**。

**与 ch19 关口策略的关系**：关口策略（ch19）是图形化方法的一个特例（固定序列图）。图形化方法是关口策略的泛化，能表达更灵活的 α 传递规则。当临床试验有多层级终点（主要→次要→探索性）且有复杂的优先级关系时，图形化方法优于固定关口策略。

## 关键要点

1. **是否需要调整**：如果检验之间相互独立，且目的是控制 FWER，则需要调整
2. **检验次数越多，调整越严格**，但检验效能也越低
3. "缺乏证据不等于缺乏效果"——非显著结果可能是检验效能不足
4. 调整方法应在研究设计阶段预先规定（在 SAP 中写明）
5. Bonferroni 虽然简单，但在检验数多时过于保守，不推荐作为首选
6. 对于预先指定的主要终点较少时，可不做多重比较调整；对于大量探索性分析推荐 FDR
7. **多层级终点（主要→次要）推荐图形化方法**（Bretz 2009），比固定 Bonferroni 效能更高，比关口策略更灵活

## 局限性

- 多重比较调整降低发现真实效应的检验效能
- Bonferroni 校正 10 次检验时，所需效应量增加约 43%；20 次时增加约 54%
- 过度调整可能导致有临床意义的效果被遗漏

## 临床研究建议

| 场景 | 推荐方法 |
|------|---------|
| 1-2 个主要终点（共同主要） | 不调整或 Gatekeeping |
| 3-10 个预设终点（有优先级） | **图形化方法（Bretz）** 或 Hochberg |
| 大量探索性分析（>10） | FDR（Benjamini-Hochberg） |
| 多层级终点（主要→次要→探索） | **图形化方法（Bretz）**，优于固定 Gatekeeping |
| 期中分析 | O'Brien-Fleming 或 Lan-DeMets |

## 参考文献

1. Cao J, Zhang S. Multiple comparison procedures. 方法学, 2014, 312(5): 543–544.
2. Saitz R, et al. Screening and brief intervention for drug use in primary care. 方法学, 2014, 312(5): 502–513.
3. Hochberg Y. A sharper Bonferroni procedure for multiple tests of significance. Biometrika, 1988, 75(4): 800–802.
4. Dmitrienko A, et al. Gatekeeping procedures in clinical trials. Drug Inf J, 2006, 40: 439–450.
5. Bretz F, Maurer W, Brannath W, Posch M. A graphical approach to sequentially rejective multiple test procedures. Stat Med, 2009, 28(4): 586–604. （图形化方法原始论文）
6. Bretz F, et al. A graphical approach to sequentially rejective multiple test procedures. gMCPLite R 包实现. CRAN. （R 实现，含 group sequential 扩展）

---

*来源：方法学统计与方法指南 第18章*




