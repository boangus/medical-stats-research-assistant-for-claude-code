---
version: "0.3.0"
name: 方法学-statistics-methods
description: "方法学统计与方法指南知识库。用于临床研究设计、医学文献解读、统计学方法应用。涵盖干预性研究、观察性研究、外科数据库研究的方法学原则和最佳实践。"
data_access_level: reference
task_type: knowledge-retrieval
works_with: [analysis-plan, data-prep, analysis-exec, report]
allowed-tools:
  - Read
  - Grep
argument-hint: [主题、方法名称或章节编号]
trigger: 统计方法 / 研究设计 / 方法学 / 指南 / 章节 / 方法学 / 临床试验 / 观察性研究 / 诊断试验 / 数据库研究 / 非劣效性 / 倾向性评分 / 生存分析 / 缺失数据 / 多重比较 / 样本量 / 混杂控制 / 贝叶斯 / Meta分析 / 系统综述 / 报告规范 / 效应量 / 预测模型 / 医学统计 / biostatistics / study design / clinical trial / observational study / survival analysis / propensity score / missing data / sample size / meta-analysis / 统计咨询 / 方法选择 / 统计方法探讨 / ch01~ch55 / 第1章 / 第2章 / 剂量探索 / 整群随机 / 阶梯楔形 / 实效性试验 / 估计目标 / 意向性治疗 / 多重插补 / logistic回归 / ROC / 决策曲线 / 双重差分 / 病例对照 / 中介分析 / 孟德尔随机化 / E值 / 指示性混杂 / 边际效应 / 协变量校正 / 成本效益 / 深度学习 / NNT / MCID / 关口策略
---

# 方法学 统计与方法指南

**主编**: Edward H. Livingston, Roger J. Lewis | **主译**: 雷翀 | **页数**: ~370 | **章节**: 41（删除了14章数据库指南和深度学习，与统计分析无关） | **来源**: 书籍PDF扫描版 | **生成日期**: 2026-05-29

## 工作流程

### Phase 1: 意图识别 → 确定查询范围

| 用户输入 | 识别规则 | 对应操作 |
|---------|---------|---------|
| 仅加载核心框架 | 无参数或"帮我看看方法学指南" | Phase 2 → 跳过，直接展示核心框架 |
| 单章查询 | 包含章节号或方法名（"ch10""倾向性评分"） | Phase 2 → 加载单章 |
| 跨章合成 | 涉及多个方法（"生存分析+缺失数据"） | Phase 2 → 加载多章 → Phase 3 (冲突检查) |
| 方法选择咨询 | "该用什么方法""怎么分析" | Phase 2 → 🔴 研究类型确认 → 方法决策树 → 推荐章节 |
| 浏览索引 | "有哪些章节" | 展示章节索引表 |

**输入**: 用户查询文本
**输出**: 查询类型判定 + 需要加载的章节列表

### 🔴 CHECKPOINT: 研究类型确认

在给出方法学建议前，自动检查上下文：

- **用户已明确研究类型**（RCT/观察性/诊断） → 按类型匹配的方法和章节回答
- **用户未提供研究类型** → **🛑 STOP** 必须暂停，询问："这是用于 RCT、观察性研究还是诊断试验？"

> 研究类型不明确时，不得未经确认直接给出方法建议。RCT 的方法（如 ITT/ANCOVA）与观察性研究的方法（如 PSM/DAG/多变量调整）体系不同，交叉套用可能导致结论无效。

### 🛑 STOP: 跨上下文冲突检查

当用户提问涉及多个章节的交叉内容（如"SEER 数据库做生存分析"同时涉及数据库方法 + 生存分析方法），合成回答前执行：

1. 各章节推荐的方法是否适用于同一研究类型？
2. 是否有章节特定的前提条件（如 RCT 方法套用到观察性研究）？
3. 冲突时以章节内容为准，标注差异

> [ADAPTIVE] 仅检测到跨章节检索时触发。单章查询自动跳过。

### 🔴 CHECKPOINT: 方法适用性验证

加载目标章节并提取方法后，自动验证方法是否适用于用户的研究场景：

| 检查项 | 触发条件 | 处理 |
|-------|---------|------|
| 研究类型与章节方法匹配 | RCT 用户索取观察性方法（或反之） | **🛑 STOP** 暂停，提示用户方法体系不匹配，推荐替代方法 |
| 数据特征满足方法前提假设 | 用户数据不满足正态/方差齐/PH假设等 | 标记"建议先验证数据特征"，推荐假设检验章节(ch10/ch15) |
| 效应量报告要求 | 章节建议 OR/HR 但未指定效应量类型 | 自动补全常用效应量配置 + 置信区间要求 |

> [MANDATORY] 方法适用性检查未通过时，**必须警告用户**并给出替代方案。不得跳过检查直接给出不兼容的方法建议。

## 核心框架速查

> 本节为快速导航。详细内容见对应章节。

| 领域 | 主题 | 核心要点 | 详见 |
|------|------|---------|------|
| **研究设计** | 非劣效性试验 | 界值需临床依据；单侧CI；ITT+PP 同时分析 | [ch01](chapters/ch01-non-inferiority-trials.md) |
| | 整群随机 | ICC 调整样本量；GEE/多层模型 | [ch04](chapters/ch04-cluster-randomized-trials.md) |
| | 阶梯楔形 | 时间趋势调整；混合模型 | [ch05](chapters/ch05-stepped-wedge-clinical-trials.md) |
| | 实效性试验 | 外部效度优先；宽松入组 | [ch03](chapters/ch03-pragmatic-trials.md) |
| **统计分析** | 样本量 | α + power + 效应量 + MCID 原则 | [ch06](chapters/ch06-sample-size-calculations.md) |
| | ITT | 按随机分组分析；非劣效性需 PP 补充 | [ch13](chapters/ch13-intention-to-treat-principle.md) |
| | 缺失数据 | MCAR→完整病例 / MAR→多重插补 / MNAR→敏感性分析 | [ch12](chapters/ch12-missing-data.md), [ch20](chapters/ch20-multiple-imputation.md) |
| | 多重比较 | 预定义校正方法；Bonferroni/Holm/FDR/关口策略 | [ch18](chapters/ch18-multiple-comparisons-methods.md), [ch19](chapters/ch19-gatekeeping-strategies.md) |
| **观察性研究** | 倾向性评分 | 匹配/分层/调整/IPW 四种方式；仅控制已测量混杂 | [ch35](chapters/ch35-propensity-scores.md) |
| | 混杂控制 | 设计阶段(随机化/匹配/限制) + 分析阶段(分层/回归/PS) | [ch33](chapters/ch33-covariate-adjustment.md) |
| | 因果推断 | MR/中介分析/DID；观察性研究因果推断需谨慎 | [ch27](chapters/ch27-mendelian-randomization.md), [ch30](chapters/ch30-mediation-analysis.md), [ch24](chapters/ch24-difference-in-differences.md) |
| **结果报告** | 效应量 | 同时报告点估计 + 95% CI + 精确 p 值 | [ch31](chapters/ch31-odds-ratio.md), [ch32](chapters/ch32-marginal-effects.md) |
| | 预测模型 | C-statistic >0.7 合理 / 校准曲线 / DCA | [ch39](chapters/ch39-c-statistic.md), [ch23](chapters/ch23-decision-curve-analysis.md) |
| | 贝叶斯 | 先验+数据→后验；小样本/适应性设计/证据综合 | [ch22](chapters/ch22-bayesian-analysis.md), [ch38](chapters/ch38-hierarchical-bayesian-models.md) |

---

## 异常处理与失败模式

> 使用知识库时可能遇到以下场景。按触发条件执行对应处理，确保检索结果可靠。

| # | 触发条件 | 一线处理 | 仍失败兜底 |
|---|---------|---------|-----------|
| 1 | 用户询问的主题在核心框架和章节索引中均未找到 | 使用 WebSearch 搜索该主题的 方法学 指南相关内容 | 告知用户该主题不在本书覆盖范围，推荐 biomedical-search 或 medical-research skill |
| 2 | 用户指定的章节文件不存在或为空（stub） | 尝试从核心框架中提取该主题的相关摘要 | 标记为"章节内容待补充"，返回核心框架中可用信息 |
| 3 | 用户提问涉及多个章节的交叉内容（如"SEER数据库做生存分析"） | 先加载数据库章节（ch46），再加载方法章节（ch10），合并关键要点 | 返回两个章节的核心摘要，标注"跨章节合成" |
| 4 | 同一条目在多个章节有不同描述（如倾向性评分在 ch35 和核心框架均有内容） | 以章节内容为详细版，核心框架为摘要版，优先使用章节内容 | 若两者冲突，以章节内容为准，在回答中标注差异 |
| 5 | 用户要求的方法在本书中仅以简短概念存在（无独立章节） | 从核心框架提取相关内容，补充跨章引用 | 告知用户该主题描述有限，推荐其他来源 |
| 6 | 用户询问的统计方法需要代码实现而非方法学解释 | 返回方法学原则+关键参数（如 alpha/beta/效应量），不提供完整代码 | 告知用户本 skill 是方法学指南而非代码库，推荐 MSRA templates/ |
| 7 | 章节内容与 MSRA 流水线当前阶段不匹配（如在 data-prep 阶段问生存分析章节） | 返回内容本身，附加"该内容属于 MSRA 分析执行阶段（Stage 3）"的上下文提示 | 无额外操作 |
| 8 | 用户连续追问深度问题，超出章节摘要范围 | 首次回答后提示"如需更详细内容，建议参考原书第 X 章" | 提供该章节可 OCR 补充的计划 |

**IRON RULE**: 遇到章节 stub 时，**不能编造不存在的章节内容**。必须如实告知用户该章节为摘要版，并优先从核心框架提供等价信息。

---

## 反例与黑名单

> **以下行为在使用本技能时必须避免**。违反任何一条将导致统计方法误用或结论不可靠。

### 🚫 检索与引用禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 1 | 章节 stub 为空时编造内容填充 | 编造的方法学内容可能误导研究设计 | 核心框架有摘要就用，没有则告知用户 |
| 2 | 跨章节引用时忽略上下文冲突（如 RCT 方法套用到观察性研究） | 研究类型决定方法论体系，错位引用导致结论无效 | 引用时标注来源章节的研究类型上下文 |
| 3 | 仅检索一个章节就给出综合性答案 | 很多主题在多个章节有不同角度的讨论 | 主题索引交叉引用全面检索后再回答 |
| 4 | 将本书方法学指南当作代码实现文档 | 本书不提供具体编程实现 | 返回原则和参数后建议 MSRA templates/ |

### 🚫 统计方法应用禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 5 | 非劣效性试验不指定界值就给出解释 | 界值选择直接影响结论，没有界值就无意义 | 始终提醒用户：先确定非劣效界值 |
| 6 | 观察性研究推荐因果结论（如"X 导致 Y"） | 观察性研究无法排除混杂，因果关系推断需要随机化或专门因果推断方法 | 使用"关联""相关""预测"等措辞 |
| 7 | 多重比较时仅推荐 Bonferroni 而不考虑其他方法 | Bonferroni 过于保守，在检验数多时效能极低 | 根据检验数和相关性推荐 Holm/FDR/关口策略 |
| 8 | 缺失数据处理时默认推荐完整病例分析 | 完整病例分析在 MAR/MNAR 下有严重偏倚 | 先判断缺失机制，再推荐插补或敏感性分析 |
| 9 | 报告 AUC 时不说明区分度分级标准 | AUC 0.6 和 0.9 的临床价值差异巨大 | 附带标准：>0.7合理，>0.8良好，>0.9优秀 |

### 🚫 方法论边界禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 10 | 将 ICH E9(R1) Estimands 框架硬套于观察性研究 | Estimands 框架专为临床试验设计 | 观察性研究使用"目标估计量"定义 |
| 11 | ITT 分析适用于所有研究类型 | ITT 在非劣效性试验中可能过于保守 | 非劣效性试验同时报告 ITT + 符合方案集 |
| 12 | 忽略本书是 2021 年中文翻译版 | 部分内容可能已有更新（如深度学习章节） | 标注出版年份，建议结合最新文献 |

---

## 章节索引

| # | 标题 | 关键框架 |
|---|------|----------|
| [ch01](chapters/ch01-non-inferiority-trials.md) | 非劣效性试验 | 非劣效性界值、单侧置信区间 |
| [ch02](chapters/ch02-dose-finding-trials.md) | 剂量探索试验 | 剂量-反应模型、二期试验 |
| [ch03](chapters/ch03-pragmatic-trials.md) | 实效性试验 | 外部效度、真实世界证据 |
| [ch04](chapters/ch04-cluster-randomized-trials.md) | 整群随机试验 | ICC、广义估计方程 |
| [ch05](chapters/ch05-stepped-wedge-clinical-trials.md) | 阶梯楔形临床试验 | 时间趋势调整、混合模型 |
| [ch06](chapters/ch06-sample-size-calculations.md) | 样本量计算 | 效能分析、MCID |
| [ch07](chapters/ch07-minimal-clinically-important-difference.md) | 最小临床重要性差值 | MCID确定方法 |
| [ch08](chapters/ch08-randomization-in-clinical-research.md) | 随机化 | 区组随机化、分层 |
| [ch09](chapters/ch09-equipoise-in-research.md) | 均势 | 临床研究伦理 |
| [ch10](chapters/ch10-time-to-event-analysis.md) | 时间事件分析 | 生存分析、Cox回归 |
| [ch11](chapters/ch11-composite-endpoints.md) | 复合结局测量 | 效用加权、临床意义 |
| [ch12](chapters/ch12-missing-data.md) | 缺失数据 | MCAR/MAR/MNAR |
| [ch13](chapters/ch13-intention-to-treat-principle.md) | 意向性治疗原则 | ITT分析 |
| [ch14](chapters/ch14-mixed-models-for-repeated-measures.md) | 混合模型 | 重复测量分析 |
| [ch15](chapters/ch15-logistic-regression.md) | Logistic回归 | 二分类结局分析 |
| [ch16](chapters/ch16-logistic-regression-diagnostics.md) | Logistic回归诊断 | 模型评估、ROC曲线 |
| [ch17](chapters/ch17-number-needed-to-treat.md) | 需治数 | NNT计算与解读 |
| [ch18](chapters/ch18-multiple-comparisons-methods.md) | 多重比较法 | 假阳性控制 |
| [ch19](chapters/ch19-gatekeeping-strategies.md) | 关口策略 | 多终点试验设计 |
| [ch20](chapters/ch20-multiple-imputation.md) | 多重插补 | 缺失数据处理 |
| [ch21](chapters/ch21-interpretation-of-early-stopped-trials.md) | 早期终止试验解读 | 期中分析、O'Brien-Fleming |
| [ch22](chapters/ch22-bayesian-analysis.md) | 贝叶斯分析 | 先验分布、后验推断 |
| [ch23](chapters/ch23-decision-curve-analysis.md) | 决策曲线分析 | 临床净获益 |
| [ch24](chapters/ch24-difference-in-differences.md) | 双重差分法 | 政策评估 |
| [ch25](chapters/ch25-case-control-studies.md) | 病例对照研究 | OR计算、选择偏倚 |
| [ch26](chapters/ch26-meta-analysis.md) | Meta分析 | 证据综合、PRISMA |
| [ch27](chapters/ch27-mendelian-randomization.md) | 孟德尔随机化 | 工具变量、因果推断 |
| [ch28](chapters/ch28-e-value.md) | E值 | 未测量混杂评估 |
| [ch29](chapters/ch29-indication-bias.md) | 指示性混杂 | 适应症偏倚 |
| [ch30](chapters/ch30-mediation-analysis.md) | 中介分析 | 因果路径分析 |
| [ch31](chapters/ch31-odds-ratio.md) | 比值比 | OR解读与应用 |
| [ch32](chapters/ch32-marginal-effects.md) | 边际效应 | Logistic回归结果解释 |
| [ch33](chapters/ch33-covariate-adjustment.md) | 协变量校正 | 混杂控制 |
| [ch34](chapters/ch34-treatment-effects-in-multicenter-rcts.md) | 多中心试验治疗效果 | 中心效应 |
| [ch35](chapters/ch35-propensity-scores.md) | 倾向性评分 | 混杂控制方法 |
| [ch36](chapters/ch36-froc-curves.md) | FROC曲线 | 诊断准确性评估 |
| [ch37](chapters/ch37-random-effects-meta-analysis.md) | 随机效应Meta分析 | 异质性处理 |
| [ch38](chapters/ch38-hierarchical-bayesian-models.md) | 层次贝叶斯模型 | 多层数据分析 |
| [ch39](chapters/ch39-c-statistic.md) | C统计量 | 模型区分度评估 |
| [ch40](chapters/ch40-cost-effectiveness-analysis.md) | 成本-效益分析 | ICER、QALY |
| [ch41](chapters/ch41-time-horizon-selection.md) | 时间范围选择 | 经济学评价 |

---

## 主题索引

- **贝叶斯分析** → ch22, ch38
- **比值比 (OR)** → ch31
- **边际效应** → ch32
- **病例对照研究** → ch25
- **成本-效益分析** → ch40, ch41
- **C统计量** → ch39
- **缺失数据** → ch12, ch20
- **倾向性评分** → ch35
- **随机化** → ch8
- **随机效应Meta分析** → ch37
- **生存分析** → ch10
- **样本量计算** → ch6
- **意向性治疗原则** → ch13
- **中介分析** → ch30
- **整群随机试验** → ch4
- **指示性混杂** → ch29
- **E值** → ch28
- **非劣效性试验** → ch1
- **风险预测模型** → ch39
- **混杂控制** → ch33, ch35
- **阶梯楔形试验** → ch5
- **均势** → ch9
- **Logistic回归** → ch15, ch16
- **MCID** → ch7
- **Meta分析** → ch26, ch37
- **多重比较** → ch18, ch19
- **多重插补** → ch20
- **NNT** → ch17
- **孟德尔随机化** → ch27
- **实效性试验** → ch3
- **双重差分法** → ch24
- **决策曲线分析** → ch23

---

## 支持文件

- [glossary.md](glossary.md) — 关键术语定义
- [patterns.md](patterns.md) — 方法学模式库
- [cheatsheet.md](cheatsheet.md) — 快速参考表和决策指南

---

## 范围与限制

此技能涵盖《方法学统计与方法指南》书籍内容（雷翀主译，2021年出版）。经过裁剪，保留 41 章与统计分析直接相关的内容，删除了数据库实践指南（ch43-55）和深度学习（ch42）章节。
来源为书籍PDF扫描版，章节内容通过OCR从原书提取（逐章处理），已填充章节可从章节文件获取完整内容。

- 本书是方法学指南，不提供具体统计软件的代码实现
- 对于本书范围之外的主题，请查询 `biomedical-search` 或 `medical-research` 技能
- 对于具体代码实现，请参考 `MSRA shared/templates/`




