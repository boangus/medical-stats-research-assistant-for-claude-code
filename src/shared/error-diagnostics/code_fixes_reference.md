# 统计分析错误处理代码参考

> MSRA 项目专用。本文件包含统计分析执行中常见错误的完整代码修复示例。
> 供 `skills/analysis-exec/SKILL.md` Phase 6 自愈机制引用，避免 SKILL.md 过长。
>
> 简要诊断规则见 [`error_patterns.md`](error_patterns.md)，本文件提供完整可执行代码。

---

## 一、完全分离问题 (Perfect Separation)

### 错误现象
- R: `"X matrix deemed to be singular"`
- Python: `"Perfect separation detected"`

### R — Firth 惩罚 Logistic 回归

```r
# 错误: "X matrix deemed to be singular" (完全分离)
# 解决方案: 使用 Firth 惩罚 Logistic 回归

# 安装并加载 logistf 包
if (!require("logistf")) install.packages("logistf")
library(logistf)

# 使用 firth 惩罚拟合模型
model_firth <- logistf(
  formula = outcome ~ treatment + age + sex + bmi,
  data = data,
  firth = TRUE,      # 启用 Firth 惩罚
  pl = TRUE          # 计算剖面似然 CI
)

# 查看结果
summary(model_firth)
# 提取 OR 和 95% CI
or <- exp(model_firth$coefficients)
ci_lower <- exp(model_firth$ci.lower)
ci_upper <- exp(model_firth$ci.upper)
```

### Python — Firth / L1 正则化

```python
# 错误: "Perfect separation detected"
# 解决方案: 使用 statsmodels 的 penalized 参数或手动 Firth

import statsmodels.api as sm
import statsmodels.formula.api as smf

# 方法1: 使用 penalized 参数 (L2 惩罚)
model = smf.logit(
    'outcome ~ treatment + age + sex + bmi',
    data=df
).fit_regularized(
    method='l1',      # L1 惩罚
    alpha=0.01        # 惩罚强度
)

# 方法2: 使用 Firth 近似 (通过调整)
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(
    penalty='l2',
    C=0.1,            # 较小的 C = 较强的正则化
    solver='lbfgs',
    max_iter=1000
)
model.fit(X, y)
```

---

## 二、多重共线性 (Multicollinearity)

### 错误现象
- 系数不稳定，标准误过大
- VIF > 10 提示严重共线性

### R — VIF 诊断与修复

```r
# 错误: 共线性导致系数不稳定
# 解决方案: VIF 诊断 + 变量选择

library(car)

# 计算 VIF
model <- lm(outcome ~ age + bmi + sbp + dbp + weight + height, data = df)
vif_values <- vif(model)
print(vif_values)

# VIF > 10 表示严重共线性
# 修复策略1: 删除高 VIF 变量
high_vif_vars <- names(vif_values)[vif_values > 10]
cat("高 VIF 变量:", high_vif_vars, "\n")

# 修复策略2: 合并共线性变量 (如 BMI 和 weight/height)
df$bmi_calc <- df$weight / (df$height/100)^2
model_fixed <- lm(outcome ~ age + bmi_calc + sbp + dbp, data = df)

# 修复策略3: 使用主成分分析 (PCA)
library(caret)
preproc <- preProcess(df[, c("age", "bmi", "sbp", "dbp")], method = c("center", "scale", "pca"))
df_pca <- predict(preproc, df)
```

### Python — VIF 诊断与修复

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# 计算 VIF
def calculate_vif(df, features):
    vif_data = pd.DataFrame()
    vif_data["feature"] = features
    vif_data["VIF"] = [variance_inflation_factor(df[features].values, i)
                       for i in range(len(features))]
    return vif_data

vif_result = calculate_vif(df, ['age', 'bmi', 'sbp', 'dbp', 'weight'])
print(vif_result)

# 删除 VIF > 10 的变量
high_vif = vif_result[vif_result['VIF'] > 10]['feature'].tolist()
features_selected = [f for f in features if f not in high_vif]

# 或使用 PCA
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[features])
pca = PCA(n_components=0.95)  # 保留 95% 方差
X_pca = pca.fit_transform(X_scaled)
```

---

## 三、Cox 回归 PH 假设违反

### 错误现象
- Schoenfeld 残差检验 p < 0.05
- 残差图显示时间趋势

### R — 分层 Cox / 时依系数 / 分段 Cox

```r
# 错误: Schoenfeld 残差检验 p < 0.05 (PH 假设违反)
# 解决方案: 分层 Cox 或时依系数模型

library(survival)

# 检验 PH 假设
cox_model <- coxph(Surv(time, event) ~ treatment + age + sex, data = df)
ph_test <- cox.zph(cox_model)
print(ph_test)

# 如果 treatment 违反 PH 假设
# 方案1: 分层 Cox (按 treatment 分层)
cox_stratified <- coxph(
  Surv(time, event) ~ age + sex + strata(treatment),
  data = df
)

# 方案2: 时依系数模型
cox_td <- coxph(
  Surv(time, event) ~ treatment + age + sex + tt(treatment),
  data = df,
  tt = function(x, t, ...) x * log(t)  # 时间交互
)

# 方案3: 分段 Cox (不同时间段不同 HR)
df$time_period <- cut(df$time, breaks = c(0, 12, 24, Inf),
                      labels = c("0-12m", "12-24m", ">24m"))
cox_piecewise <- coxph(
  Surv(time, event) ~ treatment * time_period + age + sex,
  data = df
)
```

### Python — 分层 Cox

```python
from lifelines import CoxPHFitter
from lifelines.statistics import proportional_hazard_test

# 检验 PH 假设
cph = CoxPHFitter()
cph.fit(df, duration_col='time', event_col='event',
        formula='treatment + age + sex')

# Schoenfeld 残差检验
results = proportional_hazard_test(cph, df, time_transform='rank')
print(results.print_summary())

# 如果违反 PH 假设，使用分层
# 按 treatment 分层分析
for group in df['treatment'].unique():
    df_group = df[df['treatment'] == group]
    cph_group = CoxPHFitter()
    cph_group.fit(df_group, duration_col='time', event_col='event',
                  formula='age + sex')
    print(f"\nGroup {group}:")
    print(cph_group.summary)
```

---

## 引用关系

| 文件 | 用途 |
|------|------|
| [`error_patterns.md`](error_patterns.md) | 错误分类与简要诊断规则（S1-S4, D1-D3, E1-E3, C1-C3） |
| [`auto_fix_suggestions.py`](auto_fix_suggestions.py) | Python 自动修复建议生成器 |
| [`auto_fix_suggestions.R`](auto_fix_suggestions.R) | R 自动修复建议生成器 |
| **本文件** | 完整可执行代码修复示例（Firth/VIF/Cox PH） |
