# Ch52: 因果森林与异质性治疗效应 (Heterogeneous Treatment Effects)

> **适用场景**: 个性化治疗、亚组发现、治疗效应异质性探索
> **核心方法**: Causal Forest、Meta-learners (S/T/X-learner)
> **参考文献**: Athey & Imbens (2016), Wager & Athey (2018)

---

## 1. 概述

异质性治疗效应 (HTE) 研究：不同患者对同一治疗的反应不同。传统亚组分析（交互项检验）统计效能低且需预设亚组。机器学习方法可数据驱动地发现 HTE。

**核心概念**:
- **CATE**: Conditional Average Treatment Effect, E[Y(1)-Y(0) | X=x]
- **ATE**: Average Treatment Effect, E[Y(1)-Y(0)]
- **ITE/CATE**: 个体/条件平均治疗效应

## 2. 因果森林 (Causal Forest)

### 2.1 原理

因果森林是广义随机森林在因果推断中的应用：
- 每棵树在分裂时优化治疗效应异质性
- 使用 honest estimation（训练集和估计集分离）
- 提供点估计和置信区间

### 2.2 R 实现

```r
# R: grf 包
library(grf)

# 数据准备
X <- model.matrix(~ age + sex + bmi + baseline_score - 1, data = df)
W <- df$treatment  # 0/1 治疗变量
Y <- df$outcome

# 训练因果森林
cf <- causal_forest(
  X = X, Y = Y, W = W,
  num.trees = 2000,
  honesty = TRUE,
  honesty.fraction = 0.5,
  min.node.size = 5,
  seed = 42
)

# CATE 预测
cate_pred <- predict(cf)$predictions

# 变量重要性
var_importance <- variable_importance(cf)
print(var_importance[order(-var_importance), ])

# 平均治疗效应
average_treatment_effect(cf, target.sample = "all")
average_treatment_effect(cf, target.sample = "treated")
average_treatment_effect(cf, target.sample = "control")

# 最佳线性投影（解释 CATE 变异）
blp <- best_linear_projection(cf, X = X)
summary(blp)
```

### 2.3 Python 实现

```python
# Python: econml 或 grf
from econml.dml import CausalForestDML
import numpy as np

# Causal Forest DML
cf = CausalForestDML(
    n_estimators=2000,
    min_samples_leaf=5,
    discrete_treatment=False,
    random_state=42
)

# 拟合
cf.fit(Y, T, X=X, W=W)

# CATE 预测
cate = cf.effect(X)

# 置信区间
cate_ci = cf.effect_interval(X, alpha=0.05)

# 变量重要性
feature_importances = cf.feature_importances_
```

## 3. Meta-learners

### 3.1 S-learner (Single)

```python
from econml.metalearners import SLearner
from sklearn.ensemble import RandomForestRegressor

slearner = SLearner(overall_model=RandomForestRegressor())
slearner.fit(Y, T, X=X)
cate_s = slearner.effect(X)
```

### 3.2 T-learner (Two)

```python
from econml.metalearners import TLearner

tlearner = TLearner(models=RandomForestRegressor())
tlearner.fit(Y, T, X=X)
cate_t = tlearner.effect(X)
```

### 3.3 X-learner

```python
from econml.metalearners import XLearner

xlearner = XLearner(models=RandomForestRegressor())
xlearner.fit(Y, T, X=X)
cate_x = xlearner.effect(X)
```

### 3.4 Learner 选择指南

| Learner | 适用场景 | 优点 | 缺点 |
|---------|---------|------|------|
| S-learner | 治疗效应小 | 简单 | 可能忽略交互 |
| T-learner | 治疗组/对照组差异大 | 灵活 | 小样本不稳定 |
| X-learner | 样本量不平衡 | 利用倾向性评分 | 较复杂 |
| R-learner | 高维数据 | 正则化 | 实现复杂 |

## 4. 亚组发现

```r
# R: causalTree + honest estimation
library(causalTree)

# 训练因果树
ct <- causalTree(
  outcome ~ age + sex + bmi + baseline_score,
  data = df_train,
  treatment = df_train$treatment,
  split.Rule = "CT",
  cv.option = "CT",
  split.Honest = TRUE,
  cv.Honest = TRUE,
  minsize = 20
)

# 可视化
plot(ct, uniform = TRUE)
text(ct, use.n = TRUE)
```

## 5. 临床应用流程

```
1. 定义因果问题
   └── 治疗效应在哪些患者中最强/最弱？

2. 数据准备
   ├── 协变量选择（基于 DAG 和临床知识）
   ├── 处理缺失值
   └── 标准化

3. 模型训练
   ├── 因果森林（首选）
   ├── Meta-learners（辅助）
   └── 交叉验证选择超参数

4. 结果评估
   ├── CATE 分布（直方图/箱线图）
   ├── CATE 置信区间覆盖率
   ├── Qini 曲线 / AUUC
   └── 与已知亚组的一致性

5. 临床解读
   ├── 最佳线性投影（哪些变量驱动 HTE）
   ├── 高/低获益亚组特征描述
   └── 与领域知识交叉验证

6. 敏感性分析
   ├── 不同超参数的结果稳定性
   ├── 不同 learner 的结果一致性
   └── 未测量混杂的影响（E-value）
```

## 6. 结果报告

```
── 异质性治疗效应分析结果 ──

方法: 因果森林 (Causal Forest, grf 1.2.0)
树数: 2000, honesty=TRUE, min.node.size=5

ATE: {值} (95% CI: {下限}, {上限})

CATE 分布:
- 均值: {值}
- 标准差: {值}
- 25th percentile: {值} (低获益组)
- 75th percentile: {值} (高获益组)

驱动 HTE 的关键变量:
1. {变量名}: 重要性 {值}
2. {变量名}: 重要性 {值}
3. {变量名}: 重要性 {值}

高获益亚组特征: {描述}
低获益亚组特征: {描述}

注意: HTE 发现为探索性，需独立数据集验证。
```

## 7. 注意事项

| 陷阱 | 说明 | 正确做法 |
|------|------|---------|
| 因果假设违反 | 无未测量混杂 | DAG + 敏感性分析 |
| 过拟合 | CATE 估计不稳定 | 交叉验证 + honest estimation |
| 样本量不足 | HTE 检测效能低 | 参考 power analysis |
| 忽略不确定性 | 仅看点估计 | 报告 CI + Qini CI |
| 直接翻译为政策 | 发现≠验证 | 需 RCT 验证亚组效应 |

## 8. 参考文献

1. Wager S, Athey S. Estimation and inference of heterogeneous treatment effects using random forests. JASA. 2018;113(523):1228-1242.
2. Athey S, Imbens G. Recursive partitioning for heterogeneous causal effects. PNAS. 2016;113(27):7353-7360.
3. Künzel SR, Sekhon JS, Bickel PJ, Yu B. Metalearners for estimating heterogeneous treatment effects using machine learning. PNAS. 2019;116(10):4156-4165.
4. Nie X, Wager S. Quasi-oracle estimation of heterogeneous treatment effects. Biometrika. 2021;108(2):299-319.
5. Athey S, Tibshirani J, Wager S. Generalized random forests. Ann Stat. 2019;47(2):1148-1178.
