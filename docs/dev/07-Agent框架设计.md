# Agent 框架设计 — Multi-Agent 架构详述

> **目录**: `agents/` | **版本**: v1.1.0 | **更新日期**: 2026-06-22

---

## 1. 框架概述

MSRA 是一个 **Claude Code 插件**，其 Multi-Agent 协作通过插件的 Skill 调度机制实现。`agents/` 目录下的 Python 代码是架构参考实现，当前未被插件实际调用。

### 1.1 两种使用模式

MSRA Agent 框架支持两种使用模式，适用于不同场景：

| 模式 | 说明 | 适用场景 | 当前状态 |
|------|------|---------|---------|
| **模式 A: Skill 调度** | Agent 角色由 LLM 的 Skill 调度实现，每个 Skill 内置角色定义和协作规则 | 日常使用、快速迭代、低代码需求 | ✅ **主模式（插件实际运行方式）** |
| **模式 B: Python Agent 代码** | 使用 Python 代码实现 IAgent 接口，通过 MessageBus/TaskQueue 进行异步通信 | 高并发、需要持久化、需要监控指标 | 🔧 **代码已开发，未集成到插件** |

#### 模式 A: Skill 调度模式（插件实际运行方式）

这是 **MSRA 插件实际运行的方式**。用户在 Claude Code 中输入 `/msra` 等命令 → `manifest.json` 路由到对应 SKILL.md → LLM 按 Skill 定义的角色和规则执行。

Agent 角色（Data Validator、Method Consultant、Exec Runner 等）以 LLM 上下文中的角色扮演形式存在，不是独立的 Python 进程。

```
用户命令 (/msra-data, /msra-plan, /msra-exec, ...)
    │
    ▼
Pipeline Orchestrator (skills/pipeline/SKILL.md)
    │  解析意图 → 路由到对应 Skill → LLM 扮演对应 Agent 角色
    ▼
各阶段 Skill (data-prep, analysis-plan, analysis-exec, ...)
    │  每个 Skill 内置角色定义、协作规则、质量门闸
    │  Agent 间信息通过 Pipeline 编排器的上下文传递
    ▼
质量门闸 (Gate 1.5 / 2.5 / 3.5 / 5.5 / 5.8)
    │  Skill 内置阻断式检查逻辑（LLM 按检查清单执行）
    ▼
输出产物
```

**运行方式**: 用户在 Claude Code 中输入 `/msra` → `manifest.json` 路由到 `skills/pipeline/SKILL.md` → LLM 按 Skill 定义的角色和规则执行

**Agent 角色**: 由 LLM 在对话中扮演，不是独立进程。例如 `data-prep` Skill 告诉 LLM "你是一位医学数据质量专家"，LLM 就以这个角色执行数据验证。

**协作机制**: Pipeline 编排器在上下文中传递信息（上一阶段的输出作为下一阶段的输入），质量门闸以检查清单形式由 LLM 逐项检查。

**插件命令注册**: 12 个命令通过 `manifest.json` 注册，每个命令的 `entry_point` 指向对应的 SKILL.md

**适用场景**: 日常使用、快速迭代、Claude Code 插件形态

#### 模式 B: Python Agent 代码模式（代码已开发，未集成到实际流程）

`agents/` 目录下的 Python 代码是 **已经开发完成的参考实现**，包含完整的 Agent 框架：

| 文件 | 内容 | 开发状态 |
|------|------|---------|
| `agents/core/interfaces.py` | IAgent 接口、AgentMessage、Handoff、ConflictReport 等数据结构 | ✅ 已开发 |
| `agents/core/base_agent.py` | BaseAgent 基类 | ✅ 已开发 |
| `agents/core/communication.py` | MessageBus + TaskQueue | ✅ 已开发 |
| `agents/core/cache.py` | MultiLevelCache (L1 内存 + L2 磁盘) | ✅ 已开发 |
| `agents/core/conflict_resolution.py` | ConflictResolver (自动/投票/仲裁/用户决策) | ✅ 已开发 |
| `agents/core/registry.py` | Agent 注册表 + 服务发现 | ✅ 已开发 |
| `agents/core/monitor.py` | 资源监控 + 告警 | ✅ 已开发 |
| `agents/implementations/data_validator_agent.py` | DataValidatorAgent | ✅ 已开发 |
| `agents/implementations/method_consultant_agent.py` | MethodConsultantAgent | ✅ 已开发 |
| `agents/implementations/exec_runner_agent.py` | ExecRunnerAgent | ✅ 已开发 |
| `agents/implementations/exec_inference_agent.py` | ExecInferenceAgent | ✅ 已开发 |
| `agents/implementations/qc_inspector_agent.py` | QCInspectorAgent | ✅ 已开发 |
| `tests/test_agent_framework.py` | 单元测试 (28 个用例) | ✅ 已开发 |
| `tests/test_agent_message_passing.py` | 消息传递测试 (18 个用例) | ✅ 已开发 |

**但是**: 这些代码目前 **没有被 Pipeline 的实际运行流程调用**。Pipeline 运行时走的是模式 A（Skill 调度），而不是 `import agents` 然后实例化 Agent 对象。

**价值**: 作为架构规范和未来演进方向。如果需要将 MSRA 从 Skill 模式迁移到独立服务模式（例如部署为 Web 服务、支持多用户并发），这些代码可以直接使用。

#### 两种模式的关系

```
当前状态:
  Pipeline 运行 → 模式 A (Skill 调度) ← 实际使用
  agents/ 代码  → 模式 B (Python Agent) ← 参考实现 + 未来演进

未来可能:
  Pipeline 运行 → 模式 B (Python Agent) ← 如果需要独立服务化
```

#### 模式选择指南

| 场景 | 推荐模式 | 说明 |
|------|---------|------|
| 日常数据分析 | 模式 A (Skill 调度) | 开箱即用，无需额外配置 |
| 快速原型验证 | 模式 A | 直接在 Claude Code 中运行 |
| 需要高并发处理 | 模式 B (Python Agent) | 需要额外开发集成层 |
| 需要持久化任务队列 | 模式 B | 需要额外开发集成层 |
| 需要详细的监控指标 | 模式 B | 需要额外开发集成层 |
| 需要自定义冲突解决策略 | 模式 B | 需要额外开发集成层 |

#### 模式 A vs 模式 B 对比

| 维度 | 模式 A (Skill 调度) | 模式 B (Python Agent) |
|------|---------------------|----------------------|
| **运行方式** | LLM 在对话中扮演 Agent 角色 | 独立 Python 进程/协程 |
| **Agent 间通信** | Pipeline 编排器上下文传递 | MessageBus 异步消息 |
| **质量门闸** | LLM 按检查清单执行 | QCInspectorAgent 代码执行 |
| **状态管理** | 对话上下文 | TaskQueue + Cache |
| **开发复杂度** | 低（写 Skill 即可） | 高（需要 Python 代码） |
| **可扩展性** | 受限于 LLM 上下文长度 | 可扩展到多进程/分布式 |
| **当前状态** | ✅ 生产使用 | 🔧 代码已开发，未集成 |

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| **接口统一** | 所有 Agent 实现 IAgent 标准接口 |
| **消息驱动** | Agent 间通过 MessageBus 异步通信 |
| **冲突可解** | 内置 ConflictResolver，支持仲裁 |
| **缓存分层** | L1(内存) + L2(磁盘) 多级缓存 |
| **任务优先** | 优先级任务队列，支持依赖管理 |

---

## 2. 核心接口 (IAgent)

### 2.1 接口定义

```python
class IAgent(ABC):
    @property
    @abstractmethod
    def agent_id(self) -> str: ...

    @property
    @abstractmethod
    def agent_type(self) -> str: ...

    @property
    @abstractmethod
    def capabilities(self) -> List[AgentCapability]: ...

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool: ...

    @abstractmethod
    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Handoff: ...

    @abstractmethod
    async def receive_message(self, message: AgentMessage) -> AgentMessage: ...

    @abstractmethod
    async def send_message(self, message: AgentMessage) -> bool: ...

    @abstractmethod
    async def report_conflict(self, conflict: ConflictReport) -> str: ...

    @abstractmethod
    async def get_status(self) -> AgentStatus: ...

    @abstractmethod
    async def shutdown(self) -> bool: ...
```

### 2.2 Agent 状态机

```
IDLE → PROCESSING → COMPLETED
  │        │            │
  │        ▼            │
  │     WAITING ────────┘
  │        │
  │        ▼
  │     BLOCKED → ESCALATED
  │        │
  ▼        ▼
FAILED   CANCELLED
```

### 2.3 资源监控模块 (ResourceMonitor)

**文件**: `agents/core/monitor.py`

ResourceMonitor 实现资源监控仪表板，追踪 Agent 执行状态和系统资源：

| 监控维度 | 说明 |
|----------|------|
| **任务指标** | 完成数、失败数、成功率、平均执行时间 |
| **Token 消耗** | 输入/输出 Token 统计 |
| **缓存效率** | L1/L2 命中率 |
| **冲突统计** | 冲突次数和解决策略分布 |
| **队列状态** | 任务队列大小和运行数 |

**告警机制**:

| 告警类型 | 默认阈值 | 说明 |
|----------|---------|------|
| `token_usage_per_task` | 50,000 | 单任务 Token 超限 |
| `task_failure_rate` | 10% | 失败率超限 |
| `cache_hit_rate` | 50% | 缓存命中率过低 |
| `execution_time` | 300s | 单任务执行超时 |
| `queue_size` | 100 | 队列积压 |

**使用方式**:
```python
from agents.core.monitor import get_monitor, init_monitor

# 初始化（可自定义阈值）
monitor = init_monitor(alert_thresholds={"token_usage_per_task": 80000})

# 记录任务
await monitor.record_task_start(agent_id="exec_runner", task_id="t-001")
await monitor.record_task_complete(agent_id="exec_runner", task_id="t-001",
                                   execution_time=45.2, tokens_input=3000, tokens_output=1500)

# 获取仪表板数据
dashboard = await monitor.get_dashboard_data()
```

### 2.4 快速上手示例

完整示例见 `agents/examples/quick_start.py`，演示如何：
- 初始化 Agent 框架
- 创建并注册 Agent
- 通过 MessageBus 发送消息
- 使用 ResourceMonitor 追踪执行

---

## 3. 核心组件

### 3.1 MessageBus (异步消息队列)

**文件**: `agents/core/communication.py`

| 功能 | 说明 |
|------|------|
| 优先级消息 | 1-10 优先级，1 最高 |
| 消息确认 | ACK/NACK 机制 |
| TTL 支持 | 消息过期自动丢弃 |
| 重试机制 | 可配置重试次数 |

**消息类型**:

| 类型 | 说明 |
|------|------|
| `request` | 请求消息 |
| `response` | 响应消息 |
| `ack` | 确认消息 |
| `nack` | 拒绝消息 |
| `block` | 阻断消息 |
| `escalate` | 升级消息 |

### 3.2 TaskQueue (优先级任务队列)

**文件**: `agents/core/communication.py`

| 功能 | 说明 |
|------|------|
| 优先级排序 | TaskPriority 枚举 (CRITICAL=1, BATCH=9) |
| 依赖管理 | TaskDependency 支持 blocks/must_complete/should_complete |
| 状态追踪 | PENDING → QUEUED → RUNNING → COMPLETED/FAILED |
| 超时控制 | 可配置任务超时 |

### 3.3 MultiLevelCache (多级缓存)

**文件**: `agents/core/cache.py`

```
L1 Cache (内存)
    │  命中 → 直接返回
    │  未命中
    ▼
L2 Cache (磁盘)
    │  命中 → 加载到 L1 → 返回
    │  未命中
    ▼
计算 → 写入 L1 + L2 → 返回
```

| 功能 | 说明 |
|------|------|
| TTL 支持 | 缓存过期自动失效 |
| 标签管理 | 按标签批量失效 |
| 大小限制 | 可配置 L1/L2 容量 |
| 访问统计 | 记录访问次数和时间 |

### 3.4 ConflictResolver (冲突解决)

**文件**: `agents/core/conflict_resolution.py`

**冲突级别**:

| 级别 | 说明 | 处理方式 |
|------|------|---------|
| TRIVIAL (1) | 轻微差异 | 记录即可 |
| MINOR (2) | 小差异 | 条件通过 |
| MODERATE (3) | 中等差异 | 需确认 |
| SIGNIFICANT (4) | 显著差异 | 阻断 |
| CRITICAL (5) | 严重差异 | 立即上报 |

**冲突类型**:

| 类型 | 说明 |
|------|------|
| DATA_INCONSISTENCY | 数据不一致 |
| METHOD_DISAGREEMENT | 方法分歧 |
| RESULT_DIVERGENCE | 结果偏离 |
| QUALITY_GATE_FAILURE | 质量门闸失败 |
| RESOURCE_CONTENTION | 资源竞争 |
| PRIORITY_CONFLICT | 优先级冲突 |

**解决策略**:

| 策略 | 说明 |
|------|------|
| AUTO_RESOLVE | 自动解决（仅 TRIVIAL/MINOR） |
| VOTING | 投票决定 |
| ARBITRATION | 仲裁者决定 |
| USER_DECISION | 用户决定 |
| ROLLBACK | 回滚到上一状态 |
| MERGE | 合并多个方案 |

---

## 4. Agent 实现

### 4.1 Data Validator Agent

**文件**: `agents/implementations/data_validator_agent.py`

| 属性 | 值 |
|------|-----|
| agent_id | `data_validator` |
| agent_type | `validator` |
| 对应 Skill | `data-prep` |

**职责**:
- 数据结构验证
- 缺失值检测与处理
- 异常值检测
- 变量构造
- 盲态审核流程

**边界**:
- ✅ 建议清洗策略
- ✅ 自动执行常规清洗
- ❌ 自行决定删除数据
- ❌ 跳过盲态审核流程

### 4.2 Method Consultant Agent

**文件**: `agents/implementations/method_consultant_agent.py`

| 属性 | 值 |
|------|-----|
| agent_id | `method_consultant` |
| agent_type | `consultant` |
| 对应 Skill | `analysis-plan` |

**职责**:
- 探索性数据分析 (EDA)
- 估计目标定义 (ICH E9(R1) 五要素)
- 统计方法选择决策树
- SAP 撰写与审查
- 样本量计算

**边界**:
- ✅ 独立完成 EDA → 生成 EDA 报告
- ✅ 提供多种合理方法选项 → 等待用户选择
- ❌ 在未讨论的情况下单方面选择统计方法
- ❌ 跳过敏感性分析计划

### 4.3 Exec Runner Agent

**文件**: `agents/implementations/exec_runner_agent.py`

| 属性 | 值 |
|------|-----|
| agent_id | `exec_runner` |
| agent_type | `executor` |
| 对应 Skill | `analysis-exec` (Phase 0-6) |
| MAX_DEBUG_ROUNDS | 5 |

**职责**:
- R/Python 代码生成
- 最多 5 轮自愈 Debug
- 按 SAP 变量构造逻辑生成分析变量
- [SKIP] 诚实标记

**边界**:
- ✅ 独立生成并执行代码
- ✅ 最多 5 轮自愈 Debug
- ❌ 偏离 SAP 内容
- ❌ 自行解读结果或下统计推断
- ❌ 5 轮 Debug 仍失败时静默跳过

### 4.4 Exec Inference Agent

**文件**: `agents/implementations/exec_inference_agent.py`

| 属性 | 值 |
|------|-----|
| agent_id | `exec_inference` |
| agent_type | `inference` |
| 对应 Skill | `analysis-exec` (Phase 7-9) |

**职责**:
- 独立假设检验
- 质量检查
- Generator-Evaluator 比对

### 4.5 QC Inspector Agent

**文件**: `agents/implementations/qc_inspector_agent.py`

| 属性 | 值 |
|------|-----|
| agent_id | `qc_inspector` |
| agent_type | `inspector` |
| 对应 Skill | 跨阶段 |

**职责**:
- 数据质量门闸 (Stage 1.5, 9 项)
- SAP 质量门闸 (Stage 2.5, 8 项)
- 结果质量门闸 (Stage 3.5, 9 项)
- 数值一致性检查
- 异常结果标记
- 报告规范合规检查
- 结果复现性验证

**边界**:
- ✅ 独立执行所有检查项
- ✅ 标记通过/警告/阻断级别
- ⚠️ 阻断级未通过 → 强制退回前一阶段
- ❌ 修改分析结果或 SAP 内容

---

## 5. 数据结构

### 5.1 AgentMessage

```python
@dataclass
class AgentMessage:
    message_id: str           # UUID
    sender: str               # 发送者 agent_id
    recipient: str | list     # 接收者
    message_type: str         # request/response/ack/nack/block/escalate
    payload: Dict[str, Any]   # 消息内容
    timestamp: datetime       # 时间戳
    correlation_id: str       # 关联 ID（用于追踪）
    ttl: int = 300            # 生存时间（秒）
    priority: int = 5         # 优先级 (1-10, 1最高)
    retry_count: int = 0      # 已重试次数
    max_retries: int = 3      # 最大重试次数
```

### 5.2 Handoff (接棒格式)

```python
@dataclass
class Handoff:
    agent_name: str                    # Agent 名称
    completed_work: List[str]          # 已完成工作
    artifacts: Dict[str, str]          # 产物路径 → 描述
    verification_method: str           # 验证方法
    known_issues: List[str]            # 已知问题
    pending_decisions: List[str]       # 待决策项
    data_summary: Dict[str, Any]       # 数据摘要
    timestamp: datetime                # 时间戳
    next_agent: str                    # 下一个 Agent
    status: AgentStatus                # 状态
```

### 5.3 ConflictReport

```python
@dataclass
class ConflictReport:
    conflict_id: str                   # UUID
    source_agent: str                  # 来源 Agent
    target_agent: str                  # 目标 Agent
    conflict_type: str                 # 冲突类型
    conflict_level: ConflictLevel      # 冲突级别
    description: str                   # 描述
    evidence: Dict[str, Any]           # 证据
    resolution_suggestions: List[str]  # 解决建议
    timestamp: datetime                # 时间戳
    resolution_status: str             # 解决状态
```

---

## 6. 协作流程

```
Stage 1: Orchestrator → Data Validator (构建数据)
                      → QC Inspector 审查 (Gate 1.5)

Stage 2: Orchestrator → Method Consultant (制定SAP)
                      → QC Inspector 审查 (Gate 2.5)

Stage 3: Orchestrator → Exec Runner (生成代码 Phase 0-6)
                      → Exec Inference (推断检验 Phase 7-9)
                      → QC Inspector 审查 (Gate 3.5)

Stage 4: Orchestrator → Report Expert (生成报告)

冲突发生 → ConflictResolver → [AUTO/VOTING/ARBITRATION/USER]
```

---

## 7. 混合模式架构（Skill + 子 Agent）

### 7.1 架构概述

**模式 C: Skill + 子 Agent 混合模式** 是 MSRA 的新一代运行架构。编排层保持 Skill 调度，关键执行角色拆分为独立子 Agent（通过 WorkBuddy Agent 工具启动），获得上下文隔离和并行执行能力。

```
用户命令 (/msra)
    │
    ▼
Pipeline Orchestrator (Skill, 主对话上下文)
    │  意图检测 → 阶段路由 → 进度追踪 → 人机回环
    │
    ├─ Data Validator (子 Agent, 独立上下文) ──── 可与因果探索并行
    │    └─ 输出: 清洗后数据 + 验证报告 → Material Passport
    │
    ├─ QC Inspector (子 Agent, 独立上下文) ──── 可与下一阶段准备并行
    │    └─ 输出: 质量门闸报告 (PASS/WARN/FAIL)
    │
    ├─ Exec Runner (主对话内, 紧耦合循环)
    │    └─ 输出: 分析代码 + 结果表 + 图表
    │
    ├─ Exec Inference (子 Agent, 独立上下文) ── 真正独立于 Exec Runner
    │    └─ 输出: 推断验证报告 + Generator-Evaluator 差异
    │
    └─ Method Consultant (子 Agent, 独立上下文)
         └─ 输出: SAP + Estimands
```

### 7.2 Agent 拆分决策

| Agent | 拆分方式 | 理由 | 并行收益 |
|-------|---------|------|---------|
| **QC Inspector** | ✅ 子 Agent | 纯只读审查，不修改数据/代码；检查逻辑高度独立 | Gate 检查可与下一阶段准备并行 |
| **Exec Inference** | ✅ 子 Agent | Generator-Evaluator 需要独立上下文才能真正"独立验证" | 推断检验可与报告生成准备并行 |
| **Data Validator** | ✅ 子 Agent | 数据验证/清洗/EDA 有明确输入输出边界 | 数据质量检查可与因果探索并行 |
| **Method Consultant** | ✅ 子 Agent | SAP 制定需要深度统计学知识，独立上下文可加载更多参考 | 需与 Data Validator 频繁交互 |
| **Exec Runner** | ❌ 主对话内 | 代码生成-执行-自愈是紧密耦合循环，拆分会增加延迟 | — |
| **Pipeline Orchestrator** | ❌ 主对话内 | 必须保持单一控制源，拆分导致状态同步噩梦 | — |

### 7.3 上下文隔离策略

| 维度 | Skill 模式（旧） | 混合模式（新） |
|------|-----------------|---------------|
| **Exec Inference 看到 Exec Runner 的推理过程** | ✅ 是（同一上下文） | ❌ 否（独立上下文） |
| **QC Inspector 看到分析代码的生成过程** | ✅ 是 | ❌ 否（只看产物） |
| **Gate 检查与下一阶段** | 串行 | 可并行 |
| **上下文窗口占用** | 所有角色共享 | 各子 Agent 独立 |

**隔离的核心价值**: Exec Inference 不再能看到 Exec Runner 的推理过程，确保 Generator-Evaluator 比对是真正独立的。QC Inspector 只审查产物文件，不被生成过程中的"解释"影响判断。

### 7.4 子 Agent 生命周期

```
Orchestrator 决定启动子 Agent
    │
    ├─ 准备输入: 产物文件路径 + Handoff Schema
    │
    ├─ 启动子 Agent (WorkBuddy Agent 工具)
    │    ├─ subagent_type: "general-purpose"
    │    ├─ prompt: 角色定义 + 输入数据 + 期望输出格式
    │    └─ run_in_background: true (可选并行)
    │
    ├─ 子 Agent 执行 (独立上下文)
    │    ├─ 读取输入文件
    │    ├─ 执行任务
    │    └─ 写入输出文件 (产物)
    │
    ├─ Orchestrator 收到完成通知
    │    ├─ 读取子 Agent 输出
    │    ├─ 验证 Handoff Schema 完整性
    │    └─ 决定下一步
    │
    └─ 异常处理
         ├─ 子 Agent 超时 → 降级到 Skill 模式
         ├─ 子 Agent 失败 → 重试 1 次，再失败降级
         └─ 输出 Schema 不合规 → 要求子 Agent 修正
```

### 7.5 Handoff 协议（子 Agent 间）

子 Agent 间通过 **文件交接** 而非内存传递：

| 交接方式 | 说明 |
|----------|------|
| **输入** | Orchestrator 在 prompt 中指定产物文件路径 |
| **输出** | 子 Agent 将结果写入指定路径的文件 |
| **验证** | Orchestrator 读取输出文件，验证 Schema 完整性 |
| **持久化** | 所有交接记录写入 Material Passport |

**标准 Handoff 格式**:
```markdown
## Handoff: [Agent Name]

### 已完成工作
- [任务1]: [结果]
- [任务2]: [结果]

### 产物路径
- [产物1]: [文件路径]
- [产物2]: [文件路径]

### 验证方法
- [如何验证产物正确性]

### 已知问题
- [问题描述]

### 待决策项
- [需要用户/Orchestrator 决定的事项]
```

### 7.6 降级策略

当子 Agent 不可用时，自动降级到 Skill 模式：

| 场景 | 降级方式 | 用户感知 |
|------|---------|---------|
| 子 Agent 启动失败 | 回退到 Skill 内角色扮演 | 无感知（功能不变） |
| 子 Agent 超时 (>300s) | 回退到 Skill 内角色扮演 | 提示"已降级到兼容模式" |
| 子 Agent 输出 Schema 不合规 | 要求修正 1 次，再失败则降级 | 提示"子 Agent 输出异常" |
| 用户显式禁用子 Agent | 直接使用 Skill 模式 | 用户主动选择 |

**降级不影响功能正确性**，只失去上下文隔离和并行执行的优势。

### 7.7 并行执行场景

| 场景 | 并行内容 | 收益 |
|------|---------|------|
| Stage 1 完成后 | Gate 1.5 检查 ∥ Stage 1.8 探索性分析准备 | 节省等待时间 |
| Stage 3 Phase 6 完成后 | Exec Inference 推断检验 ∥ 报告模板准备 | 节省等待时间 |
| Stage 2 完成后 | Gate 2.5 检查 ∥ Stage 3 环境准备 | 节省等待时间 |

### 7.8 模式选择指南（更新）

| 场景 | 推荐模式 | 说明 |
|------|---------|------|
| 日常数据分析 | **模式 C (混合)** | 默认推荐，兼顾隔离性和易用性 |
| 快速原型验证 | 模式 A (Skill) | 无需子 Agent 启动开销 |
| 需要严格独立验证 | **模式 C (混合)** | Exec Inference 独立上下文 |
| 高并发/多用户 | 模式 B (Python Agent) | 需要额外开发集成层 |
| 调试/开发中 | 模式 A (Skill) | 单上下文更易调试 |

---

## 8. 相关文件

| 文件 | 说明 |
|------|------|
| `agents/AGENTS.md` | 团队架构文档 |
| `agents/core/interfaces.py` | IAgent 接口定义 |
| `agents/core/base_agent.py` | BaseAgent 基类 |
| `agents/core/communication.py` | MessageBus + TaskQueue |
| `agents/core/cache.py` | MultiLevelCache |
| `agents/core/conflict_resolution.py` | ConflictResolver |
| `agents/core/registry.py` | Agent 注册表 |
| `agents/core/monitor.py` | 监控模块 |
| `agents/implementations/data_validator_agent.py` | Data Validator |
| `agents/implementations/method_consultant_agent.py` | Method Consultant |
| `agents/implementations/exec_runner_agent.py` | Exec Runner |
| `agents/implementations/exec_inference_agent.py` | Exec Inference |
| `agents/implementations/qc_inspector_agent.py` | QC Inspector |
