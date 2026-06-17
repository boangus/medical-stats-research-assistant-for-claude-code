# 设计文档：MSRA × ARS 整合（数据统计 → 学术写作全流水线）

- **日期**: 2026-06-17
- **状态**: 待审批
- **作者**: boangus（经 brainstorming 流程）
- **关联上游**: [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) v3.12.1 (commit `88fc003`, 2026-06-17)

---

## 1. 目标

把 ARS（Academic Research Skills）的"研究→写作→评审→修订→定稿"能力接进 MSRA，
使用户在 MSRA 完成"数据清洗→分析计划→执行→报告"后，能无缝进入 ARS 的论文写作与
评审流程，形成**从原始数据到可投稿论文的完整流水线**。

### 成功标准

1. MSRA 报告阶段（Stage 4 `/msra-report`）完成后，用户可通过新命令把报告产物交给 ARS
   开始写作，**不需要手工搬运文件**。
2. ARS 的 4 个 skill（academic-paper / academic-paper-reviewer / academic-pipeline /
   deep-research）能**端到端跑通**——即它们引用的 `shared/` 依赖全部就位、不报缺失。
3. ARS 的 CC BY-NC 4.0 协议与 MSRA 的 MIT 协议**物理隔离、清晰声明**，不产生协议混淆。
4. 整合对 MSRA 现有 6 个 skill（data-prep / analysis-plan / analysis-exec / report /
   pipeline / calibration）**零侵入**。

### 非目标（YAGNI）

- 不在 MSRA 内实现文献检索（那是 ARS `deep-research` 的职责；MSRA 产物不含 Bibliography）。
- 不做 ARS 的中文化——ARS 保持英文，桥接时中英混排由 academic-paper 的语言设置处理。
- 不做自动升级机制（上游 ARS 更新时手动重新 vendor，记录版本号）。
- 不改 MSRA 的 pipeline skill 去耦合 ARS（桥接是独立 skill，pipeline 不感知 ARS）。

---

## 2. 关键决策（已与用户确认）

| 维度 | 决策 | 理由 |
|---|---|---|
| 整合范围 | **完整 ARS 流水线** | 用户要 research→write→review→revise→finalize 全打通 |
| 桥接方式 | **独立桥接 skill** | MSRA 与 ARS 都不改主体，单一 skill 负责翻译与唤起 |
| shared/ 获取 | **Vendor 拷贝 + 双协议声明** | 单仓库自包含、安装简单；用 NOTICE + third_party/ 隔离协议 |
| intake 识别 | **ARS intake 加 MSRA 分支** | 字段更准确（携带 figures/tables），代价仅改 1 个 agent 文件 |

---

## 3. 现状分析（为什么需要做这些事）

### 3.1 ARS skill 本地已有但"半成品"

`skills/` 下已有 4 个 ARS skill（git 未跟踪 `??` 状态），其内部 `agents/ references/
templates/ examples/` 齐全，版本较新：

| skill | 本地版本 | 上游 v3.12.1 |
|---|---|---|
| academic-paper | v3.2.0 | ✅ |
| academic-paper-reviewer | v1.10.0 | ✅ |
| academic-pipeline | v3.12.1 | ✅ |
| deep-research | v2.10.0 | ✅ |

### 3.2 缺口：约 54 个 `shared/` 文件 + `.claude/CLAUDE.md` + commands

这 4 个 skill 在运行时引用 `shared/` 下的依赖文件，而 MSRA 仓库的 `shared/` 是医学统计
专用目录（statistics-methods / reporting-guidelines 等），**不含任何 ARS 依赖**。引用扫描
发现有约 40 处 `shared/...` 引用（去重后指向约 30 个不同文件，上游实际提供 54 个 shared
文件）全部指向本地不存在的文件，典型如：

- `shared/handoff_schemas.md`（跨 skill 数据契约，9 个 schema）
- `shared/collaboration_depth_rubric.md`
- `shared/references/intent_clarification_protocol.md`
- `shared/compliance_checkpoint_protocol.md`
- `shared/contracts/` 下 7 个子目录（passport/ submission/ writer/ reviewer/ patch/ audit/ evaluator/）
- `.claude/CLAUDE.md`（Routing Discipline v3.9.2 的所在地，被每个 ARS skill 顶部引用）

**结论**：不补齐这些依赖，ARS 端到端跑不起来；单纯写桥接 skill 也无效。

### 3.3 MSRA 有现成的产物追踪机制可复用

MSRA 的 `shared/passport/passport_schema.md` 定义了 Material Passport（灵感本身来自 ARS），
记录每个 stage 的产物路径、hash、status、`study_type`。这是桥接 skill 的**权威数据源**——
桥接读 passport 即可定位所有报告产物，无需约定新文件位置。

---

## 4. 架构

### 4.1 总体数据流

```
[ MSRA 流水线 ]                                    [ ARS 流水线 ]
原始数据                                           ┌─ Stage 1: research (deep-research)
  │                                               │      ↑ 跳过（MSRA 已有数据与结果）
  ├─ Stage 1: data-prep                          │
  ├─ Stage 1.5: 数据质量门闸                       │
  ├─ Stage 2: analysis-plan ──→ SAP.md ──────┐    ├─ Stage 2: write (academic-paper)
  ├─ Stage 2.5: SAP 质量门闸                   │    │      ↑ intake 检测 MSRA Handoff Bundle
  ├─ Stage 3: analysis-exec ──→ 分析结果 ──┐  │    │        → 自动预填配置、跳过 literature search
  ├─ Stage 3.5: 结果质量门闸                 │  │    │
  ├─ Stage 4: report ──→ final_report.md ─┤  │    ├─ Stage 2.5: integrity check
  │                       figures/*.png    │  │    ├─ Stage 3: review (5 reviewers)
  │                       tables/*.docx    │  │    ├─ Stage 4: revise
  │                       方法描述         │  │    ├─ Stage 3': re-review
  │                                       │  │    ├─ Stage 4': re-revise
  │   passport.json (追踪全部产物) ───────┤──┤    ├─ Stage 4.5: final integrity
  │                                       │  │    ├─ Stage 5: finalize (MD/DOCX/PDF)
  └───────────────────────────────────────┘  │    └─ Stage 6: process summary
                                              │
                            ┌─────────────────┘
                            ▼
                   ┌─────────────────────────┐
                   │  skills/msra-to-ars/    │  ← 新建桥接 skill
                   │  读取 passport + 产物    │
                   │  翻译 → MSRA Handoff     │
                   │  Bundle → 唤起 ARS       │
                   └─────────────────────────┘
```

### 4.2 三大组件

#### 组件 A：`third_party/academic-research-skills/`（vendor 区）

存放 ARS 的运行时依赖，与 MSRA 自身代码物理隔离。

```
third_party/academic-research-skills/
├── ATTRIBUTION.md      ← 署名：作者 Cheng-I Wu、仓库 URL、版本 v3.12.1、commit hash、CC BY-NC 4.0
├── LICENSE-ARS         ← CC BY-NC 4.0 全文（从上游 LICENSE 拷贝）
├── shared/             ← 上游 shared/ 原样拷贝（54 文件）
├── commands/           ← ars-* 斜杠命令
└── .claude/
    └── CLAUDE.md       ← Routing Discipline v3.9.2
```

**协议隔离要点**：
- ARS 文件全部留在 `third_party/` 下，**不合并进 MSRA 的 `shared/`**。
- MSRA 根 `LICENSE`（MIT）不变；新增根 `NOTICE.md` 声明边界。
- 每个 ARS vendored 目录顶层放 `ATTRIBUTION.md` + `LICENSE-ARS`，满足 CC BY-NC 4.0 的署名要求。
- README.md 新增"第三方组件"章节，列出 ARS 来源、版本、协议、非商用限制。

**路径适配问题与解决**：本地 4 个 ARS skill 引用 `shared/...` 是相对仓库根的路径。
vendored 后这些路径指向 `third_party/academic-research-skills/shared/...`。两种解法：

- **方案 P1（选中）**：在 MSRA 仓库根建**符号链接/ junction** `shared_ars` →
  `third_party/academic-research-skills/shared`，并把 ARS skill 里的 `shared/` 引用批量
  改为 `shared_ars/`（脚本一次性替换）。优点：路径稳定、跨平台可建 junction。
- **方案 P2（备选，不推荐）**：直接把 `shared/` 内容合并进 MSRA `shared/`。否决——会污染
  MSRA 的 MIT shared/，破坏协议隔离。

> 注：Windows 用 `mklink /J` 建 junction（不需管理员权限）；Linux/macOS 用 `ln -s`。
> 安装脚本 `install.ps1` 里加 junction 创建步骤。

#### 组件 B：`skills/msra-to-ars/SKILL.md`（桥接 skill，核心交付物）

**职责单一**：读取 MSRA 报告产物 → 翻译成 MSRA Handoff Bundle → 唤起 academic-paper。

**frontmatter**:
```yaml
---
name: msra-to-ars
version: "0.1.0"
description: |
  把 MSRA 的报告产物（final_report + figures + tables + SAP）桥接到 ARS 的论文写作流水线。
  读取 MSRA passport，生成 MSRA Handoff Bundle，唤起 academic-paper（跳过 deep-research）。
  触发: 写论文 / 从报告写论文 / msra to ars / 接力写作 / 转论文 / write paper from report
data_access_level: verified_only
task_type: open-ended
depends_on: [report, academic-paper]
works_with: [academic-paper, academic-pipeline, academic-paper-reviewer]
---
```

**触发与命令**：在 `manifest.json` 新增 `/msra-write` 命令：
```json
"/msra-write": {
  "id": "msra-to-ars-bridge",
  "name": "MSRA to ARS Bridge",
  "entry_point": "skills/msra-to-ars/SKILL.md",
  "description": "把 MSRA 报告产物桥接到 ARS 论文写作",
  "usage": "/msra-write [options]",
  "examples": ["/msra-write", "/msra-write --review", "/msra-write --full-pipeline"]
}
```

**工作流程（3 Phase）**:

```
Phase 1: 产物发现 → 输入: passport.json → 输出: 产物清单 + 完整性校验
  │  读 MSRA/passport.json，定位 stage_4 的 report 类产物
  │  校验：final_report.md 存在 + 至少 1 张 figure + 至少 1 张 table
  │  失败 → 提示用户先跑 /msra-report
  ▼
Phase 2: 翻译 → 输入: MSRA 产物 → 输出: MSRA Handoff Bundle
  │  生成 MSRA_HANDOFF_BUNDLE.md（见下方字段映射表）
  │  路径用绝对/项目相对路径，不复制文件（passport 已追踪 hash）
  ▼
Phase 3: 唤起 → 输入: MSRA Handoff Bundle → 输出: academic-paper 启动
  │  调用 academic-paper skill（full 或 plan 模式）
  │  academic-paper 的 intake_agent 检测到 MSRA Handoff Bundle → 预填配置
  │  [STOP] 用户确认后进入写作
  │
  │  用户可选：
  │  --review         → 写完后接 academic-paper-reviewer
  │  --full-pipeline  → 接 academic-pipeline 跑完整 review/revise/finalize
```

**字段映射表（MSRA 产物 → MSRA Handoff Bundle → academic-paper intake）**:

| academic-paper intake 字段 | 来源（MSRA） | 默认值 |
|---|---|---|
| Topic / Research Question | `passport.study_type` + SAP.md 研究问题章节 | 从 SAP 提取 |
| Discipline | 推导自 study_type（RCT/观察性→临床医学；诊断→诊断试验） | `medicine` |
| Paper Type | 实证研究默认 | `IMRaD` |
| Target Journal | 无（用户填） | `General` |
| Citation Format | 医学默认 | `Vancouver` |
| Output Format | | `Markdown` |
| Body Language | 跟随 MSRA 报告语言 | `Bilingual` |
| Existing Materials | ✅ Data/Results（final_report + figures + tables） | 全部勾选 |
| 数据/结果 | final_report.md Phase 1 结果解读 + tables/*.docx + figures/*.png | 路径引用 |

**MSRA Handoff Bundle 格式**（新文件 `MSRA/msra_handoff_bundle.md`）:
```markdown
# MSRA Handoff Bundle

## Source
- passport_id: msra-20260529-001
- study_type: RCT
- msra_version: 0.7.6

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

## Bibliography
[EMPTY — 由 academic-paper 的 literature_strategist 补充；MSRA 不做文献检索]
```

#### 组件 C：修改 `skills/academic-paper/agents/intake_agent.md`（加 MSRA 分支）

在现有"Deep Research Handoff Detection"（约第 23-64 行）之后，新增并列的
"MSRA Handoff Detection"分支。**只改这 1 个 agent 文件，不动 academic-paper 的其他部分**。

新增逻辑：
```markdown
## MSRA Handoff Detection

### Detection Logic（在 Deep Research 检测之后执行）

1. 检查对话上下文或工作目录是否存在 `MSRA_HANDOFF_BUNDLE.md`
2. 识别标记（任一命中即触发）：
   - 文件头含 `# MSRA Handoff Bundle`
   - passport_id 字段（格式 msra-YYYYMMDD-NNN）
   - 由 msra-to-ars skill 唤起（前置 skill 标记）

### When MSRA Handoff Is Detected

1. 自动预填（从 bundle 读取）：
   - RQ ← bundle 的 Research Question
   - Discipline ← bundle 的 study_type 推导（默认 medicine）
   - Method ← bundle 的 Methods Summary
   - Existing Materials ← 全部勾选 Data/Results
   - Citation Format ← Vancouver（医学默认）
   - Paper Type ← IMRaD

2. 跳过冗余问题：
   - 跳过 Step 1（Topic & RQ）
   - 跳过 Step 8（Existing Materials）
   - 仍需确认：Target Journal、Output Format、Language、Co-Authors、Funding

3. Bibliography 特殊处理：
   - MSRA 不提供文献 → literature_strategist 正常运行 Phase A 检索
   - 在 Paper Configuration Record 标注：Bibliography source = ARS（非 MSRA）

4. 通知用户：
   "检测到 MSRA 报告产物。已自动填充：研究问题、学科、研究方法、数据/结果材料。
    还需确认：目标期刊、输出格式、语言、作者、基金信息。"
```

### 4.3 不改动的部分（明确边界）

- ❌ 不改 MSRA 的 6 个核心 skill（data-prep / analysis-plan / analysis-exec / report /
  pipeline / calibration）
- ❌ 不改 MSRA 的 `shared/` 目录
- ❌ 不改 academic-paper 除 intake_agent.md 外的任何文件
- ❌ 不改 academic-paper-reviewer / academic-pipeline / deep-research
- ❌ 不改 MSRA 的 passport schema（只读取，不写入）

---

## 5. 错误处理

| 场景 | 处理 |
|---|---|
| passport.json 不存在 | 提示"未找到 MSRA 项目，请先在项目目录运行 /msra" |
| Stage 4 报告产物缺失 | 提示"报告未生成，请先运行 /msra-report"，列出缺失文件 |
| figures/ 或 tables/ 为空 | 警告但不阻断（用户可能只要文字报告） |
| ARS skill 的 shared/ 引用解析失败（junction 未建） | 提示重新运行 install.ps1 的 ARS 步骤 |
| study_type 无法推导 Discipline | 默认 medicine，让用户在 intake 确认时改 |
| Bibliography 为空 | 正常——academic-paper 的 literature_strategist 会补检索 |

---

## 6. 测试策略

- **冒烟测试**：在一个示例 MSRA 项目（passport + final_report + figures + tables）上跑
  `/msra-write`，验证：(a) 产物发现正确 (b) Handoff Bundle 生成 (c) academic-paper 能
  读到 bundle 并预填配置。
- **缺失场景测试**：删掉 passport / 删掉 figures，验证错误提示符合预期。
- **协议检查**：确认 `third_party/` 下所有文件都有 ATTRIBUTION + LICENSE-ARS，MSRA 根
  LICENSE 仍是 MIT。
- **路径检查**：ARS skill 里所有 `shared_ars/` 引用都能解析到 `third_party/.../shared/`。
- **回归**：MSRA 原有 6 个 skill 的 test-prompts.json 仍通过（证明零侵入）。

---

## 7. 实施顺序（高层）

1. Vendor ARS 依赖到 `third_party/academic-research-skills/`（shared/ + .claude/ +
   commands/）+ ATTRIBUTION + LICENSE-ARS
2. 建路径适配（junction + ARS skill 内 shared/→shared_ars/ 批量替换）
3. 写根 NOTICE.md + README 第三方组件章节
4. 写 `skills/msra-to-ars/SKILL.md`
5. 改 `skills/academic-paper/agents/intake_agent.md` 加 MSRA 分支
6. manifest.json 加 `/msra-write` 命令
7. install.ps1 加 ARS vendor + junction 步骤
8. 冒烟测试 + 回归测试

（详细步骤交由 writing-plans 拆解。）

---

## 8. 风险

| 风险 | 影响 | 缓解 |
|---|---|---|
| ARS 上游更新后 shared/ 路径变化 | 桥接失效 | ATTRIBUTION.md 锁定 commit hash；手动重新 vendor |
| CC BY-NC 4.0 限制商用 | 用户商用 MSRA 时受限 | NOTICE.md + README 明确标注 third_party 区域为非商用 |
| Windows junction 在某些环境失效 | 路径解析失败 | install.ps1 提供降级（手动复制 + 路径替换脚本） |
| 改 intake_agent.md 与上游 ARS 冲突 | 未来同步 ARS 时冲突 | 用清晰注释标记 `# [MSRA-BRIDGE]` 区块，便于 rebase |
| Bibliography 为空导致 academic-paper Phase A 检索质量 | 文献覆盖不全 | intake 明确告知用户文献由 ARS 补，建议用户复核 |

---

## 9. 开放问题（实施时再定）

- `shared_ars` junction 名 vs 直接在 ARS skill 里改路径——实施时验证哪种更稳。
- MSRA Handoff Bundle 是放在 `MSRA/`（运行时目录）还是项目根——倾向 `MSRA/` 与
  passport 同目录。
- 是否需要 `/msra-write` 的 `--dry-run`（只生成 bundle 不唤起 ARS）——倾向加，便于调试。
