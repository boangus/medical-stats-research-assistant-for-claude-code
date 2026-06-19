---
version: "0.8.0"
name: MSRA Pipeline
description: |
  医学统计分析 + 学术写作统一流水线编排器。从任意阶段切入，自动识别当前位置，
  引导完成后续所有流程。Stage 4 完成后可选择继续 Paper Track（论文写作）。
  纯调度架构——不做实质性工作，只负责检测、选择、调度、转换和追踪。
  输出: 完整流水线（Stage 1-4 统计分析 + Stage 5-6 论文写作）+ 3个阻断式门闸
  + 最终报告(figures/*.png + tables/*.docx + HTML+MD) + 可选论文。
  触发: /msra / 流水线 / pipeline / 数据分析流程 / 统计流程 / 完整流程 / 从头开始 / 数据清洗 / 统计分析 / 分析报告 / 结果解读 / 统计咨询 / orchestrator / 编排 / 调度 / 质量门闸
data_access_level: redacted
task_type: open-ended
depends_on: [data-prep, analysis-plan, analysis-exec, report, calibration, academic-pipeline, academic-paper, academic-paper-reviewer, deep-research]
works_with: [agents/AGENTS.md, shared/passport/passport_schema.md, .claude/CLAUDE.md]
author: "MSRA Team"
license: "MIT"
min_claude_version: "3.5"
tags: [medical-statistics, clinical-trial, pipeline, orchestrator, quality-gate]
---

# MSRA Pipeline Orchestrator

> **IRON RULE**: You are an orchestrator, NOT a worker. You do NOT perform
> substantive statistical work yourself. Your only job is to detect where the
> user is, recommend the right skill/mode, dispatch, and track progress.

---

## 1. Pipeline Stages

```
原始数据 → 研究类型识别（RCT / 观察性）
   │
   ▼
┌──────────────────────────────────────────────────────────────┐
│  Stage 1: DATA PREP  (/msra-data)                            │
│  数据验证 → 交互式清洗 → 值规范化(新增) → EDA(数据质量)       │
│  → 盲态审核 → 数据库锁定                                     │
│  [RCT] 启用盲法审核 / [观察性] 启用混杂评估                  │
│  值规范化: TCM术语变体(GB/T 16751)+数值格式变体[ADAPTIVE]    │
└────────────────────────────┬─────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────┐
│  🔴 Stage 1.5: DATA QUALITY GATE  (阻断式检查)               │
│  9 项检查 → ❌退回 Stage 1 / ✅进入 Stage 2                  │
└────────────────────────────┬─────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────┐
│  Stage 2: ANALYSIS PLAN  (/msra-plan)                        │
│  Estimands(估计目标) → 方法探讨 → SAP → 审查 → 定稿         │
│  [RCT] ITT/PP 人群 + ANCOVA 为主                             │
│  [观察性] DAG/混杂控制 + PSM/多变量为主                      │
└────────────────────────────┬─────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────┐
│  🔴 Stage 2.5: SAP QUALITY GATE  (阻断式检查)                │
│  + 变量构造逻辑检查（确保 SAP 中分析变量的构造逻辑已定义）     │
│  ❌退回 Stage 2 / ✅进入 Stage 3                             │
└────────────────────────────┬─────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────┐
│  Stage 3: ANALYSIS EXEC  (/msra-exec)                        │
│  样本量验证 → 变量构造(按SAP) → 执行前检查                    │
│  → 描述性统计(Table 1) → 依从性分析 → 主要分析               │
│  → 敏感性分析 → 安全性分析 → 亚组分析 → 假设检验 → 质检     │
└────────────────────────────┬─────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────┐
│  🔴 Stage 3.5: RESULTS QUALITY GATE  (阻断式检查)            │
│  9 项检查 → ❌退回 Stage 3 / ✅进入 Stage 4                  │
└────────────────────────────┬─────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────┐
│  Stage 4: REPORT  (/msra-report)                             │
│  结果解读 → 表格/图表 → 方法学描述 → 统计质量检查 → 报告组装   │
│  输出: final_report.md + final_report.html + figures/*.svg   │
│        + figures/*.png + tables/*.docx                        │
│  ★ STAGE 4 CHECKPOINT: [A] 结束 / [B] Paper Track            │
└────────────────────────────┬─────────────────────────────────┘
                             ▼
          ┌────────────────────────────────────────────┐
          │ ★ STAGE 4 CHECKPOINT (MANDATORY-M4')       │
          │ [A] 统计报告完成，结束 → track=report_only  │
          │ [B] 继续写论文 → Paper Track               │
          │     守卫检查: final_report + figures/tables │
          └───────┬──────────────────┬────────────────┘
                  │                  │
            [A] ↓                    ↓ [B]
         ═════════════      ┌─────────────────────────────────┐
         │  Pipeline 结束   │  Stage 5.0: PAPER INTAKE        │
         │  (report_only)   │  Handoff Bundle + 论文配置      │
         ═════════════      └──────────────┬──────────────────┘
                                           ▼
                            ┌─────────────────────────────────┐
                            │  Stage 5.1: LITERATURE SEARCH   │
                            │  文献检索 + 综述撰写            │
                            └──────────────┬──────────────────┘
                                           ▼
                            ┌─────────────────────────────────┐
                            │  Stage 5.2: PAPER WRITING       │
                            │  IMRaD 章节撰写                 │
                            └──────────────┬──────────────────┘
                                           ▼
                            ┌─────────────────────────────────┐
                            │  🔴 Stage 5.5: INTEGRITY CHECK  │
                            │  完整性检查（阻断式）            │
                            └──────────────┬──────────────────┘
                                           ▼
                            ┌─────────────────────────────────┐
                            │  Stage 5.6: PEER REVIEW         │
                            │  5人评审团                     │
                            └──────────────┬──────────────────┘
                                           ▼
                            ┌─────────────────────────────────┐
                            │  Stage 5.7: REVISION            │
                            │  修订 + Response to Reviewers   │
                            └──────────────┬──────────────────┘
                                           ▼
                            ┌─────────────────────────────────┐
                            │  Stage 5.8: FINAL INTEGRITY     │
                            │  最终完整性检查（阻断式）        │
                            └──────────────┬──────────────────┘
                                           ▼
                            ┌─────────────────────────────────┐
                            │  Stage 5.9: FINALIZE            │
                            │  定稿导出（MD → DOCX → PDF）     │
                            └──────────────┬──────────────────┘
                                           ▼
                            ┌─────────────────────────────────┐
                            │  Stage 6: PROCESS SUMMARY       │
                            │  完整过程记录                    │
                            └─────────────────────────────────┘
```

---

## 2. Intent Detection & Mid-Entry

当用户发起对话时，通过关键词和上下文自动判断入口阶段：

| 用户信号 | 检测规则 | 入口阶段 | 前置条件 |
|---------|---------|---------|---------|
| "我有原始数据" / 提供数据文件 | 有数据文件路径 | **Stage 1** | 无 |
| "数据已经清洗好了" / 提供清洗后数据 | 声明已清洗 | **Stage 2** | 需确认 Stage 1.5 门闸通过 |
| "我想讨论统计方法" / "该用什么方法" | 方法咨询意图 | **Stage 2** | 需确认 Stage 1.5 门闸通过 |
| "我有分析计划了" / 提供SAP文件 | 有SAP文档 | **Stage 3** | 需审查SAP |
| "分析做完了，帮我检查" | 有分析结果 | **Stage 3** (质检) | 需确认SAP |
| "帮我写报告" / "生成表格" | 报告生成意图 | **Stage 4** | 需确认分析结果 |
| "完整流程" / "从头开始" | 全流程意图 | **Stage 1** | 无 |
| "继续写论文" / "paper track" | Paper Track 意图 | **Stage 5.0** | 需确认 Stage 4 已完成 + passport.track == full_paper |
| 提供论文要求review | 审稿意图 | **Stage 3** (质检) | 需先验证数据完整性 |

### Mid-Entry 前置检查

进入任何阶段前，必须确认前置产物是否存在且有效。
使用 **Material Passport** (shared/passport/passport_schema.md) 追踪产物生命周期：

```
进入 Stage 1.5 之前  → 确认: 清洗后数据 + 清洗日志 + 盲态审核记录 + 数据库锁定记录
进入 Stage 2 之前     → 确认: 清洗后数据 + 清洗日志 + Stage 1.5 门闸通过
进入 Stage 2.5 之前   → 确认: 已批准的SAP
进入 Stage 3 之前     → 确认: Stage 2.5 通过 + 已批准的SAP
进入 Stage 3.5 之前   → 确认: 分析结果 + 质检报告
进入 Stage 4 之前     → 确认: Stage 3.5 通过 + 分析结果
```

**Passport 检查流程**：
1. 读取 `MSRA/passport.json`，检查各产物状态
2. 产物状态: `planned` → `in_progress` → `completed` → `verified` → `consumed`
3. 前置产物必须为 `verified` 或 `consumed` 才允许进入下一阶段
4. 若 passport.json 不存在，提示用户初始化或从现有产物重建

**IRON RULE**: 如果前置产物缺失或过期，必须先回退补齐，不能跳过。

---

## 2.1 研究类型识别

在确定入口阶段后，自动识别或询问研究类型。后续所有 Stage 按类型分支执行不同逻辑。

| 用户信号 | 检测规则 | 研究类型 |
|---------|---------|---------|
| "RCT" / "随机对照" / "randomized" / "随机" | 关键词匹配 | **RCT** |
| "队列" / "cohort" / "观察性" / "observational" | 关键词匹配 | **观察性** |
| "病例对照" / "case-control" | 关键词匹配 | **观察性** |
| "诊断" / "diagnostic" / "诊断试验" | 关键词匹配 | **诊断试验** |
| 未明确说明 | 询问用户 | 由用户指定 |

**研究类型对 Pipeline 的影响**：

| 维度 | RCT | 观察性 | 诊断试验 |
|------|-----|--------|---------|
| 数据准备 | 启用盲态审核 | 启用混杂偏倚评估 | 启用金标准验证 |
| 分析计划 | ITT/PP 人群、ANCOVA 为主 | DAG/PSM/多变量调整 | AUC/敏感度/特异度 |
| 质量门闸 | 检查随机化隐藏 | 检查混杂控制 | 检查金标准偏倚 |
| 报告规范 | CONSORT | STROBE | STARD |
| 敏感性分析 | 偏离 ITT 的敏感性 | E-value / 未测量混杂 | 不同切点的分析 |

**入口响应格式**（研究类型识别 + 交互模式 + 语言选择后输出）：
```
── Pipeline Orchestrator ──
检测到: 研究类型=RCT | 入口=Stage 1 (原始数据)
前置检查: 无前置产物，从 Stage 1 开始

交互模式: [1] 详细引导 [2] 高效模式
分析语言: [1] R (推荐) [2] Python

输入编号或描述需求:
```

---

## 2.5 用户类型与交互密度预判

在确定入口阶段后，询问用户期望的交互密度。此后按对应模式自动调整 Checkpoint 密度，无需每个决策点都问一遍。

**入口处提示**：
```
选择交互模式：

[1] 详细引导
    每个关键步骤都会暂停与你确认：数据清洗策略、变量筛选、参数定义、
    方法选择、协变量调整、敏感性分析等，全部在对话中逐一讨论。
    适合：首次分析、对统计方法不熟、数据质量不确定、需要严格把控。

[2] 高效模式（推荐）
    全程自动推进，仅在质量门闸（4个阻断点）暂停。
    统计参数直接使用默认值，方法选择基于数据特征自动推荐。
    如需修改，可在 SAP 文档中调整后重新生成。
    适合：熟悉流程、标准分析、赶时间。
```

| 用户选择 | Checkpoint 密度 | 适用场景 |
|---------|----------------|---------|
| **[1] 详细引导** | MANDATORY + SLIM + 协作深度观察 | 首次分析、对统计方法不熟、数据质量不确定、需要严格把控 |
| **[2] 高效模式** (默认) | MANDATORY 仅门闸暂停，其余自动推进 | 熟悉流程、标准分析、赶时间 |

**模式内行为**：
- 详细引导：每个决策点暂停，展示选项供用户选择
- 高效模式：使用默认参数自动推进，仅在异常时提问
- 用户可在 SAP 文档中修改参数后，说"重新执行"即可
- 用户说"继续吧别问太细" → 切换至高效模式
- 用户说"这块你定就行" → 该 Checkpoint 降级为仅记录，不询问

---

## 2.6 分析语言选择

在确定交互模式后，询问用户期望的分析语言。此后全程使用该语言生成代码、执行分析和输出结果。

**入口处提示**：
```
选择分析语言：

[1] R (推荐)
    使用 R 语言进行统计分析。
    优势：统计方法丰富、医学统计生态成熟、gtsummary/flextable 生成三线表、
          survival 包做生存分析、WeightIt 做因果推断。
    适合：临床研究、生存分析、因果推断、需要专业统计包。

[2] Python
    使用 Python 语言进行统计分析。
    优势：机器学习生态强大、Pandas 数据处理灵活、Plotly 交互式可视化。
    适合：大数据分析、机器学习、需要与其他 Python 工具链集成。
```

| 用户选择 | 默认包 | 适用场景 |
|---------|--------|---------|
| **[1] R** (默认) | survival, survey, WeightIt, gtsummary, flextable | 临床研究、生存分析、因果推断 |
| **[2] Python** | pandas, numpy, scipy, scikit-learn, lifelines | 大数据、机器学习、Python 工具链 |

**语言影响**：
- **Stage 3**: 生成对应语言的分析代码
- **Stage 4**: 使用对应语言的包生成表格和图表
- **模板**: 使用 `shared/templates/` 下对应的语言模板

---

## 3. Stage Dispatching

每个 Stage 调用对应的 Skill，并选择最佳 Mode：

### Stage 1: DATA PREP
- **Skill**: `data-prep`
- **Mode 匹配**:
  - 用户说"帮我清洗数据" → `guided` (交互式)
  - 用户说"快速检查一下" → `quick` (快速验证)
- **研究类型分支**:
  - RCT → 启用盲态审核、随机化检查
  - 观察性 → 启用混杂偏倚评估、数据源描述
- **输入**: 原始数据文件路径（单文件或多文件目录）
- **输出**: 清洗后数据 + 清洗日志 + EDA报告(数据质量) + 验证报告 + 盲态审核记录 + 数据库锁定记录
- **🆕 多数据集模式**: 输入为目录（含多个 CSV）时自动进入 multi-dataset 模式，逐文件验证 + 跨中心一致性检查（Phase 1b）
- **子步骤**:
  0. **数据画像**（Quick Profile）：自动生成数据概览——变量数、样本量、变量类型分布、缺失率排名 Top10、数值变量概要（min/max/mean/median/sd）、分类变量层级数、时间跨度。[SLIM] 展示后继续（极端情况如缺失率>50%或变量数<3 时升级为 MANDATORY）。
  0.5. **多数据集检测**（仅目录输入时）：自动检测多中心数据，激活 multi-dataset 模式
  1. 数据验证（结构、类型、缺失、逻辑、范围）
  1b. **跨中心一致性检查**（仅 multi-dataset 模式）：变量名/类型一致性、缺失率比较、基线分布差异
  2. 交互式清洗（与用户讨论策略 → 批准 → 执行）
  3. **值规范化**（新增：检测TCM术语变体 + 数值格式变体，用户确认后执行）
  4. EDA 数据质量检查（缺失模式、异常值、分布特征——仅用于数据质量评估，不用于方法选择）
  5. 盲态审核（盲法试验时在盲态下审核数据质疑、脱落、方案偏离）
  6. 数据库锁定（锁定流程确认，避免解锁）
- **Checkpoint**: 无额外确认点。Stage 1 完成后直接进入 Stage 1.5 门闸检查。

### Stage 1.5: DATA QUALITY GATE 🔴（阻断式检查）

> **IRON RULE**: 这是阻断式检查点。Stage 1.5 未通过 → **必须退回 Stage 1 修订**，不得继续进入 Stage 2。

- **Skill**: `data-prep` (复用)
- **Mode**: `quality-gate`（只检查，不修改）
- **输入**: 清洗后数据 + 清洗日志 + 盲态审核记录 + 数据库锁定记录
- **输出**: 数据质量门闸报告（通过/不通过 + 具体问题清单）
- **阻断检查清单 (9 项)**:

  ```
  □ 1. 清洗日志完整: 所有数据变更是否记录在案（变更原因、影响记录数）？
  □ 2. 变量定义明确: 所有衍生变量的构造逻辑是否清晰、可复现？
  □ 3. 缺失机制评估: 是否已评估缺失模式（MCAR/MAR/MNAR）并选择处理策略？
  □ 4. 盲态审核完成: 盲态审核记录完整，无未解决的质疑？
  □ 5. 数据库锁定确认: 锁定版本号和锁定时间已记录？
  □ 6. 逻辑一致性验证: 清洗后数据的关键逻辑关系是否自洽（日期顺序、范围约束）？
  □ 7. 值规范化完成: 所有非标准值是否已规范化并记录？
      - 中医术语变体（后缀变体、同义变体）已检测并规范化（GB/T 16751.2）
      - 数值截断标记（<、>、小于、大于等）已处理
      - 逗号多值已处理
      - 规范化日志完整（含原值、规范值、处理策略、影响记录数）
      - 通过标准: 无遗留非标准值；如含自定义术语已征得用户确认
  □ 8. 可重复性: 清洗脚本是否可独立运行并复现相同结果？
  □ 9. 隐私合规完成: PHI字段是否已检测并脱敏/处理？ 🆕
      - 直接标识字段（姓名、身份证、电话等）已脱敏或删除
      - 准标识符字段（精确日期、邮编等）已泛化处理
      - 自由文本PII已检测并替换
      - 隐私合规分级报告已生成
      - 通过标准: 无未处理的直接标识字段；准标识符已泛化或用户确认接受风险
  ```

  - **全部通过 (9/9)** → ✅ 进入 Stage 2
  - **条件通过 (7-8/9，即 ≤2 项非关键项未通过)** → ⚠️ 记录风险后进入 Stage 2
  - **阻断 (≤6/9 或 关键项 5/6/7/9 任一未通过)** → ❌ **强制退回 Stage 1 修订**
  > 关键项定义：项5(数据库锁定)、项6(逻辑一致性)、项7(值规范化)、项9(隐私合规) 为硬阻断项，不可条件通过。
- **Checkpoint**: [MANDATORY-M1] 门闸通过后进入 Stage 2

### Stage 2: ANALYSIS PLAN
- **Skill**: `analysis-plan`
- **Mode 匹配**:
  - 用户说"帮我制定分析计划" / "讨论统计方法" → `guided` (交互式，逐步讨论 Estimands/方法)
  - 用户说"快速生成SAP" / "我有方法了直接写" → `quick` (快速生成，用户事后审阅)
  - 用户说"我想探索一下数据特征再决定" → `exploratory` (先 EDA 再制定)
- **研究类型分支**:
  - RCT → ITT/PP/Safety 人群定义、ANCOVA 推荐、随机化验证、多重性控制
  - 观察性 → DAG 混杂结构、倾向性评分(PSM/IPTW)推荐、E-value 敏感性分析
  - 诊断试验 → AUC 比较、金标准偏倚评估、切点选择
- **输入**: 清洗后数据 + EDA 数据质量报告 + 研究问题 + 研究类型
- **输出**: 估计目标定义 + 分析方法决策 + 统计分析计划(SAP) + 分析规范表
- **子步骤**:
  1. 深度 EDA（方法选择用，与 Stage 1 EDA 区分）
  1.5. 文献种子检索（3-5 篇核心文献，为方法选择提供实证依据）🆕
  2. 估计目标定义 + 方法探讨（基于研究类型、数据特征和文献种子，与用户讨论方法选择）
  3. 制定 SAP（人群定义、终点、方法、敏感性分析、期中分析、多重性控制）
  4. 计划审查（适当性、有效性、完整性、可行性）
- **🆕 多数据集模式**（仅 multi-dataset 模式）：Phase 6.7 多中心分析计划，制定中心效应处理策略
- **Checkpoint**: 仅 [MANDATORY-M2] SAP 门闸检查。Stage 2 内部无额外确认点。

### Stage 2.5: SAP QUALITY GATE 🔴（阻断式检查）

> **IRON RULE**: 这是阻断式检查点。Stage 2.5 未通过 → **必须退回 Stage 2 修订**，不得继续进入 Stage 3。
> 参考：shared/sap/sap_standard.md — SAP标准格式定义
> 参考：shared/sap/validate_sap.py — SAP验证脚本

- **Skill**: `analysis-plan` (复用)
- **Mode**: `quality-gate`（只检查，不修改）
- **输入**: 已审查的 SAP + EDA 报告
- **输出**: SAP 质量门闸报告（通过/不通过 + 具体问题清单）
- **阻断检查清单 (8 项)**:

  ```
  □ 1. SAP 结构完整: 所有必需章节是否存在？
  □ 2. 研究目标明确: 主要/次要目标是否清晰定义？
  □ 3. 估计目标完整: ICH E9(R1) 五要素是否齐全？
  □ 4. 方法选择合理: 统计方法与研究设计及研究类型(RCT/观察性)是否匹配？
  □ 5. 假设条件验证: 数据特征是否支持所选方法的假设？
  □ 6. 敏感性分析计划: 是否包含足够的敏感性分析？
  □ 7. 变量构造逻辑: 所有分析变量的构造公式、切点、依据是否在SAP中预定义？
  □ 8. 可重复性: SAP 是否足够详细以便独立复现？
  ```

  - **全部通过 (8/8)** → ✅ 进入 Stage 3
  - **条件通过 (6-7/8，即 ≤2 项非关键项未通过)** → ⚠️ 记录偏差后进入 Stage 3
  - **阻断 (≤5/8 或 关键项 3/5/7 任一未通过)** → ❌ **强制退回 Stage 2 修订**
  > 关键项定义：项3(估计目标完整)、项5(假设条件验证)、项7(变量构造逻辑) 为硬阻断项，不可条件通过。
- **Checkpoint**: [MANDATORY-M2] 门闸通过后进入 Stage 3

### Stage 3: ANALYSIS EXEC
- **Skill**: `analysis-exec`
- **Agent 拆分**: Exec Runner (Phase 0-6) + Exec Inference (Phase 7-9)
  - Generator-Evaluator 差异报告作为 Stage 3.5 门闸的输入项之一
- **Mode 匹配**:
  - 用户说"按SAP执行分析" → `sap-guided` (按计划执行)
  - 用户说"先探索一下数据" → `exploratory` (探索性)
- **输入**: 清洗后数据 + 已批准的SAP（含变量构造逻辑）
- **输出**: 分析代码 + 构造后分析数据集 + 描述性统计表 + 依从性分析 + 主要/次要/探索性分析结果 + 安全性分析 + 假设检验报告 + 质检报告
- **子步骤**:
  0. **样本量验证**（新增）：实际可用样本量 vs SAP 计划样本量，不足时标记为 exploratory
  1. **变量构造**（从 Stage 1 移入）：按 SAP 定义的变量构造逻辑生成分析变量
  2. 执行前检查（数据集与 SAP 一致性验证）
  3. 描述性统计（Table 1、分布汇总、受试者分布）
  4. 依从性和合并用药分析
  5. 主要估计目标分析（主估计方法）
  6. 敏感性分析（探索主估计的稳健性）
  7. 次要和探索性估计目标分析
  8. 安全性分析（不良事件、实验室检查、生命体征）
  9. 亚组分析和补充分析
  10. 假设检验（SAP中计划的所有诊断检验）
  11. 质量检查（方法正确性、假设满足、结果合理性、报告完整性）
- **🆕 多数据集模式**（仅 multi-dataset 模式）：Phase 7.7 多中心汇总分析，含森林图 + 异质性检验 + leave-one-out
- **Checkpoint**: 仅 [MANDATORY-ME1] 主要分析结果确认（Phase 6 完成后）。其余阶段无确认点。
- **🆕 SAP Amendment**: Phase 7.5 支持透明的 SAP 修正流程（最多 3 次，详见 analysis-exec/SKILL.md Phase 7.5）

### Stage 3.5: RESULTS QUALITY GATE 🔴（阻断式检查）

> **IRON RULE**: 这是阻断式检查点。Stage 3.5 未通过 → **必须退回 Stage 3 修正**，不得继续进入 Stage 4。

- **Skill**: `analysis-exec` (复用)
- **Mode**: `quality-gate`（只检查，不修改）
- **输入**: 分析结果 + 质检报告 + SAP
- **输出**: 结果质量门闸报告（通过/不通过 + 具体问题清单）
- **阻断检查清单 (14 项)**:

  ```
  □ 1. 结果完整性: 所有 SAP 中计划的分析是否都已执行？
  □ 2. 假设验证: 所有方法的假设条件是否已检验并满足？
  □ 3. 数值一致性: 报告中的关键数字在分析输出中是否一致？
  □ 4. 敏感性分析: 敏感性分析结果是否与主分析一致？
  □ 5. 效应量报告: 是否包含效应量及其置信区间？
  □ 6. 异常结果标记: 是否有异常/意外结果被标记说明？
  □ 7. 结果复现: 3 次重跑关键结论是否一致？（详见 shared/reproducibility/）
  □ 8. [SKIP] 标记: 跳过的分析是否有合理记录？
  □ 9. [校准联动] 校准置信度: 该方法类型的历史校准指标是否达标？
      - 读取 MSRA/calibration/calibration_db.json 中该方法类型的累计 TPR/FPR
      - TPR ≥ 90% 且 FPR ≤ 10% → ✅ 高置信度
      - TPR 80-90% 或 FPR 10-15% → ⚠️ 低置信度，必须人工复核
      - TPR < 80% 或 FPR > 15% → ❌ 不可信，强制人工复核
      - 校准数据不足 (<10条) → ⚠️ 无法评估，必须人工复核
  □ 10. P值格式合规 🆕: 所有P值符合 P-R01~R07（无 P=0.000，无二元化表述）
      - 参考: shared/statistics-methods/statistical_constraints.md
  □ 11. 方法一致性 🆕: 加权分析链无混用（M-R01~R08），方法一致性追踪表已填写
  □ 12. 数据集一致性 🆕: 数据集差异已提醒用户抉择（D-R01~R05），追踪表已填写
  □ 13. 统计原则违反处理 🆕: 所有统计原则违反已记录并经用户确认（S-R01~S-R08）
  □ 14. 图表发表级质量 🆕: 图表符合 publication_figure_standards.md（rcParams/SVG/配色/变量名/P值标注）
  ```

  - **全部通过** → ✅ 进入 Stage 4
  - **1-2 项未通过** → ⚠️ 提示用户，可带条件进入 Stage 4
  - **3+ 项未通过 或 项目 1/3/4/10/11/12/13 未通过** → ❌ **强制退回 Stage 3 修正**
- **Checkpoint**: [MANDATORY-M3] 门闸通过后进入 Stage 3.7

### Stage 3.7: RESULTS INTERPRETATION SESSION 🆕（交互式会话）

- **Skill**: `report`（预览模式）
- **输入**: analysis_results + quality_check
- **执行流程**:
  1. 系统展示分析结果摘要：
     - 主要终点：效应量 + p值 + 95% CI
     - 次要终点：显著性列表
     - 安全性信号：AE/SAE 摘要
     - 异常发现：与预期不符的结果
  2. 用户交互：
     - "哪些发现你认为是最重要的？" → 记录为报告核心重点
     - "哪些结果需要进一步探索？" → 触发额外分析请求
     - "哪些结果可能需要谨慎解读？" → 标记为报告中的注意事项
  3. 输出：`interpretation_priorities.md`（用户确认的结果优先级）
- **Checkpoint**: 🔴 [MANDATORY] 必须确认结果优先级后才进入 Stage 4
- **设计原则**：不修改任何分析结果，仅调整报告的关注重点和叙述框架
- **注意**：Stage 3.7 不允许用户修改分析结果——如需修改应退回 Stage 3

### Stage 4: REPORT
- **Skill**: `report`
- **Mode 匹配**:
  - 用户说"生成完整报告" → `guided` (交互式)
  - 用户说"生成Table 1" → `quick` (快速生成)
- **研究类型分支**:
  - RCT → CONSORT (报告规范选择移至 Stage 5.0，统计报告阶段不强制全文合规)
  - 观察性 → STROBE
  - 诊断试验 → STARD
- **输入**: 分析结果 + 质检报告 + 研究类型
- **输出**: 统计报告 + 图表(figures/*.png) + 三线表(tables/*.docx) + 方法学描述 + 统计质量检查 + 图文HTML报告
- **子步骤**:
  1. 结果解读（临床意义、效应量解释、局限性、与文献对比）
  2. 生成表格（Table 1、结果表、敏感性分析表）
  3. 表格导出（三线表→docx）
  4. 生成图表（执行模板→保存PNG：KM曲线、森林图、ROC等出版级图表）
  5. 方法学描述（按模板结构化段落）
  6. 统计质量检查（statcheck + anti-patterns + 统计维度 quality_checklist）
  7. 报告组装（Phase 7: JSON骨架→HTML图文报告，按模板章节组织）
- **Checkpoint**: [MANDATORY-M4] 统计质量检查 → 确认 → [MANDATORY-M4'] ★ STAGE 4 CHECKPOINT: [A] 结束 / [B] Paper Track
- **输出**: final_report.md + final_report.html + figures/*.png + tables/*.docx

### Stage 5: PAPER TRACK（可选 — Stage 4 checkpoint 选 [B] 时进入）

> **入口守卫（IRON RULE）**：仅在 passport.track == "full_paper" 时进入。
> Stage 1-4 必须全部 completed/consumed。Stage 4 报告产物（final_report + figures + tables）必须齐全。

MSRA Pipeline 在 Paper Track 保持纯调度，依次调用各写作 skill 完成论文从选题到定稿的全流程。

#### Stage 5.0: PAPER INTAKE

- **Skill**: `report`
- **输入**: MSRA passport (track=full_paper) + final_report + SAP + Stage 3.5 门闸报告
- **工作流**:
  1. 产物校验（passport stage_4 == completed + final_report 存在）
  2. 生成 MSRA Handoff Bundle（调用 `scripts/generate_msra_handoff_bundle.py` → `MSRA/msra_handoff_bundle.md`）— 包含 RQ、方法摘要、表格/图表列表、核心发现、安全性发现、局限性讨论、论文级方法文本
  3. 报告规范选择（基于 study_type 推荐 CONSORT/STROBE/STARD；用户可覆盖）
  4. 期刊模板选择（`shared/journal-templates/`）
  5. 论文配置确认（预填 RQ/Discipline/Method/Existing Materials/Citation=Vancouver）
- **输出**: `msra_handoff_bundle.md` + 论文配置
- **Checkpoint**: [MANDATORY] 确认论文配置后进入 Stage 5.1

#### Stage 5.1: LITERATURE SEARCH

- **Skill**: `deep-research`
- **输入**: MSRA Handoff Bundle（含文献 seed）+ 研究问题
- **工作流**:
  1. 读取 MSRA Phase 1 文献对比作为 seed
  2. 基于 seed 扩展检索（Forward/Backward citation）
  3. 针对性补充检索（Introduction 需要的背景文献、Discussion 需要的对比文献）
  4. 质量评估（证据层级、相关性评分）
  5. 主题综合（非逐篇罗列）
- **输出**: 完整 Bibliography + Synthesis Report
- **复用机制**: MSRA Phase 1 文献直接纳入，不重复检索
- **Checkpoint**: [MANDATORY] 文献覆盖评估确认

#### Stage 5.2: PAPER WRITING

- **Skill**: `academic-paper`
- **输入**: MSRA Handoff Bundle + Bibliography + Synthesis Report + figures/*.png + tables/*.docx
- **工作流**:
  1. **Introduction**: 文献综述 + 研究背景 + 研究空白 + RQ 陈述
  2. **Methods**: 直接引用 MSRA Stage 4 Phase 5 方法学描述（不重新生成）
  3. **Results**: 直接引用 MSRA figures/tables（不重新生成）+ 结果描述
  4. **Discussion**: 结果解读 + 与文献对比 + 局限性 + 临床意义
  5. **Abstract**: 结构化摘要生成
  6. **Compliance Check**: 基于 study_type 的报告规范检查（CONSORT/STROBE/STARD）
- **输出**: 完整论文草稿（IMRaD 结构）
- **复用机制**: 融合点 D（方法学）+ 融合点 F（表格图表）
- **Checkpoint**: [MANDATORY] 草稿审查确认

#### Stage 5.5: INTEGRITY CHECK 🔴（阻断式检查）

> **IRON RULE**: 这是阻断式检查点。Stage 5.5 未通过 → 必须退回 Stage 5.2 修订。

- **Skill**: 内置完整性验证
- **输入**: 论文草稿 + Stage 3.5 门闸报告 + MSRA Handoff Bundle
- **检查清单**:
  1. 引用完整性（所有引用是否真实存在）
  2. 数字一致性（论文中数字与 MSRA 分析结果是否一致）
  3. 引用格式合规（所选 Citation Format 是否正确应用）
  4. 报告规范合规（CONSORT/STROBE/STARD 检查清单）
  5. 重复内容检测（无自我抄袭）
  6. 伦理合规（IRB 声明、知情同意）
- **复用机制**: Stage 3.5 门闸报告已验证统计数字，不重复检查
- **检查结果**:
  - 全部通过 → ✅ 进入 Stage 5.6
  - 1-2 项未通过 → ⚠️ 带条件进入（记录风险）
  - 3+ 项未通过 → ❌ 强制退回 Stage 5.2
- **Checkpoint**: [MANDATORY] 完整性报告确认

#### Stage 5.6: PEER REVIEW

- **Skill**: `academic-paper-reviewer`
- **输入**: 论文草稿 + 完整性报告 + 研究类型
- **工作流**:
  1. 5 位独立审稿人评审：EIC + 方法学审稿人 + 领域审稿人 + 写作审稿人 + Devil's Advocate
  2. 7 维评分：Originality、Methodological Rigor、Evidence Sufficiency、Argument Coherence、Writing Quality、Literature Integration、Significance
  3. 编辑决策：Accept / Minor Revision / Major Revision / Reject
  4. 生成 Revision Roadmap（优先级排序的修改建议）
- **输出**: Review Report + Revision Roadmap + Editorial Decision
- **Checkpoint**: [MANDATORY] 评审结果确认 → 决定是否修订

#### Stage 5.7: REVISION

- **Skill**: `academic-paper`
- **输入**: 论文草稿 + Revision Roadmap + Review Report
- **工作流**:
  1. 逐项修改论文（按 Revision Roadmap）
  2. 生成 Response to Reviewers（逐条回应）
  3. 更新论文草稿
- **输出**: 修订后论文 + Response to Reviewers
- **Checkpoint**: [MANDATORY] 修订完成确认

#### Stage 5.8: FINAL INTEGRITY CHECK 🔴（阻断式检查）

> **IRON RULE**: 这是阻断式检查点。Stage 5.8 未通过 → 必须退回 Stage 5.7 修订。

- **Skill**: 内置完整性验证（最终版）
- **输入**: 修订后论文 + Response to Reviewers + Revision Roadmap
- **检查清单**:
  1. 所有评审意见是否已回应
  2. 所有修改是否已落实
  3. 新引入的内容是否合规
  4. R&R Traceability Matrix 是否完整
- **检查结果**:
  - 全部通过 → ✅ 进入 Stage 5.9
  - 未通过 → ❌ 强制退回 Stage 5.7
- **Checkpoint**: [MANDATORY] 最终完整性报告确认

#### Stage 5.9: FINALIZE

- **Skill**: `academic-paper`
- **输入**: 最终论文 + 期刊模板
- **工作流**:
  1. 格式转换：MD → DOCX（via Pandoc）
  2. PDF 导出
  3. 排版调整（期刊模板适配）
  4. 最终检查（格式、页码、参考文献）
- **输出**: final_paper.md + final_paper.docx + final_paper.pdf

#### Stage 6: PROCESS SUMMARY

- **输入**: MSRA passport + 所有阶段产物
- **工作流**:
  1. 汇总 Stage 1-5 全过程记录
  2. 更新 passport：所有阶段标记 completed，status = "completed"
  3. 生成过程摘要报告
- **输出**: process_summary.md + 更新后的 passport.json

---

## 4. Checkpoint Protocol（三级分层）

> 根据 §2.5 用户选择的交互密度，Checkpoint 按三级执行。**核心原则**：
> - MANDATORY 级：用户不可绕过，必须展示并等待决策
> - SLIM 级：仅一行确认，无需完整 Dashboard
> - ADAPTIVE 级：仅在特定异常条件触发

### 4.1 MANDATORY Checkpoint（阻断式，所有模式均强制执行）

以下 5 个检查点**不可跳过**，无论用户选择哪种模式都必须暂停展示结果：

| # | 位置 | 触发条件 | 展示内容 | 用户决策选项 |
|---|------|---------|---------|-------------|
| M1 | Stage 1.5 通过后 | 数据门闸结果 | 9 项门闸检查结果 + 阻断判定 | 通过继续 / 退回修订 / 带条件通过 |
| M2 | Stage 2.5 通过后 | SAP 门闸结果 | 8 项门闸检查结果 + 阻断判定 | 通过继续 / 退回修订 / 带条件通过 |
| M3 | Stage 3.5 通过后 | 结果门闸结果 | 9 项门闸检查结果 + 阻断判定 | 通过继续 / 退回修正 / 带条件通过 |
| M4 | Stage 4 完成时 | 统计质量检查 + 报告交付决策 | 统计质量报告 + ★[A]结束/[B]继续Paper Track | [A]结束 / [B]进入Stage 5.0 |
| M5 | 任一门闸回退≥3次（收敛失败） | 收敛检测触发 | 未通过项清单 + 回退历史 + 风险评估 | 书面接受风险继续 / 退回根本原因排查 / 换方法换人 |

**MANDATORY Checkpoint 简化 Dashboard**（一行即可，不再展示 ASCII 框）：

```
── MANDATORY CHECKPOINT ──
Stage {N} 完成 | 产物: {产物1} ✅ | 选择: [继续 / 回改 / 查看详情]
```

**协作深度观察**（详细引导模式可选输出）：

> 参考：shared/statistics-methods/collaboration_rubric.md — 协作深度评估框架
> 三个维度：委托强度 / 认知警觉 / 认知再分配，各 0-5 分
> 必须有对话证据支撑，不凭感觉打分

```
── 协作深度观察（非阻断）──
委托强度: 4/5 ✅ | 认知警觉: 2/5 ⚠️ 建议在门闸结果上逐项核对 | 认知再分配: 3/5
```

输出规则：
- 高效模式下不输出协作深度观察
- 用户需要时再说"输出协作观察"
- 每个 MANDATORY Checkpoint **最多输出一次**

### 4.2 SLIM Checkpoint（一行确认，根据用户模式选择性执行）

> **设计原则**：仅在详细引导模式下执行。高效模式下全部跳过（仅记录）。

| 模式 | SLIM 执行规则 |
|------|-------------|
| 详细引导 | 执行 S1（Stage 2 方法确认后） |
| 高效模式 | 全部跳过（仅记录） |

SLIM 触发点：

| # | 位置 | 提示模板 | 备注 |
|---|------|---------|------|
| S1 | Stage 2 Estimands + 方法确认后 | `Estimands + 方法已确认, 生成 SAP? [y/N]` | 详细引导模式下执行 |
| S2 | Stage 3 Phase 6 主要分析完成后 | `主要分析结果已出，继续敏感性分析? [y/N]` | 详细引导模式下执行 |
| S3 | Stage 4 Phase 1 结果解读完成后 | `结果解读已完成，继续生成表格? [y/N]` | 详细引导模式下执行 |
| S4 | Stage 4 Phase 5 方法学描述完成后 | `方法学描述已完成，进入统计质量检查? [y/N]` | 详细引导模式下执行 |

### 4.3 ADAPTIVE Checkpoint（异常触发式）

> **设计原则**：仅在异常条件触发，正常流程不暂停。

| 触发条件 | 自动暂停 |
|---------|---------|
| 数据质量严重问题（缺失率 > 30%、异常值异常多） | ✅ 必须暂停讨论 |
| SAP 审查发现 P0/P1 级缺陷 | ✅ 必须退回修改 |
| 分析结果与预期严重不符（效应方向相反、P 值边界） | ✅ 必须暂停讨论 |

**模式差异**：
- 详细引导：展示问题详情 + 选项供用户选择
- 高效模式：展示问题摘要 + 推荐方案，用户确认后继续

**正常流程**：无异常 → 全程无额外暂停，直接从 Stage 1 流向 Stage 4。

**IRON RULE**: MANDATORY checkpoint 不能以任何理由自动跳过。SLIM 和 ADAPTIVE 可跳过/合并，但所有跳过操作必须记录到进度追踪。

**IRON RULE**: 记住用户选择的交互模式。如果后续交互与用户选择的模式不一致，先确认再继续。不要自行升级降级交互密度。

### 4.4 分层验证框架

> 参考：shared/reporting-guidelines/quality_checklist.md — 8 维度质量检查清单；shared/reproducibility/reproducibility_guide.md — 复现验证标准

每个 Stage 完成后，执行分层验证：

**第一层：自动化快速检查（秒级）**
- [ ] 所有计划产物已生成（无遗漏）
- [ ] 产物格式合规（无 markdown 残留、无异常标记）
- [ ] 数值一致性（报告中引用的数字与分析输出一致）
- [ ] 表格/图表引用完整
- [ ] [SKIP] 标记数量和原因已记录

**第二层：LLM 辅助质量评估（分钟级）**
- 逐阶段质量评分（准确性、完整性、特异性）
- 与 SAP/指南标准对比
- 输出结构化改进建议

**第三层：重复性验证（可选）**
- 同一输入运行 N 次，检查关键结论一致性
- 统计输出变动范围（关键数字应 100% 一致）

---

## 5. Progress Tracking

> 使用 Material Passport (`shared/passport/passport.py`) 追踪产物生命周期。
> 护照路径: `.msra/passport.json`（自动创建）。
> 能力: 产物追踪(planned→consumed) / 前置检查 / 恢复(`/msra --resume`) / 回滚 / 门闸记录

### 5.0 状态表示

在每个 checkpoint 更新进度（示例）：

```
Stage 1  [数据准备]       ██████████ 100% ✅
Stage 1.5 [数据质量门闸]   ██████████ 100% ✅
Stage 2  [分析计划]       ████████░░  80% 🔄
Stage 3  [分析执行]       ░░░░░░░░░░   0% ⏳
Stage 3.5 [结果质量门闸]   ░░░░░░░░░░   0% ⏳
Stage 4  [报告生成]       ░░░░░░░░░░   0% ⏳
Stage 5  [论文写作]       ░░░░░░░░░░   --  ⏸ (track=full_paper 时显示)
```

### 5.1 产物追踪

使用 Passport 自动管理（`pm.update_status()` / `pm.get_resume_point()`）：

| 阶段 | 产物 | 护照ID |
|------|------|--------|
| Stage 1 | 清洗后数据 + 清洗日志 + 盲态审核 + 锁定记录 | cleaned_data / cleaning_log / ... |
| Stage 1.5 | 数据质量门闸报告 | gate_stage_1.5 |
| Stage 2 | SAP | sap |
| Stage 2.5 | SAP质量门闸报告 | gate_stage_2.5 |
| Stage 3 | 分析结果 + 质检报告 | analysis_results / qc_report |
| Stage 3.5 | 结果质量门闸报告 | gate_stage_3.5 |
| Stage 4 | 最终报告 + 图表 + 三线表 | final_report / figures / tables |

---

## 5.2 Material Passport JSON Schema

> 以下为 `.msra/passport.json` 的完整 JSON Schema 定义。所有阶段调度、前置检查、门闸记录均基于此结构。

```json
{
  "passport_version": "1.0",
  "study_id": "string",
  "current_stage": "Stage 0|1|1.5|2|2.5|3|3.5|4|5",
  "artifacts": {
    "raw_data": {"path": "string", "status": "pending|completed", "hash": "string"},
    "cleaned_data": {"path": "string", "status": "pending|completed", "hash": "string"},
    "sap": {"path": "string", "status": "pending|completed|approved", "hash": "string"},
    "analysis_results": {"path": "string", "status": "pending|completed", "hash": "string"},
    "report": {"path": "string", "status": "pending|completed", "hash": "string"}
  },
  "gates": {
    "stage_1_5": {"status": "pending|passed|blocked", "checks_passed": 0, "checks_total": 9},
    "stage_2_5": {"status": "pending|passed|blocked"},
    "stage_3_5": {"status": "pending|passed|blocked", "checks_passed": 0, "checks_total": 14}
  },
  "deviations": [],
  "timestamp": "ISO 8601"
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `passport_version` | string | Schema 版本号，当前为 "1.0" |
| `study_id` | string | 研究唯一标识符 |
| `current_stage` | string | 当前所处阶段 |
| `artifacts.*.status` | string | 产物状态：pending → completed（SAP 可为 approved） |
| `artifacts.*.hash` | string | 产物文件哈希，用于完整性校验 |
| `gates.*.status` | string | 门闸状态：pending → passed / blocked |
| `gates.*.checks_passed/total` | number | 门闸检查项通过数/总数 |
| `deviations` | array | 偏差记录列表，每条含阶段、内容、影响评估、用户确认状态 |
| `timestamp` | string | 最后更新时间（ISO 8601） |

---

## 6. Agent Dispatch Mode (多 Agent 协作)

> 在不同阶段切换为对应专家角色，完成后切回 Orchestrator 模式。
> 完整定义见 [agents/AGENTS.md](../../agents/AGENTS.md)（含接棒协议、异常上报、跨 Agent 约束）。
> Agent 角色定义文件（均已验证存在于 agents/ 目录）：
> - [Data Validator Agent](../../agents/data_validator_agent.md) — Stage 1
> - [Method Consultant Agent](../../agents/method_consultant_agent.md) — Stage 2
> - [Exec Runner Agent](../../agents/exec_runner_agent.md) — Stage 3 Phase 0-6
> - [Exec Inference Agent](../../agents/exec_inference_agent.md) — Stage 3 Phase 7-9
> - [QC Inspector Agent](../../agents/qc_inspector_agent.md) — Stage 1.5/2.5/3.5
> - [AGENTS.md](../../agents/AGENTS.md) — 接棒协议与跨 Agent 约束总纲

### 6.1 角色切换规则

每个 Stage 开始时切换为对应角色，完成后切回 Orchestrator。
Stage 3 使用 Generator-Evaluator 双角色：Phase 0-6 为 Exec Runner，Phase 7-9 为 Exec Inference。
差异比对结果纳入 Stage 3.5 门闸输入。

### 6.2 Agent 角色卡速查

| 阶段 | 角色 | Agent 文件 | 核心行为 | 禁止行为 |
|------|------|-----------|---------|---------|
| Stage 1 | [Data Validator](../../agents/data_validator_agent.md) | `agents/data_validator_agent.md` | 验证/清洗/构造 | 决定统计方法 |
| Stage 1.5 | [QC Inspector](../../agents/qc_inspector_agent.md) | `agents/qc_inspector_agent.md` | 数据 9 项阻断检查 | 修改数据或清洗脚本 |
| Stage 2 | [Method Consultant](../../agents/method_consultant_agent.md) | `agents/method_consultant_agent.md` | EDA/Estimands/SAP | 写代码执行分析 |
| Stage 2.5 | [QC Inspector](../../agents/qc_inspector_agent.md) | `agents/qc_inspector_agent.md` | SAP 8 项阻断检查 | 修改 SAP 内容 |
| Stage 3 (Phase 0-6) | [Exec Runner](../../agents/exec_runner_agent.md) | `agents/exec_runner_agent.md` | 代码生成/执行/自愈 Debug | 偏离 SAP/自行解读结果 |
| Stage 3 (Phase 7-9) | [Exec Inference](../../agents/exec_inference_agent.md) | `agents/exec_inference_agent.md` | 独立假设检验/质检/输出 | 修改代码/跳过假设验证 |
| Stage 3.5 | [QC Inspector](../../agents/qc_inspector_agent.md) | `agents/qc_inspector_agent.md` | 结果 9 项阻断检查 + Generator-Evaluator 差异审查 | 修改结果 |
| Stage 4 | Report Expert | `skills/report/SKILL.md` | 解读/制表/生成 | 修改数据 |

详细接棒协议（Handoff 格式）、异常上报规则（INFO/WARN/BLOCK 三级别及阻断触发条件）及跨 Agent 约束见 [agents/AGENTS.md](../../agents/AGENTS.md)。

---

## 7. Error Handling & Rollback

### 7.1 阶段内错误

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| 数据验证发现严重问题 | 回到 Stage 1 重新清洗 | 标记数据为"不可用"，要求用户决定是否重新收集 |
| **Stage 1.5 质量门闸未通过** | **退回 Stage 1 修订清洗流程** | **3+ 项未通过或项目 5/6 未通过必须修订，不得跳过；回退 ≥ 2 次走收敛检测 (7.3)** |
| SAP 审查不通过 | 回到 Stage 2 修改计划 | 用户接受风险后继续，记录偏差 |
| **Stage 2.5 质量门闸未通过** | **退回 Stage 2 修订 SAP** | **3+ 项未通过必须修订，不得跳过；回退 ≥ 2 次走收敛检测 (7.3)** |
| 质检发现严重错误 | 回到 Stage 3 修正分析 | 标记结果为"待验证"并阻断进入 Stage 4，用户确认后方可解锁 |
| **Stage 3.5 质量门闸未通过** | **退回 Stage 3 修正分析** | **3+ 项未通过必须修正，不得跳过；回退 ≥ 2 次走收敛检测 (7.3)** |
| 前置产物缺失 | 提示用户补充 | 用户确认跳过后继续，记录风险 |

**错误处理优先级规则**：
1. 🚫 **Blocking** (门闸 3+ 项未通过) → 必须退回，用户不可跳过
2. ⚠️ **Conditional** (门闸 1-2 项未通过/质检问题) → 可带条件通过，记录风险
3. 🔵 **Informational** (前置产物缺失) → 可跳过，但记录偏差
4. 多阶段错误同时发生时：**从最早出错的阶段开始修复**

**多信号冲突处理**：

| 场景 | 处理策略 |
|------|---------|
| 用户同时提供 SAP + 原始数据 | 检测到原始数据→从 Stage 1 开始，告知用户 SAP 将在 Stage 2 使用 |
| 用户说"做分析"但有清洗数据和分析结果两个线索 | 优先从 Stage 3 执行（分析执行），因为分析执行最接近用户意图 |
| 用户说"完整流程"和"快速"矛盾 | 以"完整流程"为准，但推荐 Stage 1-4 分步执行而非一次完成 |

### 7.2 偏差记录
如果分析执行中偏离了 SAP：
1. 记录偏差内容
2. 评估偏差影响
3. 与用户讨论是否可接受
4. 如不可接受，回退修正

### 7.3 收敛检测与回退循环控制（⏱ 新增）

> 防止同一环节无限循环回退。借鉴 ARS 的 early-stopping 设计。

**回退计数器**：每个质量门闸维护独立的回退次数计数：

| 门闸 | 计数器名 | 最大回退次数 |
|------|---------|------------|
| Stage 1.5 → Stage 1 | `retry_data_prep` | 2 |
| Stage 2.5 → Stage 2 | `retry_sap` | 2 |
| Stage 3.5 → Stage 3 | `retry_analysis` | 2 |

**收敛判断逻辑**：

```
第 1 次退回 → 正常修改，记录偏差原因
第 2 次退回 → 警告："已退回 2 次，建议检查根本原因或降低标准"
第 3 次退回 → BLOCK: "同阶段已退回 3 次，自动转入偏差记录模式"
                → 必须走 M5 Checkpoint，用户需书面接受风险
                → 后续分析结果标注 ⚠️ [CONVERGED WITH DEVIATIONS]
```

**Early-stopping 辅助判断**：
- 如果质量门闸未通过项数在上一次回退后**没有减少** → 强制暂停，引导用户换人审查或换方法，并在护照中标记"收敛异常"
- 如果未通过项数减少但仍有 **≥3 项关键项未通过** → 强制进入 ADPATIVE checkpoint，提示用户评估修改研究设计的必要性
- 每次回退必须记录"上一次做了哪些修改" + "本次检查结果是否有改善"

**IRON RULE**: 回退超过 2 次后，不得自动再次退回。必须走 MANDATORY Checkpoint 让用户决策。

---

## 检查点量化标准

| 门闸 | 检查项 | 通过标准 | 条件通过 | 阻断标准 |
|------|--------|---------|---------|---------|
| Stage 1.5 | 9项检查 | 9/9通过 | 7-8/9通过(记录风险) | ≤6/9 或 项5/6/7/9未通过 |
| Stage 2.5 | 8项检查 | 8/8通过 | 6-7/8通过(记录偏差) | ≤5/8 或 项3/5/7未通过 |
| Stage 3.5 | 14项检查 | 14/14通过 | 10-13/14通过(记录风险) | <10/14 或 项10/11/12/13未通过 |

**Stage 3.5 关键项量化标准**:

| 项号 | 检查项 | 通过标准 | 阻断标准 |
|------|--------|---------|---------|
| 10 | P值格式 | 全部P值符合P-R01~R07 | 任何P=0.000出现 |
| 11 | 方法一致性 | 加权/非加权不混用(M-R01) | 检测到混用 |
| 12 | 数据集一致性 | 全程使用同一锁定数据集(D-R02) | 检测到数据集切换 |
| 13 | 统计原则 | 所有假设检验已执行(S-R01~R08) | 跳过假设检验 |
| 14 | 图表质量 | SVG+PNG 300dpi双格式 | 仅PNG或<300dpi |

> **升级规则**: Stage 3.5项10/11/12/13为硬阻断项，不可条件通过。
> **收敛规则**: 同一Stage退回≥3次 → BLOCK → 用户书面接受风险 → [CONVERGED WITH DEVIATIONS]

## 7.4 边缘场景处理

> 以下场景在流水线执行中可能遇到，需按表中的降级策略执行，确保流程可追踪且不静默失败。

| 场景 | 触发条件 | 处理策略 | 标记 |
|------|---------|---------|------|
| analysis-exec 产出为空 | Stage 3 执行后无任何分析输出 | BLOCK，使用简化 SAP 重试，最多重试 3 次 | [EMPTY_OUTPUT] |
| 代码执行超时 | 单次执行耗时 > 300s | 终止执行，记录超时日志，建议用户简化分析 | [TIMEOUT] |
| 部分阶段失败 | 部分分析成功、部分失败 | 继续使用成功结果，失败项标记为部分失败 | [PARTIAL_FAIL] |
| Material Passport 损坏 | passport.json 格式异常或字段缺失 | 从各阶段产物重建 passport，记录重建事件 | [PASSPORT_REBUILT] |
| Skill 依赖缺失 | 所需 skill（如 academic-pipeline）未安装 | 跳过对应阶段（如 Paper Track），提示用户安装 | [SKIP: dependency missing] |
| 用户中途中止 | 用户在阶段执行中主动中止 | 保存当前状态到 passport，允许从最后检查点恢复 | [USER_ABORTED] |

---

## 8. Quick Reference Commands

| 命令 | 触发 | 入口 |
|------|------|------|
| `/msra` | 启动流水线（自动检测入口） | 智能检测 |
| `/msra --from data` | 从数据准备开始 | Stage 1 |
| `/msra --from plan` | 从分析计划开始 | Stage 2 |
| `/msra --from exec` | 从分析执行开始 | Stage 3 |
| `/msra --from report` | 从报告生成开始 | Stage 4 |
| `/msra --status` | 查看当前进度 | - |
| `/msra-data` | 直接调用数据准备 | Stage 1 |
| `/msra-plan` | 直接调用分析计划 | Stage 2 |
| `/msra-exec` | 直接调用分析执行 | Stage 3 |
| `/msra-report` | 直接调用报告生成 | Stage 4 |
| `/msra-report CONSORT` | 指定规范的报告生成 | Stage 4 |
| `/msra-report --output html` | 指定输出HTML图文报告 | Stage 4 |
| `/msra --calibrate <gold.csv>` | 运行度量校准 ⚠️ 实验性 | QC Inspector |
| `/msra --calibrate-status` | 查看当前校准状态 ⚠️ 实验性 | - |
| `/msra --calibrate-update <results.csv>` | 增量更新校准 ⚠️ 实验性 | - |
| `/msra --status` | 查看当前进度（Passport） | - |
| `/msra --resume` | 从上次中断处恢复（读取 Passport） | 智能检测 |

---

## 9. Interaction Examples

### Example 1: 全流程（高效模式）
```
用户: /msra 我有一份RCT的原始数据，想完成整个分析流程
→ 检测到原始数据 → 从 Stage 1 开始 → 用户选 [2] 高效模式

Stage 1 → [MANDATORY] → Stage 1.5(9项) → [MANDATORY]
→ Stage 2 → [SLIM] → [MANDATORY] → Stage 2.5(8项) → [MANDATORY]
→ Stage 3 → [SLIM] → Stage 3.5(9项) → [MANDATORY]
→ Stage 4 → [MANDATORY] 合规检查 → 完成 ✅
共 6 次 MANDATORY + 2 次 SLIM
```

### Example 2: 中途切入 + 新手引导
```
# 中途切入
用户: /msra 数据已清洗好，帮我做分析计划
→ 从 Stage 2 开始 → 前置检查: 清洗日志存在 → 高效模式 → Stage 2 → ...

# 新手详细引导
用户: /msra 我有数据但不确定怎么做统计
→ 从 Stage 1 开始 → 用户选 [1] 详细引导
→ 每步暂停讨论策略 → 逐项解释门闸结果 → 全程 FULL checkpoint
```

---

## Stage 流转图

```
Stage 0: 入口诊断
    │ 自动识别研究类型/数据规模/用户意图
    ▼
Stage 1: 数据准备 (data-prep)
    │ 输出: cleaned_data + cleaning_log + validation_report
    ▼
┌─ Stage 1.5: 数据质量门闸 ─┐
│  9项阻断检查 (□1-□9)      │
│  全通过 → 继续             │
│  ≤6项通过 → 阻断退回       │
└──────────────────────────┘
    │
    ▼
Stage 2: 分析计划 (analysis-plan)
    │ 输出: SAP + variable_spec
    ▼
┌─ Stage 2.5: SAP质量门闸 ─┐
│  审查通过/需修改/需重做    │
│  收敛检测 (3次退回→BLOCK)  │
└──────────────────────────┘
    │
    ▼
Stage 3: 分析执行 (analysis-exec)
    │ 输出: analysis_code + results + figures + audit_log
    ▼
┌─ Stage 3.5: 分析质量门闸 ─┐
│  14项阻断检查 (含P值/方法  │
│  一致性/图表质量)          │
│  10-14项通过 → 继续        │
│  <10项通过 → 阻断退回      │
└──────────────────────────┘
    │
    ▼
Stage 4: 报告生成 (report)
    │ 输出: HTML报告 + SVG图表 + DOCX表格
    ▼
Stage 5: 论文写作 (Paper Track, 可选)
    │ 输出: 论文初稿 + 审稿回复
```

## 架构集成图

```
┌──────────────────────────────────────────────────────────┐
│                    MSRA Pipeline 架构                      │
│                                                            │
│  ┌─────────┐   ┌──────────┐   ┌──────────┐   ┌────────┐  │
│  │ data-   │   │ analysis-│   │ analysis-│   │ report │  │
│  │ prep    │   │ plan     │   │ exec     │   │        │  │
│  └────┬────┘   └────┬─────┘   └────┬─────┘   └───┬────┘  │
│       │             │              │              │       │
│       ▼             ▼              ▼              ▼       │
│  ┌────────────────────────────────────────────────────┐  │
│  │              Material Passport (JSON)               │  │
│  │  ┌──────────┬──────────┬──────────┬──────────┐    │  │
│  │  │ artifacts│  gates   │deviations│ timestamp│    │  │
│  │  └──────────┴──────────┴──────────┴──────────┘    │  │
│  └────────────────────────────────────────────────────┘  │
│       │             │              │              │       │
│       ▼             ▼              ▼              ▼       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │
│  │ Stage 1.5│  │ Stage 2.5│  │     Stage 3.5        │   │
│  │ 数据门闸  │  │ SAP门闸  │  │     分析门闸         │   │
│  │ (9项)    │  │(审查)    │  │     (14项)           │   │
│  └──────────┘  └──────────┘  └──────────────────────┘   │
│       │             │              │              │       │
│       └─────────────┴──────────────┴──────────────┘       │
│                         │                                  │
│                    ┌────▼────┐                             │
│                    │calibration│ (gate-check 模式)         │
│                    └─────────┘                             │
│                         │                                  │
│                    ┌────▼────┐                             │
│                    │  Stage 5 │ (Paper Track, 可选)        │
│                    └─────────┘                             │
└──────────────────────────────────────────────────────────┘
```

**架构设计原则**:
1. Pipeline为纯调度器，不做实质性分析工作
2. Material Passport是唯一的跨Stage状态传递机制
3. 质量门闸为阻断式，不可跳过(MANDATORY)
4. 每个Stage的Skill独立运行，通过Passport解耦
5. calibration作为Stage 3.5的子检查集成，不独立成Stage

## 10. 快速模式 (Quick Mode)

> 面向简单数据集和快速探索场景的精简流水线。在保证核心质量门闸的前提下跳过非必要步骤。

### 触发条件

满足以下任一条件即自动进入 Quick Mode：
- 用户输入包含"快速"、"quick"、"快速分析"等关键词
- 数据集变量数 < 10 且行数 < 100

### 简化流程

```
Stage 0: 入口检测 → 识别为 Quick Mode
   ▼
Stage 1: 数据准备（仅快速验证，跳过数据画像 Phase 0）
   ▼
Stage 1.5: 数据质量门闸（缩减为 5 项关键检查）
   ▼
Stage 2: 分析计划（使用模板 SAP，跳过文献种子检索）
   ▼
Stage 3: 分析执行（仅核心分析，跳过敏感性/亚组/安全性分析）
   ▼
Stage 3.5: 结果质量门闸（缩减为 7 项关键检查）
   ▼
Stage 4: 报告生成（标准 HTML 报告，PNG 图表，无 SVG）
```

### 跳过的阶段/步骤

| 跳过项 | 原因 | 风险 |
|--------|------|------|
| Phase 0 数据画像 | 小数据集可快速概览 | 低 |
| Phase 2.5 值规范化 | 简单数据集通常无需 | 中（需人工确认） |
| Stage 3 敏感性/亚组/安全性分析 | 快速模式仅做核心分析 | 中（报告标注"未执行"） |
| Stage 3.7 结果解读会话 | 快速模式自动生成解读 | 低 |
| Phase 5 盲态审核 | 仅 RCT 需要，快速模式默认非 RCT | 低 |
| Stage 5 Paper Track | 快速模式不进入论文写作 | 无 |

### 质量门闸缩减规则

| 门闸 | 标准模式 | Quick Mode |
|------|---------|------------|
| Stage 1.5 | 9 项检查 | 5 项关键检查（项目 1/3/5/6/9） |
| Stage 2.5 | 8 项检查 | 跳过（使用模板 SAP） |
| Stage 3.5 | 14 项检查 | 7 项关键检查（项目 1/2/3/5/9/10/11） |

### 输出格式

- 报告：HTML 格式，无 SVG 图表，仅 PNG
- 表格：标准三线表（docx）
- 标注：报告头部标注"[Quick Mode] — 精简流程，非完整分析"

### 示例

```
用户："快速分析这个CSV"
→ Pipeline 检测: 数据 8 变量 × 85 行 → 自动进入 Quick Mode
→ Stage 1 快速验证 → Stage 1.5 (5项) → Stage 2 模板 SAP
→ Stage 3 核心分析 → Stage 3.5 (7项) → Stage 4 HTML 报告
→ 5 分钟内输出基础报告
```

> [IRON RULE] Quick Mode 不得用于复杂研究设计（多中心 RCT、复杂观察性研究等）。检测到复杂设计时自动升级为标准模式并提示用户。

### Stage 执行时间估算

| Stage | 数据规模 | 预计时间 | 主要耗时 |
|-------|---------|---------|---------|
| Stage 0 | 任意 | <30秒 | 数据类型识别 |
| Stage 1 | 500行×20列 | 5-15分钟 | 数据验证+清洗+EDA |
| Stage 1.5 | - | <30秒 | 门闸检查 |
| Stage 2 | 任意 | 10-30分钟 | EDA+方法讨论+SAP制定 |
| Stage 2.5 | - | 1-5分钟 | SAP审查 |
| Stage 3 | 500行×20列 | 10-30分钟 | 代码生成+执行+自愈 |
| Stage 3.5 | - | <1分钟 | 门闸检查(14项) |
| Stage 4 | - | 5-15分钟 | 报告生成+statcheck |
| Stage 5 | - | 30-120分钟 | 论文写作 |
| **总计(Stage 1-4)** | **500行×20列** | **30-90分钟** | - |
| **Quick Mode** | **500行×20列** | **10-20分钟** | - |

### 常见流水线错误与解决方案

| 错误场景 | 症状 | 解决方案 |
|---------|------|---------|
| Stage 1 数据读取失败 | FileNotFoundError/EncodingError | 检查文件路径和编码(UTF-8/GBK)，提示用户确认格式 |
| Stage 1.5 门闸阻断 | 缺失清洗日志/锁定记录 | 退回Stage 1补充产物，不跳过门闸 |
| Stage 2 SAP审查不收敛 | 连续3次退回 | 触发收敛检测→BLOCK→用户书面接受风险→标注[CONVERGED] |
| Stage 3 代码执行失败 | Python/R报错 | 自愈机制5轮重试→仍失败则标记[SKIP]并记录 |
| Stage 3.5 P值格式不合规 | P=0.000 | 退回Stage 3修复(P-R01规则)→重新通过门闸 |
| Stage 4 statcheck失败 | 统计结果不一致 | 标记[STATCHECK_FAILED]→退回Stage 3核查 |
| Passport状态丢失 | 无法恢复进度 | 从stage产物重建passport→验证一致性→继续 |
| 用户中途切换研究类型 | 类型不匹配 | 重置Stage 2-4→保留Stage 1产物→重新规划 |

---

## 反例与黑名单

> **以下行为必须避免**。作为编排器，你的核心职责是**调度和追踪**，而非执行实质性工作。
> 完整医学统计反模式目录参见：shared/anti-patterns/medical_stats_anti_patterns.md（B2/B3）

### 🚫 编排器角色禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 1 | 自己执行统计分析、生成报告等实质性工作 | 违反"纯调度架构"定位，破坏职责边界 | 只 dispatch 到对应 skill，不自己执行 |
| 2 | 跳过前置检查直接进入下一阶段 | 前置产物缺失会导致后续分析无依据 | Mid-Entry 前置检查必须执行，缺失则回退 |
| 3 | **自动跳过 MANDATORY Checkpoint** | 用户失去关键决策控制，可能产生意外结果 | SLIM/ADAPTIVE 可跳过，**MANDATORY 必须暂停等待用户确认** |
| 4 | 忽略用户信号冲突（多个信号指向不同阶段） | 可能路由到错误阶段 | 多信号时取最强信号，或询问用户确认 |

### 🚫 阶段跳转禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 5 | 从 Stage 1 直接跳到 Stage 2 | 跳过数据质量门闸，数据问题可能带入分析阶段 | 必须经过 Stage 1.5 门闸检查 |
| 6 | Stage 1.5 质量门闸未通过就进入 Stage 2 | 数据质量未保证，后续分析全部不可信 | 🔴 Blocking：Stage 1.5 全部通过或用户书面接受风险 |
| 7 | 从 Stage 1 直接跳到 Stage 4 | 跳过分析计划和执行，报告无依据 | 必须按顺序：Stage 1 → 1.5 → 2 → 2.5 → 3 → 3.5 → 4 |
| 8 | Stage 2 SAP 审查未通过就进入 Stage 3 | 有缺陷的计划会导致后续分析全部错误 | [MANDATORY] SAP 审查通过后才可进入 Stage 2.5 |
| 9 | Stage 2.5 质量门闸未通过就进入 Stage 3 | SAP 质量未保证，分析结果不可信 | 🔴 Blocking：Stage 2.5 全部通过或用户书面接受风险 |
| 10 | Stage 3 质检未通过就进入 Stage 4 | 错误结果会被写入报告 | [SLIM] 质检通过后才可进入 Stage 3.5 |
| 11 | Stage 3.5 质量门闸未通过就进入 Stage 4 | 结果可靠性未验证 | 🔴 Blocking：Stage 3.5 全部通过或用户书面接受风险 |

### 🚫 进度追踪禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 8 | 不更新 Progress Dashboard | 用户无法了解当前状态 | 每个 CHECKPOINT 必须更新进度 |
| 9 | 不记录产物版本 | 无法追溯变更历史 | 产物追踪表必须记录版本和状态 |
| 10 | 偏差不记录就继续执行 | 违反 GCP 规范，不可审计 | Section 6.2 偏差记录必须执行 |

### 🚫 错误处理禁忌 🆕

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 11 | 门闸回退时不更新回退计数器 | 收敛检测依赖于准确的回退计数，不更新会导致门闸无限循环 | 每次回退必须自增计数器，门闸消费后更新 |
| 12 | 多阶段错误同时发生时从最后一个出错阶段修复 | 下游阶段的问题可能是上游问题带入的，下游修复无法根治 | 从最早出错的阶段开始修复，固定一个再处理下一个 |
| 13 | 异常发生时静默继续不告知用户 | 用户失去对意外情况的知情权和决策权 | 所有异常（包括 ADAPTIVE 级别的）必须先展示并得到用户响应才继续 |

### 🚫 检查点协议禁忌 🆕

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 14 | 在高效模式下跳过 MANDATORY 检查点 | MANDATORY 是所有模式的硬性要求，SLIM 和 ADAPTIVE 才可按模式跳过 | 5 个 MANDATORY 检查点（M1-M5）在任何模式下都必须展示并等待用户决策 |
| 15 | 多个 MANDATORY 检查点同时触发时只展示最新的 | 当前阶段的信息不足以让用户做出跨阶段的风险决策 | 同时触发的 MANDATORY 检查点必须依次展示，上一点决策后再展示下一点 |
| 16 | 用户选择详细引导模式但自动降级为高效模式 | 交互密度是用户显式选择的，自动降级违反信任 | 记录用户选择的模式，除非用户主动要求切换，不得自动升降级 |

---

## 流水线反例与黑名单（核心八条）

> **以下 8 条为流水线编排核心禁止行为**，违反任何一条将导致流程不可追踪或结果不可信。

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 1 | 跳过质量门闸直接进入下一阶段 | 门闸是质量保证的核心机制，跳过会导致未经验证的结果流入下游 | 必须通过 Stage 1.5/2.5/3.5 门闸，未通过时退回或书面接受风险 |
| 2 | Material Passport 不记录偏差就修改分析结果 | 无偏差记录的修改破坏可审计性，无法追溯变更原因 | 任何偏离 SAP 的修改必须先记录偏差到 passport.deviations |
| 3 | Stage 3.5 门闸检查时修改分析代码 | 门闸检查应只读，同时修改代码既当裁判又当选手 | 门闸检查只读分析结果，修改必须退回 Stage 3 |
| 4 | 多数据集模式不检查跨中心一致性就汇总 | 跨中心差异可能导致汇总结果误导，掩盖中心效应 | 必须执行 Phase 1b 跨中心一致性检查后再汇总 |
| 5 | Quick Mode 用于复杂研究设计（如多中心 RCT） | 精简流程跳过敏感性/亚组分析，复杂设计下会遗漏关键发现 | 检测到复杂设计时自动升级为标准模式 |
| 6 | 用户中止后不保存状态直接退出 | 用户丢失已完成的工作，无法恢复 | 必须保存当前状态到 passport，允许 `/msra --resume` 恢复 |
| 7 | Paper Track 在 Stage 4 未完成时启动 | 论文写作依赖 Stage 4 的报告、图表和表格，未完成时启动会导致论文缺失素材 | 入口守卫检查 passport stage_4 == completed，未完成时拒绝进入 |
| 8 | 收敛检测触发后仍继续退回而不转入偏差记录模式 | 无限循环退回浪费资源，且无法推进流程 | 回退 ≥ 3 次后必须走 M5 Checkpoint，转入偏差记录模式 |



