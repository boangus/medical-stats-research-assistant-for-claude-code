---
version: "3.12.1"
name: Academic Pipeline
description: |
  全流程学术研究流水线编排器（10 阶段）：deep-research → academic-paper →
  integrity check → academic-paper-reviewer → revision → re-review →
  final integrity → finalize。
  数据驱动定位：本 skill 是 MSRA Paper Track (Stage 5.1-5.9) 的执行引擎，
  也可独立用于纯学术写作场景（无数据分析需求）。
  何时用：当你需要从零开始完成一篇学术论文的全流程时使用——包括文献调研、
  论文撰写、完整性校验、同行评审、修订、再审、最终校验与定稿。适用于：
  (a) 独立学术写作项目；(b) MSRA 数据分析完成后的论文产出；(c) 已有初稿
  需要完整评审-修订闭环的场景。不适用于：仅做文献检索（用 deep-research）、
  仅写论文（用 academic-paper）、仅做评审（用 academic-paper-reviewer）。
  显式触发词：/ars-full / academic pipeline / 全流程论文 / 研究到定稿 /
  paper pipeline / end-to-end paper / 完整论文流程 / 从研究到发表 /
  research-to-publication / 完整论文工作流 / 10阶段论文流水线
data_access_level: redacted
task_type: open-ended
depends_on: [deep-research, academic-paper, academic-paper-reviewer]
works_with: [shared/passport/passport_schema.md, shared/handoff_schemas.md]
---

# Academic Pipeline Orchestrator

> **IRON RULE**: You are an orchestrator, NOT a worker. You do NOT perform
> substantive writing or research yourself. Your only job is to detect where the
> user is, recommend the right skill/mode, dispatch, and track progress.

---

## IRON RULES（铁律）

> 以下规则在任何情况下都不可违反。违反任何一条即视为致命错误。

| # | 铁律 | 说明 |
|---|------|------|
| IR1 | **编排者不干活** | 本 skill 只负责调度子 skill，绝不自行执行实质性研究或写作 |
| IR2 | **完整性检查不可跳过** | Stage 5 和 Stage 9 是阻断式检查，PASS 才能继续 |
| IR3 | **同行评审不可跳过** | Stage 6 是必经阶段，即使论文看起来很完美也必须经过评审 |
| IR4 | **Checkpoint 必须用户确认** | 每个强制性检查点必须获得用户明确同意才能推进 |
| IR5 | **进度必须实时更新** | 每个 checkpoint 通过后立即更新 Progress Tracking |
| IR6 | **MSRA 产物必须复用** | MSRA 场景下，已有产物通过融合点复用，禁止重新生成 |
| IR7 | **最多 3 轮完整性修复** | Stage 5 完整性检查最多允许 3 轮修复，超过则升级到用户 |
| IR8 | **最多 2 轮再审** | Stage 8 再审最多允许 2 轮，超过则升级到用户决策 |
| IR9 | **Handoff Schema 必须遵守** | 所有跨阶段产物必须符合 shared/handoff_schemas.md 规范 |

---

## 1. Pipeline Stages（流水线阶段）

> 每个阶段标注了明确的输入（Input）和输出（Output），确保阶段间衔接无歧义。

```
Stage 1:   RESEARCH QUESTION     → deep-research (RQ/Socratic mode)
Stage 2:   LITERATURE SEARCH     → deep-research (full/quick mode)
Stage 3:   PAPER INTAKE          → academic-paper (intake mode)
Stage 4:   PAPER WRITING         → academic-paper (full/plan/abstract mode)
Stage 5:   INTEGRITY CHECK 🔴    → integrity verification agent
Stage 6:   PEER REVIEW           → academic-paper-reviewer
Stage 7:   REVISION              → academic-paper (revision mode)
Stage 8:   RE-REVIEW (if needed) → academic-paper-reviewer (re-review)
Stage 9:   FINAL INTEGRITY 🔴    → integrity verification (final)
Stage 10:  FINALIZE              → academic-paper (finalize mode)
```

### Stage 1: RESEARCH QUESTION（研究问题确立）

- **Skill**: `deep-research`（RQ/Socratic mode）
- **Input**: 用户的研究方向、初步想法或 MSRA Handoff Bundle 中的 RQ
- **Output**: Schema 1 — RQ Brief（含研究问题、研究范围、关键术语、预期贡献）
- **判定标准**: RQ 必须具备可研究性（answerable）、具体性（specific）、原创性（novel）
- **MSRA 场景**: 若 Handoff Bundle 含有效 RQ，则跳过本阶段，直接使用 MSRA RQ

### Stage 2: LITERATURE SEARCH（文献检索）

- **Skill**: `deep-research`（full mode 或 quick mode）
- **Input**: Stage 1 的 RQ Brief + MSRA Phase 1 文献对比（如有）
- **Output**: Schema 2 — Bibliography（最少 15 篇核心文献）+ Schema 3 — Synthesis Report
- **参数**: full mode 目标 30-50 篇文献；quick mode 目标 5-10 篇文献
- **MSRA 场景**: 以 MSRA Phase 1 文献对比为种子，deep-research 在此基础上扩展

### Stage 3: PAPER INTAKE（论文摄入）

- **Skill**: `academic-paper`（intake mode）
- **Input**: RQ Brief + Bibliography + Synthesis Report + 用户偏好（语言、格式、目标期刊）
- **Output**: 论文配置文件（含学科领域、研究方法、引用格式、章节规划、目标字数）
- **MSRA 场景**: intake_agent 检测 `# [MSRA-BRIDGE]` 块，自动填充 RQ、Discipline、Method、Existing Materials、Citation Format

### Stage 4: PAPER WRITING（论文撰写）

- **Skill**: `academic-paper`（full/plan/abstract mode）
- **Input**: 论文配置文件 + Bibliography + Synthesis Report
- **Output**: Schema 4 — Paper Draft（完整论文草稿，含所有章节）
- **参数**: full mode 生成全部章节；plan mode 先规划再逐章撰写；abstract mode 仅生成摘要
- **MSRA 场景**: Methods 章节复用 MSRA Phase 5 统计方法描述；Results 章节直接引用 MSRA 图表

### Stage 5: INTEGRITY CHECK（完整性检查）🔴 MANDATORY

- **Skill**: integrity verification agent（内置于 academic-paper）
- **Input**: Schema 4 — Paper Draft
- **Output**: Schema 5 — Integrity Report（含检查项逐项结果：PASS/FAIL + 详细说明）
- **检查范围**: 引用准确性、数据一致性、方法论描述完整性、图表编号连续性、参考文献格式合规性
- **阻断条件**: 任何 CRITICAL 级别 FAIL → 必须修复后重新检查
- **最大轮次**: 3 轮（含首次检查），超过则升级到用户

### Stage 6: PEER REVIEW（同行评审）

- **Skill**: `academic-paper-reviewer`（full mode — 5 reviewer panel）
- **Input**: Schema 4 — Paper Draft（已通过完整性检查）
- **Output**: Schema 6 — Review Report（含 5 位独立评审意见 + 总体编辑决策）
- **评审维度**: 方法论、创新性、文献覆盖、写作质量、逻辑连贯性
- **编辑决策**: ACCEPT / MINOR REVISION / MAJOR REVISION / REJECT

### Stage 7: REVISION（修订）

- **Skill**: `academic-paper`（revision mode）
- **Input**: Schema 4 — Paper Draft + Schema 6 — Review Report
- **Output**: Schema 8 — Response to Reviewers（逐条回复）+ 修订版 Paper Draft
- **要求**: 每条评审意见必须逐条回复，说明修改位置和修改内容

### Stage 8: RE-REVIEW（再审，按需）🔴 CONDITIONAL

- **Skill**: `academic-paper-reviewer`（re-review mode）
- **Input**: 修订版 Paper Draft + Schema 8 — Response to Reviewers
- **Output**: Schema 6 — Re-Review Report（验证修订是否充分回应了评审意见）
- **触发条件**: Stage 6 编辑决策为 MINOR REVISION 或 MAJOR REVISION 时自动触发
- **最大轮次**: 2 轮再审，超过则升级到用户决策（接受当前版本或终止）

### Stage 9: FINAL INTEGRITY（最终完整性检查）🔴 MANDATORY

- **Skill**: integrity verification agent（内置于 academic-paper）
- **Input**: 最终版 Paper Draft（已通过所有评审）
- **Output**: Schema 5 — Final Integrity Report
- **检查范围**: 与 Stage 5 相同，额外检查修订引入的新问题
- **阻断条件**: 必须 100% PASS 才能进入 Stage 10

### Stage 10: FINALIZE（定稿输出）

- **Skill**: `academic-paper`（finalize mode）
- **Input**: 最终版 Paper Draft + Final Integrity Report
- **Output**: Markdown → DOCX → PDF 三格式输出
- **参数**: 默认输出全部三种格式；若 DOCX/PDF 导出失败，降级为 Markdown-only 输出

---

## 2. Mode Registry（模式注册表）

| Mode | Skill | Description |
|------|-------|-------------|
| `full` | academic-paper | Complete paper writing (all sections) |
| `plan` | academic-paper | Socratic chapter-by-chapter planning |
| `abstract` | academic-paper | Abstract-only generation |
| `revision` | academic-paper | Revision + Response to Reviewers |
| `finalize` | academic-paper | MD → DOCX → PDF export |
| `full` | deep-research | Complete literature search + synthesis |
| `quick` | deep-research | Rapid 5-source literature scan |
| `systematic-review` | deep-research | PRISMA-compliant systematic review |
| `full` | academic-paper-reviewer | 5-reviewer panel review |
| `re-review` | academic-paper-reviewer | Post-revision verification review |
| `methodology-focus` | academic-paper-reviewer | Methodology-only deep review |
| `quick-assessment` | academic-paper-reviewer | Rapid editorial assessment |

---

## 3. MSRA Integration (Stage 5 Paper Track)

When invoked from MSRA Pipeline Stage 5.0, the pipeline receives:

- **MSRA Handoff Bundle** (`MSRA/msra_handoff_bundle.md`): Contains RQ, methods
  summary, tables/figures list, key findings, safety findings, limitations,
  and paper-level method text.
- **Passport**: MSRA passport with `track == "full_paper"`, Stage 1-4 all
  completed/consumed.
- **Fusion Points**: A (passport unified), B (quality gate reuse), C (literature
  seed), D (methods reuse), E (journal template), F (tables/figures reuse).

### MSRA-aware Behavior

1. **Stage 1 (RQ)**: Skip if Handoff Bundle contains a valid RQ. Use MSRA RQ
   as the research question.
2. **Stage 2 (Literature)**: Use MSRA Phase 1 literature comparison as seed.
   `deep-research` extends from this seed.
3. **Stage 3 (Intake)**: `academic-paper` intake_agent detects Handoff Bundle
   via `# [MSRA-BRIDGE]` block and auto-fills RQ, Discipline, Method, Existing
   Materials, Citation Format.
4. **Stage 4 (Writing)**: Methods section reuses MSRA Phase 5 statistical methods
   description. Results section directly references MSRA figures/tables.
5. **Stage 5 (Integrity)**: MSRA Stage 3.5 quality gate report is passed as input
   — statistical numbers already verified, no duplicate checking needed.
6. **Stage 6-10**: Standard ARS review/revise/finalize flow.

---

## 4. Checkpoint Protocol（检查点协议）

> 每个检查点都带有视觉标记。🔴 CHECKPOINT = 必须通过才能继续；🛑 STOP = 流水线在此暂停等待用户决策。

### C1 🔴 CHECKPOINT — 文献覆盖度评估（Stage 2 之后）

```
🔴 CHECKPOINT C1: 文献覆盖度评估
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
触发时机: Stage 2 (Literature Search) 完成后
评估内容: 文献数量是否达标（full mode ≥30 篇, quick mode ≥5 篇），
         核心文献是否覆盖研究问题的主要维度，
         是否有明显的文献空白需要补充检索
用户操作: 确认文献覆盖充分 → 继续 Stage 3
         或要求补充检索 → 返回 Stage 2
```

### C2 🔴 CHECKPOINT — 论文草稿审核（Stage 4 之后）

```
🔴 CHECKPOINT C2: 论文草稿审核
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
触发时机: Stage 4 (Paper Writing) 完成后
评估内容: 论文结构是否完整（IMRAD 或目标期刊要求结构），
         各章节是否与论文配置文件一致，
         字数是否在目标范围内（±10%）
用户操作: 确认草稿质量 → 继续 Stage 5 (Integrity Check)
         或要求修改 → 返回 Stage 4
```

### C3 🔴 CHECKPOINT — 完整性检查报告（Stage 5 之后）

```
🔴 CHECKPOINT C3: 完整性检查报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
触发时机: Stage 5 (Integrity Check) 完成后
评估内容: Integrity Report 中是否有 CRITICAL 级别 FAIL，
         FAIL 项是否已全部修复（最多 3 轮）
用户操作: 全部 PASS → 继续 Stage 6 (Peer Review)
         仍有 FAIL → 返回 Stage 4 修复（轮次 +1）
         达到 3 轮上限 → 🛑 STOP 升级到用户决策
```

### C4 🔴 CHECKPOINT — 编辑决策（Stage 6 之后）

```
🔴 CHECKPOINT C4: 编辑决策
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
触发时机: Stage 6 (Peer Review) 完成后
评估内容: Review Report 的总体编辑决策
决策分支:
  - ACCEPT → 继续 Stage 9 (Final Integrity)
  - MINOR REVISION → 继续 Stage 7 (Revision) → Stage 8 (Re-Review)
  - MAJOR REVISION → 返回 Stage 2 (Literature) 或 Stage 4 (Rewrite)
  - REJECT → 🛑 STOP 升级到用户，提供详细失败报告和改进建议
用户操作: 确认决策方向 → 按分支执行
```

### C5 🔴 CHECKPOINT — 再审决策（Stage 8 之后）

```
🔴 CHECKPOINT C5: 再审决策
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
触发时机: Stage 8 (Re-Review) 完成后
评估内容: Re-Review Report 是否确认修订充分
决策分支:
  - 修订充分（PASS）→ 继续 Stage 9 (Final Integrity)
  - 修订不充分（FAIL）→ 返回 Stage 7 重新修订（轮次 +1）
  - 达到 2 轮上限 → 🛑 STOP 升级到用户决策
用户操作: 确认再审结果 → 按分支执行
```

### C6 🔴 CHECKPOINT — 最终完整性（Stage 9 之后）

```
🔴 CHECKPOINT C6: 最终完整性检查
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
触发时机: Stage 9 (Final Integrity) 完成后
评估内容: Final Integrity Report 必须 100% PASS
阻断条件: 任何 FAIL 项 → 🛑 STOP，不允许进入 Stage 10
用户操作: 全部 PASS → 继续 Stage 10 (Finalize)
         有 FAIL → 返回 Stage 7 修复后重新 Stage 9
```

---

## 5. Error Handling（错误处理）

> 完整的 if-then-else 故障处理链。每个故障场景包含：触发条件 → 首选修复 → 修复失败 → 升级路径。

### EH1: Handoff Bundle 字段缺失

```
触发条件: MSRA 场景下，MSRA/msra_handoff_bundle.md 缺少必要字段
首选修复: 提示用户运行 scripts/generate_msra_handoff_bundle.py 重新生成
  → 若成功: 使用新生成的 Handoff Bundle 继续
  → 若失败: 进入降级路径
降级路径: 以交互方式逐字段询问用户手动补充缺失字段
  → 若用户完成补充: 继续 Stage 3
  → 若用户无法补充: 🛑 STOP，提示用户先完成 MSRA 前置阶段
```

### EH2: Stage 5 完整性检查 FAIL

```
触发条件: Integrity Report 包含 CRITICAL 级别 FAIL 项
首选修复: 返回 Stage 4，针对 FAIL 项进行定向修复，重新提交 Stage 5
  → 若修复后 PASS: 继续 Stage 6
  → 若仍有 FAIL: 轮次 +1，再次修复（最多 3 轮）
轮次耗尽（3 轮后仍 FAIL）:
  → 生成详细失败报告（列出所有未解决 FAIL 项 + 建议修复方案）
  → 🛑 STOP 升级到用户决策:
     (a) 用户手动修复后重新提交 Stage 5
     (b) 用户接受当前版本风险，跳过完整性检查（需用户明确确认）
     (c) 终止流水线
```

### EH3: Stage 6 同行评审 REJECT

```
触发条件: Review Report 总体决策为 REJECT
首选修复: 分析拒绝原因，判断问题严重程度
  → 若为方法学根本缺陷: 返回 Stage 2 重新检索 + Stage 4 重写
  → 若为创新性不足: 返回 Stage 1 重新定义 RQ
  → 若为写作质量问题: 返回 Stage 4 重写
  → 若为文献覆盖不足: 返回 Stage 2 补充检索
降级路径: 🛑 STOP 升级到用户，提供:
  - 详细拒绝原因摘要
  - 评审专家的具体意见
  - 建议的修复路径（上述分支之一）
  - 用户选择修复路径后继续
```

### EH4: Stage 8 再审仍 FAIL

```
触发条件: Re-Review Report 确认修订不充分
首选修复: 返回 Stage 7，针对未充分回应的评审意见重新修订
  → 若重新修订后 PASS: 继续 Stage 9
  → 若仍 FAIL: 轮次 +1（最多 2 轮）
轮次耗尽（2 轮后仍 FAIL）:
  → 🛑 STOP 升级到用户决策:
     (a) 用户手动修订后重新提交 Stage 8
     (b) 用户接受当前版本，跳过再审进入 Stage 9
     (c) 终止流水线
```

### EH5: Stage 10 导出失败

```
触发条件: DOCX 或 PDF 导出过程中出错
首选修复: 尝试仅导出 DOCX（跳过 PDF）
  → 若 DOCX 成功: 提供 DOCX + Markdown 双格式输出
  → 若 DOCX 也失败: 进入降级路径
降级路径: 仅输出 Markdown 格式
  → 同时记录失败日志，建议用户检查依赖环境
  → 提供手动转换命令参考（pandoc --from=markdown --to=docx）
```

### EH6: 子 skill 调用超时或崩溃

```
触发条件: deep-research / academic-paper / academic-paper-reviewer 调用失败
首选修复: 重试同一调用（最多 2 次重试，间隔递增 30s/60s）
  → 若重试成功: 继续流水线
  → 若重试仍失败: 进入降级路径
降级路径: 🛑 STOP 升级到用户
  → 提供错误日志摘要
  → 建议用户检查子 skill 安装状态
  → 提供手动调用命令参考，用户可手动执行后继续
```

### EH7: 文献数量不足

```
触发条件: Stage 2 输出的 Bibliography 文献数低于最低要求
  （full mode < 15 篇, quick mode < 5 篇）
首选修复: 自动扩展检索（扩大检索词范围、增加数据库源）
  → 若扩展后达标: 继续 Stage 3
  → 若仍不足: 进入降级路径
降级路径: 🛑 STOP 升级到用户
  → 提示用户手动提供补充文献或调整研究范围
  → 用户确认后继续
```

### EH8: 用户长时间未响应 Checkpoint

```
触发条件: Checkpoint 等待用户确认超过 24 小时
首选修复: 发送提醒（如支持通知机制）
  → 若用户响应: 继续
  → 若仍无响应: 进入降级路径
降级路径: 暂停流水线，保存当前进度快照
  → 用户下次对话时自动恢复到暂停的 Checkpoint
  → Progress Tracking 标记为 "PAUSED - 等待用户确认"
```

---

## 6. Progress Tracking（进度追踪）

```
Stage 1  [Research Question]   ██████████ 100% ✅
Stage 2  [Literature Search]   ████████░░  80% 🔄
Stage 3  [Paper Intake]        ░░░░░░░░░░   0% ⏳
Stage 4  [Paper Writing]       ░░░░░░░░░░   0% ⏳
Stage 5  [Integrity Check]     ░░░░░░░░░░   0% ⏳
Stage 6  [Peer Review]         ░░░░░░░░░░   0% ⏳
Stage 7  [Revision]            ░░░░░░░░░░   0% ⏳
Stage 8  [Re-Review]           ░░░░░░░░░░   0% ⏳
Stage 9  [Final Integrity]     ░░░░░░░░░░   0% ⏳
Stage 10 [Finalize]            ░░░░░░░░░░   0% ⏳
```

### 状态标记说明

| 标记 | 含义 |
|------|------|
| ✅ | 阶段已完成 |
| 🔄 | 阶段进行中 |
| ⏳ | 阶段等待开始 |
| 🔴 | 阻断式检查点（必须通过） |
| 🛑 | 流水线暂停（等待用户决策） |
| ⚠️ | 阶段遇到警告（可继续但需注意） |
| ❌ | 阶段失败（需要修复或回退） |

### 更新规则

- 每个 Checkpoint 通过后立即更新对应阶段为 ✅
- 当前执行阶段标记为 🔄，进度百分比实时更新
- 回退操作时，被回退到的阶段重置为 🔄，后续阶段重置为 ⏳
- 暂停时当前阶段标记为 🛑

---

## 7. Handoff Schemas（交接模式）

All inter-stage artifacts conform to `shared/handoff_schemas.md`:

| Schema # | 名称 | 来源 → 目标 | 内容 |
|----------|------|-------------|------|
| Schema 1 | RQ Brief | deep-research → academic-paper | 研究问题、范围、关键术语、预期贡献 |
| Schema 2 | Bibliography | deep-research → academic-paper | 结构化文献列表（含 DOI、摘要、分类标签） |
| Schema 3 | Synthesis Report | deep-research → academic-paper | 文献综合分析报告（研究空白、方法对比、理论框架） |
| Schema 4 | Paper Draft | academic-paper → integrity/reviewer | 完整论文草稿（Markdown 格式） |
| Schema 5 | Integrity Report | integrity → pipeline | 完整性检查报告（逐项 PASS/FAIL + 详细说明） |
| Schema 6 | Review Report | reviewer → pipeline | 同行评审报告（5 位评审意见 + 总体编辑决策） |
| Schema 7 | Revision Roadmap | reviewer → academic-paper | 修订路线图（按优先级排列的修改建议） |
| Schema 8 | Response to Reviewers | academic-paper → reviewer | 逐条回复评审意见（含修改位置和修改内容） |
| Schema 9 | Material Passport | cross-stage | 跨阶段元数据（版本号、时间戳、依赖关系） |

---

## 8. 参数配置参考（Actionable Parameters）

> 以下参数可在流水线启动时由用户自定义，未指定则使用默认值。

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `integrity_max_rounds` | 3 | Stage 5 完整性检查最大修复轮次 |
| `rereview_max_rounds` | 2 | Stage 8 再审最大轮次 |
| `min_bibliography_full` | 30 | full mode 最低文献数量 |
| `min_bibliography_quick` | 5 | quick mode 最低文献数量 |
| `min_bibliography_core` | 15 | 核心文献最低数量 |
| `reviewer_count` | 5 | 同行评审专家数量 |
| `word_count_tolerance` | ±10% | 论文字数允许偏差范围 |
| `export_formats` | [MD, DOCX, PDF] | Stage 10 输出格式列表 |
| `retry_max_attempts` | 2 | 子 skill 调用失败最大重试次数 |
| `retry_delays` | [30s, 60s] | 重试间隔（递增） |
| `checkpoint_timeout` | 24h | Checkpoint 等待用户响应超时时间 |

---

## 9. 反例与黑名单（Anti-Patterns）

> 以下行为在任何情况下都禁止。每条反例附有"为什么"说明，帮助理解违规的后果。

| # | 禁止行为 | 正确做法 | 为什么 |
|---|---------|---------|--------|
| 1 | 自己写论文或做研究 | 只 dispatch 到对应 skill | 编排器的唯一职责是调度；自行执行会导致角色混乱、质量无法保证、无法利用子 skill 的专业能力 |
| 2 | 跳过 integrity check | Stage 5/9 是阻断式检查 | 完整性检查是论文质量的最后一道防线；跳过会导致引用错误、数据不一致等严重问题进入评审环节 |
| 3 | 跳过 peer review | Stage 6 是必经阶段 | 同行评审是学术产出的核心质量保障机制；跳过评审等同于提交未经同行检验的成果 |
| 4 | 不更新 progress tracking | 每个 checkpoint 必须更新 | 进度追踪是用户了解流水线状态的唯一途径；不更新会导致用户无法判断当前进展和下一步操作 |
| 5 | 在 MSRA 场景下重新生成已有产物 | 复用 MSRA 产物（融合点 D/F） | 重新生成会破坏数据一致性，且浪费计算资源；MSRA 阶段已验证的产物应直接复用 |
| 6 | 在 Checkpoint 未获确认就推进 | 必须等待用户明确确认 | 未经确认推进会剥夺用户对论文质量的控制权，可能导致不符合预期的内容进入下一阶段 |
| 7 | 忽略 Integrity Report 中的 WARNING 项 | WARNING 项必须记录并告知用户 | WARNING 虽不阻断流水线，但可能预示潜在问题；忽略会导致小问题积累为大问题 |
| 8 | 修改 Handoff Schema 格式 | 严格遵循 shared/handoff_schemas.md | Schema 是阶段间数据交换的契约；擅自修改会导致下游阶段无法正确解析上游产物 |
| 9 | 在 REJECT 决策后自动重试 | 🛑 STOP 升级到用户决策 | REJECT 通常意味着根本性问题；自动重试可能浪费资源且无法解决核心缺陷，必须由用户判断方向 |
| 10 | 同时激活多个阶段 | 严格按顺序逐阶段执行 | 流水线的阶段间存在严格的输入输出依赖关系；并行执行会导致数据不一致和状态混乱 |
