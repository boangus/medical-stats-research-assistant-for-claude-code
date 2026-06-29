# 统计方法选择器 → MSRA 映射表

> 将 `stat-method-selector/decision-tree.json` 中的112个方法叶子节点映射到 MSRA 的统计指南章节、R/Python 实现和参考文献。
> 本文件供 `analysis-plan` Skill 在方法选择阶段使用。

---

## 使用说明

1. 在 `decision-tree.json` 中到达叶子节点后，用 `method_en` 查找本映射表
2. 获取对应的 MSRA 章节编号（用于深入参考）和 R/Python 实现指引
3. 每次推荐必须引用 `references.md` 中的文献依据

---

## 一、比较差异 (compare)

### 连续结局 — 参数方法

| method_en | 中文名 | MSRA 章节 | R 实现 | Python 实现 | 文献依据 |
|-----------|--------|-----------|--------|-------------|---------|
| One-sample t-test | 单样本t检验 | — | `t.test(x, mu=mu0)` | `scipy.stats.ttest_1samp` | Mishra(22-3)+PMC8483143 |
| Independent t-test | 独立样本t检验 | — | `t.test(y~g, var.equal=TRUE)` | `scipy.stats.ttest_ind` | Mishra(22-4)+Sungur |
| Welch t-test | Welch t检验 | — | `t.test(y~g)` (默认) | `scipy.stats.ttest_ind(equal_var=False)` | Mishra(22-4)+PMC8483143 |
| Paired t-test | 配对t检验 | — | `t.test(y1, y2, paired=TRUE)` | `scipy.stats.ttest_rel` | Mishra(22-4)+Sungur |
| One-way ANOVA | 单因素方差分析 | — | `aov(y~g)` / `anova_test()` | `scipy.stats.f_oneway` | Mishra(22-4)+Sungur |
| Welch ANOVA | Welch方差分析 | — | `welch_anova_test()` (rstatix) | `scipy.stats.f_oneway` + Welch | Sungur+PMC8483143 |
| Two-way ANOVA | 双因素方差分析 | — | `aov(y~A*B)` | `statsmodels.formula.api.ols` + `anova_lm` | Mishra(22-4)+Sungur |
| Three-way ANOVA | 三因素方差分析 | — | `aov(y~A*B*C)` | `statsmodels.formula.api.ols` + `anova_lm` | Mishra(22-4) |
| Repeated measures ANOVA | 重复测量方差分析 | ch14 MMRM | `anova_test(dv=., wid=., within=.)` | `Pingouin.rm_anova` | Mishra(22-4)+Sungur |
| Split-plot ANOVA | 裂区设计方差分析 | — | `aov(y~A*B+Error(S/A))` | `statsmodels` MixedLM | Mishra(22-4) |
| Crossover design analysis | 交叉设计分析 | ch01 | `aov(y~Treatment+Period+Sequence+Error(Subject))` | `statsmodels` MixedLM | Mishra(22-4) |
| ANCOVA | 协方差分析 | — | `aov(y~Group+Covariate)` | `statsmodels.formula.api.ols` | Mishra(22-4) |
| Hotelling's T² | Hotelling T²检验 | — | `HotellingsT2()` (Hotelling包) | `scipy.stats` + 自定义 | Mishra(22-3) |
| MANOVA | 多元方差分析 | — | `manova <- Manova(lm(cbind(y1,y2)~g))` | `statsmodels.multivariate.manova` | Mishra(22-3) |

### 连续结局 — 非参数方法

| method_en | 中文名 | MSRA 章节 | R 实现 | Python 实现 | 文献依据 |
|-----------|--------|-----------|--------|-------------|---------|
| Wilcoxon signed-rank test | Wilcoxon符号秩检验 | — | `wilcox.test(x, mu=mu0)` | `scipy.stats.wilcoxon` | Mishra(22-3)+PMC8483143 |
| Mann-Whitney U test | Mann-Whitney U检验 | — | `wilcox.test(y~g)` | `scipy.stats.mannwhitneyu` | Mishra(22-3)+PMC8483143 |
| Brunner-Munzel test | Brunner-Munzel检验 | — | `brunnermunzel.test()` (brunnermunzel包) | `scipy.stats.brunnermunzel` | Brunner&Munzel 2000 |
| Kruskal-Wallis H test | Kruskal-Wallis检验 | — | `kruskal.test(y~g)` | `scipy.stats.kruskal` | Mishra(22-3)+PMC8483143 |
| Friedman test | Friedman检验 | — | `friedman.test(y~g|block)` | `scipy.stats.friedmanchisquare` | Mishra(22-3)+PMC8483143 |

### 二分类结局

| method_en | 中文名 | MSRA 章节 | R 实现 | Python 实现 | 文献依据 |
|-----------|--------|-----------|--------|-------------|---------|
| Chi-square test | 卡方检验 | — | `chisq.test()` | `scipy.stats.chi2_contingency` | Mishra(22-3)+PMC8483143 |
| Fisher's exact test | Fisher精确检验 | — | `fisher.test()` | `scipy.stats.fisher_exact` | Mishra(22-3)+PMC8483143 |
| McNemar test | McNemar检验 | — | `mcnemar.test()` | `statsmodels.stats.contingency_tables` | McNemar 1947 |
| Cochran's Q test | Cochran Q检验 | — | `cochran_q_test()` (rstatix) | 自定义 | Mishra(22-3) |
| Bowker's test | Bowker对称性检验 | — | `mcnemar.test()` (扩展) | 自定义 | Mishra(22-3) |
| R×C Chi-square | R×C列联表卡方 | — | `chisq.test()` | `scipy.stats.chi2_contingency` | Mishra(22-3)+PMC8483143 |
| Cochran-Armitage trend test | 趋势检验 | — | `prop.trend.test()` | `statsmodels.stats.proportion` | PMC8483143 |

### 有序结局

| method_en | 中文名 | MSRA 章节 | R 实现 | Python 实现 | 文献依据 |
|-----------|--------|-----------|--------|-------------|---------|
| Proportional odds ordinal logistic | 有序Logistic回归 | ch15 | `polr()` (MASS) / `clm()` (ordinal) | `statsmodels.miscmodels.ordinal_model` | Agresti 2013+Venkatesh |
| Partial proportional odds model | 偏比例优势模型 | — | `clm()` + nominal_effects | 自定义 | Agresti 2013 |

---

## 二、关联/相关 (correlation)

| method_en | 中文名 | MSRA 章节 | R 实现 | Python 实现 | 文献依据 |
|-----------|--------|-----------|--------|-------------|---------|
| Pearson correlation | Pearson相关 | — | `cor.test(x, y, method="pearson")` | `scipy.stats.pearsonr` | Mishra(22-3)+PMC8483143 |
| Spearman rank correlation | Spearman秩相关 | — | `cor.test(x, y, method="spearman")` | `scipy.stats.spearmanr` | Mishra(22-3)+PMC8483143 |
| Kendall's tau | Kendall τ | — | `cor.test(x, y, method="kendall")` | `scipy.stats.kendalltau` | PMC8483143 |
| Kendall's tau-b | Kendall τ-b | — | `cor.test(x, y, method="kendall")` | `scipy.stats.kendalltau` | PMC8483143 |
| Chi-square test of independence | 卡方独立性检验 | — | `chisq.test()` | `scipy.stats.chi2_contingency` | Mishra(22-3)+PMC8483143 |
| Cramér's V | Cramér V系数 | — | `cramersV()` (rstatix) | `scipy.stats.contingency.association` | PMC8483143 |
| Point-biserial correlation | 点二列相关 | — | `cor.test(x, as.numeric(y))` | `scipy.stats.pointbiserialr` | PMC8483143 |

---

## 三、预测 (predict)

| method_en | 中文名 | MSRA 章节 | R 实现 | Python 实现 | 文献依据 |
|-----------|--------|-----------|--------|-------------|---------|
| Multiple linear regression | 多元线性回归 | — | `lm(y~x1+x2)` | `statsmodels.api.OLS` | Venkatesh+PMC8483143 |
| Logistic regression | Logistic回归 | ch15, ch16 | `glm(y~x, family=binomial)` | `statsmodels.api.Logit` | Venkatesh+PMC8483143 |
| Firth's penalized logistic | Firth惩罚Logistic | — | `logistf()` (logistf包) | `firth_regression` (sklearn-ext) | Firth 1993 |
| RCS-Logistic regression | RCS-Logistic回归 | — | `lrm(y~rcs(x,3))` (rms包) | `patsy.dmatrix` + GLM | Harrell 2015 |
| Ordinal logistic regression | 有序Logistic回归 | — | `polr()` (MASS) | `statsmodels.miscmodels.ordinal_model` | Agresti 2013 |
| Multinomial logistic regression | 多项Logistic回归 | — | `multinom()` (nnet) | `sklearn.linear_model.LogisticRegression(multi_class='multinomial')` | Agresti 2013 |
| Poisson regression | 泊松回归 | — | `glm(y~x, family=poisson)` | `statsmodels.api.GLM(family=Poisson)` | McCullagh&Nelder 1989 |
| Negative binomial regression | 负二项回归 | — | `glm.nb()` (MASS) | `statsmodels.api.NegativeBinomial` | McCullagh&Nelder 1989 |
| Zero-inflated Poisson | 零膨胀泊松 | — | `zeroinfl()` (pscl) | `statsmodels.api.ZeroInflatedPoisson` | McCullagh&Nelder 1989 |
| Zero-inflated negative binomial | 零膨胀负二项 | — | `zeroinfl(, dist="negbin")` (pscl) | `statsmodels.api.ZeroInflatedNegativeBinomial` | McCullagh&Nelder 1989 |
| LASSO regression | LASSO回归 | — | `glmnet(alpha=1)` | `sklearn.linear_model.LassoCV` | Venkatesh |
| Ridge regression | 岭回归 | — | `glmnet(alpha=0)` | `sklearn.linear_model.RidgeCV` | Hoerl&Kennard 1970 |
| Elastic Net | 弹性网络 | — | `glmnet(alpha=0.5)` | `sklearn.linear_model.ElasticNetCV` | Venkatesh |
| Random forest feature importance | 随机森林特征重要性 | — | `randomForest()` | `sklearn.ensemble.RandomForestClassifier` | Venkatesh |

---

## 四、因果推断 (causal)

| method_en | 中文名 | MSRA 章节 | R 实现 | Python 实现 | 文献依据 |
|-----------|--------|-----------|--------|-------------|---------|
| Propensity score matching (PSM) | 倾向性评分匹配 | ch35 | `MatchIt()` | `sklearn` + 自定义 | Rosenbaum&Rubin 1983; Austin 2011 |
| Inverse probability of treatment weighting (IPTW) | 逆概率处理加权 | ch35 | `weightit()` (cobalt) | `statsmodels` + 自定义 | Austin 2011 |
| Doubly robust estimation | 双重稳健估计 | ch35 | `WeightIt` + `lm` | `DoWhy` + `EconML` | Austin 2011 |
| Mediation analysis (Baron-Kenny) | Baron-Kenny中介分析 | ch30 | `mediation` 包 | `statsmodels` + `mediation` | Hayes 2017 |
| Causal mediation analysis | 因果中介分析 | ch30 | `mediation` 包 (反事实) | `DoWhy` | VanderWeele 2016 |
| Mendelian randomization (IVW) | 孟德尔随机化IVW | ch45 | `MendelianRandomization` 包 | `MR-Base` API | Burgess 2015 |
| MR-Egger regression | MR-Egger回归 | ch45 | `MendelianRandomization` | `MR-Base` API | Burgess 2015 |
| Difference-in-differences (DID) | 双重差分法 | ch24 | `fixest` / `did` 包 | `statsmodels` + `linearmodels` | Callaway&Sant'Anna 2021 |
| E-value sensitivity analysis | E-value敏感性分析 | ch28 | `EValue` 包 | `evalue` (Python) | VanderWeele&Ding 2017 |

---

## 五、生存分析 (survival)

| method_en | 中文名 | MSRA 章节 | R 实现 | Python 实现 | 文献依据 |
|-----------|--------|-----------|--------|-------------|---------|
| Kaplan-Meier estimator | Kaplan-Meier估计 | ch10 | `survfit(Surv(time,status)~1)` | `lifelines.KaplanMeierFitter` | Mishra(22-3)+PMC8483143 |
| Log-rank test | Log-rank检验 | ch10 | `survdiff(Surv(time,status)~g)` | `lifelines.statistics.logrank_test` | Mishra(22-3)+PMC8483143 |
| Cox proportional hazards regression | Cox PH回归 | ch10 | `coxph(Surv(time,status)~x)` | `lifelines.CoxPHFitter` | Venkatesh+Mishra |
| Stratified Cox model | 分层Cox模型 | ch10 | `coxph(Surv~x+strata(S))` | `lifelines.CoxPHFitter(strata=)` | Mishra |
| Restricted mean survival time (RMST) | 限制性平均生存时间 | ch10 | `survRM2` 包 | `lifelines` + 自定义 | — |
| Fine-Gray competing risks model | Fine-Gray竞争风险模型 | ch10 | `crr()` (cmprsk) | `lifelines` + `sksurv` | Fine&Gray 1999 |
| Cause-specific hazard model | 原因别风险模型 | ch10 | `coxph()` + 竞争事件编码 | `lifelines.CoxPHFitter` | Fine&Gray 1999 |

---

## 六、诊断试验 (diagnostic)

| method_en | 中文名 | MSRA 章节 | R 实现 | Python 实现 | 文献依据 |
|-----------|--------|-----------|--------|-------------|---------|
| ROC curve + AUC | ROC曲线+AUC | — | `roc()` (pROC) | `sklearn.metrics.roc_auc_score` | DeLong 1988 |
| Youden index cutoff | Youden指数截断值 | — | `coords(., "best")` (pROC) | `sklearn.metrics` + 自定义 | Youden 1950 |
| DeLong test for AUC comparison | DeLong检验比较AUC | — | `roc.test(., method="delong")` (pROC) | `scipy.stats` + 自定义 | DeLong 1988 |
| Sensitivity/Specificity/PPV/NPV | 敏感度/特异度/PPV/NPV | — | 自定义（四格表） | `sklearn.metrics` | Jaeschke 1994 |
| Likelihood ratio (LR+/LR-) | 似然比 | — | 自定义 | 自定义 | Jaeschke 1994 |
| Precision-Recall curve | 精确率-召回率曲线 | — | `pr.curve()` (PRROC) | `sklearn.metrics.precision_recall_curve` | — |

---

## 七、一致性/信度 (reliability)

| method_en | 中文名 | MSRA 章节 | R 实现 | Python 实现 | 文献依据 |
|-----------|--------|-----------|--------|-------------|---------|
| ICC (model selection required) | 组内相关系数 | — | `icc()` (irr) | `pingouin.intraclass_corr` | Koo&Li 2016 |
| Cohen's Kappa | Cohen Kappa系数 | — | `kappa2()` (irr) | `sklearn.metrics.cohen_kappa_score` | Landis&Koch 1977 |
| Fleiss' Kappa | Fleiss Kappa系数 | — | `kappam.fleiss()` (irr) | `statsmodels.stats.inter_rater` | Landis&Koch 1977 |
| Weighted Kappa | 加权Kappa | — | `kappa2(., weight="equal")` (irr) | `sklearn.metrics.cohen_kappa_score(weights=)` | Landis&Koch 1977 |
| Gwet's AC1 | Gwet AC1系数 | — | `agree.coeff()` (irrCAC) | 自定义 | Stolyar 2024 |
| Bland-Altman analysis | Bland-Altman分析 | — | `bland.altman.stats()` (BlandAltmanLeh) | 自定义 | Koo&Li 2016 |
| Bowker's test of symmetry | Bowker对称性检验 | — | `mcnemar.test()` (扩展) | 自定义 | — |

---

## 八、等效/非劣效 (equivalence_non_inferiority)

| method_en | 中文名 | MSRA 章节 | R 实现 | Python 实现 | 文献依据 |
|-----------|--------|-----------|--------|-------------|---------|
| TOST (Two One-Sided Tests) | 双单侧检验 | ch01 | `tost()` (TOSTER包) | `statsmodels.stats.proportion` | Schuirmann 1987 |
| Non-inferiority test | 非劣效检验 | ch01 | `tost()` + 单侧 | 自定义 | Piaggio 2012 |

---

## 九、Meta分析 (meta_analysis)

| method_en | 中文名 | MSRA 章节 | R 实现 | Python 实现 | 文献依据 |
|-----------|--------|-----------|--------|-------------|---------|
| Fixed-effect meta-analysis | 固定效应Meta分析 | ch26 | `metagen()` / `metabin()` (meta) | `statsmodels.stats.meta_analysis` | Cochrane Handbook |
| Random-effects meta-analysis (DL) | 随机效应Meta(DL) | ch26 | `metagen(., random=TRUE)` | `statsmodels.stats.meta_analysis` | DerSimonian&Laird 1986 |
| Subgroup analysis | 亚组分析 | ch26 | `update.meta(., subgroup=.)` | 自定义 | Cochrane Handbook |
| Meta-regression | Meta回归 | ch26 | `metareg()` (meta) | 自定义 | Thompson&Higgins 2002 |
| Egger test for publication bias | Egger检验 | ch26 | `metabias()` (meta) | 自定义 | Egger 1997 |
| Funnel plot | 漏斗图 | ch26 | `funnel()` (meta) | `matplotlib` + 自定义 | Egger 1997 |
| I² heterogeneity statistic | I²异质性统计量 | ch26 | `metagen()` 自动输出 | `statsmodels` | Higgins&Thompson 2002 |

---

## 十、缺失数据 (missing_data)

| method_en | 中文名 | MSRA 章节 | R 实现 | Python 实现 | 文献依据 |
|-----------|--------|-----------|--------|-------------|---------|
| Complete case analysis | 完整案例分析 | ch12 | `na.omit()` | `pandas.dropna()` | Rubin 1976 |
| Multiple imputation (MICE) | 多重插补 | ch20 | `mice()` (mice包) | `sklearn.experimental.IterativeImputer` | van Buuren 2018 |
| FIML (Full Information ML) | 全信息最大似然 | ch12 | `lavaan(estimator="ML", missing="fiml")` | `statsmodels` | Enders 2010 |
| Pattern mixture model | 模式混合模型 | ch12 | 自定义 | 自定义 | Little&Rubin 2019 |
| IPW selection model | IPW选择模型 | ch12 | 自定义 | 自定义 | Little&Rubin 2019 |

---

## 十一、多重比较 (multiple_comparisons)

| method_en | 中文名 | MSRA 章节 | R 实现 | Python 实现 | 文献依据 |
|-----------|--------|-----------|--------|-------------|---------|
| Bonferroni correction | Bonferroni校正 | ch18 | `p.adjust(., "bonferroni")` | `statsmodels.stats.multitest.multipletests` | Holm 1979 |
| Holm step-down | Holm逐步下降法 | ch18 | `p.adjust(., "holm")` | `statsmodels.stats.multitest.multipletests` | Holm 1979 |
| Hochberg step-up | Hochberg逐步上升法 | ch18 | `p.adjust(., "hochberg")` | `statsmodels.stats.multitest.multipletests` | Hochberg 1988 |
| Benjamini-Hochberg FDR | BH错误发现率 | ch18 | `p.adjust(., "fdr")` | `statsmodels.stats.multitest.multipletests` | Benjamini&Hochberg 1995 |
| Dunnett test | Dunnett检验 | ch18 | `glht(., linfct=mcp(g="Dunnett"))` (multcomp) | `scipy.stats` + 自定义 | Dunnett 1955 |
| Tukey HSD | Tukey HSD | — | `TukeyHSD()` | `scipy.stats.tukey_hsd` | — |
| Dunn's test | Dunn检验 | — | `dunn_test()` (rstatix) | `scikit_posthocs.posthoc_dunn` | — |
| Games-Howell | Games-Howell | — | `games_howell_test()` (rstatix) | `scikit_posthocs.posthoc_gameshowell` | — |
| Graphical approach (Bretz) | 图形化多重比较 | ch18 | `gMCPLite` 包 | 自定义 | Bretz 2009 |

---

## 十二、贝叶斯分析 (bayesian)

| method_en | 中文名 | MSRA 章节 | R 实现 | Python 实现 | 文献依据 |
|-----------|--------|-----------|--------|-------------|---------|
| Bayesian one-sample t-test | 贝叶斯单样本t检验 | ch22 | `ttestBF()` (BayesFactor) | `pingouin.bayesian_ttest` | Rouder 2009 |
| Bayesian independent t-test | 贝叶斯独立t检验 | ch22 | `ttestBF(formula=y~g)` | `pingouin.bayesian_ttest` | Rouder 2009 |
| Bayesian paired t-test | 贝叶斯配对t检验 | ch22 | `ttestBF(x=diff)` | `pingouin.bayesian_ttest` | Rouder 2009 |
| Bayesian one-way ANOVA | 贝叶斯单因素ANOVA | ch22 | `anovaBF(y~g)` | `pingouin` + 自定义 | Kruschke 2015 |
| Bayesian linear regression | 贝叶斯线性回归 | ch22 | `brm()` (brms) | `PyMC` / `bambi` | Gelman 2013 |
| Bayesian logistic regression | 贝叶斯Logistic回归 | ch22 | `brm(., family=bernoulli)` | `PyMC` / `bambi` | Gelman 2013 |
| Bayes factor for contingency table | 贝叶斯列联表 | ch22 | `contingencyTableBF()` | `pingouin` + 自定义 | Kass&Raftery 1995 |
| Bayes factor for correlation | 贝叶斯相关 | ch22 | `correlationBF()` | `pingouin` + 自定义 | Kass&Raftery 1995 |
| Bayesian meta-analysis | 贝叶斯Meta分析 | ch22 | `brm()` (brms) | `PyMC` | Gelman 2013 |
| Bayesian survival analysis | 贝叶斯生存分析 | ch22 | `brm()` + survival | `PyMC` + `lifelines` | Gelman 2013 |
| Bayesian diagnostic test | 贝叶斯诊断试验 | ch22 | 自定义 | 自定义 | Gelman 2013 |
| Bayesian equivalence test | 贝叶斯等效性检验 | ch22 | `tostBF()` (BayesFactor) | 自定义 | Kass&Raftery 1995 |
| Bayesian mediation analysis | 贝叶斯中介分析 | ch22 | `brm()` 多方程 | `PyMC` + 自定义 | Gelman 2013 |

---

## 十三、纵向分析 (longitudinal)

| method_en | 中文名 | MSRA 章节 | R 实现 | Python 实现 | 文献依据 |
|-----------|--------|-----------|--------|-------------|---------|
| GEE (Generalized Estimating Equations) | GEE广义估计方程 | ch14 | `geeglm()` (geepack) | `statsmodels.genmod.generalized_estimating_equations` | Venkatesh; Gelman&Hill |
| Linear mixed model (LMM) | 线性混合模型 | ch14 | `lmer()` (lme4) | `statsmodels.regression.mixed_linear_model` | Venkatesh; Gelman&Hill |
| Generalized linear mixed model (GLMM) | 广义线性混合模型 | ch14 | `glmer()` (lme4) | `statsmodels` + `PyMC` | Venkatesh; Gelman&Hill |

---

## 十四、降维/结构验证 (dimension_reduction)

| method_en | 中文名 | MSRA 章节 | R 实现 | Python 实现 | 文献依据 |
|-----------|--------|-----------|--------|-------------|---------|
| PCA (Principal Component Analysis) | 主成分分析 | — | `prcomp()` | `sklearn.decomposition.PCA` | PMC8483143 |
| EFA (Exploratory Factor Analysis) | 探索性因子分析 | — | `factanal()` | `sklearn.decomposition.FactorAnalysis` | PMC8483143 |
| CFA (Confirmatory Factor Analysis) | 验证性因子分析 | — | `cfa()` (lavaan) | `semopy` | Hu&Bentler 1999 |
| SEM (Structural Equation Modeling) | 结构方程模型 | — | `sem()` (lavaan) | `semopy` | Hu&Bentler 1999 |

---

## 十五、描述性统计 (descriptive)

| method_en | 中文名 | MSRA 章节 | R 实现 | Python 实现 | 文献依据 |
|-----------|--------|-----------|--------|-------------|---------|
| Descriptive statistics | 描述性统计 | — | `summary()` / `gtsummary::tbl_summary()` | `pandas.describe()` | PMC8483143 |
| Normality test (Shapiro-Wilk) | 正态性检验 | — | `shapiro.test()` | `scipy.stats.shapiro` | PMC8483143 |
| Homogeneity of variance (Levene) | 方差齐性检验 | — | `leveneTest()` (car) | `scipy.stats.levene` | PMC8483143 |

---

## 效应量解释标准速查

| 效应量 | 小 | 中 | 大 | 来源 |
|--------|---|----|----|------|
| Cohen's d | 0.2 | 0.5 | 0.8 | Cohen, 1988 |
| Pearson r / Spearman ρ | <0.3 | 0.3-0.5 | >0.5 | Cohen, 1988 |
| Cramér's V (df=1) | 0.1 | 0.3 | 0.5 | Cohen, 1988 |
| η² / 偏η² | 0.01 | 0.06 | 0.14 | Cohen, 1988 |
| ICC | <0.50差 | 0.50-0.75中 | ≥0.75好 | Koo & Li, 2016 |
| Kappa | <0.41差-一般 | 0.41-0.60中 | ≥0.61高度 | Landis & Koch, 1977 |
| SMD (PSM均衡) | — | <0.1为均衡 | — | Austin, 2011 |
