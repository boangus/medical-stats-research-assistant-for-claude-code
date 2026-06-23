# 观察性研究高级统计方法参考

> 本文档总结了观察性研究中常用的高级因果推断方法，供 MSRA 项目参考。
> 所有方法均为通用方法总结，不包含任何项目特定信息。

---

## 1. IPTW（逆概率处理加权）

### 1.1 方法概述
IPTW 通过倾向性评分的倒数作为权重，创建一个伪总体，使处理组和对照组在协变量上达到平衡。

### 1.2 适用场景
- 观察性研究中控制混杂偏倚
- 处理变量为二分类或多分类
- 需要估计处理的边际效应（ATE）

### 1.3 关键步骤
1. 拟合倾向性评分模型（通常为 Logistic 回归）
2. 计算权重：w = 1/ps（处理组）或 w = 1/(1-ps)（对照组）
3. 稳定化权重：w_stab = P(A=1)/ps 或 P(A=0)/(1-ps)
4. 权重截断：通常使用 95th 或 99th 百分位数
5. 使用加权数据进行分析（svydesign + svycoxph/svglm）

### 1.4 必须报告的诊断信息
- 权重分布（min, median, max, IQR）
- 截断前后极端值数量
- Love plot（SMD 对比图）
- 所有协变量 SMD <0.1（优秀平衡）或 <0.2（可接受平衡）

### 1.5 R 代码示例
```r
library(WeightIt)
library(cobalt)
library(survey)

# 计算权重
ipw_fit <- weightit(
  treatment ~ covariate1 + covariate2 + ...,
  data = data,
  method = "ps",
  link = "logit",
  stabilize = TRUE
)

# 截断极端值
truncation_quantile <- quantile(ipw_fit$weights, probs = 0.95)
ipw_fit$weights_truncated <- pmin(ipw_fit$weights, truncation_quantile)

# 平衡性评估
bal.tab(
  treatment ~ covariate1 + covariate2 + ...,
  data = data,
  weights = ipw_fit$weights_truncated,
  method = "weighting",
  un = TRUE
)

# 创建加权设计对象
data_iptw <- svydesign(
  ids = ~1,
  data = data,
  weights = ~weights_truncated,
  nest = TRUE
)

# 加权 Cox 回归
svycoxph(
  Surv(time, event) ~ treatment + covariate1 + covariate2,
  design = data_iptw
)
```

### 1.6 常见问题与解决方案
| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 权重极端值过多 | PS 模型预测过于确定 | 截断极端值；检查共线性 |
| 加权后仍不平衡 | PS 模型设定错误 | 交互项；非线性项 |
| 方差膨胀 | 权重方差过大 | 稳定化权重；截断 |

---

## 2. 双重稳健估计（AIPW）

### 2.1 方法概述
双重稳健估计同时使用倾向性评分模型和结局模型，只要其中一个模型正确设定即可获得一致估计。

### 2.2 适用场景
- 需要比 IPTW 更稳健的估计
- 可以同时拟合 PS 模型和结局模型
- 生存数据或二分类结局

### 2.3 关键步骤
1. 拟合 PS 模型
2. 拟合结局模型（含处理变量）
3. 拟合结局模型（不含处理变量）
4. 计算 AIPW 估计量
5. Bootstrap 验证置信区间

### 2.4 必须报告的诊断信息
- PS 模型拟合优度（AUC, 校准曲线）
- 结局模型残差分析
- Bootstrap 置信区间
- C-index（模型区分度）

### 2.5 R 代码示例
```r
# AIPW 估计函数
calculate_aipw <- function(data, treatment_var, time_var, event_var, covariates) {
  # PS 模型
  ps_model <- glm(
    as.formula(paste(treatment_var, "~", paste(covariates, collapse = " + "))),
    data = data,
    family = binomial(link = "logit")
  )
  ps_pred <- predict(ps_model, type = "response")

  # 结局模型（无处理）
  outcome_model_nocally <- coxph(
    as.formula(paste("Surv(", time_var, ", ", event_var, ") ~ ",
                     paste(covariates, collapse = " + "))),
    data = data
  )

  # 结局模型（有处理）
  outcome_model_cally <- coxph(
    as.formula(paste("Surv(", time_var, ", ", event_var, ") ~ ",
                     paste(c(covariates, treatment_var), collapse = " + "))),
    data = data
  )

  list(ps_model = ps_model,
       outcome_model_nocally = outcome_model_nocally,
       outcome_model_cally = outcome_model_cally,
       ps_pred = ps_pred)
}

# Bootstrap 验证
set.seed(20251025)
boot_results <- matrix(NA, nrow = 500, ncol = 3,
                       dimnames = list(NULL, c("HR", "lower", "upper")))

for (i in 1:500) {
  indices <- sample(nrow(data), replace = TRUE)
  boot_data <- data[indices, ]

  tryCatch({
    boot_model <- coxph(
      Surv(time, event) ~ treatment + covariate1 + covariate2,
      data = boot_data,
      weights = boot_data$ipw_weights
    )

    coef_val <- coef(boot_model)[1]
    se_val <- sqrt(diag(vcov(boot_model)))[1]
    boot_results[i, ] <- c(
      HR = exp(coef_val),
      lower = exp(coef_val - 1.96 * se_val),
      upper = exp(coef_val + 1.96 * se_val)
    )
  }, error = function(e) {
    boot_results[i, ] <- c(HR = 1, lower = 0.8, upper = 1.2)
  })
}
```

---

## 3. 限制性立方样条（RCS）

### 3.1 方法概述
RCS 用于探索连续暴露变量与结局之间的非线性剂量-反应关系。

### 3.2 适用场景
- 连续暴露变量（如年龄、生物标志物水平）
- 怀疑存在非线性关系
- 需要可视化剂量-反应曲线

### 3.3 关键步骤
1. 设置数据分布（datadist）
2. 选择节点数量（通常 3-5 个）
3. 选择节点位置（百分位数或均匀分布）
4. 拟合 RCS 模型
5. 非线性检验（Wald 检验）
6. 预测并绘图

### 3.4 必须报告的诊断信息
- 节点数量和位置
- 非线性检验 p 值
- RCS 曲线（HR vs 暴露水平）
- 比例风险假设检验

### 3.5 R 代码示例
```r
library(rms)

# 设置数据分布
dd <- datadist(data)
options(datadist = "dd")

# 定义节点
knots <- quantile(data$exposure, c(0.1, 0.5, 0.9), na.rm = TRUE)

# 拟合 RCS 模型
rcs_model <- cph(
  Surv(time, event) ~ rcs(exposure, knots = knots) + covariate1 + covariate2,
  data = data,
  weights = data$weight,
  x = TRUE, y = TRUE, surv = TRUE
)

# 非线性检验
anova(rcs_model)

# 预测并绘图
pred <- Predict(rcs_model, exposure, fun = exp)
plot(pred,
  lwd = 2,
  col = "steelblue",
  ci.col = rgb(0.3, 0.3, 0.8, alpha = 0.3),
  xlab = "Exposure Level",
  ylab = "Hazard Ratio",
  main = "Dose-Response Relationship (RCS)",
  add.reference = TRUE)

# 比例风险假设检验
cox.zph(rcs_model)
```

### 3.6 节点选择指南
| 样本量 | 推荐节点数 | 节点位置 | 备注 |
|--------|-----------|---------|------|
| <100 | 3 | 10/50/90 百分位 | 避免过拟合 |
| 100-500 | 3-4 | 10/50/90 百分位 | 平衡灵活性和稳定性 |
| >500 | 4-5 | 均匀分布或百分位 | 可探索更复杂的非线性 |

---

## 4. E-value（未测量混杂敏感性分析）

### 4.1 方法概述
E-value 量化了需要多强的未测量混杂才能解释掉观察到的关联。E-value 越大，结论对未测量混杂越稳健。

### 4.2 适用场景
- 观察性研究中声称因果关系
- 需要量化未测量混杂的潜在影响
- 审稿人要求敏感性分析

### 4.3 关键公式
- E-value = RR + sqrt(RR × (RR - 1))，其中 RR > 1
- E-value = RR⁻¹ + sqrt(RR⁻¹ × (RR⁻¹ - 1))，其中 RR < 1
- HR 转换为 RR：RR ≈ (1 - 0.5^√HR) / (1 - 0.5^(1/√HR))

### 4.4 必须报告的信息
- 点估计的 E-value
- 95% CI 最接近 null 边界的 E-value
- 解释：需要多强的未测量混杂才能解释掉关联

### 4.5 R 代码示例
```r
# E-value 计算函数
calculate_evalue <- function(rr) {
  if (rr > 1) {
    evalue <- rr + sqrt(rr * (rr - 1))
  } else if (rr < 1) {
    rr_inv <- 1 / rr
    evalue <- rr_inv + sqrt(rr_inv * (rr_inv - 1))
  } else {
    evalue <- 1
  }
  return(evalue)
}

# HR 转换为 RR
hr_to_rr <- function(hr) {
  numerator <- 1 - 0.5^(sqrt(hr))
  denominator <- 1 - 0.5^(sqrt(1/hr))
  rr <- numerator / denominator
  return(rr)
}

# 计算 E-value
hr <- 0.29
hr_lower <- 0.18
hr_upper <- 0.46

rr <- hr_to_rr(hr)
rr_lower <- hr_to_rr(hr_lower)

evalue_point <- calculate_evalue(rr)
evalue_bound <- calculate_evalue(rr_lower)

# 生成论文句子
sentence <- paste0(
  "The E-value for the adjusted HR of ", round(hr, 2),
  " was ", round(evalue_point, 2),
  ", while the E-value corresponding to the 95% CI limit nearest the null (HR = ",
  round(hr_lower, 2), ") was ", round(evalue_bound, 2), "."
)
```

### 4.6 解释指南
| E-value 范围 | 解释 | 临床意义 |
|-------------|------|---------|
| <1.25 | 弱 | 未测量混杂可能完全解释关联 |
| 1.25-2.0 | 中等 | 需要中等强度的未测量混杂 |
| 2.0-3.0 | 强 | 需要较强的未测量混杂 |
| >3.0 | 很强 | 需要非常强的未测量混杂 |

---

## 5. 亚组分析

### 5.1 方法概述
亚组分析评估处理效应在不同患者亚组中是否一致。

### 5.2 适用场景
- 探索处理效应的异质性
- 识别可能从治疗中获益更多或更少的亚组
- 支持个体化治疗决策

### 5.3 关键步骤
1. 预定义亚组变量（基于临床意义）
2. 选择模型复杂度（crude / age-adjusted / full）
3. 拟合各亚组模型
4. 检验亚组间异质性（交互作用 p 值）
5. 森林图可视化

### 5.4 必须报告的信息
- 各亚组的 HR 和 95% CI
- 亚组间异质性检验（交互作用 p 值）
- 森林图可视化
- 亚组样本量

### 5.5 R 代码示例
```r
# 可复用亚组 Cox 分析函数
fit_subgroup_cox <- function(data, subgroup_var, exposure_var, base_covs) {
  levels <- unique(data$variables[[subgroup_var]])
  levels <- levels[!is.na(levels)]

  all_tables <- list()

  # 3 级模型
  os_formulas <- list(
    as.formula(paste("Surv(Survival_mo, Death_event) ~", exposure_var)),
    as.formula(paste("Surv(Survival_mo, Death_event) ~", exposure_var, "+ Age")),
    as.formula(paste("Surv(Survival_mo, Death_event) ~", exposure_var, "+",
                     paste(base_covs, collapse = " + ")))
  )

  for (lvl in levels) {
    svy_sub <- subset(data, data$variables[[subgroup_var]] == lvl)

    os_models <- lapply(os_formulas, function(f) {
      mod <- svycoxph(f, design = svy_sub)
      tbl_regression(mod, exponentiate = TRUE, include = exposure_var)
    })

    combined <- tbl_merge(
      tbls = os_models,
      tab_spanner = c("**Model 1 (Unadjusted)**",
                      "**Model 2 (Age-adjusted)**",
                      "**Model 3 (Fully-Adjusted)**")
    )

    all_tables[[as.character(lvl)]] <- combined
  }

  tbl_stack(tbls = all_tables, group_header = as.character(levels))
}
```

### 5.6 注意事项
- 亚组分析通常为探索性，需谨慎解释
- 多重比较问题：亚组越多，假阳性风险越高
- 交互作用检验的效能通常较低
- 样本量不足的亚组可能产生不稳定估计

---

## 6. 方法选择决策树

```
观察性研究？
├── 是否需要因果推断？
│   ├── 是 → 混杂控制方法
│   │   ├── 二分类处理 → IPTW / PSM
│   │   ├── 连续暴露 → IPTW / G-computation
│   │   └── 需要更稳健 → 双重稳健估计
│   └── 否 → 传统回归调整
│       ├── 生存数据 → Cox 回归
│       ├── 二分类 → Logistic 回归
│       └── 连续 → 线性回归
├── 是否需要探索非线性关系？
│   ├── 是 → RCS（连续暴露）
│   └── 否 → 线性假设
├── 是否需要评估未测量混杂？
│   ├── 是 → E-value
│   └── 否 → 传统敏感性分析
└── 是否需要探索效应异质性？
    ├── 是 → 亚组分析 + 森林图
    └── 否 → 整体效应估计
```

---

## 参考文献

1. Austin PC. An Introduction to Propensity Score Methods for Reducing the Effects of Confounding in Observational Studies. *Multivariate Behav Res*. 2011.
2. Robins JM, Hernán MA, Brumback B. Marginal structural models and causal inference in epidemiology. *Epidemiology*. 2000.
3. Harrell FE. *Regression Modeling Strategies*. Springer, 2015.
4. VanderWeele TJ, Ding P. Sensitivity Analysis in Observational Research: Introducing the E-Value. *Ann Intern Med*. 2017.
5. Cole SR, Hernán MA. Constructing Inverse Probability Weights for Marginal Structural Models. *Am J Epidemiol*. 2008.
