# 生存分析中的机器学习方法 (Machine Learning for Survival Analysis)

> 版本: 1.0 | 2026-06-13
> MSRA 关联: `analysis-plan` Phase 3 方法选择, `analysis-exec` Phase 5 预后模型, `report` Phase 7 结果报告

---

## 概述

传统生存分析以 Cox 比例风险模型为核心，但当数据具有高维特征、复杂非线性关系或比例风险 (PH) 假设违反时，机器学习方法提供了更灵活的替代方案。本章介绍生存分析中常用的 ML 方法及其与传统方法的比较。

### ML vs 传统生存分析：何时选择？

| 特征 | 传统方法 (Cox PH) | ML 方法 |
|------|-------------------|---------|
| 样本量 | 中等即可 (数百) | 通常需要较大样本 (数千以上) |
| 变量数 | 适中 (数十) | 适合高维 (数百至数千) |
| 非线性关系 | 需手动建模 | 自动捕获 |
| 交互效应 | 需预先指定 | 自动学习 |
| 可解释性 | 高 (HR 可直接解释) | 较低 (需后处理) |
| PH 假设 | 必须满足 | 无此要求 |
| 外部验证 | 成熟的校准评估 | 仍在发展中 |

> **实践原则**: 优先尝试 Cox PH (带适当扩展)，仅当 PH 假设严重违反或变量关系高度非线性时才转向 ML 方法。

---

## 一、正则化 Cox 模型 (Regularized Cox-PH)

### 1.1 原理

在 Cox 偏似然函数中加入惩罚项，适用于高维数据（如基因组学）:

$$\ell_{pen}(\beta) = \ell_{Cox}(\beta) - \lambda \cdot P(\beta)$$

| 惩罚类型 | 惩罚函数 $P(\beta)$ | 特点 |
|---------|---------------------|------|
| **Lasso** | $\sum|\beta_j|$ | 变量选择，产生稀疏解 |
| **Ridge** | $\sum\beta_j^2$ | 处理共线性，保留所有变量 |
| **Elastic Net** | $\alpha\sum\|\beta_j\| + (1-\alpha)\sum\beta_j^2$ | 兼具两者优点 |

### 1.2 R 实现

```r
library(glmnet)

# 准备生存数据矩阵
x <- as.matrix(df[, predictors])
y <- Surv(df$time, df$status)

# Lasso Cox 回归
cv_fit <- cv.glmnet(x, y, family = "cox", alpha = 1, nfolds = 10)

# 最优 lambda (1-SE 规则)
best_lambda <- cv_fit$lambda.min

# 提取非零系数（变量选择）
coef_best <- coef(cv_fit, s = "lambda.min")
selected_vars <- rownames(coef_best)[which(coef_best != 0)]

# 预测风险评分
risk_scores <- predict(cv_fit, newx = x, s = "lambda.min", type = "link")
```

---

## 二、随机生存森林 (Random Survival Forests, RSF)

### 2.1 原理

随机生存森林是随机森林在生存数据上的扩展，通过集成大量生存树来估计累积风险函数。

**关键步骤**:
1. 从原始数据中 Bootstrap 抽样
2. 在每棵树的每个节点随机选择 $m_{try}$ 个候选变量
3. 使用**对数秩分裂准则 (log-rank splitting rule)** 选择最优分裂
4. 在终端节点估计 Nelson-Aalen 累积风险
5. 对所有树的预测取平均

**优势**:
- 无需 PH 假设
- 自动处理非线性和交互效应
- 内置变量重要性评估
- 可处理高维数据

### 2.2 R 实现

```r
library(randomForestSRC)

# 拟合 RSF 模型
rsf_fit <- rfsrc(
  Surv(time, status) ~ .,
  data = df_train,
  ntree = 1000,           # 树的数量
  mtry = 5,               # 每节点候选变量数
  nodesize = 15,          # 终端节点最小样本量
  importance = TRUE,      # 计算变量重要性
  seed = 42
)

# 模型摘要
print(rsf_fit)

# 变量重要性
vimp <- vimp(rsf_fit)
plot(vimp)

# 预测
pred <- predict(rsf_fit, newdata = df_test)
# pred$predicted = 预测的累积风险
# pred$survival = 预测的生存函数 (每行一个个体，每列一个时间点)

# 部分依赖图
# 变量效应可视化
plot.variable(rsf_fit, xvar.names = "age", partial = TRUE)
```

### 2.3 超参数调优

| 参数 | 说明 | 调优建议 |
|------|------|---------|
| `ntree` | 树的数量 | ≥ 1000，更多树更稳定 |
| `mtry` | 候选变量数 | 默认 $\sqrt{p}$，生存数据建议 $p/3$ |
| `nodesize` | 终端节点最小样本量 | 较大值 (15-30) 防止过拟合 |
| `nsplit` | 每节点随机分裂候选数 | 10 可加速训练 |

---

## 三、深度生存机器 (Deep Survival Machines)

### 3.1 原理

深度生存机器使用神经网络学习生存数据的特征表示，同时估计参数化的生存分布（如 Weibull 或 Log-Normal）。

$$S(t|x) = S(t|\mu(x), \sigma(x))$$

其中 $\mu(x)$ 和 $\sigma(x)$ 是由神经网络从特征 $x$ 预测的分布参数。

### 3.2 适用场景

- 非常大的数据集 (N > 10,000)
- 复杂的特征空间 (如图像、文本与结构化数据融合)
- 传统方法 PH 假设严重违反

> **注意**: 深度学习方法在小样本临床数据中通常不优于正则化 Cox 或 RSF。仅在数据量充足且特征复杂时考虑使用。

---

## 四、灵活参数模型 (Royston-Parmar 模型)

### 4.1 原理

Royston-Parmar 模型使用限制性立方样条 (restricted cubic splines) 对基线累积风险函数进行建模，是 Cox PH 和完全参数模型之间的灵活折中:

$$\ln[H_0(t)] = s(\ln(t), \gamma)$$

其中 $s(\cdot)$ 为样条函数，$\gamma$ 为样条参数。

**优势**:
- 无需 PH 假设（可建模时依协变量效应）
- 可直接估计生存概率（不像 Cox 只能估计相对效应）
- 支持多种链接函数（比例风险、比例优势、probit 等）

### 4.2 R 实现

```r
library(flexsurv)

# Royston-Parmar 模型 (使用样条的灵活模型)
rp_fit <- flexsurvspline(
  Surv(time, status) ~ age + sex + stage + treatment,
  data = df,
  k = 3,            # 内部节点数
  scale = "hazard"  # 对累积风险建模 (比例风险)
)

# 模型摘要
summary(rp_fit)

# 预测生存概率
pred_surv <- summary(rp_fit, newdata = new_patient,
                     type = "survival", t = c(12, 24, 36, 60))

# 预测中位生存时间
summary(rp_fit, newdata = new_patient, type = "median")

# 基线累积风险的样条拟合可视化
plot(rp_fit, X = new_patient, ci = TRUE, xlab = "时间 (月)")
```

### 4.3 与 Cox PH 的比较

| 特征 | Cox PH | Royston-Parmar |
|------|--------|---------------|
| 基线风险 | 非参数，未建模 | 样条建模，可直接估计 |
| 绝对风险预测 | 需要基线风险估计 | 直接可得 |
| PH 假设 | 严格要求 | 可放宽 (时依效应) |
| 外推 | 不可靠 | 可合理外推 (需谨慎) |
| 经济学评价 | 困难 | 适合 (直接输出生存曲线) |

---

## 五、限制性平均生存时间 (RMST)

### 5.1 定义

RMST 是生存曲线在时间 $t^*$ 之前的面积，即"平均无事件时间":

$$\text{RMST}(t^*) = \int_0^{t^*} S(t) \, dt$$

### 5.2 优势

- **无需 PH 假设**: 对任意生存曲线均有定义
- **直观解释**: 平均无事件生存月数
- **差异解读**: $\Delta\text{RMST}$ = 两组平均无事件时间差异

### 5.3 R 实现

```r
library(survRM2)

# 两组 RMST 比较
rmst_result <- rmst2(
  time = df$time,
  status = df$status,
  arm = df$treatment,    # 0/1 二分组
  tau = 36               # 截断时间 (月)
)

summary(rmst_result)

# 输出:
# RMST (arm=1): {值}
# RMST (arm=0): {值}
# Difference: {值} (95% CI: {下限}, {上限})
```

### 5.4 截断时间 $\tau$ 的选择

| 选择策略 | 说明 |
|---------|------|
| 临床意义时间点 | 如 5 年生存率对应的月数 |
| 最短随访时间 | 确保两组均有充足的风险集 |
| 敏感性分析 | 尝试多个 $\tau$ 检查结论稳健性 |

---

## 六、评估指标

### 6.1 判别能力指标

| 指标 | 定义 | 取值范围 | 说明 |
|------|------|---------|------|
| **Harrell's C-index** | 一致性概率 | 0.5-1.0 | 生存版 AUC，最常用 |
| **时间依赖 AUC (tdAUC)** | 特定时间点的判别力 | 0-1.0 | 不同时间点 C-index 不同 |
| **Uno's C** | 修正删失偏倚的 C-index | 0.5-1.0 | 适用于高删失率 |

### 6.2 校准指标

| 指标 | 定义 | 理想值 |
|------|------|--------|
| **校准斜率** | 预测风险 vs 观察风险的斜率 | 1.0 |
| **校准截距** | 平均预测风险校准 | 0.0 |
| **Integrated Brier Score (IBS)** | 平均 Brier 评分 | 越低越好 |

### 6.3 R 实现

```r
library(riskRegression)
library(survival)
library(pec)

# C-index
c_index <- concordance(Surv(time, status) ~ risk_score, data = df)
c_index$concordance

# 时间依赖 AUC
td_auc <- Score(
  list("Model" = cox_fit),
  formula = Surv(time, status) ~ 1,
  data = df_test,
  times = c(12, 24, 36, 60),
  metrics = "auc"
)
plotAUC(td_auc)

# Integrated Brier Score
brier <- pec(
  list("Cox" = cox_fit, "RSF" = rsf_fit),
  formula = Surv(time, status) ~ 1,
  data = df_test,
  exact = FALSE,
  cens.model = "marginal"
)
print(brier)
plot(brier)

# 校准图
cal <- calibrate(
  cox_fit,
  u = 24,  # 24 个月
  cens.model = "marginal"
)
plot(cal)
```

---

## 七、方法选择决策树

```
开始
├── 样本量 < 200?
│   └── 是 → 使用 Cox PH 或参数模型
├── 变量数 > 样本量?
│   └── 是 → 正则化 Cox (Lasso/Elastic Net)
├── PH 假设满足?
│   ├── 是 → Cox PH (首选)
│   └── 否 → 检查以下条件:
│       ├── 需要绝对风险预测? → Royston-Parmar
│       ├── 存在复杂非线性/交互? → RSF
│       ├── 样本量 > 10,000 + 高维特征? → 深度生存模型
│       └── 仅需组间差异比较? → RMST
└── 需要经济模型外推? → Royston-Parmar (首选)
```

---

## 八、R 包生态汇总

| 包名 | 方法 | 特点 |
|------|------|------|
| `survival` | Cox PH, KM | 基础生存分析 |
| `glmnet` | 正则化 Cox | 高维变量选择 |
| `randomForestSRC` | 随机生存森林 | 集成学习，变量重要性 |
| `flexsurv` | Royston-Parmar, 参数模型 | 灵活参数模型，经济模型外推 |
| `survRM2` | RMST | 无 PH 假设的组间比较 |
| `riskRegression` | tdAUC, Brier score | 模型评估与比较 |
| `pec` | 预测误差曲线 | 校准和 Brier 评分 |
| `mlr3proba` | 概率性生存预测框架 | 统一接口，支持多种 ML 方法 |
| `mlr3learners.coxph` | mlr3 生态的 Cox 学习器 | 与 mlr3 管道集成 |
| `deepsurv` / `pycox` | 深度生存模型 | Python 生态 (通过 reticulate) |

---

## 九、常见陷阱

| 陷阱 | 说明 | 解决方案 |
|------|------|---------|
| 过早转向 ML | 数据量不足时 ML 未必优于 Cox | 先拟合 Cox，再与 ML 对比 |
| C-index 过度依赖 | C-index 无法评估校准 | 同时报告校准图和 IBS |
| 未处理删失 | ML 中忽略删失导致偏倚 | 使用专用生存 ML 方法 (如 RSF) |
| RSF 外推不可靠 | 树模型不擅长外推到训练数据之外 | 需要外推时使用参数模型 |
| 过拟合 | 高维数据上未正则化 | 使用交叉验证，报告验证集性能 |
| 死亡竞争风险 | 未区分原因别风险 | 考虑竞争风险模型 (如 Fine-Gray) |
| 时依协变量 | Cox 中未正确处理时依协变量 | 使用扩展 Cox 或状态转换模型 |

---

## 十、报告模板

> 本研究使用 {方法名称} 构建 {临床结局} 预后预测模型。训练数据: {N} 例 ({事件数} 例事件)，中位随访 {月数} 个月。{描述 PH 假设检验结果及方法选择依据}。模型包含 {变量数} 个预测变量，{描述变量选择方法}。判别能力: C-index = {值} (95% CI: {下限}-{上限})，{时间} 个月 tdAUC = {值}。校准: 校准斜率 = {值}，IBS = {值}。{与 Cox PH 的性能比较}。验证: {内部/外部} 验证 C-index = {值}。变量重要性: {前 3-5 个重要变量}。分析使用 R {版本}，{包名} 包。

---

## 十一、参考资源

- **RSF**: Ishwaran H, Kogalur UB, Blackstone EH, Lauer MS. Random survival forests. *Ann Appl Stat*, 2008, 2(3): 841-860.
- **正则化 Cox**: Simon N, Friedman J, Hastie T, Tibshirani R. Regularization paths for Cox's proportional hazards model via coordinate descent. *J Stat Softw*, 2011, 39(5): 1-13.
- **Royston-Parmar**: Royston P, Parmar MK. Flexible parametric proportional-hazards and proportional-odds models for censored survival data, with application to prognostic modelling and estimation of treatment effects. *Stat Med*, 2002, 21(15): 2175-2197.
- **RMST**: Uno H, Claggett B, Tian L, et al. Moving beyond the hazard ratio in quantifying the between-group difference in survival analysis. *J Clin Oncol*, 2014, 32(22): 2380-2385.
- **深度生存模型**: Katzman JL, Shaham U, Cloninger A, et al. DeepSurv: personalized treatment recommender system using a Cox proportional hazards deep neural network. *BMC Med Res Methodol*, 2018, 18: 24.
- **R 包**: `randomForestSRC`, `glmnet`, `flexsurv`, `survRM2`, `riskRegression`, `pec`, `mlr3proba`
- **MSRA 模板**: `src/shared/templates/survival_ml_template.R`
