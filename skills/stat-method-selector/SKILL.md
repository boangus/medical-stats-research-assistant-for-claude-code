---
name: stat-method-selector
description: 帮助用户选择最合适的统计方法。基于已发表方法学论文构建的决策树，支持问卷式和自然语言描述两种输入方式。当用户需要选择统计方法、不确定用什么检验、询问"我的数据该用什么统计方法"时使用。
layer: functional
source: https://github.com/ApintLin/stat-method-selector
license: MIT
version: 2.2
author: ApintLin
---

# 统计方法选择器

> **来源声明**: 本技能整合自 [ApintLin/stat-method-selector](https://github.com/ApintLin/stat-method-selector)（MIT License, v2.2）。详细的第三方许可信息见 `THIRD-PARTY-NOTICES.md`。

帮用户从"不知道用什么方法"到"就是这个方法"。

## 核心逻辑

读 `decision-tree.json` 决策树。6-8层维度：研究目标 → 结局类型 → 组数 → 分布 → 设计类型（含诊断节点） → 推荐方法。共15个根目标（含贝叶斯分析），112个叶子方法节点（含15个贝叶斯方法）。覆盖三因素ANOVA、裂区设计、交叉设计等实验设计，以及Bowker检验、Gwet's AC1、CFA、Cause-specific Hazard、Precision-Recall曲线等专业方法。

**每次为用户推荐统计方法时，必须先阅读 `references.md` 参考资料文件**，其中包含所有决策树所依据的原始文献的详细内容、方法选择速查表和效应量解释标准。每次推荐必须引用对应文献作为方法学依据。

## 适用范围

本决策树侧重**医学与健康科学**领域的统计方法选择。决策维度（结局类型、组数、分布特性、设计类型）基于已发表的医学方法学文献构建。虽然多数方法（t检验、ANOVA、回归等）在其他领域通用，但需注意：
- 因果推断分支侧重医学观察性研究（PSM、MR、DID）
- 诊断试验分支（ROC、DeLong检验、似然比）专门针对临床诊断场景
- 生存分析分支针对医学随访数据（Cox PH、Fine-Gray竞争风险）
- 对于社会科学、经济学等领域的特殊方法（如结构方程模型细节、实验经济学设计），可能需要补充领域特定的参考文献

## 两种使用路径

### 路径一：问卷式

用户输入触发词（如"帮我选统计方法"、"问卷"、"一步步来"）→ 逐题引导。

规则：
1. **每次只问一个问题**，列出选项（标号 1/2/3）
2. 用户回答后，推进到树的下一层
3. 通常5-8步内到达叶子节点
4. 输出推荐卡片（见下方格式）

### 路径二：自然语言解析

用户直接描述研究场景 → 从描述中提取结构化参数 → 在 JSON 树中查找匹配路径 → 输出推荐 + 推理链。

提取参数方法：从用户描述中识别以下维度，映射到 JSON 的 `value`：
- goal: "比较差异"/"看关联"/"预测"/"因果"/"生存"/"降维"/"纵向"/"Meta分析"/"诊断试验"/"等效非劣效"/"缺失数据"/"多重比较"/"描述"/"贝叶斯分析"
- outcome_type: "连续"/"二分类"/"有序分类"/"计数"/"多因变量"
- num_groups: "1"/"2"/"3plus"
- normality: "normal"/"non_normal"
- design: "independent"/"paired"/"repeated"
- num_factors: "1"/"2"/"nested" (多因素设计)
- has_covariate: true/false (是否需要控制协变量，ANCOVA相关)
- multicollinearity: "low"/"high" (预测模型中共线性诊断)
- epv: "adequate"/"insufficient" (Logistic回归中每变量事件数)
- heterogeneity: "low"/"high" (Meta分析中I²异质性)
- missing_mechanism: "mcar"/"mar"/"mnar" (缺失数据机制)
- mc_scenario: "all_pairwise"/"vs_control"/"high_dim" (多重比较场景)
- eq_goal: "equivalence"/"non_inferiority" (等效性/非劣效性目标)
- diag_goal: "single_test"/"compare_tests" (诊断试验评价目标)

**如果某个维度信息缺失**，追问该维度的问题（只问缺失的）。

**推理链示例：**
> 您描述：比较三组治疗方案对血压的影响，数据不服从正态分布
> → 研究目标：比较差异 → 结局：连续变量 → 3组 → 独立样本 → 非正态
> → 推荐：Kruskal-Wallis H检验 + Dunn事后检验

### 输出格式

```markdown
## 推荐方法：{方法中文名}
**英文名：** {method_en}

**适用条件：** {description}

**前提假设：**
- 假设1
- 假设2

**假设不满足时：** {if_violated}

**SPSS操作：** {spss}
**R代码：** `{r_code}`
**效应量：** {effect_size}
**样本量要求：** {sample_size}
**功效分析：** {power_analysis}

**文献依据：** {reference}

**备选方法：** {alternative_method}（当存在明确的替代方法时显示）
**备选适用场景：** {alternative_when}
**贝叶斯替代：** {bayesian_alternative}（当存在贝叶斯对应方法时显示）
```

如果方法存在备选推荐（alternative_method），应主动提示用户，说明在什么条件下选择备选方法更合适。

如果有诊断注意事项（非参数方法或有特殊诊断要求的方法）：
```markdown
**诊断注意事项：** {diagnostic_tips}
```

如果用户问"为什么是这个方法"，解释推理链。不要发明新方法，只推荐 JSON 树中已定义的方法。

### 边界场景指南

当用户场景同时匹配两条可能路径时，以下对比帮助区分：

| 情境 | 选项A | 选项B | 选择标准 |
|------|-------|-------|---------|
| 纵向数据 | GEE (边际模型) | LMM/GLMM (条件模型) | GEE回答"人群平均效应"，LMM回答"个体特异轨迹"。GEE对随机效应分布不敏感，LMM可建模随机斜率 |
| 非正态+方差不齐 | Welch ANOVA | Kruskal-Wallis | 轻中度非正态+N较大 → Welch ANOVA(稳健)；严重偏态+N较小 → Kruskal-Wallis |
| 有序结局(2组) | Mann-Whitney U | 有序Logistic回归 | 无需校正协变量 → Mann-Whitney；需校正混杂 → 有序Logistic |
| 计数过离散 | 负二项回归 | Quasi-Poisson | NB给出完整似然(AIC/BIC可用)；Quasi-Poisson仅调整标准误 |
| Meta异质性高 | 随机效应+亚组分析 | Meta回归 | 亚组分析(分类协变量) vs Meta回归(连续协变量); Meta回归需每协变量≥10项研究 |
| 缺失数据处理 | 多重插补MICE | FIML | MICE适用于一般缺失场景；FIML在SEM/混合模型中自然集成 |
| 多重比较(m~10) | Bonferroni/Holm | Hochberg | Hochberg功效更高但要求检验独立/正相关；不确定时用Holm(无需独立性假设) |
| 单组连续+非正态 | 单样本Wilcoxon | Bootstrap置信区间 | 小样本(n<15) → Wilcoxon更保守; 中等样本 → Bootstrap可提供更精确的区间估计 |
| 竞争风险(>1事件类型) | Fine-Gray SHR | Cause-specific Hazard | Fine-Gray回答"预测个体风险"问题(SHR); CSH回答"病因效应"问题(HR) |
| 不平衡结局+诊断 | ROC曲线 | Precision-Recall曲线 | 事件率10%-90% → ROC; 事件率<10%或>90% → PR曲线(AUC不依赖TN) |
| 信度+极端患病率 | Cohen's Kappa | Gwet's AC1 | 患病率5%-95% → Kappa; 患病率<5%或>95% → Gwet's AC1(避免Kappa悖论) |
| 因子分析 | EFA | CFA | 无先验假设 → EFA探索结构; 有理论假设 → CFA检验模型拟合 |
| 信度+多因子模型 | ICC/Alpha | SEM-based omega | 单因子等价测量 → ICC/Alpha; 多因子或相关误差 → omega(不假设tau-equivalence) |
| 配对分类+>2类别 | McNemar | Bowker | 2×2配对四格表 → McNemar; k×k配对表(k>2) → Bowker对称性检验 |
| 实验设计选择 | 平行组设计 | 交叉设计 | 无法排除延滞效应 → 平行组; 洗脱期充分 → 交叉设计(样本量~1/4) |
| 重复测量+组间因素 | RM ANOVA | 裂区/混合ANOVA | 纯组内因素 → RM ANOVA; 同时含组间+组内因素 → 裂区设计 |
| 多因素(>2) | 二因素ANOVA | 三因素ANOVA | 2个分类自变量 → Two-way; 3个分类自变量 → Three-way(注意三阶交互样本量需求) |

### 贝叶斯路径（第15根目标）

当用户偏好贝叶斯框架（报告Bayes因子而非p值、量化不确定性为概率分布）时：
1. 决策树中询问贝叶斯分析目标（比较差异/相关分析/回归预测/Meta分析）
2. 推荐贝叶斯对应方法，输出包含Bayes因子(BF)和后验分布
3. **Bayes因子解读标准** (Kass & Raftery, 1995): BF10>3=中等证据, BF10>10=强证据, BF10>30=极强证据, BF10>100=决定性证据
4. 每个贝叶斯方法在 `bayesian_alternative` 字段中与频率派方法双向关联
5. 贝叶斯方法覆盖：t检验(单样本/独立/配对)、ANOVA(独立/重复测量)、相关分析、回归(线性/Logistic/计数)、列联表、Meta分析、生存分析、中介分析、诊断试验评价、等效性检验

**CLT使用注意：** n≥30是经验准则，不是数学保证。重度偏态分布（收入、住院天数、医疗费用等）即使n>100也应考虑非参数或贝叶斯方法。始终结合Shapiro-Wilk检验和Q-Q图综合判断正态性。

## 参考文献

### 核心决策框架（5篇）

| # | 来源 | 年份 | 贡献 |
|---|------|------|------|
| 1 | Najmi, Sadasivam & Ray, *J Family Med Prim Care* (PMC8483143) | 2021 | 面向临床研究者的5维度决策表，推荐方法与数据类型的直接对应 |
| 2 | Mishra, Pandey, Singh et al., *Ann Card Anaesth* 22(3):297-301 | 2019 | 参数 vs 非参数方法分类决策表，含软件操作指引 |
| 3 | Mishra, Singh, Pandey et al., *Ann Card Anaesth* 22(4):407-411 | 2019 | t检验、ANOVA、ANCOVA的详细操作手册，含实例数据演示 |
| 4 | Venkatesh & Santhosh, *NMO Journal* 19(2):182-188 | 2025 | 描述-比较-关联-预测四域框架，强调效应量和现代推断 |
| 5 | Sungur & Karabulut, *Düzce Med J* 26(3):183-190 | 2024 | 1组/2组/3组+设计的详细决策流程图，含事后检验选择 |

### 特定领域文献（4篇）

| # | 来源 | 年份 | 贡献 |
|---|------|------|------|
| 6 | Stolyar et al., *npj Digital Medicine* 7:258 (Fig.6) | 2024 | 信度评估方法(ICC, Kappa)的可视化决策树 |
| 7 | Koo & Li, *J Chiropr Med* 15(2):155-163 | 2016 | ICC选择的权威指南（10种形式 × 3维度），15000+引用 |
| 8 | Landis & Koch, *Biometrics* 33(1):159-174 | 1977 | Kappa系数解释标准，64000+引用 |
| 9 | Burgess, Daniel, Butterworth, Thompson et al., *Int J Epidemiol* 44(2):484-495 | 2015 | 孟德尔随机化方法学标准，网络MR框架 |

### 因果推断与观察性研究（7篇）

| # | 来源 | 年份 | 贡献 |
|---|------|------|------|
| 10 | Rosenbaum & Rubin, *Biometrika* 70(1):41-55 | 1983 | 倾向性评分方法的开创性论文 |
| 11 | Austin, *Multivar Behav Res* 46(3):399-424 | 2011 | PSM实用方法指南，SMD评估标准 |
| 12 | Austin, *Stat Med* 28(25):3083-3107 | 2009 | PSM均衡诊断标准(SMD<0.1)的方法学文献 |
| 13 | VanderWeele, *Annu Rev Public Health* 37:17-32 | 2016 | 因果中介分析实用指南，反事实框架 |
| 14 | Hayes, *Introduction to Mediation, Moderation, and Conditional Process Analysis*, 2nd ed. Guilford Press | 2017 | PROCESS宏方法学基础，Baron-Kenny框架现代发展 |
| 15 | Angrist & Pischke, *Mostly Harmless Econometrics*. Princeton Univ Press | 2009 | 计量经济学因果推断权威教材(IV, DID, RDD) |
| 16 | Callaway & Sant'Anna, *J Econometrics* 225(2):200-230 | 2021 | 多期DID现代方法学标准 |

### 回归建模与高级方法（5篇）

| # | 来源 | 年份 | 贡献 |
|---|------|------|------|
| 17 | Hoerl & Kennard, *Technometrics* 12(1):55-67 | 1970 | Ridge回归原创文献，处理多重共线性 |
| 18 | Firth, *Biometrika* 80(1):27-38 | 1993 | Firth惩罚似然，解决Logistic小样本偏倚和完全分离 |
| 19 | Harrell, *Regression Modeling Strategies*, 2nd ed. Springer | 2015 | 限制性立方样条(RCS)在回归模型中的应用权威教材 |
| 20 | Gelman & Hill, *Data Analysis Using Regression and Multilevel/Hierarchical Models*. Cambridge | 2007 | 多水平模型/层次模型权威教材 |
| 21 | Fine & Gray, *JASA* 94(446):496-509 | 1999 | 竞争风险模型原创论文，子分布风险(SHR)框架 |

### 补充方法学文献（5篇）

| # | 来源 | 年份 | 贡献 |
|---|------|------|------|
| 22 | Brunner & Munzel, *Biometrical J* 42(1):17-25 | 2000 | Brunner-Munzel检验，分布形状不同时的非参数替代 |
| 23 | VanderWeele & Ding, *Ann Intern Med* 167(4):268-274 | 2017 | E-value敏感性分析，量化未测量混杂影响 |
| 24 | Hu & Bentler, *Struct Equ Modeling* 6(1):1-55 | 1999 | SEM/CFA拟合指数标准(CFI, RMSEA, SRMR) |
| 25 | Altman, *Practical Statistics for Medical Research*. Chapman & Hall/CRC | 1991 | 经典医学统计教科书 |
| 26 | Bland, *An Introduction to Medical Statistics*, 3rd ed. Oxford | 2000 | 医学统计学入门权威教材 |

### Meta分析文献（5篇）

| # | 来源 | 年份 | 贡献 |
|---|------|------|------|
| 27 | DerSimonian & Laird, *Control Clin Trials* 7(3):177-188 | 1986 | 随机效应Meta分析创始文献（29000+引用） |
| 28 | Higgins & Thompson, *Stat Med* 21(11):1539-1558 | 2002 | I²异质性统计量，25000+引用 |
| 29 | Thompson & Higgins, *Stat Med* 21(11):1559-1573 | 2002 | Meta回归方法学指南 |
| 30 | Egger et al., *BMJ* 315(7109):629-634 | 1997 | Egger检验检测发表偏倚 |
| 31 | Higgins et al. (eds), *Cochrane Handbook v6.5* | 2024 | 系统综述与Meta分析方法学权威手册 |

### 诊断准确性评价文献（4篇）

| # | 来源 | 年份 | 贡献 |
|---|------|------|------|
| 32 | DeLong, DeLong & Clarke-Pearson, *Biometrics* 44(3):837-845 | 1988 | DeLong检验，比较配对ROC曲线AUC的标准方法 |
| 33 | Youden, *Cancer* 3(1):32-35 | 1950 | Youden指数，选择诊断试验最佳截断值 |
| 34 | Jaeschke et al., *JAMA* 271(9):703-707 | 1994 | 似然比EBM框架的里程碑文献 |
| 35 | Bossuyt et al. (STARD), *BMJ* 351:h5527 | 2015 | 诊断准确性研究的30项报告标准 |

### 等效性/非劣效性文献（2篇）

| # | 来源 | 年份 | 贡献 |
|---|------|------|------|
| 36 | Schuirmann, *J Pharmacokinet Biopharm* 15(6):657-680 | 1987 | TOST双单侧检验创始文献 |
| 37 | Piaggio et al. (CONSORT), *JAMA* 308(24):2594-2604 | 2012 | 非劣效/等效性试验的CONSORT扩展声明 |

### 缺失数据处理文献（4篇）

| # | 来源 | 年份 | 贡献 |
|---|------|------|------|
| 38 | Rubin, *Biometrika* 63(3):581-592 | 1976 | MCAR/MAR/MNAR缺失机制分类的奠基文献 |
| 39 | Little & Rubin, *Statistical Analysis with Missing Data*, 3rd ed. Wiley | 2019 | 缺失数据分析权威教材 |
| 40 | van Buuren, *Flexible Imputation of Missing Data*, 2nd ed. CRC Press | 2018 | MICE多重插补算法与R实现 |
| 41 | Enders, *Applied Missing Data Analysis*. Guilford Press | 2010 | FIML与多重插补应用实践教材 |

### 多重比较校正文献（4篇）

| # | 来源 | 年份 | 贡献 |
|---|------|------|------|
| 42 | Benjamini & Hochberg, *JRSS-B* 57(1):289-300 | 1995 | FDR/BH过程创始文献（109000+引用） |
| 43 | Holm, *Scand J Stat* 6:65-70 | 1979 | Holm-Bonferroni逐步法 |
| 44 | Hochberg, *Biometrika* 75(4):800-802 | 1988 | Hochberg逐步法 |
| 45 | Dunnett, *JASA* 50(272):1096-1121 | 1955 | Dunnett检验（多组vs对照组） |

### 补充经典方法学文献（3篇）

| # | 来源 | 年份 | 贡献 |
|---|------|------|------|
| 46 | McCullagh & Nelder, *Generalized Linear Models*, 2nd ed. Chapman & Hall | 1989 | GLM权威教材，泊松/负二项/有序Logistic的方法学基础 |
| 47 | McNemar, *Psychometrika* 12(2):153-157 | 1947 | McNemar检验原始文献，配对二分类数据统计检验创始论文 |
| 48 | Agresti, *Categorical Data Analysis*, 3rd ed. Wiley | 2013 | 分类数据分析权威教材，有序/多项Logistic、对数线性模型 |

### 贝叶斯方法文献（5篇）

| # | 来源 | 年份 | 贡献 |
|---|------|------|------|
| 49 | Kruschke, *Doing Bayesian Data Analysis*, 2nd ed. Academic Press | 2015 | BEST框架(Bayesian Estimation Supersedes the t-test)，贝叶斯实用教材 |
| 50 | Gelman, Carlin, Stern et al., *Bayesian Data Analysis*, 3rd ed. CRC Press | 2013 | 贝叶斯推断权威教材，层次模型、先验选择、模型检查 |
| 51 | Kass & Raftery, *JASA* 90(430):773-795 | 1995 | Bayes因子解释标准(BF10>3/10/30/100)，15000+引用 |
| 52 | Rouder, Speckman, Sun et al., *Psychon Bull Rev* 16:225-237 | 2009 | JZS先验贝叶斯t检验创始论文，BayesFactor R包方法学基础 |
| 53 | Wagenmakers, Love, Marsman et al., *Psychon Bull Rev* 25:58-76 | 2018 | JASP软件贝叶斯操作指南，涵盖t检验/ANOVA/回归/列联表/相关 |

> 以上53篇文献的详细摘要、方法学内容和效应量解释标准见 `references.md`。
