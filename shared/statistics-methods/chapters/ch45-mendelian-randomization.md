# 孟德尔随机化 (Mendelian Randomization, MR) 进阶方法

> 版本: 1.0 | 2026-06-13
> MSRA 关联: `analysis-plan` Phase 3 方法选择, `analysis-exec` Phase 7 因果推断
> 注: 本章为孟德尔随机化完整章节（原ch27基础概念已合并至本章）

---

## 概述

孟德尔随机化 (MR) 利用遗传变异作为工具变量，推断暴露与结局之间的因果关系。本章涵盖工具选择、多种估计方法、多效性评估及报告规范。

### MR 三大核心假设

| 假设 | 含义 | 评估方法 |
|------|------|---------|
| **相关性 (Relevance)** | 工具变量与暴露强相关 | F 统计量 > 10；$R^2$ 评估 |
| **独立性 (Independence)** | 工具变量与混杂因素无关 | 主成分分析、人群分层检查 |
| **排他性 (Exclusion Restriction)** | 工具变量仅通过暴露影响结局 | 多效性检验（见下文） |

**F 统计量计算**:

$$F = \frac{R^2 / k}{(1 - R^2) / (n - k - 1)}$$

其中 $R^2$ 为工具变量解释暴露变异的比例，$k$ 为工具变量个数，$n$ 为样本量。

---

## 一、工具变量筛选

### 1.1 全基因组显著性阈值

| 阈值 | 用途 | 说明 |
|------|------|------|
| $p < 5 \times 10^{-8}$ | 标准阈值 | 常规 MR 分析推荐 |
| $p < 5 \times 10^{-6}$ | 宽松阈值 | 标准阈值工具不足时，需报告敏感性分析 |
| $p < 1$ (全 GWAS) | MR-PRESSO 用 | 用于检测水平多效性 |

### 1.2 工具变量独立性处理

- **LD clumping**: 以 $r^2 < 0.001$，窗口 10,000 kb 阈值去除连锁不平衡 SNP
- **条件分析**: 使用条件/联合分析 (COJO) 提取独立信号
- **LD 参考面板**: 使用与暴露 GWAS 匹配的人群（如 1000 Genomes EUR）

### 1.3 双向效应剔除

- 从 PhenoScanner 查询工具变量是否与结局强关联
- 剔除与结局直接关联 ($p < 5 \times 10^{-8}$) 的 SNP（违反排他性假设）

---

## 二、双样本 MR (Two-Sample MR)

### 2.1 设计原理

暴露和结局的 GWAS 来自**不重叠**的独立样本，避免弱工具偏倚的方向性偏倚。

| 条件 | 单样本 MR | 双样本 MR |
|------|-----------|-----------|
| 样本重叠 | 同一样本 | 不重叠样本 |
| 偏倚方向 | 向零偏倚 | 无偏倚 |
| 方差估计 | 偏低 | 正确 |
| 数据可及性 | 需个体数据 | 仅需汇总统计 |

### 2.2 比率估计量 (Wald Ratio)

当仅有一个工具变量时：

$$\hat{\beta}_{MR} = \frac{\hat{\beta}_{YG}}{\hat{\beta}_{XG}} = \frac{\text{工具-结局效应}}{\text{工具-暴露效应}}$$

$$\text{SE}(\hat{\beta}_{MR}) \approx \frac{\text{SE}(\hat{\beta}_{YG})}{|\hat{\beta}_{XG}|}$$

### 2.3 R 实现 (TwoSampleMR)

```r
library(TwoSampleMR)

# 1. 获取暴露工具变量
exposure_dat <- extract_instruments("ieu-a-2")  # 示例: BMI

# 2. 获取结局数据
outcome_dat <- extract_outcome_data(
  snps = exposure_dat$SNP,
  outcomes = "ieu-a-7"  # 示例: 冠心病
)

# 3. 协调数据 (对齐效应等位基因方向)
dat <- harmonise_data(exposure_dat, outcome_dat)

# 4. 主分析
res <- mr(dat, method_list = c("mr_ivw", "mr_egger_regression", "mr_weighted_median"))
```

---

## 三、MR 分析方法

### 3.1 方法比较

| 方法 | 假设 | 多效性容忍度 | 推荐场景 |
|------|------|------------|---------|
| **IVW** | 所有工具有效 (InSIDE) | 无 | 主分析（无多效性时） |
| **MR-Egger** | InSIDE 假设 | 允许定向多效性 | 多效性可能存在时 |
| **加权中位数** | ≥50% 工具有效 | 允许多数工具无效 | 稳健性检查 |
| **加权众数** | 最大工具簇有效 | 允许多数工具无效 | 存在异常值时 |
| **MR-PRESSO** | 多数工具有效 | 识别并剔除离群工具 | 多效性检测 |
| **MR-RAPS** | 正则化 | 允许弱工具和多效性 | 大规模工具集 |

### 3.2 逆方差加权 (IVW)

$$\hat{\beta}_{IVW} = \frac{\sum_j \hat{\beta}_{Yj} \hat{\beta}_{Xj} \sigma_{Yj}^{-2}}{\sum_j \hat{\beta}_{Xj}^2 \sigma_{Yj}^{-2}}$$

- **固定效应 IVW**: 假设无异质性
- **随机效应 IVW**: 允许工具间异质性（推荐默认使用）

### 3.3 MR-Egger 回归

$$\hat{\beta}_{Yj} = \theta_0 + \theta_1 \hat{\beta}_{Xj} + \epsilon_j$$

- $\theta_1$ = 因果效应估计（校正定向多效性）
- $\theta_0$ = 截距项（偏离零提示方向性多效性）
- **InSIDE 假设**: 工具变量对暴露的效应与多效性效应独立

**局限**: 统计功效低，通常置信区间较宽。

### 3.4 加权中位数与众数

```r
# 加权中位数 (至少 50% 工具有效即可)
res_median <- mr(dat, method_list = c("mr_weighted_median"))

# 加权众数 (最大工具簇有效)
res_mode <- mr(dat, method_list = c("mr_mode"))
```

---

## 四、多效性评估

### 4.1 MR-PRESSO

```r
library(MRPRESSO)

presso <- mr_presso(
  BetaOutcome = "beta.outcome",
  BetaExposure = "beta.exposure",
  SdOutcome = "se.outcome",
  SdExposure = "se.exposure",
  data = dat,
  OUTLIERtest = TRUE,
  DISTORTIONtest = TRUE,
  SignifThreshold = 0.05
)

# 全局检验 (是否有离群工具)
presso$`MR-PRESSO results`$`Global Test`$Pvalue

# 离群检验 (识别哪些是离群工具)
presso$`MR-PRESSO results`$`Outlier Test`

# 失真检验 (剔除离群后效应是否改变)
presso$`MR-PRESSO results`$`Distortion Test`$Pvalue
```

### 4.2 多效性评估汇总

| 检验 | 原假设 | 解读 |
|------|--------|------|
| MR-Egger 截距 | 无定向多效性 | p < 0.05 提示存在定向多效性 |
| MR-PRESSO 全局检验 | 无离群工具 | p < 0.05 提示存在水平多效性 |
| Cochran Q 统计量 | 工具间无异质性 | p < 0.05 提示存在异质性/多效性 |

---

## 五、异质性检验

### 5.1 Cochran Q 统计量

$$Q = \sum_{j=1}^{k} w_j (\hat{\beta}_{MR,j} - \hat{\beta}_{IVW})^2$$

- $Q \sim \chi^2_{k-1}$ under $H_0$ (无异质性)
- $I^2 = \frac{Q - (k-1)}{Q} \times 100\%$ 量化异质性程度

### 5.2 异质性解读

| $I^2$ | 异质性 | 操作 |
|--------|--------|------|
| < 25% | 低 | IVW 结果可信 |
| 25-50% | 中等 | 检查敏感性方法一致性 |
| 50-75% | 较高 | 使用 MR-Egger/中位数 |
| > 75% | 高 | 排查离群 SNP，使用 MR-PRESSO |

```r
# 异质性检验
mr_heterogeneity(dat, method_list = c("mr_ivw"))
```

---

## 六、逐一剔除分析 (Leave-One-Out)

逐一剔除每个 SNP 重新估计因果效应，识别是否有单一 SNP 驱动整体结果。

```r
loo <- mr_leaveoneout(dat)

# 可视化
p_loo <- mr_leaveoneout_plot(loo)
p_loo[[1]]
```

**解读要点**:
- 如果剔除某 SNP 后效应大幅改变 → 该 SNP 为潜在离群工具
- 如果所有剔除后效应稳定 → 结果稳健

---

## 七、多变量 MR (Multivariable MR, MVMR)

### 7.1 适用场景

- 暴露之间存在共线性（如 HDL 胆固醇与甘油三酯）
- 需要同时估计多个暴露的独立因果效应
- 校正中间变量的直接/间接效应

### 7.2 模型

$$\hat{\beta}_{Yg} = \sum_{i=1}^{p} \theta_i \hat{\beta}_{X_i g} + \epsilon_g$$

### 7.3 R 实现

```r
library(MendelianRandomization)

mv_input <- mr_mvinput(
  bx = cbind(bx_bmi, bx_ldl, bx_hdl),   # 多暴露效应
  bxse = cbind(bx_bmi_se, bx_ldl_se, bx_hdl_se),
  by = by_outcome,
  byse = by_outcome_se
)

# IVW 估计
mv_ivw <- mr_mvivw(mv_input)

# Egger 扩展
mv_egger <- mr_mvegger(mv_input)
```

---

## 八、报告模板

> 本研究采用两样本孟德尔随机化 (MR) 方法评估 {暴露} 与 {结局} 之间的因果关系。工具变量选自 {暴露 GWAS 来源}（样本量: n = {N}），以全基因组显著性阈值 $p < 5 \times 10^{-8}$ 筛选 {k} 个独立 SNP（LD clumping $r^2 < 0.001$），F 统量均值为 {F}。结局汇总数据来自 {结局 GWAS 来源}（n = {N}）。
>
> 主分析采用随机效应逆方差加权 (IVW) 法。敏感性分析包括 MR-Egger 回归（截距 p = {p}）、加权中位数、加权众数及 MR-PRESSO 全局检验 (p = {p})。异质性通过 Cochran Q 检验评估 ($I^2$ = {I2}%)。逐一剔除分析确认无单一 SNP 驱动结果。因果效应以 {OR/β} (95% CI: [{lower}, {upper}]) 表示。分析使用 R {版本}，`TwoSampleMR` 和 `MendelianRandomization` 包。

---

## 九、常见陷阱

| 陷阱 | 说明 | 解决方案 |
|------|------|---------|
| 样本重叠 | 单样本/部分重叠导致偏倚 | 确认暴露与结局 GWAS 样本独立 |
| 弱工具偏倚 | F < 10 | 报告 F 统计量，使用 MR-RAPS |
| Winner's curse | 暴露 GWAS 发现样本过小 | 使用外部复制样本 |
| 人群分层 | 不同祖源混合 | 限制于同祖源，使用 PCA 校正 |
| 连锁不平衡 | LD 导致工具不独立 | 使用条件分析 (COJO) |
| 反向因果 | 结局影响暴露 | 双向 MR 检验 |
| 统计功效不足 | 效应量小、工具弱 | 事前功效计算 (mRnd 在线工具) |

---

## 十、参考资源

- **核心文献**: Lawlor DA, Harbord RM, Sterne JA, et al. Mendelian randomization: using genes as instruments for making causal inferences in epidemiology. *Stat Med*, 2008, 27(8): 1133-1163.
- **方法学**: Burgess S, Thompson SG. *Mendelian Randomization: Methods for Using Genetic Variants in Causal Estimation*. Chapman & Hall/CRC, 2015.
- **R 包**: `TwoSampleMR` (MRC-IEU), `MendelianRandomization`, `MR-PRESSO`, `mr.raps`, `phenoscanner`
- **在线工具**: MR-Base (www.mrbase.org), GWAS Catalog, PhenoScanner
- **MSRA 模板**: `shared/templates/mr_analysis_template.R`
