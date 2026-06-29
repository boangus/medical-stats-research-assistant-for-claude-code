# Ch49: 等价性检验 (Equivalence Testing)

> **适用场景**: 验证两种处理（药物/器械/方案）的疗效差异在临床可接受的等价界值内
> **核心方法**: TOST (Two One-Sided Tests)
> **参考文献**: Schuirmann (1987), Wellek (2010), ICH E10

---

## 1. 概述

等价性检验旨在证明两种处理的差异**不超过**预先设定的临床等价界值 Δ，而非传统假设检验的"差异为零"。

**与非劣效性检验的区别**:

| 维度 | 等价性检验 | 非劣效性检验 |
|------|-----------|-------------|
| 假设 | H₀: |μ₁-μ₂| ≥ Δ vs H₁: |μ₁-μ₂| < Δ | H₀: μ₁-μ₂ ≤ -Δ vs H₁: μ₁-μ₂ > -Δ |
| 方向 | 双侧 | 单侧 |
| 结论 | 两处理"足够相似" | 新处理"不差于"对照 |
| 典型应用 | 仿制药生物等效性、不同剂型对比 | 新药 vs 标准治疗 |

## 2. TOST 方法

### 2.1 原理

TOST 将等价性检验拆分为两个单侧检验：
- H₀₁: μ₁-μ₂ ≤ -Δ → 拒绝则证明差异 > -Δ
- H₀₂: μ₁-μ₂ ≥ Δ → 拒绝则证明差异 < Δ

**当两个单侧检验均拒绝时**，结论为等价。

### 2.2 等价界值 Δ 的选择

| 方法 | 说明 | 适用场景 |
|------|------|---------|
| 临床判断法 | 基于最小临床重要差异 (MCID) | RCT、临床结局 |
| 参照法 | 基于阳性对照已知效应的百分比 (如 50%) | 仿制药生物等效性 |
| 统计法 | 基于参考治疗的 CI 下限 | 辅助方法 |
| 监管标准 | FDA: 80-125% (生物等效性) | 药代动力学参数 |

**⚠️ IRON RULE**: Δ 必须在试验开始前预先设定，不得基于观察数据调整。

## 3. R 实现

```r
# 使用 TOSTER 包
library(TOSTER)

# 连续结局：独立样本 t 检验
TOSTtwo(m1 = 10.2, m2 = 10.5, sd1 = 2.1, sd2 = 2.3,
        n1 = 100, n2 = 100, low_eqbound_d = -0.5, high_eqbound_d = 0.5,
        alpha = 0.05, var.equal = TRUE)

# 效应量版本（Cohen's d）
TOSTtwo(m1 = 10.2, m2 = 10.5, sd1 = 2.1, sd2 = 2.3,
        n1 = 100, n2 = 100, low_eqbound_d = -0.5, high_eqbound_d = 0.5)

# 配对样本
TOSTpaired(n = 50, m1 = 10.2, m2 = 10.5, sd1 = 2.1, sd2 = 2.3,
           r12 = 0.6, low_eqbound_dz = -0.5, high_eqbound_dz = 0.5)

# 生物等效性（对数转换后）
# 使用 log-transformed AUC/Cmax 数据
TOSTone(m = 0.05, mu = 0, sd = 0.3, n = 24,
        low_eqbound = -0.223, high_eqbound = 0.223, alpha = 0.05)
```

## 4. Python 实现

```python
import numpy as np
from scipy import stats

def tost_two_sample(x1, x2, delta, alpha=0.05):
    """
    Two One-Sided Tests (TOST) for two independent samples.
    
    Parameters
    ----------
    x1, x2 : array-like
        Sample data for groups 1 and 2
    delta : float
        Equivalence margin (symmetric)
    alpha : float
        Significance level (default 0.05)
    
    Returns
    -------
    dict with test statistics and p-values
    """
    n1, n2 = len(x1), len(x2)
    m1, m2 = np.mean(x1), np.mean(x2)
    s1, s2 = np.std(x1, ddof=1), np.std(x2, ddof=1)
    
    # Pooled SE
    se = np.sqrt(s1**2/n1 + s2**2/n2)
    df = (s1**2/n1 + s2**2/n2)**2 / ((s1**2/n1)**2/(n1-1) + (s2**2/n2)**2/(n2-1))
    
    diff = m1 - m2
    
    # TOST: two one-sided tests
    t1 = (diff - (-delta)) / se  # H0: diff <= -delta
    t2 = (diff - delta) / se      # H0: diff >= delta
    
    p1 = 1 - stats.t.cdf(t1, df)  # p-value for lower bound
    p2 = stats.t.cdf(t2, df)       # p-value for upper bound
    
    p_tost = max(p1, p2)  # TOST p-value is the larger of the two
    
    # 90% CI (for equivalence assessment)
    ci_low = diff - stats.t.ppf(1-alpha, df) * se
    ci_high = diff + stats.t.ppf(1-alpha, df) * se
    
    equivalent = p_tost < alpha
    
    return {
        "difference": diff,
        "t1": t1, "p1": p1,
        "t2": t2, "p2": p2,
        "p_tost": p_tost,
        "ci_90": (ci_low, ci_high),
        "equivalent": equivalent,
        "message": "等价" if equivalent else "未能证明等价"
    }

# 示例
np.random.seed(42)
group1 = np.random.normal(10.2, 2.1, 100)
group2 = np.random.normal(10.5, 2.3, 100)
result = tost_two_sample(group1, group2, delta=1.0)
print(f"差异: {result['difference']:.3f}")
print(f"TOST p值: {result['p_tost']:.4f}")
print(f"90% CI: ({result['ci_90'][0]:.3f}, {result['ci_90'][1]:.3f})")
print(f"结论: {result['message']}")
```

## 5. 样本量计算

```r
# R: PowerTOST 包
library(PowerTOST)

# 生物等效性样本量
sampleN.TOST(CV = 0.3, theta0 = 1.0, theta1 = 0.8, theta2 = 1.25,
             targetpower = 0.8, alpha = 0.05)

# 一般等价性检验样本量
powerTOST(CV = 0.3, theta0 = 0, theta1 = -0.5, theta2 = 0.5,
          n = 100, alpha = 0.05)
```

```python
# Python 样本量计算
import numpy as np
from scipy import stats

def sample_size_equivalence(delta, sd, alpha=0.05, power=0.8, k=1):
    """
    样本量计算（等价性检验，两组 1:1 分配）
    
    Parameters
    ----------
    delta : float
        等价界值
    sd : float
        总体标准差
    alpha : float
        显著性水平
    power : float
        检验效能
    k : float
        分配比例 n2/n1
    """
    z_alpha = stats.norm.ppf(1 - alpha)
    z_beta = stats.norm.ppf(power)
    
    n1 = ((1 + 1/k) * sd**2 * (z_alpha + z_beta)**2) / delta**2
    return int(np.ceil(n1))

n = sample_size_equivalence(delta=0.5, sd=2.0, alpha=0.05, power=0.8)
print(f"每组所需样本量: {n}")
```

## 6. 结果解释

**等价性检验结果报告模板**:

```
使用双单侧检验 (TOST) 评估两种处理的等价性。
等价界值预先设定为 Δ = {值}（基于{依据}）。

结果：
- 均值差: {值} (90% CI: {下限}, {上限})
- TOST p值: {值}
- 结论: {等价/未能证明等价}

等价界值与 90% CI 的关系：
- 若 90% CI 完全在 [-Δ, +Δ] 内 → 等价
- 若 90% CI 部分超出 → 未能证明等价
- 若 90% CI 完全在界值外 → 证明不等价
```

## 7. 注意事项

| 常见陷阱 | 说明 | 正确做法 |
|---------|------|---------|
| 事后设定等价界值 | 基于观察到的 CI 选 Δ | 试验前基于临床意义设定 |
| 与"不显著"混淆 | p>0.05 不等于等价 | 必须使用 TOST，不能用传统检验 |
| 忽略方向性 | 等价性是双侧的 | 使用 90% CI（对应 α=0.05 双侧） |
| 样本量不足 | 效能不够导致假阴性 | 提前计算等价性检验的样本量 |
| 生物等效性误解 | 80-125% 是特定参数标准 | 不适用于临床结局指标 |

## 8. 参考文献

1. Schuirmann DJ. A comparison of the two one-sided tests procedure and the power approach for assessing the equivalence of average bioavailability. J Pharmacokinet Biopharm. 1987;15(6):657-680.
2. Wellek S. Testing Statistical Hypotheses of Equivalence and Noninferiority. 2nd ed. Chapman & Hall/CRC; 2010.
3. ICH E10: Choice of Control Group and Related Issues in Clinical Trials. 2000.
4. Lakens D. Equivalence tests: A practical primer for t tests, correlations, and meta-analyses. Soc Psychol Personal Sci. 2017;8(4):355-362.
5. FDA Guidance: Statistical Approaches to Establishing Bioequivalence. 2001.
