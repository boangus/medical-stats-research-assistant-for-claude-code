# GRADE 证据质量评估指南

> Grading of Recommendations, Assessment, Development and Evaluations

## 概述

GRADE 是一种系统评估证据质量和推荐强度的方法学框架，被 WHO、Cochrane、NICE 等国际组织广泛采用。

## 证据质量等级

| 等级 | 定义 | 符号 |
|------|------|------|
| 高 | 非常确信真实效应接近估计效应 | ⊕⊕⊕⊕ |
| 中 | 对估计效应有中等信心，真实效应可能接近估计效应，也可能差别很大 | ⊕⊕⊕◯ |
| 低 | 对估计效应信心有限，真实效应可能与估计效应差别很大 | ⊕⊕◯◯ |
| 极低 | 对估计效应几乎没有信心，真实效应可能与估计效应完全不同 | ⊕◯◯◯ |

## 降级因素 (5 个)

### 1. 偏倚风险 (Risk of Bias)

- 限制: 纳入研究存在严重的方法学缺陷
- 评估: 使用 RoB 2 / ROBINS-I / NOS 等工具
- 降级: 多数研究存在高偏倚风险 → 降 1-2 级

### 2. 不一致性 (Inconsistency)

- 限制: 研究结果间存在显著异质性
- 评估: I² 统计、Q 检验、预测区间
- 降级: I²>60% 且无合理解释 → 降 1 级

### 3. 间接性 (Indirectness)

- 限制: 证据不能直接回答研究问题
- 评估: PICO 各要素的匹配程度
- 降级: 人群/干预/结局存在间接性 → 降 1 级

### 4. 不精确性 (Imprecision)

- 限制: 估计效应的置信区间过宽
- 评估: 95% CI 是否跨越临床决策阈值
- 降级: 信息不充分 (optimal information size 未达到) → 降 1 级

### 5. 发表偏倚 (Publication Bias)

- 限制: 存在小样本研究效应或漏斗图不对称
- 评估: 漏斗图、Egger/Begg 检验
- 降级: 存在发表偏倚的证据 → 降 1 级

## 升级因素 (3 个)

### 1. 大效应量

- 条件: 效应量很大 (RR>2 或 RR<0.5)
- 升级: 升 1 级 (效应量 2-5) 或 2 级 (效应量 >5)

### 2. 剂量-反应梯度

- 条件: 存在明确的剂量-反应关系
- 升级: 升 1 级

### 3. 残余混杂方向

- 条件: 所有可能的混杂因素会降低效应量
- 升级: 升 1 级

## GRADE 评估流程

```
1. 确定结局 (每个结局单独评估)
   ↓
2. 确定起始质量 (RCT=高, 观察性=低)
   ↓
3. 评估降级因素 (5 个)
   ↓
4. 评估升级因素 (3 个)
   ↓
5. 确定最终质量等级
   ↓
6. 生成证据概要表 (Summary of Findings)
```

## 参考文献

- Guyatt GH, Oxman AD, Vist GE, et al. GRADE: an emerging consensus on rating quality of evidence and strength of recommendations. BMJ. 2008;336:924-926.
- Schünemann HJ, Brożek J, Guyatt G, Oxman AD, eds. GRADE handbook. Updated October 2013.
