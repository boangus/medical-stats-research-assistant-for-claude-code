# Ch55: 自适应试验设计进阶 (Advanced Adaptive Designs)

> **适用场景**: 早期临床试验剂量探索、无缝 II/III 期设计、平台试验
> **核心方法**: BOIN, CRM, mTPI, Response-adaptive randomization
> **参考文献**: FDA Guidance on Adaptive Designs (2019), Berry et al. (2010)

---

## 1. 概述

自适应设计允许在试验过程中基于累积数据修改设计要素，同时控制 I 类错误率。进阶主题包括：

- **自适应随机化**: 根据累积结果调整分配比例
- **剂量探索**: BOIN, CRM, mTPI 设计
- **无缝设计**: Phase II/III 合并
- **平台试验**: 多干预共享对照

## 2. 剂量探索设计

### 2.1 BOIN (Bayesian Optimal Interval)

```r
# R: BOIN 包
library(BOIN)

# 确定 MTD
besign <- get.boundary(target = 0.3, ncohort = 10, cohortsize = 3)
# n.earlystop: 最大样本量
# boundary: dose escalation/de-escalation boundary

# 模拟 BOIN 设计
sim.boin <- get.oc(target = 0.3, p.true = c(0.05, 0.15, 0.30, 0.45, 0.60),
                   ncohort = 10, cohortsize = 3, n.earlystop = 30,
                   startdose = 1, ntrial = 1000)
```

### 2.2 CRM (Continual Reassessment Method)

```r
# R: dfcrm 包
library(dfcrm)

# 先验毒性概率
prior <- c(0.05, 0.10, 0.20, 0.35, 0.50, 0.65)

# CRM 设计
crm_fit <- crm(prior = prior, target = 0.30, tox = c(0, 1, 0, 0, 1),
               level = c(1, 2, 3, 4, 5), model = "empiric", method = "bayes")
```

### 2.3 mTPI (modified Toxicity Probability Interval)

```r
# R: dfcrm 或手动实现
# mTPI 使用等效区间方法
target <- 0.30
epsilon1 <- 0.05  # 下界
epsilon2 <- 0.05  # 上界

# 决策规则
# 若 P(tox < target-ε1 | data) > 0.5 → 升级
# 若 P(tox > target+ε2 | data) > 0.5 → 降级
# 否则 → 保持当前剂量
```

## 3. 自适应随机化

### 3.1 响应适应性随机化 (RAR)

```python
import numpy as np

def response_adaptive_randomization(success_counts, total_counts, method='thompson'):
    """
    响应适应性随机化
    
    Parameters
    ----------
    success_counts : array, 各臂成功数
    total_counts : array, 各臂总人数
    method : str, 'thompson' 或 'urn'
    """
    if method == 'thompson':
        # Thompson Sampling (Beta-Binomial)
        probs = []
        for s, n in zip(success_counts, total_counts):
            # Beta(s+1, n-s+1) 后验
            sample = np.random.beta(s + 1, n - s + 1)
            probs.append(sample)
        probs = np.array(probs)
        return probs / probs.sum()
    
    elif method == 'urn':
        # Drop-the-loser
        # 简化版：失败越多，分配越少
        failure_counts = total_counts - success_counts
        weights = 1.0 / (failure_counts + 1)
        return weights / weights.sum()

# 示例
success = np.array([15, 20, 10])
total = np.array([30, 30, 30])
alloc_probs = response_adaptive_randomization(success, total, method='thompson')
print(f"分配概率: {alloc_probs}")
```

## 4. 无缝 Phase II/III 设计

```
传统设计: Phase II → 中断 → Phase III
无缝设计: Phase II → 直接进入 Phase III（无需重新入组）

优势:
- 节省时间（减少 1-2 年）
- 利用 Phase II 的患者数据
- 减少总样本量

设计要素:
1. Phase II 阶段：剂量选择或 futility 分析
2. 适应性决策：基于 Phase II 数据选择剂量/继续/停止
3. Phase III 阶段：确认性分析
4. α 分配：使用 α 消耗函数控制 I 类错误
```

## 5. 平台试验

```
平台试验特征:
- 多个干预同时评估
- 共享对照组（减少总样本量）
- 可动态加入/移除干预臂
- 统一基础设施和数据监查

例子:
- I-SPY 2 (乳腺癌)
- RECOVERY (COVID-19)
- REMAP-CAP (重症肺炎)

统计考虑:
- 共享对照 vs 专属对照
- 跨时期混杂（时间趋势）
- 多重比较控制
```

## 6. Alpha 消耗函数

```r
# R: rpact 或 ldbounds

# Lan-DeMets alpha 消耗函数
library(ldbounds)

# O'Brien-Fleming 型
obf <- function(t) 2 * (1 - pnorm(qnorm(1 - 0.025/2) / sqrt(t)))

# Pocock 型
pocock <- function(t) 0.05 * log(1 + (exp(1) - 1) * t)

# 在各分析时点的 alpha 分配
time_points <- c(0.5, 0.75, 1.0)
alpha_obf <- c(obf(0.5), obf(0.75) - obf(0.5), obf(1.0) - obf(0.75))
alpha_pocock <- c(pocock(0.5), pocock(0.75) - pocock(0.5), pocock(1.0) - pocock(0.75))
```

## 7. FDA 指南要点

**FDA Guidance on Adaptive Designs (2019)** 关键要求：

| 要素 | 要求 |
|------|------|
| I 类错误控制 | 必须证明自适应设计控制 I 类错误率在 α 水平 |
| 操作特征 | 提供模拟研究展示设计的操作特性 |
| 适应性规则 | 在方案中详细描述所有适应性规则 |
| 独立数据监查 | 建议建立 IDMC |
| 统计方法 | 提供自适应设计的统计方法学依据 |
| 代码可审计 | 提供模拟代码供 FDA 审查 |

## 8. 参考文献

1. FDA. Adaptive Designs for Clinical Trials of Drugs and Biologics: Guidance for Industry. 2019.
2. Berry SM, Carlin BP, Lee JJ, Muller P. Bayesian Adaptive Methods for Clinical Trials. Chapman & Hall/CRC; 2010.
3. Liu Y, Yuan Y. Bayesian optimal interval designs for phase I clinical trials. J R Stat Soc C. 2015;64(3):507-523.
4. O'Quigley J, Pepe M, Fisher L. Continual reassessment method: a practical design for phase 1 clinical trials in cancer. Biometrics. 1990;46(1):33-48.
5. Park JW, Liu MC, Yee D, et al. Adaptive randomization of neratinib in early breast cancer. N Engl J Med. 2016;375(1):11-22.
6. REMAP-CAP Investigators. Interleukin-6 receptor antagonists in critically ill patients with Covid-19. N Engl J Med. 2021;384(16):1491-1502.
