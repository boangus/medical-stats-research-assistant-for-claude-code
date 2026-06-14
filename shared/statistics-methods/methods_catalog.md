# 医学统计方法目录
>
> **模板索引** ⭐ 新增:
> - **基线特征表**: `table1_template.R` (gtsummary) | `table1_pharmaverse.R` (Pharmaverse rtables)
> - **生存分析**: `survival_ggsurvfit.R` (ggsurvfit, 推荐) | `survival_lifelines.py` (lifelines)
> - **因果推断**: `psm_template.py` (PSM) | `overlapping_weighting_template.py` (OW) | `causal_inference_dowhy.py` (DoWhy+EconML)
> - **机器学习**: `ml_analysis_template.py` (完整 ML 流程) | `shap_plot_template.py` (SHAP 可解释性)
> - **临床预测模型**: `prediction_model_template.py` (TRIPOD 合规：EPV→开发→Bootstrap→DCA→列线图→报告)
> - **敏感性一致性**: `shared/sensitivity-agreement/` (主要-敏感性分析一致性评估)
>
> **统计方法指南** :
> - **完整索引**: `shared/statistics-methods/INDEX.md` — 55 章完整索引
> - **速查**: `shared/statistics-methods/cheatsheet.md`
> - **术语表**: `shared/statistics-methods/glossary.md`

## 1. 描述性统计 (Descriptive Statistics)

### 连续变量
- **均值 ± 标准差**: 正态分布数据
- **中位数 (四分位距)**: 偏态分布数据
- **范围**: 最小值到最大值

### 分类变量
- **频数 (百分比)**: n (%)
- **率**: 每1000人年

## 2. 组间比较 (Group Comparisons)

### 两组独立样本
| 数据类型 | 参数检验 | 非参数检验 |
|---------|---------|-----------|
| 连续, 正态 | 独立样本 t 检验 | Mann-Whitney U 检验 |
| 连续, 配对 | 配对 t 检验 | Wilcoxon 符号秩检验 |
| 二分类 | 卡方检验 | Fisher 精确检验 |

### 多组比较 (>2组)
| 数据类型 | 参数检验 | 非参数检验 |
|---------|---------|-----------|
| 连续, 正态 | 单因素方差分析 (ANOVA) | Kruskal-Wallis H 检验 |
| 重复测量 | 重复测量方差分析 | Friedman 检验 |

## 3. 回归分析 (Regression Analysis)

### 线性回归 (Linear Regression)
- **适用**: 连续型结局变量
- **假设**: 线性关系、残差正态、方差齐性
- **R**: `lm(y ~ x1 + x2, data = df)`
- **Python**: `statsmodels.api.OLS`

### Logistic 回归
- **适用**: 二分类结局变量
- **输出**: 比值比 (OR) 及 95% CI
- **R**: `glm(y ~ x, family = binomial)`
- **Python**: `statsmodels.api.Logit`

### Poisson 回归
- **适用**: 计数型结局变量
- **输出**: 发生率比 (IRR)
- **注意**: 过度离散时改用负二项回归

### Cox 比例风险模型
- **适用**: 生存数据 (时间-事件)
- **输出**: 风险比 (HR) 及 95% CI
- **假设**: 比例风险假设
- **R**: `coxph(Surv(time, status) ~ x, data = df)`
- **Python**: `lifelines.CoxPHFitter`

## 4. 生存分析 (Survival Analysis)

### Kaplan-Meier 曲线
- 估计生存概率
- Log-rank 检验比较组间差异

**可用模板**:
- `survival_ggsurvfit.R` — ggsurvfit 版本 (推荐, 出版级 ggplot2 风格)
- `survival_lifelines.py` — Python lifelines 版本 ⭐ **新增**
- `cox_template.py` — Python Cox 回归模板

### 竞争风险模型
- 当存在多种终点事件时
- Fine-Gray 模型

### 生存数据推荐包
- **R**: `survival`, `survminer`, `ggsurvfit` (Pharmaverse), `tidycmprsk` (竞争风险)
- **Python**: `lifelines`, `scikit-survival`

## 5. 诊断试验 (Diagnostic Tests)

### ROC 分析
- AUC (曲线下面积)
- 最佳截断值 (Youden 指数)
- 敏感性和特异性

### 一致性检验
- Kappa 系数 (分类变量)
- ICC (组内相关系数, 连续变量)
- Bland-Altman 图

## 6. 高级方法 (Advanced Methods)

### 倾向性评分 (Propensity Score)
- 匹配 (Matching): 最近邻、卡钳、最优、分层
- 加权 (Weighting): IPTW、Overlapping Weighting (OW)
- 协变量调整
- **模板**: `psm_template.py` (PSM) | `overlapping_weighting_template.py` (OW)

### 机器学习 (Machine Learning)
- **分类模型**: Logistic 回归(基线)、Random Forest、XGBoost、LightGBM、SVM、Elastic Net
- **特征重要性**: MDI (Mean Decrease Impurity)、Permutation Importance、SHAP
- **模型评估**: AUC、Accuracy、F1、Brier Score、校准曲线
- **交叉验证**: K-fold CV、超参数调优
- **模板**: `ml_analysis_template.py` (完整 ML 流程) | `shap_plot_template.py` (SHAP 可解释性)
- **适用场景**: 预测模型开发、特征筛选、非线性关系建模、亚组发现

### 临床预测模型 (Clinical Prediction Model)
- **样本量评估**: EPV (Events Per Variable) ≥ 10-20
- **模型开发**: 多模型比较 + 变量选择
- **内部验证**: Bootstrap optimism correction (Harrell 2015)
- **校准评估**: 校准曲线 + 校准斜率/截距
- **临床效用**: DCA (Decision Curve Analysis) + 临床影响曲线
- **可视化**: 列线图 (Nomogram)
- **报告规范**: TRIPOD / TRIPOD+AI
- **模板**: `prediction_model_template.py` (7 阶段完整流程)
- **依赖包**: `dcurves` (DCA) | `simpleNomo` (列线图) | `pmsampsize` (样本量)

### 多重插补 (Multiple Imputation)
- 处理缺失数据
- 链式方程 (MICE)

### Meta 分析
- 固定效应模型
- 随机效应模型
- 异质性检验 (I²)

### 多水平模型 (Multilevel Models)
- 层次数据结构
- 混合效应模型

## 7. 样本量计算 (Sample Size)

### 两组比较
- 连续变量: `power.t.test()`
- 二分类: `power.prop.test()`

### 生存分析
- `powerSurvEpi::powerCT()`

### 诊断试验
- 敏感性/特异性估计

## 8. 方法降级决策树 (Method Fallback Decision Tree)

> 受 BioMedAgent 交互式探索机制启发 (Nature BME 2026)
> 目的：当统计假设违反时，Agent 应遵循明确的三段式降级路径，而非简单报错。

### 8.1 降级路径总表

| 方法 | 假设检验 | 检验通过 | 首轮降级 | 次轮降级 | 终极降级 |
|------|---------|---------|---------|---------|---------|
| **t 检验** | Shapiro-Wilk 正态性 + Levene 方差齐性 | 独立样本 t 检验 | Mann-Whitney U (非正态) | Welch t 检验 (方差不齐) | Bootstrap t 检验 |
| **配对 t 检验** | 配对差值正态性 (Shapiro-Wilk) | 配对 t 检验 | Wilcoxon 符号秩检验 | — | 符号检验 |
| **单因素 ANOVA** | 残差正态性 + Bartlett 方差齐性 | ANOVA | Kruskal-Wallis H 检验 | Welch ANOVA (方差不齐) | 置换检验 (Permutation) |
| **重复测量 ANOVA** | 球形假设 (Mauchly) | 重复测量 ANOVA | Greenhous-Geisser 校正 | Friedman 检验 | — |
| **卡方检验** | 期望频数 ≥ 5 (80% 以上单元格) | Pearson 卡方 | Fisher 精确检验 (2×2) | 模拟 p 值 (simulate.p.value) | — |
| **线性回归** | 残差正态 + 方差齐 + 无强影响点 | OLS 线性回归 | 稳健标准误 (HC SE) | 加权最小二乘 (WLS) | 分位数回归 / 广义线性模型 |
| **Logistic 回归** | 线性 logit + 无完全分离 | 标准 Logistic 回归 | Firth 罚似然 Logistc (brglm) | 精确 Logistic (logistf) | 随机森林 / XGBoost |
| **Cox 比例风险** | PH 假设 (Schoenfeld 残差) | Cox 回归 | 分层 Cox (strata) | 时依系数 (tt()) | Aalen 加性模型 / 参数生存模型 |
| **Poisson 回归** | 均值 = 方差 (无过度离散) | Poisson 回归 | 负二项回归 (NB) | 零膨胀 Poisson (ZIP) | 零膨胀负二项 (ZINB) |
| **生存分析 (KM)** | — | KM + Log-rank | 分层 Log-rank | Cox 回归校正 | 竞争风险 (Fine-Gray) |
| **ROC 分析** | — | 标准 ROC + AUC | 偏 AUC (pAUC) | 净重分类改善度 (NRI) | 决策曲线分析 (DCA) |
| **倾向性评分** | 平衡性 (SMD < 0.1) | PSM 匹配 | 卡钳匹配 (0.2 SD) | IPTW 加权 | 双重稳健估计 (DR) |
| **Overlapping Weighting** | 平衡性 (SMD < 0.1) | OW 加权 | — | IPTW 对比 | 双重稳健估计 (DR) |
| **机器学习预测** | 过拟合 (CV AUC-训练AUC < 0.05) | RF / XGBoost / LightGBM | Elastic Net | SHAP 可解释性 | 回退传统回归 |

### 8.2 降级流程

```
分析方法选定
    │
    ├── 假设检验
    │     ├── ✅ 通过 → 使用首选方法
    │     ├── ⚠️ 边界 (p 0.05-0.10) → 检查 Q-Q 图 + 效应量
    │     │     ├── 视觉判断 OK → 使用首选 + 备注
    │     │     └── 视觉判断不 OK → 首轮降级
    │     └── ❌ 违反 → 首轮降级
    │
    ├── 首轮降级
    │     ├── 结果合理 → 使用 + 在 SAP 偏差中说明
    │     └── 仍违反假设 → 次轮降级
    │
    ├── 次轮降级
    │     ├── 结果合理 → 使用 + 说明
    │     └── 仍不可行 → 终极降级
    │
    └── 终极降级
          ├── 方法可行 → 使用 + 强调方法学局限性
          └── 所有方法均不可行 → [SKIP] + 报告中注明原因
```

### 8.3 方法降级文档化模板

每次降级应在分析报告中记录：

```
[方法降级记录]
- 首选方法: [方法名]
- 违反假设: [具体违反项及检验结果]
- 降级路径: [首轮 → 次轮 → 最终]
- 最终使用: [方法名]
- 对结论影响: [影响评估，如区间宽度变化]
```

### 8.4 降级决策示例

| 场景 | 首选 | 检测到 | 降级步骤 | 说明 |
|------|------|--------|---------|------|
| 两组年龄比较 | t 检验 | 非正态分布 (p=0.003) | t → MWU | MWU 检验效率约为 t 的 95% |
| 手术后生存分析 | Cox 回归 | PH 假设违反 (p=0.02) | Cox → 分层 Cox → Aalen | 分层 Cox 对治疗效应无影响 |
| 药物副作用率 | 卡方检验 | 40% 单元格期望频数<5 | 卡方 → Fisher → 模拟 p | Fisher 适用于 2×2，模拟适用于大表 |
| BMI-血压回归 | OLS | 异方差 (BP 检验 p<0.001) | OLS → HC SE → WLS | HC SE 是最简单的修复 |

## 9. 质量控制检查清单

### 分析前
- [ ] 数据清理完成
- [ ] 缺失数据模式分析
- [ ] 异常值检查
- [ ] 分布检验 (正态性)

### 分析中
- [ ] 方法选择合理性
- [ ] 假设检验
- [ ] 多重比较校正
- [ ] 敏感性分析

### 分析后
- [ ] 效应量报告
- [ ] 置信区间
- [ ] 临床意义解释
- [ ] 局限性讨论

---

## 10. 统计方法指南引用

> ⭐ 本目录的方法学依据可参考 `shared/statistics-methods/` 中的 55 章《统计与方法指南》。
> 以下列出每个方法分类对应的章节，便于深入查阅原始方法学出处。

| 方法分类 | 对应章节 | 关键参考文献 |
|---------|---------------|------------|
| 描述性统计 | ch32（边际效应） | 参见 `shared/statistics-methods/chapters/ch32-marginal-effects.md` |
| 组间比较（t 检验/ANOVA） | ch33（协变量调整） | `shared/statistics-methods/chapters/ch33-covariate-adjustment.md` |
| Logistic 回归 | **ch15**（Logistic 回归）**ch16**（诊断） | `ch15-logistic-regression.md` + `ch16-logistic-regression-diagnostics.md` |
| Cox 回归/生存分析 | **ch10**（时间至事件分析） | `ch10-time-to-event-analysis.md` |
| 诊断试验/ROC | **ch23**（决策曲线分析）**ch36**（FROC）**ch39**（C统计量） | `ch23-decision-curve-analysis.md` |
| 倾向性评分 | **ch35**（倾向性评分） | `ch35-propensity-scores.md` |
| 多重插补 | **ch12**（缺失数据）**ch20**（多重插补） | `ch12-missing-data.md` + `ch20-multiple-imputation.md` |
| Meta 分析 | **ch26**（Meta 分析）**ch37**（随机效应 Meta 分析） | `ch26-meta-analysis.md` + `ch37-random-effects-meta-analysis.md` |
| 多水平/混合模型 | **ch14**（MMRM）**ch38**（分层贝叶斯） | `ch14-mixed-models-for-repeated-measures.md` |
| 样本量计算 | **ch06**（样本量计算）**ch07**（MCID） | `ch06-sample-size-calculations.md` + `ch07-minimal-clinically-important-difference.md` |
| 多重比较 | **ch18**（多重比较方法）**ch19**（关口策略） | `ch18-multiple-comparisons-methods.md` |
| 效应量（OR/HR/NNT） | **ch31**（OR）**ch17**（NNT） | `ch31-odds-ratio.md` + `ch17-number-needed-to-treat.md` |
| 因果推断（DID/MR） | **ch24**（双重差分）**ch45**（孟德尔随机化）**ch30**（中介分析） | `ch24-difference-in-differences.md` |
| 混杂控制（E值） | **ch28**（E值）**ch29**（指示性混杂） | `ch28-e-value.md` + `ch29-indication-bias.md` |
| 研究设计（RCT/非劣效性） | **ch01**（非劣效性）**ch04**（整群随机）**ch05**（阶梯楔形） | `shared/statistics-methods/INDEX.md` 第一节 |
| 贝叶斯分析 | **ch22**（贝叶斯分析） | `ch22-bayesian-analysis.md`



