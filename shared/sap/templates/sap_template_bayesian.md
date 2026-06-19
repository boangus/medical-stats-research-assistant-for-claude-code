# 统计分析计划（SAP）— 贝叶斯分析

## [{研究标题}]

**版本**：v1.0  
**日期**：2026-06-19  
**状态**：draft  
**研究ID**：[{研究ID}]  
**SAP编制人**：[{姓名}]  
**SAP审核人**：[{姓名}]

---

## 1. 研究设计

### 1.1 贝叶斯框架说明

本研究采用贝叶斯统计推断框架。与频率学派不同，贝叶斯方法将参数视为随机变量，通过先验分布整合已有知识，结合观测数据的似然函数，利用贝叶斯定理得到后验分布：

$$p(\theta \mid \text{data}) = \frac{p(\text{data} \mid \theta) \times p(\theta)}{p(\text{data})}$$

其中：
- $p(\theta)$：先验分布，反映分析前对参数的认知
- $p(\text{data} \mid \theta)$：似然函数，反映数据信息
- $p(\theta \mid \text{data})$：后验分布，为推断基础

### 1.2 设计类型

- **研究类型**：[{RCT / 队列 / 病例对照 / 诊断 / Meta分析}]
- **研究人群**：[{目标人群描述}]
- **干预/暴露**：[{干预组描述}] vs [{对照组描述}]
- **为何选择贝叶斯方法**：[{如：小样本/利用历史数据/灵活建模/直接概率推断/自适应设计}]

### 1.3 贝叶斯方法优势与局限

| 维度 | 优势 | 局限 |
|------|------|------|
| 推断 | 直接给出参数的概率陈述（如"疗效>0的概率为95%"） | 先验选择主观性 |
| 历史 | 可通过先验整合历史数据 | 先验不当可能导致偏倚 |
| 灵活性 | 适用于复杂模型、层次结构 | 计算成本高 |
| 小样本 | 在先验信息丰富时优于频率方法 | 先验影响随样本量减小而增大 |

---

## 2. 研究目的

### 2.1 主要目的

[{主要研究目的，如：评估干预效应的大小及方向，量化效应大于临床有意义阈值的后验概率}]

### 2.2 次要目的

- [{次要目的1，如：评估亚组间效应异质性}]
- [{次要目的2，如：利用历史对照数据提高估计精度}]
- [{次要目的3，如：进行预测概率推断}]

### 2.3 研究假设

- **H0（零假设）**：[{如：治疗效应 δ = 0}]
- **H1（备择假设）**：[{如：治疗效应 δ ≠ 0}]
- **临床有意义阈值**：[{如：δ_min = 0.5（MCID）}]

---

## 3. 先验分布 Specification

> 先验分布的选择是贝叶斯分析的核心，需明确论证每种先验的选择依据。

### 3.1 先验分布汇总表

| 参数 | 先验类型 | 分布 | 超参数 | 选择依据 | 敏感性分析 |
|------|---------|------|--------|---------|-----------|
| [{治疗效应 δ}] | [{无信息/弱信息/信息}] | [{如：Normal(0, 10²)}] | [{均值, 标准差}] | [{依据}] | §8.1 |
| [{基线风险 β₀}] | [{类型}] | [{如：Normal(0, 2.5²)}] | [{超参数}] | [{依据}] | §8.1 |
| [{协变量系数 β₁}] | [{类型}] | [{如：Normal(0, 2.5²)}] | [{超参数}] | [{依据}] | §8.1 |
| [{组间方差 σ²}] | [{类型}] | [{如：Half-Cauchy(0, 5)}] | [{超参数}] | [{依据}] | §8.1 |
| [{随机效应方差 τ²}] | [{类型}] | [{如：Half-Normal(0, 1)}] | [{超参数}] | [{依据}] | §8.1 |

### 3.2 无信息先验（Non-informative Priors）

> 当缺乏可靠的先验信息时使用，让数据主导后验推断。

| 参数 | 分布 | 理由 |
|------|------|------|
| [{δ}] | [{如：Uniform(-∞, ∞) 或 Normal(0, 10⁴)}] | 极度分散，对后验几乎无影响 |
| [{概率 p}] | [{Beta(1, 1) = Uniform(0,1)}] | Jeffreys先验，无信息 |
| [{方差 σ²}] | [{如：1/σ² ~ Gamma(0.001, 0.001)}] | 弱信息共轭先验 |

**注意事项**：
- 无信息先验可能导致后验不可积（improper posterior），需验证后验可积性
- 在高维参数空间中，"无信息"先验可能隐含信息，需谨慎

### 3.3 弱信息先验（Weakly Informative Priors）

> 提供轻度正则化，防止极端估计，但不主导后验。

| 参数 | 分布 | 理由 |
|------|------|------|
| [{δ}] | [{如：Normal(0, 2.5²)（log-OR尺度）}] | 限制效应在合理范围（OR ∈ [0.05, 20]），Gelman推荐 |
| [{σ}] | [{如：Half-Cauchy(0, 5) 或 Half-Normal(0, 5)}] | 允许大值但偏好小值，Gelman推荐 |
| [{β}] | [{如：Normal(0, 2.5²)（log-OR尺度）}] | 限制协变量效应在合理范围 |

### 3.4 信息先验（Informative Priors）

> 基于历史数据或专家知识构建，需详细论证来源和构建方法。

| 参数 | 分布 | 构建方法 | 数据来源 |
|------|------|---------|---------|
| [{δ}] | [{如：Normal(0.3, 0.1²)}] | [{Meta分析历史数据/专家 elicitation}] | [{文献来源/试验名称}] |
| [{基线率}] | [{如：Beta(15, 85)（等效于100例中15事件）}] | [{历史对照数据等效样本量法}] | [{历史试验名称}] |

**信息先验构建方法**：
- **历史数据映射法**：将历史试验结果映射为先验分布（如幂先验法 power prior）
- **专家elicitation**：使用SHELF或MATCH工具进行专家先验 elicitation
- **Meta分析先验**：从系统综述的合并效应量构建先验

**先验-数据一致性检验**：
- 方法：[{如：先验预测检验（prior predictive check）/ Bayes因子比较}]
- 标准：若先验与数据严重冲突（BF < 1/10），需重新评估先验合理性

---

## 4. 模型 Specification

### 4.1 似然函数

| 数据类型 | 似然函数 | 模型表达式 |
|---------|---------|-----------|
| [{连续型结局}] | [{正态分布}] | $y_i \sim \text{Normal}(\mu_i, \sigma^2)$ |
| [{二分类结局}] | [{伯努利/二项分布}] | $y_i \sim \text{Bernoulli}(p_i)$ |
| [{计数结局}] | [{泊松/负二项分布}] | $y_i \sim \text{Poisson}(\lambda_i)$ |
| [{生存结局}] | [{Weibull/指数分布}] | $t_i \sim \text{Weibull}(\alpha, \lambda_i)$ |

### 4.2 链接函数与线性预测器

```
[{如：Logit链接}]
logit(p_i) = β₀ + δ × treatment_i + β₁ × age_i + β₂ × sex_i + ...

[{如：恒等链接（连续结局）}]
μ_i = β₀ + δ × treatment_i + β₁ × covariate_i + ...
```

### 4.3 随机效应结构

> 如适用（多中心、重复测量、层次结构），描述随机效应。

| 随机效应 | 层级 | 分布 | 说明 |
|---------|------|------|------|
| 中心随机截距 | 中心 j | $u_{0j} \sim \text{Normal}(0, \tau^2_{center})$ | [{多中心变异}] |
| 个体随机截距 | 个体 k | $u_{0k} \sim \text{Normal}(0, \tau^2_{subject})$ | [{重复测量相关}] |
| 时间随机斜率 | 个体 k | $u_{1k} \sim \text{Normal}(0, \tau^2_{slope})$ | [{个体变化轨迹}] |

### 4.4 完整模型表达式

```
[{完整模型伪代码/数学表达式}]

示例（二分类结局，多中心）：
  y_ij ~ Bernoulli(p_ij)
  logit(p_ij) = β₀ + δ × treat_ij + Σ β_k × x_kij + u_0j
  u_0j ~ Normal(0, τ²_center)

  Priors:
    δ ~ Normal(0, 2.5²)         # 弱信息先验
    β₀ ~ Normal(0, 5²)          # 弱信息先验
    β_k ~ Normal(0, 2.5²)       # 弱信息先验
    τ_center ~ Half-Cauchy(0, 2) # 弱信息先验
```

---

## 5. MCMC设置

### 5.1 MCMC参数配置

| 参数 | 设定值 | 理由 |
|------|--------|------|
| 采样器 | [{如：NUTS / HMC / Gibbs / JAGS默认}] | [{理由}] |
| 链数（chains） | [{如：4}] | 多链便于收敛诊断 |
| 总迭代次数（iter） | [{如：10000}] | 确保后验充分探索 |
| 预烧期（burn-in/warmup） | [{如：5000}] | 丢弃初始不稳定样本 |
| 稀释（thin） | [{如：1 或 5}] | [{如需降低自相关}] |
| 有效后验样本数 | [{如：≥2000}] | 确保估计精度 |

### 5.2 收敛诊断标准

| 诊断指标 | 标准 | 处理措施（未达标时） |
|---------|------|-------------------|
| **R-hat（Gelman-Rubin）** | < 1.01（所有参数） | 增加迭代次数/重新参数化 |
| **有效样本量（ESS）** | > 400（每个参数） | 增加迭代/调整采样器 |
| **轨迹图（Trace plot）** | 毛毛虫状，无趋势/自相关 | 增加burn-in/重新参数化 |
| **自相关图（ACF）** | 快速衰减至0 | 增加thin |
| **发散转移（Divergences）** | 0（NUTS/HMC） | 调整adapt_delta/重新参数化 |
| **能量图（Energy plot）** | 边际与转移能量分布重叠 | 重新参数化/改进模型 |

### 5.3 采样器调优

```python
# PyMC 示例
import pymc as pm

with model:
    trace = pm.sample(
        draws=5000,
        tune=5000,
        chains=4,
        cores=4,
        target_accept=0.95,   # 提高以减少发散
        max_treedepth=12,
        random_seed=42,
        return_inferencedata=True
    )
```

```r
# Stan (rstan) 示例
fit <- sampling(
  stan_model,
  data = stan_data,
  iter = 10000,
  warmup = 5000,
  chains = 4,
  cores = 4,
  control = list(adapt_delta = 0.95, max_treedepth = 12),
  seed = 42
)
```

---

## 6. 假设检验

### 6.1 贝叶斯因子（Bayes Factor）

> 贝叶斯因子 BF₁₀ 衡量数据对 H1 相对于 H0 的支持程度。

| BF₁₀ | 解释 |
|-------|------|
| > 100 | 极强支持 H1 |
| 30-100 | 很强支持 H1 |
| 10-30 | 强支持 H1 |
| 3-10 | 中等支持 H1 |
| 1-3 | 弱支持 H1 |
| 1 | 无差异 |
| 1/3-1 | 弱支持 H0 |
| 1/3-1/10 | 中等支持 H0 |
| < 1/100 | 极强支持 H0 |

**计算方法**：[{如：bridge sampling / Savage-Dickey密度比 / 调和均值估计}]

### 6.2 后验概率（Posterior Probability）

> 直接计算参数满足特定条件的后验概率。

| 假设 | 后验概率表达式 | 报告方式 |
|------|--------------|---------|
| H1: δ > 0 | $P(\delta > 0 \mid \text{data})$ | "治疗有效（δ>0）的后验概率为 [{X}%]" |
| H1: δ > δ_min | $P(\delta > \delta_{min} \mid \text{data})$ | "效应超过MCID的后验概率为 [{X}%]" |
| H1: |δ| < ε | $P(\|\delta\| < \varepsilon \mid \text{data})$ | "效应在等效区间内的后验概率为 [{X}%]" |

**决策阈值**：
- $P(\delta > 0) > 0.95$：强证据支持有效
- $P(\delta > \delta_{min}) > 0.95$：强证据支持临床有意义
- $P(|\delta| < \varepsilon) > 0.95$：强证据支持等效

### 6.3 ROPE区域（Region of Practical Equivalence）

> 定义实践等效区域，评估参数落入该区域的后验概率。

| 参数 | ROPE定义 | 依据 |
|------|---------|------|
| [{δ}] | [{如：(-0.1, 0.1)（标准化效应量）}] | [{MCID的1/5 / 临床判断}] |
| [{OR}] | [{如：(0.9, 1.1)}] | [{临床等效范围}] |

**ROPE决策规则**：
- 后验落入ROPE的概率 > 95%：接受等效（H0）
- 后验完全在ROPE外（100%在ROPE外）：拒绝等效（接受H1）
- 其他情况：不确定，需更多数据

---

## 7. 模型比较

### 7.1 信息准则

| 指标 | 公式/方法 | 解释 | 偏好 |
|------|---------|------|------|
| **WAIC** | $-2(\text{lpd} - p_{waic})$ | Watanabe-Akaike信息准则，考虑后验不确定性 | 值越小越好 |
| **LOO-CV** | Pareto平滑重要性采样留一交叉验证 | 近似留一交叉验证对数预测密度 | 值越小越好 |
| **DIC** | $-2\bar{D} + p_D$ | Deviance信息准则（较老方法） | 值越小越好 |

### 7.2 模型比较表

| 模型 | WAIC | WAIC SE | LOO-CV | LOO SE | p_WAIC | 选择 |
|------|------|---------|--------|--------|--------|------|
| 模型A（[{描述}]） | [{值}] | [{SE}] | [{值}] | [{SE}] | [{值}] | [{是/否}] |
| 模型B（[{描述}]） | [{值}] | [{SE}] | [{值}] | [{SE}] | [{值}] | [{是/否}] |
| 模型C（[{描述}]） | [{值}] | [{SE}] | [{值}] | [{SE}] | [{值}] | [{是/否}] |

**比较标准**：
- ΔWAIC > 10：强证据偏好较小值模型
- ΔWAIC 2-10：中等证据
- ΔWAIC < 2：模型无显著差异，选更简单模型

### 7.3 后验预测检验（Posterior Predictive Check）

> 评估模型生成数据与观测数据的吻合程度。

| 检验内容 | 统计量/图形 | 方法 | 通过标准 |
|---------|-----------|------|---------|
| 分布拟合 | [{如：直方图叠加}] | 从后验模拟新数据，与观测比较 | 模拟分布覆盖观测分布 |
| 汇总统计 | [{如：均值/方差/偏度}] | Bayesian p-value | 0.05 < p < 0.95 |
| 分位数 | [{如：Q-Q图}] | 后验预测分位数 vs 观测分位数 | 点落在对角线附近 |
| 组间差异 | [{如：组均值差}] | 模拟组间差异 vs 观测差异 | Bayesian p-value接近0.5 |

```python
# PyMC 后验预测检验示例
import pymc as pm

with model:
    ppc = pm.sample_posterior_predictive(trace, var_names=["y_obs"])
    # Bayesian p-value
    bayes_p = (ppc["y_obs"].mean(axis=1) >= data["y"].mean()).mean()
```

---

## 8. 敏感性分析

### 8.1 先验敏感性分析

> 评估不同先验选择对后验推断的影响。

| 场景 | 先验设定 | 目的 | 比较指标 |
|------|---------|------|---------|
| 主分析 | [{主先验，如：弱信息}] | 基准 | — |
| S1-无信息 | [{如：Normal(0, 100²)}] | 评估先验影响 | 后验均值/95%CI变化 |
| S2-怀疑先验 | [{如：Normal(0, 0.5²)（偏向无效）}] | 保守评估 | P(δ>0)变化 |
| S3-乐观先验 | [{如：Normal(0.5, 0.3²)（偏向有效）}] | 乐观评估 | P(δ>0)变化 |
| S4-信息先验 | [{如：基于历史数据}] | 历史数据影响 | 后验均值/CI变化 |

**稳健性判定**：
- 若不同先验下结论方向一致（P(δ>0)均>0.95或均<0.05）：结论稳健
- 若结论随先验改变：需报告先验依赖性，讨论最合理先验

### 8.2 模型敏感性分析

| 场景 | 模型变化 | 目的 |
|------|---------|------|
| M1-不同似然 | [{如：Probit vs Logit}] | 链接函数影响 |
| M2-随机效应 | [{含/不含随机效应}] | 层次结构影响 |
| M3-协变量 | [{全调整/部分调整/不调整}] | 混杂控制影响 |
| M4-异常值 | [{含/不含异常值}] | 异常值影响 |
| M5-缺失数据 | [{完整病例/多重插补}] | 缺失机制影响 |

---

## 9. 与频率学派结果的对比报告

> 为增强结果可信度和可解读性，同时报告贝叶斯和频率学派结果。

| 指标 | 贝叶斯结果 | 频率结果 | 一致性评估 |
|------|-----------|---------|-----------|
| 效应量（δ） | 后验均值 [{值}]，95% HPD [{CI}] | 点估计 [{值}]，95% CI [{CI}] | [{一致/不一致}] |
| 假设检验 | P(δ>0) = [{X}%]，BF₁₀ = [{值}] | p = [{值}] | [{一致/不一致}] |
| AUC/效应量 | 后验均值 [{值}] | 点估计 [{值}] | [{一致/不一致}] |

**对比要点**：
- 后验95% HPD区间与频率95% CI的比较（通常在弱信息先验下接近）
- 贝叶斯概率陈述与频率p值的对应关系
- 先验信息对结论的影响程度
- 两种方法结论不一致时的讨论

---

## 10. 图表计划

### 10.1 Tables

| 编号 | 内容 | 说明 |
|------|------|------|
| Table 1 | 基线特征 | 按组分组 |
| Table 2 | 先验分布汇总 | 所有参数的先验设定 |
| Table 3 | 后验汇总 | 后验均值、中位数、SD、95% HPD |
| Table 4 | 假设检验结果 | 后验概率、BF、ROPE |
| Table 5 | 模型比较 | WAIC、LOO-CV |
| Table 6 | 敏感性分析 | 不同先验/模型下的结果 |
| Table 7 | 贝叶斯vs频率对比 | 两种方法结果并排 |

### 10.2 Figures

| 编号 | 内容 | 格式 | 说明 |
|------|------|------|------|
| Figure 1 | 先验/后验分布图 | PDF | 各参数先验分布（虚线）与后验分布（实线）叠加，直观展示数据对先验的更新 |
| Figure 2 | Trace plot | PDF | 各参数4条链的轨迹图，展示收敛性 |
| Figure 3 | 后验密度图 | PDF | 主要效应参数的后验密度图，标注95% HPD和ROPE区域 |
| Figure 4 | 森林图 | PDF | 各参数/亚组后验均值及95% HPD的森林图 |
| Figure 5 | 后验预测检验图 | PDF | 观测数据 vs 后验预测分布叠加图 |
| Figure 6 | 自相关图 | PDF | 各参数MCMC样本的自相关函数图 |
| Figure 7 | ROPE图 | PDF | 后验分布与ROPE区域的可视化 |

### 10.3 图表技术规范

- **先验/后验图**：先验用半透明虚线，后验用实线填充；标注后验均值和95% HPD
- **Trace plot**：每条链不同颜色，展示混合良好（毛毛虫状）
- **森林图**：点为后验中位数，线为95% HPD，垂直参考线在0（无效）
- **ROPE图**：后验密度图上以不同底色标注ROPE区域
- **格式**：矢量图（PDF/SVG），色盲友好配色

---

## 11. 软件环境

### 11.1 主分析软件

| 软件 | 版本 | 用途 |
|------|------|------|
| [{PyMC / Stan / JAGS}] | [{版本号}] | [{MCMC采样/后验推断}] |

### 11.2 PyMC环境（如选用）

- **Python版本**：[{如 3.12}]

| 包名 | 用途 | 版本 |
|------|------|------|
| pymc | 贝叶斯建模、NUTS采样 | [{版本}] |
| arviz | 后验诊断、trace plot、WAIC/LOO | [{版本}] |
| numpyro | JAX后端加速采样 | [{版本}] |
| bambi | 高级模型公式接口 | [{版本}] |
| scipy | 统计分布 | [{版本}] |
| numpy | 数值计算 | [{版本}] |
| pandas | 数据处理 | [{版本}] |
| matplotlib | 绘图 | [{版本}] |

```python
# PyMC 环境验证
import pymc as pm; print(f"PyMC {pm.__version__}")
import arviz as az; print(f"ArviZ {az.__version__}")
```

### 11.3 Stan环境（如选用）

- **接口**：[{rstan / CmdStanR / CmdStanPy / pystan}]

| 包名 | 用途 | 版本 |
|------|------|------|
| rstan / cmdstanr | R接口 | [{版本}] |
| Stan | C++后端 | [{版本}] |
| bayesplot | 贝叶斯绘图 | [{版本}] |
| loo | WAIC/LOO-CV | [{版本}] |
| bridgesampling | 贝叶斯因子 | [{版本}] |
| shinystan | 交互式诊断 | [{版本}] |

```r
# R/Stan 环境验证
library(rstan); packageVersion("rstan")
library(bayesplot); packageVersion("bayesplot")
library(loo); packageVersion("loo")
rstan_options(auto_write = TRUE)
options(mc.cores = parallel::detectCores())
```

### 11.4 JAGS环境（如选用）

| 包名 | 用途 | 版本 |
|------|------|------|
| rjags / runjags | R接口 | [{版本}] |
| JAGS | Gibbs采样后端 | [{版本}] |
| coda | MCMC诊断 | [{版本}] |
| mcmcplots | MCMC绘图 | [{版本}] |

### 11.5 可重复性

- **随机种子**：[{如 seed = 42}]
- **代码版本控制**：[{Git仓库/commit hash}]
- **计算环境**：[{Docker镜像/renv.lock/requirements.txt}]
- **运行时间**：[{预计MCMC运行时间}]
- **并行设置**：[{如 4 cores, 4 chains}]

---

## 12. 修改记录

| 版本 | 日期 | 修改内容 | 修改人 |
|------|------|----------|--------|
| v1.0 | 2026-06-19 | 初始版本 | [{姓名}] |

---

## 附录A：贝叶斯分析报告清单

> 参照 FDA Bayesian Guidance 及 GAMABIAS 报告规范。

| 条目 | 内容 | 状态 |
|------|------|------|
| 先验分布明确说明 | 所有参数先验分布及超参数 | [ ] |
| 先验选择论证 | 无信息/弱信息/信息先验的选择理由 | [ ] |
| MCMC设置 | 链数、迭代、burn-in、thin | [ ] |
| 收敛诊断 | R-hat, ESS, trace plot, divergences | [ ] |
| 后验汇总 | 均值、中位数、SD、95% HPD/CI | [ ] |
| 假设检验 | 后验概率、BF、ROPE | [ ] |
| 模型比较 | WAIC/LOO-CV | [ ] |
| 后验预测检验 | PPC图及Bayesian p-value | [ ] |
| 敏感性分析 | 先验敏感性 + 模型敏感性 | [ ] |
| 频率对比 | 与频率方法结果对比 | [ ] |
| 代码可重复 | 代码+种子+环境 | [ ] |

---

## 附录B：模型代码模板

### B.1 PyMC 模板

```python
import pymc as pm
import arviz as az
import numpy as np

# 数据准备
# y = np.array([...])      # 结局变量
# treat = np.array([...])   # 处理分组 (0/1)
# age = np.array([...])     # 协变量

with pm.Model() as model:
    # 先验
    beta_0 = pm.Normal("beta_0", mu=0, sigma=5)
    delta = pm.Normal("delta", mu=0, sigma=2.5)       # 治疗效应
    beta_age = pm.Normal("beta_age", mu=0, sigma=2.5)
    
    # 线性预测器
    logit_p = beta_0 + delta * treat + beta_age * age
    
    # 似然
    p = pm.math.invlogit(logit_p)
    y_obs = pm.Bernoulli("y_obs", p=p, observed=y)
    
    # 采样
    trace = pm.sample(
        draws=5000, tune=5000, chains=4, cores=4,
        target_accept=0.95, random_seed=42,
        return_inferencedata=True
    )

# 收敛诊断
print(az.rhat(trace))
print(az.ess(trace))
az.plot_trace(trace)

# 后验汇总
summary = az.summary(trace, hdi_prob=0.95)
print(summary)

# 后验概率
delta_samples = trace.posterior["delta"].values.flatten()
p_positive = (delta_samples > 0).mean()
p_mcid = (delta_samples > 0.5).mean()  # MCID=0.5
print(f"P(delta > 0) = {p_positive:.4f}")
print(f"P(delta > MCID) = {p_mcid:.4f}")

# ROPE
rope = (-0.1, 0.1)
p_rope = ((delta_samples > rope[0]) & (delta_samples < rope[1])).mean()
print(f"P(delta in ROPE) = {p_rope:.4f}")
```

### B.2 Stan 模板

```stan
// model.stan
data {
  int<lower=0> N;              // 样本量
  array[N] int<lower=0,upper=1> y;  // 结局
  vector[N] treat;             // 处理
  vector[N] age;               // 协变量
}
parameters {
  real beta_0;
  real delta;
  real beta_age;
}
model {
  // 先验
  beta_0 ~ normal(0, 5);
  delta ~ normal(0, 2.5);
  beta_age ~ normal(0, 2.5);
  
  // 似然
  y ~ bernoulli_logit(beta_0 + delta * treat + beta_age * age);
}
generated quantities {
  // 后验预测
  array[N] int y_rep;
  for (i in 1:N)
    y_rep[i] = bernoulli_logit_rng(beta_0 + delta * treat[i] + beta_age * age[i]);
}
```

```r
# R 调用
library(rstan)
fit <- stan("model.stan", data = stan_data,
            iter = 10000, warmup = 5000, chains = 4, seed = 42)
print(fit, probs = c(0.025, 0.5, 0.975))
```

---

*参考标准：ICH E9(R1) Estimands; FDA Guidance on Bayesian Statistics (2010); Gelman et al. Bayesian Data Analysis (BDA3); Spiegelhalter et al. (2004); Kruschke (2014) Doing Bayesian Data Analysis; Vehtari et al. (2021) LOO-CV; Wagenmakers et al. (2018) Bayes Factor*
