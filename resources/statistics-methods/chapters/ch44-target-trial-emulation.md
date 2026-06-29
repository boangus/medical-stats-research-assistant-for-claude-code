# 目标试验模拟 (Target Trial Emulation, TTE)

> 版本: 1.0 | 2026-06-13
> MSRA 关联: `analysis-plan` Phase 3 方法选择, `analysis-exec` Phase 7 因果推断

---

## 概述

目标试验模拟 (Target Trial Emulation, TTE) 是将**观察性数据**按照假设的目标随机试验 (target trial) 进行分析的框架，由 Hernán & Robins (2016) 系统提出。核心思想：在分析观察性数据前，先明确"如果我们要设计一个随机试验来回答这个问题，试验会是什么样？"，然后用因果推断方法模拟该试验。

### 何时使用 TTE

| 场景 | 说明 |
|------|------|
| 无法开展 RCT | 伦理限制（如吸烟与肺癌）、可行性不足 |
| 需要补充 RCT 证据 | RCT 外推性不足、长期结局缺乏 |
| 利用注册登记数据 | 医保数据库、电子病历、疾病登记系统 |
| 已有治疗的真实效果 | 即 effectiveness（而非 efficacy） |

**TTE 不适用于**: 暴露不可干预（如基因、性别）或缺乏合适数据源的情况。

---

## 一、目标试验的要素规范

实施 TTE 的第一步是完整定义目标试验的**协议要素**：

| 要素 | 说明 | 示例 |
|------|------|------|
| **研究人群 (Eligibility)** | 纳入/排除标准 | 年龄≥18岁、确诊2型糖尿病 |
| **治疗策略 (Treatment Strategies)** | 比较的干预 | 手术 vs 药物保守治疗 |
| **时间零点 (Time Zero)** | 随机化/入组时间点 | 首次诊断日期、首次处方日期 |
| **随访期 (Follow-up)** | 起止时间 | 从时间零点到事件/删失 |
| **结局 (Outcome)** | 主要终点 | 全因死亡、MACE |
| **因果对比 (Causal Contrast)** | ITT 效应 vs PP 效应 | 见下文 |

### 因果对比选择

| 对比 | 含义 | 适用场景 |
|------|------|---------|
| **意向治疗效应 (ITT-like)** | 按初始治疗策略分析，不考虑依从性 | 类比 RCT 的 ITT |
| **按方案效应 (PP-like)** | 仅分析持续遵循初始方案的个体 | 类比 RCT 的 per-protocol |
| **即刻启动效应** | 比较"立即开始治疗" vs "从不开始" | 开始治疗的时间差异有意义 |

---

## 二、克隆-删失-加权法 (Clone-Censor-Weight, CCW)

### 2.1 基本原理

CCW 是模拟 PP 效应最常用的方法，分三步：

1. **克隆 (Clone)**: 为每个个体创建两个"克隆体"，分别分配到两个治疗策略
2. **删失 (Censor)**: 当克隆体偏离其分配的策略时，将其删失
3. **加权 (Weight)**: 用逆概率权重 (IPCW) 校正信息性删失

### 2.2 权重计算

使用逆概率删失权重 (Inverse Probability of Censoring Weights, IPCW):

$$w_i(t) = \prod_{k=1}^{t} \frac{1}{P(C_i = 0 | C_i \geq k, \bar{L}_k, A_i)}$$

其中:
- $C_i$ = 删失指示变量
- $\bar{L}_k$ = 截至时间 k 的时变协变量历史
- $A_i$ = 治疗策略

**权重稳定化**: 使用边际概率替代条件概率的分母，避免极端权重。

### 2.3 R 实现

```r
library(TrialEmulation)

# 定义目标试验
trial_spec <- trial_specification(
  estimand_type = "PP",          # per-protocol
  outcome_type = "survival",
  censor_if_switch = TRUE,       # 偏离策略时删失
  clone = TRUE,                  # 克隆策略
  switch_hazard_model = treatment ~ age + sex + comorbidity
)

# IPW 权重
w <- weight_calculate(
  trial_spec,
  numerator = ~ age + sex,
  denominator = ~ age + sex + comorbidity + prior_treatment,
  stabilize = TRUE
)
```

---

## 三、g-计算 (G-computation)

### 3.1 原理

g-computation 是参数化 g-formula 的实现，通过模拟反事实结局估计因果效应：

1. 拟合结局模型: $E[Y | A, \bar{L}]$
2. 对每个个体，分别代入两种治疗策略
3. 计算反事实结局的边际均值之差

### 3.2 g-formula vs IPW

| 特征 | g-computation | IPW (CCW) |
|------|---------------|-----------|
| 模型依赖 | 结局模型 | 治疗/删失模型 |
| 正则性条件 | 需正确指定结局模型 | 需正确指定治疗模型 |
| 效率 | 通常更高 | 依赖权重稳定性 |
| 实现复杂度 | 较高（需模拟） | 较低 |
| 时变混杂 | 处理良好 | 处理良好 |

### 3.3 R 实现

```r
library(gfoRmula)

gform <- gformula_survival(
  obs_data = df,
  id = "patient_id",
  time_name = "visit",
  outcome_name = "death",
  covnames = c("bp", "cholesterol", "egfr"),
  covtypes = c("normal", "normal", "normal"),
  histories = c(lagged),
  basecovs = c("age", "sex"),
  treatment_name = "treatment",
  intvars = list("treatment"),
  intvals = list(list(1)),  # 干预: 所有人接受治疗
  nsimul = 10000
)
```

---

## 四、逆概率删失加权 (IPCW) 要点

### 4.1 权重诊断

| 指标 | 可接受范围 | 操作 |
|------|-----------|------|
| 最大权重 | < 100 | 超出需截断或检查模型 |
| 权重均值 | 接近 1.0 (稳定化后) | 偏离提示模型问题 |
| 标准化权重分布 | 近似对称 | 右偏提示极端权重 |
| ESS (有效样本量) | > 原始样本的 50% | 过低提示权重不稳定 |

### 4.2 截断策略

```r
# 无截断
weights_raw <- ipcw$weights

# 百分位截断 (推荐第 99 百分位)
weights_trunc <- pmin(weights_raw, quantile(weights_raw, 0.99))

# 分子截断 (同时截断分子分母)
weights_marginal <- pmin(ipcw$numerator / ipcw$denominator, 10)
```

---

## 五、时间零点与永恒时间偏倚

### 5.1 常见时间零点定义

| 策略 | 说明 | 偏倚风险 |
|------|------|---------|
| 首次诊断 | 以疾病确诊为入组点 | 低（理想） |
| 首次处方 | 以首次用药为入组点 | 存在 immortal time bias 风险 |
| 新用户设计 | 纳入新开始治疗者 | 消除 prevalent user bias |

### 5.2 永恒时间偏倚 (Immortal Time Bias)

当随访开始时间与治疗开始时间不一致时，未接受治疗期间的"永恒时间"被错误归入治疗组，导致疗效被高估。

**解决方法**: 使用 time-zero alignment 或 landmark analysis。

---

## 六、敏感性分析

| 分析类型 | 目的 | 方法 |
|----------|------|------|
| **权重敏感性** | 检查权重截断影响 | 比较不同截断阈值 |
| **未测量混杂** | 评估 E-value | VanderWeele & Ding 方法 |
| **模型规范** | 检查结局/治疗模型 | 改变函数形式、变量集 |
| **删失假设** | 评估 informative censoring | tipping point analysis |
| **时间零点** | 检查入组定义 | landmark analysis 替代 |

---

## 七、常见陷阱

| 陷阱 | 说明 | 解决方案 |
|------|------|---------|
| 未明确目标试验 | 直接用观察性数据做比较 | 先写出完整试验方案 |
| 时间零点模糊 | 混淆 prevalent vs incident users | 使用新用户设计 |
| 权重极端不稳定 | 治疗预测模型 misspecified | 检查 covariate balance，简化模型 |
| 忽略 positivity 违反 | 某些亚组仅接受一种治疗 | 检查 positivity，限制人群 |
| 永恒时间偏倚 | 治疗开始前的时间归入治疗组 | time-zero alignment |
| 过度依赖单一方法 | 仅报告一种估计 | 同时报告 g-comp 和 IPW |

---

## 八、报告模板

> 本研究采用目标试验模拟框架 (Hernán & Robins, 2016) 利用 {数据来源} 评估 {治疗策略 A} vs {治疗策略 B} 对 {结局} 的因果效应。目标试验定义如下: 人群为 {纳入标准}，时间零点为 {定义}，随访至 {终止条件}。采用克隆-删失-加权法模拟 {ITT/PP} 效应，使用逆概率删失权重（分子模型: {变量}，分母模型: {变量}），权重经第 {99} 百分位截断。结局采用 {Cox 比例风险/参数生存} 模型估计，校正 {基线协变量}。敏感性分析包括 {权重截断敏感性/未测量混杂 E-value/tipping point}。所有分析使用 R {版本}，`TrialEmulation` 包。

---

## 九、参考资源

- **核心文献**: Hernán MA, Robins JM. Using big data to emulate a target trial when a randomized trial is not available. *Am J Epidemiol*, 2016, 183(8): 758-764.
- **综述**: Hernán MA, Robins JM. *Causal Inference: What If*. Chapman & Hall/CRC, 2020. (Chapter 18-22)
- **R 包**: `TrialEmulation` (CRAN), `gfoRmula` (g-computation), `WeightIt` (IPW 权重), `survival` (生存模型), `ipw` (IPCW)
- **MSRA 模板**: `src/shared/templates/tte_causal_template.R`
