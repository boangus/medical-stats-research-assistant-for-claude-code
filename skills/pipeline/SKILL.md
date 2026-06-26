---
version: "1.0.0"
name: MSRA Pipeline
description: |
  医学统计分析流水线编排器。从任意阶段切入，自动识别当前位置，
  引导完成后续所有流程。纯调度架构——不做实质性工作，只负责检测、
  选择、调度、转换和追踪。
  输出: 7阶段完整流水线 + 3个阻断式门闸 + 最终报告(figures/*.png + tables/*.docx + HTML+MD)。
  触发: /msra / 流水线 / pipeline / 数据分析流程 / 统计流程 / 完整流程 / 从头开始 / 数据清洗 / 统计分析 / 分析报告 / 结果解读 / 统计咨询 / orchestrator / 编排 / 调度 / 质量门闸
data_access_level: redacted
task_type: open-ended
depends_on: [data-prep, analysis-plan, analysis-exec, report]
works_with: [agents/AGENTS.md, agents/protocol.md]
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
│  14 项检查 → ❌退回 Stage 3 / ✅进入 Stage 4                 │
└────────────────────────────┬─────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────┐
│  Stage 4: REPORT  (/msra-report)                             │
│  结果解读 → 确定规范 → 选择模板(期刊/自定义) → 表格/图表     │
│  → 表格导出 → 方法学描述 → 规范检查 → 报告组装                │
│  输出: final_report.md + final_report.html + figures/*.png   │
│        + tables/*.docx                                        │
│  [RCT] CONSORT / [观察性] STROBE                            │
│  模板: NEJM/JAMA/Lancet/BMJ/CMJ/Other                       │
└────────────────────────────┬─────────────────────────────────┘
                             ▼
       最终报告 (图文HTML+纯文本MD+PNG图+三线表DOCX)
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
| 提供论文要求review | 审稿意图 | **Stage 3** (质检) | 需先验证数据完整性 |

### Mid-Entry 前置检查

进入任何阶段前，必须确认前置产物是否存在且有效：

```
进入 Stage 1.5 之前  → 确认: 清洗后数据 + 清洗日志 + 盲态审核记录 + 数据库锁定记录
进入 Stage 2 之前     → 确认: 清洗后数据 + 清洗日志 + Stage 1.5 门闸通过
进入 Stage 2.5 之前   → 确认: 已批准的SAP
进入 Stage 3 之前     → 确认: Stage 2.5 通过 + 已批准的SAP
进入 Stage 3.5 之前   → 确认: 分析结果 + 质检报告
进入 Stage 4 之前     → 确认: Stage 3.5 通过 + 分析结果
```

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

**入口响应格式**：
```
── Pipeline Orchestrator ──
检测到: 研究类型=RCT | 入口=Stage 1 (原始数据)
前置检查: 无前置产物，从 Stage 1 开始
交互模式: [1] 详细引导 [2] 高效模式 [3] 极速模式
输入编号或描述需求:
```

---

## 2.5 用户类型与交互密度预判

在确定入口阶段后，询问用户期望的交互密度。此后按对应模式自动调整 Checkpoint 密度，无需每个决策点都问一遍。

**入口处提示**：
```
选择交互模式：
[1] 详细引导（新手/对流程不熟：每个步骤都确认）
[2] 高效模式（熟悉流程：只需关键决策点确认）
[3] 极速模式（赶时间：仅阻断式门闸暂停，其余自动推进）
```

| 用户选择 | Checkpoint 密度 | 适用场景 |
|---------|----------------|---------|
| **[1] 详细引导** (默认) | FULL: 所有 Stage 后都暂停 | 首次使用、对统计方法不熟、数据质量不确定 |
| **[2] 高效模式** | MANDATORY: 仅 6 个阻断式暂停 + SLIM: "继续？"一行确认 | 日常使用、熟悉流程、标准 RCT 分析 |
| **[3] 极速模式** | MANDATORY: 仅质量门闸结果暂停，其余自动推进 | 赶时间、已做过类似分析、数据质量有把握 |

**AI 自动降级规则**（省去每步询问）：
- 同一个用户连续 3 次在某个 Checkpoint 选"继续" → 后续自动降至 SLIM
- 用户明确说"继续吧别问太细" → 切换至高效模式
- 用户说"这块你定就行" → 该 Checkpoint 降级为仅记录，不询问

**AI 自动升级规则**（安全网，防止简化模式遗漏关键问题）：
- **P0/P1 缺陷检测** → 当前 Stage 自动升级到详细引导模式（缺陷修复后可恢复）
- **质量门闸失败 ≥2 次** → 当前 Stage 升级到高效模式，强制展示失败详情
- **用户表达不确定性**（"我不确定"、"这个对吗"、"帮我看看"） → 升级到详细引导
- **统计假设违反**（正态性/方差齐性/PH假设等被拒绝） → 暂停并升级，展示降级路径选项
- **数据质量异常**（缺失>20%、异常值>5%、类别不平衡>10:1） → 升级到高效模式并展示警告

> **设计原则**：降级规则尊重用户效率偏好，升级规则保障统计严谨性。两者互补，确保"该快则快，该慢则慢"。

---

## 3. Stage Dispatching

每个 Stage 调用对应的 Skill，并选择最佳 Mode：

### Stage 1: DATA PREP
- **Skill**: `data-prep`
- **Mode 匹配**: "帮我清洗数据" → `guided` (交互式) | "快速检查一下" → `quick` (快速验证)
- **研究类型分支**: RCT → 启用盲态审核、随机化检查 | 观察性 → 启用混杂偏倚评估、数据源描述
- **输入**: 原始数据文件路径
- **输出**: 清洗后数据 + 清洗日志 + EDA报告(数据质量) + 验证报告 + 盲态审核记录 + 数据库锁定记录
- **子步骤**: 1.数据验证 → 2.交互式清洗 → 3.值规范化(TCM术语+数值格式) → 4.EDA数据质量检查 → 5.盲态审核 → 6.数据库锁定
- **Checkpoint**: [MANDATORY-M1] 展示清洗摘要 + EDA 质量报告 + 审核记录，用户确认后进入 Stage 1.5

### Stage 1.5: DATA QUALITY GATE 🔴（阻断式检查）

> **完整门闸定义参见**：[shared/quality_gates/gate-data.md](../../shared/quality_gates/gate-data.md)（9 项检查清单 + 判定规则）
> **阻断规则**：9 项中关键项 5/6/7/9 任一未通过 或 <7/9 通过 → ❌ 强制退回 Stage 1 修订；回退 ≥2 次触发收敛检测（§7.3）。

### Stage 2: ANALYSIS PLAN
- **Skill**: `analysis-plan`
- **研究类型分支**:
  - RCT → ITT/PP/Safety 人群定义、ANCOVA 推荐、随机化验证、多重性控制
  - 观察性 → DAG 混杂结构、倾向性评分(PSM/IPTW)推荐、E-value 敏感性分析
  - 诊断试验 → AUC 比较、金标准偏倚评估、切点选择
- **输入**: 清洗后数据 + EDA 数据质量报告 + 研究问题 + 研究类型
- **输出**: 估计目标定义 + 分析方法决策 + 统计分析计划(SAP) + 分析规范表
- **子步骤**: 1.估计目标定义(ICH E9(R1)) → 2.方法探讨 → 3.制定SAP → 4.计划审查
- **Checkpoint**: [SLIM-S2] 方法选择后一行确认；[MANDATORY-M3] SAP 审查通过后进入 Stage 2.5

### Stage 2.5: SAP QUALITY GATE 🔴（阻断式检查）

> **完整门闸定义参见**：[shared/quality_gates/gate-sap.md](../../shared/quality_gates/gate-sap.md)（8 项检查清单 + 判定规则）
> **阻断规则**：8 项中关键项 3/5/7 任一未通过 或 3+ 项未通过 → ❌ 强制退回 Stage 2 修订；回退 ≥2 次触发收敛检测（§7.3）。

### Stage 3: ANALYSIS EXEC
- **Skill**: `analysis-exec`
- **Agent 拆分**: Exec Runner (Phase 0-6) + Exec Inference (Phase 7-9)；Generator-Evaluator 差异报告作为 Stage 3.5 门闸输入
- **Mode 匹配**: "按SAP执行分析" → `sap-guided` | "先探索一下数据" → `exploratory`
- **输入**: 清洗后数据 + 已批准的SAP（含变量构造逻辑）
- **输出**: 分析代码 + 构造后分析数据集 + 描述性统计表 + 依从性分析 + 主要/次要/探索性分析结果 + 安全性分析 + 假设检验报告 + 质检报告
- **子步骤**: 0.样本量验证 → 1.变量构造(按SAP) → 2.执行前检查 → 3.描述性统计(Table 1) → 4.依从性分析 → 5.主要估计目标分析 → 6.敏感性分析 → 7.次要/探索性分析 → 8.安全性分析 → 9.亚组分析 → 10.假设检验 → 11.质量检查
- **Checkpoint**: [SLIM-S3] 变量构造 + 质检结果一行确认 → 进入 Stage 3.5

### Stage 3.5: RESULTS QUALITY GATE 🔴（阻断式检查）

> **完整门闸定义参见**：[shared/quality_gates/gate-results.md](../../shared/quality_gates/gate-results.md)（14 项检查清单 + 判定规则）
> **阻断规则**：14 项中关键项 1/3/4/10/11/12/13 任一未通过 或 3+ 项未通过 → ❌ 强制退回 Stage 3 修正；回退 ≥2 次触发收敛检测（§7.3）。

### Stage 4: REPORT
- **Skill**: `report`
- **Mode 匹配**: "生成完整报告" → `guided` | "生成Table 1" → `quick`
- **研究类型分支**: RCT → CONSORT | 观察性 → STROBE | 诊断试验 → STARD
- **输入**: 分析结果 + 质检报告 + 研究类型 + (可选) 期刊模板
- **输出**: 结果解读 + 模板结构化报告 + 图表(figures/*.png) + 三线表(tables/*.docx) + 方法学描述 + 规范合规报告 + 图文HTML报告
- **子步骤**: 1.结果解读 → 2.确定报告规范 → 3.选择输出模板 → 4.生成表格 → 5.生成图表(PNG) → 6.表格导出(docx) → 7.方法学描述 → 8.规范检查 → 9.报告组装(JSON骨架→HTML图文报告)
- **Checkpoint**: [MANDATORY-M5] 合规检查 → 最终确认交付

---

## 4. Checkpoint Protocol（三级分层）

> **完整协议定义参见**：[shared/checkpoint_protocol.md](../../shared/checkpoint_protocol.md)（三级 MANDATORY/SLIM/ADAPTIVE 完整规范 + 分层验证框架）

| 级别 | 触发 | 跳过规则 | 数量 |
|------|------|---------|------|
| **MANDATORY** | 阻断式（6 个：M1/GATE-01/GATE-02/GATE-03/M5/GATE-06） | 任何模式都不可跳过 | 6 |
| **SLIM** | 一行确认（S1-S4） | 详细引导全执行；高效模式跳 Stage 3；极速模式全跳过 | 4 |
| **ADAPTIVE** | 异常触发（缺失率>30%、方法多选、P0/P1 缺陷、效应反向等） | 正常流程不触发 | 5 |

**IRON RULE**: MANDATORY 不可自动跳过；SLIM/ADAPTIVE 可跳过但必须记录到进度追踪。不要自行升级降级交互密度。

---

## 5. Progress Tracking (Passport)

> 使用 Material Passport (`shared/passport/passport.py`) 持久化追踪全部产物。护照路径: `.msra/passport.json`（自动创建）

**Passport 能力**：产物追踪(planned→in_progress→completed→verified→consumed) · 前置检查(`verify_prerequisites`) · 恢复(`get_resume_point`) · 回滚(`rollback_to`) · 门闸记录(`set_gate_result`)

**初始化**：
```python
from shared.passport.passport import PassportManager
pm = PassportManager(".msra/passport.json")
```

**状态表示**（每个 checkpoint 更新）：
```
Pipeline Progress:
  Stage 1    [数据准备]     ██████████ 100% ✅
  Stage 1.5  [数据质量门闸]  ██████████ 100% ✅
  Stage 2    [分析计划]     ██████████ 100% ✅
  Stage 2.5  [SAP质量门闸]  ████████░░  80% 🔄 (2/7 检查完成)
  Stage 3    [分析执行]     ░░░░░░░░░░   0% ⏳
  ...
```

**产物追踪**（Passport 自动维护）：Stage 1 → cleaned_data, cleaning_log | Stage 1.5 → gate_stage_1.5 报告 | Stage 2 → sap | Stage 2.5 → gate_stage_2.5 报告 | Stage 3 → analysis_results | Stage 3.5 → gate_stage_3.5 报告 | Stage 4 → final_report (HTML+MD), figures/*.png, tables/*.docx

---

## 6. Agent Dispatch Mode (多 Agent 协作)

> **Agent 角色定义唯一来源**：[agents/AGENTS.md](../../agents/AGENTS.md)（协作协议 + Handoff 格式）+ [agents/protocol.md](../../agents/protocol.md)（异常上报规则）
> Agent 文件：[Data Validator](../../agents/data_validator_agent.md)(Stage 1) · [Method Consultant](../../agents/method_consultant_agent.md)(Stage 2) · [Exec Runner](../../agents/exec_runner_agent.md)(Stage 3 P0-6) · [Exec Inference](../../agents/exec_inference_agent.md)(Stage 3 P7-9) · [QC Inspector](../../agents/qc_inspector_agent.md)(Stage 1.5/2.5/3.5)

### 6.1 角色切换规则

```
Pipeline Orchestrator
  │
  ├── Stage 1: Data Validator → 数据验证/清洗 → 切回 Orchestrator → Checkpoint
  ├── Stage 1.5: QC Inspector → 数据质量门闸 → 切回 Orchestrator → 结果决策
  ├── Stage 2: Method Consultant → SAP 制定 → 切回 Orchestrator → Checkpoint
  ├── Stage 2.5: QC Inspector → SAP 质量门闸 → 切回 Orchestrator → 结果决策
  ├── Stage 3: Generator-Evaluator 模式
  │     ├── Phase 0-6: Exec Runner → 代码生成/执行 → 自动切回（无 Checkpoint）
  │     ├── Phase 7-9: Exec Inference → 假设检验/质检 → 切回 Orchestrator → Checkpoint
  │     └── Generator-Evaluator 差异比对 → 纳入 Stage 3.5 门闸输入
  ├── Stage 3.5: QC Inspector → 结果质量门闸 → 切回 Orchestrator → 结果决策
  └── Stage 4: Report Expert → 生成报告 → 最终交付
```

### 6.2 Agent 角色定义

> Agent 角色卡（核心行为 + 禁止行为）、接棒协议（Handoff 格式）、异常上报规则（INFO/WARN/BLOCK 三级别）详见 [agents/AGENTS.md](../../agents/AGENTS.md) 和 [agents/protocol.md](../../agents/protocol.md)。

| 阶段 | Agent | 文件 |
|------|-------|------|
| Stage 1 | Data Validator | [data_validator_agent.md](../../agents/data_validator_agent.md) |
| Stage 1.5/2.5/3.5 | QC Inspector | [qc_inspector_agent.md](../../agents/qc_inspector_agent.md) |
| Stage 2 | Method Consultant | [method_consultant_agent.md](../../agents/method_consultant_agent.md) |
| Stage 3 (P0-6) | Exec Runner | [exec_runner_agent.md](../../agents/exec_runner_agent.md) |
| Stage 3 (P7-9) | Exec Inference | [exec_inference_agent.md](../../agents/exec_inference_agent.md) |

---

## 7. Error Handling & Rollback

### 7.1 阶段内错误

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| 数据验证发现严重问题 | 回到 Stage 1 重新清洗 | 标记数据"不可用"，阻断后续直到修复或用户书面接受风险 |
| **Stage 1.5 门闸未通过** | **退回 Stage 1 修订** | **3+ 项或关键项 5/6/7/9 未通过必须修订；回退 ≥2 次走收敛检测** |
| SAP 审查不通过 | 回到 Stage 2 修改计划 | 用户接受风险后继续，记录偏差 |
| **Stage 2.5 门闸未通过** | **退回 Stage 2 修订 SAP** | **3+ 项或关键项 3/5/7 未通过必须修订；回退 ≥2 次走收敛检测** |
| 质检发现严重错误 | 回到 Stage 3 修正分析 | 标记结果"待验证"，阻断进入 Stage 4 直到修正 |
| **Stage 3.5 门闸未通过** | **退回 Stage 3 修正** | **3+ 项或关键项 1/3/4/10/11/12/13 未通过必须修正；回退 ≥2 次走收敛检测** |
| 前置产物缺失 | 提示用户补充 | 用户确认跳过后继续，记录风险 |

**错误处理优先级**：🚫 Blocking(门闸 3+ 项未通过)→必须退回 ⚠️ Conditional(1-2 项未通过)→可带条件通过 🔵 Informational(前置缺失)→可跳过记录偏差。多阶段错误同时发生：从最早出错阶段开始修复。

**多信号冲突处理**：同时提供 SAP + 原始数据 → 从 Stage 1 开始，告知 SAP 在 Stage 2 使用 | "做分析"但有清洗数据+分析结果 → 优先 Stage 3 | "完整流程"+"快速"矛盾 → 以"完整流程"为准，推荐分步执行

### 7.2 偏差记录
分析执行中偏离 SAP：1.记录偏差内容 → 2.评估偏差影响 → 3.与用户讨论是否可接受 → 4.如不可接受，回退修正

### 7.3 收敛检测与回退循环控制

> 防止同一环节无限循环回退。每个质量门闸维护独立回退计数器，最大回退 2 次。

| 门闸 | 计数器名 | 最大回退次数 |
|------|---------|------------|
| Stage 1.5 → Stage 1 | `retry_data_prep` | 2 |
| Stage 2.5 → Stage 2 | `retry_sap` | 2 |
| Stage 3.5 → Stage 3 | `retry_analysis` | 2 |

**收敛判断**：
- 第 1 次退回 → 正常修改，记录偏差原因
- 第 2 次退回 → 警告 + 5 Whys 根因分析 → 用户选择：[A] 修改方案重试 / [B] 降低标准(书面记录) / [C] 换人审查
- 第 3 次退回 → BLOCK：转入偏差记录模式，走 M6 Checkpoint，用户书面接受风险，结果标注 ⚠️ [CONVERGED WITH DEVIATIONS]

**Early-stopping 辅助**：未通过项数无减少 → BLOCK（展示回退历史对比表，用户选 [A]换审查者/[B]换方法/[C]接受风险） | 未通过项数减少但 ≥3 关键项未通过 → BLOCK（用户选 [A]修改设计/[B]降级目标/[C]接受风险）。每次回退必须记录"上一次修改内容"+"本次检查结果是否有改善"。

**IRON RULE**: 回退超过 2 次后，不得自动再次退回。必须走 MANDATORY Checkpoint 让用户决策。

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
| `/msra --resume` | 从上次中断处恢复（读取 Passport） | 智能检测 |

---

## 9. Interaction Examples

### Example 1: 全流程（高效模式）
```
用户: /msra 我有一份RCT的原始数据，想完成整个分析流程

→ 检测到原始数据 → 从 Stage 1 开始 → 用户选 [2] 高效模式
  Stage 1: 数据验证和清洗 → [MANDATORY] 清洗完成，继续？
  → Stage 1.5: 数据质量门闸（9项）→ [MANDATORY] 门闸结果，继续？
  → Stage 2: 制定分析计划 → [SLIM] EDA 展示后确认 → [MANDATORY] SAP 审查通过
  → Stage 2.5: SAP 质量门闸（8项）→ [MANDATORY] 门闸通过，继续？
  → Stage 3: 执行分析 → [SLIM] 质检结果确认
  → Stage 3.5: 结果质量门闸（14项）→ [MANDATORY] 门闸通过，继续？
  → Stage 4: 生成报告 → [MANDATORY] 合规检查，最终确认
完成 ✅（6 次 MANDATORY + 2 次 SLIM，比旧版 19 次暂停减少约 58%）
```

### Example 2: 中途切入
```
用户: /msra 我的数据已经清洗好了，帮我制定分析计划
→ 检测到已清洗数据 → 从 Stage 2 开始 → 前置检查: 确认清洗日志存在 → 用户选 [2] 高效模式 → Stage 2: 制定分析计划 → ...
```

### Example 3: 跳到报告（极速模式）
```
用户: /msra 分析做完了，帮我生成CONSORT报告
→ 检测到分析结果 → 从 Stage 4 开始 → 前置检查: 确认 Stage 3.5 门闸通过 + 质检报告存在 → 用户选 [3] 极速模式 → Stage 4: 生成报告 → 自动完成 ✅（仅在合规检查发现问题时暂停）
```

### Example 4: 新手详细引导
```
用户: /msra 我有一份数据，但不太确定该怎么做统计
→ 检测到原始数据 → 从 Stage 1 开始 → 用户选 [1] 详细引导 → 每个步骤都有完整 Dashboard → Stage 1: 每步暂停讨论 → Stage 1.5: 逐项解释门闸结果 → ...每个 Stage 后 FULL checkpoint
```

---

## 反例与黑名单

> **完整反模式目录参见**：[shared/anti-patterns/medical_stats_anti_patterns.md](../../shared/anti-patterns/medical_stats_anti_patterns.md)（A1/A2/B2/B3 + 编排器角色禁忌 + 阶段跳转禁忌 + 进度追踪禁忌）
