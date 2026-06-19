# 倾向性评分

**作者**: Jason S. Haukoos, Roger J. Lewis | **主译**: 龙宇琴

---

本章讨论了在随机对照研究不可行时，使用倾向性评分校正偏倚的方法。

## 为什么要使用倾向性评分？

影响临床医生选择治疗方式的因素很多。常规临床实践中，使用一种治疗策略的患者往往与使用另外一种的患者基线特征不同，这将导致患者基线特征影响治疗决策选择和患者结局，即混杂因素（常被称为适应证混杂因素）。如果来源于临床实践的观察性研究数据用于比较患者不同治疗策略的优劣，那么观察到的差异可能同时包括了患者基线特征的差异及治疗选择的差异。

随机对照研究是评价一种干预策略是否有效的最好方式，因其随机化使两组患者的基线特征相同。在观察性研究中，随机化无法实施，因此研究者只能通过校正两组间的差异来分析不同治疗策略的结局。倾向性评分可用于减少偏倚，使研究者在分析非随机观察性研究时，尽可能减少混杂因素对结局影响。

## 倾向性评分的定义

倾向性评分即患者接受治疗的可能性，可能受到患者基线特征、临床医生及临床环境的影响。这一可能性可以用多变量统计模型（如 logistic 回归）来估计（治疗策略作为结局变量，患者的基线特征、临床医生和临床特征作为预测因子）。研究者利用该模型预测每一例患者接受某种治疗的可能性。

## 四种应用方式

### 1. 匹配（最常用）
将倾向性评分接近或相同的患者配对。统计学分析基于配对样本，可近似认为两组间具备随机对照研究的样本特征（即可比性）。

### 2. 分层
依据患者的倾向性评分将患者分到不同的层中。大部分研究将患者分为 5 层。目标治疗与结局之间的关系在每一层内分析或最终将所有的结果综合分析。

### 3. 协变量调整
倾向性评分模型建立后，新建一个多变量模型（结局作为结局，治疗策略及倾向性评分作为预测因子），从而在估计治疗效应的同时校正混杂因素。

### 4. 逆处理概率加权（IPTW）
利用倾向性评分为每一个样本计算统计学权重，建立一个虚拟样本。在这个虚拟样本中潜在混杂因素的分布与暴露因素无关，从而使无偏倚地分析治疗和结局的关系成为可能。

## 关键要点

1. 倾向性评分只能控制已测量的混杂因素
2. 匹配后的平衡性必须检查（标准化差异 <0.1 为佳）
3. 倾向性评分模型的质量取决于预测因子的选择
4. 样本量较大的研究更适合使用倾向性评分方法
5. 敏感性分析（如 E 值）应作为倾向性评分分析的补充

## 局限与注意事项

- 不能控制未测量的混杂因素
- 在样本量小或治疗组/对照组严重不平衡时效果不佳
- 倾向性评分模型的正确设定（包括交互项和非线性项）至关重要
- 倾向性评分不代表因果关系，仅是混杂控制的一种工具

## 倾向性评分模型诊断

### 模型设定检验

倾向性评分模型的质量直接影响因果推断的有效性。模型设定不当会导致残余混杂。

**必须检查的指标**：
1. **C-statistic（AUC）**：PS 模型的区分度。一般 0.7-0.8 为佳；>0.9 可能意味着分离（separation）
2. **校准曲线**：预测概率与实际治疗比例的一致性
3. ** Hosmer-Lemeshow 检验**：分层校准度（p>0.05 为佳）

### 平衡性诊断

匹配/加权后必须评估协变量平衡：

| 指标 | 阈值 | 说明 |
|------|------|------|
| 标准化均值差 (SMD) | <0.1 | 所有协变量均应满足 |
| 方差比 (VR) | 0.5-2.0 | 连续变量的方差比 |
| 重叠度 (Overlap) | 可视化 | PS 分布重叠区域 |

**Love Plot**：可视化匹配前后所有协变量的 SMD 变化，是最直观的平衡性诊断工具。

### 常见陷阱

1. **Positivity 违反**：PS 接近 0 或 1 的区域缺乏重叠 → 无法进行有效推断
2. **过度拟合**：PS 模型 AUC >0.95 → 可能存在分离，导致匹配失败
3. **忽略非线性**：PS 模型仅包含线性项 → 残余混杂
4. **匹配后重新评估**：匹配后必须重新检查协变量平衡，而非假设匹配即平衡

## MSRA 工具链

| 工具 | 用途 |
|------|------|
| `shared/causal-inference/psm_template.py` | PSM 匹配 + 平衡诊断 |
| `shared/causal-inference/overlapping_weighting_template.py` | OW/IPTW 加权 |
| `shared/templates/ps_diagnostics_template.R` | R 版 PS 诊断（Love plot + 重叠图） |
| `analysis-exec skill Phase 6.1` | 主分析 vs 敏感性一致性（已整合） |

## 参考文献

1. Rosenbaum PR, Rubin DB. The central role of the propensity score in observational studies for causal effects. Biometrika, 1983, 70(1): 41–55.
2. Austin PC. An introduction to propensity score methods for reducing the effects of confounding in observational studies. Multivariate Behav Res, 2011, 46(3): 399–424.
3. Austin PC. Balance diagnostics for comparing the distribution of baseline covariates between treatment groups in propensity-score matched samples. Stat Med, 2009, 28(25): 3083–3107.
4. Lee BK, Lessler J, Stuart EA. Improving propensity score weighting using machine learning. Stat Med, 2010, 29(3): 337–346.
5. Lunceford JK, Davidian M. Stratification and weighting via the propensity score in estimation of causal treatment effects. Stat Med, 2004, 23(19): 2937–2960.

---

*来源：方法学统计与方法指南 第35章*




