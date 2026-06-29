# QUADAS-2 风险偏倚评估清单

> 适用于诊断准确性研究的偏倚风险和适用性评估
> 基于 **QUADAS-2 工具**（Whiting et al., BMC Med Res Methodol 2011）
> 参考: [bristol.ac.uk/quadas](https://www.bristol.ac.uk/population-health-sciences/projects/quadas/)
> 更新日期: 2026-06-15

> **IRON RULES**:
> - 本清单严格对齐 QUADAS-2 官方 4 域结构
> - 每个域评估偏倚风险（Risk of Bias）和适用性（Applicability Concerns）
> - 判断等级: **Low** / **High** / **Unclear**
> - 适用于: 诊断准确性研究（横断面、前瞻性队列等）
> - 参考: src/shared/reporting-guidelines/STARD_checklist.md（如存在；报告规范）；本清单（偏倚评估）互补使用

---

## 整体判断

```
整体偏倚风险 = MAX(4 域 RoB 判断)
整体适用性 = MAX(3 域适用性判断)（D4 无适用性评估）
```

---

## 研究流程图

```
纳入标准 ──→ 选择偏倚（D1）
    │
    ▼
待评估试验 ──→ 待评估试验偏倚（D2）
    │
    ▼
金标准 ──→ 金标准偏倚（D3）
    │
    ▼
流程和时序 ──→ 流程偏倚（D4）
    │
    ▼
2×2 列联表 ──→ 敏感度、特异度
```

---

## Domain 1: 研究对象选择 (Patient Selection)

### 偏倚风险 — 信号问题

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 1.1 | 研究对象是否为连续或随机样本（非便利样本）？ | □ |
| 1.2 | 是否避免了病例-对照设计（除非是验证研究）？ | □ |
| 1.3 | 是否避免了根据待评估试验结果选择研究对象？ | □ |
| 1.4 | 是否避免了根据金标准结果选择研究对象？ | □ |

### 适用性评估

```
- 研究对象是否与综述问题的目标人群匹配？
- 纳入/排除标准是否过度限制（如排除合并症）？
→ Low concern / High concern / No information
```

### 常见偏倚来源
- 病例-对照设计（已知诊断状态）→ 高估准确性（spectrum bias）
- 三级医院样本 → 选择偏倚（疾病严重度偏倚）
- 根据待评估试验选择研究对象 → 验证偏倚

---

## Domain 2: 待评估试验 (Index Test)

### 偏倚风险 — 信号问题

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 2.1 | 待评估试验的结果判读是否在不了解金标准结果的情况下进行？ | □ |
| 2.2 | 待评估试验的操作和判读方法是否与临床实践一致？ | □ |
| 2.3 | 是否预先设定了阳性阈值（cutoff）？ | □ |

### 适用性评估

```
- 待评估试验的实施方式是否与综述问题一致？
- 阈值是否与临床实践一致？
→ Low concern / High concern / No information
```

### 关键问题
- 事后优化阈值（data-driven cutoff）→ 高估准确性
- 设盲不足 → 评估偏倚

---

## Domain 3: 金标准 (Reference Standard)

### 偏倚风险 — 信号问题

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 3.1 | 金标准是否能正确分类目标疾病状态？ | □ |
| 3.2 | 金标准的结果判读是否在不了解待评估试验结果的情况下进行？ | □ |

### 适用性评估

```
- 金标准是否与综述问题一致？
- 是否为公认的疾病定义？
→ Low concern / High concern / No information
```

### 关键问题
- 金标准不完美（imperfect reference standard）→ 需用 latent class analysis 或 Bayesian 方法
- 不同研究使用不同金标准 → 异质性来源

---

## Domain 4: 流程和时序 (Flow and Timing)

### 偏倚风险 — 信号问题

| # | 问题 | 是/可能是/否/无信息 |
|---|------|---------------------|
| 4.1 | 待评估试验和金标准之间的时间间隔是否可接受（避免疾病进展）？ | □ |
| 4.2 | 是否所有研究对象均接受了金标准检查？ | □ |
| 4.3 | 是否所有研究对象均纳入了最终分析？ | □ |

### 判断逻辑

```
IF 时间间隔短+所有人均接受金标准+无排除 → Low
IF 仅部分接受金标准（如待评估试验阴性者跳过金标准）→ High（partial verification bias）
ELSE → Unclear
```

### 常见偏倚来源
- 部分验证偏倚（partial verification bias）→ 高估敏感度
- 差异疾病进展偏倚（differential disease progression bias）
- 待评估试验结果影响后续检查决策

---

## 整体判断汇总表

### 偏倚风险

| 域 | 判断 | 理由 |
|----|------|------|
| D1 研究对象 | □ Low / □ High / □ Unclear | |
| D2 待评估试验 | □ Low / □ High / □ Unclear | |
| D3 金标准 | □ Low / □ High / □ Unclear | |
| D4 流程和时序 | □ Low / □ High / □ Unclear | |
| **整体 RoB** | □ Low / □ High / □ Unclear | |

### 适用性

| 域 | 判断 | 理由 |
|----|------|------|
| D1 研究对象 | □ Low concern / □ High concern / □ No info | |
| D2 待评估试验 | □ Low concern / □ High concern / □ No info | |
| D3 金标准 | □ Low concern / □ High concern / □ No info | |
| **整体适用性** | □ Low concern / □ High concern / □ No info | |

---

## 与 PROBAST 的区别

| 特征 | QUADAS-2（诊断准确性） | PROBAST（预测模型） |
|------|-------------------------|---------------------|
| 适用研究 | 单个诊断试验准确性 | 临床预测模型开发/验证 |
| 核心指标 | 敏感度/特异度 | AUC/校准度 |
| 域数 | 4 域 | 4 域 |
| 结果类型 | 二分类（有病/无病） | 连续概率 |
| 应用场景 | 系统综述诊断准确性 | 系统综述预测模型 |

---

## 参考文献

1. Whiting PF, Rutjes AWS, Westwood ME, et al. QUADAS-2: A Revised Tool for the Quality Assessment of Diagnostic Accuracy Studies. Ann Intern Med. 2011;155(8):529-536.
2. Cochrane Handbook, Chapter 10: Including non-randomized studies and studies of diagnostic test accuracy.
3. Reitsma JB, et al. Beyond ROC curves: when should we use alternative measures of diagnostic accuracy? BMJ. 2009;339:b2551.
