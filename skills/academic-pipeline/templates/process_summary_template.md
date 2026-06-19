---
study_id: MSRA-{YYYY}-{NNN}
version: v1.0
created_date: YYYY-MM-DD
status: draft
template_type: process_summary
---

# Paper Creation Process Summary 模板

> MSRA 项目专用。Stage 6 全流程总结模板，记录人机协作完整历程。
> 对齐 `skills/academic-pipeline/references/process_summary_protocol.md`。
>
> **触发条件**：Stage 5.9 (FINALIZE) 完成后自动触发。
> **输出格式**：Markdown → LaTeX → PDF（tectonic 编译）。
> **文件命名**：`paper_creation_process.md`（中文）/ `paper_creation_process_en.md`（英文）。

---

## 1. Paper Information（论文信息 / Paper Information）

| 字段 | 值 | 说明 |
|------|-----|------|
| 标题（Title） | [{论文标题}] | 最终定稿标题 |
| 最终交付物（Final Deliverables） | [{交付物清单}] | 如：manuscript.docx, response_to_reviewers.md, process_summary.pdf |
| 流水线版本（Pipeline Version） | [{MSRA v0.8.0}] | 使用的 MSRA Pipeline 版本 |
| 开始日期（Start Date） | [{YYYY-MM-DD}] | Stage 1 启动日期 |
| 结束日期（End Date） | [{YYYY-MM-DD}] | Stage 6 完成日期 |
| 总时长（Total Duration） | [{N} 天] | 从启动到完成的总天数 |
| 轨道（Track） | [{report_only / full_paper}] | Pipeline 轨道 |

---

## 2. Executive Summary（执行摘要 / Executive Summary）

> 1-2 页概览，供快速了解全流程。

- **研究问题一句话陈述**：[{研究问题一句话}]
- **最终成果概述**：[{最终成果概述}]
- **关键决策数量**：[{N} 项]
- **质量门闸通过情况**：[{N}/{M} 门闸通过]
- **迭代轮次**：[{N} 轮审稿修订]
- **核心结论**：[{核心结论一句话}]

---

## 3. Stage-by-Stage Process（逐阶段过程记录 / Stage-by-Stage Process）

> 每个阶段记录：输入、关键决策、用户干预、产物、时长。用户指令需逐字引用。

### Stage 1: Data Preparation（数据准备）

| 项目 | 内容 |
|------|------|
| Input（输入） | [{用户初始指令，逐字引用}] |
| Key Decisions（关键决策） | [{关键决策点列表}] |
| User Interventions（用户干预） | [{用户干预内容}] |
| Output（产物） | [{产物清单：cleaned_data.csv, cleaning_log.md, eda_report.md}] |
| Duration（时长） | [{N} 小时] |

### Stage 1.5: Data Quality Gate（数据质量门闸）

| 项目 | 内容 |
|------|------|
| 检查项通过 | [{N}/9 项通过] |
| 判定 | [{PASS / CONDITIONAL / BLOCKED}] |
| 关键风险 | [{如有，描述}] |

### Stage 2: Analysis Plan（分析计划）

| 项目 | 内容 |
|------|------|
| Input（输入） | [{清洗后数据 + 研究问题}] |
| Key Decisions（关键决策） | [{如：选择 Cox 回归 / 竞争风险模型等}] |
| User Interventions（用户干预） | [{用户对 SAP 的修改意见}] |
| Output（产物） | [{SAP.md, estimand_definition.md, analysis_specification.md}] |
| Duration（时长） | [{N} 小时] |

### Stage 2.5: SAP Quality Gate（SAP 质量门闸）

| 项目 | 内容 |
|------|------|
| 检查项通过 | [{N}/8 项通过] |
| 判定 | [{PASS / CONDITIONAL / BLOCKED}] |
| 关键风险 | [{如有，描述}] |

### Stage 3: Analysis Execution（分析执行）

| 项目 | 内容 |
|------|------|
| Input（输入） | [{SAP + 清洗后数据}] |
| Key Decisions（关键决策） | [{如：假设不满足时的方法切换}] |
| User Interventions（用户干预） | [{用户对分析结果的反馈}] |
| Output（产物） | [{analysis_code.R, tables/*.docx, figures/*.png}] |
| Duration（时长） | [{N} 小时] |

### Stage 3.5: Results Quality Gate（结果质量门闸）

| 项目 | 内容 |
|------|------|
| 检查项通过 | [{N}/9 项通过] |
| 判定 | [{PASS / CONDITIONAL / BLOCKED}] |
| 关键风险 | [{如有，描述}] |

### Stage 4: Statistical Report（统计报告）

| 项目 | 内容 |
|------|------|
| Input（输入） | [{分析结果 + SAP}] |
| Key Decisions（关键决策） | [{如：报告格式选择、图表布局}] |
| User Interventions（用户干预） | [{用户对报告的修改意见}] |
| Output（产物） | [{final_report.md, final_report.html}] |
| Duration（时长） | [{N} 小时] |
| **Checkpoint Decision** | **[{A}] report_only / [{B}] full_paper** |
| **User Quote** | "[{用户选择原话，逐字引用}]" |

### Stage 5: Paper Track（论文写作，如适用）

#### Stage 5.0: Paper Intake

| 项目 | 内容 |
|------|------|
| Input | [{msra_handoff_bundle.md}] |
| Key Decisions | [{如：论文类型、目标期刊、引用格式}] |
| Output | [{paper_configuration.md}] |
| Duration | [{N} 小时] |

#### Stage 5.1: Literature Search

| 项目 | 内容 |
|------|------|
| Input | [{Literature Seed from Handoff Bundle}] |
| Key Decisions | [{如：检索策略、纳入排除标准}] |
| Output | [{bibliography.md, synthesis_report.md}] |
| Duration | [{N} 小时] |

#### Stage 5.2: Paper Writing

| 项目 | 内容 |
|------|------|
| Input | [{Handoff Bundle + 文献综述}] |
| Key Decisions | [{如：章节结构、论证策略}] |
| User Interventions | [{用户对初稿的修改意见}] |
| Output | [{paper_draft.md}] |
| Duration | [{N} 小时] |

#### Stage 5.5: Integrity Check（完整性检查，阻断式）

| 项目 | 内容 |
|------|------|
| 检查结果 | [{PASS / FAIL}] |
| 关键问题 | [{如有，描述}] |

#### Stage 5.6: Peer Review（同行评审）

| 项目 | 内容 |
|------|------|
| 评审团组成 | [{EIC + 方法学 + 领域 + 写作 + DA}] |
| 评审意见数 | [{N} 条}] |
| 总体评分 | [{XX}/100] |
| 建议 | [{Accept / Minor Revision / Major Revision / Reject}] |

#### Stage 5.7: Revision（修订）

| 项目 | 内容 |
|------|------|
| Input | [{评审报告 + paper_draft.md}] |
| Key Decisions | [{如：哪些意见接受、哪些反驳}] |
| User Interventions | [{用户对修订的指导}] |
| Output | [{revised_paper.md, response_to_reviewers.md}] |
| Duration | [{N} 小时] |

#### Stage 5.8: Final Integrity（最终完整性检查，阻断式）

| 项目 | 内容 |
|------|------|
| 检查结果 | [{PASS / FAIL}] |
| 关键问题 | [{如有，描述}] |

#### Stage 5.9: Finalize（定稿导出）

| 项目 | 内容 |
|------|------|
| Output | [{final_paper.docx, final_paper.pdf}] |
| 格式 | [{DOCX + PDF}] |
| Duration | [{N} 小时] |

---

## 4. Iteration Details（迭代详情 / Iteration Details）

| 轮次 | 审稿意见数 | 修订项数 | 复审结果 | 时长 |
|------|-----------|---------|---------|------|
| Round 1 | [{N}] | [{N}] | [{Accept / Minor / Major}] | [{N} 天] |
| Round 2 | [{N}] | [{N}] | [{Accept}] | [{N} 天] |
| ... | ... | ... | ... | ... |

---

## 5. Interaction Pattern Summary（交互模式汇总 / Interaction Pattern Summary）

| 指标 | 值 | 说明 |
|------|-----|------|
| 用户角色（User Role） | [{Director / Collaborator / Reviewer}] | 用户在协作中的主要角色 |
| Claude 角色（Claude Role） | [{Executor / Advisor / Co-author}] | Claude 在协作中的主要角色 |
| 总干预数（Total Interventions） | [{N}] | 用户主动介入次数 |
| 方向纠正数（Direction Corrections） | [{N}] | 用户纠正 AI 方向的次数 |
| 关键转折点（Key Turning Points） | [{N}] | 改变流程方向的关键时刻 |
| 跳过检查点（Checkpoints Skipped） | [{N / Y}] | 用户选择跳过的检查点 |
| 用户覆盖数（User Overrides） | [{N}] | 用户否决 AI 建议的次数 |

---

## 6. User Key Decisions（用户关键决策 / User Key Decisions）

> 按时间顺序记录用户做出的每个重要决策，含逐字引用。

1. **[{YYYY-MM-DD}]** [{决策内容，含逐字引用}]
   - 背景：[{决策背景}]
   - 决策："[{用户原话}]"
   - 影响：[{对后续流程的影响}]

2. **[{YYYY-MM-DD}]** [{决策内容}]
   - 背景：[{决策背景}]
   - 决策："[{用户原话}]"
   - 影响：[{对后续流程的影响}]

3. ...（继续列出所有关键决策）

---

## 7. Key Lessons（关键经验教训 / Key Lessons）

### 7.1 Positive Lessons（正面经验，可复制推广）

1. [{经验1：具体行为 + 量化效果}]
2. [{经验2：具体行为 + 量化效果}]
3. ...

### 7.2 Negative Lessons（反面教训，需规避）

1. [{教训1}]
   - 当时如何做：[{具体行为}]
   - 为何出错：[{原因分析}]
   - 如何避免：[{改进措施}]
2. [{教训2}]
   - 当时如何做：[{具体行为}]
   - 为何出错：[{原因分析}]
   - 如何避免：[{改进措施}]

### 7.3 Improvement Recommendations（改进建议）

1. [{建议1：谁做 + 做什么 + 何时完成}]
2. [{建议2：谁做 + 做什么 + 何时完成}]
3. ...

---

## 8. Quality Gate Pass Status（质量门闸通过情况 / Quality Gate Pass Status）

| 门闸 | 阶段 | 状态 | 通过项数 | 总项数 | 日期 |
|------|------|------|---------|--------|------|
| 1.5 | Data Quality（数据质量） | [{PASS / CONDITIONAL / BLOCKED}] | [{N}] | 9 | [{YYYY-MM-DD}] |
| 2.5 | Plan Quality（计划质量） | [{PASS / CONDITIONAL / BLOCKED}] | [{N}] | 8 | [{YYYY-MM-DD}] |
| 3.5 | Results Quality（结果质量） | [{PASS / CONDITIONAL / BLOCKED}] | [{N}] | 9 | [{YYYY-MM-DD}] |
| 5.5 | Pre-review Integrity（审前完整性） | [{PASS / FAIL}] | - | - | [{YYYY-MM-DD}] |
| 5.8 | Final Integrity（最终完整性） | [{PASS / FAIL}] | - | - | [{YYYY-MM-DD}] |

---

## 9. Artifact Inventory（产物清单 / Artifact Inventory）

| Artifact ID | Stage | Type | Format | Path | Status |
|-------------|-------|------|--------|------|--------|
| [{raw_data}] | 1 | dataset | csv | [{data/raw/}] | [{consumed}] |
| [{cleaned_data}] | 1 | dataset | csv | [{data/cleaned/}] | [{consumed}] |
| [{cleaning_log}] | 1 | log | md | [{MSRA/cleaning_log.md}] | [{consumed}] |
| [{eda_report}] | 1 | report | md | [{MSRA/eda_report.md}] | [{consumed}] |
| [{sap}] | 2 | plan | md | [{MSRA/SAP.md}] | [{consumed}] |
| [{estimand_def}] | 2 | definition | md | [{MSRA/estimand_definition.md}] | [{consumed}] |
| [{analysis_code}] | 3 | code | R/py | [{MSRA/analysis.R}] | [{consumed}] |
| [{final_report}] | 4 | report | md/html | [{MSRA/reports/}] | [{consumed}] |
| [{handoff_bundle}] | 5.0 | contract | md | [{MSRA/msra_handoff_bundle.md}] | [{consumed}] |
| [{bibliography}] | 5.1 | bibliography | md | [{paper/bibliography.md}] | [{consumed}] |
| [{paper_draft}] | 5.2 | manuscript | md | [{paper/draft.md}] | [{completed}] |
| [{response_to_reviewers}] | 5.7 | response | md | [{paper/response_to_reviewers.md}] | [{completed}] |
| [{final_paper}] | 5.9 | manuscript | docx/pdf | [{paper/final/}] | [{completed}] |

---

## 10. Timeline（时间线 / Timeline）

- **[{YYYY-MM-DD HH:MM}]** Stage 1 开始 — [{简要描述}]
- **[{YYYY-MM-DD HH:MM}]** Stage 1.5 门闸通过
- **[{YYYY-MM-DD HH:MM}]** Stage 2 开始 — [{简要描述}]
- **[{YYYY-MM-DD HH:MM}]** Stage 2.5 门闸通过
- **[{YYYY-MM-DD HH:MM}]** Stage 3 开始 — [{简要描述}]
- **[{YYYY-MM-DD HH:MM}]** Stage 3.5 门闸通过
- **[{YYYY-MM-DD HH:MM}]** Stage 4 开始 — [{简要描述}]
- **[{YYYY-MM-DD HH:MM}]** Stage 4 Checkpoint — 用户选择 [{A/B}]
- **[{YYYY-MM-DD HH:MM}]** Stage 5.0 开始 — [{简要描述}]
- **[{YYYY-MM-DD HH:MM}]** Stage 5.2 初稿完成
- **[{YYYY-MM-DD HH:MM}]** Stage 5.5 完整性检查通过
- **[{YYYY-MM-DD HH:MM}]** Stage 5.6 评审完成
- **[{YYYY-MM-DD HH:MM}]** Stage 5.7 修订完成
- **[{YYYY-MM-DD HH:MM}]** Stage 5.8 最终完整性检查通过
- **[{YYYY-MM-DD HH:MM}]** Stage 5.9 定稿导出
- **[{YYYY-MM-DD HH:MM}]** Stage 6 过程总结开始

---

## 11. AI Self-Reflection Report（AI 自我反思报告 / AI Self-Reflection Report）

> 本章节由 AI 自行撰写，诚实记录自身行为模式。
> **注意**：本反思由可能在流水线中存在谄媚行为的同一 AI 生成，用户应带着此意识阅读。

### 11.1 Behavioral Summary（行为摘要）

[{一段话描述 AI 整体行为模式}]

### 11.2 Sycophancy Risk Assessment（谄媚风险评估）

| 指标 | 值 | 说明 |
|------|-----|------|
| DA Concession Rate（DA 让步率） | [{X/Y (Z%)}] | 让步数 / 总反驳数 |
| DA Consecutive Concessions（连续让步） | [{如有，列出}] | 违反无连续让步规则 |
| Checkpoints Skipped（跳过检查点） | [{X/Y}] | SLIM 或用户跳过 / 总检查点 |
| User Overrides（用户覆盖） | [{X}] | 用户否决 AI 建议次数 |
| Dialogue Health Alerts（对话健康警报） | [{X}] | 健康检查干预触发次数 |
| - Persistent Agreement（持续同意） | [{X}] | |
| - Conflict Avoidance（冲突回避） | [{X}] | |
| - Premature Convergence（过早收敛） | [{X}] | |
| Intent Mode Transitions（意图模式转换） | [{X}] | exploratory ↔ goal-oriented |
| Cross-Model Disagreements（跨模型分歧） | [{X}] | 如启用 |

**风险等级**：[{LOW / MEDIUM / HIGH}]
- LOW：让步率 <50%，0 健康警报
- MEDIUM：让步率 50-65%，或 1-2 警报
- HIGH：让步率 >65%，或 3+ 警报

[{如 HIGH，包含警告："AI may have been too accommodating in this run. Human review of DA findings and integrity results is strongly recommended."}]

### 11.3 Frame-Lock Incidents（框架锁定事件）

[{列出任何 [CROSS-MODEL-FINDING] 或框架锁定检测。如无，声明 "No frame-lock incidents detected — note this could mean either good coverage or undetected frame-lock."}]

### 11.4 Convergence Pattern（收敛模式）

[{在苏格拉底对话阶段，意图是否被正确检测？导师是否试图过早收敛？报告模式转换和任何过早收敛健康警报。}]

### 11.5 What AI Got Wrong（AI 错误列表）

[{坦诚列出 AI 在运行过程中的错误或不足 — 需要的纠正、检查点失败、发现的完整性问题。这不是失败报告，而是质量门闸正常工作的证据。}]

### 11.6 Failure Mode Audit Log（失败模式审计日志 v3.2）

> 对 `references/ai_research_failure_modes.md` 中的 7 种 AI 研究失败模式，报告最终状态。

| 失败模式 | 最终状态 | 历史 | 覆盖原因 |
|---------|---------|------|---------|
| Mode 1: Implementation bug passing AI self-review | [{CLEAR / OVERRIDDEN}] | [{如曾被标记，记录阶段和解决方式；无历史则填 "CLEAR (no flags)"}] | [{如 OVERRIDDEN，记录用户理由}] |
| Mode 2: Hallucinated citation | [{CLEAR / OVERRIDDEN}] | [{...}] | [{...}] |
| Mode 3: Hallucinated experimental result | [{CLEAR / OVERRIDDEN}] | [{...}] | [{...}] |
| Mode 4: Shortcut reliance | [{CLEAR / OVERRIDDEN}] | [{...}] | [{...}] |
| Mode 5: Implementation bug reframed as novel insight | [{CLEAR / OVERRIDDEN}] | [{...}] | [{...}] |
| Mode 6: Methodology fabrication | [{CLEAR / OVERRIDDEN}] | [{...}] | [{...}] |
| Mode 7: Frame-lock at early pipeline stage | [{CLEAR / OVERRIDDEN}] | [{...}] | [{...}] |

> 无历史的模式可简写为 `CLEAR (no flags)`。

### 11.7 Reading Probe Outcomes（阅读探针结果，如适用）

> 仅当 `ARS_SOCRATIC_READING_PROBE` 已启用时填写。如未启用，省略本节（不要写 "not applicable"）。
>
> **Pickup rule**（两种来源，任一即可）：
> - (a) 从 Research Plan Summary 的 `### Reading Probe Outcomes` 子节逐字复制（权威的人类可读记录）
> - (b) 搜索 `[READING-PROBE: status=..., paper=..., outcome=..., turn=...]` 标签（机器稳定锚点）
>
> 如两者都有，(a) 作为显示来源，(b) 作为最后一行附加。

[{逐字复制 Reading Probe Outcomes 子节内容}]

[{如有机器标签，附加最后一行：[READING-PROBE: status=..., paper=..., outcome=..., turn=...]}]

> **注意**：AI 未验证释义准确性。

---

## 12. Collaboration Quality Evaluation（协作质量评估 / Collaboration Quality Evaluation）

> 诚实、建设性地评估用户在人机协作中的表现。
> **原则**：诚实第一，不夸大，不奉承。如果用户只是按"继续"，如实反映。

### 12.1 Overall Score（总分）

```
+--------------------------------------------------+
|  Collaboration Quality Score: [{XX}]/100          |
+--------------------------------------------------+
```

[{一句话评价}]

### 12.2 Scoring Dimensions（评分维度）

| 维度 | 分数 | 说明 |
|------|------|------|
| Direction Setting（方向设定） | [{XX}] | 清晰度、时机、范围定义 |
| Intellectual Contribution（智力贡献） | [{XX}] | 洞察深度、原创性问题、概念挑战 |
| Quality Gatekeeping（质量把关） | [{XX}] | 视觉检查、格式要求、质量标准 |
| Iteration Discipline（迭代纪律） | [{XX}] | 及时纠正方向、愿意重跑流水线 |
| Delegation Efficiency（委托效率） | [{XX}] | 何时干预/何时放手、指令精度 |
| Meta-Learning（元学习） | [{XX}] | 将经验反馈到 skills、请求记录教训 |

**评分标准**：

| 分数范围 | 含义 |
|---------|------|
| 90-100 | 卓越 — 用户干预显著提升了论文的智力质量，超越 AI 独立产出 |
| 75-89 | 优秀 — 用户做出正确方向决策，有效利用流水线迭代能力 |
| 60-74 | 良好 — 用户完成必要决策，但错过了一些机会 |
| 40-59 | 基本 — 用户主要充当"继续"按钮，缺乏实质性干预 |
| 1-39 | 需改进 — 用户干预可能干扰了工作流或缺乏关键质量把关 |

### 12.3 What Worked Well（做得好的）

1. [{具体行为，含逐字引用}]
2. [{具体行为，含逐字引用}]
3. [{具体行为，含逐字引用}]

### 12.4 Missed Opportunities（错过的机会）

1. [{用户本可做但未做的事}]
2. [{用户本可做但未做的事}]

### 12.5 Recommendations for Next Time（下次建议）

1. [{具体、可操作的改进建议}]
2. [{具体、可操作的改进建议}]
3. [{具体、可操作的改进建议}]

### 12.6 Human vs AI Value-Add（人 vs AI 价值增量）

> 明确区分哪些质量来自用户干预（AI 无法独立实现）。

| 来源 | 贡献内容 |
|------|---------|
| 用户干预（Human） | [{列出用户独有的贡献}] |
| AI 独立产出（AI） | [{列出 AI 独立完成的贡献}] |
| 协作增效（Synergy） | [{列出人机协作产生的额外价值}] |

---

## 模板使用说明

### 使用时机
- Stage 5.9 (FINALIZE) 完成后，由 `academic-pipeline` 自动触发
- 也可由用户手动请求生成

### 填写方式
1. **自动填充**：Stage 1-5 的过程记录、门闸状态、产物清单、时间线可从 `passport.json` 和会话历史自动提取
2. **人工/AI 编写**：用户关键决策、经验教训、协作质量评估需从会话历史中提取
3. **AI 自评**：AI 自我反思报告由 AI 根据对话日志自行撰写

### 输出格式
- **Markdown**：`paper_creation_process.md`（中文）/ `paper_creation_process_en.md`（英文）
- **PDF**：`paper_creation_process_zh.pdf` / `paper_creation_process_en.pdf`
- **LaTeX**：`article` class, 12pt, A4, Times New Roman + Source Han Serif TC VF
- **编译**：tectonic

### 与其他文档的关系
- **上游**：`passport.json`（产物状态）、会话历史（决策记录）
- **下游**：无（Stage 6 为最终阶段）
- **参考**：`references/process_summary_protocol.md`（协议定义）、`references/ai_research_failure_modes.md`（7种失败模式）

### 评估原则
- **诚实第一**：不夸大，不奉承。如果用户只是按"继续"，如实反映
- **证据驱动**：每个评分都有具体行为或对话记录支撑
- **建设性**：每条批评必须包含可操作的改进建议
- **承认不确定性**：某些维度无法评估时（如中途入场跳过了研究阶段），标记为 N/A
- **双向反思**：也坦诚指出 Claude 在过程中的不足

### 长度指南
- 无发现的维度用一句话陈述空结果
- 仅在发现问题时展开
- 避免"一切正常"的冗长段落
