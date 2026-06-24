# Ch54: 多类别 ROC 与时间依赖 ROC (Advanced ROC Analysis)

> **适用场景**: 多分类诊断、生存分析中的预测准确性、竞争风险
> **核心方法**: 多类别 AUC、时间依赖 ROC、累积/dynamic AUC
> **参考文献**: Heagerty & Zheng (2005), Hand & Till (2001)

---

## 1. 概述

标准 ROC 分析仅适用于二分类结局。进阶场景包括：
- **多分类 ROC**: 3+ 类别的诊断准确性
- **时间依赖 ROC**: 生存数据中随时间变化的预测准确性
- **竞争风险 ROC**: 存在竞争事件时的预测评估

## 2. 多分类 ROC

### 2.1 One-vs-Rest (OvR) 方法

将 k 类问题拆分为 k 个二分类问题：

```python
from sklearn.preprocessing import label_binarize
from sklearn.metrics import roc_curve, auc
import numpy as np

# 假设有 3 个类别
classes = [0, 1, 2]
y_bin = label_binarize(y_true, classes=classes)

# 为每个类别计算 ROC
fpr = {}; tpr = {}; roc_auc = {}
for i, cls in enumerate(classes):
    fpr[cls], tpr[cls], _ = roc_curve(y_bin[:, i], y_score[:, i])
    roc_auc[cls] = auc(fpr[cls], tpr[cls])

# 宏平均 AUC
macro_auc = np.mean(list(roc_auc.values()))

# 微平均 AUC
fpr["micro"], tpr["micro"], _ = roc_curve(y_bin.ravel(), y_score.ravel())
roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])
```

### 2.2 Hand-Till 方法 (推荐)

```python
# Hand & Till (2001) 多类别 AUC
from sklearn.metrics import roc_auc_score

# 直接计算
macro_auc = roc_auc_score(y_true, y_score, multi_class='ovr', average='macro')
weighted_auc = roc_auc_score(y_true, y_score, multi_class='ovr', average='weighted')

# Hand-Till 方法 (pairwise)
hand_till_auc = roc_auc_score(y_true, y_score, multi_class='ovo', average='macro')
```

```r
# R: pROC 多分类
library(pROC)

# 多分类 AUC
multiclass.roc(response = y_true, predictor = y_score)
# 或
multiclass.roc(y_true, y_score, algorithm = 3)  # Hand-Till
```

## 3. 时间依赖 ROC

### 3.1 概念

在生存分析中，疾病状态随时间变化。时间依赖 ROC 在每个时间点 t 评估：
- **灵敏度**: Pr(M > c | T ≤ t) — 在 t 之前发生事件且预测值高于阈值
- **特异度**: Pr(M ≤ c | T > t) — 在 t 之后仍存活且预测值低于阈值

### 3.2 R 实现

```r
# R: timeROC 包
library(timeROC)

# 时间依赖 ROC
roc_result <- timeROC(
  T = df$time, delta = df$event,
  marker = df$risk_score,
  cause = 1,
  times = c(1, 2, 3, 5),  # 预测时间点（年）
  iid = TRUE
)

# AUC(t)
roc_result$AUC

# 95% CI
confint(roc_result)

# 绘图
plot(roc_result, time = 1, col = "red", lwd = 2)
plot(roc_result, time = 3, col = "blue", lwd = 2, add = TRUE)
legend("bottomright", legend = c("1-year", "3-year"),
       col = c("red", "blue"), lwd = 2)

# 累积/dynamic AUC
roc_result$AUC  # 默认为 cumulative/dynamic
```

### 3.3 Python 实现

```python
# Python: lifelines + 自定义
from lifelines.utils import concordance_index

# C-index（时间依赖 AUC 的特例）
c_index = concordance_index(df['time'], -df['risk_score'], df['event'])

# 自定义时间依赖 AUC
import numpy as np
from sklearn.metrics import roc_auc_score

def time_dependent_auc(times, events, marker, t):
    """
    累积/dynamic 时间依赖 AUC
    """
    # 定义事件状态
    case = (times <= t) & (events == 1)  # t 前发生事件
    control = times > t                    # t 后仍存活
    
    if case.sum() < 5 or control.sum() < 5:
        return np.nan
    
    # 二分类化
    y_true = np.concatenate([np.ones(case.sum()), np.zeros(control.sum())])
    y_score = np.concatenate([marker[case], marker[control]])
    
    return roc_auc_score(y_true, y_score)

# 计算多个时间点的 AUC
for t in [1, 2, 3, 5]:
    auc_t = time_dependent_auc(df['time'].values, df['event'].values,
                                df['risk_score'].values, t)
    print(f"AUC({t}年): {auc_t:.3f}")
```

## 4. 竞争风险下的 ROC

```r
# R: timeROC (竞争风险)
library(timeROC)

# 竞争风险时间依赖 ROC
roc_cr <- timeROC(
  T = df$time, delta = df$status,  # status: 0=censored, 1=event, 2=competing
  marker = df$risk_score,
  cause = 1,  # 感兴趣的事件
  other_cause = 2,  # 竞争事件
  times = c(1, 2, 3, 5),
  iid = TRUE
)

roc_cr$AUC
```

## 5. ROC 比较

```r
# R: DeLong 检验
library(pROC)

roc1 <- roc(response = y_true, predictor = score1)
roc2 <- roc(response = y_true, predictor = score2)

# DeLong 检验比较两个 AUC
roc.test(roc1, roc2, method = "delong")
```

```python
# Python: DeLong 检验
from scipy import stats

def delong_test(y_true, y_score1, y_score2):
    """简化版 DeLong 检验"""
    from sklearn.metrics import roc_auc_score
    auc1 = roc_auc_score(y_true, y_score1)
    auc2 = roc_auc_score(y_true, y_score2)
    # 完整实现需要计算方差-协方差矩阵
    # 建议使用 R 的 pROC 包进行正式检验
    return auc1, auc2
```

## 6. 结果报告

```
── ROC 分析结果 ──

二分类 ROC:
- AUC: {值} (95% CI: {下限}, {上限})
- 最佳切点 (Youden): {值} (Se={值}, Sp={值})

时间依赖 ROC (累积/dynamic):
- AUC(1年): {值} (95% CI: {下限}, {上限})
- AUC(3年): {值} (95% CI: {下限}, {上限})
- AUC(5年): {值} (95% CI: {下限}, {上限})

多分类 ROC:
- 宏平均 AUC: {值}
- 微平均 AUC: {值}
- 各类别 AUC: {Class1: 值, Class2: 值, Class3: 值}
```

## 7. 参考文献

1. Heagerty PJ, Zheng Y. Survival model predictive accuracy and ROC curves. Biometrics. 2005;61(1):92-105.
2. Hand DJ, Till RJ. A simple generalisation of the area under the ROC curve for multiple class classification problems. Mach Learn. 2001;45(2):171-186.
3. Blanche P, Dartigues JF, Jacqmin-Gadda H. Estimating and comparing time-dependent areas under receiver operating characteristic curves for censored event times with competing risks. Stat Med. 2013;32(30):5381-5397.
4. DeLong ER, DeLong DM, Clarke-Pearson DL. Comparing the areas under two or more correlated receiver operating characteristic curves: a nonparametric approach. Biometrics. 1988;44(3):837-845.
5. Uno H, Cai T, Tian L, Wei LJ. Evaluating prediction rules for t-year survivors with censored regression models. JASA. 2007;102(478):527-537.
