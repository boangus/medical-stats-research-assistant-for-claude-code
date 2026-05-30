# MSRA Agent Collaboration Protocol

> 定义 Agent 间协作规则：接棒格式、异常上报、状态同步。
> 版本: 0.1.0 | 2026-05-29

---

## 1. 接棒格式 (Handoff Protocol)

每个 Agent 完成任务切换到下一 Agent 时，必须输出标准接棒消息：

```markdown
## [Agent Name] → [Next Agent] Handoff

### 产物清单
| 产物 | 路径 | 状态 |
|------|------|------|
| 清洗后数据 | data/cleaned.csv | ✅ |
| 清洗日志 | data/cleaning_log.md | ✅ |

### 验证要点
[下一 Agent 需要重点检查的内容]

### 已知风险
[需要下一 Agent 注意的问题]

### 待用户决策
[当前阶段需要用户确认的事项]
```

### 接棒检查清单

| 方向 | 必须传递的内容 |
|------|--------------|
| Data Validator → Method Consultant | 变量清单、缺失模式、清洗决策记录 |
| Method Consultant → Code Executor | SAP（含方法选择依据）、Estimands 表、敏感性分析计划 |
| Code Executor → QC Inspector | 分析代码路径、执行日志、自检结果、[SKIP] 记录 |
| QC Inspector → 下一阶段 | 门闸报告（通过的标记 + 未通过的原因 + 风险评估） |

---

## 2. 异常上报协议 (Escalation)

### 上报级别

```
🟢 INFO   → 信息性，无需处理
🟡 WARN   → 需关注但不阻断
🔴 BLOCK  → 阻断流程，必须处理
```

### 上报通道

| 级别 | 谁处理 | 响应时限 |
|------|--------|---------|
| 🟢 INFO | Orchestrator 记录 | 无 |
| 🟡 WARN | Orchestrator 评估 → 可能问用户 | 阶段结束时 |
| 🔴 BLOCK | Orchestrator 暂停流程 → 立即询问用户 | 立即 |

### Blocking 触发条件

```yaml
Data Validator BLOCK:
  - 数据无法读取（格式不识别/文件损坏）
  - 缺失率 > 50% 的关键变量
  - 逻辑校验发现不可修复的矛盾

Method Consultant BLOCK:
  - 无法确定研究设计类型
  - 结局变量定义冲突
  - 用户提供的 SAP 与数据不匹配

Code Executor BLOCK:
  - 3 轮 Debug 后代码仍失败
  - 关键依赖包无法安装
  - 数据与 SAP 冲突（如变量缺失）

QC Inspector BLOCK:
  - SAP 质量门闸 3+ 项未通过
  - 结果质量门闸 3+ 项未通过
  - 关键分析结果不可复现
```

---

## 3. 状态同步

### 阶段状态机

```
INACTIVE → ACTIVE（Agent 正在工作）
         → BLOCKED（Agent 上报阻断）
         → COMPLETED（Agent 完成工作）
         → REVIEW（QC 正在审查）
         → RETURNED（退回修正）
```

### Orchestrator 状态追踪

在每个 Checkpoint 展示：

```
╔══════════════════════════════════════════════════╗
║           MSRA Agent Collaboration Status         ║
╠══════════════════════════════════════════════════╣
║                                                   ║
║  Active Agent: [名字]                             ║
║  Status:      [ACTIVE/REVIEW/BLOCKED/COMPLETED]   ║
║                                                   ║
║  Collaboration Chain:                             ║
║    Stage 1 [Data Validator]    → ✅ 完成           ║
║    Stage 2 [Method Consultant] → ▶ 正在进行        ║
║    Stage 2.5 [QC Inspector]    → ⏳ 等待           ║
║                                                   ║
║  Recent Handoffs:                                 ║
║    [时间] Data Validator → Method Consultant      ║
║           → 传递: 变量清单 + 清洗日志              ║
║                                                   ║
║  Blockers: 无                                     ║
╚══════════════════════════════════════════════════╝
```

---

## 4. 协作反例

| # | 禁止行为 | 原因 | 正确做法 |
|---|---------|------|---------|
| 1 | 同一个 Agent 既产生又审查自己的产出 | 自检盲区，质量问题会漏出 | 跨角色验证 |
| 2 | 跳过一个 Agent 直接进入下一阶段 | 跳过数据验证可能导致分析错误 | 必须按角色顺序执行 |
| 3 | Blocking 问题自行猜测处理 | 用户决策权被剥夺 | 🔴 BLOCK → 上报 Orchestrator → 询问用户 |
| 4 | 接棒时不传递已知风险 | 下一 Agent 重复踩坑 | 接棒必须包含已知问题 |
| 5 | Agent 工作超时静默 | Orchestrator 无法判断状态 | 每 3 轮工具调用后主动报告进度 |



