# Phase 2: 估计目标定义与方法确认（3 个子步骤，单一确认点）

> **来源说明**: 本文件从 SKILL.md L521-830 抽取，内容与原文语义等价。
> **上游**: Phase 1.5 交互式数据要素确认
> **下游**: Phase 3 制定 SAP
> **Checkpoint**: CP-4（🔴 STOP，硬阻断，Step 2.1+2.2+2.3 全部完成后触发）
>
> 依据：ICH E9(R1) Estimands and Sensitivity Analysis in Clinical Trials
> 参考：shared/statistics-methods/methods_catalog.md 伴发事件处理策略
>
> **设计原则**：Phase 2 包含 3 个顺序子步骤，全部完成后合并为单一 MANDATORY 确认点。
> 子步骤之间自动流转，不单独暂停；仅在全部完成后一次性展示给用户确认。

```
Step 2.1: Estimands 定义（五要素 + 伴发事件策略）
    → 自动流转
  Step 2.2: 方法选择（基于研究类型 + 数据特征 + 文献种子）
    → 自动流转
  Step 2.3: 参数确认（默认值预填，用户可覆盖）
      🔴 [MANDATORY] 单一确认点：展示完整 SAP 概要，等待用户确认
```

#### Step 2.1: Estimands 定义

在讨论统计方法之前，先精确定义估计目标。这是统计分析的核心框架

**估计目标五要素**:
| 要素 | 说明 | 示例 |
|------|------|------|
| **治疗条件** | 要比较的治疗 | 药物A vs 安慰剂 |
| **人群** | 目标患者群 | 所有随机化患者 |
| **变量(终点)** | 测量什么 | HbA1c从基线到24周的变化 |
| **伴发事件** | 影响结果解释的事件 | 停药、补救用药、死亡 |
| **人群层面汇总** | 如何汇总 | 两组均值差 |

**伴发事件处理策略**（必须选择并说明）
| 策略 | 说明 | 适用场景 |
|------|------|---------|
| **疗法策略** | 无论是否停药，都按原治疗组分析 | 意向性治疗(ITT) |
| **假想策略** | 假设未发生伴发事件会怎样 | 停药后的数据填补 |
| **复合变量** | 将伴发事件纳入终点定义 | 治疗失败=死亡+疾病进展 |
| **在治策略** | 仅分析治疗期间的数据 | 安全性分析 |
| **主层策略** | 按实际治疗分层分析 | 非依从性严重时 |

**输出**:
- 主要估计目标定义（含五要素）
- 伴发事件处理策略及临床依据
- 次要估计目标定义
- 探索性估计目标定义（如有）

**Estimands 定义异常处理**
| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| 用户无法提供伴发事件信息 | 基于研究设计推断常见伴发事件（如晚期肿瘤试验的死亡/停药为必然伴发事件） | 默认使用"疗法策略"（最保守），标注 "伴发事件策略基于默认假设" |
| 关联的伴发事件处理策略不可行（如数据不支持假想策略所需的填补假设） | 展示替代策略（疗法策略或复合变量）并说明切换理由 | 标记"策略受限"，在局限性中讨论 |
| 用户对Estimands 框架不熟悉 | 用研究问题直接推导五要素，用户确认后转换Estimands 术语 | 使用"Estimands 简化模式"：仅定义处理策略(疗法策略)和人群(ITT)，省略伴发事件/缺失数据策略，标注"Estimands 简化模式，缺少 ICH E9(R1) 完整五要素" |

#### Step 2.2: 方法选择

> **规范方法选择源**: `skills/stat-method-selector/decision-tree.json`（15-goal, 112-method 决策树，基于53篇方法学论文构建）
> **方法学文献依据**: `skills/stat-method-selector/references.md`（53篇文献结构化摘要 + 效应量解释标准）
> **本地速查**: `shared/statistics-methods/stat_test_decision_tree.md`（统计检验决策树，含 R 代码速查）
> **方法索引**: `shared/statistics-methods/INDEX.md`（48章统计指南章节索引）

基于 Step 2.1 Estimands、清洗后的数据特征和研究问题，选择统计方法。

**方法选择三步流程**:

**Step A: 研究目标维度定位**
从 `stat-method-selector` 决策树的15个根目标中，根据研究设计和Estimands确定所属分支：

| 根目标 (goal) | 适用场景 | MSRA 研究类型映射 |
|--------------|---------|-----------------|
| `compare` | 比较组间差异 | RCT / 观察性 |
| `correlation` | 变量间关联 | 任意 |
| `predict` | 预测结局 | 观察性 / 预测模型 |
| `causal` | 因果推断 | 观察性（PSM/MR/DID） |
| `survival` | 生存分析 | RCT / 观察性 |
| `dimension_reduction` | 降维 / 结构验证 | 任意（EFA/CFA/SEM） |
| `longitudinal` | 纵向/重复测量 | 任意 |
| `meta_analysis` | Meta分析 | 系统综述 |
| `diagnostic` | 诊断准确性 | 诊断试验 |
| `equivalence_non_inferiority` | 等效/非劣效 | RCT |
| `missing_data` | 缺失数据处理 | 任意 |
| `multiple_comparisons` | 多重比较校正 | 任意 |
| `descriptive` | 描述性统计 | 任意 |
| `reliability` | 一致性/信度 | 诊断试验 / 评估 |
| `bayesian` | 贝叶斯分析 | 任意 |

> 触发词映射详情见 `shared/statistics-methods/method_selector_mapping.md`

**Step B: 多维度决策路径**

确定根目标后，沿决策树逐层细化。核心维度（按层级）：

```
根目标 (goal)
  → 结局类型 (outcome_type): 连续 / 二分类 / 有序分类 / 计数 / 多因变量 / 时间-事件
    → 组数/比较 (num_groups): 1组 / 2组 / 3组+
      → 分布特性 (normality): 正态 / 非正态
        → 设计类型 (design): 独立 / 配对 / 重复测量
          → 方差齐性 (homogeneity): 齐 / 不齐（仅连续+正态时检查）
            → 推荐方法 + 文献依据
```

**需要向用户收集的信息**（EDA 已提供的自动跳过）：

| 维度 | 来源 | 需追问？ |
|------|------|---------|
| 结局类型 | Phase 1 EDA / Estimands | ❌ 已知 |
| 组数/比较 | Phase 1.5 研究要素确认 | ❌ 已知 |
| 正态性 | Phase 1 EDA（Shapiro-Wilk + Q-Q图） | ❌ 已知 |
| 设计类型 | Phase 1.5 数据要素确认 | ❌ 已知 |
| 方差齐性 | Phase 1 EDA（Levene/Brown-Forsythe） | ❌ 已知 |
| 球对称（重复测量） | Phase 1 EDA（Mauchly检验） | 仅重复测量设计 |
| 期望频数（分类数据） | Phase 1 EDA | 仅卡方检验 |
| 分布形状相同（非参） | Phase 1 EDA | 仅两组非参比较 |

> **关键**: Phase 1 EDA 已为方法选择提供了大部分决策依据。仅在信息不足时向用户追问缺失维度。

**Step C: 方法确认 + 文献依据**

从决策树到达叶子节点后，输出推荐卡片（格式见下方）。
每次推荐**必须引用 `references.md` 中的文献依据**，标注推荐的方法学来源。

**一次性输出格式**:
```
── 统计分析计划概要 ──
Estimands: [治疗条件] | [人群] | [终点] | [伴发事件策略] | [汇总方式]
主分析: [方法] | 调整变量: [列表]
次要分析: [方法列表]
敏感性: [方法列表]
参数: [关键参数及默认值]

确认以上计划? [继续 / 修改]
```

**1. 了解研究问题**
- 主要研究假设是什么？
- 主要结局指标是什么？
- 关键次要结局有哪些？
- 重要的亚组有哪些？

**2. 评估数据特征**
- 结局变量类型（连续/二分类/计数/生存/有序）
- 预测变量类型和数量

**2.5. 文献种子引用**（如 Phase 1 Step 1.5 已执行）
- 方法推荐时标注"基于文献种子 N 的方法选择"
- 样本量计算参考同类研究的效应量
- 如果用户提供的效应量与文献种子差异大，触发 ADAPTIVE checkpoint 提醒
> 参考：shared/sample-size/ — 样本量计算器 (Python/R)，支持 RCT/观察性/诊断试验多种设计
- 数据结构（独立/配对/重复测量/聚类）
- 样本量
- 缺失数据模式

**3. 方法推荐决策树（CANONICAL — 完整维度版本）**

> **规范源**: `skills/stat-method-selector/decision-tree.json`（15-goal, 112-method, 53篇文献支撑）
> **映射表**: `shared/statistics-methods/method_selector_mapping.md`（决策树方法→MSRA章节→R/Python实现）
> **文献依据**: `skills/stat-method-selector/references.md` 每次推荐必须引用

```
研究目标 (Step A 定位)
├── 比较差异 (compare)
│   ├── 连续结局
│   │   ├── 1组 → 单样本t检验(正态) / Wilcoxon符号秩(非正态)
│   │   ├── 2组
│   │   │   ├── 独立 → 独立t检验(正态+方差齐) / Welch t(正态+方差不齐) / Mann-Whitney U(非正态)
│   │   │   └── 配对 → 配对t检验(差值正态) / Wilcoxon符号秩(差值非正态)
│   │   ├── 3+组
│   │   │   ├── 独立 → One-way ANOVA+Tukey(正态+方差齐) / Welch ANOVA+Games-Howell(方差不齐) / Kruskal-Wallis+Dunn(非正态)
│   │   │   └── 重复测量 → RM-ANOVA(正态+球对称) / Friedman+Wilcoxon事后(非正态)
│   │   └── 多因变量 → Hotelling's T²(2组) / MANOVA(3+组)
│   ├── 二分类结局
│   │   ├── 2组独立 → Pearson卡方(期望≥5) / Fisher精确(小样本)
│   │   ├── 2组配对 → McNemar检验
│   │   └── 3+组 → R×C卡方 / Cochran-Armitage趋势(有序暴露)
│   └── 有序结局
│       ├── 2组独立 → Mann-Whitney U / 有序Logistic
│       └── 3+组 → Kruskal-Wallis+Dunn / 有序Logistic
│
├── 关联/相关 (correlation)
│   ├── 连续×连续 → Pearson(双正态+线性) / Spearman(非正态/非线性) / Kendall τ(小样本)
│   ├── 分类×分类 → 卡方独立性 + Cramér's V
│   └── 有序×有序 → Kendall τ-b / Spearman
│
├── 预测 (predict)
│   ├── 连续结局 → 多元线性回归 / Ridge(VIF≥10) / RCS(非线性)
│   ├── 二分类结局 → Logistic回归(EPV≥10) / Firth惩罚Logistic(EPV<10或分离) / RCS-Logistic(非线性logit)
│   ├── 有序结局 → 有序Logistic回归(比例优势假设通过) / 偏比例优势(假设违反)
│   ├── 计数结局 → 泊松回归(等离散) / 负二项(过离散) / 零膨胀(零过多)
│   └── 高维(n<p) → LASSO / Elastic Net / 随机森林
│
├── 因果推断 (causal) [观察性专用]
│   ├── PSM → 1:1匹配 / 0.2×SD卡尺 / SMD<0.1均衡诊断
│   ├── IPTW → 稳定化权重 / 95th截断 / 权重诊断
│   ├── 双重稳健 → AIPW + Bootstrap
│   ├── 中介分析 → 因果中介(反事实框架) / Baron-Kenny / Bootstrap CI
│   ├── 孟德尔随机化 → IVW + MR-Egger(水平多效性) + 加权中位数
│   ├── 双重差分DID → 平行趋势检验 + 事件研究图
│   └── E-value敏感性分析 → 未测量混杂影响量化
│
├── 生存分析 (survival)
│   ├── 描述 → Kaplan-Meier + 中位生存时间
│   ├── 比较曲线 → Log-rank检验
│   ├── 多因素 → Cox PH回归(PH假设通过) / 分层Cox(PH违反) / RMST(非比例风险)
│   └── 竞争风险 → Fine-Gray子分布HR / Cause-specific HR
│
├── 诊断试验 (diagnostic)
│   ├── 单试验 → ROC+AUC+Youden截断值 / Se/Sp/PPV/NPV/LR±
│   ├── 比较两试验 → DeLong检验比较AUC
│   └── 报告标准 → STARD 2015(30项)
│
├── 一致性/信度 (reliability)
│   ├── 连续测量 → ICC(3维度选择) + Bland-Altman
│   ├── 分类测量 → Cohen's Kappa(2评估者) / Fleiss' Kappa(多评估者) / 加权Kappa(有序)
│   └── Kappa悖论(患病率极端) → Gwet's AC1
│
├── 等效/非劣效 (equivalence_non_inferiority)
│   ├── 等效性 → TOST(双单侧检验)
│   └── 非劣效 → 单侧检验 + 预设Δ界值
│
├── Meta分析 (meta_analysis)
│   ├── 异质性低(I²<50%) → 固定效应Meta
│   ├── 异质性高(I²≥50%) → 随机效应Meta(DL) + 亚组/Meta回归
│   └── 发表偏倚 → Egger检验 + 漏斗图
│
├── 缺失数据 (missing_data)
│   ├── MCAR + 缺失<5% → 完整案例分析
│   ├── MAR通用 → 多重插补MICE
│   ├── MAR SEM/混合模型 → FIML
│   └── MNAR → 模式混合模型 / δ调整 / IPW选择模型
│
├── 多重比较 (multiple_comparisons)
│   ├── 全部两两(m≤10) → Bonferroni / Holm(FWER)
│   ├── 全部两两(11≤m≤50) → Hochberg逐步法
│   ├── k组vs1对照 → Dunnett检验
│   ├── 高维(m>50) → Benjamini-Hochberg FDR
│   └── 多层级终点 → 图形化方法(Bretz 2009)
│
├── 贝叶斯分析 (bayesian)
│   ├── t检验替代 → BEST框架(Kruschke 2015) / JZS先验(Rouder 2009)
│   ├── ANOVA替代 → 贝叶斯单/多因素ANOVA
│   ├── 回归替代 → 贝叶斯线性/Logistic回归
│   └── 模型比较 → Bayes因子(Kass&Raftery 1995: BF10>3/10/30/100)
│
└── 纵向分析 (longitudinal)
    ├── 人群平均效应 → GEE(边际模型)
    └── 个体特异效应 → LMM/GLMM(条件模型)
```

假设不满足转换流水线:
  Shapiro-Wilk(正态) + Brown-Forsythe(方差齐性)
  右偏: log10 | 通用: Box-Cox | 比例: Arcsine-Sqrt
  转换后重检，仍不满足: 非参数 | SAP中记录转换详情
事后检验(主检验显著时):
  ANOVA: Tukey/Dunnett/Sidak | K-W: Dunn's | 重复测量: Tukey+配对t
  多重比较校正须在SAP预定: Bonferroni/Holm/FDR/图形化方法(Bretz)

其他: 混杂→多变量/PS | 重复测量→混合GEE | 聚类→多水平 | 复杂设计→GLMM/GEE

**方法推荐输出格式**（每个推荐方法附带）:
```
## 推荐方法：{方法中文名}
**英文名：** {method_en}
**适用条件：** {description}
**前提假设：** {假设列表}
**假设检查：** {检验方法}
**假设不满足时：** {替代方法}
**效应量：** {效应量指标 + 解释标准}
**SPSS/R/Python 操作路径：** {操作指引}
**文献依据：** {references.md 中的引用}
```

**4. 观察性研究高级方法选择**

> **当研究类型为观察性研究时**，在基础方法选择后，必须额外讨论以下高级因果推断方法。
> 参考：shared/statistics-methods/chapters/ch35-propensity-scores.md 倾向性评分方法
> 参考：shared/statistics-methods/chapters/ch28-e-value.md E-value 敏感性分析（与阴性对照NCO 互补关系见章节MSRA 延伸）
> 参考：shared/causal-inference/causal_inference_workflow.md §3.3.5 阴性对照分析（NCO 证伪检查 + COCA 校正）

| 方法 | 适用场景 | 默认参数（无需确认） |
|------|---------|---------------------|
| **IPTW** | 混杂控制，需创建伪总体 | 95th截断 / logit PS / 稳定化权重 |
| **PSM** | 1:1 或 1:n 匹配 | 1:1匹配 / 0.2×SD卡尺 |
| **双重稳健** | 同时使用PS+结局模型 | 500次Bootstrap / Cox结局 |
| **RCS** | 连续变量非线性关系 | 3节点 / 百分位数(10/50/90) |
| **TTE** | 模拟目标试验（clone-censor-weight） | 1:1克隆 / IPCW / Cox结局 |
| **E-value** | 未测量混杂敏感性 | 观察性研究必需 |
| **阴性对照(NCO)** | 未测量混杂证伪检查 | 观察性研究强烈推荐（E-value 互补） |
| **亚组分析** | 处理效应异质性 | 3级模型(crude/age/full) |

> **参数使用默认值，无需逐项确认**。用户如需修改特定参数，在确认点提出即可。
> **🔴 [MANDATORY]** 仅在用户修改时才展开参数选项。否则直接使用默认值。

**效应量报告要求**（SAP中必须预定义）:

| 检验类型 | 效应量 | 计算方式 |
|---------|--------|---------|
| t检验 | Cohen's d | 独立: pooled SD; 配对: SD of differences |
| ANOVA | eta-squared / partial eta-squared | SS_effect / SS_total |
| Mann-Whitney | r | Z / sqrt(N) |
| Kruskal-Wallis | epsilon-squared | H / (N²-1) |
| Logistic回归 | OR | exp(β) |
| Cox回归 | HR | exp(β) |
| 原则 | **p值必须配合效应量+95%CI报告** | |

**5. 讨论框架**
对每个方法选择:
- 推荐方法及理由
- 所需假设
- 假设不满足时的替代方法

> **🔴 [MANDATORY]** Step 2.1 + 2.2 + 2.3 全部完成后，合并为**单一确认点**展示给用户。用户确认后进入 SAP 制定（Phase 3）。用户选项：[A] 确认进入 SAP 制定 / [B] 修改方法或参数 / [C] 暂停

**方法探讨失败处理**
| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| 数据特征与研究问题不匹配（如样本量不足以检验主要假设） | 要求用户选择：调整研究问题 / 增加样本量 / 标记为探索性分析 | 标记为探索性分析，降低结论强度 |
| 多种方法均适用且无明确优劣 | 展示各方法的优缺点，让用户选择 | 默认推荐最保守的方法（如非参数方法） |
| 用户坚持使用不推荐的方法 | 记录偏差，说明潜在风险 | 标注"用户决定"，在局限性中讨论 |

---

## Phase 2 Checkpoint

**Checkpoint CP-4**（🔴 STOP，硬阻断）:
- 触发位置: Step 2.1+2.2+2.3 全部完成
- 通过标准 (PASS): 用户**显式确认**方法+参数；Estimands 五要素完整填写
- 阻断标准 (BLOCK): 用户未确认 / Estimands 五要素缺失≥1
- 升级动作: 🛑 **硬阻断**：不制定 SAP，等待用户确认
- **Estimands 完整**: CP-4 必须定义全部 5 要素，缺失时用默认值并标注"[默认: 疗法策略]"
