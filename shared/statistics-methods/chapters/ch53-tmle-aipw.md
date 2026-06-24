# Ch53: TMLE/AIPW 双重稳健估计 (Doubly Robust Estimation)

> **适用场景**: 因果推断中的平均治疗效应估计、需要鲁棒估计的观察性研究
> **核心方法**: TMLE (Targeted Maximum Likelihood Estimation), AIPW (Augmented Inverse Probability Weighting)
> **参考文献**: van der Laan & Rose (2011), Robins et al. (1994)

---

## 1. 概述

双重稳健 (Doubly Robust, DR) 估计器在以下两个模型中**只需正确指定一个**即可获得一致估计：
1. **倾向性评分模型** (Propensity Score): P(T=1|X)
2. **结局模型** (Outcome Model): E[Y|T,X]

这比单纯的回归调整（需结局模型正确）或 IPTW（需倾向性模型正确）更鲁棒。

## 2. 方法对比

| 方法 | 需正确模型 | 双重稳健 | 半参数有效 | 偏倚校正 |
|------|-----------|---------|-----------|---------|
| 回归调整 | 结局模型 | ❌ | ❌ | 无 |
| IPTW | 倾向性模型 | ❌ | ❌ | 无 |
| AIPW | 任一模型 | ✅ | ✅ (当两者都正确) | 自动 |
| TMLE | 任一模型 | ✅ | ✅ (当两者都正确) | 迭代校正 |

## 3. AIPW (Augmented Inverse Probability Weighting)

### 3.1 原理

AIPW 估计量 = IPTW 估计量 + 回归调整的偏差校正项：

```
τ_AIPW = 1/n Σ [ (T·Y)/π(X) - ((T-π(X))·μ₁(X))/π(X) ]
       - 1/n Σ [ ((1-T)·Y)/(1-π(X)) - ((T-π(X))·μ₀(X))/(1-π(X)) ]
```

其中 π(X) = P(T=1|X) 是倾向性评分，μ₁(X) = E[Y|T=1,X]，μ₀(X) = E[Y|T=0,X]

### 3.2 R 实现

```r
# R: 使用 WeightIt + 自定义
library(WeightIt)
library(sandwich)

# 倾向性评分
ps_model <- glm(treatment ~ age + sex + bmi + baseline_score,
                data = df, family = binomial)
ps <- predict(ps_model, type = "response")

# 结局模型
outcome_model_treated <- lm(outcome ~ age + sex + bmi + baseline_score,
                            data = df[df$treatment == 1, ])
outcome_model_control <- lm(outcome ~ age + sex + bmi + baseline_score,
                            data = df[df$treatment == 0, ])

mu1 <- predict(outcome_model_treated, newdata = df)
mu0 <- predict(outcome_model_control, newdata = df)

# AIPW 估计
T_vec <- df$treatment
Y_vec <- df$outcome

aipw_ate <- mean(
  T_vec * Y_vec / ps - (T_vec - ps) * mu1 / ps -
  (1 - T_vec) * Y_vec / (1 - ps) + (T_vec - ps) * mu0 / (1 - ps)
)

# Bootstrap CI
boot_aipw <- replicate(1000, {
  idx <- sample(nrow(df), replace = TRUE)
  df_boot <- df[idx, ]
  # 重复上述计算...
})
quantile(boot_aipw, c(0.025, 0.975))
```

### 3.3 Python 实现

```python
import numpy as np
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

def aipw_ate(T, Y, X, ps_model=None, outcome_model=None):
    """
    AIPW 估计平均治疗效应
    
    Parameters
    ----------
    T : array, treatment indicator (0/1)
    Y : array, outcome
    X : array, covariates
    ps_model : sklearn model for propensity score
    outcome_model : sklearn model for outcome
    """
    n = len(T)
    
    if ps_model is None:
        ps_model = LogisticRegression(max_iter=1000)
    if outcome_model is None:
        outcome_model = RandomForestRegressor(n_estimators=100)
    
    # 拟合倾向性评分
    ps_model.fit(X, T)
    ps = ps_model.predict_proba(X)[:, 1]
    ps = np.clip(ps, 0.01, 0.99)  # 截断极端权重
    
    # 拟合结局模型（分别拟合）
    mu1_model = outcome_model.__class__(**outcome_model.get_params())
    mu0_model = outcome_model.__class__(**outcome_model.get_params())
    
    mu1_model.fit(X[T == 1], Y[T == 1])
    mu0_model.fit(X[T == 0], Y[T == 0])
    
    mu1 = mu1_model.predict(X)
    mu0 = mu0_model.predict(X)
    
    # AIPW 估计
    aipw = np.mean(
        T * Y / ps - (T - ps) * mu1 / ps -
        (1 - T) * Y / (1 - ps) + (T - ps) * mu0 / (1 - ps)
    )
    
    return aipw

# Bootstrap CI
def bootstrap_ci(T, Y, X, n_boot=1000, alpha=0.05):
    estimates = []
    for _ in range(n_boot):
        idx = np.random.choice(len(T), len(T), replace=True)
        est = aipw_ate(T[idx], Y[idx], X[idx])
        estimates.append(est)
    return np.percentile(estimates, [100*alpha/2, 100*(1-alpha/2)])
```

## 4. TMLE (Targeted Maximum Likelihood Estimation)

### 4.1 原理

TMLE 通过迭代更新初始结局模型的预测值，使其偏向因果推断的目标参数：
1. **初始估计**: 使用 Super Learner 拟合 E[Y|T,X]
2. **倾向性评分**: 使用 Super Learner 拟合 P(T=1|X)
3. **波动参数**: 通过 logistic 回归更新预测值
4. **迭代**: 直到收敛

### 4.2 R 实现

```r
# R: tmle 包
library(tmle)
library(SuperLearner)

# Super Learner 库
sl_lib <- c("SL.glm", "SL.randomForest", "SL.glmnet", "SL.rpart")

# TMLE 估计
tmle_result <- tmle(
  Y = df$outcome,
  A = df$treatment,
  W = df[, c("age", "sex", "bmi", "baseline_score")],
  Q.SL.library = sl_lib,
  g.SL.library = sl_lib,
  family = "gaussian"
)

# 结果
print(tmle_result)
tmle_result$estimates$ATE
tmle_result$estimates$CI
```

### 4.3 Python 实现

```python
# Python: econml
from econml.dml import LinearDML

# 使用 Double Machine Learning
dml = LinearDML(
    model_y=RandomForestRegressor(),
    model_t=RandomForestClassifier(),
    discrete_treatment=True
)
dml.fit(Y, T, X=X, W=W)
ate = dml.ate(X)
ci = dml.ate_interval(X, alpha=0.05)
```

## 5. Super Learner (交叉验证集成)

```r
# R: SuperLearner
library(SuperLearner)

SL_library <- c("SL.glm", "SL.glmnet", "SL.randomForest",
                "SL.rpart", "SL.nnet", "SL.svm")

sl_fit <- SuperLearner(
  Y = df$outcome,
  X = df[, predictors],
  SL.library = SL_library,
  family = gaussian(),
  method = "method.NNLS"
)

# 查看各算法权重
sl_fit$coef
```

## 6. 结果报告

``── 双重稳健估计结果 ──

方法: {AIPW / TMLE}

ATE 估计:
- DR 估计值: {值} (95% CI: {下限}, {上限})
- IPTW 估计值: {值} (95% CI: {下限}, {上限}) [对照]
- 回归调整估计值: {值} (95% CI: {下限}, {上限}) [对照]

倾向性评分诊断:
- 权重范围: [{min}, {max}]
- 标准化均值差 (加权后): {值} (<0.1 为良好平衡)
- 权重分布: {描述}

敏感性分析:
- 不同截断阈值 (0.01, 0.025, 0.05): {结果}
- E-value: {值} (未测量混杂需关联强度 > {值} 才能解释掉效应)
```

## 7. 注意事项

| 陷阱 | 说明 | 正确做法 |
|------|------|---------|
| 极端权重 | 倾向性评分接近 0/1 | 截断权重 (0.01-0.99) |
| 忽略正性假设 | 存在确定性治疗分配 | 检查权重分布 |
| 仅报告点估计 | 缺乏不确定性量化 | Bootstrap CI |
| 模型选择偏差 | 手动选择模型 | 使用 Super Learner |
| 与因果森林混淆 | DR 估计 ATE，森林估计 CATE | 根据目标选择方法 |

## 8. 参考文献

1. van der Laan MJ, Rose S. Targeted Learning: Causal Inference for Observational and Experimental Data. Springer; 2011.
2. Robins JM, Rotnitzky A, Zhao LP. Estimation of regression coefficients when some regressors are not always observed. JASA. 1994;89(427):846-866.
3. Bang H, Robins JM. Doubly robust estimation in missing data and causal inference models. Biometrics. 2005;61(4):962-973.
4. van der Laan MJ, Rubin D. Targeted maximum likelihood learning. Int J Biostat. 2006;2(1).
5. Chernozhukov V, Chetverikov D, Demirer M, et al. Double/debiased machine learning for treatment and structural parameters. Econom J. 2018;21(1):C1-C68.
