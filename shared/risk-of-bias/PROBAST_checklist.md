# PROBAST 风险偏倚评估清单

> 适用于临床预测模型研究的偏倚风险和适用性评估
> 基于 **PROBAST 工具**（Wolff et al., Ann Intern Med 2019）+ **PROBAST+AI 扩展**（BMJ 2025）
> 参考: [probast.org](https://www.probast.org) | [riskofbias.info](https://www.riskofbias.info)
> 更新日期: 2026-06-15

> **IRON RULES**:
> - 本清单严格对齐 PROBAST 官方 4 域 20 信号问题结构
> - 每个域评估偏倚风险（Risk of Bias, RoB）和适用性（Applicability）
> - 判断等级: **Low** / **High** / **Unclear**
> - 适用于: 诊断/预后预测模型（含机器学习和 AI 模型）
> - PROBAST+AI 扩展项以 **🤖 AI** 标注
> - 参考: shared/reporting-guidelines/TRIPOD_AI_checklist.md（报告规范）；本清单（偏倚评估）互补使用

---

## 整体判断

```
整体偏倚风险 = MAX(4 域 RoB 判断)
- 4 域均 Low → 整体 Low
- 任一域 High → 整体 High
- 任一域 Unclear → 整体 Unclear

整体适用性 = MAX(3 域适用性判断)（D4 无适用性评估）
```

---

## Domain 1: 研究对象域 (Participants)

### 偏倚风险 — 信号问题

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 1.1 | 数据来源是否适当（如连续入组、随机抽样）？ | □ |
| 1.2 | 研究对象的纳入/排除标准是否合适且无过度限制？ | □ |
| 1.3 | 是否避免了不适当排除可能影响模型泛化的亚组？ | □ |
| 1.4 | 研究对象是否代表了模型的目标人群？ | □ |

### 适用性评估

```
- 研究对象与预期应用场景是否匹配？
- 目标人群的定义是否合理？
→ Low concern / High concern / No information
```

### 🤖 AI 扩展
- 训练数据是否充分代表目标人群的多样性（年龄/性别/种族/地域）？
- 是否评估了数据集的分布偏移（distribution shift）风险？

### 常见偏倚来源
- 回顾性选择偏倚（case-control 设计用于预测模型）
- 单中心数据限制泛化性
- 排除标准过于严格导致人群不具代表性

---

## Domain 2: 预测变量域 (Predictors)

### 偏倚风险 — 信号问题

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 2.1 | 预测变量的定义是否明确且可重复？ | □ |
| 2.2 | 预测变量的测量方法是否适当且在所有研究对象中一致？ | □ |
| 2.3 | 预测变量是否在结果评估前测量（避免信息偏倚）？ | □ |
| 2.4 | 所有研究对象的预测变量是否均可用？ | □ |

### 适用性评估

```
- 预测变量是否在预期应用场景中可用？
- 测量方法是否与临床实践一致？
→ Low concern / High concern / No information
```

### 🤖 AI 扩展
- 特征工程过程是否透明且可重复？
- 是否避免了使用目标变量的衍生特征（data leakage）？
- 图像/文本等非结构化数据的预处理是否标准化？

---

## Domain 3: 结果域 (Outcome)

### 偏倚风险 — 信号问题

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 3.1 | 结果的定义是否明确且可重复？ | □ |
| 3.2 | 结果的测量方法是否适当且可靠？ | □ |
| 3.3 | 结果评估者是否对预测变量信息设盲？ | □ |
| 3.4 | 结果评估与预测变量测量之间的时间间隔是否合理？ | □ |
| 3.5 | 是否所有研究对象的结果均可用？ | □ |

### 适用性评估

```
- 结果定义是否与预期应用场景一致？
- 结果测量方法是否与临床实践一致？
→ Low concern / High concern / No information
```

### 关键问题
- 诊断金标准是否在所有研究对象中执行？（workup bias）
- 结果定义是否因时间窗不同而改变？

---

## Domain 4: 分析域 (Analysis)

### 偏倚风险 — 信号问题

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 4.1 | 研究对象数量相对于预测变量数量是否充足（EPV ≥ 10）？ | □ |
| 4.2 | 缺失数据是否得到适当处理？ | □ |
| 4.3 | 是否使用了适当的变量选择方法？ | □ |
| 4.4 | 模型构建方法是否适合数据类型？ | □ |
| 4.5 | 是否进行了内部验证（如 bootstrap、交叉验证）？ | □ |
| 4.6 | 模型区分度（如 AUC）和校准度（如校准图）是否均报告？ | □ |
| 4.7 | 是否避免了过度拟合（如通过正则化、剪枝）？ | □ |
| 4.8 | 模型性能是否在亚组中评估（如按年龄、性别）？ | □ |

### 🤖 AI 扩展
- 超参数调优过程是否透明（搜索策略、验证集划分）？
- 是否报告了多次运行的方差（模型稳定性）？
- 是否评估了模型在分布偏移数据上的鲁棒性？
- 是否使用了适当的公平性评估（fairness metrics）？

### 常见偏倚来源
- EPV < 10 → 过拟合
- 缺失数据用 complete case → 选择偏倚
- 无内部验证 → 性能高估（乐观偏差）
- 变量选择用单变量筛选 → 遗漏重要预测变量

---

## 整体判断汇总表

### 偏倚风险

| 域 | 判断 | 理由 |
|----|------|------|
| D1 研究对象 | □ Low / □ High / □ Unclear | |
| D2 预测变量 | □ Low / □ High / □ Unclear | |
| D3 结果 | □ Low / □ High / □ Unclear | |
| D4 分析 | □ Low / □ High / □ Unclear | |
| **整体 RoB** | □ Low / □ High / □ Unclear | |

### 适用性

| 域 | 判断 | 理由 |
|----|------|------|
| D1 研究对象 | □ Low concern / □ High concern / □ No info | |
| D2 预测变量 | □ Low concern / □ High concern / □ No info | |
| D3 结果 | □ Low concern / □ High concern / □ No info | |
| **整体适用性** | □ Low concern / □ High concern / □ No info | |

---

## 与 TRIPOD+AI 的互补关系

| 维度 | TRIPOD+AI（报告规范） | PROBAST（偏倚评估） |
|------|------------------------|---------------------|
| 目的 | 模型研究是否报告了所有必要信息 | 模型研究是否存在偏倚风险 |
| 时机 | 撰写/审稿时 | 系统综述/Meta分析时 |
| 判断 | 符合/不符合报告条目 | Low/High/Unclear |
| 对应 | Item 6（结局定义）→ D3 | Item 10（模型开发）→ D4 |

---

## 参考文献

1. Wolff RF, Moons KGM, Riley RD, et al. PROBAST: A Tool to Assess the Risk of Bias and Applicability of Prediction Model Studies. Ann Intern Med. 2019;170(1):51-58.
2. Collins GS, Wolff RF, Whiting P, et al. PROBAST+AI: an updated quality, risk of bias, and applicability assessment tool for prediction models. BMJ. 2025;388:e082505.
3. Riley RD, et al. Calculating the sample size required for developing a clinical prediction model. BMJ. 2020;368:m441.
