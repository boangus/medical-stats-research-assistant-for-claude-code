# Ch51: 纵向数据分析进阶 (Advanced Longitudinal Data Analysis)

> **适用场景**: 重复测量数据、生长曲线、联合建模、功能数据分析
> **核心方法**: GEE vs LMM、非线性增长曲线、联合模型、FDA
> **参考文献**: Diggle et al. (2002), Rizopoulos (2012)

---

## 1. 概述

纵向数据（重复测量）在临床研究中极为常见：患者在多个时间点被反复测量。进阶方法包括：

- **边际 vs 条件模型**: GEE (population-averaged) vs LMM (subject-specific)
- **非线性增长曲线**: 生物标志物的非线性轨迹
- **联合模型**: 纵向标志物与生存结局的联合建模
- **功能数据分析**: 密集纵向数据的函数视角

## 2. GEE vs LMM 选择指南

| 维度 | GEE (边际模型) | LMM (条件模型) |
|------|---------------|---------------|
| 解释 | 总体平均效应 | 个体特异效应 |
| 假设 | 不需分布假设 | 需随机效应分布假设 |
| 缺失处理 | 依赖 MCAR (标准) | 依赖 MAR |
| 时间依赖协变量 | 可处理 | 更灵活 |
| 预测 | 仅总体 | 可做个体预测 |
| 推荐场景 | RCT 主分析、群体推断 | 个体轨迹、预测模型 |

**决策树**:
```
研究目标是什么？
├── 总体平均效应（RCT 主分析）→ GEE
├── 个体特异效应（预测/个性化）→ LMM
├── 两者都需要 → 报告两套结果
└── 时间依赖协变量 + 生存结局 → 联合模型
```

## 3. GEE 实现

```r
# R: geepack
library(geepack)

# GEE 模型
gee_fit <- geeglm(
  outcome ~ treatment * time + age + sex,
  data = df,
  id = subject_id,
  family = gaussian,
  corstr = "exchangeable"  # 可选: ar1, unstructured, independence
)

# 结果摘要
summary(gee_fit)

# 稳健方差估计
coef(summary(gee_fit))[, c("Estimate", "Std.err", "Pr(>|W|)")]
```

```python
# Python: statsmodels GEE
import statsmodels.api as sm
import statsmodels.genmod.generalized_estimating_equations as gee

# GEE 模型
family = sm.families.Gaussian()
cov_struct = sm.cov_struct.Exchangeable()

model = gee.GEE.from_formula(
    "outcome ~ treatment * time + age + sex",
    groups="subject_id",
    data=df,
    family=family,
    cov_struct=cov_struct
)
result = model.fit()
print(result.summary())
```

## 4. LMM / GLMM 实现

```r
# R: lme4
library(lme4)

# 线性混合模型
lmm_fit <- lmer(
  outcome ~ treatment * time + age + sex + (1 + time | subject_id),
  data = df,
  REML = TRUE
)

# 随机截距 + 随机斜率
summary(lmm_fit)
confint(lmm_fit, method = "profile")

# 模型比较（LRT）
lmm_null <- lmer(outcome ~ treatment + time + (1 | subject_id), data = df)
anova(lmm_null, lmm_fit)

# GLMM（二分类结局）
glmm_fit <- glmer(
  response ~ treatment * time + (1 | subject_id),
  data = df,
  family = binomial
)
```

```python
# Python: statsmodels MixedLM
import statsmodels.formula.api as smf

# 线性混合模型
model = smf.mixedlm(
    "outcome ~ treatment * time + age + sex",
    data=df,
    groups=df["subject_id"],
    re_formula="~time"  # 随机截距 + 随机斜率
)
result = model.fit()
print(result.summary())
```

## 5. 非线性增长曲线

```r
# R: nlme
library(nlme)

# 非线性混合模型（例如：logistic 生长曲线）
nlme_fit <- nlme(
  outcome ~ SSlogis(time, Asym, xmid, scal),
  data = df,
  fixed = Asym + xmid + scal ~ treatment,
  random = Asym + xmid + scal ~ 1 | subject_id,
  start = c(Asym = 100, xmid = 5, scal = 1)
)

# 模型摘要
summary(nlme_fit)
```

## 6. 联合模型 (Joint Model)

联合模型同时建模纵向标志物轨迹和生存结局，解决：
- 纵向标志物有测量误差
- 时间依赖协变量内生性
- 个体动态预测

```r
# R: JMbayes2
library(JMbayes2)

# Step 1: 纵向子模型
lme_fit <- lme(log_biomarker ~ time * treatment + age,
               random = ~ time | subject_id,
               data = df_long)

# Step 2: 生存子模型
cox_fit <- coxph(Surv(time, event) ~ treatment + age,
                 data = df_surv, x = TRUE)

# Step 3: 联合模型
jm_fit <- jm(cox_fit, lme_fit, time_var = "time",
             n_iter = 10000L, n_burnin = 1000L)

# 结果摘要
summary(jm_fit)

# 动态预测
pred <- predict(jm_fit, newdata = new_patient,
                process = "event",
                times = seq(0, 5, by = 0.5))
```

```python
# Python: 使用 lifelines + 自定义（Python 联合模型生态较弱）
# 推荐 R 的 JMbayes2 作为首选工具
```

## 7. 功能数据分析 (FDA)

```r
# R: refund
library(refund)

# 功能主成分分析 (FPCA)
fpca_fit <- fpca.face(Y = dense_matrix, argvals = time_grid)

# 功能回归
freg_fit <- pffr(Y ~ x1 + x2, data = df_func)
```

## 8. 模型选择标准

| 标准 | 适用场景 | 说明 |
|------|---------|------|
| AIC | 模型比较 | 越小越好，惩罚复杂度 |
| BIC | 模型选择 | 更强惩罚，倾向于简单模型 |
| LRT (似然比检验) | 嵌套模型 | 需嵌套关系，df 差异 |
| REML vs ML | 固定效应比较 | REML 用于方差组件，ML 用于固定效应 |
| 交叉验证 | 预测模型 | 时间序列 CV |

## 9. 注意事项

| 陷阱 | 说明 | 正确做法 |
|------|------|---------|
| GEE 用于个体预测 | GEE 仅估计总体效应 | 用 LMM 做个体预测 |
| 忽略随机效应 | 固定效应模型低估 SE | 至少加随机截距 |
| 时间编码不当 | 连续时间 vs 离散时间 | 根据设计选择 |
| 协方差结构选择 | 错误结构影响 SE | 用 AIC/BIC 比较 |
| 基线作为时间点 | 基线测量的处理 | 考虑 baseline as covariate |

## 10. 参考文献

1. Diggle PJ, Heagerty P, Liang KY, Zeger SL. Analysis of Longitudinal Data. 2nd ed. Oxford University Press; 2002.
2. Rizopoulos D. Joint Models for Longitudinal and Time-to-Event Data. Chapman & Hall/CRC; 2012.
3. Fitzmaurice GM, Laird NM, Ware JH. Applied Longitudinal Analysis. 2nd ed. Wiley; 2011.
4. Liang KY, Zeger SL. Longitudinal data analysis using generalized linear models. Biometrika. 1986;73(1):13-22.
5. Laird NM, Ware JH. Random-effects models for longitudinal data. Biometrics. 1982;38(4):963-974.
6. Rizopoulos D. Dynamic predictions and prospective accuracy in joint models for longitudinal and time-to-event data. Biometrics. 2011;67(3):819-829.
