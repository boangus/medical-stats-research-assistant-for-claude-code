# RoB 2 风险偏倚评估清单

> 适用于随机对照试验（RCT）的偏倚风险评估
> 基于 **RoB 2 工具**（Sterne et al., BMJ 2019; Cochrane 2019-08-22 最终版）
> 参考: [riskofbias.info](https://www.riskofbias.info/welcome/rob-2-0-tool/current-version-of-rob-2)
> 更新日期: 2026-06-15

> **IRON RULES**:
> - 本清单严格对齐 Cochrane RoB 2 官方 5 域结构，不得自创域编号
> - 每个域含信号问题（signaling questions）→ 域级判断 → 整体判断
> - 判断等级: **Low** / **Some concerns** / **High**
> - 适用于: 个体随机平行组试验；集群随机和交叉试验需用专用版本
> - 参考: src/shared/reporting-guidelines/CONSORT_checklist.md（报告规范）；本清单（偏倚评估）互补使用

---

## 整体判断算法

```
整体判断 = MAX(各域判断)
- 5 域均 Low → 整体 Low
- 任一域 Some concerns → 整体 Some concerns
- 任一域 High → 整体 High
```

---

## Domain 1: 随机化过程产生的偏倚 (Bias arising from the randomization process)

### 信号问题

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 1.1 | 是否有充分证据表明分配序列的产生使用了足够随机的方法？ | □ |
| 1.2 | 分配隐藏是否充分，确保分配序列在入组前不可预测？ | □ |
| 1.3 | 是否有足够的证据表明分配序列的产生和隐藏方法未被破坏（如封存信封被篡改）？ | □ |

### 判断逻辑

```
IF 1.1=是 AND 1.2=是 AND 1.3=是 → Low
IF 1.1=否 OR 1.2=否 OR (1.1=无信息 AND 1.2=无信息) → High
ELSE → Some concerns
```

### 关键偏倚风险
- 分配隐藏不足 → 选择偏倚（高估效应 20-40%）
- 序列生成可预测（如按入院日期交替）→ 破坏随机性

---

## Domain 2: 偏离预期干预措施产生的偏倚 (Bias due to deviations from intended interventions)

### 信号问题（评估效果比较时）

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 2.1 | 试验参与者和提供干预者是否对分配的干预措施设盲？ | □ |
| 2.2 | 是否有证据表明试验期间盲法被破坏？ | □ |
| 2.3 | 是否有适当的分析来调整偏离预期干预措施的影响？（如 per-protocol 分析含工具变量） | □ |

### 判断逻辑

```
IF 2.1=是 AND 2.2=否 AND 2.3=是 → Low
IF 2.1=否 AND 存在偏离预期干预措施 AND 未调整 → High
ELSE → Some concerns
```

### 关键偏倚风险
- 未设盲（开放标签试验）→ 实施偏倚 + 测量偏倚
- 高脱落率（>20%）且未用 ITT → 偏倚方向不确定

---

## Domain 3: 缺失结果数据产生的偏倚 (Bias due to missing outcome data)

### 信号问题

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 3.1 | 结果数据对所有（或几乎所有）随机化的参与者是否可用？ | □ |
| 3.2 | 缺失结果数据是否有可能与真实结果相关？（如因不良事件脱落） | □ |
| 3.3 | 缺失结果数据的比例、原因或模式是否有可能导致偏差？ | □ |

### 判断逻辑

```
IF 3.1=是 AND (3.2=否 OR 合理填补方法) → Low
IF 缺失>20% OR 缺失与真实结果相关且未处理 → High
ELSE → Some concerns
```

### 关键阈值
- 缺失 <5%: 通常 Low risk
- 缺失 5-20%: 需评估缺失机制
- 缺失 >20%: 通常 High risk（除非有强证据支持 MAR）

---

## Domain 4: 结果测量产生的偏倚 (Bias in measurement of the outcome)

### 信号问题

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 4.1 | 结果评估者是否对分配的干预措施设盲？ | □ |
| 4.2 | 如果未设盲，结果评估方法是否可能受到干预知识的影响？ | □ |
| 4.3 | 结果测量方法在各组间是否相同（除了干预措施）？ | □ |

### 判断逻辑

```
IF 4.1=是 AND 4.3=是 → Low
IF 4.1=否 AND 4.2=是 → High
ELSE → Some concerns
```

### 特殊情况
- 客观终点（全因死亡）→ 即使未设盲通常 Low
- 主观终点（疼痛评分、生活质量）→ 设盲至关重要

---

## Domain 5: 选择性报告结果产生的偏倚 (Bias in selection of the reported result)

### 信号问题

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 5.1 | 试验分析是否按照预先注册的分析计划执行？ | □ |
| 5.2 | 是否有证据表明研究者在多个结果中选择了最有利的结果报告？ | □ |
| 5.3 | 是否有证据表明研究者在多个时间点中选择了最有利的时间点？ | □ |

### 判断逻辑

```
IF 5.1=是 AND 5.2=否 AND 5.3=否 → Low
IF 5.2=是 OR 5.3=是 → High
ELSE → Some concerns
```

### 检测方法
- 对照试验注册号（ClinicalTrials.gov / ChiCTR）
- 检查分析计划 vs 实际报告的一致性
- 检查亚组分析是否为事后选择

---

## 整体判断汇总表

| 域 | 判断 | 理由 |
|----|------|------|
| D1 随机化 | □ Low / □ Some / □ High | |
| D2 偏离干预 | □ Low / □ Some / □ High | |
| D3 缺失数据 | □ Low / □ Some / □ High | |
| D4 结果测量 | □ Low / □ Some / □ High | |
| D5 选择性报告 | □ Low / □ Some / □ High | |
| **整体** | □ Low / □ Some / □ High | |

---

## 与 CONSORT 2025 的互补关系

| 维度 | CONSORT 2025（报告规范） | RoB 2（偏倚评估） |
|------|--------------------------|-------------------|
| 目的 | 研究是否报告了所有必要信息 | 研究结果是否可能被偏倚扭曲 |
| 时机 | 撰写/审稿时 | 系统综述/Meta分析时 |
| 判断 | 符合/不符合报告条目 | Low/Some/High 风险 |
| 对应 | Item 23（随机化序列）→ D1 | Item 25（盲法）→ D2+D4 |

---

## 参考文献

1. Sterne JAC, Savović J, Page MJ, et al. RoB 2: a revised tool for assessing risk of bias in randomised trials. BMJ. 2019;366:l4898.
2. Cochrane Handbook for Systematic Reviews of Interventions, Chapter 8: Assessing risk of bias in a randomized trial.
3. Higgins JPT, Thomas J, Chandler J, et al. (editors). Cochrane Handbook for Systematic Reviews of Interventions version 6.4 (updated August 2023).
