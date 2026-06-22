# 网络 Meta 分析 (Network Meta-Analysis, NMA)

> 版本: 1.0 | 2026-06-13
> MSRA 关联: `analysis-plan` Phase 3 方法选择, `analysis-exec` Phase 7 证据合成

---

## 概述

网络 Meta 分析 (Network Meta-Analysis, NMA)，又称混合治疗比较 (Mixed Treatment Comparison, MTC)，允许在**同一分析框架**内同时比较多种干预措施，包括那些**从未在头对头试验中直接比较**的干预。

### NMA vs 传统 Meta 分析

| 特征 | 传统配对 Meta 分析 | 网络 Meta 分析 |
|------|------------------|---------------|
| 比较范围 | 仅直接比较 (A vs B) | 直接 + 间接比较 (A vs B, A vs C, B vs C) |
| 干预排序 | 无法排序 | 可提供干预排序 (SUCRA, P-score) |
| 假设 | 同质性 | 同质性 + 一致性 (consistency) |
| 效率 | 较低 | 更高（借力间接证据） |

---

## 一、间接比较原理

### 1.1 间接比较的传递性

当 A vs B 和 A vs C 的试验均存在，但缺少 B vs C 的直接证据时：

$$\hat{\beta}_{BC}^{indirect} = \hat{\beta}_{AC} - \hat{\beta}_{AB}$$

**传递性假设**: A 在 A vs B 试验中的效应与在 A vs C 试验中的效应相同。这要求两项试验中 A 的定义、剂量、患者特征可比。

### 1.2 网络几何 (Network Geometry)

使用 `netmeta` 的网络图可视化：

- **节点 (Node)**: 各干预措施
- **边 (Edge)**: 直接比较的试验连接
- **边粗细**: 直接比较的试验数/总样本量
- **封闭环**: 存在直接+间接证据 → 可检验一致性

```r
library(netmeta)

# 绘制网络图
netgraph(net1, thickness = "number.of.studies", cex = 1.2)
```

---

## 二、一致性假设

### 2.1 一致性 vs 不一致性

**一致性 (Consistency)**: 直接比较和间接比较的效应估计一致。

$$\omega = \hat{\beta}_{BC}^{direct} - \hat{\beta}_{BC}^{indirect}$$

$\omega = 0$ 表示一致性成立。

### 2.2 不一致性检验

| 方法 | 原理 | 适用场景 |
|------|------|---------|
| **Design-by-Treatment** | 检验不同试验设计间效应差异 | 通用方法，推荐首选 |
| **节点分裂 (Node-Splitting)** | 分离某节点的直接与间接证据 | 逐节点检验 |
| **回环特定一致性 (Loop-Specific)** | 封闭环内检验 | 仅适用于存在封闭环的情况 |

### 2.3 R 实现

```r
# Design-by-Treatment 检验
decomp <- decomp.design(net1)
print(decomp)

# 节点分裂
ns <- netsplit(net1)
print(ns)

# 不一致性可视化
forest(ns, show = "both",orderby = "tau2")
```

---

## 三、频率学方法 (Frequentist NMA)

### 3.1 模型框架

NMA 的一般线性模型:

$$Y_{ik} = \mu_i + d_{A_i B_k} + \epsilon_{ik}$$

其中:
- $\mu_i$ = 试验 i 的基线效应
- $d_{AB}$ = A vs B 的相对治疗效应
- $\epsilon_{ik} \sim N(0, \sigma^2_{ik})$

**随机效应模型**: 在固定效应基础上加入试验间异质性 $\tau^2$。

### 3.2 netmeta 包

```r
library(netmeta)

# 数据格式: TE, seTE, treat1, treat2, studlab
nma_res <- netmeta(
  TE = TE,
  seTE = seTE,
  treat1 = treat1,
  treat2 = treat2,
  studlab = studlab,
  data = df,
  sm = "OR",           # 效应量: OR, RR, RD, SMD, HR, MD
  common = TRUE,        # 固定效应
  random = TRUE,        # 随机效应
  reference = "Placebo" # 参照组
)

summary(nma_res)
```

### 3.3 P-score 排序

P-score (Rücker & Schwarzer, 2015) 是频率学框架下的干预排序指标：

$$P_{score}(A) = \frac{\sum_{B \neq A} \Phi\left(\frac{\hat{d}_{AB}}{\sqrt{\text{Var}(\hat{d}_{AB})}}\right)}{n_t - 1}$$

- 范围: [0, 1]
- P-score = 1 表示该干预"确定最优"

```r
# P-score 排序
ranking <- rankogram(nma_res)
print(ranking)

# netrank 函数
netrank(nma_res, small.values = "good")  # "good" for small values preferred
```

---

## 四、贝叶斯方法 (Bayesian NMA)

### 4.1 模型框架

贝叶斯 NMA 使用马尔可夫链蒙特卡罗 (MCMC) 方法：

$$\hat{d}_{AB} | \mu_i, d, \tau^2 \sim N(d_{A_i B_k}, \sigma^2_i + \tau^2)$$

**先验选择**:
- 异质性参数 $\tau$: 建议使用弱信息先验，如 $\tau \sim \text{Uniform}(0, 5)$ 或 $\tau \sim \text{Half-Normal}(0, 1)$
- 注意: 均匀先验在某些情况下可能导致 MCMC 不收敛

### 4.2 SUCRA 排序

SUCRA (Surface Under the Cumulative Ranking curve) 是贝叶斯框架下的排序指标：

$$\text{SUCRA}(A) = \frac{\sum_{b=1}^{n_t-1} \text{cum}_{b}}{n_t - 1}$$

- 范围: [0, 1]
- SUCRA 越高，该干预越好

### 4.3 gemtc 包

```r
library(gemtc)

# 创建网络
network <- mtc.network(
  data.ab = df,
  treatments = treatments_df
)

# 拟合模型
model <- mtc.model(
  network,
  type = "consistency",
  likelihood = "binom",   # 二分类: binom; 连续: normal
  link = "logit",         # logit, log, cloglog
  linearModel = "random", # random or fixed
  n.chain = 4
)

# MCMC 采样
results <- mtc.run(model, n.adapt = 5000, n.iter = 20000, thin = 10)

# SUCRA 排序
rank <- rank.probability(results)
sucra <- sucra(rank)
plot(sucra)

# League table
relative.effects.table(results)
```

---

## 五、联赛表 (League Table)

联赛表是 NMA 结果呈现的核心，以矩阵形式展示所有干预两两比较的效应估计。

```
         A           B           C           D
A        --          0.23        -0.15       0.41
                     (0.05,0.41) (-0.38,0.08) (0.18,0.64)
B        -0.23       --          -0.38       0.18
         (-0.41,-0.05)           (-0.58,-0.18) (-0.02,0.38)
C        0.15        0.38        --          0.56
         (-0.08,0.38) (0.18,0.58)            (0.32,0.80)
D        -0.41       -0.18       -0.56       --
         (-0.64,-0.18) (-0.38,0.02) (-0.80,-0.32)
```

**解读**: 行干预 vs 列干预。正值表示行干预优于列干预（当效应方向为"越大越好"时）。

```r
# netmeta 联赛表
league_table <- netleague(nma_res, digits = 2, ci = TRUE)
print(league_table)

# gemtc 联赛表
league <- relative.effects.table(results)
```

---

## 六、NMA 中的亚组分析与 Meta 回归

### 6.1 网络 Meta 回归

在 NMA 中加入协变量以探索效应修饰因素：

$$d_{AB,i} = d_{AB} + \beta_{AB} (x_i - \bar{x})$$

```r
# netmeta: meta 回归
nma_reg <- netmeta(
  TE = TE, seTE = seTE,
  treat1 = treat1, treat2 = treat2,
  studlab = studlab,
  data = df,
  sm = "OR",
  covariate = age_mean  # 协变量
)

# gemtc: meta 回归
model_reg <- mtc.model(network, regressor = list(
  variable = "age_mean",
  coefficient = "shared",  # 共享回归系数
  control = "Placebo"
))
```

### 6.2 注意事项

| 问题 | 说明 |
|------|------|
| 生态学偏倚 | 研究水平的协变量 ≠ 个体水平效应修饰 |
| 统计功效 | Meta 回归需要大量研究（≥10） |
| 比较性假设 | 假设协变量在所有比较中效应修饰一致 |
| 稀疏网络 | 间接证据稀少时回归系数不稳定 |

---

## 七、敏感性分析

| 分析类型 | 目的 | 方法 |
|----------|------|------|
| 异质性敏感性 | 评估 $\tau^2$ 对结论影响 | 比较固定/随机效应模型 |
| 偏倚调整 | 评估发表偏倚/研究质量 | 使用比较校正模型 (comparison-adjusted funnel plot) |
| 一致性敏感性 | 剔除异常研究后一致性变化 | 逐一剔除研究 |
| 先验敏感性 (贝叶斯) | 评估先验对后验影响 | 更换 $\tau$ 先验 |
| 网络结构 | 剔除低质量研究后网络连通性 | 检查网络图变化 |

```r
# 比较校正漏斗图
funnel(nma_res, order = TRUE)

# 逐一剔除研究
netsens <- netimpact(net1)
forest(netsens)
```

---

## 八、常见陷阱

| 陷阱 | 说明 | 解决方案 |
|------|------|---------|
| 传递性违反 | 不同试验中患者特征/干预定义不可比 | 检查试验特征一致性，限制人群 |
| 不一致性未检验 | 直接与间接证据冲突 | 报告 Design-by-Treatment 检验 |
| 网络稀疏 | 间接证据薄弱 | 报告直接/间接证据贡献比例 |
| 排序误用 | 仅看 SUCRA/P-score 最高即下结论 | 结合效应大小、置信区间、证据质量 |
| 异质性忽略 | 不同试验间 $\tau^2$ 过大 | 报告 $I^2$、预测区间 |
| 小样本效应 | 小样本试验可能夸大效应 | 使用比较校正漏斗图、调节模型 |
| 多重比较膨胀 | 多干预比较增加 I 类错误 | 报告校正后置信区间或使用最小充分统 |

---

## 九、报告模板 (PRISMA-NMA 扩展)

> 本研究遵循 PRISMA 网络 Meta 分析扩展报告规范。系统检索 {数据库}，纳入 {N} 项 RCT 比较 {干预列表} 对 {结局} 的影响。采用 {频率学/贝叶斯} 网络 Meta 分析，使用 {netmeta/gemtc} 包。效应量为 {OR/RR/MD/HR}，随机效应模型，异质性参数 $\tau^2$ = {值}。网络连通性: {N} 个节点，{E} 条边，{L} 个封闭环。一致性通过 Design-by-Treatment 检验评估 (p = {值})。干预排序采用 {SUCRA/P-score}。联赛表呈现所有两两比较的效应估计及 95% {可信/置信} 区间。敏感性分析包括 {偏倚调整/逐一剔除/先验敏感性}。证据质量采用 {GRADE} 评估。分析使用 R {版本}。

---

## 十、参考资源

- **核心文献**: Salanti G. Indirect and mixed-treatment comparison, network, or multiple-treatments meta-analysis: many names, many benefits, many concerns for the next generation evidence synthesis tool. *Res Synth Methods*, 2012, 3(2): 80-97.
- **PRISMA-NMA**: Hutton B, Salanti G, Caldwell DM, et al. The PRISMA extension statement for reporting of systematic reviews incorporating network meta-analyses of health care interventions. *Ann Intern Med*, 2015, 162(2): 126-132.
- **排名方法**: Rücker G, Schwarzer G. Ranking treatments in frequentist network meta-analysis works without resampling methods. *BMC Med Res Methodol*, 2015, 15: 58.
- **R 包**: `netmeta` (频率学 NMA), `gemtc` (贝叶斯 NMA), `meta` (配对 Meta 分析), `rjags`/`R2WinBUGS` (MCMC 引擎)
- **在线工具**: CINeMA (Confidence in Network Meta-Analysis, cinema.ispm.ch)
- **MSRA 模板**: `shared/templates/nma_analysis_template.R`
