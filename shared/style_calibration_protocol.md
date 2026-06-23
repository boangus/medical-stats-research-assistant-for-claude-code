# 医学写作风格校准 — 期刊特定风格适配

## 目的

根据目标期刊的写作规范调整论文的语言风格、结构格式和专业术语。医学论文的写作风格高度依赖目标期刊的编辑偏好——JAMA 和 Lancet 对摘要格式、人称使用、段落长度有截然不同的要求。本协议确保稿件从首次撰写就符合目标期刊的风格标准。

> **设计边界**: 本协议不是"去 AI 化"工具。目标是让论文读起来像作者写的，因为作者的判断和风格是学术身份的一部分。期刊规范始终优先于个人偏好。

---

## 适用场景

- **主要入口**: report skill 论文写作模式的摘要/正文撰写阶段
- **Pipeline 集成**: report skill 通过 Material Passport 在各阶段传递 Style Profile
- **消费者**: report skill 的草稿撰写模块

---

## 校准流程

### Step 1: 目标期刊确定

询问用户：
> "您的目标期刊是什么？如果尚未确定，我可以根据研究类型推荐匹配的期刊。"

**期刊信息收集**:
- 期刊名称和 ISSN
- 研究领域和子专科
- 影响因子区间（高/中/低）
- 是否有特定的报告规范要求（如 ICMJE、EQUATOR Network）

### Step 2: 期刊风格分析

根据目标期刊提取风格特征。以下为四大类医学期刊的核心风格差异：

---

#### 2A: JAMA 风格 (Journal of the American Medical Association)

**摘要格式**: 结构化摘要（Importance, Objective, Design/Setting/Participants, Main Outcomes and Measures, Results, Conclusions and Relevance）— 字数限制严格

**人称与语态**:
- 摘要：第三人称被动语态为主（"A randomized clinical trial was conducted..."）
- 正文：允许第一人称复数（"We found..."），但多数 JAMA 编辑偏好被动语态
- 结论：使用"这些发现表明"（These findings suggest）而非"我们证明了"

**语言特征**:
- 临床聚焦：强调"患者层面"的结局（patient-level outcomes）
- 精确量化：必须报告绝对风险差异（ARR）和相对风险（RR）
- 临床意义优先：使用"临床意义"（clinical significance）而非仅"统计学意义"
- 术语使用：遵循 AMA Manual of Style

**段落结构**:
- 段落长度适中（100-200 词）
- 每段一个核心论点
- 方法和结果部分高度结构化

**参考文献格式**: AMA 格式（Vancouver 系统的变体），编号制

**特殊要求**:
- 必须包含"关键点"（Key Points）框
- 必须包含"意义"（Relevance）语句
- 图表必须符合 JAMA 图表规范

---

#### 2B: Lancet 风格 (The Lancet)

**摘要格式**: 非结构化叙述摘要（背景、方法、结果、结论 — 但不使用标题标签），250-300 词

**人称与语态**:
- 摘要：第三人称为主（"We did a randomised controlled trial..." 或 "This trial was done..."）
- 正文：允许第一人称复数（"Our findings suggest..."），Lancet 编辑偏好直接的主动语态
- 讨论：可以有观点性表达（"We believe..."、"These data challenge the notion that..."）

**语言特征**:
- 全球卫生视角：强调研究对全球健康的影响
- 叙事性更强：比 JAMA 更注重故事性和可读性
- 批判性讨论：鼓励对既往研究的直接批评
- 术语使用：遵循 The Lancet House Style

**段落结构**:
- 段落较长（150-300 词），叙事性更强
- 讨论部分可以有更自由的结构
- 允许更长的引言（设置研究背景和全球健康语境）

**参考文献格式**: Vancouver 系统（编号制），但 Lancet 有自己的格式微调

**特殊要求**:
- 必须包含"解读"（Interpretation）部分（Lancet 特有）
- 必须包含"资金来源"和"研究团队"的详细声明
- 鼓许包含"评论"（Commentary）和"观点"（Viewpoint）类型文章

---

#### 2C: NEJM 风格 (New England Journal of Medicine)

**摘要格式**: 结构化摘要（Background, Methods, Results, Conclusions）— 非常简洁

**人称与语态**:
- 摘要：被动语态为主（"We randomly assigned..." 逐渐被接受，但传统上偏好被动）
- 正文：中性语态，避免过度使用"我们"
- 结论：极其简洁，通常 1-2 句

**语言特征**:
- 机制聚焦：强调生物学机制和因果关系
- 简洁至上：NEJM 的标志性风格——能用 5 个词说清的不用 10 个词
- 安全性优先：药物试验必须详细报告不良事件
- 术语使用：遵循 NEJM Style Guide

**段落结构**:
- 段落极短（50-150 词），这是 NEJM 的核心风格特征
- 方法部分高度简洁（通常 800-1000 词）
- 结果部分按主要结局→次要结局→安全性顺序组织

**参考文献格式**: Vancouver 系统（编号制），文献数量有严格限制

**特殊要求**:
- 必须包含"背景"（Background）段落（比其他期刊更详细）
- 必须包含"试验设计"（Trial Design）描述
- 图表必须极其简洁——NEJM 不接受复杂的大型图表
- 必须包含"全文化"（Full Text）中的附录（Supplementary Appendix）

---

#### 2D: BMJ 风格 (British Medical Journal)

**摘要格式**: 结构化摘要（Objective, Design, Setting, Participants, Interventions, Main outcome measures, Results, Conclusions）

**人称与语态**:
- 摘要：允许第一人称（"We aimed to..."）
- 正文：允许第一人称复数和主动语态（"We conducted..."）
- 讨论：鼓励作者表达个人观点和实践建议

**语言特征**:
- 患者导向：强调对患者和临床实践的直接影响
- 实用性：强调研究结果的可操作性（"What should I do differently?"）
- 政策相关性：强调对卫生政策的启示
- 术语使用：遵循 BMJ House Style

**段落结构**:
- 段落长度适中（100-200 词）
- 讨论部分鼓励"What this study adds"和"What is already known on this topic"的对比
- 允许更自由的讨论结构

**参考文献格式**: Vancouver 系统（编号制）

**特殊要求**:
- 必须包含"What is already known on this topic"和"What this study adds"框
- 鼓许包含"Practice points"（临床实践要点）
- 必须包含"Patient and public involvement"声明
- 必须包含"Data sharing"声明

---

### Step 3: 风格模板生成

根据目标期刊的分析，生成 **Style Profile**：

```
## Style Profile: [期刊名称]

### 摘要风格
- 格式: [结构化/非结构化]
- 字数限制: [X 词]
- 标题标签: [具体标签列表]
- 人称: [第一人称/第三人称/被动语态]

### 正文风格
- 人称: [允许/偏好/禁止] 第一人称
- 语态: [主动/被动/中性]
- 段落长度: [X-Y 词]
- 术语遵循: [具体 style guide 名称]

### 特殊要求
- [期刊特定要求列表]

### 参考文献格式
- [格式名称和具体规则]

### 冲突检测
- [与作者个人风格的潜在冲突及处理建议]
```

---

## 优先级系统

当 Style Profile 被用于撰写时，应用以下优先级层级：

```
Priority 1 (HARD): 报告规范要求
  → 不可违反。例如，CONSORT 要求报告随机化方法，
    即使期刊风格允许省略，也必须报告。

Priority 2 (STRONG): 目标期刊风格规范
  → 如果用户已指定目标期刊，其风格规范优先。
    例如，NEJM 要求极短段落，作者偏好长段落则需调整。

Priority 3 (SOFT): 作者个人风格
  → 仅在不与 Priority 1 或 2 冲突时应用。
    例如，作者偏好的过渡词选择、引用整合比例——这些可以安全应用。
```

### 冲突解决

当个人风格与期刊规范冲突时：

1. **使用期刊规范**（Priority 1 或 2 优先）
2. **在草稿元数据中记录冲突**：
   ```
   风格冲突: 作者偏好主动语态（样本中 72%），
   但目标期刊（NEJM）传统上偏好被动语态。
   → 按期刊规范使用被动语态。
   ```
3. **通知用户**（每篇稿件仅通知一次）：
   > "注意：您常用的 [特征] 与 [期刊] 的规范不同。我已按期刊规范调整，但您可以手动修改。"

### 安全维度（可自由应用）

这些维度很少与规范冲突：
- 过渡词偏好（在学术语域内）
- 限定词选择
- 报告动词偏好
- 引用整合比例（叙述式 vs 括号式）
- 修饰词密度（在保持精确性的前提下）

### 风险维度（应用前需检查）

这些维度可能与期刊规范冲突：
- 人称（第一人称 vs 第三人称）— 期刊依赖
- 段落长度 — 期刊依赖
- 正式程度 — 期刊依赖
- 语态（主动 vs 被动）— 期刊依赖

---

## 边界情况

### 目标期刊未确定
如果用户尚未确定目标期刊：生成通用医学写作风格（以 AMA Manual of Style 为基础），并在用户确定期刊后更新 Style Profile。

### 中文稿件
如果目标期刊为中文期刊：遵循中华医学会系列杂志的投稿规范，使用中文医学术语标准（人民卫生出版社《医学名词》）。

### 多期刊投稿
如果用户同时考虑多个期刊：为每个目标期刊生成独立的 Style Profile，标注主要差异。

### 风格演变
如果用户提供了多篇不同风格的既往稿件：标注风格变化趋势，在生成 Style Profile 时优先使用最近 2 年的稿件。

---

## 与其他模块的集成

| 模块 | 集成方式 |
|------|---------|
| report skill | 在论文撰写阶段加载 Style Profile，指导全文写作风格 |
| peer-review | 在评审时检查稿件是否符合目标期刊风格 |
| pipeline | 在 Stage 5.0 (Paper Intake) 确定目标期刊后触发校准 |
| shared/handoff_schemas.md | Style Profile 作为 Schema 10 在各阶段传递 |
