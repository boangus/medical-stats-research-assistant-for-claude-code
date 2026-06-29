# ROBINS-I V2 风险偏倚评估清单

> 适用于非随机干预研究（NRSI）的偏倚风险评估
> 基于 **ROBINS-I V2 工具**（Sterne et al., BMJ 2016; Cochrane 更新版 2024）
> 参考: [riskofbias.info](https://www.riskofbias.info/welcome/robins-i-v2)
> 更新日期: 2026-06-15

> **IRON RULES**:
> - 本清单严格对齐 ROBINS-I V2 官方 7 域结构
> - 每个域含信号问题 → 域级判断 → 整体判断
> - 判断等级: **Low** / **Moderate** / **Serious** / **Critical** / **No information**
> - 适用于: 非随机干预研究（队列、病例对照、前后对比、中断时间序列等）
> - 暴露研究（非干预）请用 ROBINS-E（Bero et al., Environment International 2024）
> - 参考: src/shared/reporting-guidelines/STROBE_checklist.md（报告规范）；本清单（偏倚评估）互补使用

---

## 整体判断算法

```
整体判断 = MAX(各域判断)
- 若任一域为 Critical → 整体 Critical
- 若任一域为 Serious → 整体 Serious
- 依此类推，取最高风险等级
```

---

## 预设对照（target trial emulation）前提

ROBINS-I V2 要求评估者先定义一个**目标试验（target trial）**：
1. 确定研究问题（干预 A vs B 或干预 vs 无干预）
2. 确定目标人群
3. 确定干预分配方案
4. 确定随访起始点和结局

评估基于研究结果与目标试验结果的接近程度。

---

## Domain 1: 混杂产生的偏倚 (Bias due to confounding)

### 信号问题

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 1.1 | 是否测量了所有重要的混杂因素？ | □ |
| 1.2 | 对混杂因素的测量是否在正确的时间点（干预分配前）？ | □ |
| 1.3 | 混杂因素的定义和测量方法是否适当？ | □ |
| 1.4 | 分析中是否适当调整了所有重要的混杂因素？ | □ |
| 1.5 | 是否有未测量的重要混杂因素可能影响结果？ | □ |

### 判断逻辑

```
IF 所有重要混杂均已测量+调整 → Low/Moderate
IF 存在未测量的重要混杂 → Serious/Critical
IF 无法判断 → No information
```

### 关键偏倚风险
- 未调整年龄、性别等核心混杂 → 严重混杂偏倚
- 时间相关偏倚（immortal time bias）→ 需专用分析方法
- 使用不适当的调整方法（如仅用单变量筛选）→ 残余混杂

---

## Domain 2: 研究对象选择产生的偏倚 (Bias in selection of participants into the study)

### 信号问题

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 2.1 | 研究对象的纳入/排除标准是否合适？ | □ |
| 2.2 | 是否所有研究对象在干预分配前即满足入选条件？ | □ |
| 2.3 | 是否避免了根据干预后事件选择研究对象？ | □ |
| 2.4 | 各组的纳入/排除标准是否一致？ | □ |

### 判断逻辑

```
IF 标准一致 AND 干预前确定 AND 无干预后选择 → Low
IF 根据结局选择研究对象 → Critical
ELSE → Moderate/Serious
```

### 典型问题
- 依从者效应（healthy adherer bias）→ 选择偏倚
- 新用户设计 vs 现有用户设计 → 影响偏倚方向

---

## Domain 3: 干预分类产生的偏倚 (Bias in classification of interventions)

### 信号问题

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 3.1 | 干预的定义和分类是否明确？ | □ |
| 3.2 | 干预分类是否在结果测量前确定？ | □ |
| 3.3 | 干预分类方法在各组间是否一致？ | □ |
| 3.4 | 是否有可能因结果知识影响干预分类？ | □ |

### 判断逻辑

```
IF 定义明确+分类前确定+方法一致 → Low
IF 分类依赖结果知识 → Serious/Critical
ELSE → Moderate
```

---

## Domain 4: 偏离预期干预措施产生的偏倚 (Bias due to deviations from intended interventions)

### 信号问题

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 4.1 | 是否有足够的参与者接受了分配的干预？ | □ |
| 4.2 | 是否有参与者同时接受了对照组的干预？（污染） | □ |
| 4.3 | 是否有合理的分析来处理偏离干预的情况？ | □ |
| 4.4 | 偏离干预的原因在各组间是否平衡？ | □ |

### 判断逻辑

```
IF 依从率高+无污染+适当分析 → Low
IF 存在严重污染且未处理 → Serious
ELSE → Moderate
```

---

## Domain 5: 缺失数据产生的偏倚 (Bias due to missing data)

### 信号问题

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 5.1 | 结果数据是否对所有研究对象可用？ | □ |
| 5.2 | 缺失数据的比例和原因是否在各组间平衡？ | □ |
| 5.3 | 缺失数据是否可能与真实结果相关？ | □ |
| 5.4 | 缺失数据处理方法是否适当（如多重插补）？ | □ |

### 判断逻辑

```
IF 缺失<5% 且 MCAR → Low
IF 缺失 5-20% 且 MAR + 适当处理 → Moderate
IF 缺失>20% OR MNAR → Serious/Critical
ELSE → No information
```

---

## Domain 6: 结果测量产生的偏倚 (Bias in measurement of outcomes)

### 信号问题

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 6.1 | 结果测量方法是否有效且可靠？ | □ |
| 6.2 | 结果评估者是否对干预状态设盲？ | □ |
| 6.3 | 结果测量方法在各组间是否一致？ | □ |
| 6.4 | 是否有可能因干预知识影响结果评估？ | □ |

### 判断逻辑

```
IF 客观终点（死亡、实验室指标）→ Low（即使未设盲）
IF 主观终点+未设盲 → Serious
IF 方法不一致 → Serious/Critical
ELSE → Moderate
```

---

## Domain 7: 选择性报告结果产生的偏倚 (Bias in selection of the reported result)

### 信号问题

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 7.1 | 是否按照预先注册的分析计划执行？ | □ |
| 7.2 | 是否有证据表明在多个结果中选择了最有利的报告？ | □ |
| 7.3 | 是否有证据表明在多个亚组分析中选择了最有利的结果？ | □ |
| 7.4 | 是否有证据表明在多个时间点中选择了最有利的时间点？ | □ |

### 判断逻辑

```
IF 按计划执行+无选择性报告 → Low
IF 存在选择性报告证据 → Serious/Critical
ELSE → Moderate
```

---

## 整体判断汇总表

| 域 | 判断 | 理由 |
|----|------|------|
| D1 混杂 | □ Low / □ Mod / □ Serious / □ Critical / □ No info | |
| D2 选择 | □ Low / □ Mod / □ Serious / □ Critical / □ No info | |
| D3 分类 | □ Low / □ Mod / □ Serious / □ Critical / □ No info | |
| D4 偏离干预 | □ Low / □ Mod / □ Serious / □ Critical / □ No info | |
| D5 缺失数据 | □ Low / □ Mod / □ Serious / □ Critical / □ No info | |
| D6 结果测量 | □ Low / □ Mod / □ Serious / □ Critical / □ No info | |
| D7 选择性报告 | □ Low / □ Mod / □ Serious / □ Critical / □ No info | |
| **整体** | □ Low / □ Mod / □ Serious / □ Critical / □ No info | |

---

## 与 STROBE 的互补关系

| 维度 | STROBE（报告规范） | ROBINS-I V2（偏倚评估） |
|------|---------------------|--------------------------|
| 目的 | 研究是否报告了所有必要信息 | 研究结果是否可能被偏倚扭曲 |
| 时机 | 撰写/审稿时 | 系统综述/Meta分析时 |
| 判断 | 符合/不符合报告条目 | 5级风险判断 |
| 对应 | Item 6（参与者）→ D2 | Item 12a（混杂）→ D1 |

---

## ROBINS-I V2 vs RoB 2 的区别

| 特征 | RoB 2（RCT） | ROBINS-I V2（NRSI） |
|------|--------------|---------------------|
| 适用设计 | 随机对照试验 | 非随机干预研究 |
| 核心域 | 5 域 | 7 域（含混杂+选择） |
| 判断等级 | 3 级（Low/Some/High） | 5 级（Low/Mod/Serious/Critical/No info） |
| 混杂处理 | 随机化自动控制 | 需显式评估 |
| 前提 | 无 | 需定义目标试验 |

---

## 参考文献

1. Sterne JA, Hernán MA, Reeves BC, et al. ROBINS-I: a tool for assessing risk of bias in non-randomised studies of interventions. BMJ. 2016;355:i4919.
2. Cochrane Methods Bias Group. ROBINS-I V2 tool. riskofbias.info. 2024.
3. Bero L, et al. ROBINS-E: a tool for assessing risk of bias in non-randomised studies of exposures. Environment International. 2024.
