# 统计方法选择器 — 参考文献资料

> 本文档整合了决策树所依据的核心方法学文献。每次为用户推荐统计方法时，必须参考本文档中的文献依据和方法学标准。

---

## 一、核心决策框架文献

### 1. Najmi A, Sadasivam B, Ray A. How to choose and interpret a statistical test? An update for budding researchers. *Journal of Family Medicine and Primary Care*. 2021;10(8):2763-2767. doi:10.4103/jfmpc.jfmpc_433_21. PMCID: PMC8483143.

**贡献定位：面向临床研究者的友好决策表，推荐方法与数据类型的直接对应关系**

**核心决策框架（5个维度筛选）：**

| 维度 | 选项 |
|------|------|
| 1. 数据类型分布 | 正态（用均值）vs 非正态/偏态（用中位数） |
| 2. 分析类型 | 比较（Comparison）、相关（Correlation）、回归（Regression） |
| 3. 组数 | 1组、2组、≥3组 |
| 4. 研究设计 | 配对/匹配 vs 非配对/独立 |
| 5. 变量类型 | 连续、有序（评分/等级）、二分类（比例） |

**方法映射表：**

*参数方法（正态分布数据）：*
- Student's t检验 → 比较2个均值
- 方差分析ANOVA → 比较≥3个均值
- Pearson相关 → 连续变量线性关系
- 线性回归 → 预测因变量

*非参数方法（偏态/非正态数据）：*
- Wilcoxon符号秩检验 → t检验的配对版
- Mann-Whitney U检验 → t检验的非配对版
- Kruskal-Wallis检验 → 单因素ANOVA对应
- Friedman检验 → 重复测量ANOVA对应
- Spearman秩相关 → Pearson对应
- 卡方检验 → 二分类/比例数据（无非参数-参数之分）

**关键解读指导：**
- P<0.05为常规阈值但非绝对，当P>0.05时需考虑研究功效（>80%）后再下"不显著"结论
- 统计显著性≠临床意义：统计学显著但临床意义微小（如降低血糖2mg%）不应过度解读
- 置信区间应与P值同时报告，尤其对于非显著性结果
- 95%CI包含零值对应5%水平的不显著性，窄CI表示更高精度

---

### 2. Mishra P, Pandey CM, Singh U, Keshri A, Sabaretnam M. Selection of appropriate statistical methods for data analysis. *Annals of Cardiac Anaesthesia*. 2019;22(3):297-301. doi:10.4103/aca.ACA_248_18.

**贡献定位：参数 vs 非参数方法分类决策表，含软件操作指引和样本量指导**

**三大选择因素：**
1. 研究目的和目标
2. 数据类型和分布（连续正态→参数→比较均值；连续非正态或其他→非参数→比较中位数/秩均值/比例）
3. 观测性质（配对 vs 非配对/独立）

**参数与非参数对应表（Table 1）：**

| 参数方法 | 非参数替代 |
|----------|-----------|
| 独立样本t检验 | Mann-Whitney U检验 |
| 配对t检验 | Wilcoxon符号秩检验 |
| 单因素ANOVA | Kruskal-Wallis H检验 |
| 重复测量ANOVA | Friedman检验 |
| Pearson相关 | Spearman秩相关 |
| 线性回归 | 对数线性回归 |

**比例比较方法（Table 2，均为非参数，无参数对应）：**

| 情境 | 检验方法 |
|------|---------|
| 两个/多个独立组 | Pearson卡方 / Fisher精确检验 |
| 两个配对组 | McNemar检验 |
| 三个及以上配对组 | Cochran's Q检验 |
| 独立/依赖比例 | Z检验比例 |

---

### 3. Mishra P, Singh U, Pandey CM, Mishra P, Pandey G. Application of Student's t-test, analysis of variance, and covariance. *Annals of Cardiac Anaesthesia*. 2019;22(4):407-411. doi:10.4103/aca.ACA_94_19.

**贡献定位：t检验、方差分析、协方差的详细"操作手册"**

**涵盖内容：**
- 单样本t检验：比较样本均值与已知总体均值
- 独立样本t检验：比较两组独立均值，需满足正态性、方差齐性(Levene检验)
- 配对t检验：同批受试者前后比较，差值需正态
- 单因素ANOVA：三组及以上均值比较，正态+方差齐
- 重复测量ANOVA：同批受试者多个时间点
- 两因素ANOVA：两个分类自变量的主效应和交互效应
- ANCOVA：控制连续协变量后比较组间差异

**包含完整的20名患者实例数据演示。**

---

### 4. Venkatesh U, Santhosh VN. Aligning Research Questions with Statistical Tests: A Clinician's Practical Framework. *NMO Journal*. 2025;19(2):182-188. doi:10.4103/JNMO.JNMO_61_25.

**贡献定位：涵盖描述-比较-关联-预测的四域框架，强调效应量报告和现代推断方法**

**四大分析域框架：**

**域一：全面数据表征**
- 变量类型识别（连续、分类、有序）
- 分布特性评估（Shapiro-Wilk检验、Kolmogorov-Smirnov检验、Q-Q图）
- 数据质量评估（缺失数据处理策略）

**域二：研究问题公式化**
- 描述性目标：总结数据特征
- 比较性目标：组间差异
- 相关性目标：变量关联
- 预测性目标：预测结局

**域三：比较分析方法**
- 两组比较：t检验、Mann-Whitney U、卡方、Fisher精确、McNemar
- 多组比较：ANOVA、Kruskal-Wallis、重复测量ANOVA、Friedman
- 强调效应量（Cohen's d）报告

**域四：高级回归建模**
- 线性回归、Logistic回归、生存分析
- 复杂数据结构处理方法
- 从传统假设检验向效应估计和透明性转变
- 整合现代机器学习方法同时保持临床可解释性

---

### 5. Sungur MA, Karabulut E. Conscious and Correct Use of Biostatistical Methods in Medical Researches: From Planning to Reporting the Results - Part II. *Düzce Medical Journal*. 2024;26(3):183-190. doi:10.18678/dtfd.1604460.

**贡献定位：单组/两组/三组+设计的详细决策流程图，含事后检验选择**

**决策流程图覆盖：**
- **单组设计：**
  - 连续+正态 → 单样本t检验
  - 连续+非正态 → Wilcoxon符号秩检验
  - 二分类 → 二项检验/卡方拟合优度

- **两组设计（独立）：**
  - 连续+正态+方差齐 → 独立样本t检验
  - 连续+正态+方差不齐 → Welch t检验
  - 连续+非正态 → Mann-Whitney U检验
  - 二分类+大样本 → Pearson卡方
  - 二分类+小样本 → Fisher精确检验
  - 有序 → Mann-Whitney U

- **两组设计（配对）：**
  - 连续+差值正态 → 配对t检验
  - 连续+差值非正态 → Wilcoxon符号秩检验
  - 二分类 → McNemar检验

- **三组及以上设计（独立）：**
  - 连续+正态+方差齐 → 单因素ANOVA + Tukey HSD
  - 连续+正态+方差不齐 → Welch ANOVA + Games-Howell
  - 连续+非正态 → Kruskal-Wallis + Dunn事后
  - 二分类 → R×C卡方或Fisher-Freeman-Halton

- **三组及以上设计（重复测量）：**
  - 连续+正态+球对称 → 重复测量ANOVA
  - 球对称违反 → Greenhouse-Geisser/Huynh-Feldt校正
  - 非正态 → Friedman + Wilcoxon事后(Bonferroni校正)

**核心原则：** 强调理解方法选择的逻辑/原理而非数学计算，统计原理适用于研究的所有阶段（计划→报告）。

---

## 二、特定领域文献

### 6. Stolyar A, et al. A framework for human evaluation of large language models in healthcare derived from literature review. *npj Digital Medicine*. 2024;7:258. doi:10.1038/s41746-024-01258-7.

**贡献定位：信度评估方法（ICC, Kappa）的可视化决策树（Fig.6）**

**Fig.6 决策树内容：**
- 基于评估类型和度量类型选择正确的统计检验
- **连续型测量一致性：** 组内相关系数 (ICC)
  - ICC模型选择：单因素随机、双因素随机、双因素混合
  - ICC类型选择：单一测量 vs 平均测量
  - ICC定义选择：一致性 vs 绝对一致
- **分类测量一致性：**
  - 二评估者 → Cohen's Kappa
  - 多评估者 → Fleiss' Kappa
  - 有序分类 → 加权Kappa
  - Kappa悖论场景 → Gwet's AC1
- **Bland-Altman分析：** 可视化系统偏倚和一致性界限

---

### 7. Koo TK, Li MY. A Guideline of Selecting and Reporting Intraclass Correlation Coefficients for Reliability Research. *Journal of Chiropractic Medicine*. 2016;15(2):155-163. doi:10.1016/j.jcm.2016.02.012. PMCID: PMC4913118.

**贡献定位：ICC选择与解释的权威指南（15000+引用）**

**ICC选择的三个维度（McGraw & Wong, 1996框架的10种形式）：**

1. **模型 (Model)：**
   - 单因素随机效应 (one-way random)：每个被试由不同随机评估者评定
   - 双因素随机效应 (two-way random)：评估者随机抽样，可推广到所有评估者
   - 双因素混合效应 (two-way mixed)：评估者固定（特定的评估者），仅适用于这些评估者

2. **类型 (Type)：**
   - 单一测量 (single rater/measurement)：基于单个评估者的可靠性
   - 平均测量 (mean of k raters/measurements)：基于k个评估者均值的可靠性

3. **定义 (Definition)：**
   - 绝对一致 (absolute agreement)：评估者给出完全相同的分数
   - 一致性 (consistency)：评估者分数相关性高但可系统偏移

**ICC解释基准（基于95%置信区间）：**
- ICC < 0.50 → 差 (poor)
- 0.50 ≤ ICC < 0.75 → 中等 (moderate)
- 0.75 ≤ ICC < 0.90 → 好 (good)
- ICC ≥ 0.90 → 优秀 (excellent)

**报告建议：** 始终报告软件、模型、类型、定义、ICC估计值及其95%置信区间。

---

### 8. Landis JR, Koch GG. The Measurement of Observer Agreement for Categorical Data. *Biometrics*. 1977;33(1):159-174. doi:10.2307/2529310.

**贡献定位：Kappa系数解释标准（64000+引用，里程碑级文献）**

**Kappa解释基准：**

| Kappa值范围 | 一致强度 |
|------------|---------|
| < 0.00 | 差 (Poor) |
| 0.00 – 0.20 | 轻微 (Slight) |
| 0.21 – 0.40 | 一般 (Fair) |
| 0.41 – 0.60 | 中等 (Moderate) |
| 0.61 – 0.80 | 高度 (Substantial) |
| 0.81 – 1.00 | 几乎完美 (Almost Perfect) |

**重要注意事项：**
- Kappa校正了随机一致的成分
- 患病率极低或极高时可能出现Kappa悖论（高一致但低Kappa）
- Kappa悖论场景下建议使用Gwet's AC1替代

---

### 9. Burgess S, Daniel RM, Butterworth AS, Thompson SG; EPIC-InterAct Consortium. Network Mendelian randomization: using genetic variants as instrumental variables to investigate mediation in causal pathways. *International Journal of Epidemiology*. 2015;44(2):484-495. doi:10.1093/ije/dyu176.

**贡献定位：孟德尔随机化方法学标准，特别是中介效应下的网络MR框架**

**标准MR三大核心工具变量假设：**
1. **IV1（相关性）：** 遗传变异与暴露强相关（F统计量>10）
2. **IV2（独立性）：** 遗传变异不与混杂因素相关
3. **IV3（排除限制）：** 遗传变异仅通过暴露途径影响结局

**网络MR扩展（中介路径下）：**
- 将总效应分解为直接效应和间接效应（通过中介变量）
- 两种分析方法：回归法和结构方程模型（SEM）
- 额外假设：暴露-中介效应同质性、中介-结局效应同质性、线性无交互
- 稳健性发现：即使存在相当大的异质性，偏差也不大

**核心方法：**
- 主分析：逆方差加权法 (IVW)
- 敏感性分析：MR-Egger回归（截距项检验水平多效性）、加权中位数法
- 异质性检验：Cochran's Q
- 弱工具变量处理：MR-RAPS、MR-PRESSO

---

---

## 三-A、Meta分析文献

### 27. DerSimonian R, Laird N. Meta-analysis in clinical trials. *Controlled Clinical Trials*. 1986;7(3):177-188. doi:10.1016/0197-2456(86)90046-2.

**贡献定位：随机效应Meta分析的创始文献（29000+引用）**

引入DerSimonian-Laird随机效应荟萃分析方法，将研究间异质性纳入治疗效应估计。权重同时考虑研究内方差和研究间方差(τ²)。当异质性较高时，随机效应模型给出比固定效应更保守（更宽置信区间）的合并效应估计。是最广泛使用的随机效应Meta分析方法。

### 28. Higgins JPT, Thompson SG. Quantifying heterogeneity in a meta-analysis. *Statistics in Medicine*. 2002;21(11):1539-1558. doi:10.1002/sim.1186.

**贡献定位：I²异质性统计量的原创文献（25000+引用）**

引入I²统计量描述总变异中归因于异质性而非抽样误差的比例。I²=0%无异质性，25%低，50%中，75%高。与传统Q检验不同，I²不依赖于研究数量。同时引入H²和R²等互补指标。

### 29. Thompson SG, Higgins JPT. How should meta-regression analyses be undertaken and interpreted? *Statistics in Medicine*. 2002;21(11):1559-1573. doi:10.1002/sim.1187.

**贡献定位：Meta回归方法学指南**

提出应用于临床试验的正确荟萃回归方法。强调应使用随机效应权重同时考虑研究内方差和残留异质性。警告Meta回归的关联是观察性而非因果性（生态学谬误风险），每协变量至少10项研究。

### 30. Egger M, Davey Smith G, Schneider M, Minder C. Bias in meta-analysis detected by a simple, graphical test. *BMJ*. 1997;315(7109):629-634. doi:10.1136/bmj.315.7109.629.

**贡献定位：Egger检验的原创文献——发表偏倚的标准检测方法**

引入Egger回归检验检测漏斗图不对称性。通过对效应量/标准误差与精密度（1/标准误差）进行线性回归，截距项偏离零表示可能存在发表偏倚。建议结合漏斗图视觉检查和Egger检验定量证据。

### 31. Higgins JPT, Thomas J, Chandler J, Cumpston M, Li T, Page MJ, Welch VA (editors). *Cochrane Handbook for Systematic Reviews of Interventions* version 6.5 (updated August 2024). Cochrane, 2024.

**贡献定位：系统综述和Meta分析的方法学权威手册**

涵盖系统综述全流程方法学标准：检索策略、偏倚风险评估(RoB 2)、异质性评估、Meta分析方法选择（固定/随机效应）、亚组分析和Meta回归、发表偏倚评估、GRADE证据质量评级。是所有医学Meta分析的标准参考文献。

---

## 三-B、诊断准确性评价文献

### 32. DeLong ER, DeLong DM, Clarke-Pearson DL. Comparing the areas under two or more correlated receiver operating characteristic curves: A nonparametric approach. *Biometrics*. 1988;44(3):837-845. doi:10.2307/2531595.

**贡献定位：DeLong检验的原创文献——比较配对ROC曲线的非参数标准方法**

利用广义U统计量理论估计两个（或多个）相关ROC曲线下面积(AUC)差的协方差矩阵，构造渐近卡方检验统计量。适用于同一批受试者接受两个诊断试验的配对设计。是医学诊断研究中比较AUC的最常用方法。

### 33. Youden WJ. Index for rating diagnostic tests. *Cancer*. 1950;3(1):32-35. doi:10.1002/1097-0142(1950)3:1<32::AID-CNCR2820030106>3.0.CO;2-3.

**贡献定位：Youden指数的原创文献——选择诊断试验最佳截断值的经典指标**

Youden指数 J = Se + Sp - 1 综合了敏感度和特异度，通过最大化J值确定最佳截断值。范围从0（完全无效）到1（完美）。不受患病率影响，在ROC曲线上对应离左上角最近的点。

### 34. Jaeschke R, Guyatt GH, Sackett DL, et al. Users' Guides to the Medical Literature. III. How to Use an Article about a Diagnostic Test. B: What Are the Results and Will They Help Me in Caring for My Patients? *JAMA*. 1994;271(9):703-707. doi:10.1001/jama.1994.03510330081039.

**贡献定位：似然比EBM框架的里程碑文献**

系统将似然比(LR)框架引入诊断试验解释。经典LR解释标准：LR+>10结论性、5-10中等、2-5弱；LR-<0.1结论性。介绍Fagan列线图将检验前概率转化为检验后概率。强调LR±不受患病率影响，优于PPV/NPV。

### 35. Bossuyt PM, Reitsma JB, Bruns DE, et al. (STARD Group). STARD 2015: An Updated List of Essential Items for Reporting Diagnostic Accuracy Studies. *BMJ*. 2015;351:h5527. doi:10.1136/bmj.h5527.

**贡献定位：诊断准确性研究的权威报告标准**

提供STARD 2015检查表——30个应在每份诊断准确性研究报告中包含的基本项目。涵盖标题/摘要、引言、方法（参与者、试验方法、金标准）、结果（流程图、诊断性能估计）、讨论。是诊断准确性研究的标准化报告框架。

---

## 三-C、等效性/非劣效性检验文献

### 36. Schuirmann DJ. A comparison of the two one-sided tests procedure and the power approach for assessing the equivalence of average bioavailability. *Journal of Pharmacokinetics and Biopharmaceutics*. 1987;15(6):657-680. doi:10.1007/BF01068419.

**贡献定位：TOST（双单侧检验）的创始文献——等效性检验方法学基础**

引入双单侧检验(TOST)程序用于生物等效性检验。证明TOST等价于使用真实平均差异的(1-2α)置信区间法。论证了TOST优于"功效方法"的数学性质。是FDA和EMA认可的等效性检验标准方法。

### 37. Piaggio G, Elbourne DR, Pocock SJ, Evans SJ, Altman DG; CONSORT Group. Reporting of Noninferiority and Equivalence Randomized Trials: Extension of the CONSORT 2010 Statement. *JAMA*. 2012;308(24):2594-2604. doi:10.1001/jama.2012.87802.

**贡献定位：CONSORT 2010的非劣效性/等效性扩展声明**

提供了修改后的CONSORT检查表，对25个项目中的12个进行了补充。关键要点：非劣效界值Δ必须在试验前确定并论证、需同时报告ITT和PP分析、非劣效界值设定应基于标准干预的历史效应证据。是报告非劣效性试验的权威指南。

---

## 三-D、缺失数据处理方法文献

### 38. Rubin DB. Inference and missing data (with discussion). *Biometrika*. 1976;63(3):581-592. doi:10.1093/biomet/63.3.581.

**贡献定位：缺失数据机制分类（MCAR/MAR/MNAR）的奠基性文献**

引入缺失数据机制的基础性分类法——MCAR（完全随机缺失）、MAR（随机缺失）和MNAR/NMAR（非随机缺失）。确立了可忽略性概念：当数据为MAR且缺失机制参数与数据模型参数不同时，基于似然的推断可忽略缺失机制。是全部缺失数据方法领域的理论基石。

### 39. Little RJA, Rubin DB. *Statistical Analysis with Missing Data*. 3rd ed. Hoboken, NJ: John Wiley & Sons; 2019. doi:10.1002/9781119482260.

**贡献定位：缺失数据分析的权威教材**

系统涵盖从MCAR/MAR/MNAR理论、EM算法、多重插补(MI)、全信息最大似然(FIML)到非可忽略缺失模型的所有方法。第三版增加了大量现代计算方法和R语言实现。是实施任何缺失数据方法时的必备参考。

### 40. van Buuren S. *Flexible Imputation of Missing Data*. 2nd ed. Boca Raton, FL: CRC Press; 2018. doi:10.1201/9780429492259.

**贡献定位：多重插补的实用权威教材——MICE算法的R实现**

详细介绍通过链式方程进行多重插补(MICE)的方法，包括作者开发的R包mice。第二版包含插补模型诊断、收敛评估、Rubin规则合并、灵敏度分析等完整工作流程。是应用多重插补的标准操作参考。

### 41. Enders CK. *Applied Missing Data Analysis*. New York, NY: Guilford Press; 2010. ISBN 978-1-60623-639-0.

**贡献定位：FIML和多重插补的应用实践教材**

系统介绍全信息最大似然(FIML)和多重插补(MI)在实际数据分析中的应用。涵盖SEM框架下的FIML实现、基于EM的缺失值处理、SPSS/Mplus/R中的实际操作。适用于结构方程模型和混合效应模型的缺失数据场景。

---

## 三-E、多重比较校正文献

### 42. Benjamini Y, Hochberg Y. Controlling the false discovery rate: a practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B (Methodological)*. 1995;57(1):289-300. doi:10.1111/j.2517-6161.1995.tb02031.x.

**贡献定位：错误发现率(FDR)和Benjamini-Hochberg过程的创始文献（109000+引用）**

引入FDR作为大规模多重假设检验中家族错误率(FWER)的替代方案。BH过程控制所有被拒绝假设中假阳性的期望比例≤q。相比Bonferroni等FWER方法，FDR在检验数量大时功效显著更高。已成为基因组学、神经影像、高通量筛选中多重比较校正的标准方法。

### 43. Holm S. A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics*. 1979;6:65-70.

**贡献定位：Holm-Bonferroni逐步法的原创文献**

引入Holm逐步下降法：将p值从小到大排序，第k个p值与α/(m-k+1)比较，拒绝直到第一个不显著为止。对FWER的强控制始终优于经典Bonferroni校正（更强大），且无需假设检验独立。应作为Bonferroni的默认替代方案。

### 44. Hochberg Y. A sharper Bonferroni procedure for multiple tests of significance. *Biometrika*. 1988;75(4):800-802. doi:10.1093/biomet/75.4.800.

**贡献定位：Hochberg逐步法的原创文献**

引入Hochberg逐步上升法：从大到小检查p值，使用与Holm相同的临界值但反向操作。在p值独立或正相关的条件下比Holm方法更强（功效更高）。适用于检验统计量独立或正相关的常见场景（如多组比较的事后检验）。

### 45. Dunnett CW. A multiple comparison procedure for comparing several treatments with a control. *Journal of the American Statistical Association*. 1955;50(272):1096-1121. doi:10.1080/01621459.1955.10501294.

**贡献定位：Dunnett检验的原创文献——多处理组与单一对照组的专用多重比较方法**

利用多变量t分布处理k个处理组与单一对照组的多重比较。由于只关心处理-对照比较（而非处理之间），Dunnett检验比Bonferroni或Tukey HSD在同等FWER控制下更强大（15-30%功效增益）。是剂量-反应研究和活性对照试验的标准方法。

---

## 三、补充方法学文献

### 10. Altman DG. *Practical Statistics for Medical Research*. London: Chapman & Hall/CRC; 1991.

经典医学统计教科书，涵盖从描述统计到高级建模的完整方法体系。

### 11. Bland JM. *An Introduction to Medical Statistics*. 3rd ed. Oxford: Oxford University Press; 2000.

医学统计学入门权威教材，适合临床研究者建立统计基础。

### 12. Rosenbaum PR, Rubin DB. The central role of the propensity score in observational studies for causal effects. *Biometrika*. 1983;70(1):41-55.

倾向性评分方法的开创性论文，建立了PSM的理论基础。

### 13. Austin PC. An introduction to propensity score methods for reducing the effects of confounding in observational studies. *Multivariate Behavioral Research*. 2011;46(3):399-424.

PSM实用方法指南，含标准化均值差(SMD<0.1为均衡)等评估标准。

### 14. VanderWeele TJ. Mediation analysis: a practitioner's guide. *Annual Review of Public Health*. 2016;37:17-32.

因果中介分析的实用指南，涵盖反事实框架和敏感性分析。

### 15. Hayes AF. *Introduction to Mediation, Moderation, and Conditional Process Analysis: A Regression-Based Approach*. 2nd ed. New York: Guilford Press; 2017.

PROCESS宏方法学基础，Baron-Kenny框架的现代发展。

### 16. Angrist JD, Pischke JS. *Mostly Harmless Econometrics: An Empiricist's Companion*. Princeton: Princeton University Press; 2009.

计量经济学因果推断方法权威教材，涵盖IV、DID、RDD等方法。

### 17. Fine JP, Gray RJ. A proportional hazards model for the subdistribution of a competing risk. *Journal of the American Statistical Association*. 1999;94(446):496-509.

竞争风险模型的原创论文，定义了子分布风险(SHR)框架。

### 18. Hu LT, Bentler PM. Cutoff criteria for fit indexes in covariance structure analysis: Conventional criteria versus new alternatives. *Structural Equation Modeling*. 1999;6(1):1-55.

SEM/CFA拟合指数标准（CFI>0.90可接受/>0.95好, RMSEA<0.08可接受/<0.05好, SRMR<0.08）。

### 19. Callaway B, Sant'Anna PHC. Difference-in-differences with multiple time periods. *Journal of Econometrics*. 2021;225(2):200-230.

多期DID的现代方法学标准，替代传统双向固定效应模型。

### 20. Hoerl AE, Kennard RW. Ridge regression: Biased estimation for nonorthogonal problems. *Technometrics*. 1970;12(1):55-67.

**贡献定位：Ridge回归的原创文献，处理多重共线性的经典方法**

通过在OLS目标函数中加入系数的L2范数惩罚项（λΣβ²），以略微增加偏差为代价显著降低估计方差。特别适用于预测变量高度相关（VIF≥10）时OLS估计不稳定的场景。岭迹图（ridge trace）可视化系数随λ变化的收缩路径。

### 21. Firth D. Bias reduction of maximum likelihood estimates. *Biometrika*. 1993;80(1):27-38.

**贡献定位：Firth惩罚似然的原创文献，解决Logistic回归中小样本偏倚和完全分离问题**

通过在似然函数中加入Jeffreys不变先验的惩罚项，将MLE的O(n⁻¹)阶偏倚降至O(n⁻²)。在EPV<10、完全分离或准完全分离场景下，Firth方法给出有限且合理的估计，而标准MLE可能发散或严重偏倚。

### 22. Brunner E, Munzel U. The nonparametric Behrens-Fisher problem: Asymptotic theory and a small-sample approximation. *Biometrical Journal*. 2000;42(1):17-25.

**贡献定位：Brunner-Munzel检验的原创文献，处理两组分布形状不同时的非参数比较**

当Mann-Whitney U检验的"两组分布形状相同"假设不满足时，Brunner-Munzel检验提供了一种不依赖该假设的非参数替代。检验统计量基于相对效应（relative effect）而非秩和，对分布形状差异稳健。

### 23. Harrell FE. *Regression Modeling Strategies: With Applications to Linear Models, Logistic and Ordinal Regression, and Survival Analysis*. 2nd ed. New York: Springer; 2015.

**贡献定位：限制性立方样条（RCS）在回归模型中应用的方法学权威教材**

系统介绍了RCS的理论基础、节点选择策略（默认3-5个节点）、非线性效应的检验和图形展示。涵盖线性回归、Logistic回归、有序回归和Cox回归中RCS的使用。提供了完整的R语言rms包使用指南。

### 24. Gelman A, Hill J. *Data Analysis Using Regression and Multilevel/Hierarchical Models*. Cambridge: Cambridge University Press; 2007.

**贡献定位：多水平模型/层次模型的权威教材**

系统介绍多层次数据的分析方法，从简单的随机截距模型到复杂的随机斜率模型和交叉分类模型。涵盖模型拟合（lme4）、假设检验、模型比较（AIC/BIC/Deviance）、预测和图形展示。提供完整的R语言实现。

### 25. VanderWeele TJ, Ding P. Sensitivity analysis in observational research: Introducing the E-value. *Annals of Internal Medicine*. 2017;167(4):268-274.

**贡献定位：E-value敏感性分析的方法学文献，量化未测量混杂的影响**

E-value定义为：需要多强的未测量混杂因素（与暴露和结局的最小关联强度，以风险比尺度）才能完全解释观察到的暴露-结局关联。E-value越大（通常>2为较稳健），结论对未测量混杂越不敏感。适用于风险比、比值比、风险差和连续结局。

### 26. Austin PC. Balance diagnostics for comparing the distribution of baseline covariates between treatment groups in propensity-score matched samples. *Statistics in Medicine*. 2009;28(25):3083-3107.

**贡献定位：倾向性评分匹配的均衡诊断标准（SMD<0.1）的方法学文献**

系统比较了假设检验（t检验、卡方）和标准化差异（SMD）在评估匹配后协变量均衡性方面的优劣。推荐使用SMD（以0.1为阈值）而非假设检验p值，因为p值受样本量影响而SMD不受。同时讨论了love plot、分位数-分位数图等可视化诊断工具。

---

## 四、方法选择速查表

### 根据研究目标快速定位：

| 研究目标 | 结局类型 | 组数/设计 | 数据特性 | 推荐方法 | 文献依据 |
|---------|---------|----------|---------|---------|---------|
| 比较差异 | 连续 | 1组 | 正态 | 单样本t检验 | Mishra(22-3)+Sungur |
| 比较差异 | 连续 | 1组 | 非正态 | Wilcoxon符号秩 | Mishra(22-3)+PMC8483143 |
| 比较差异 | 连续 | 2组独立 | 正态+方差齐 | 独立样本t检验 | Mishra(22-4)+Sungur |
| 比较差异 | 连续 | 2组独立 | 正态+方差不齐 | Welch t检验 | Mishra(22-4)+PMC8483143 |
| 比较差异 | 连续 | 2组独立 | 非正态 | Mann-Whitney U | Mishra(22-3)+PMC8483143 |
| 比较差异 | 连续 | 2组配对 | 差值正态 | 配对t检验 | Mishra(22-4)+Sungur |
| 比较差异 | 连续 | 2组配对 | 差值非正态 | Wilcoxon符号秩 | Mishra(22-3)+PMC8483143 |
| 比较差异 | 连续 | ≥3组独立 | 正态+方差齐 | One-way ANOVA+Tukey HSD | Mishra(22-4)+Sungur |
| 比较差异 | 连续 | ≥3组独立 | 正态+方差不齐 | Welch ANOVA+Games-Howell | Sungur+PMC8483143 |
| 比较差异 | 连续 | ≥3组独立 | 非正态 | Kruskal-Wallis+Dunn事后 | Mishra(22-3)+PMC8483143 |
| 比较差异 | 连续 | ≥3组重复 | 正态+球对称 | 重复测量ANOVA | Mishra(22-4)+Sungur |
| 比较差异 | 连续 | ≥3组重复 | 非正态 | Friedman+Wilcoxon事后 | Mishra(22-3)+PMC8483143 |
| 比较差异 | 二分类 | 2组独立 | 大样本(期望≥5) | Pearson卡方 | Mishra(22-3)+PMC8483143 |
| 比较差异 | 二分类 | 2组独立 | 小样本 | Fisher精确 | Mishra(22-3)+PMC8483143 |
| 比较差异 | 二分类 | 2组配对 | — | McNemar | Mishra(22-3) |
| 比较差异 | 二分类 | ≥3组 | 期望频数OK | R×C卡方 | Mishra(22-3)+PMC8483143 |
| 比较差异 | 有序 | 2组独立 | — | Mann-Whitney U/有序Logistic | PMC8483143 |
| 比较差异 | 有序 | ≥3组 | — | Kruskal-Wallis+Dunn | PMC8483143 |
| 关联/相关 | 连续-连续 | — | 双正态+线性 | Pearson相关 | Mishra(22-3)+PMC8483143 |
| 关联/相关 | 连续-连续 | — | 非正态/非线单调 | Spearman秩相关 | Mishra(22-3)+PMC8483143 |
| 关联/相关 | 分类-分类 | — | 名义 | 卡方独立性+Cramér's V | Mishra(22-3)+PMC8483143 |
| 关联/相关 | 有序-有序 | — | — | Kendall's tau-b/Spearman | PMC8483143 |
| 关联/相关 | 连续-二分类 | — | — | 点二列相关/双列相关 | PMC8483143 |
| 一致性 | 连续测量 | 2方法/评估者 | — | ICC + Bland-Altman | Koo&Li+Stolyar(2024)Fig.6 |
| 一致性 | 分类测量 | 2评估者 | — | Cohen's Kappa | Landis&Koch+Stolyar(2024)Fig.6 |
| 预测 | 连续结局 | 多自变量 | — | 多元线性回归 | Venkatesh&Santhosh+PMC8483143 |
| 预测 | 二分类结局 | 适中变量 | — | Logistic回归 | Venkatesh&Santhosh+PMC8483143 |
| 预测 | 二分类结局 | 高维(n<p) | — | LASSO/Ridge/Elastic Net | Venkatesh&Santhosh |
| 预测 | 有序多分类 | — | — | 有序Logistic回归 | Venkatesh&Santhosh |
| 预测 | 计数 | 等离散(方差≈均值) | — | 泊松回归 | Venkatesh&Santhosh |
| 预测 | 计数 | 过离散(方差>均值) | — | 负二项回归 | Venkatesh&Santhosh |
| 因果推断 | — | 遗传工具变量 | — | 孟德尔随机化(IVW+MR-Egger) | Burgess&Thompson 2015 |
| 因果推断 | — | 观察性+混杂 | — | PSM/IPTW | Rosenbaum&Rubin; Austin |
| 因果推断 | — | 中介路径 | — | 因果中介分析 | VanderWeele; Hayes |
| 因果推断 | — | 政策干预+前后 | — | 双重差分DID | Angrist&Pischke; Callaway&Sant'Anna |
| 生存分析 | 时间-事件 | 描述 | — | Kaplan-Meier | Mishra(22-3)+PMC8483143 |
| 生存分析 | 时间-事件 | 比较曲线 | — | Log-rank检验 | Mishra(22-3)+PMC8483143 |
| 生存分析 | 时间-事件 | 多因素 | 无竞争风险 | Cox比例风险回归 | Venkatesh&Santhosh+Mishra |
| 生存分析 | 时间-事件 | 多因素 | 有竞争风险 | Fine-Gray竞争风险模型 | Fine&Gray 1999 |
| 降维 | 连续变量 | 提取因子 | — | EFA/PCA | PMC8483143 |
| 降维 | 结构验证 | 预设模型 | — | CFA/SEM | Venkatesh&Santhosh+Hu&Bentler |
| 纵向 | 混合数据 | 人群平均 | — | GEE(边际模型) | Venkatesh&Santhosh; Gelman&Hill |
| 多结局 | 连续 | ≥2结局 | — | MANOVA | Mishra(22-3) |
| 描述 | — | — | — | 描述性统计(均值±SD/中位数IQR/频数%) | PMC8483143 |
| 比较差异 | 多因变量 | 2组 | — | Hotelling's T² | Mishra(22-3) |
| 比较差异 | 多因变量 | ≥3组 | — | MANOVA | Mishra(22-3) |
| 比较差异 | 连续 | ≥3组独立 | 正态+方差齐+2因素 | Two-way ANOVA+交互 | Mishra(22-4)+Sungur |
| 比较差异 | 连续 | ≥3组独立 | 正态+方差齐+协变量 | ANCOVA | Mishra(22-4) |
| 比较差异 | 连续 | ≥3组独立 | 正态+方差齐+嵌套 | Nested ANOVA/HLM | Venkatesh+Santhosh+Gelman&Hill |
| 预测 | 连续 | 多自变量 | 高共线性(VIF≥10) | Ridge回归/PCR | Hoerl&Kennard+Venkatesh |
| 预测 | 二分类 | 多自变量 | EPV<10 | Firth's惩罚Logistic | Firth 1993+Venkatesh |
| 预测 | 二分类 | 多自变量 | 非线性logit | RCS-Logistic回归 | Harrell 2015+Venkatesh |
| 因果推断 | — | 观察性+未测量混杂 | — | E-value敏感性分析 | VanderWeele&Ding 2017 |
| 比较差异 | 有序 | 1组 | — | 单样本Wilcoxon/卡方GOF | Sungur+PMC8483143 |
| 比较差异 | 有序 | ≥3组重复 | — | Friedman+Wilcoxon事后 | Mishra(22-3)+PMC8483143 |
| Meta分析 | 二分类 | 多研究 | 异质性低 | 固定效应Meta(M-H/IV) | DerSimonian&Laird; Cochrane Handbook |
| Meta分析 | 二分类 | 多研究 | 异质性高(I²≥50%) | 随机效应Meta(DL)+亚组/Egger | DerSimonian&Laird; Higgins&Thompson; Egger |
| Meta分析 | 连续 | 多研究 | 异质性低 | 固定效应Meta(MD/SMD) | DerSimonian&Laird; Cochrane Handbook |
| Meta分析 | 连续 | 多研究 | 异质性高(I²≥50%) | 随机效应Meta(DL)+Meta回归 | DerSimonian&Laird; Thompson&Higgins; Egger |
| 诊断准确性 | 连续标志物 | 1个试验 | — | ROC曲线+AUC+Youden截断值 | DeLong 1988; Youden 1950; Jaeschke 1994 |
| 诊断准确性 | 二分类试验 | 1个试验 | — | Se/Sp/PPV/NPV/LR± 四格表 | Jaeschke 1994; Bossuyt(STARD) 2015 |
| 诊断准确性 | 连续标志物 | 2个试验配对 | — | DeLong检验比较AUC | DeLong 1988 |
| 诊断准确性 | 任意 | 样本量估计 | — | 诊断试验样本量(Se/Sp驱动) | Bossuyt(STARD) 2015 |
| 等效性/非劣效 | 连续 | 2组 | — | TOST(等效)/单侧NI检验(非劣效) | Schuirmann 1987; Piaggio(CONSORT) 2012 |
| 等效性/非劣效 | 二分类 | 2组 | — | 率差/率比TOST或NI检验 | Schuirmann 1987; Piaggio(CONSORT) 2012 |
| 缺失数据 | 连续 | MCAR | 缺失<5% | 完整案例分析(listwise deletion) | Rubin 1976; Little&Rubin 2019 |
| 缺失数据 | 通用 | MAR | 通用场景 | 多重插补MICE(链式方程) | Rubin 1976; van Buuren 2018 |
| 缺失数据 | 通用 | MAR | SEM/混合模型 | 全信息最大似然FIML | Rubin 1976; Enders 2010 |
| 缺失数据 | 通用 | MNAR | 灵敏度分析 | 模式混合模型/δ调整 | Little&Rubin 2019 |
| 缺失数据 | 通用 | MNAR | 选择模型 | 逆概率加权(IPW) | Little&Rubin 2019 |
| 多重比较 | 通用 | 全部两两比较 | m≤10 | Bonferroni/Holm FWER | Holm 1979 |
| 多重比较 | 通用 | 全部两两比较 | 11≤m≤50 | Hochberg逐步法 | Hochberg 1988 |
| 多重比较 | 通用 | k组vs1对照 | 任何m | Dunnett检验 | Dunnett 1955 |
| 多重比较 | 通用 | 高维(m>50) | 探索性 | Benjamini-Hochberg FDR | Benjamini&Hochberg 1995 |
| 纵向 | 连续/分类 | 重复测量个人 | 人群平均效应 | GEE(边际模型) | Venkatesh&Santhosh; Gelman&Hill |
| 纵向 | 连续/分类 | 重复测量个人 | 个体特异效应 | LMM/GLMM(条件模型) | Venkatesh&Santhosh; Gelman&Hill |

---

## 五、效应量解释标准汇总

| 效应量 | 小 | 中 | 大 | 来源 |
|--------|---|----|----|------|
| Cohen's d | 0.2 | 0.5 | 0.8 | Cohen, 1988 |
| Pearson r / Spearman ρ | <0.3 | 0.3-0.5 | >0.5 | Cohen, 1988 |
| Cramér's V (df=1) | 0.1 | 0.3 | 0.5 | Cohen, 1988 |
| Kendall's tau | <0.2 | 0.2-0.4 | >0.4 | 惯例 |
| η² / 偏η² | 0.01 | 0.06 | 0.14 | Cohen, 1988 |
| ICC | <0.50差 | 0.50-0.75中 | ≥0.75好 | Koo & Li, 2016 |
| Kappa | <0.41差-一般 | 0.41-0.60中 | ≥0.61高度 | Landis & Koch, 1977 |
| CFI (SEM) | — | >0.90可接受 | >0.95好 | Hu & Bentler, 1999 |
| RMSEA (SEM) | — | <0.08可接受 | <0.05好 | Hu & Bentler, 1999 |
| SMD (PSM均衡) | — | <0.1为均衡 | — | Austin, 2011 |

---

## 六、补充经典方法学文献

### 46. McCullagh P, Nelder JA. *Generalized Linear Models*. 2nd ed. Chapman & Hall; 1989. ISBN: 978-0412317606.

**贡献定位：广义线性模型(GLM)权威教材，建立泊松回归、负二项回归等计数模型的方法学基础**

**核心GLM框架：**
- 统一指数族框架：正态→恒等链接; 二分类→Logit链接; 计数→Log链接
- 泊松回归的等离散假设：方差=均值，使用deviance/df检验（>1.5提示过离散）
- 过离散处理：quasi-Poisson（调整标准误）或负二项回归（完整的似然模型）
- 模型比较：残差deviance、AIC

**计数模型选择流程：**
1. 拟合泊松模型 → 检查deviance/df
2. deviance/df ≈ 1 → 泊松回归
3. deviance/df > 1.5 → 负二项回归
4. 零计数远多于模型预期 → 零膨胀模型（ZIP/ZINB）

---

### 47. McNemar Q. Note on the sampling error of the difference between correlated proportions or percentages. *Psychometrika*. 1947;12(2):153-157. doi:10.1007/BF02295996.

**贡献定位：McNemar检验原始文献，配对二分类数据的统计检验创始论文**

**方法学核心：**
- 用于配对设计中的二分类结局（干预前后、配对病例-对照）
- 检验统计量基于不一致对(b和c)：χ² = (b-c)²/(b+c)
- 小样本时使用二项检验：基于不一致对总数(b+c)，检验b是否偏离0.5
- 与独立样本卡方检验的本质区别：利用配对设计减少个体间变异

**使用条件：**
- 二分类结局（是/否，阳性/阴性）
- 配对设计（同一受试者两个时间点，或1:1匹配的病例-对照）
- 仅不一致对提供信息（一致对a和d不进入检验统计量）

---

### 48. Agresti A. *Categorical Data Analysis*. 3rd ed. John Wiley & Sons; 2013. ISBN: 978-0470463635.

**贡献定位：分类数据分析权威教材，涵盖有序Logistic回归、多项Logistic回归、对数线性模型等高级分类方法**

**有序分类方法贡献：**
- 比例优势模型（Proportional Odds Model）：有序Logistic的核心假设
- Brant检验：评估比例优势假设（p>0.05为假设成立）
- 偏比例优势模型：当Brant检验显著时允许部分变量违反比例优势
- 相邻类别Logit模型和连续比率Logit模型的替代选择

**多项Logistic贡献：**
- 基线类别Logit模型（Baseline-category Logit）：多项Logistic的标准形式
- IIA假设（无关选项独立性）的Hausman-McFadden检验
- 当IIA不成立时的替代：嵌套Logit模型或多项Probit模型

**分类数据分析一般原则：**
- 小样本/稀疏表格 → Fisher精确检验或Firth惩罚似然
- 有序数据不应降级为无序分析（损失统计功效）
- 效应量和置信区间与p值同等重要

---

## 七、贝叶斯方法文献

### 49. Kruschke JK. *Doing Bayesian Data Analysis: A Tutorial with R, JAGS, and Stan*. 2nd ed. Academic Press; 2015. ISBN: 978-0124058880.

**贡献定位：贝叶斯统计实用教材，提出BEST框架（Bayesian Estimation Supersedes the t-test）**

**BEST框架核心（第16章）：**
- 贝叶斯t检验替代经典t检验
- 使用t分布（而非正态）作为似然函数，允许离群值稳健性
- 默认弱信息先验：正态(0,1000²)对均值，均匀(0.001,1000)对标准差，指数(1/29)对自由度
- 输出：后验均值差值的95% HDI（最高密度区间）+ 效应量分布

**HDI解释 vs 置信区间：**
- 95% HDI = 给定数据下参数以95%概率落在该区间内
- 95% CI = 无限次重复抽样中95%的区间包含真值（频率派解释，单一区间不提供概率陈述）

**贝叶斯ANOVA与GLM：**
- 第18-19章：贝叶斯单因素/多因素/重复测量ANOVA
- 第21章：贝叶斯GLM框架统一ANOVA和回归

---

### 50. Gelman A, Carlin JB, Stern HS, Dunson DB, Vehtari A, Rubin DB. *Bayesian Data Analysis*. 3rd ed. CRC Press; 2013. ISBN: 978-1439840955.

**贡献定位：贝叶斯推断权威教材，涵盖层次模型、MCMC收敛诊断和模型检查**

**层次模型（多水平模型）核心（第5、15章）：**
- 收缩估计(shrinkage)：组均值向总体均值收缩，小样本组受益最大
- 随机效应分布：正态先验作为随机截距/斜率的默认先验
- 多层次贝叶斯模型的等价表述：lme4::lmer()频率派 ≈ brms::brm()贝叶斯版

**先验选择原则：**
- 弱信息先验(weakly informative prior)：提供正则化但不主导似然函数
  - 回归系数：正态(0, 2.5) 或 Cauchy(0, 2.5)（标准化后）
  - 方差分量：半Cauchy(0, 2.5) 或半Student-t(3, 0, 2.5)
- 信息先验：基于先前研究或领域知识的先验设定
- 先验预测检查(prior predictive check)：验证先验是否生成合理数据

**模型检查与比较：**
- 后验预测检查(posterior predictive check)：模拟新数据与观测数据对比
- WAIC/LOO-CV用于模型比较（优于DIC）
- Bayes因子在模型比较中的应用与局限

---

### 51. Kass RE, Raftery AE. Bayes Factors. *Journal of the American Statistical Association*. 1995;90(430):773-795. doi:10.1080/01621459.1995.10476572.

**贡献定位：Bayes因子解释标准的权威文献（15000+引用），建立BF阈值体系**

**Bayes因子定义：**
- BF10 = p(data|H1)/p(data|H0) = 给定数据下H1相对于H0的证据比
- BF01 = 1/BF10 = 支持H0的证据

**解释标准（Jeffreys 1961 校准版）：**

| BF10 | 解释 |
|------|------|
| 1-3 | 极弱/anecdotal证据 |
| 3-10 | 中等/positive证据 |
| 10-30 | 强/strong证据 |
| 30-100 | 很强/very strong证据 |
| >100 | 决定性/decisive证据 |

**频率派p值与Bayes因子关系：**
- p=0.05 对应 BF10≈3（最乐观情况下），即仅提供中等证据
- p=0.01 对应 BF10≈8-20，即强但不具决定性
- 这是p值被误解为"H0不成立的证据"的重要方法论纠正

**与频率派框架的关系：**
- Bayes因子不依赖p值，也不要求预先设定α水平
- 序贯设计：可在达到预设BF阈值后停止数据收集

---

### 52. Rouder JN, Speckman PL, Sun D, Morey RD, Iverson G. Bayesian t tests for accepting and rejecting the null hypothesis. *Psychonomic Bulletin & Review*. 2009;16(2):225-237. doi:10.3758/PBR.16.2.225.

**贡献定位：JZS先验（Jeffreys-Zellner-Siow）贝叶斯t检验创始论文，BayesFactor R包方法学基础**

**JZS先验框架：**
- 效应量delta的先验：Cauchy(0, r)，r为scale参数
  - r = 'medium' (√2/2 ≈ 0.707)：默认，适中
  - r = 'wide' (1)：对较大效应的预期
  - r = 'ultrawide' (√2 ≈ 1.414)：最保守，需要强证据
- Cauchy先验的优势：厚尾允许大效应可能性，峰值在0实现Occam's razor

**三种t检验的JZS公式：**
- 单样本 → `ttestBF(x, mu = mu0, rscale = 'medium')`
- 独立样本 → `ttestBF(formula = y ~ group, rscale = 'medium')`
- 配对 → `ttestBF(x = diff, rscale = 'medium')`

**与经典t检验的兼容性：**
- 大样本下后验均值近似样本均值差，但精确度由先验调节
- 小样本时贝叶斯检验更保守（不夸大效应）

---

### 53. Wagenmakers EJ, Love J, Marsman M, et al. Bayesian inference for psychology. Part II: Example applications with JASP. *Psychonomic Bulletin & Review*. 2018;25(1):58-76. doi:10.3758/s13423-017-1323-7.

**贡献定位：JASP软件中的贝叶斯操作指南，涵盖贝叶斯t检验、ANOVA、回归、列联表、相关分析的操作步骤**

**JASP操作对应表：**

| 分析类型 | JASP路径 |
|----------|---------|
| 贝叶斯t检验（单/独立/配对） | T-Tests → Bayesian |
| 贝叶斯ANOVA（单因素/多因素/重复测量） | ANOVA → Bayesian |
| 贝叶斯相关 | Regression → Bayesian → Correlation |
| 贝叶斯回归（线性/Logistic） | Regression → Bayesian → Linear/Logistic Regression |
| 贝叶斯列联表 | Frequencies → Bayesian → Contingency Tables |
| 贝叶斯Meta分析 | Meta-Analysis → Bayesian |

**JASP输出解释：**
- BF10（支持H1）和BF01（支持H0）同时报告
- 后验分布图 + 95% HDI
- 序贯分析图（如数据支持随时间变化的轨迹）
- 先验vs后验对比图

**与频率派方法的协同使用：**
- 同一数据可同时报告经典p值和Bayes因子
- 当p=0.04但BF10=2.5（仅轶事证据）时，贝叶斯框架提示结果可能不可靠
- 当p=0.06但BF10=12（强证据）时，贝叶斯框架可能支持效应存在

---

## 使用说明

当用户请求选择统计方法时，应按以下步骤使用本文档：

1. **解析用户场景** → 提取研究目标、结局类型、组数、设计类型、分布特性
2. **查找速查表** → 在第四部分速查表中匹配最接近的行
3. **确认文献依据** → 核对第一~三部分中相应文献的详细指导
4. **输出推荐** → 引用对应文献作为方法学依据

**重要原则：**
- 只推荐在决策树（decision-tree.json）中已定义的方法
- 每次推荐必须包含文献依据
- 如方法选择涉及效应量报告，参考第五部分的解释标准
- Kappa悖论场景（患病率极低/极高）应推荐Gwet's AC1而非Kappa
- ICC选择必须指定模型（单因素/双因素随机/双因素混合）× 类型（单一/平均）× 定义（绝对一致/一致性）
