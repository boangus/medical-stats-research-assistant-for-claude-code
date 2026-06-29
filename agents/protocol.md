# MSRA Agent 异常上报协议 (Protocol)

> 异常上报规则与 Agent 间通信协议。本文档与 [AGENTS.md](AGENTS.md) 互补：
> - **AGENTS.md**：Agent 角色定义 + Handoff 格式 + 协作流程 + 冲突解决
> - **protocol.md**（本文）：异常上报三级机制（INFO/WARN/BLOCK）+ 升级路径 + 通信规范
>
> 版本: 1.0.0 | 2026-06-25 | 引用方：pipeline/SKILL.md

---

## 1. 异常上报三级框架

所有 Agent 在执行过程中发现异常时，必须按以下三级框架分类上报。级别决定了处理路径与阻断行为。

### 1.1 级别定义

| 级别 | 名称 | 阻断行为 | 典型场景 | 处理路径 |
|------|------|---------|---------|---------|
| **INFO** | 信息记录 | 不阻断 | 非关键偏差、可接受的方法调整、文档补充 | 记录到 audit_log，继续流转 |
| **WARN** | 警告升级 | 条件阻断 | 假设违反但结论稳健、敏感性分析差异、边界场景 | 标记风险 → Orchestrator 评估 → 条件通过或退回 |
| **BLOCK** | 阻断升级 | 强制阻断 | 门闸失败、Generator-Evaluator 严重差异、数据完整性问题 | 强制退回前一阶段 → 用户决策 |

### 1.2 判定标准

**INFO（信息记录）**：
- 数值偏差 < 5% 且结论方向一致
- 非关键检查项未通过（质量门闸 7-8/9 通过）
- 文档格式问题（不影响分析结论）
- 可接受的方法微调（如连续变量分箱方式变更）

**WARN（警告升级）**：
- 假设检验违反（正态性/方差齐性/比例风险）但稳健性分析支持结论
- 敏感性分析与主分析结论方向一致但效应量差异 > 10%
- 质量门闸条件通过（1-2 项非关键项未通过）
- Generator-Evaluator 差异在可接受范围但需记录

**BLOCK（阻断升级）**：
- 质量门闸阻断（关键项未通过或通过率 < 阈值）
- Generator-Evaluator 严重差异（结论方向相反或 p 值跨阈值）
- 数据完整性问题（缺失率超阈值、数据库未锁定、盲态审核未完成）
- SAP 严重偏离（未经批准的方法变更）
- 3 轮 Debug 仍失败（Exec Runner）
- 同一阶段退回 ≥ 2 次（收敛检测触发）

---

## 2. 上报格式

### 2.1 标准上报结构

所有异常上报必须采用以下结构化格式：

```markdown
## [LEVEL] 异常报告

### 元数据
- report_id: {唯一标识}
- stage: {Stage X.Y}
- agent: {上报 Agent}
- timestamp: {ISO 8601}
- level: INFO | WARN | BLOCK

### 异常描述
{简明描述异常内容}

### 证据
- 预期: {预期值/状态}
- 实际: {实际值/状态}
- 偏差: {量化偏差，如适用}

### 影响评估
- 对结论的影响: {无/轻微/显著/致命}
- 可逆性: {可逆/不可逆}
- 波及范围: {当前阶段/下游阶段/全局}

### 建议处理
{Agent 建议的处理方式}
```

### 2.2 上报渠道

| 级别 | 上报对象 | 渠道 | 时效 |
|------|---------|------|------|
| INFO | audit_log | 写入 `{stage_dir}/audit_log.jsonl` | 立即 |
| WARN | Orchestrator + audit_log | MessageBus 优先级消息 + audit_log | 立即 |
| BLOCK | Orchestrator + User + audit_log | MessageBus 阻断消息 + 人机回环 | 立即，暂停流转 |

---

## 3. 升级路径

### 3.1 INFO 升级路径

```
Agent 发现 INFO 级异常
  → 记录到 audit_log
  → 继续当前阶段流转
  → 在 Handoff 中汇总 INFO 记录
```

**规则**：INFO 不暂停流转，但必须在阶段 Handoff 中汇总，供下游 Agent 知晓。

### 3.2 WARN 升级路径

```
Agent 发现 WARN 级异常
  → 标记风险到 audit_log
  → 上报 Orchestrator（MessageBus WARN 消息）
  → Orchestrator 评估影响
    ├── 轻微影响 → 条件通过，记录风险，继续流转
    ├── 中等影响 → 请求用户确认后继续
    └── 显著影响 → 升级为 BLOCK，触发退回
```

**规则**：WARN 必须由 Orchestrator 评估后决定是否继续。条件通过时必须在 Passport 中记录风险标记。

### 3.3 BLOCK 升级路径

```
Agent 发现 BLOCK 级异常
  → 立即暂停当前阶段流转
  → 上报 Orchestrator（MessageBus BLOCK 消息）
  → Orchestrator 触发人机回环
  → 用户决策
    ├── 退回前一阶段修正
    ├── 调整分析计划（需重新审查 SAP）
    └── 终止流程
```

**规则**：BLOCK 强制暂停流转，必须经用户决策后才能继续。退回前一阶段时，Passport 状态回滚。

### 3.4 收敛检测

同一阶段退回次数达到阈值时触发收敛检测：

| 退回次数 | 处理 |
|---------|------|
| 1 次 | 正常退回，修正后重试 |
| 2 次 | 标记为"收敛风险"，WARN 上报 |
| ≥ 3 次 | 强制 BLOCK，要求用户介入根因分析 |

---

## 4. 与 AGENTS.md 的关系

### 4.1 职责划分

| 文档 | 内容 |
|------|------|
| [AGENTS.md](AGENTS.md) | Agent 角色定义、Handoff 格式、协作流程、冲突解决系统、级联错误防御 |
| **protocol.md（本文）** | 异常上报三级机制、升级路径、通信规范 |

### 4.2 异常上报映射

本文 §1.2 的三级框架与 AGENTS.md §2 异常上报表的映射关系：

| AGENTS.md 触发条件 | protocol.md 级别 |
|-------------------|-----------------|
| 数据无法验证 | BLOCK（Data Validator） |
| SAP 多项未通过 | BLOCK（QC Inspector → 退回 Method Consultant） |
| 代码反复失败 | WARN（3 轮 Debug 失败）→ BLOCK（5 轮失败） |
| Generator-Evaluator 差异 | WARN（轻微）或 BLOCK（严重） |
| 结果不一致 | WARN（QC Inspector → 用户决策） |

### 4.3 冲突解决联动

当异常上报涉及 Agent 间冲突时，按 AGENTS.md §冲突解决系统处理：
- TRIVIAL/MINOR 级别冲突 → 对应 INFO
- MODERATE 级别冲突 → 对应 WARN
- SIGNIFICANT/CRITICAL 级别冲突 → 对应 BLOCK

---

## 5. 通信规范

### 5.1 MessageBus 消息优先级

| 级别 | 优先级 | 投递保证 |
|------|--------|---------|
| INFO | LOW（1） | 至少一次，允许异步 |
| WARN | MEDIUM（3） | 至少一次，立即投递 |
| BLOCK | HIGH（5） | 恰好一次，同步投递，等待确认 |

### 5.2 消息格式

```json
{
  "message_id": "uuid",
  "type": "exception_report",
  "level": "INFO | WARN | BLOCK",
  "source_agent": "exec_runner | exec_inference | qc_inspector | ...",
  "stage": "Stage X.Y",
  "timestamp": "ISO 8601",
  "payload": {
    "description": "...",
    "evidence": {"expected": "...", "actual": "..."},
    "impact": "...",
    "suggestion": "..."
  },
  "requires_ack": true
}
```

### 5.3 确认机制

- **INFO**：无需确认，异步写入 audit_log
- **WARN**：Orchestrator 必须在 1 个处理周期内确认
- **BLOCK**：Orchestrator + User 必须确认，超时（默认 5 分钟）自动升级为用户告警

---

## 6. 审计与追溯

所有异常上报（无论级别）必须写入 audit_log，确保可追溯：

```
{stage_dir}/audit_log.jsonl
  每行一条 JSON 记录，包含：
  - report_id, timestamp, level, agent, stage
  - description, evidence, impact, suggestion
  - resolution（处理结果）, resolved_by, resolved_at
```

审计日志由 `resources/contracts/audit/audit_jsonl.schema.json` 定义 Schema，由 `src/shared/reproducibility/pipeline_auditor.py` 验证完整性。

---

## 参考

- [AGENTS.md](AGENTS.md) — Agent 角色定义 + Handoff 格式 + 协作协议
- [multi_agent_specification.md](multi_agent_specification.md) — 多 Agent 规范详述
- [../resources/shared/checkpoint_protocol.md](../resources/shared/checkpoint_protocol.md) — 三级检查点协议（MANDATORY/SLIM/ADAPTIVE）
- [../resources/contracts/audit/](../resources/contracts/audit/) — 审计 Schema 定义
