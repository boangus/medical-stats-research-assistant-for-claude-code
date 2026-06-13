# 方法学 统计与方法指南 — 索引

> 来源：*方法学 Guide to Statistics and Methods*（Edward H. Livingston, Roger J. Lewis 主编）
> 整合日期：2026-05-29
> 本目录提供 46 个与统计分析直接相关的章节索引，按主题分组，便于在 MSRA 流水线各阶段快速查阅。
> v0.7.1 新增: ch44 目标试验模拟, ch45 孟德尔随机化, ch46 网络Meta分析
> 已删除 14 章无关内容（数据库实践指南 ch43-55、深度学习 ch42）。

---

## 一、研究设计（第 1–9 章）

| 编号 | 章节 | 文件名 | MSRA 关联阶段 |
|------|------|--------|-------------|
| ch01 | 非劣效性试验 | `chapters/ch01-non-inferiority-trials.md` | `analysis-plan` Phase 3 方法探讨 |
| ch02 | 剂量探索试验 | `chapters/ch02-dose-finding-trials.md` | `analysis-plan` Phase 3 |
| ch03 | 实效性试验 | `chapters/ch03-pragmatic-trials.md` | `analysis-plan` Phase 3 |
| ch04 | 整群随机试验 | `chapters/ch04-cluster-randomized-trials.md` | `analysis-plan` Phase 3 |
| ch05 | 阶梯楔形临床试验 | `chapters/ch05-stepped-wedge-clinical-trials.md` | `analysis-plan` Phase 3 |
| ch06 | 样本量计算 | `chapters/ch06-sample-size-calculations.md` | `analysis-plan` Phase 3; `analysis-exec` Phase 0 |
| ch07 | 最小临床重要性差异（MCID） | `chapters/ch07-minimal-clinically-important-difference.md` | `analysis-plan` Phase 3; `report` Phase 1 |
| ch08 | 临床研究中的随机化 | `chapters/ch08-randomization-in-clinical-research.md` | `analysis-plan` Phase 3 |
| ch09 | 研究均势（Equipoise） | `chapters/ch09-equipoise-in-research.md` | `analysis-plan` Phase 3 |

## 二、统计分析方法（第 10–19 章）

| 编号 | 章节 | 文件名 | MSRA 关联阶段 |
|------|------|--------|-------------|
| ch10 | 时间至事件分析（生存分析） | `chapters/ch10-time-to-event-analysis.md` | `analysis-exec` Phase 7 |
| ch11 | 复合终点 | `chapters/ch11-composite-endpoints.md` | `analysis-plan` Phase 2 Estimands |
| ch12 | 缺失数据 | `chapters/ch12-missing-data.md` | `analysis-plan` Phase 1 EDA |
| ch13 | 意向性治疗原则（ITT） | `chapters/ch13-intention-to-treat-principle.md` | `analysis-plan` Phase 2; `analysis-exec` Phase 0 |
| ch14 | 重复测量混合模型（MMRM） | `chapters/ch14-mixed-models-for-repeated-measures.md` | `analysis-exec` Phase 7 |
| ch15 | Logistic 回归 | `chapters/ch15-logistic-regression.md` | `analysis-exec` Phase 7 |
| ch16 | Logistic 回归诊断 | `chapters/ch16-logistic-regression-diagnostics.md` | `analysis-exec` Phase 7 |
| ch17 | 需治数（NNT） | `chapters/ch17-number-needed-to-treat.md` | `report` Phase 1 |
| ch18 | 多重比较方法 | `chapters/ch18-multiple-comparisons-methods.md` | `analysis-plan` Phase 4 SAP 制定 |
| ch19 | 关口策略（Gatekeeping） | `chapters/ch19-gatekeeping-strategies.md` | `analysis-plan` Phase 4 |

## 三、高级分析方法（第 20–30 章）

| 编号 | 章节 | 文件名 | MSRA 关联阶段 |
|------|------|--------|-------------|
| ch20 | 多重插补 | `chapters/ch20-multiple-imputation.md` | `analysis-exec` Phase 7 |
| ch21 | 早期终止试验的解读 | `chapters/ch21-interpretation-of-early-stopped-trials.md` | `analysis-plan` Phase 4 |
| ch22 | 贝叶斯分析 | `chapters/ch22-bayesian-analysis.md` | `analysis-plan` Phase 3 |
| ch23 | 决策曲线分析（DCA） | `chapters/ch23-decision-curve-analysis.md` | `report` Phase 4 图表 |
| ch24 | 双重差分法（DID） | `chapters/ch24-difference-in-differences.md` | `analysis-plan` Phase 3 观察性 |
| ch25 | 病例对照研究 | `chapters/ch25-case-control-studies.md` | `analysis-plan` Phase 3 |
| ch26 | Meta 分析 | `chapters/ch26-meta-analysis.md` | `analysis-plan` Phase 3 |
| ch27 | 孟德尔随机化 | `chapters/ch27-mendelian-randomization.md` | `analysis-plan` Phase 3 观察性 |
| ch28 | E 值（敏感性分析） | `chapters/ch28-e-value.md` | `analysis-exec` Phase 7 敏感性 |
| ch29 | 指示性混杂（Indication Bias） | `chapters/ch29-indication-bias.md` | `analysis-plan` Phase 3; `analysis-exec` Phase 7 |
| ch30 | 中介分析 | `chapters/ch30-mediation-analysis.md` | `analysis-plan` Phase 3 观察性 |

## 四、效应量与模型解读（第 31–39 章）

| 编号 | 章节 | 文件名 | MSRA 关联阶段 |
|------|------|--------|-------------|
| ch31 | 比值比（OR） | `chapters/ch31-odds-ratio.md` | `report` Phase 1 |
| ch32 | 边际效应 | `chapters/ch32-marginal-effects.md` | `analysis-exec` Phase 7 |
| ch33 | 协变量调整 | `chapters/ch33-covariate-adjustment.md` | `analysis-plan` Phase 3 |
| ch34 | 多中心 RCT 的处理效应 | `chapters/ch34-treatment-effects-in-multicenter-rcts.md` | `analysis-plan` Phase 3 |
| ch35 | 倾向性评分 | `chapters/ch35-propensity-scores.md` | `analysis-exec` Phase 7 |
| ch36 | FROC 曲线 | `chapters/ch36-froc-curves.md` | `analysis-exec` Phase 7 |
| ch37 | 随机效应 Meta 分析 | `chapters/ch37-random-effects-meta-analysis.md` | `analysis-exec` Phase 7 |
| ch38 | 分层贝叶斯模型 | `chapters/ch38-hierarchical-bayesian-models.md` | `analysis-plan` Phase 3 |
| ch39 | C 统计量 | `chapters/ch39-c-statistic.md` | `report` Phase 1 |

## 五、卫生经济学（第 40–41 章）

| 编号 | 章节 | 文件名 | MSRA 关联阶段 |
|------|------|--------|-------------|
| ch40 | 成本效益分析 | `chapters/ch40-cost-effectiveness-analysis.md` | `analysis-plan` Phase 3 |
| ch41 | 时间范围选择 | `chapters/ch41-time-horizon-selection.md` | `analysis-plan` Phase 3 |

## 六、新增方法（第 42–46 章）

| 编号 | 章节 | 文件名 | MSRA 关联阶段 |
|------|------|--------|-------------|
| ch42 | 非参数检验方法 | `chapters/ch42-nonparametric-tests.md` | `analysis-plan` Phase 3; `analysis-exec` Phase 7 |
| ch43 | 广义估计方程 (GEE) | `chapters/ch43-gee-longitudinal-analysis.md` | `analysis-plan` Phase 3; `analysis-exec` Phase 7 |
| ch44 | 目标试验模拟 (TTE) | `chapters/ch44-target-trial-emulation.md` | `analysis-plan` Phase 3 观察性; `analysis-exec` Phase 7 |
| ch45 | 孟德尔随机化 (MR) | `chapters/ch45-mendelian-randomization.md` | `analysis-plan` Phase 3 观察性 |
| ch46 | 网络 Meta 分析 (NMA) | `chapters/ch46-network-meta-analysis.md` | `analysis-plan` Phase 3; `analysis-exec` Phase 7 |

---

## 辅助文件

| 文件 | 说明 |
|------|------|
| `glossary.md` | 术语表 |
| `cheatsheet.md` | 研究设计、统计方法、偏倚类型速查 |
| `patterns.md` | 8 种常见方法学模式 |
| `SKILL.md` | 完整的方法学框架与思维模型 |

## 与 MSRA 各阶段的对应关系

```
MSRA Pipeline Stage        → 涉及的 方法学 章节
──────────────────────────────────────────────────────
analysis-plan Phase 1 EDA  → ch12 缺失数据
analysis-plan Phase 2      → ch11 复合终点, ch13 ITT
analysis-plan Phase 3      → ch01-09 研究设计, ch22/ch24-27 高级方法
analysis-plan Phase 4 SAP  → ch18 多重比较, ch19 Gatekeeping, ch21 期中分析
analysis-exec Phase 0      → ch06 样本量, ch13 ITT
analysis-exec Phase 7      → ch10/ch14-16/ch28/ch32/ch35-37 统计方法
report Phase 1 结果解读    → ch07 MCID, ch17 NNT, ch31 OR, ch39 C统计量
report Phase 5 方法学描述  → 全章（方法学 报告风格参考）
```




