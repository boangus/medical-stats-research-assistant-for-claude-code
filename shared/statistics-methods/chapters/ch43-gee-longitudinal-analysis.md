# 广义估计方程 (GEE) 与纵向数据分析

> 版本: 1.0 | 2026-06-13
> MSRA 关联: `analysis-plan` Phase 3 方法选择, `analysis-exec` Phase 7

---

## 概述

广义估计方程 (Generalized Estimating Equations, GEE) 是处理**纵向/重复测量/聚类数据**的半参数方法。与混合模型不同，GEE 估计的是**总体平均效应 (Population-Averaged Effect)**，而非个体特异效应。

### GEE vs 混合模型选择

| 特征 | GEE | 混合模型 (GLMM) |
|------|-----|----------------|
| 目标估计量 | 总体平均效应 (marginal) | 条件效应 (conditional) |
| 分布假设 | 仅需均值和方差指定 | 需要完整分布假设 |
| 缺失假设 | MCAR（完全随机缺失） | MAR（随机缺失）即可 |
| 相关结构 | 需预设工作相关矩阵 | 通过随机效应建模 |
| 解释 | "人群平均" | "给定个体" |
| 适用场景 | 关注政策/人群水平效应 | 关注个体水平预测 |

**经验法则**:
- 关注"某干预对人群平均效果" → GEE
- 关注"某特定个体的预测" → GLMM
- OR/HR 在 GEE 和 GLMM 中不同（Neyman-Pearson 矛盾），需在 SAP 中预定义

---

## 一、工作相关矩阵选择

| 结构 | 描述 | 适用场景 |
|------|------|---------|
| Independence | 各观测独立 | 聚类随机试验（clustering） |
| Exchangeable | 同一簇内任意两次观测相关相同 | 基线+随访设计，各时间点等距 |
| AR(1) | 相邻时间点相关最强，随距离衰减 | 密集纵向数据，时间间隔固定 |
| Unstructured | 所有时间点对的相关自由估计 | 时间点少(≤4)且无先验假设 |

**选择策略**:
1. 基于研究设计的先验知识选择
2. 用 **QIC (Quasi-Information Criterion)** 比较不同结构 → QIC 越小越好
3. 如果各结构下结论一致 → 结论稳健
4. 如果各结构下结论不一致 → 需谨慎解读，报告多种结果

---

## 二、GEE 模型规范

### 2.1 基本公式

$$\sum_{i=1}^{n} D_i^T V_i^{-1} (Y_i - \mu_i) = 0$$

其中:
- $D_i = \partial \mu_i / \partial \beta$ — 设计矩阵的导数
- $V_i = \phi A_i^{1/2} R_i(\alpha) A_i^{1/2}$ — 工作方差矩阵
- $A_i$ — 对角矩阵，$a_{jj} = \text{Var}(Y_{ij} | \mu_{ij})$
- $R_i(\alpha)$ — 工作相关矩阵
- $\phi$ — 离散参数

### 2.2 稳健方差 (Sandwich Estimator)

GEE 的核心优势: 使用**稳健三明治方差估计**，即使工作相关矩阵误设，效应估计仍一致（但可能损失效率）。

$$\hat{V}_{robust} = \hat{M}^{-1} \left(\sum_i D_i^T V_i^{-1} \text{Var}(Y_i) V_i^{-1} D_i \right) \hat{M}^{-1}$$

**注意**: 小样本时三明治方差可能有偏 → 使用 **F-K (Fay-Graubard) 修正** 或 **MD (Mancl-DeRouen) 修正**。

---

## 三、结果解读

### 3.1 Gaussian GEE

直接解读 β 系数:
- β = 1.5 表示暴露组平均比对照组高 1.5 个单位

### 3.2 Binomial GEE (Logit 链接)

解读为 OR (Odds Ratio):
- exp(β) = OR，注意这是**边际 OR**，通常小于条件 OR
- 当结局罕见时，边际 OR ≈ 条件 OR

### 3.3 Poisson GEE (Log 链接)

解读为 RR (Rate Ratio):
- exp(β) = RR

---

## 四、常见陷阱

| 陷阱 | 说明 |
|------|------|
| 混淆边际与条件效应 | GEE 的 OR ≠ GLMM 的 OR（当结局常见时差异大） |
| 小样本使用标准三明治方差 | 需用修正版本 (FG/MD) |
| 忽略 MCAR 假设 | GEE 在 MAR 下有偏 → 考虑加权 GEE (WGEE) |
| AR(1) 用于不等距数据 | 不等距时用 Unstructured 或时间特定相关 |
| 过多时间点用 Unstructured | k > 4 时参数过多 → 用 AR(1) 或 Exchangeable |

---

## 五、报告模板

> 纵向数据采用广义估计方程 (GEE) 分析，以 {family} 分布和 {corstr} 工作相关矩阵建模。采用稳健三明治方差估计。{结局变量} 的组间差异具有{统计学意义/无统计学意义}（β = {β}, SE = {SE}, 95% CI: [{lower}, {upper}], p = {p}），暴露组的 {结局变量} 平均{高/低} {绝对差异} 个单位（或 RR = {RR}, 95% CI: [{lower}, {upper}]）。不同工作相关矩阵 (Exchangeable/AR1/Unstructured) 下结论一致 (QIC: {qic1}/{qic2}/{qic3})。

---

## 六、参考资源

- **书籍**: Diggle, Heagerty, Liang & Zeger. *Analysis of Longitudinal Data* (2nd ed.)
- **R 包**: `geepack`, `gee`, `MuMIn` (QIC 计算)
- **Python**: `statsmodels.genmod.generalized_estimating_equations.GEE`
- **MSRA 模板**: `shared/templates/gee_template.R`, `shared/templates/gee_template.py`
