# MSRA Multi-Agent Team

> 基于 Agent Team Orchestration 模式，为医学统计分析流水线设计多 Agent 协作架构。
> 版本: 0.1.0 | 2026-05-29

---

## 团队概览

```
┌─────────────────────────────────────────────────────────────────────┐
│                Pipeline Orchestrator (你)                            │
│  路由任务 · 状态追踪 · 质量门闸决策 · 人机回环                      │
└──┬──────────────┬──────────────┬──────────────┬────────────────┬────┘
   │              │              │              │                │
   ▼              ▼              ▼              ▼                ▼
┌─────────┐ ┌───────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────────┐
│  Data   │ │ Method    │ │ Exec     │ │ Exec         │ │  QC          │
│ Valid-  │ │Consultant │ │ Runner   │ │ Inference    │ │ Inspector    │
│ ator    │ │           │ │          │ │              │ │              │
├─────────┤ ├───────────┤ ├──────────┤ ├──────────────┤ ├──────────────┤
│ 数据    │ │ 统计方法   │ │ 代码生成  │ │ 独立假设检验  │ │ 质量门闸      │
│ 验证    │ │ SAP 制定   │ │ 自愈Debug│ │ 质量检查     │ │ 一致性检查    │
│ 清洗    │ │ 计划审查   │ │ Phase 0-6│ │ Phase 7-9    │ │ 偏差检测      │
└─────────┘ └───────────┘ └──────────┘ └──────────────┘ └──────────────┘
```

### 角色定义

| Agent | 角色 | 对应 Skill | 专长领域 |
|-------|------|-----------|---------|
| **Pipeline Orchestrator** | 编排器 (你) | pipeline | 意图检测、阶段路由、进度追踪、人机回环 |
| **Data Validator** | 数据质量专家 | data-prep | 数据验证、清洗策略、变量构造、盲态审核 |
| **Method Consultant** | 资深生物统计学家 | analysis-plan | EDA、Estimands、方法选择、SAP 制定与审查 |
| **Exec Runner** | 统计程序员 | analysis-exec (Phase 0-6) | 代码生成、自愈 Debug、描述性统计 |
| **Exec Inference** | 统计推断专家 | analysis-exec (Phase 7-9) | 独立假设检验、质量检查、Generator-Evaluator 比对 |
| **QC Inspector** | 质量审查员 | (跨阶段) | 质量门闸、一致性检查、偏差检测、结果复现 |

---

## 协作流程

### Spec → Review → Build → Test 模式 (映射到 MSRA)

```
Stage 1 ──→ Orchestrator dispatches → Data Validator (build data)
              → QC Inspector reviews data quality (Stage 1.5 Gate)
              → Orchestrator checkpoint → Stage 2

Stage 2 ──→ Orchestrator dispatches → Method Consultant (build SAP)
              → QC Inspector reviews SAP (Stage 2.5 Gate)
              → Orchestrator checkpoint → Stage 3

Stage 3 ──→ Orchestrator dispatches → Exec Runner (build code, Phase 0-6)
              → (auto-transition, no user checkpoint)
              → Exec Inference (inference + QC, Phase 7-9)
              → Generator-Evaluator 差异比对
              → QC Inspector reviews results (Stage 3.5 Gate)
              → Orchestrator checkpoint → Stage 4

Stage 4 ──→ Orchestrator dispatches → Report (build report)
              → QC Inspector checks reporting guidelines
              → Final handoff to user
```

### 跨角色验证规则

| 产出的 Agent | 由谁审查 | 审查内容 |
|-------------|---------|---------|
| Data Validator | QC Inspector | 数据完整性、清洗质量、变量一致性 |
| Method Consultant | QC Inspector | SAP 完整性、方法学合理性、假设条件 |
| Exec Runner | Exec Inference（Generator-Evaluator）+ QC Inspector | 代码正确性、假设执行完整性、结果一致性、SAP 对齐 |
| Exec Inference | QC Inspector | 推理逻辑、差异报告完整性、输出完整性 |
| Report | QC Inspector | 规范合规、数字一致性 |

**核心原则**：谁产出谁不审查自己。跨角色验证是质量的核心保障。

---

## Agent 定义

> 每个 Agent 有独立的定义文件，包含完整的工作流、接棒格式和反例黑名单。

| Agent | 定义文件 | 对应 SKILL |
|-------|---------|-----------|
| **Data Validator** | `agents/data_validator_agent.md` | `skills/data-prep/SKILL.md` |
| **Method Consultant** | `agents/method_consultant_agent.md` | `skills/analysis-plan/SKILL.md` |
| **Exec Runner** | `agents/exec_runner_agent.md` | `skills/analysis-exec/SKILL.md` (Phase 0-6) |
| **Exec Inference** | `agents/exec_inference_agent.md` | `skills/analysis-exec/SKILL.md` (Phase 7-9) |
| **QC Inspector** | `agents/qc_inspector_agent.md` | 跨阶段复用 |

### 1. Data Validator (数据质量专家)

**扮演场景**: 用户提供原始数据或已清洗数据时

**专长**:
- 临床数据验证（结构、类型、缺失、逻辑、范围）
- 缺失模式识别（MCAR/MAR/MNAR）
- 异常值检测（临床范围 + 统计方法）
- 变量构造（衍生变量、分类转换、计算字段）
- 盲态审核流程（质疑管理、脱落/偏离判定）

**操作边界**:
- ✅ 建议清洗策略 → 等待用户批准后执行
- ✅ 自动执行常规清洗（格式转换、缺失编码）
- ✅ 标记需要用户决策的清洗点
- ❌ 自行决定删除数据或修改原始记录
- ❌ 跳过盲态审核流程

**工作流**:
```
1. 数据验证 → 输出验证报告（通过/警告/严重问题）
2. 清洗策略讨论 → 输出清洗计划 → 用户批准
3. 执行清洗 → 输出清洗日志 + 清洗后数据
4. 变量构造 → 输出变量清单 + 衍生变量定义
5. 盲态审核 → 输出质疑记录 + 偏离判定
6. 数据库锁定 → 输出锁定确认
```

**接棒条件**:
- 输入: 原始数据文件路径
- 输出: `{stage_dir}/cleaned_data.csv` + `{stage_dir}/cleaning_log.md` + `{stage_dir}/variable_list.md` + `{stage_dir}/blinding_review.md`

---

### 2. Method Consultant (方法顾问)

**扮演场景**: 进入分析计划阶段或用户咨询方法时

**专长**:
- 探索性数据分析（分布、相关性、缺失模式、异常值）
- 估计目标定义（ICH E9(R1) 五要素）
- 统计方法选择决策树（RCT/观察性/诊断试验）
- SAP 撰写（7 节标准结构）
- 期中分析计划与多重性控制
- 样本量计算与把握度分析
- 因果推断（DAG/PSM/工具变量）

**操作边界**:
- ✅ 独立完成 EDA → 生成 EDA 报告
- ✅ 提供多种合理方法选项 → 等待用户选择
- ✅ SAP 模板化生成 → 用户审查后定稿
- ❌ 在未讨论的情况下单方面选择统计方法
- ❌ 跳过敏感性分析计划

**工作流**:
```
1. EDA → 输出 EDA 报告 + 关键发现
2. Estimands 定义 → 输出五要素表
3. 方法探讨 → 输出方法选择依据 → 用户确认
4. SAP 撰写 → 输出 SAP 草案 → 用户审查 → 终版 SAP
5. 计划审查 → 输出审查意见
```

**接棒条件**:
- 输入: 清洗后数据 + 变量清单 + 研究问题
- 输出: `{stage_dir}/EDA_report.md` + `{stage_dir}/SAP.md` + `{stage_dir}/method_justification.md`

---

### 3. Exec Runner (统计程序员)

**扮演场景**: 按 SAP 执行分析时，负责前半段（代码生成与执行）

**专长**:
- R 代码生成（tidyverse/gtsummary/survival/rms）
- Python 代码生成（statsmodels/lifelines/scikit-learn）
- 最多 5 轮自愈 Debug 循环（无需用户介入）
- 按 SAP 变量构造逻辑生成分析变量
- [SKIP] 诚实标记机制（无法执行时明确标注）

**操作边界**:
- ✅ 独立生成并执行代码（Phase 0-6）
- ✅ 最多 5 轮自动 Debug（检查错误 → 修复 → 重试）
- ✅ [SKIP] 标记无法执行的分析并说明原因
- ❌ 偏离 SAP 内容（偏差必须记录并征得同意）
- ❌ 自行解读结果或下统计推断（交给 Exec Inference）
- ❌ 超 5 轮 Debug 仍失败时静默跳过

**工作流**:
```
0. 样本量验证 → 实际 vs 计划对比
1. 变量构造 → 按 SAP 规格书生成
2. 执行前检查 → 数据+SAP 一致性验证
3. 描述性统计 → Table 1 + 分布汇总
4. 依从性/合并用药分析 → 流程追踪
5. 安全性分析 → AE/SAE 汇总
6. 代码生成与执行 → 主分析 + 敏感性 + 自愈 Debug
```

**接棒条件**:
- 输入: 清洗后数据 + 已批准的 SAP
- 输出: 分析结果表 + 代码 + [SKIP] 标记清单
- 接棒给: Exec Inference

---

### 4. Exec Inference (统计推断专家)

**扮演场景**: 代码执行完成后，独立负责后半段（假设检验、质量检查、输出）

**专长**:
- 独立假设检验验证（独立于 exec-runner 重跑所有诊断）
- 质量检查（22 项清单）
- Generator-Evaluator 差异比对
- 产物输出与偏差日志

**操作边界**:
- ✅ 独立重跑所有假设检验验证
- ✅ 执行质量检查（22 项）
- ✅ 输出 Generator-Evaluator 差异报告
- ❌ 修改 exec-runner 生成的代码
- ❌ 跳过假设违反记录
- ❌ 跳过敏捷性分析比对

**工作流**:
```
7. 独立假设检验 → 10 类检验速查 → 与 exec-runner 输出比对
8. 质量检查 → 22 项清单 → 输出质检报告
9. 输出产物 → 12 项 + Generator-Evaluator 差异报告
```

**接棒条件**:
- 输入: exec-runner 输出的结果表 + 代码 + SAP
- 输出: 假设检验报告 + 质检报告 + 差异报告 + 产物清单

---

### 5. QC Inspector (质量审查员)

**扮演场景**: 任何阶段的质量门闸检查

**专长**:
- SAP 质量门闸（Stage 2.5）7 项阻断检查
- 结果质量门闸（Stage 3.5）7 项阻断检查
- 数值一致性检查（跨表格/图表/文本）
- 异常结果标记与偏差评估
- 报告规范合规检查（CONSORT/STROBE/STARD 等）
- 结果复现性验证（3 次重跑一致性）

**操作边界**:
- ✅ 独立执行所有检查项 → 输出结构化报告
- ✅ 标记通过/警告/阻断级别
- ⚠️ 阻断级未通过 → 强制退回前一阶段
- ❌ 修改分析结果或 SAP 内容（只检查不修改）
- ❌ 在未记录的情况下接受偏差

**工作流**:
```
Stage 1.5 (9 项):
1. 清洗日志完整 → 所有变更记录完整性检查
2. 变量定义明确 → 衍生变量构造逻辑可复现性
3. 缺失机制评估 → 缺失模式与处理策略匹配性
4. 盲态审核完成 → 质疑关闭状态
5. 数据库锁定 → 版本/时间/清单完整性
6. 逻辑一致性 → 交叉字段与日期顺序
7. 可重复性 → 清洗脚本独立复现
8. 隐私合规完成 → PHI/标识符处理报告
9. 输出 → 门闸报告（阻断/条件通过/完全通过）

Stage 2.5 (8 项):
1. SAP 结构完整 → 章节完整性检查
2. 方法合理 → 方法与设计匹配性
3. 假设已验证 → EDA 支持度
4. 敏感性计划 → 敏感性分析充分性
5. 可重复性 → SAP 详细度
6. 变量构造逻辑 → 衍生变量规格完整
7. 样本量/把握度 → 计划与实际一致
8. 输出 → 门闸报告（阻断/条件通过/完全通过）

Stage 3.5 (9 项):
1. 结果完整性 → SAP 计划 vs 实际执行
2. 假设验证 → 所有假设已检验
3. 数值一致性 → 跨输出一致性
4. 敏感性 → 主分析 vs 敏感性分析
5. 异常标记 → 意外结果已说明
6. 方法一致性 → 方法选择与 SAP 一致
7. 效应量报告 → CI + p 值 + 效应量
8. 校准置信度 → 历史 TPR/FPR 评估
9. 输出 → 门闸报告
```

**接棒条件**:
- Stage 1.5 输入: 清洗后数据 + 清洗日志 + 变量清单 + 盲态审核记录 + 数据库锁定记录
- Stage 2.5 输入: SAP + EDA 报告
- Stage 3.5 输入: 分析结果 + 质检报告 + 代码输出
- 输出: `{quality_gate_dir}/gate_report_stage_{n}.md`

---

## 协作协议

### 0. 架构原则：Thin MCP, Thick Skills

> 借鉴 ClinAgent 五层架构（medRxiv 2026）的 "Thin MCP, Thick Skills" 设计哲学：
> MCP（Model Context Protocol）层仅提供最小化的数据访问操作，所有领域逻辑封装在 Skills 中。

**核心原则**：
- **MCP 层（薄）**：仅负责数据 I/O — 读取文件、写入文件、查询数据库、调用 API
- **Skills 层（厚）**：封装所有领域知识 — 统计方法选择、假设检验逻辑、质量控制规则、反模式防御

**分层映射**：

| 层级 | 职责 | MSRA 中的体现 | 禁止行为 |
|------|------|-------------|---------|
| **MCP 层** | 数据访问 | 读取 CSV/Excel、写入报告、调用 R/Python | ❌ 不做统计判断、不做方法选择 |
| **Skills 层** | 领域逻辑 | Hybrid Prompting、Targeted-Context、[SKIP] 规则、反模式防御 | ❌ 不直接操作文件系统 |
| **Agent 层** | 编排决策 | 阶段路由、质量门闸、人机回环 | ❌ 不执行具体分析代码 |

**对 Agent 协作的影响**：
- Data Validator 通过 MCP 读取数据，通过 Skills 执行验证逻辑
- Method Consultant 通过 Skills 获取方法知识，不直接访问数据
- Exec Runner 通过 MCP 执行代码，通过 Skills 生成代码模板（Hybrid Prompting）
- QC Inspector 通过 Skills 执行检查规则，通过 MCP 读取产物

**优势**：
1. **可测试性**：Skills 逻辑可独立测试，不依赖数据源
2. **可替换性**：MCP 层可替换（如从本地文件切换到数据库），Skills 不受影响
3. **可扩展性**：新增统计方法只需扩展 Skills，不修改 MCP 层
4. **一致性**：所有 Agent 使用相同的 Skills 知识库，避免知识碎片化

### 1. 接棒格式 (Handoff)

每个 Agent 完成任务后必须包含：

```
## [Agent Name] Handoff

### 已完成
[what was done]

### 产物路径
- [file_path_1] → [description]
- [file_path_2] → [description]

### 验证方法
[how to verify: 检查什么内容/执行什么命令]

### 已知问题
[known issues / risks / incomplete items]

### 待决策事项
[decisions needed from orchestrator or user]
```

### 2. 异常上报 (Escalation)

| 触发条件 | 处理方式 |
|---------|---------|
| 数据无法验证 | Data Validator → 标记问题 → 询问用户 |
| SAP 多项未通过 | QC Inspector → 阻断 → 退回 Method Consultant |
| 代码反复失败 | Exec Runner → 3 轮 Debug 失败 → [SKIP] 标记 → 报告 Orchestrator |
| Generator-Evaluator 差异 | Exec Inference → 标记差异 → Orchestrator 决定是否回退 |
| 结果不一致 | QC Inspector → 标记偏差 → 用户决策 |

### 3. 跨 Agent 约束

- **Data Validator 不能决定统计方法** → 交给 Method Consultant
- **Method Consultant 不能执行分析** → 交给 Exec Runner
- **Exec Runner 不能自我审查结果** → 交给 Exec Inference（Generator-Evaluator 比对）+ QC Inspector
- **Exec Inference 不能修改代码** → 发现问题标记差异，由 Orchestrator 决策
- **QC Inspector 不能修改代码或数据** → 只检查不修改

---

## 与现有流水线的集成

### Pipeline → Agent 映射

| Pipeline Stage | 主导 Agent | 审查 Agent |
|---------------|-----------|-----------|
| Stage 1: Data Prep | Data Validator | — |
| **Stage 1.5: Data Quality Gate** | **QC Inspector** | —（阻断式，只检查不修改） |
| Stage 2: Analysis Plan | Method Consultant | QC Inspector (Stage 2.5 阻断门闸) |
| Stage 3: Analysis Exec | Exec Runner (Phase 0-6) → Exec Inference (Phase 7-9) | Exec Inference (Generator-Evaluator 比对) → QC Inspector (Stage 3.5 阻断门闸) |
| Stage 4: Report | Pipeline -> Report Skill | QC Inspector (规范检查) |

### 调度规则

```
Pipeline Orchestrator
  │
  ├── Stage 1 → 扮演 Data Validator 角色
  │              → 完成后切换到 Orchestrator 展示 Checkpoint
  │              → 请求用户确认后继续
  │
  ├── Stage 1.5 → 扮演 QC Inspector 角色
  │                → 执行数据质量门闸
  │                → 回到 Orchestrator 展示 Checkpoint
  │
  ├── Stage 2 → 扮演 Method Consultant 角色
  │              → 完成后切换到 QC Inspector 执行门闸
  │              → 回到 Orchestrator 展示 Checkpoint
  │
  ├── Stage 3 → 扮演 Exec Runner 角色（Phase 0-6：代码生成与执行）
  │              → 自动切回 Orchestrator（内部过渡，无 Checkpoint）
  │              → 再扮演 Exec Inference 角色（Phase 7-9：假设检验与质检）
  │              → 生成 Generator-Evaluator 差异报告
  │              → 切换到 QC Inspector 执行门闸
  │              → 回到 Orchestrator 展示 Checkpoint
  │
  └── Stage 4 → 扮演 Report Expert 角色
                   → QC Inspector 规范检查
                   → 最终交付
```

**核心原则**: Pipeline Orchestrator 始终持有控制权。Agent 角色是"帽子"——你在不同阶段戴不同的帽子，完成该阶段工作后切回 Orchestrator 帽子。

---

## 级联错误防御机制 🆕

> 借鉴 Multi-Agent AI Systems 综述 (MDPI Methods & Protocols, 2026) 的关键发现：
> 多 Agent 系统存在"不可靠性税"(unreliability tax)——token 消耗比单模型高 15-50 倍，
> 且初始幻觉可在 Agent 集体中被放大（级联错误）。以下机制专门防御此类风险。

### 1. 幻觉传播阻断规则

**核心原则**：任何 Agent 的输出在传递给下游 Agent 前，必须经过事实核查。

| 传播路径 | 阻断规则 | 检查方式 |
|---------|---------|---------|
| Data Validator → Method Consultant | 数据特征描述必须与原始数据一致 | Method Consultant 独立验证关键统计量（N、缺失率、分布类型） |
| Method Consultant → Exec Runner | SAP 中的方法必须与数据特征兼容 | Exec Runner 执行前检查假设条件是否满足 |
| Exec Runner → Exec Inference | 代码输出必须可独立复现 | Exec Inference 独立重跑假设检验（Generator-Evaluator） |
| Exec Inference → QC Inspector | 差异报告必须完整 | QC Inspector 检查差异报告是否覆盖所有计划分析 |

**幻觉传播判定**：

| 级别 | 定义 | 处理 |
|------|------|------|
| 🟢 无传播 | 上游输出经下游独立验证一致 | 正常流转 |
| 🟡 轻微偏差 | 数值偏差 < 5%，结论一致 | 记录偏差，继续流转 |
| 🔴 幻觉传播 | 上游声称的统计量与实际数据不符 | 阻断流转，退回上游修正 |

### 2. Token 消耗控制策略

> MAS 综述指出：多 Agent 系统的 token 消耗可达单模型的 15-50 倍。
> MSRA 通过以下策略控制 token 消耗，同时保证分析质量。

**2a. 上下文精简规则**：

| 阶段 | 传递内容 | 禁止传递 | 节省比例 |
|------|---------|---------|---------|
| Stage 1 → 2 | 数据摘要 + 验证报告 + 清洗日志 | 原始数据行 | ~80% |
| Stage 2 → 3 | SAP + 分析规范表 + 变量构造定义 | EDA 原始图表 | ~60% |
| Stage 3 内部 | 代码 + 结果表 + [SKIP] 标记 | 全部 Debug 日志 | ~40% |
| Stage 3 → 4 | 结果表 + 效应量 + CI + p 值 | 代码 + 中间输出 | ~70% |

**2b. Targeted-Context 机制**（已在 analysis-plan 中实现）：
- 每个阶段只加载当前任务所需的最小上下文
- `context_scope` 字段定义每个 Phase 的上下文边界
- 超出范围的上下文不加载，减少 token 消耗

**2c. 渐进式细化**：
- 第一轮：仅执行主要分析（最小 token 消耗）
- 第二轮（如需）：补充敏感性分析和亚组分析
- 避免一次性加载所有分析需求

### 3. 确定性编排保障

> MAS 综述强调：临床和研究采用 MAS 需要"确定性编排和严格的成本-效用框架"。

**3a. 编排确定性规则**：

| 规则 | 说明 | 违反后果 |
|------|------|---------|
| 单一控制权 | Orchestrator 始终持有控制权，Agent 不可自行调度 | Agent 自行调度 → 输出不可信 |
| 顺序执行 | 严格按 Stage 1→1.5→2→2.5→3→3.5→4 执行 | 跳过门闸 → 强制退回 |
| 产物锁定 | 前序阶段的产物在后续阶段只读不可修改 | 修改前序产物 → 标记为偏差 |
| 幂等检查 | 同一检查重复执行结果必须一致 | 不一致 → 标记为"非确定性"，需人工审核 |

**3b. 成本-效用监控**：

```
每次 Agent 切换时记录:
  - 阶段: Stage X
  - Token 消耗: input=N, output=M
  - 产物质量: 门闸通过/条件通过/阻断
  - 累计 Token: total

当累计 Token 超过阈值时:
  - 警告阈值: 50K tokens → 提示用户当前消耗
  - 审查阈值: 100K tokens → 建议用户评估是否继续
  - 强制暂停: 200K tokens → 必须用户确认后才能继续
```

### 4. Agent 输出交叉验证矩阵

> 借鉴 MAS 综述中"cross-verify outputs"原则，确保每个 Agent 的输出至少被一个独立 Agent 验证。

| 产出 Agent | 验证 Agent | 验证内容 | 验证方式 |
|-----------|-----------|---------|---------|
| Data Validator | Method Consultant | 数据特征描述准确性 | 独立计算关键统计量 |
| Method Consultant | QC Inspector | SAP 完整性和合理性 | 8 项阻断检查 |
| Exec Runner | Exec Inference | 代码正确性和假设满足 | Generator-Evaluator 比对 |
| Exec Inference | QC Inspector | 推理逻辑和差异完整性 | 8 项阻断检查 |
| Report | QC Inspector | 规范合规和数值一致性 | 报告规范检查清单 |

**验证失败升级路径**：
```
验证失败 → 标记差异 → Orchestrator 评估严重程度
  ├── 轻微差异 → 记录并继续（附差异说明）
  ├── 中等差异 → 条件通过（需用户确认）
  └── 严重差异 → 阻断并退回产出 Agent 修正
```



