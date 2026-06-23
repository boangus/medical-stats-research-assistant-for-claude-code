# 医学统计反模式目录

> MSRA 项目专用。列出医学统计分析中 LLM 最容易出错的思维模式，以及对应的防御策略。
> 各 SKILL 的"反例与黑名单"节引用本目录，本目录不与任何具体 SKILL 绑定。

---

## 设计初衷

LLM 在医学统计场景下存在三类系统性弱点：
1. **方法学过度自信**：倾向选择一个看似合理的方法，不验证假设条件
2. **长对话漂移**：在 10 阶段流水线的第 8 阶段，忘记第 2 阶段定下的 SAP 约束
3. **静默绕过**：当数据不完美时，倾向静默调整而非报告偏差

本目录按 **认知模式** 而非阶段分类，帮助各 SKILL 防御共性问题。

---

## 一、方法学反模式

### A1. 正态性假定默认化

> **现象**：拿到连续变量不检验分布，直接 t 检验 / ANOVA / 线性回归

| 方面 | 内容 |
|------|------|
| 典型表现 | "组间比较采用独立样本 t 检验"——未出现"正态性检验通过"的前提说明 |
| 为何危险 | 偏态数据用参数检验 → 假阳性率升高 / 检验效能下降 |
| 防御规则 | 必须在报告检验结果前声明"Shapiro-Wilk P=0.XX，数据满足正态性假定"或"不满足，采用 Mann-Whitney U 检验" |
| 涉及 SKILL | analysis-exec Phase 7, report Phase 5 |

### A2. 缺失数据静默处理

> **现象**：静默做 complete-case analysis 不报告

| 方面 | 内容 |
|------|------|
| 典型表现 | 代码里 `dropna()` 后直接跑分析，不评估缺失模式不报告删除了多少记录 |
| 为何危险 | CC 分析在 MAR/MNAR 下有偏，审稿人和读者不知道缺失程度 |
| 防御规则 | 报告缺失率 → 评估 MCAR/MAR/MNAR → 记录处理策略 → 敏感性分析比较不同方法 |
| 涉及 SKILL | data-prep Phase 4, analysis-plan Phase 1 |

### A3. 事后分析伪装成预设

> **现象**：看到分析结果后才调整方法选择，且不记录

| 方面 | 内容 |
|------|------|
| 典型表现 | 正态性检验 P=0.048（边缘显著），选择用参数检验因为"基本满足" |
| 为何危险 | 灵活性偏倚（researcher degrees of freedom），SAP 约束被打破 |
| 防御规则 | SAP 中预定义排除标准（如 Shapiro-Wilk P<0.10 则用非参数），严格按标准执行 |
| 涉及 SKILL | analysis-exec, analysis-plan, pipeline |

### A4. 效应量选择随意

> **现象**：多个效应量中"哪个显著报哪个"

| 方面 | 内容 |
|------|------|
| 典型表现 | 同一分析既有 Cohen's d 又有 η² 又有 OR，哪个 P<0.05 就重点报告哪个 |
| 为何危险 | 选择性报告 → 效应量膨胀 |
| 防御规则 | SAP 中必须预定义主要效应量类型，其他效应量仅作为补充信息 |
| 涉及 SKILL | analysis-plan Phase 3, report Phase 1 |

### A5. 过度解读亚组分析

> **现象**：不做交互检验就按亚组分拆做比较

| 方面 | 内容 |
|------|------|
| 典型表现 | 总人群 P=0.06，女性亚组 P=0.03 → "在女性中效果显著" |
| 为何危险 | 无交互检验的亚组分析是典型的数据窥探（data dredging） |
| 防御规则 | 亚组分析必须报告交互检验 P 值，无交互时不做拆分比较 |
| 涉及 SKILL | analysis-exec Phase 7, report Phase 1 |

### A6. 多重比较不校正

> **现象**：多个终点各自独立检验，不做 multiplicity adjustment

| 方面 | 内容 |
|------|------|
| 典型表现 | 次要终点 8 个，每个单独检验，报告"其中有 3 个显著" |
| 为何危险 | 总 I 类错误率膨胀到 1-(0.95)⁸≈33% |
| 防御规则 | RCT 强控制（Bonferroni/Holm/层次检验），观察性探索性分析用 FDR |
| 涉及 SKILL | analysis-plan Phase 3, analysis-exec Phase 7 |

---

## 二、长对话漂移反模式

### B1. SAP 约束遗忘

> **现象**：在 Stage 3 Phase 6 生成代码时，使用了 Stage 2 没有讨论过的方法

| 方面 | 内容 |
|------|------|
| 典型表现 | SAP 定了 ANCOVA，生成代码时跑了 mixed model "因为更灵活" |
| 为何危险 | 偏离预先注册的计划，结果不再可重复 |
| 防御规则 | 每段分析代码开头注释引用 SAP 对应章节；生成代码前重读 SAP 方法部分 |
| 涉及 SKILL | analysis-exec Phase 6, code_executor_agent |

### B2. 质量门闸标准自降

> **现象**：在门闸检查时对严重问题降低标准

| 方面 | 内容 |
|------|------|
| 典型表现 | "缺失率 35% 但分析方法对缺失不敏感，可以通过"——替代独立评估 |
| 为何危险 | 门闸失去阻断意义，质量保障体系崩塌 |
| 防御规则 | QC Inspector 严格执行阻断条件，不自行解释"可以通融" |
| 涉及 SKILL | qc_inspector_agent, pipeline Stage 1.5/2.5/3.5 |

### B3. 交互模式浮动

> **现象**：用户选了高效模式，但模型在中间阶段又回到详细引导

| 方面 | 内容 |
|------|------|
| 典型表现 | Phase 3 的 SLIM 确认变成了一整段 Dashboard 展示 |
| 为何危险 | 用户预期被打断，效率下降 |
| 防御规则 | pipeline 记住用户选择的模式，每次 Checkpoint 之前确认模式是否一致 |
| 涉及 SKILL | pipeline |

---

## 三、数据处理反模式

### C1. 异常值自动静默修正

> **现象**：发现异常值后不调查就直接 Winsorization 或删除

| 方面 | 内容 |
|------|------|
| 典型表现 | "检测到 3 个年龄=250 的异常值，自动修正为年龄中位数" |
| 为何危险 | 可能是真实极端值（如罕见病/超高龄），自动修正丢失重要信息 |
| 防御规则 | 必须先调查数据源 → 确认录入错误后才能修正 → 记录在清洗日志 |
| 涉及 SKILL | data-prep Phase 2 |

### C2. 变量构造切点随意

> **现象**：分组建档/切点时选择"看起来合理"的切点而非预定义

| 方面 | 内容 |
|------|------|
| 典型表现 | "年龄按中位数分为两组"——不在 SAP 里预定义 |
| 为何危险 | 切点选择自由度：不同切点产生不同结果 |
| 防御规则 | 切点必须在 SAP 中预定义（临床意义切点优先，分位数切点说明依据） |
| 涉及 SKILL | analysis-plan Phase 6, analysis-exec Phase 1 |

---

## 四、报告与解读反模式

### D1. P 值二元化

> **现象**：只写 P<0.05 或 P>0.05，不报告精确 P 值和效应量

| 方面 | 内容 |
|------|------|
| 典型表现 | "P<0.05，差异有统计学意义"但未给出 P=0.047 还是 P=0.003 |
| 为何危险 | 无法区分边缘显著和高度显著，不支持元分析 |
| 防御规则 | 报告精确 P 值（P=0.XX）和效应量+95%CI；用 `shared/reporting-guidelines/statcheck_patterns.py` 自动验证 P 值与统计量一致性 |
| 涉及 SKILL | report Phase 1, analysis-exec Phase 9 |

### D2. 统计显著 = 临床显著

> **现象**：P<0.05 就解读为"效果显著"，忽略效应量大小

| 方面 | 内容 |
|------|------|
| 典型表现 | "治疗组与对照组差异有统计学意义(P=0.03)"——差多少？有没有临床意义？ |
| 为何危险 | 大样本下微小差异也能显著，误导临床决策 |
| 防御规则 | 解读必须同时包含：效应量大小 + 置信区间 + 临床意义判断 |
| 涉及 SKILL | report Phase 1 |

### D3. 不报告假设检验结果

> **现象**：方法部分写了"用 t 检验"，但结果部分不报告正态性/方差齐性检验结果

| 方面 | 内容 |
|------|------|
| 典型表现 | "两组比较采用 t 检验" → 结果表格里没有 Shapiro-Wilk 和 Levene 结果 |
| 为何危险 | 读者无法判断方法选择是否正确 |
| 防御规则 | 报告模板中预留假设检验结果空间，SAP 中预定义需报告的假设检验 |
| 涉及 SKILL | report Phase 5, analysis-exec Phase 7 |

---

## 五、LLM 特有反模式

### E1. [SKIP] 应贴不贴

> **现象**：LLM 倾向于"硬做"而不是诚实标记无法执行的分析

| 方面 | 内容 |
|------|------|
| 典型表现 | 数据不足以做 Cox 回归（事件数 < 10/变量），但 LLM 仍生成代码并输出结果 |
| 为何危险 | 结果不可靠但报告未标记异常 |
| 防御规则 | 严格执行 [SKIP] 条件：样本量不足、假设严重违反且转换失败 → 标记 [SKIP] |

### E2. 代码"一次性"倾向

> **现象**：LLM 生成长而全的代码，难以调试和复现

| 方面 | 内容 |
|------|------|
| 典型表现 | 一个脚本完成数据加载、清洗、分析、绘图——出错时整段重来 |
| 为何危险 | 不可复现，无法定位错误 |
| 防御规则 | 分析代码必须按 Phase 分离：变量构造 / 描述性统计 / 推断分析 / 绘图 |

### E3. 自我审查放松

> **现象**：同一模型在写代码和检查代码时对错误不敏感

| 方面 | 内容 |
|------|------|
| 典型表现 | 自己写代码 → 自己检查 → "没问题" → 实际上变量构造公式有误 |
| 为何危险 | 缺乏独立验证，同类错误持续漏过 |
| 防御规则 | Generator-Evaluator 分离：exec-runner 写完 → 切回 Orchestrator → exec-inference 独立检查 |

---

## 六、机器学习反模式

### F1. 过拟合不检测

> **现象**：直接报告训练集准确率/AUC，未做交叉验证或外部验证

| 方面 | 内容 |
|------|------|
| 典型表现 | "Random Forest AUC=0.98"（训练集），未提及测试集或 CV 结果 |
| 为何危险 | 过拟合模型在新数据上性能崩塌，临床预测不可靠 |
| 防御规则 | 必须报告交叉验证 AUC + 测试集 AUC；两者差距 >0.05 时标记为过拟合风险 |

### F2. 黑箱无解释

> **现象**：使用复杂 ML 模型但不提供任何可解释性分析

| 方面 | 内容 |
|------|------|
| 典型表现 | "XGBoost AUC=0.85"，未说明哪些特征驱动预测 |
| 为何危险 | 临床决策需要理解模型逻辑，黑箱模型无法获得临床信任 |
| 防御规则 | 必须至少提供特征重要性（MDI/Permutation）+ SHAP 分析 |

### F3. 忽略校准

> **现象**：报告区分度（AUC）但不报告校准度（Brier Score / 校准曲线）

| 方面 | 内容 |
|------|------|
| 典型表现 | "模型 AUC=0.85"，未提及 Brier Score 或校准曲线 |
| 为何危险 | AUC=0.85 但校准差的模型会高/低估实际风险，临床决策失误 |
| 防御规则 | 必须报告 Brier Score + 校准曲线；校准斜率应接近 1 |

### F4. OW/IPTW 权重不检查

> **现象**：使用加权方法但不检查权重分布和极端权重

| 方面 | 内容 |
|------|------|
| 典型表现 | "采用 IPTW 加权"，未报告权重分布、截断策略、有效样本量 |
| 为何危险 | 极端权重导致方差膨胀，点估计不稳定 |
| 防御规则 | 必须报告权重分布（min/median/max）；IPTW 需截断极端值；OW 自动截断 |

---

## G. 网络Meta分析 (新增)

### G1. 忽略一致性检验

> **现象**：报告 NMA 合并结果但不检验全局/局部一致性

| 方面 | 内容 |
|------|------|
| 典型表现 | "SUCRA 排名 A>B>C"，未报告设计×治疗交互检验 p 值 |
| 为何危险 | 直接和间接证据矛盾时，合并结果无意义 |
| 防御规则 | 必须报告全局一致性检验（p 值）；显著时分别报告直接和间接结果 |

### G2. 排名当结论

> **现象**：将 SUCRA 排名等同于"最优治疗"推荐

| 方面 | 内容 |
|------|------|
| 典型表现 | "A 药排名第一，推荐临床使用" |
| 为何危险 | 排名基于点估计，不考虑置信区间宽度和证据质量；小样本干预可能排名虚高 |
| 防御规则 | 排名必须结合效应量+CI+证据质量(GRADE)；排名差距 <5% 时不应区分优劣 |

### G3. 不讨论传递性

> **现象**：假设网络中所有干预可直接比较，不讨论跨研究可比性

| 方面 | 内容 |
|------|------|
| 典型表现 | 将 5 种不同剂量、不同人群的 RCT 合并为一个网络 |
| 为何危险 | 传递性是 NMA 的核心假设；违反时间接比较无效 |
| 防御规则 | 必须讨论干预剂量、人群、对照类型的一致性；不一致时限制网络范围 |

---

## H. 孟德尔随机化 (新增)

### H1. 工具变量三假设不验证

> **现象**：使用 GWAS 显著位点作为工具变量，但不验证三个核心假设

| 方面 | 内容 |
|------|------|
| 典型表现 | "选取 p<5e-8 的 SNP 作为工具变量"，未验证关联性/独立性/排他性 |
| 为何危险 | 弱工具变量偏倚、多效性偏倚会导致因果推断无效 |
| 防御规则 | 必须报告 F 统计量（>10 为强工具）；必须做 MR-Egger 截距检验（多效性）；必须做 Cochran's Q 检验（异质性） |

### H2. 只报告 IVW 不做敏感性分析

> **现象**：仅报告 IVW 结果，不做 MR-Egger、加权中位数等敏感性分析

| 方面 | 内容 |
|------|------|
| 典型表现 | "IVW p=0.02，因果关系成立" |
| 为何危险 | IVW 在存在水平多效性时有偏；单一方法结论不可靠 |
| 防御规则 | 必须至少报告 IVW + MR-Egger + 加权中位数三种方法；结论一致时才可信 |

---

## I. 目标试验模拟 (新增)

### I1. 不定义目标试验协议

> **现象**：声称做 TTE 但不明确目标试验的五个要素

| 方面 | 内容 |
|------|------|
| 典型表现 | "采用克隆-删失-加权方法"，未定义目标试验的纳入标准、治疗策略、结局、随访、因果对比 |
| 为何危险 | 没有明确协议的 TTE 等于没有预注册的 RCT——事后修改无法辨别 |
| 防御规则 | 必须在分析前定义目标试验协议（五要素）；协议变更需记录 |

### I2. 克隆后不检查可比性

> **现象**：执行克隆操作但不验证克隆后两组的基线可比性

| 方面 | 内容 |
|------|------|
| 典型表现 | 克隆-删失后直接拟合 Cox 模型，未检查加权后协变量平衡 |
| 为何危险 | 克隆-删失可能引入选择偏倚；IPCW 未正确调整时效应估计有偏 |
| 防御规则 | 克隆后必须检查加权后协变量平衡（SMD<0.1）；IPCW 截断极端权重 |

---

## J. 广义估计方程 (新增)

### J1. 不报告工作相关矩阵选择理由

> **现象**：使用 GEE 但不说明为何选择特定工作相关矩阵

| 方面 | 内容 |
|------|------|
| 典型表现 | "采用 GEE 分析"，未说明使用 exchangeable/AR1/unstructured |
| 为何危险 | 不同相关矩阵影响标准误；不报告选择理由无法评估稳健性 |
| 防御规则 | 必须报告选择的工作相关矩阵 + 理由；必须用 QIC 比较不同结构；结论不一致时报告多种结果 |

### J2. 混淆边际效应与条件效应

> **现象**：将 GEE 的边际 OR 与 GLMM 的条件 OR 混淆解读

| 方面 | 内容 |
|------|------|
| 典型表现 | "GEE 显示 OR=1.5" 但未说明这是边际效应还是条件效应 |
| 为何危险 | 边际 OR 通常小于条件 OR（Neyman-Pearson 矛盾），当结局常见时差异可达 50% |
| 防御规则 | 必须明确报告"GEE 估计的是边际效应(总体平均)"；当结局率 >20% 时必须讨论边际与条件效应差异 |

---

---

## K. RWE 生成失败模式（借鉴 RWE-bench 评估）

> 基于 RWE-bench（真实世界证据生成基准）对 LLM Agent 的评估发现：
> 最佳 Agent 成功率仅 39.9%，主要失败模式如下。本节将这些失败模式纳入反模式目录，
> 帮助 MSRA 在执行观察性研究分析时主动规避。

### K1. 队列定义不完整

> **现象**：生成 RWE 时未完整定义纳入/排除标准，导致队列无效

| 方面 | 内容 |
|------|------|
| 典型表现 | 仅定义年龄范围，未定义用药时长、洗脱期、首次用药日期等关键纳入条件 |
| 为何危险 | 队列定义不完整 → 偏倚引入 → 真实世界效应估计无效 |
| RWE-bench 数据 | 队列定义不完整占失败案例的 32% |
| 防御规则 | 队列定义必须包含：纳入标准 + 排除标准 + 索引日期定义 + 洗脱期 + 随访起点/终点 |
| 涉及 SKILL | analysis-plan Phase 3, data-prep Phase 1 |

### K2. 任务未完成即输出

> **现象**：LLM 在分析任务未完全执行时就输出"结果"

| 方面 | 内容 |
|------|------|
| 典型表现 | SAP 计划了 5 项分析，仅完成 3 项就生成报告，未提及缺失的 2 项 |
| 为何危险 | 不完整分析导致结论偏颇，读者不知道哪些分析被遗漏 |
| RWE-bench 数据 | 任务不完整占失败案例的 28% |
| 防御规则 | 分析执行完成后必须逐项核对 SAP 分析规范表；每项标记 ✅完成 / [SKIP:原因] / ❌未执行 |
| 涉及 SKILL | analysis-exec Phase 6, report Phase 1 |

### K3. 混杂因素遗漏

> **现象**：观察性研究未识别和调整关键混杂因素

| 方面 | 内容 |
|------|------|
| 典型表现 | 仅调整年龄和性别，遗漏了疾病严重程度、合并症等重要混杂 |
| 为何危险 | 残留混杂使效应估计有偏，可能颠倒效应方向 |
| RWE-bench 数据 | 混杂遗漏占失败案例的 22% |
| 防御规则 | 观察性研究必须：1) 构建 DAG 识别混杂路径 2) 列出所有潜在混杂 3) 逐项说明调整/不调整理由 |
| 涉及 SKILL | analysis-plan Phase 3, analysis-exec Phase 3 |

### K4. 效应量方向错误

> **现象**：LLM 生成的效应量方向与数据实际关系相反

| 方面 | 内容 |
|------|------|
| 典型表现 | 数据显示治疗组优于对照组，但 LLM 报告 HR < 1 表示风险增加 |
| 为何危险 | 方向性错误是最严重的统计错误，直接导致临床决策反转 |
| RWE-bench 数据 | 方向错误占失败案例的 12% |
| 防御规则 | 效应量必须标注方向含义（如 "HR=0.75 表示治疗组风险降低25%"）；Generator-Evaluator 独立验证方向 |
| 涉及 SKILL | analysis-exec Phase 7-9, report Phase 1 |

### K5. 代码与描述不一致

> **现象**：生成的分析代码与文字描述的方法不匹配

| 方面 | 内容 |
|------|------|
| 典型表现 | SAP 写"采用 Cox 比例风险模型"，代码实际跑的是 Logistic 回归 |
| 为何危险 | 代码是实际执行的逻辑，描述是读者理解的内容，不一致 = 不可复现 |
| RWE-bench 数据 | 代码-描述不一致占失败案例的 18% |
| 防御规则 | 每段代码开头注释引用 SAP 章节号；QC Inspector 交叉验证代码方法与 SAP 一致性 |
| 涉及 SKILL | analysis-exec Phase 6, qc_inspector_agent |

---

## 十二、认知偏倚反模式

### L1. 辛普森悖论未识别

> **现象**：分层分析结论与总体分析结论方向相反，未识别时导致错误因果推断

| 方面 | 内容 |
|------|------|
| 典型表现 | 总体 OR=1.2（有利），但按中心/年龄分层后 OR<1（不利）——报告中只展示总体结果 |
| 为何危险 | 混杂因素方向翻转导致完全相反的临床决策 |
| 防御规则 | 观察性研究的亚组分析必须同时报告总体和分层结果；方向不一致时必须讨论混杂结构 |
| 涉及 SKILL | analysis-exec Phase 7, report Phase 5 |

### L2. 永恒时间偏倚

> **现象**：观察性研究中将随访开始到治疗开始之间的时间错误地归入"未暴露"组

| 方面 | 内容 |
|------|------|
| 典型表现 | "从入组开始计算生存时间"——但治疗组患者在入组后数周才开始治疗，此期间被错误归入对照组 |
| 为何危险 | 系统性高估对照组事件率，夸大治疗效果 |
| 防御规则 | 采用 landmark 设计或时依协变量 Cox 模型；必须在方法部分说明暴露时间定义 |
| 涉及 SKILL | analysis-plan Phase 3, analysis-exec Phase 7 |

### L3. 对撞偏倚

> **现象**：条件于中间变量（碰撞节点）时引入虚假关联

| 方面 | 内容 |
|------|------|
| 典型表现 | "仅分析住院患者"——住院是疾病严重程度和合并症的碰撞节点，限制分析引入虚假关联 |
| 为何危险 | 创造不存在的因果关联或遮盖真实的因果关系 |
| 防御规则 | DAG 构建时必须标注碰撞节点；限制分析必须有明确的因果图支持 |
| 涉及 SKILL | analysis-plan Phase 3, analysis-exec Phase 7 |

### L4. 文件抽屉效应

> **现象**：仅执行并报告显著的分析，不显著的分析不写入报告

| 方面 | 内容 |
|------|------|
| 典型表现 | SAP 预设 5 个敏感性分析，报告只展示 3 个显著的，2 个"未展示" |
| 为何危险 | 选择性报告导致假阳性膨胀，破坏研究可信度 |
| 防御规则 | SAP 预设的所有分析必须全部执行并报告；[SKIP] 必须有明确技术原因且记录在偏差表中 |
| 涉及 SKILL | analysis-exec Phase 9, report Phase 5, qc_inspector_agent |

---

## M. 统计约束反模式（新增）

> 基于 shared/statistics-methods/statistical_constraints.md 中定义的约束规则。
> 覆盖 P 值格式化、方法一致性、数据集一致性、统计原则违反四大维度。

### M1. P 值格式化违规

> **现象**：P 值展示不规范，违反 P-R01~R07 约束规则

| 方面 | 内容 |
|------|------|
| 典型表现 | 报告 "P = 0.000" 而非 "P < 0.001"；仅写 "P < 0.05" 不给精确值；用星号替代精确 P 值 |
| 为何危险 | "P = 0.000" 暗示 P 值为零，误导读者；二元化表述无法区分边缘显著和高度显著；星号标注不符合期刊要求 |
| 防御规则 | 严格执行 P-R01~R07：P<0.001 统一展示为 "P < 0.001"；0.001≤P<1.0 报告精确到 3 位小数；禁止二元化表述；禁止仅用星号 |
| 涉及 SKILL | analysis-exec Phase 6/9, report Phase 1/3/4 |

### M2. 加权数据混用

> **现象**：加权分析链中混用非加权数据，违反 M-R01~R05 约束规则

| 方面 | 内容 |
|------|------|
| 典型表现 | 主分析使用 IPTW 加权 Cox 回归，但 Table 1 使用非加权描述性统计；敏感性分析突然切换为非加权模型 |
| 为何危险 | 加权与非加权结果不可直接比较；混用导致效应估计不一致，读者无法判断哪个结果可信 |
| 防御规则 | 严格执行 M-R01~R05：加权分析链中所有相关分析必须使用同一加权数据集；切换必须标注并说明理由；填写方法一致性追踪表 |
| 涉及 SKILL | analysis-exec Phase 6/6.1/8, report Phase 5 |

### M3. 数据集混淆不提醒

> **现象**：不同分析使用不同数据集而不提醒用户，违反 D-R01~R05 约束规则

| 方面 | 内容 |
|------|------|
| 典型表现 | 主分析用 ITT 人群，敏感性分析突然用完整病例数据集，未提醒用户也未在报告中标注 |
| 为何危险 | 不同数据集的结果不可直接比较；读者可能误以为所有分析基于同一人群 |
| 防御规则 | 严格执行 D-R01~R05：每项分析标注数据集；不同数据集需提醒用户抉择（D-R02）；填写数据集一致性追踪表 |
| 涉及 SKILL | analysis-exec Phase 6/8, report Phase 5 |

### M4. 统计原则违反静默绕过

> **现象**：检测到统计原则违反时不提醒用户，自行调整方法，违反 S-R01~R08 约束规则

| 方面 | 内容 |
|------|------|
| 典型表现 | Shapiro-Wilk P=0.003（正态性违反），LLM 自行切换为非参数方法而不提醒用户抉择 |
| 为何危险 | 静默绕过剥夺了用户的决策权；事后方法切换如不记录，破坏 SAP 预注册性 |
| 防御规则 | 严格执行 S-R01~R08：检测到统计原则违反时必须暂停（🛑 STOP），展示用户抉择模板，由用户决定处理方案 |
| 涉及 SKILL | analysis-exec Phase 7/7.5 |

### M5. 图表非发表级质量

> **现象**：结果阶段输出给用户的图表未达到发表级标准

| 方面 | 内容 |
|------|------|
| 典型表现 | 图表使用默认 matplotlib 样式；无 Arial 字体；SVG 文本不可编辑；坐标轴无单位；P 值格式不规范；变量名不统一 |
| 为何危险 | 非发表级图表无法直接用于投稿；变量名不统一导致读者无法对应各处结果 |
| 防御规则 | 严格执行 shared/chart-styles/publication_figure_standards.md：三行强制 rcParams；语义化调色板；仅左+下轴线；SVG 首要导出；变量名遵循 variable_naming_conventions.md |
| 涉及 SKILL | analysis-exec Phase 9, report Phase 4 |

### M6. 变量命名不一致

> **现象**：同一变量在不同位置（SAP/代码/表格/图表/正文）使用不同名称

| 方面 | 内容 |
|------|------|
| 典型表现 | SAP 中写"收缩压"，代码中用 `sbp`，表格中写"Systolic BP"，图表中写"SBP"，正文写"血压" |
| 为何危险 | 读者无法对应各处结果；审稿人可能质疑数据一致性 |
| 防御规则 | 严格执行 shared/chart-styles/variable_naming_conventions.md：三列命名体系（代码变量名/规范显示名/英文显示名）；全流程一致性检查（V-R01~R07） |
| 涉及 SKILL | data-prep, analysis-plan, analysis-exec, report |

---

## 各 SKILL IRON RULE 速查

```yaml
pipeline:
  - "你是编排器，不是工作者。不执行任何实质性统计分析。"
  - "MANDATORY Checkpoint 不能以任何理由自动跳过。"
  - "回退超过 2 次后，不得自动再次退回。必须走 MANDATORY Checkpoint。"
  - "记住用户选择的交互模式，不一致时先确认再继续。"

data-prep:
  - "你永远不自动清洗数据——总是先验证、再讨论、获得批准后才执行。"
  - "静默删除任何数据是绝对禁止的——删除操作必须用户明确确认。"
  - "值规范化日志必须完整记录原值→规范值映射，供门闸消费。"
  - "盲法试验数据审核必须在盲态下进行。"

analysis-plan:
  - "不能将 RCT 的分析方法套用在观察性研究上，反之亦然。研究类型决定方法论体系。"
  - "SAP 中必须预定义主要效应量、切点、假设检验方法。"
  - "EDA 为方法选择服务，不能用于修改 SAP 中已定的分析框架。"

analysis-exec:
  - "严格按 SAP 执行。任何偏离都必须记录为偏差并征得用户同意。"
  - "生产分析和结果解读必须分两步：先生成代码和输出，再独立解读。"
  - "假设检验必须先于推断分析执行。不满足假设时必须降级到预定义的替代方法。"
  - "P值<0.001统一展示为 P < 0.001，禁止 P = 0.000（P-R01）。"
  - "加权分析链中不得混用非加权数据，切换必须标注（M-R01~R05）。"
  - "不同分析使用不同数据集时必须提醒用户抉择（D-R02）。"
  - "统计原则违反时必须暂停并让用户抉择处理方案（S-R01~R08）。"
  - "结果图表必须达到发表级标准（publication_figure_standards.md）。"

report:
  - "报告精确 P 值和效应量+95%CI，不写 P<0.05 / P>0.05 的二元结果。"
  - "[SKIP] 标记必须在最终报告中高亮标注，不得静默跳过。"
  - "结果解读必须包含临床意义判断，不能仅依赖统计显著性。"
  - "报告中所有P值格式必须统一且符合约束（P-R01~R07）。"
  - "方法学描述必须说明加权策略和数据集定义（M-R01~R08, D-R01~R05）。"
  - "图表注释中的P值与表格、正文必须完全一致（P-R07）。"
  - "图表必须达到发表级标准，变量名遵循 variable_naming_conventions.md。"

QC Inspector:
  - "谁产出谁不审查自己——你永远不修改任何内容。"
  - "阻断条件必须严格执行，不得自行解释'可以通融'。"
```

---

## 五、详细案例与代码示例

> 以下为各反模式的具体代码示例，展示**错误写法**与**正确写法**的对比。

### 案例 A1: 正态性假定默认化

**❌ 错误写法**:
```python
# 直接 t 检验，不检查分布
from scipy.stats import ttest_ind
stat, p = ttest_ind(group_a, group_b)
print(f"t={stat:.3f}, p={p:.4f}")
```

**✅ 正确写法**:
```python
from scipy.stats import ttest_ind, shapiro, mannwhitneyu

# Step 1: 正态性检验
sw_a = shapiro(group_a)
sw_b = shapiro(group_b)
print(f"Shapiro-Wilk: Group A p={sw_a.pvalue:.4f}, Group B p={sw_b.pvalue:.4f}")

# Step 2: 根据结果选择方法
if sw_a.pvalue < 0.10 or sw_b.pvalue < 0.10:
    # 不满足正态性 → 非参数检验
    stat, p = mannwhitneyu(group_a, group_b, alternative="two-sided")
    method = "Mann-Whitney U"
else:
    # 满足正态性 → 参数检验
    stat, p = ttest_ind(group_a, group_b)
    method = "Independent t-test"

print(f"Method: {method}, statistic={stat:.3f}, p={p:.4f}")
```

### 案例 A2: 缺失数据静默处理

**❌ 错误写法**:
```python
import pandas as pd
df = pd.read_csv("data.csv")
df_clean = df.dropna()  # 静默删除所有缺失行
result = analyze(df_clean)  # 不报告删除了多少数据
```

**✅ 正确写法**:
```python
import pandas as pd

df = pd.read_csv("data.csv")
n_original = len(df)

# Step 1: 报告缺失模式
missing_report = df.isnull().sum()
missing_pct = (missing_report / n_original * 100).round(2)
print(f"原始数据: {n_original} 行")
print(f"缺失变量统计:\n{missing_report[missing_report > 0]}")

# Step 2: 评估缺失机制 (MCAR/MAR/MNAR)
# 使用 Little's MCAR 检验或可视化模式
from statsmodels.imputation.mice import MCAR
# ... (实际实现需要更复杂的逻辑)

# Step 3: 记录处理策略
strategy = "complete-case (CC) — 用户确认"
n_clean = len(df.dropna())
removed = n_original - n_clean
print(f"处理策略: {strategy}")
print(f"删除行数: {removed} ({removed/n_original:.1%})")

# Step 4: 敏感性分析
# compare CC results with multiple imputation results
```

### 案例 A5: 过度解读亚组分析

**❌ 错误写法**:
```python
# 不做交互检验，直接分亚组报告 P 值
for subgroup in ["male", "female"]:
    sub_data = df[df["sex"] == subgroup]
    stat, p = ttest_ind(sub_data[treatment == 1], sub_data[treatment == 0])
    if p < 0.05:
        print(f"  {subgroup}: p={p:.4f} *** SIGNIFICANT ***")
```

**✅ 正确写法**:
```python
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Step 1: 先做交互检验
model_interaction = smf.ols("outcome ~ treatment * sex", data=df).fit()
interaction_term = "treatment:sex"
interaction_p = model_interaction.pvalues.get(interaction_term, None)

print(f"Interaction test (treatment × sex): p={interaction_p:.4f}")

if interaction_p is not None and interaction_p < 0.10:
    # 交互显著 → 亚组分析有意义
    print("→ Interaction detected, subgroup analysis is justified")
    for subgroup in ["male", "female"]:
        sub_data = df[df["sex"] == subgroup]
        stat, p = ttest_ind(sub_data[treatment == 1], sub_data[treatment == 0])
        print(f"  {subgroup}: effect={stat:.3f}, p={p:.4f}")
else:
    # 交互不显著 → 不应做亚组比较
    print("→ No significant interaction, subgroup analysis is NOT justified")
    print("  Report overall effect only")
```

### 案例 A6: 多重比较不校正

**❌ 错误写法**:
```python
# 5 个终点各自检验，不做校正
for endpoint in ["endpoint1", "endpoint2", "endpoint3", "endpoint4", "endpoint5"]:
    stat, p = ttest_ind(df_treatment[endpoint], df_control[endpoint])
    significant = "***" if p < 0.05 else ""
    print(f"  {endpoint}: p={p:.4f} {significant}")
```

**✅ 正确写法**:
```python
from statsmodels.stats.multitest import multipletests

raw_pvalues = []
for endpoint in ["endpoint1", "endpoint2", "endpoint3", "endpoint4", "endpoint5"]:
    stat, p = ttest_ind(df_treatment[endpoint], df_control[endpoint])
    raw_pvalues.append(p)

# Benjamini-Hochberg 校正 (控制 FDR)
rejected, corrected_p, _, _ = multipletests(raw_pvalues, method="fdr_bh")

for endpoint, raw_p, corr_p, sig in zip(
    ["endpoint1", "endpoint2", "endpoint3", "endpoint4", "endpoint5"],
    raw_pvalues, corrected_p, rejected
):
    status = "*** SIG" if sig else ""
    print(f"  {endpoint}: raw p={raw_p:.4f}, FDR-adjusted p={corr_p:.4f} {status}")
```

### 案例 B1: SAP 偏离未记录

**❌ 错误写法**:
```python
# SAP 说用 ANCOVA，但代码里用了 t 检验
# 原因：数据不完全满足 ANCOVA 假设
# 问题：没有记录这个偏离
stat, p = ttest_ind(group_a, group_b)  # 偏离 SAP，无记录
```

**✅ 正确写法**:
```python
# SAP 定义: ANCOVA with baseline as covariate
# 执行中检查假设
from scipy.stats import levene

# Check homogeneity of regression slopes
model_interaction = smf.ols("y ~ treatment * baseline", data=df).fit()
slope_test_p = model_interaction.pvalues.get("treatment:baseline", 1.0)

if slope_test_p < 0.10:
    # ANCOVA 假设不满足 → 需要偏离
    deviation = {
        "sap_method": "ANCOVA",
        "actual_method": "Welch t-test (no covariate)",
        "reason": f"Regression slope homogeneity violated (interaction p={slope_test_p:.4f})",
        "user_approved": False,  # 必须等待用户确认
    }
    print("⚠️ SAP DEVIATION DETECTED")
    print(f"   SAP method: {deviation['sap_method']}")
    print(f"   Proposed: {deviation['actual_method']}")
    print(f"   Reason: {deviation['reason']}")
    print("   → MUST obtain user approval before proceeding")
    # ... 等待用户确认 ...
else:
    # 假设满足，按 SAP 执行
    model = smf.ols("y ~ treatment + baseline", data=df).fit()
```

### 案例 D1: P 值格式不统一

**❌ 错误写法**:
```python
# P 值格式混乱
print(f"Test 1: p = 0.000")        # P = 0.000 是错误的
print(f"Test 2: P < 0.05")          # 二元报告，丢失信息
print(f"Test 3: p=0.0349")          # 小数位不一致
print(f"Test 4: P=0.03492")         # 小数位不一致
```

**✅ 正确写法**:
```python
def format_p_value(p: float) -> str:
    """统一 P 值格式: P < 0.001 或 P = 0.XXX"""
    if p < 0.001:
        return "P < 0.001"
    else:
        return f"P = {p:.3f}"

# 所有 P 值统一处理
for test_name, p_value in results:
    print(f"{test_name}: {format_p_value(p_value)}")
# Output:
# Test 1: P < 0.001
# Test 2: P = 0.035
# Test 3: P = 0.035
# Test 4: P = 0.035
```

---

## 六、反模式检测检查清单

> 以下检查清单可在 Gate 1.5/2.5/3.5 中引用，用于自动检测反模式。

| 编号 | 检查项 | 检测方法 | 对应反模式 |
|------|--------|---------|-----------|
| AP-01 | 正态性检验存在 | 搜索代码中是否出现 `shapiro`/`normaltest`/`ks_2samp` | A1 |
| AP-02 | 缺失数据处理记录 | 检查是否有 `dropna` 但无缺失报告 | A2 |
| AP-03 | 亚组交互检验 | 搜索 `*` 交互项或 `interaction` 关键词 | A5 |
| AP-04 | 多重比较校正 | 搜索 `multipletests`/`bonferroni`/`fdr` | A6 |
| AP-05 | SAP 偏离记录 | 检查是否有 `deviation`/`变更` 记录 | B1 |
| AP-06 | P 值格式统一 | 正则匹配 `p\s*[=<>]\s*0\.` 格式 | D1 |
| AP-07 | 效应量+CI 报告 | 检查是否有 `ci`/`confidence interval` | D2 |
| AP-08 | 随机种子设置 | 搜索 `random_state`/`set.seed` | C2 |

---

*本文件持续更新。发现新的反模式时，请按上述格式添加。*
