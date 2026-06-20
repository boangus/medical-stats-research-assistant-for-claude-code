# 设计文档：MSRA × ARS 整合（数据统计 → 学术写作全流水线）

- **日期**: 2026-06-17
- **版本**: v4 (统一 Pipeline 架构，融合项目，数据驱动定位)
- **状态**: 待审批
- **作者**: boangus（经 brainstorming 流程）
- **关联上游**: [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) v3.12.1 (commit `88fc003`, 2026-06-17)
- **变更记录**: v1→v2 统一 Pipeline; v2→v3 废除协议隔离; v3→v4 数据驱动定位强化

---

## 1. 目标

将 ARS（Academic Research Skills）的"研究→写作→评审→修订→定稿"能力融入 MSRA，
形成**一个统一项目**——从原始数据出发，用户在统计报告完成后选择是结束
还是继续写可投稿论文，全程无需切换 skill 或手工搬运文件。

> **⚠️ 核心定位**：本插件仅在**需要数据处理的项目**中启用。用户若只需纯学术写作
> （无数据分析需求），应直接使用 ARS 的 academic-paper / academic-pipeline 等
> skill，**不经过本插件**。本插件的 Paper Track 是 MSRA 统计产物的下游消费者，
> 没有统计报告就进入不了论文轨道。

### 成功标准

1. **统一 Pipeline 端到端跑通**：用户从 `/msra` 一路走到最终论文，
   中间在 Stage 4 有分叉节点，不需要手动调用第二个 skill。
2. **分叉节点生效**：Stage 4 完成后用户可选择 [A] 统计报告结束 或
   [B] 继续 Paper Track；选择 [B] 后 MSRA 产物自动传递给论文写作阶段。
3. **ARS 4 个 skill 可运行**：academic-paper / academic-paper-reviewer /
   academic-pipeline / deep-research 引用的 `shared/` 依赖全部就位。
4. **临床报告规范贯通**：Paper Track 继承 MSRA 的 CONSORT/STROBE/STARD
   等 16 个报告检查清单（ARS 原生不具备此能力）。
5. **MSRA Core 零侵入**：Stage 1-4 的核心逻辑不变，仅 Stage 4 做精简。
6. **数据驱动定位明确**：本插件仅在需要数据处理的项目中启用，纯写作场景不经本插件。

### 适用范围（核心定位）

> **⚠️ 核心定位**：本插件仅在**需要数据处理的项目**中启用。用户若只需纯学术写作
> （无数据分析需求），应直接使用 ARS 的 academic-paper / academic-pipeline 等
> skill，**不经过本插件**。本插件的 Paper Track 是 MSRA 统计产物的下游消费者，
> 没有统计报告就进入不了论文轨道。

| 场景 | 是否使用本插件 | 说明 |
|---|---|---|
| 有原始数据，需要统计分析 + 报告 + 可能写论文 | ✅ **使用** | 本插件的核心场景：Stage 1→4（必须）→ 5-6（可选） |
| 有分析结果，需要统计报告 + 可能写论文 | ✅ **使用** | 从 Stage 4 中间切入，仍走 MSRA 报告流程 |
| 只需要统计报告，不写论文 | ✅ **使用** | 跑到 Stage 4 checkpoint 选 [A] 结束 |
| 只需要写论文，不需要数据分析 | ❌ **不用** | 直接用 ARS 的 `academic-paper` / `academic-pipeline` |
| 只需要文献检索 | ❌ **不用** | 直接用 ARS 的 `deep-research` |
| 只需要论文评审 | ❌ **不用** | 直接用 ARS 的 `academic-paper-reviewer` |

**判断规则**：有数据要处理 → 用本插件；无数据纯写作 → 用 ARS 原生 skill。

### 非目标（YAGNI）

- 不在 MSRA 内实现文献检索（那是 ARS `deep-research` 的职责）。
- 不做 ARS 的中文化——ARS 保持英文，桥接时中英混排由 academic-paper 的语言设置处理。
- 不做自动升级机制（上游 ARS 更新时手动合并，记录版本号）。
- 不保留独立的 `msra-to-ars` bridge skill（逻辑已内化进统一 Pipeline）。
- 不做协议隔离——融合后属于一个新项目，ARS 依赖直接合并进项目 `shared/`。
- **不替代 ARS 的通用写作能力**——纯写作场景直接用 ARS 原生 skill，不经过本插件。

---

## 2. 关键决策（已与用户确认）

| 维度 | 决策 | 理由 |
|---|---|---|
| 整合架构 | **统一 Pipeline**（废除 bridge） | 用户从 Stage 1 一路走到论文，中途分叉比切换 skill 更自然 |
| 分叉方式 | **Stage 4 末尾决策节点** | 统计报告完成后自然询问"继续写论文？" |
| ARS 报告规范 | **引入 MSRA 临床规范** | ARS 原生无 CONSORT/STROBE，这是 MSRA 独有资产 |
| shared/ 获取 | **直接合并进项目 shared/** | 融合后是一个新项目，不需要物理隔离 |
| intake 识别 | **ARS intake 加 MSRA 分支** | 字段更准确（携带 figures/tables），仅改 1 个 agent 文件 |
| MSRA Stage 4 精简 | **报告规范+期刊模板移到 Paper Track** | CONSORT 全文合规检查是发表级需求，统计报告阶段不需要 |
| Passport | **统一扩展** | 一个 passport 追踪从 Stage 1 到 final paper 的全部产物 |

---

## 3. 现状分析（为什么需要做这些事）

### 3.1 ARS skill 本地已有但"半成品"

`skills/` 下已有 4 个 ARS skill（git 未跟踪 `??` 状态），内部结构齐全：

| skill | 本地版本 | 上游 v3.12.1 |
|---|---|---|
| academic-paper | v3.2.0 | ✅ |
| academic-paper-reviewer | v1.10.0 | ✅ |
| academic-pipeline | v3.12.1 | ✅ |
| deep-research | v2.10.0 | ✅ |

### 3.2 缺口：约 54 个 ARS `shared/` 文件 + `.claude/CLAUDE.md` + commands

这 4 个 skill 在运行时引用 `shared/` 下的依赖文件，而 MSRA 仓库的 `shared/` 是医学统计
专用目录，**不含任何 ARS 依赖**。引用扫描发现有约 40 处 `shared/...` 引用（去重后约 30 个
不同文件，上游实际提供 54 个 shared 文件）全部指向本地不存在的文件，典型如：

- `shared/handoff_schemas.md`（跨 skill 数据契约，9 个 schema）
- `shared/collaboration_depth_rubric.md`
- `shared/references/intent_clarification_protocol.md`
- `shared/compliance_checkpoint_protocol.md`
- `shared/contracts/` 下 7 个子目录（passport/ submission/ writer/ reviewer/ patch/ audit/ evaluator/）
- `.claude/CLAUDE.md`（Routing Discipline v3.9.2 的所在地）

**解决方案**：将上游 ARS 的 54 个 shared 文件、`.claude/CLAUDE.md`、`commands/`
直接合并进项目。ARS skill 中的 `shared/` 引用无需修改路径，自然指向合并后的 `shared/`。
对于命名冲突的文件（如 MSRA 和 ARS 都有的同名文件），在合并时以命名空间子目录区分
（如 `shared/ars/` 存放 ARS 特有的文件，AR skill 中的引用路径做一次性替换）。

**结论**：不补齐这些依赖，ARS 端到端跑不起来。

### 3.3 ARS 完全缺乏临床报告规范能力

ARS 的 compliance 框架围绕 AI 研究透明度设计（PRISMA-trAIce + RAISE），
**没有任何 CONSORT/STROBE/STARD/PRISMA 检查清单**。具体发现：

- `resources/academic-paper/references/` 下有 `academic_writing_style.md`、
  `writing_quality_check.md` 等写作规范，但无临床报告规范。
- `academic-pipeline` Stage 2.5 的 integrity check 验证引用/数据/声明，
  不验证临床报告合规。
- `intake_agent.md` Step 12 的 `clinical` Domain Evidence Profile 是
  **reserved 空占位**，实际 fallback 到 `unknown_user_defined`。

**对比 MSRA**：`shared/reporting-guidelines/` 有 16 个文件，含：
- CONSORT 2025（30 条目，含 PPI/AI disclosure 等 7 条新增）
- STROBE 2007 + extensions
- PRISMA 2020 + NMA
- STARD 2015（含 TRIPOD+AI 交叉引用）
- TRIPOD+AI 2024 / TRIPOD-LLM 2024
- TRUE-AIM 2025（AHA AI 模型 QA）
- REMARK / CARE / ARRIVE / SPIRIT / CHEERS

**结论**：融合不仅是流水线串联，更是让 Paper Track 继承 MSRA 的临床报告规范
专业能力——独立 bridge 方案做不到这一点。

### 3.4 MSRA 有现成的产物追踪机制可复用

MSRA 的 `shared/passport/passport_schema.md` 定义了 Material Passport，
记录每个 stage 的产物路径、hash、status、`study_type`。这是统一 Pipeline 的
**权威数据源**——扩展后可追踪 ARS 阶段的产物。

### 3.5 MSRA Report 的 Quarto 模板可双轨复用

`shared/report-assembler/report_template.qmd` 已定义完整 IMRaD 结构
（Study Overview → Methods → Results → Discussion → Supplementary），
可作为论文初稿的结构基础。

---

## 4. 架构

### 4.1 统一 Pipeline 总览

```
═══════════════════════════════════════════════════════════════
  UNIFIED PIPELINE: 原始数据 → 统计报告 → (可选) 可投稿论文
  ⚠️ 入口前提: 用户有数据需要处理。纯写作场景请直接使用 ARS。
═══════════════════════════════════════════════════════════════

┌─── MSRA Core（统计分析）──────────────────────────────┐
│                                                          │
│  Stage 1:   DATA PREP            [/msra-data]            │
│  Stage 1.5: DATA QUALITY GATE     🔴                   │
│  Stage 2:   ANALYSIS PLAN        [/msra-plan]            │
│  Stage 2.5: SAP QUALITY GATE      🔴                   │
│  Stage 3:   ANALYSIS EXEC         [/msra-exec]           │
│  Stage 3.5: RESULTS QUALITY GATE  🔴                   │
│                                                          │
│  Stage 4:   STATISTICAL REPORT   [/msra-report]         │
│    ├ Phase 1: 结果解读                                   │
│    ├ Phase 3: 表格生成 + 导出                            │
│    ├ Phase 4: 图表生成                                   │
│    ├ Phase 5: 方法学描述                                 │
│    └ Phase 6: 统计质量检查（精简版）                      │
│          保留: statcheck_rules / anti-patterns          │
│          移除: CONSORT/STROBE 全文合规 + 期刊模板选择   │
│                                                          │
│  ★ STAGE 4 CHECKPOINT (MANDATORY)                       │
│  ┌──────────────────────────────────────────┐           │
│  │  统计报告已完成:                          │           │
│  │  - final_report.md + final_report.html    │           │
│  │  - figures/*.png + tables/*.docx          │           │
│  │                                          │           │
│  │  选择下一步:                              │           │
│  │  [A] 统计报告完成，结束                   │           │
│  │  [B] 继续写论文 → Paper Track            │           │
│  └──────────────────────────────────────────┘           │
└────────────────────────────────────────────────────────┘
                        │
                [A] → ════════════════════ 结束
                        │
                [B] ↓
          ┌─────────────────────────────────┐
          │ 守卫检查: Stage 1-4 产物是否齐全？│
          │   final_report + figures + tables │
          │   → 无数据则拒绝，提示用 ARS     │
          └────────────────┬────────────────┘
                           ↓
┌─── Paper Track（论文写作）─────────────────────────────┐
│                                                          │
│  Stage 5.0: PAPER INTAKE                               │
│    ⚠️ 前置条件: Stage 4 checkpoint 选 [B]，且 Stage 1-4 │
│       产物完整（passport 状态全部 completed/consumed）  │
│    ├ 期刊模板选择（从 shared/journal-templates/）       │
│    ├ 报告规范选择（CONSORT/STROBE/STARD...）             │
│    ├ 论文配置（语言/格式/引文风格/目标期刊）            │
│    └ 已有材料标注（MSRA 产物全部预填）                  │
│                                                          │
│  Stage 5.1: LITERATURE SEARCH  [deep-research]         │
│    ├ 以 MSRA Phase 1 文献对比为 seed（融合点 C）       │
│    └ 补充检索 → Bibliography                             │
│                                                          │
│  Stage 5.2: PAPER WRITING       [academic-paper]        │
│    ├ Introduction（需 literature）                      │
│    ├ Methods ← MSRA 方法学描述直接复用（融合点 D）      │
│    ├ Results ← MSRA results + tables/figures（融合点 F）│
│    └ Discussion（需 literature + clinical context）     │
│                                                          │
│  Stage 5.5: INTEGRITY CHECK    🔴                        │
│    ├ 引用/数据/声明验证                                  │
│    ├ MSRA Stage 3.5 门闸报告作为输入（融合点 B）       │
│    └ FAIL → 修复，max 3 rounds                           │
│                                                          │
│  Stage 5.6: PEER REVIEW       [academic-paper-reviewer] │
│    └ 5 reviewers + editorial decision                     │
│                                                          │
│  Stage 5.7: REVISE           [academic-paper]            │
│    └ 修订 → Response to Reviewers                        │
│                                                          │
│  Stage 5.6': RE-REVIEW（如需）                           │
│  Stage 5.7': RE-REVISE（如需）                           │
│  Stage 5.8: FINAL INTEGRITY  🔴                         │
│                                                          │
│  Stage 5.9: FINALIZE         [academic-paper]            │
│    └ MD → DOCX → PDF                                      │
│                                                          │
│  Stage 6: PROCESS SUMMARY                                │
│    └ 统一过程记录（MSRA + Paper 全流程）                │
└────────────────────────────────────────────────────────┘
```

### 4.2 六大融合点

| # | 融合点 | MSRA 来源 | ARS 消费者 | 复用方式 |
|---|--------|----------|-----------|---------|
| A | **Passport 统一** | `shared/passport/passport_schema.md` | ARS Material Passport | 扩展 MSRA passport 增加 ARS 阶段字段，替代 ARS 独立 passport |
| B | **Quality Gate 输出复用** | Stage 3.5 门闸报告 | Stage 5.5 Integrity Check | 统计数字已验证，不需重复检查 |
| C | **文献对比 → 文献检索 seed** | Stage 4 Phase 1 Step 4 文献对比 | Stage 5.1 deep-research | MSRA 已有关键文献作为起点 |
| D | **方法学描述复用** | Stage 4 Phase 5 统计方法段落 | Stage 5.2 Methods 章节 | 直接引用，不重新生成 |
| E | **期刊模板 → intake 配置** | Phase 2.5 期刊选择（如有） | Stage 5.0 Paper Intake | 已选期刊直接传递 |
| F | **表格图表双轨复用** | `figures/*.png` + `tables/*.docx` | Stage 5.2 Results 章节 | 直接引用，不重新生成 |

### 4.3 组件说明

#### 组件 A：ARS `shared/` 依赖合并进项目

将上游 ARS 的运行时依赖直接放入项目 `shared/` 目录：

```
shared/
├── [MSRA 原有目录，不动]
│   ├── reporting-guidelines/    ← 16 个临床报告规范（MSRA 独有资产）
│   ├── journal-templates/       ← 期刊模板
│   ├── passport/                 ← Material Passport
│   ├── statistics-methods/       ← 统计方法目录
│   ├── sap/                      ← SAP 标准
│   └── ...
│
├── [ARS 合并进来]
│   ├── handoff_schemas.md        ← 跨 skill 数据契约（9 个 schema）
│   ├── collaboration_depth_rubric.md
│   ├── compliance_checkpoint_protocol.md
│   ├── contracts/                ← 7 个子目录
│   │   ├── passport/
│   │   ├── submission/
│   │   ├── writer/
│   │   ├── reviewer/
│   │   ├── patch/
│   │   ├── audit/
│   │   └── evaluator/
│   └── references/
│       ├── intent_clarification_protocol.md
│       └── ...
│
└── .claude/
    └── CLAUDE.md                 ← Routing Discipline v3.9.2

commands/                         ← ARS 斜杠命令（ars-*）
```

**命名冲突处理**：
- MSRA 和 ARS 的 shared 文件经扫描**无同名冲突**——MSRA shared 是医学统计专用
  （reporting-guidelines/ statistics-methods/ sap/ passport/ 等），ARS shared 是
  学术写作通用（handoff_schemas/ contracts/ references/ 等）。
- 若未来上游 ARS 新增文件与 MSRA 同名，放入 `shared/ars/` 子目录并一次性
  替换 ARS skill 中的引用路径。
- ARS skill 中所有 `shared/` 引用**无需修改路径**，自然指向合并后的 `shared/`。

#### 组件 B：bridge skill → **废除，逻辑内化**

> v1 的独立 bridge skill 不再保留。其 Phase 1（产物发现）、Phase 2（翻译）、
> Phase 3（唤起）逻辑拆分到统一 Pipeline 的以下位置：
>
> - **Phase 1 产物发现** → pipeline Stage 4 checkpoint 读取 passport
> - **Phase 2 翻译** → pipeline Stage 5.0 Paper Intake 自动预填
> - **Phase 3 唤起** → pipeline Stage 5.0 直接调度 academic-paper skill
>
> MSRA Handoff Bundle 格式保留（见下方），但作为 pipeline 内部数据结构，
> 不再通过独立 skill 生成。

#### 组件 C：修改 `skills/resources/academic-paper/agents/intake_agent.md`（加 MSRA 分支）

在现有"Deep Research Handoff Detection"之后，新增并列的
"MSRA Handoff Detection"分支。**只改这 1 个 agent 文件，不动 academic-paper 的其他部分**。

新增逻辑：
```markdown
## MSRA Handoff Detection

### Detection Logic（在 Deep Research 检测之后执行）

1. 检查对话上下文或工作目录是否存在 `MSRA_HANDOFF_BUNDLE.md`
2. 识别标记（任一命中即触发）：
   - 文件头含 `# MSRA Handoff Bundle`
   - passport_id 字段（格式 msra-YYYYMMDD-NNN）
   - 由 unified pipeline Stage 5.0 唤起（前置 stage 标记）

### When MSRA Handoff Is Detected

1. 自动预填（从 bundle 读取）：
   - RQ ← bundle 的 Research Question
   - Discipline ← bundle 的 study_type 推导（默认 medicine）
   - Method ← bundle 的 Methods Summary
   - Existing Materials ← 全部勾选 Data/Results
   - Citation Format ← Vancouver（医学默认）
   - Paper Type ← IMRaD
   - Target Journal ← 如 MSRA Phase 2.5 已选则预填

2. 跳过冗余问题：
   - 跳过 Step 1（Topic & RQ）
   - 跳过 Step 8（Existing Materials）
   - 仍需确认：Target Journal、Output Format、Language、Co-Authors、Funding

3. 报告规范注入：
   - 从 shared/reporting-guidelines/ 加载对应规范检查清单
   - 在 Paper Configuration Record 标注适用规范（CONSORT/STROBE/STARD）
   - academic-paper Phase 6 的 compliance check 引入 MSRA 临床规范

4. Bibliography 特殊处理：
   - MSRA Phase 1 文献对比作为 seed 传入 literature_strategist
   - literature_strategist 正常运行 Phase A 检索（在此基础上扩展）
   - 标注：Bibliography source = MSRA seed + ARS extension

5. 激活 clinical Domain Evidence Profile：
   - intake Step 12 将 `clinical` 从 reserved 升级为 active
   - 使用 MSRA 统计方法知识提供临床研究专用证据标准
```

### 4.4 MSRA Handoff Bundle 格式（pipeline 内部数据结构）

生成位置：`MSRA/msra_handoff_bundle.md`（与 passport 同目录）

```markdown
# MSRA Handoff Bundle

## Source
- passport_id: msra-20260529-001
- study_type: RCT
- msra_version: 0.7.6
- track: full_paper

## Research Question
[从 SAP.md 提取的研究问题]

## Results Bundle
### 结果解读
[引用 final_report.md 的 Phase 1 结果解读章节路径]
### Tables
- tables/table1_baseline.docx
- tables/table2_primary.docx
### Figures
- figures/figure1_km_curve.png
- figures/figure2_forest.png

## Methods Summary
[引用 SAP.md 的统计方法章节 + final_report.md 的 Phase 5 方法学描述]

## Quality Gate Report
[引用 Stage 3.5 门闸报告路径]

## Literature Seed
[MSRA Phase 1 文献对比的关键文献列表]

## Journal Template (if selected)
- template: NEJM
- source: shared/journal-templates/NEJM.json

## Bibliography
[EMPTY — 由 Stage 5.1 deep-research 补充；MSRA seed 先行]
```

### 4.5 统一 Passport Schema 扩展

在现有 MSRA passport 基础上增加 ARS 阶段追踪：

```json
{
  "passport_id": "msra-20260529-001",
  "study_type": "RCT",
  "track": "full_paper",
  "stages": {
    "stage_1": { "status": "consumed", "artifacts": [...] },
    "stage_1.5": { "status": "consumed", "artifacts": [...] },
    "stage_2": { "status": "consumed", "artifacts": [...] },
    "stage_2.5": { "status": "consumed", "artifacts": [...] },
    "stage_3": { "status": "consumed", "artifacts": [...] },
    "stage_3.5": { "status": "consumed", "artifacts": [...] },
    "stage_4": { "status": "completed", "artifacts": [...] },
    "stage_5.0_intake": { "status": "pending", "artifacts": [] },
    "stage_5.1_literature": { "status": "pending", "artifacts": [] },
    "stage_5.2_writing": { "status": "pending", "artifacts": [] },
    "stage_5.5_integrity": { "status": "pending", "artifacts": [] },
    "stage_5.6_review": { "status": "pending", "artifacts": [] },
    "stage_5.7_revise": { "status": "pending", "artifacts": [] },
    "stage_5.8_final_integrity": { "status": "pending", "artifacts": [] },
    "stage_5.9_finalize": { "status": "pending", "artifacts": [] },
    "stage_6_summary": { "status": "pending", "artifacts": [] }
  }
}
```

**字段约定**：
- `track`: `"report_only"` | `"full_paper"` — 用户在 Stage 4 checkpoint 的选择
- ARS 阶段仅在 `track == "full_paper"` 时出现
- 产物状态生命周期不变：`planned` → `in_progress` → `completed` → `verified` → `consumed`

### 4.6 Stage 4 精简方案

原 Stage 4 有 7 个 Phase。精简后移除发表级内容，保留统计核心：

| Phase | 原位置 | 精简后位置 | 变化 |
|-------|--------|-----------|------|
| Phase 1: 结果解读 | MSRA Stage 4 | **MSRA Stage 4** ✅ 不变 | — |
| Phase 2: 确定报告规范 | MSRA Stage 4 | **Stage 5.0 Paper Intake** → | 移到 Paper Track |
| Phase 2.5: 期刊模板选择 | MSRA Stage 4 | **Stage 5.0 Paper Intake** → | 移到 Paper Track |
| Phase 3: 表格生成 | MSRA Stage 4 | **MSRA Stage 4** ✅ 保留 | 表格内容是统计产出 |
| Phase 3.5: 表格导出 | MSRA Stage 4 | **MSRA Stage 4** ✅ 保留 | 三线表是统计产出 |
| Phase 4: 图表生成 | MSRA Stage 4 | **MSRA Stage 4** ✅ 保留 | 图表是统计产出 |
| Phase 5: 方法学描述 | MSRA Stage 4 | **MSRA Stage 4** ✅ 保留 | 直接复用到论文 Methods |
| Phase 6: 规范合规检查 | MSRA Stage 4 | **精简为统计质量检查** → | 只保留 statcheck + anti-patterns |
| Phase 7: 报告组装 | MSRA Stage 4 | **MSRA Stage 4** ✅ 保留 | — |

**精简后的 Stage 4 流程**：
```
Phase 1: 结果解读（不变）
  ↓
Phase 3: 表格生成 + 导出（不变）
  ↓
Phase 4: 图表生成（不变）
  ↓
Phase 5: 方法学描述（不变）
  ↓
Phase 6: 统计质量检查（精简版）
  ├ statcheck_rules: NHST 结果一致性验证（保留）
  ├ anti-patterns: 统计反模式检查（保留）
  ├ quality_checklist: 9 维度质量检查（保留统计方法/结果报告维度）
  └ 移除: CONSORT/STROBE 全文合规检查 → Paper Track Stage 5.0
  ↓
Phase 7: 报告组装（不变）
  ↓
★ STAGE 4 CHECKPOINT — 用户选择 [A] 结束 / [B] 继续 Paper Track
```

### 4.7 不改动的部分（明确边界）

- ❌ 不改 MSRA 的 Stage 1-3 及其 skill（data-prep / analysis-plan / analysis-exec）
- ❌ 不改 MSRA 的 `shared/` 目录已有内容
- ❌ 不改 academic-paper 除 intake_agent.md 外的任何文件
- ❌ 不改 academic-paper-reviewer / deep-research 的主体逻辑
- ❌ 不改 MSRA 的 passport schema 已有字段（只扩展，不修改）

---

## 5. Stage 5.0 Paper Intake 详细设计

Stage 5.0 是 MSRA Core → Paper Track 的转换枢纽，合并了原 bridge skill 的
翻译逻辑和 ARS intake 的预填逻辑。

### 5.1 输入

- MSRA passport（已验证 Stage 1-4 全部 completed）
- MSRA 产物：final_report.md + figures/*.png + tables/*.docx + SAP.md
- MSRA Stage 3.5 门闸报告
- MSRA Phase 1 文献对比（如有）

### 5.2 工作流程

```
Step 1: 产物校验
  ├ 读 passport，确认 Stage 4 status == "completed"
  ├ 校验: final_report.md 存在 + 至少 1 张 figure + 至少 1 张 table
  └ 失败 → 提示用户先完成 Stage 4

Step 2: 生成 MSRA Handoff Bundle
  ├ 从 passport + SAP + final_report 提取字段
  └ 写入 MSRA/msra_handoff_bundle.md

Step 3: 报告规范选择
  ├ 基于 study_type 自动推荐（RCT→CONSORT, 观察性→STROBE, ...）
  ├ 展示推荐规范 + 检查清单概要
  └ 用户确认（可覆盖）

Step 4: 期刊模板选择
  ├ 加载 shared/journal-templates/ 可用模板
  ├ [0] 自由格式 / [1-5] 预置 / [6] 自定义
  └ 用户选择

Step 5: 论文配置确认
  ├ 预填项：RQ / Discipline / Method / Existing Materials / Citation(Vancouver)
  ├ 待确认项：Target Journal / Output Format / Language / Co-Authors / Funding
  └ 调用 academic-paper intake（传入 MSRA Handoff Bundle）
```

### 5.3 字段映射表（MSRA 产物 → Handoff Bundle → academic-paper intake）

| academic-paper intake 字段 | 来源（MSRA） | 默认值 |
|---|---|---|
| Topic / Research Question | `passport.study_type` + SAP.md 研究问题章节 | 从 SAP 提取 |
| Discipline | 推导自 study_type（RCT/观察性→临床医学；诊断→诊断试验） | `medicine` |
| Paper Type | 实证研究默认 | `IMRaD` |
| Target Journal | Phase 2.5 期刊选择（如有） | `General` |
| Citation Format | 医学默认 | `Vancouver` |
| Output Format | | `Markdown` |
| Body Language | 跟随 MSRA 报告语言 | `Bilingual` |
| Existing Materials | ✅ Data/Results（final_report + figures + tables） | 全部勾选 |
| Reporting Guideline | study_type → CONSORT/STROBE/STARD | 自动推荐 |

---

## 6. 错误处理

| 场景 | 处理 |
|---|---|
| **用户无数据处理需求，直接要求写论文** | **拒绝进入本插件，提示"纯写作请直接使用 ARS 的 academic-paper / academic-pipeline"** |
| passport.json 不存在 | 提示"未找到 MSRA 项目，请先在项目目录运行 /msra" |
| Stage 4 报告产物缺失 | 提示"报告未生成，请先运行 /msra-report" |
| figures/ 或 tables/ 为空 | 警告但不阻断（用户可能只要文字报告） |
| ARS skill 的 shared/ 文件缺失 | 提示运行 install.ps1 的 ARS 合并步骤 |
| study_type 无法推导 Discipline | 默认 medicine，让用户在 intake 确认时改 |
| Bibliography 为空 | 正常——Stage 5.1 deep-research 会补检索 |
| 用户在 Stage 4 选 [B] 但 ARS 依赖缺失 | 提示缺失文件清单，引导运行 install.ps1 |
| Stage 5.1 Literature Search 用户已有文献 | intake Step 8 可标注"已有文献"，跳过或精简检索 |
| MSRA Phase 1 无文献对比产出 | Stage 5.1 正常从零检索，标注"无 MSRA seed" |
| CONSORT/STROBE 检查清单文件缺失 | 搜索网上最新版（WebSearch），生成临时清单 |
| shared/ 文件命名冲突 | 合并时检测，冲突文件放入 `shared/ars/` 子目录 |

---

## 7. 测试策略

- **冒烟测试 1（Report Only 轨）**：完整跑 Stage 1-4，在 checkpoint 选 [A]，
  验证统计报告正确生成、pipeline 正常结束。
- **冒烟测试 2（Full Paper 轨）**：完整跑 Stage 1-4，选 [B]，
  验证：(a) Handoff Bundle 生成 (b) Paper Intake 预填正确
  (c) academic-paper 能读到 bundle (d) 完整跑通到 Stage 6。
- **拒绝场景测试**：用户无数据处理需求，直接要求"写论文"，
  验证 pipeline 拒绝进入并提示使用 ARS 原生 skill。
- **融合点测试**：
  - 融合点 B：验证 Stage 3.5 门闸报告被 Stage 5.5 引用
  - 融合点 C：验证 MSRA 文献 seed 传入 deep-research
  - 融合点 D：验证论文 Methods 章节引用 MSRA 方法学描述
  - 融合点 F：验证论文 Results 直接引用 MSRA tables/figures
- **缺失场景测试**：删掉 passport / 删掉 figures，验证错误提示。
- **路径检查**：ARS skill 里所有 `shared/` 引用在合并后都能正确解析。
- **回归测试**：MSRA Stage 1-4 的 test-prompts.json 仍通过（零侵入）。

---

## 8. 实施顺序

1. **合并 ARS shared/ 依赖**进项目 `shared/`
   （上游 54 个文件 + `.claude/CLAUDE.md` + `commands/`）
   - 检查命名冲突，冲突文件放入 `shared/ars/`
   - ARS skill 中对应的引用路径做一次性替换
2. **精简 MSRA Stage 4**
   - 移除 Phase 2（报告规范选择）和 Phase 2.5（期刊模板选择）
   - Phase 6 精简为统计质量检查（保留 statcheck + anti-patterns + quality_checklist 统计维度）
   - 在 Stage 4 末尾添加 CHECKPOINT 决策节点
3. **扩展 MSRA pipeline skill**
   - 新增 Stage 5.0-5.9 的调度逻辑（Paper Track）
   - Stage 4 checkpoint → [A] 结束 / [B] 继续 Stage 5.0
   - Stage 5.x 调度 academic-paper / academic-paper-reviewer / deep-research
   - Handoff Bundle 生成逻辑
4. **扩展 MSRA passport schema**
   - 增加 `track` 字段和 ARS 阶段追踪
5. **改 academic-paper intake_agent.md**
   - 加 MSRA Handoff Detection 分支
   - 激活 clinical Domain Evidence Profile
   - 引入 MSRA 报告规范到 compliance check
6. **manifest.json 更新**
   - 移除 `/msra-write` 命令（bridge 废除）
   - 更新 `/msra` 命令描述（反映统一 Pipeline）
7. **install.ps1 更新**
   - 加 ARS shared 合并步骤
8. **冒烟测试 + 回归测试**

---

## 9. 风险

| 风险 | 影响 | 缓解 |
|---|---|---|
| 用户无数据需求误入本插件 | 流程走不通，浪费时间 | Stage 1 入口和 Stage 4 checkpoint 均有守卫检查；明确文档定位 |
| ARS 上游更新后 shared/ 结构变化 | ARS skill 引用失效 | 合并时记录上游 commit hash；手动重新合并 + diff 检查 |
| 统一 Pipeline skill 过于庞大 | 维护复杂度上升 | Pipeline skill 仍保持 orchestrator 架构，不混入实质工作 |
| Stage 4 精简后用户仍需期刊模板 | 工作流断裂 | Paper Track Stage 5.0 必须在第一步就提供期刊模板选择 |
| CONSORT 检查清单版本过时 | 报告合规不准确 | Stage 5.0 检测缺失清单时自动 WebSearch 最新版 |
| 改 intake_agent.md 与上游 ARS 冲突 | 未来同步 ARS 时冲突 | 用清晰注释标记 `# [MSRA-BRIDGE]` 区块，便于 rebase |
| shared/ 合并后目录膨胀 | 可读性下降 | MSRA 文件和 ARS 文件天然无命名冲突；如未来冲突则用 `shared/ars/` 子目录 |

---

## 10. 开放问题（实施时再定）

- MSRA Handoff Bundle 放在 `MSRA/` 还是项目根——倾向 `MSRA/` 与 passport 同目录。
- Stage 5.1 Literature Search 是否提供"跳过"选项（用户已有文献时）——倾向提供。
- Stage 5.2 论文写作中 Methods 章节是"直接引用 MSRA 方法学描述"还是"基于 MSRA
  重新生成学术论文风格的 Methods"——倾向前者，如学术风格不足可手动调整。
- Pipeline skill 的 Paper Track 调度是否复用 `academic-pipeline` skill 的
  orchestrator 逻辑（Mode A），还是自己在 MSRA pipeline skill 里重新实现——
  倾向前者（复用 academic-pipeline 的状态机），后者导致重复代码。
- 上游 ARS 更新后的合并策略——是手动 git merge 还是脚本辅助 diff——倾向先手动，
  积累经验后考虑自动化。

---

## 附录 A：版本变更记录

### v1 → v2

| 变更项 | v1 | v2 | 理由 |
|--------|-----|-----|------|
| 整体架构 | MSRA pipeline + bridge + ARS pipeline | 统一 Pipeline（MSRA Core + Paper Track） | 减少用户认知负担 |
| Bridge skill | `skills/msra-to-ars/SKILL.md` | **废除**，逻辑内化进 pipeline | 单一入口更自然 |
| Stage 4 分叉 | 无（Stage 4 是终点） | Stage 4 checkpoint: [A] 结束 / [B] Paper Track | 用户明确意图 |
| 报告规范位置 | MSRA Stage 4 Phase 2 + Phase 6 | Paper Track Stage 5.0 | CONSORT 全文合规是发表级需求 |
| 期刊模板位置 | MSRA Stage 4 Phase 2.5 | Paper Track Stage 5.0 | 只有写论文才选期刊 |
| Passport | MSRA passport（只读）+ ARS 独立 passport | 统一扩展 passport | 一套追踪系统 |
| 临床报告规范 | MSRA 独有，ARS 无 | Paper Track 继承 MSRA 规范 | ARS 原生无此能力 |
| 文献对比 | MSRA 产出后被丢弃 | 作为 ARS 文献检索 seed | 融合点 C |
| 方法学描述 | 可能被重新生成 | 直接复用 | 融合点 D |
| 表格图表 | 可能被重新生成 | 直接复用 | 融合点 F |

### v2 → v3

| 变更项 | v2 | v3 | 理由 |
|--------|-----|-----|------|
| 项目定位 | MSRA 引入 ARS 作为第三方 | 融合为新项目 | 用户确认不需要协议隔离 |
| shared/ 获取 | `third_party/` vendor + junction `shared_ars` | 直接合并进 `shared/` | 融合项目无需物理隔离 |
| 协议声明 | ATTRIBUTION.md + LICENSE-ARS + NOTICE.md + README 章节 | 全部移除 | 新项目统一协议 |
| 路径适配 | shared/→shared_ars/ 批量替换 + junction | 无需替换（自然指向） | 合并后路径不变 |
| install.ps1 | vendor 下载 + junction 创建 | shared 文件复制/合并 | 简化安装流程 |
| 错误处理 | junction 失效、ATTRIBUTION 缺失 | shared 文件缺失、命名冲突 | 场景更简单 |
| 风险 | CC BY-NC 4.0 限制商用、junction 失效 | 上游更新合并冲突、目录膨胀 | 风险更少 |

### v3 → v4

| 变更项 | v3 | v4 | 理由 |
|--------|-----|-----|------|
| 定位 | 统一 Pipeline，无明确适用边界 | **仅限数据处理场景** | 纯写作用户不应走本插件，应直接用 ARS |
| 成功标准 | 5 条 | 6 条（新增第 6 条数据驱动定位） | 强化插件边界 |
| 非目标 | 5 条 | 6 条（新增"不替代 ARS 通用写作"） | 避免功能重叠 |
| Pipeline 图 | 无守卫 | Stage 4 checkpoint 后加**守卫检查** + Stage 5.0 前置条件 | 阻止无数据用户进入 Paper Track |
| 错误处理 | 无此场景 | 新增"用户无数据处理需求"拒绝行 | 明确拒绝逻辑 |
| 测试策略 | 无此场景 | 新增"拒绝场景测试" | 验证守卫生效 |
| 风险 | 无此风险 | 新增"用户无数据需求误入" | 提前防范误用 |
