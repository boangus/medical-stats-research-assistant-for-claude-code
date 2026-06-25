# Phase 7: 论文写作模式（原 medical-paper）

> 来源：从 SKILL.md L1091-1247 抽取。
> 以下内容合并自 medical-paper skill。本 skill 为双模式：统计报告（上方 §Phase 0-6）+ 论文写作（本节）。
> 论文写作模式由 Pipeline Stage 4 CHECKPOINT [B] 触发，或用户直接调用。

## 双模式架构

```
用户请求
    │
    ├─ "生成统计报告" / "Table 1" / "图表" → 统计报告模式 (§Phase 0-6)
    │
    └─ "写论文" / "paper" / "manuscript" → 论文写作模式 (本节)
         │
         ├─ 从零开始 → Paper Phase 0-7 完整流程
         ├─ 已有论文 → Revision / Revision-Coach 模式
         └─ 仅需摘要/引用/格式 → Abstract / Citation-Check / Format-Convert 模式
```

## 论文写作 Agent Team（12 Agents）

| # | Agent | Role | Paper Phase |
|---|-------|------|-------------|
| 1 | `paper_config_agent` | 配置访谈：论文类型、学科、引用格式、输出格式、语言 | Paper Phase 0 |
| 2 | `literature_search_agent` | 检索策略设计、来源筛选、注释书目 | Paper Phase 1 |
| 3 | `paper_outline_agent` | 论文结构选择、详细大纲、字数分配 | Paper Phase 2 |
| 4 | `evidence_chain_agent` | 论证构建、claim-evidence 链、逻辑流 | Paper Phase 3 |
| 5 | `manuscript_drafter` | 逐节全文草稿、学科语域调整 | Paper Phase 4 |
| 6 | `reference_checker` | 引用格式验证、参考文献完整性、DOI 检查 | Paper Phase 5a |
| 7 | `bilingual_abstract_agent` | 双语摘要（中+英）、各 5-7 关键词 | Paper Phase 5b |
| 8 | `mock_reviewer` | 模拟双盲审稿、五维评分、修改建议（最多 2 轮） | Paper Phase 6 |
| 9 | `output_formatter` | 转换为 LaTeX/DOCX/PDF/Markdown、期刊格式化 | Paper Phase 7 |
| 10 | `writing_mentor` | Plan 模式苏格拉底导师：逐章引导 | Plan Step 0-3 |
| 11 | `figure_generator` | 生成出版级图表代码（matplotlib/ggplot2） | Paper Phase 4/7 |
| 12 | `revision_planner` | 解析非结构化审稿意见 → 结构化 Revision Roadmap | Revision-Coach |

## 论文写作 Operational Modes（11 Modes）

| Mode | Trigger | Agents | Output |
|------|---------|--------|--------|
| `full` | "Write a paper" | All 12 | Complete paper draft |
| `plan` | "guide my paper" | 1→10→3→4 | Chapter Plan + INSIGHT |
| `outline-only` | "Paper outline" | 1→2→3 | Detailed outline + evidence map |
| `revision` | "Revise paper" | 8→5→6 | Revised draft + Response to Reviewers |
| `revision-coach` | "parse reviews" | 12 only | Revision Roadmap |
| `abstract-only` | "Write abstract" | 1→7 | Bilingual abstract + keywords |
| `lit-review` | "Literature review" | 1→2 | Annotated bibliography + synthesis |
| `format-convert` | "Convert to LaTeX" | 9 only | Formatted document |
| `citation-check` | "Check citations" | 6 only | Citation error report |
| `disclosure` | "AI disclosure" | 9 only | AI-usage disclosure paragraph |
| `rebuttal-audit` | "audit my response" | 12 only | Rebuttal QA report |

### Quick Mode Selection Guide

| 情况 | 推荐 Mode | 说明 |
|------|----------|------|
| 从零开始有明确 RQ | `full` | 完整 8 阶段流程 |
| 需要先规划再写 | `plan` | 苏格拉底引导 |
| 只要大纲 | `outline-only` | 仅 Phase 1-3 |
| 有论文收到审稿意见 | `revision` | 解析 + 修改 |
| 有非结构化审稿意见 | `revision-coach` | 结构化 Roadmap |
| 只要摘要 | `abstract-only` | 双语摘要 |
| 要检查引用 | `citation-check` | 引用合规 |
| 要转换格式 | `format-convert` | LaTeX/DOCX/PDF |
| 要文献综述 | `lit-review` | 注释书目 |
| 要 AI 使用声明 | `disclosure` | 期刊特定声明 |
| 有回复草稿要 QA | `rebuttal-audit` | 覆盖检查 |

## 论文写作 8 Phase 工作流

```
Paper Phase 0: CONFIG        → [paper_config_agent]              → Paper Configuration Record
Paper Phase 1: RESEARCH      → [literature_strategist]      → Search Strategy + Source Corpus
Paper Phase 2: ARCHITECTURE  → [structure_architect]        → Paper Outline + Evidence Map
Paper Phase 3: ARGUMENTATION → [argument_builder]           → Argument Blueprint
Paper Phase 4: DRAFTING      → [draft_writer]               → Complete Draft
Paper Phase 5a: CITATIONS    → [citation_compliance] ──┐    → Citation Audit Report
Paper Phase 5b: ABSTRACT     → [abstract_bilingual]   ─┘    → Bilingual Abstract (parallel)
Paper Phase 6: PEER REVIEW   → [peer_reviewer]              → Review Report (max 2 loops)
Paper Phase 7: FORMAT        → [formatter]                  → Final Output Package
```

### Checkpoint Rules

1. **IRON RULE**: 用户必须确认 Paper Configuration Record 后才能进入 Paper Phase 1
2. **Paper Phase 2 → 3**: 用户必须批准大纲（可要求重组）
3. **IRON RULE**: 最多 2 轮修改；未解决项 → "Acknowledged Limitations"
4. **Peer Review** Critical-severity 问题阻断进入 Paper Phase 7
5. 用户可跳过 Paper Phase 1（如有自有来源）

## 引用格式支持

APA 7.0（默认）、Chicago（Author-Date 或 Notes-Bibliography）、MLA 9、IEEE、Vancouver。
`output_formatter` 支持后期引用格式转换："Convert citations to [format]"。

## 输出格式

- **文本**: LaTeX (.tex + .bib), DOCX (via Pandoc), PDF, Markdown
- **图表**: Python matplotlib / R ggplot2，APA 7.0 格式，色盲安全调色板
- **引用**: 5 种格式互转
- 参考：shared/references/word_count_conventions.md — 医学期刊字数规范

## Style Calibration（可选）

用户提供 3+ 篇过往论文，pipeline 学习其写作风格（句式节奏、词汇偏好、引用整合风格）。
作为草稿阶段的软指南应用；学科规范始终优先。参见 `shared/style_calibration_protocol.md`。

## Writing Quality Check

草稿自审步骤中应用的写作质量检查清单：
- 检测过度使用的 AI 典型术语
- 检查破折号过度使用
- 移除 throat-clearing openers
- 检查段落长度均匀性
- 检查句式单调性

## Generator-Evaluator Contract Protocol (v3.6.6)

> 仅适用于 `full` 模式。将 Paper Phase 4（写作）和 Paper Phase 6（审稿）拆分为 paper-blind / paper-visible 调用对。

**四调用结构**：
1. **Paper Phase 4a** — Writer paper-blind pre-commitment（仅看合同+元数据）
2. **Paper Phase 4b** — Writer paper-visible drafting + self-scoring（写全文+自评）
3. **Paper Phase 6a** — Evaluator paper-blind pre-commitment（仅看合同+元数据+4a 输出）
4. **Paper Phase 6b** — Evaluator paper-visible scoring + decision（评分+决策）

**核心机制**：物理分离调用——4a 永远看不到运行时草稿，6a 永远看不到 4b 草稿。这消除了"先读论文再合理化标准"的漂移路径。

### Unusable Handling

Writer/evaluator phase 两次 lint 失败 → `[GENERATOR-PHASE-ABORTED]` → 用户介入决定重试/回退/降级。

## 论文写作反例与黑名单

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 1 | 不做配置访谈直接写论文 | 论文类型/学科/引用格式不确定会导致返工 | Phase 0 配置访谈必须完成 |
| 2 | 引用不验证直接使用 | 可能引用不存在的文献 | 每个引用必须通过 DOI 或 WebSearch 验证 |
| 3 | 超过 2 轮修改仍继续 | 进入无限修改循环 | 最多 2 轮，剩余项归入 "Acknowledged Limitations" |
| 4 | 模拟审稿人互相参考 | 破坏独立性 | 5 位审稿人独立审阅，不交叉引用 |
| 5 | Peer Review 修改论文原稿 | 审稿人只评审不修改 | 所有审稿输出为独立文档 |
| 6 | Paper Phase 6a/6b 混淆 system prompt 和 user content | 动态 LLM 输出不应进入不变策略面 | system prompt 仅含不变策略，动态内容在 user content 中 |
| 7 | 在非 full 模式调用 Generator-Evaluator 合同 | 仅 full 模式适用 | 9 个非 full 模式不触发此协议 |
| 8 | 跳过 Style Calibration 直接使用默认风格 | 可能不符合用户写作习惯 | 可选但推荐，提供 3+ 篇过往论文 |

---

## 论文写作引用与集成

| 集成方向 | 描述 |
|---------|------|
| **上游: systematic-survey → report** | Stage 5.1 文献检索提供研究基础 |
| **上游: report 统计模式 → 论文模式** | Stage 4 CHECKPOINT [B] 提供 final_report + figures + tables |
| **下游: report → peer-review** | Stage 5.4 审稿，Revision Roadmap 可直接用作修改输入 |
| **下游: report → pipeline** | 通过 passport 状态追踪，pipeline 编排 Paper Track 全流程 |
