# 设计文档：MSRA × MSRA 整合（数据统99学术写作全流水线9
- **日期**: 2026-06-17
- **版本**: v4 (统一 Pipeline 架构，融合项目，数据驱动定位)
- **状9*: 待审核- **作9*: boangus（经 brainstorming 流程9- **关联上游**: [boangus/medical-stats-research-assistant](https://github.com/boangus/medical-stats-research-assistant) v3.12.1 (commit `88fc003`, 2026-06-17)
- **变更记录**: v1→v2 统一 Pipeline; v2→v3 废除协议隔离; v3→v4 数据驱动定位强化

---

## 1. 目标

9MSRA（Academic Research Skills）的"研究→写作→评审→修订→定稿"能力融入 MSRA9形成**一个统一项目**——从原始数据出发，用户在统计报告完成后选择是结?还是继续写可投稿论文，全程无需切换 skill 或手工搬运文件9
> **⚠️ 核心定位**：本插件仅在**需要数据处理的项目**中启用。用户若只需纯学术写9> （无数据分析需求），应直接使用 MSRA 9medical-paper / medical-pipeline 9> skill9*不经过本插件**。本插件9Paper Track 9MSRA 统计产物的下游消费者，
> 没有统计报告就进入不了论文轨道9
### 成功标准

1. **统一 Pipeline 端到端跑9*：用户从 `/msra` 一路走到最终论文，
   中间9Stage 4 有分叉节点，不需要手动调用第二个 skill92. **分叉节点生效**：Stage 4 完成后用户可选择 [A] 统计报告结束 9   [B] 继续 Paper Track；选择 [B] 9MSRA 产物自动传递给论文写作阶段3. **MSRA 4 9skill 可运9*：medical-paper / medical-paper-reviewer /
   medical-pipeline / systematic-survey 引用9`shared/` 依赖全部就位94. **临床报告规范贯9*：Paper Track 继承 MSRA 9CONSORT/STROBE/STARD
   916 个报告检查清单（MSRA 原生不具备此能力）95. **MSRA Core 零侵9*：Stage 1-4 的核心逻辑不变，仅 Stage 4 做精简96. **数据驱动定位明确**：本插件仅在需要数据处理的项目中启用，纯写作场景不经本插件9
### 适用范围（核心定位）

> **⚠️ 核心定位**：本插件仅在**需要数据处理的项目**中启用。用户若只需纯学术写9> （无数据分析需求），应直接使用 MSRA 9medical-paper / medical-pipeline 9> skill9*不经过本插件**。本插件9Paper Track 9MSRA 统计产物的下游消费者，
> 没有统计报告就进入不了论文轨道9
| 场景 | 是否使用本插9| 说明 |
|---|---|---|
| 有原始数据，需要统计分9+ 报告 + 可能写论9| 9**使用** | 本插件的核心场景：Stage 19（必须）95-6（可选） |
| 有分析结果，需要统计报9+ 可能写论9| 9**使用** | 9Stage 4 中间切入，仍9MSRA 报告流程 |
| 只需要统计报告，不写论文 | 9**使用** | 跑到 Stage 4 checkpoint 9[A] 结束 |
| 只需要写论文，不需要数据分9| 9**不用** | 直接9MSRA 9`medical-paper` / `medical-pipeline` |
| 只需要文献检查| 9**不用** | 直接9MSRA 9`systematic-survey` |
| 只需要论文评价| 9**不用** | 直接9MSRA 9`medical-paper-reviewer` |

**判断规则**：有数据要处9?使用本插件；无数据纯写999MSRA 原生 skill9
### 非目标（YAGNI9
- 不在 MSRA 内实现文献检索（那是 MSRA `systematic-survey` 的职责）9- 不做 MSRA 的中文化——MSRA 保持英文，桥接时中英混排9medical-paper 的语言设置处理9- 不做自动升级机制（上9MSRA 更新时手动合并，记录版本号）9- 不保留独立的 `msra-to-MSRA` bridge skill（逻辑已内化进统一 Pipeline）9- 不做协议隔离——融合后属于一个新项目，MSRA 依赖直接合并进项9`shared/`9- **不替9MSRA 的通用写作能力**——纯写作场景直接9MSRA 原生 skill，不经过本插件9
---

## 2. 关键决策（已与用户确认）

| 维度 | 决策 | 理由 |
|---|---|---|
| 整合架构 | **统一 Pipeline**（废9bridge9| 用户9Stage 1 一路走到论文，中途分叉比切换 skill 更自9|
| 分叉方式 | **Stage 4 末尾决策节点** | 统计报告完成后自然询?继续写论文？" |
| MSRA 报告规范 | **引入 MSRA 临床规范** | MSRA 原生9CONSORT/STROBE，这9MSRA 独有资产 |
| shared/ 获取 | **直接合并进项9shared/** | 融合后是一个新项目，不需要物理隔9|
| intake 识别 | **MSRA intake 9MSRA 分支** | 字段更准确（携带 figures/tables），仅改 1 9agent 文件 |
| MSRA Stage 4 精简 | **报告规范+期刊模板移到 Paper Track** | CONSORT 全文合规检查是发表级需求，统计报告阶段不需9|
| Passport | **统一扩展** | 一9passport 追踪9Stage 1 9final paper 的全部产9|

---

## 3. 现状分析（为什么需要做这些事）

### 3.1 MSRA skill 本地已有9半成9

`skills/` 下已94 9MSRA skill（git 未跟9`??` 状态），内部结构齐全：

| skill | 本地版本 | 上游 v3.12.1 |
|---|---|---|
| medical-paper | v3.2.0 | 9|
| medical-paper-reviewer | v1.10.0 | 9|
| medical-pipeline | v3.12.1 | 9|
| systematic-survey | v2.10.0 | 9|

### 3.2 缺口：约 54 9MSRA `shared/` 文件 + `.claude/CLAUDE.md` + commands

94 9skill 在运行时引用 `shared/` 下的依赖文件，9MSRA 仓库9`shared/` 是医学统9专用目录9*不含任何 MSRA 依赖**。引用扫描发现有940 9`shared/...` 引用（去重后930 ?不同文件，上游实际提954 9shared 文件）全部指向本地不存在的文件，典型如：

- `shared/handoff_schemas.md`（跨 skill 数据契约9 9schema9- `shared/collaboration_depth_rubric.md`
- `shared/references/intent_clarification_protocol.md`
- `shared/compliance_checkpoint_protocol.md`
- `shared/contracts/` 97 个子目录（passport/ submission/ writer/ reviewer/ patch/ audit/ evaluator/9- `.claude/CLAUDE.md`（Routing Discipline v3.9.2 的所在地9
**解决方案**：将上游 MSRA 954 9shared 文件、`.claude/CLAUDE.md`、`commands/`
直接合并进项目。MSRA skill 中的 `shared/` 引用无需修改路径，自然指向合并后9`shared/`?对于命名冲突的文件（9MSRA 9MSRA 都有的同名文件），在合并时以命名空间子目录区9（如 `shared/MSRA/` 存放 MSRA 特有的文件，AR skill 中的引用路径做一次性替换）9
**结论**：不补齐这些依赖，MSRA 端到端跑不起来9
### 3.3 MSRA 完全缺乏临床报告规范能力

MSRA 9compliance 框架围绕 AI 研究透明度设计（PRISMA-trAIce + RAISE），
**没有任何 CONSORT/STROBE/STARD/PRISMA 检查清9*。具体发现：

- `resources/medical-paper/references/` 下有 `medical_writing_style.md`9  `medical_writing_quality_check.md` 等写作规范，但无临床报告规范9- `medical-pipeline` Stage 2.5 9integrity check 验证引用/数据/声明9  不验证临床报告合规9- `paper_config_agent.md` Step 12 9`clinical` Domain Evidence Profile 9  **reserved 空占9*，实9fallback 9`unknown_user_defined`9
**对比 MSRA**：`shared/reporting-guidelines/` 916 个文件，含：
- CONSORT 202590 条目，含 PPI/AI disclosure 97 条新增）
- STROBE 2007 + extensions
- PRISMA 2020 + NMA
- STARD 2015（含 TRIPOD+AI 交叉引用9- TRIPOD+AI 2024 / TRIPOD-LLM 2024
- TRUE-AIM 2025（AHA AI 模型 QA9- REMARK / CARE / ARRIVE / SPIRIT / CHEERS

**结论**：融合不仅是流水线串联，更是9Paper Track 继承 MSRA 的临床报告规9专业能力——独9bridge 方案做不到这一点9
### 3.4 MSRA 有现成的产物追踪机制可复9
MSRA 9`shared/passport/passport_schema.md` 定义9Material Passport9记录每个 stage 的产物路径、hash、status、`study_type`。这是统一 Pipeline 9**权威数据9*——扩展后可追9MSRA 阶段的产物9
### 3.5 MSRA Report 9Quarto 模板可双轨复9
`shared/report-assembler/report_template.qmd` 已定义完9IMRaD 结构
（Study Overview 9Methods 9Results 9Discussion 9Supplementary），
可作为论文初稿的结构基础9
---

## 4. 架构

### 4.1 统一 Pipeline 总览

```
══════════════════════════════════════════════════════════════9  UNIFIED PIPELINE: 原始数据 ?系统计报告 9(可9 可投稿论9  ⚠️ 入口前提: 用户有数据需要处理。纯写作场景请直接使9MSRA9══════════════════════════════════════════════════════════════9
┌─── MSRA Core（统计分析）──────────────────────────────99                                                         99 Stage 1:   DATA PREP            [/msra-data]            99 Stage 1.5: DATA QUALITY GATE     🔴                   99 Stage 2:   ANALYSIS PLAN        [/msra-plan]            99 Stage 2.5: SAP QUALITY GATE      🔴                   99 Stage 3:   ANALYSIS EXEC         [/msra-exec]           99 Stage 3.5: RESULTS QUALITY GATE  🔴                   99                                                         99 Stage 4:   STATISTICAL REPORT   [/msra-report]         99   9Phase 1: 结果解读                                   99   9Phase 3: 表格生成 + 导出                            99   9Phase 4: 图表生成                                   99   9Phase 5: 方法学描9                                99   9Phase 6: 统计质量检查（精简版）                      99         保留: statcheck_rules / anti-patterns          99         移除: CONSORT/STROBE 全文合规 + 期刊模板选择   99                                                         99 9STAGE 4 CHECKPOINT (MANDATORY)                       99 ┌──────────────────────────────────────────9          99 9 统计报告已完9                          9          99 9 - final_report.md + final_report.html    9          99 9 - figures/*.png + tables/*.docx          9          99 9                                         9          99 9 选择下一9                              9          99 9 [A] 统计报告完成，结9                  9          99 9 [B] 继续写论99Paper Track            9          99 └──────────────────────────────────────────9          9└────────────────────────────────────────────────────────9                        9                [A] 9════════════════════ 结束
                        9                [B] 9          ┌─────────────────────────────────9          9守卫检查 Stage 1-4 产物是否齐全？│
          9  final_report + figures + tables 9          9  ?无数据则拒绝，提示用 MSRA     9          └────────────────┬────────────────9                           9┌─── Paper Track（论文写作）─────────────────────────────99                                                         99 Stage 5.0: PAPER INTAKE                               99   ⚠️ 前置条件: Stage 4 checkpoint 9[B]，且 Stage 1-4 99      产物完整（passport 状态全9completed/consumed9 99   ?期刊模板选择（从 shared/journal-templates/9      99   9报告规范选择（CONSORT/STROBE/STARD...9            99   ?结论文配置（语言/格式/引文风格/目标期刊9           99   ?已有材料标注（MSRA 产物全部预填9                 99                                                         99 Stage 5.1: LITERATURE SEARCH  [systematic-survey]         99   99MSRA Phase 1 文献对比9seed（融合点 C9      99   9补充检查9Bibliography                             99                                                         99 Stage 5.2: PAPER WRITING       [medical-paper]        99   9Introduction（需 literature9                     99   9Methods 9MSRA 方法学描述直接复用（融合9D9     99   9Results 9MSRA results + tables/figures（融合点 F）│
9   9Discussion（需 literature + clinical context9    99                                                         99 Stage 5.5: INTEGRITY CHECK    🔴                        99   9引用/数据/声明验证                                  99   9MSRA Stage 3.5 门闸报告作为输入（融合点 B9      99   9FAIL ?修复复，max 3 rounds                           99                                                         99 Stage 5.6: PEER REVIEW       [medical-paper-reviewer] 99   95 reviewers + editorial decision                     99                                                         99 Stage 5.7: REVISE           [medical-paper]            99   ?修复订 9Response to Reviewers                        99                                                         99 Stage 5.6': RE-REVIEW（如需9                          99 Stage 5.7': RE-REVISE（如需9                          99 Stage 5.8: FINAL INTEGRITY  🔴                         99                                                         99 Stage 5.9: FINALIZE         [medical-paper]            99   9MD 9DOCX 9PDF                                      99                                                         99 Stage 6: PROCESS SUMMARY                                99   ?系统一过程记录（MSRA + Paper 全流程）                9└────────────────────────────────────────────────────────9```

### 4.2 六大融合9
| # | 融合9| MSRA 来源 | MSRA 消费9| 复用方式 |
|---|--------|----------|-----------|---------|
| A | **Passport 统一** | `shared/passport/passport_schema.md` | MSRA Material Passport | 扩展 MSRA passport 增加 MSRA 阶段字段，替9MSRA 独立 passport |
| B | **Quality Gate 输出复用** | Stage 3.5 门闸报告 | Stage 5.5 Integrity Check | 统计数字已验证，不需重复检查|
| C | **文献对比 ?论文献检查seed** | Stage 4 Phase 1 Step 4 文献对比 | Stage 5.1 systematic-survey | MSRA 已有关键文献作为起点 |
| D | **方法学描述复9* | Stage 4 Phase 5 统计方法段落 | Stage 5.2 Methods 章节 | 直接引用，不重新生成 |
| E | **期刊模板 9intake 配置** | Phase 2.5 期刊选择（如有） | Stage 5.0 Paper Intake | 已选期刊直接传9|
| F | **表格图表双轨复用** | `figures/*.png` + `tables/*.docx` | Stage 5.2 Results 章节 | 直接引用，不重新生成 |

### 4.3 组件说明

#### 组件 A：MSRA `shared/` 依赖合并进项9
将上9MSRA 的运行时依赖直接放入项目 `shared/` 目录9
```
shared/
├── [MSRA 原有目录，不动]
9  ├── reporting-guidelines/    916 个临床报告规范（MSRA 独有资产99  ├── journal-templates/       ?期刊模板
9  ├── passport/                 9Material Passport
9  ├── statistics-methods/       ?系统计方法目录
9  ├── sap/                      9SAP 标准
9  └── ...
9├── [MSRA 合并进来]
9  ├── handoff_schemas.md        99skill 数据契约9 9schema99  ├── collaboration_depth_rubric.md
9  ├── compliance_checkpoint_protocol.md
9  ├── contracts/                97 个子目录
9  9  ├── passport/
9  9  ├── submission/
9  9  ├── writer/
9  9  ├── reviewer/
9  9  ├── patch/
9  9  ├── audit/
9  9  └── evaluator/
9  └── references/
9      ├── intent_clarification_protocol.md
9      └── ...
9└── .claude/
    └── CLAUDE.md                 9Routing Discipline v3.9.2

commands/                         9MSRA 斜杠命令（MSRA-*9```

**命名冲突处理**9- MSRA 9MSRA 9shared 文件经扫9*无同名冲9*——MSRA shared 是医学统计专9  （reporting-guidelines/ statistics-methods/ sap/ passport/ 等），MSRA shared 9  学术写作通用（handoff_schemas/ contracts/ references/ 等）9- 若未来上9MSRA 新增文件9MSRA 同名，放9`shared/MSRA/` 子目录并一次9  替换 MSRA skill 中的引用路径9- MSRA skill 中所9`shared/` 引用**无需修改路径**，自然指向合并后9`shared/`9
#### 组件 B：bridge skill 9**废除，逻辑内化**

> v1 的独9bridge skill 不再保留。其 Phase 1（产物发现）、Phase 2（翻译）9> Phase 3（唤起）逻辑拆分到统一 Pipeline 的以下位置：
>
> - **Phase 1 产物发现** 9pipeline Stage 4 checkpoint 读取 passport
> - **Phase 2 翻译** 9pipeline Stage 5.0 Paper Intake 自动预填
> - **Phase 3 唤起** 9pipeline Stage 5.0 直接调度 medical-paper skill
>
> MSRA Handoff Bundle 格式保留（见下方），但作9pipeline 内部数据结构9> 不再通过独立 skill 生成9
#### 组件 C：修9`resources/medical-paper/agents/paper_config_agent.md`（加 MSRA 分支9
在现9Deep Research Handoff Detection"之后，新增并列的
"MSRA Handoff Detection"分支9*只改91 9agent 文件，不9medical-paper 的其他部9*9
新增逻辑9```markdown
## MSRA Handoff Detection

### Detection Logic（在 Deep Research 检测之后执行）

1. 检查对话上下文或工作目录是否存9`MSRA_HANDOFF_BUNDLE.md`
2. 识别标记（任一命中即触发）9   - 文件头含 `# MSRA Handoff Bundle`
   - passport_id 字段（格9msra-YYYYMMDD-NNN9   - 9unified pipeline Stage 5.0 唤起（前9stage 标记9
### When MSRA Handoff Is Detected

1. 自动预填（从 bundle 读取）：
   - RQ 9bundle 9Research Question
   - Discipline 9bundle 9study_type 推导（默9medicine9   - Method 9bundle 9Methods Summary
   - Existing Materials 9全部勾9Data/Results
   - Citation Format 9Vancouver（医学默认）
   - Paper Type 9IMRaD
   - Target Journal 99MSRA Phase 2.5 已选则预填

2. 跳过冗余问题9   - 跳过 Step 1（Topic & RQ9   - 跳过 Step 8（Existing Materials9   - 仍需确认：Target Journal、Output Format、Language、Co-Authors、Funding

3. 报告规范注入9   - 9shared/reporting-guidelines/ 加载对应规范检查清9   - 9Paper Configuration Record 标注适用规范（CONSORT/STROBE/STARD9   - medical-paper Phase 6 9compliance check 引入 MSRA 临床规范

4. Bibliography 特殊处理9   - MSRA Phase 1 文献对比作为 seed 传入 literature_strategist
   - literature_strategist 正常运行 Phase A 检索（在此基础上扩展）
   - 标注：Bibliography source = MSRA seed + MSRA extension

5. 激9clinical Domain Evidence Profile9   - intake Step 12 9`clinical` 9reserved 升级9active
   - 使用 MSRA 统计方法知识提供临床研究专用证据标准
```

### 4.4 MSRA Handoff Bundle 格式（pipeline 内部数据结构9
生成位置：`MSRA/msra_handoff_bundle.md`（与 passport 同目录）

```markdown
# MSRA Handoff Bundle

## Source
- passport_id: msra-20260529-001
- study_type: RCT
- msra_version: 0.7.6
- track: full_paper

## Research Question
[9SAP.md 提取的研究问题]

## Results Bundle
### 结果解读
[引用 final_report.md 9Phase 1 结果解读章节路径]
### Tables
- tables/table1_baseline.docx
- tables/table2_primary.docx
### Figures
- figures/figure1_km_curve.png
- figures/figure2_forest.png

## Methods Summary
[引用 SAP.md 的统计方法章9+ final_report.md 9Phase 5 方法学描述]

## Quality Gate Report
[引用 Stage 3.5 门闸报告路径]

## Literature Seed
[MSRA Phase 1 文献对比的关键文献列表]

## Journal Template (if selected)
- template: NEJM
- source: shared/journal-templates/NEJM.json

## Bibliography
[EMPTY 99Stage 5.1 systematic-survey 补充；MSRA seed 先行]
```

### 4.5 统一 Passport Schema 扩展

在现9MSRA passport 基础上增9MSRA 阶段追踪9
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

**字段约定**9- `track`: `"report_only"` | `"full_paper"` ?使用户9Stage 4 checkpoint 的选择
- MSRA 阶段仅在 `track == "full_paper"` 时出9- 产物状态生命周期不变：`planned` 9`in_progress` 9`completed` 9`verified` 9`consumed`

### 4.6 Stage 4 精简方案

9Stage 4 97 9Phase。精简后移除发表级内容，保留统计核心：

| Phase | 原位9| 精简后位9| 变化 |
|-------|--------|-----------|------|
| Phase 1: 结果解读 | MSRA Stage 4 | **MSRA Stage 4** ?不变 | 9|
| Phase 2: 确定报告规范 | MSRA Stage 4 | **Stage 5.0 Paper Intake** 9| 移到 Paper Track |
| Phase 2.5: 期刊模板选择 | MSRA Stage 4 | **Stage 5.0 Paper Intake** 9| 移到 Paper Track |
| Phase 3: 表格生成 | MSRA Stage 4 | **MSRA Stage 4** 9保留 | 表格内容是统计产9|
| Phase 3.5: 表格导出 | MSRA Stage 4 | **MSRA Stage 4** 9保留 | 三线表是统计产出 |
| Phase 4: 图表生成 | MSRA Stage 4 | **MSRA Stage 4** 9保留 | 图表是统计产9|
| Phase 5: 方法学描9| MSRA Stage 4 | **MSRA Stage 4** 9保留 | 直接复用到论9Methods |
| Phase 6: 规范合规检查| MSRA Stage 4 | **精简为统计质量检查* 9| 只保9statcheck + anti-patterns |
| Phase 7: 报告组装 | MSRA Stage 4 | **MSRA Stage 4** 9保留 | 9|

**精简后的 Stage 4 流程**9```
Phase 1: 结果解读（不变）
  9Phase 3: 表格生成 + 导出（不变）
  9Phase 4: 图表生成（不变）
  9Phase 5: 方法学描述（不变9  9Phase 6: 统计质量检查（精简版）
  9statcheck_rules: NHST 结果一致性验证（保留9  9anti-patterns: 统计反模式检查（保留9  9quality_checklist: 9 维度质量检查（保留统计方法/结果报告维度9  9移除: CONSORT/STROBE 全文合规检查9Paper Track Stage 5.0
  9Phase 7: 报告组装（不变）
  99STAGE 4 CHECKPOINT ?使用户选择 [A] 结束 / [B] 继续 Paper Track
```

### 4.7 不改动的部分（明确边界）

- ?不改 MSRA 9Stage 1-3 及其 skill（data-prep / analysis-plan / analysis-exec9- ?不改 MSRA 9`shared/` 目录已有内容
- ?不改 medical-paper 9paper_config_agent.md 外的任何文件
- ?不改 medical-paper-reviewer / systematic-survey 的主体逻辑
- ?不改 MSRA 9passport schema 已有字段（只扩展，不修改9
---

## 5. Stage 5.0 Paper Intake 详细设计

Stage 5.0 9MSRA Core 9Paper Track 的转换枢纽，合并了原 bridge skill 9翻译逻辑9MSRA intake 的预填逻辑9
### 5.1 输入

- MSRA passport（已验证 Stage 1-4 全部 completed9- MSRA 产物：final_report.md + figures/*.png + tables/*.docx + SAP.md
- MSRA Stage 3.5 门闸报告
- MSRA Phase 1 文献对比（如有）

### 5.2 工作流程

```
Step 1: 产物校验
  99passport，确9Stage 4 status == "completed"
  9校验: final_report.md 存在 + 至少 1 9figure + 至少 1 9table
  9失败 ?提示用户先完9Stage 4

Step 2: 生成 MSRA Handoff Bundle
  99passport + SAP + final_report 提取字段
  9写入 MSRA/msra_handoff_bundle.md

Step 3: 报告规范选择
  ?基于 study_type 自动推荐（RCT→CONSORT, 观察性→STROBE, ...9  ?展示推荐规范 + 检查清单概9  ?使用户确认（可覆盖9
Step 4: 期刊模板选择
  ?添加载 shared/journal-templates/ 可用模板
  9[0] 自由格式 / [1-5] 预置 / [6] 自定9  ?使用户选择

Step 5: 论文配置确认
  9预填项：RQ / Discipline / Method / Existing Materials / Citation(Vancouver)
  9待确认项：Target Journal / Output Format / Language / Co-Authors / Funding
  ?调用 medical-paper intake（传9MSRA Handoff Bundle9```

### 5.3 字段映射表（MSRA 产物 9Handoff Bundle 9medical-paper intake9
| medical-paper intake 字段 | 来源（MSRA9| 默认9|
|---|---|---|
| Topic / Research Question | `passport.study_type` + SAP.md 研究问题章节 | 9SAP 提取 |
| Discipline | 推导9study_type（RCT/观察性→临床医学；诊断→诊断试验9| `medicine` |
| Paper Type | 实证研究默认 | `IMRaD` |
| Target Journal | Phase 2.5 期刊选择（如有） | `General` |
| Citation Format | 医学默认 | `Vancouver` |
| Output Format | | `Markdown` |
| Body Language | 跟随 MSRA 报告语言 | `Bilingual` |
| Existing Materials | 9Data/Results（final_report + figures + tables9| 全部勾9|
| Reporting Guideline | study_type 9CONSORT/STROBE/STARD | 自动推荐 |

---

## 6. 错误处理

| 场景 | 处理 |
|---|---|
| **用户无数据处理需求，直接要求写论9* | **拒绝进入本插件，提示"纯写作请直接使用 MSRA 9medical-paper / medical-pipeline"** |
| passport.json 不存9| 提示"未找9MSRA 项目，请先在项目目录运行 /msra" |
| Stage 4 报告产物缺失 | 提示"报告未生成，请先运行 /msra-report" |
| figures/ 9tables/ 为空 | 警告但不阻断（用户可能只要文字报告） |
| MSRA skill 9shared/ 文件缺失 | 提示运行 install.ps1 9MSRA 合并步骤 |
| study_type 无法推导 Discipline | 默认 medicine，让用户9intake 确认时改 |
| Bibliography 为空 | 正常——Stage 5.1 systematic-survey 会补检查|
| 用户9Stage 4 9[B] 9MSRA 依赖缺失 | 提示缺失文件清单，引导运9install.ps1 |
| Stage 5.1 Literature Search 用户已有文献 | intake Step 8 可标?已有文献"，跳过或精简检查|
| MSRA Phase 1 无文献对比产9| Stage 5.1 正常从零检索，标注"9MSRA seed" |
| CONSORT/STROBE 检查清单文件缺9| 搜索网上最新版（WebSearch），生成临时清单 |
| shared/ 文件命名冲突 | 合并时检测，冲突文件放入 `shared/MSRA/` 子目9|

---

## 7. 测试策略

- **冒烟测试 1（Report Only 轨）**：完整跑 Stage 1-4，在 checkpoint 9[A]9  验证统计报告正确生成、pipeline 正常结束- **冒烟测试 2（Full Paper 轨）**：完整跑 Stage 1-4，9[B]9  验验证a) Handoff Bundle 生成 (b) Paper Intake 预填正确
  (c) medical-paper 能读9bundle (d) 完整跑通到 Stage 69- **拒绝场景测试**：用户无数据处理需求，直接要求"写论99  验证 pipeline 拒绝进入并提示使9MSRA 原生 skill9- **融合点测9*9  - 融合9B：验9Stage 3.5 门闸报告9Stage 5.5 引用
  - 融合9C：验9MSRA 文献 seed 传入 systematic-survey
  - 融合9D：验证论9Methods 章节引用 MSRA 方法学描9  - 融合9F：验证论9Results 直接引用 MSRA tables/figures
- **缺失场景测试**：删9passport / 删掉 figures，验证错误提示9- **路径检查*：MSRA skill 里所9`shared/` 引用在合并后都能正确解析9- **回归测试**：MSRA Stage 1-4 9test-prompts.json 仍通过（零侵入）9
---

## 8. 实施顺序

1. **合并 MSRA shared/ 依赖**进项9`shared/`
   （上954 个文9+ `.claude/CLAUDE.md` + `commands/`9   - 检查命名冲突，冲突文件放入 `shared/MSRA/`
   - MSRA skill 中对应的引用路径做一次性替92. **精简 MSRA Stage 4**
   - 移除 Phase 2（报告规范选择）和 Phase 2.5（期刊模板选择9   - Phase 6 精简为统计质量检查（保留 statcheck + anti-patterns + quality_checklist 统计维度9   - 9Stage 4 末尾添加 CHECKPOINT 决策节点
3. **扩展 MSRA pipeline skill**
   - 新增 Stage 5.0-5.9 的调度逻辑（Paper Track9   - Stage 4 checkpoint 9[A] 结束 / [B] 继续 Stage 5.0
   - Stage 5.x 调度 medical-paper / medical-paper-reviewer / systematic-survey
   - Handoff Bundle 生成逻辑
4. **扩展 MSRA passport schema**
   - 增加 `track` 字段9MSRA 阶段追踪
5. **9medical-paper paper_config_agent.md**
   - 9MSRA Handoff Detection 分支
   - 激9clinical Domain Evidence Profile
   - 引入 MSRA 报告规范9compliance check
6. **manifest.json 更新**
   - 移除 `/msra-write` 命令（bridge 废除9   - 更新 `/msra` 命令描述（反映统一 Pipeline97. **install.ps1 更新**
   - 9MSRA shared 合并步骤
8. **冒烟测试 + 回归测试**

---

## 9. 风险

| 风险 | 影响 | 缓解 |
|---|---|---|
| 用户无数据需求误入本插件 | 流程走不通，浪费时间 | Stage 1 入口9Stage 4 checkpoint 均有守卫检查；明确文档定位 |
| MSRA 上游更新9shared/ 结构变化 | MSRA skill 引用失效 | 合并时记录上9commit hash；手动重新合9+ diff 检查|
| 统一 Pipeline skill 过于庞大 | 维护复杂度上9| Pipeline skill 仍保9orchestrator 架构，不混入实质工作 |
| Stage 4 精简后用户仍需期刊模板 | 工作流断9| Paper Track Stage 5.0 必须在第一步就提供期刊模板选择 |
| CONSORT 检查清单版本过9| 报告合规不准9| Stage 5.0 检测缺失清单时自动 WebSearch 最新版 |
| 9paper_config_agent.md 与上9MSRA 冲突 | 未来同步 MSRA 时冲9| 用清晰注释标9`# [MSRA-BRIDGE]` 区块，便9rebase |
| shared/ 合并后目录膨胀 | 可读性下9| MSRA 文件9MSRA 文件天然无命名冲突；如未来冲突则9`shared/MSRA/` 子目9|

---

## 10. 开放问题（实施时再定）

- MSRA Handoff Bundle 放在 `MSRA/` 还是项目根——倾向 `MSRA/` 9passport 同目录9- Stage 5.1 Literature Search 是否提供"跳过"选项（用户已有文献时）——倾向提供9- Stage 5.2 论文写作9Methods 章节9直接引用 MSRA 方法学描?还是"基于 MSRA
  重新生成学术论文风格9Methods"——倾向前者，如学术风格不足可手动调整9- Pipeline skill 9Paper Track 调度是否复用 `medical-pipeline` skill 9  orchestrator 逻辑（Mode A），还是自己9MSRA pipeline skill 里重新实现—9  倾向前者（复用 medical-pipeline 的状态机），后者导致重复代码9- 上游 MSRA 更新后的合并策略——是手动 git merge 还是脚本辅助 diff——倾向先手动，
  积累经验后考虑自动化9
---

## 附录 A：版本变更记9
### v1 9v2

| 变更9| v1 | v2 | 理由 |
|--------|-----|-----|------|
| 整体架构 | MSRA pipeline + bridge + MSRA pipeline | 统一 Pipeline（MSRA Core + Paper Track9| 减少用户认知负担 |
| Bridge skill | `skills/msra-to-MSRA/SKILL.md` | **废除**，逻辑内化9pipeline | 单一入口更自9|
| Stage 4 分叉 | 无（Stage 4 是终点） | Stage 4 checkpoint: [A] 结束 / [B] Paper Track | 用户明确意图 |
| 报告规范位置 | MSRA Stage 4 Phase 2 + Phase 6 | Paper Track Stage 5.0 | CONSORT 全文合规是发表级需9|
| 期刊模板位置 | MSRA Stage 4 Phase 2.5 | Paper Track Stage 5.0 | 只有写论文才选期9|
| Passport | MSRA passport（只读）+ MSRA 独立 passport | 统一扩展 passport | 一套追踪系9|
| 临床报告规范 | MSRA 独有，MSRA 9| Paper Track 继承 MSRA 规范 | MSRA 原生无此能力 |
| 文献对比 | MSRA 产出后被丢弃 | 作为 MSRA 文献检查seed | 融合9C |
| 方法学描9| 可能被重新生9| 直接复用 | 融合9D |
| 表格图表 | 可能被重新生9| 直接复用 | 融合9F |

### v2 9v3

| 变更9| v2 | v3 | 理由 |
|--------|-----|-----|------|
| 项目定位 | MSRA 引入 MSRA 作为第三9| 融合为新项目 | 用户确认不需要协议隔9|
| shared/ 获取 | `third_party/` vendor + junction `shared_MSRA` | 直接合并9`shared/` | 融合项目无需物理隔离 |
| 协议声明 | ATTRIBUTION.md + LICENSE-MSRA + NOTICE.md + README 章节 | 全部移除 | 新项目统一协议 |
| 路径适配 | shared/→shared_MSRA/ 批量替换 + junction | 无需替换（自然指向） | 合并后路径不9|
| install.ps1 | vendor 下载 + junction 创建 | shared 文件复制/合并 | 简化安装流9|
| 错误处理 | junction 失效、ATTRIBUTION 缺失 | shared 文件缺失、命名冲9| 场景更简9|
| 风险 | CC BY-NC 4.0 限制商用、junction 失效 | 上游更新合并冲突、目录膨胀 | 风险更少 |

### v3 9v4

| 变更9| v3 | v4 | 理由 |
|--------|-----|-----|------|
| 定位 | 统一 Pipeline，无明确适用边界 | **仅限数据处理场景** | 纯写作用户不应走本插件，应直接用 MSRA |
| 成功标准 | 5 9| 6 条（新增96 条数据驱动定位） | 强化插件边界 |
| 非目9| 5 9| 6 条（新增"不替9MSRA 通用写作"9| 避免功能重叠 |
| Pipeline 9| 无守9| Stage 4 checkpoint 后加**守卫检查* + Stage 5.0 前置条件 | 阻止无数据用户进9Paper Track |
| 错误处理 | 无此场景 | 新增"用户无数据处理需9拒绝9| 明确拒绝逻辑 |
| 测试策略 | 无此场景 | 新增"拒绝场景测试" | 验证守卫生效 |
| 风险 | 无此风险 | 新增"用户无数据需求误9 | 提前防范误用 |
