---
name: agent_interface_specification
description: "MSRA Multi-Agent Interface Specification - Standardized Agent Contract"
version: "1.0.0"
date: "2026-06-22"
author: "MSRA Team"
status: "draft"
---

# MSRA Agent Interface Specification v1.0

> 所有Agent必须遵循本规范定义的标准接口，确保互操作性和可扩展性。

---

## 1. Agent Interface Definition

### 1.1 Core Interface (IAgent)

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

class AgentStatus(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING = "waiting"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"

class ConflictLevel(Enum):
    TRIVIAL = 1      # 轻微差异，记录即可
    MINOR = 2        # 小差异，条件通过
    MODERATE = 3     # 中等差异，需确认
    SIGNIFICANT = 4  # 显著差异，阻断
    CRITICAL = 5     # 严重差异，立即上报

@dataclass
class AgentMessage:
    """标准消息格式"""
    message_id: str
    sender: str
    recipient: Union[str, List[str]]
    message_type: str  # request/response/ack/nack/block/escalate
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    ttl: int = 300
    priority: int = 5  # 1-10, 1最高
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class Handoff:
    """标准接棒格式"""
    agent_name: str
    completed_work: List[str]
    artifacts: Dict[str, str]
    verification_method: str
    known_issues: List[str]
    pending_decisions: List[str]
    data_summary: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    next_agent: Optional[str] = None
    status: AgentStatus = AgentStatus.IDLE

@dataclass
class ConflictReport:
    """冲突报告格式"""
    conflict_id: str
    source_agent: str
    target_agent: str
    conflict_type: str
    conflict_level: ConflictLevel
    description: str
    evidence: Dict[str, Any]
    resolution_suggestions: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    resolution_status: str = "pending"

@dataclass
class AgentCapability:
    """Agent能力描述"""
    name: str
    version: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    constraints: List[str]
    dependencies: List[str]
    quality_metrics: Dict[str, str]

class IAgent(ABC):
    """Agent标准接口"""

    @property
    @abstractmethod
    def agent_id(self) -> str:
        pass

    @property
    @abstractmethod
    def agent_type(self) -> str:
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[AgentCapability]:
        pass

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Handoff:
        pass

    @abstractmethod
    async def receive_message(self, message: AgentMessage) -> AgentMessage:
        pass

    @abstractmethod
    async def send_message(self, message: AgentMessage) -> bool:
        pass

    @abstractmethod
    async def report_conflict(self, conflict: ConflictReport) -> str:
        pass

    @abstractmethod
    async def get_status(self) -> AgentStatus:
        pass

    @abstractmethod
    async def shutdown(self) -> bool:
        pass
```

---

## 2. Communication Protocol

### 2.1 Message Exchange Patterns

```python
class MessagePattern(Enum):
    REQUEST_RESPONSE = "request_response"
    PUBLISH_SUBSCRIBE = "publish_subscribe"
    COMMAND_ACK = "command_ack"
    EVENT_NOTIFICATION = "event_notification"
    CONFLICT_ESCALATION = "conflict_escalation"

class CommunicationProtocol:
    async def send_request(
        self, sender: str, recipient: str, payload: Dict[str, Any],
        correlation_id: Optional[str] = None, priority: int = 5, timeout: int = 300
    ) -> AgentMessage:
        message = AgentMessage(
            message_id=self._generate_id(),
            sender=sender, recipient=recipient,
            message_type="request", payload=payload,
            correlation_id=correlation_id, priority=priority, ttl=timeout
        )
        return await self._send_with_retry(message)

    async def acknowledge(
        self, original_message_id: str, status: str,
        result: Optional[Dict[str, Any]] = None, error: Optional[str] = None
    ) -> AgentMessage:
        return AgentMessage(
            message_id=self._generate_id(),
            sender="current_agent", recipient=original_message_id,
            message_type="ack" if status == "ack" else "nack",
            payload={"original_id": original_message_id, "status": status,
                    "result": result, "error": error},
            correlation_id=original_message_id
        )

    async def escalate(
        self, source_agent: str, conflict: ConflictReport, escalate_to: str = "arbitrator"
    ) -> AgentMessage:
        return AgentMessage(
            message_id=self._generate_id(), sender=source_agent,
            recipient=escalate_to, message_type="escalate",
            payload={"conflict_report": asdict(conflict)}, priority=1
        )
```

### 2.2 Message Queue Implementation

```python
class PriorityQueue:
    def __init__(self):
        self._queues: Dict[int, List[QueuedMessage]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def enqueue(self, message: AgentMessage) -> str:
        async with self._lock:
            queued = QueuedMessage(message=message, queued_at=datetime.now())
            self._queues[message.priority].append(queued)
            return message.message_id

    async def dequeue(self) -> Optional[QueuedMessage]:
        async with self._lock:
            for priority in range(1, 11):
                if self._queues[priority]:
                    return self._queues[priority].pop(0)
            return None

class MessageQueue:
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0,
                 exponential_backoff: bool = True):
        self._queues: Dict[str, PriorityQueue] = defaultdict(PriorityQueue)
        self._subscriptions: Dict[str, List[Callable]] = defaultdict(list)
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._exponential_backoff = exponential_backoff

    async def publish(self, recipient: str, message: AgentMessage) -> str:
        return await self._queues[recipient].enqueue(message)

    async def subscribe(self, agent_id: str, callback: Callable) -> None:
        self._subscriptions[agent_id].append(callback)
```

---

## 3. Conflict Resolution System

### 3.1 Conflict Types and Resolution Strategies

```python
class ConflictType(Enum):
    DATA_INCONSISTENCY = "data_inconsistency"
    METHOD_DISAGREEMENT = "method_disagreement"
    RESULT_DIVERGENCE = "result_divergence"
    QUALITY_GATE_FAILURE = "quality_gate_failure"
    RESOURCE_CONTENTION = "resource_contention"
    PRIORITY_CONFLICT = "priority_conflict"
    TIMING_CONFLICT = "timing_conflict"
    SEMANTIC_MISMATCH = "semantic_mismatch"

class ResolutionStrategy(Enum):
    AUTO_RESOLVE = "auto_resolve"
    VOTING = "voting"
    ARBITRATION = "arbitration"
    USER_DECISION = "user_decision"
    ROLLBACK = "rollback"
    SKIP = "skip"
    MERGE = "merge"

class ConflictResolver:
    def __init__(self, arbitrator_agent):
        self._arbitrator = arbitrator_agent
        self._strategy_map = {
            ConflictType.DATA_INCONSISTENCY: ResolutionStrategy.AUTO_RESOLVE,
            ConflictType.METHOD_DISAGREEMENT: ResolutionStrategy.ARBITRATION,
            ConflictType.RESULT_DIVERGENCE: ResolutionStrategy.VOTING,
            ConflictType.QUALITY_GATE_FAILURE: ResolutionStrategy.ARBITRATION,
        }
        self._level_strategy_min = {
            ConflictLevel.TRIVIAL: ResolutionStrategy.AUTO_RESOLVE,
            ConflictLevel.MINOR: ResolutionStrategy.AUTO_RESOLVE,
            ConflictLevel.MODERATE: ResolutionStrategy.VOTING,
            ConflictLevel.SIGNIFICANT: ResolutionStrategy.ARBITRATION,
            ConflictLevel.CRITICAL: ResolutionStrategy.USER_DECISION,
        }

    async def resolve(self, conflict: ConflictReport) -> ConflictResolution:
        base_strategy = self._strategy_map.get(ConflictType(conflict.conflict_type),
                                              ResolutionStrategy.ARBITRATION)
        min_strategy = self._level_strategy_min.get(conflict.conflict_level)
        strategy = self._choose_stricter(base_strategy, min_strategy)

        if strategy == ResolutionStrategy.AUTO_RESOLVE:
            return await self._auto_resolve(conflict)
        elif strategy == ResolutionStrategy.VOTING:
            return await self._voting_resolve(conflict)
        elif strategy == ResolutionStrategy.ARBITRATION:
            return await self._arbitration_resolve(conflict)
        elif strategy == ResolutionStrategy.USER_DECISION:
            return await self._user_decision(conflict)
        return await self._default_resolve(conflict)
```

### 3.2 Arbitrator Agent

```python
class ArbitratorAgent:
    def __init__(self, config: Dict[str, Any]):
        self.agent_id = "arbitrator"
        self._rules = self._load_arbitration_rules()

    def _load_arbitration_rules(self) -> Dict[str, Any]:
        return {
            "data_inconsistency": {
                "primary_source": "data_validator",
                "fallback": "method_consultant",
                "tie_breaker": "qc_inspector"
            },
            "method_disagreement": {
                "primary_source": "method_consultant",
                "fallback": "exec_inference",
                "tie_breaker": "qc_inspector"
            },
            "result_divergence": {
                "primary_source": "exec_inference",
                "fallback": "qc_inspector",
                "tie_breaker": "orchestrator"
            },
            "quality_gate_failure": {
                "primary_source": "qc_inspector",
                "fallback": "source_agent",
                "tie_breaker": "user"
            }
        }

    async def arbitrate(self, conflict: ConflictReport) -> ConflictResolution:
        context = await self._gather_context(conflict)
        decision = await self._apply_rules(conflict, context)
        rationale = self._generate_rationale(conflict, context, decision)

        return ConflictResolution(
            conflict_id=conflict.conflict_id,
            strategy_used=ResolutionStrategy.ARBITRATION,
            resolution=decision["action"],
            details={"context": context, "rules_applied": decision["rules"],
                    "rationale": rationale},
            resolved_by=self.agent_id,
            resolved_at=datetime.now(),
            artifacts_created=[]
        )
```

---

## 4. Multi-Level Cache System

```python
class CacheLevel(Enum):
    MEMORY = "memory"      # L1
    LOCAL = "local"        # L2
    DISTRIBUTED = "distributed"  # L3

class LRUStrategy(CacheStrategy):
    def select_eviction(self, entries: List[CacheEntry]) -> List[str]:
        sorted_entries = sorted(entries, key=lambda e: e.accessed_at)
        return [e.key for e in sorted_entries[:len(entries) // 4]]

class MemoryCache:
    def __init__(self, max_size: int = 1000, strategy: CacheStrategy = None):
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_size = max_size
        self._strategy = strategy or LRUStrategy()
        self._lock = asyncio.Lock()
        self._hits = 0
        self._misses = 0

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired() and not entry.invalidated:
                    entry.accessed_at = datetime.now()
                    entry.access_count += 1
                    self._cache.move_to_end(key)
                    self._hits += 1
                    return entry.value
                del self._cache[key]
            self._misses += 1
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None,
                  tags: List[str] = None) -> None:
        async with self._lock:
            if len(self._cache) >= self._max_size:
                to_evict = self._strategy.select_eviction(list(self._cache.values()))
                for k in to_evict:
                    del self._cache[k]
            entry = CacheEntry(key=key, value=value, created_at=datetime.now(),
                              accessed_at=datetime.now(), ttl=ttl, tags=tags or [])
            self._cache[key] = entry

class MultiLevelCache:
    def __init__(self, l1_size: int = 1000, l2_dir: str = "./cache",
                 l2_size_mb: int = 100):
        self.l1 = MemoryCache(max_size=l1_size)
        self.l2 = LocalDiskCache(cache_dir=l2_dir, max_size_mb=l2_size_mb)

    async def get(self, key: str, tags: List[str] = None,
                  compute_if_missing: Callable = None,
                  ttl: Optional[int] = None) -> Optional[Any]:
        value = await self.l1.get(key)
        if value is not None:
            return value
        value = await self.l2.get(key)
        if value is not None:
            await self.l1.set(key, value, ttl=ttl, tags=tags)
            return value
        if compute_if_missing:
            value = await compute_if_missing()
            if value is not None:
                await self.set(key, value, ttl=ttl, tags=tags)
                return value
        return None
```

---

## 5. Task Priority Queue

```python
class TaskPriority(Enum):
    CRITICAL = 1
    URGENT = 2
    HIGH = 3
    NORMAL = 5
    LOW = 7
    BATCH = 9

class TaskQueue:
    def __init__(self, max_concurrent: int = 10):
        self._queues = {p: asyncio.PriorityQueue() for p in TaskPriority}
        self._running: Dict[str, asyncio.Task] = {}
        self._completed: Dict[str, TaskResult] = {}
        self._blocked: Dict[str, List[str]] = {}
        self._max_concurrent = max_concurrent
        self._lock = asyncio.Lock()

    async def enqueue(self, task: Task) -> str:
        async with self._lock:
            can_run = await self._check_dependencies(task)
            if can_run:
                await self._queues[task.priority].put(task)
                task.status = TaskStatus.QUEUED
            else:
                for dep in task.dependencies:
                    if dep.task_id not in self._blocked:
                        self._blocked[dep.task_id] = []
                    self._blocked[dep.task_id].append(task.task_id)
            return task.task_id

    async def dequeue(self) -> Optional[Task]:
        for priority in TaskPriority:
            queue = self._queues[priority]
            if not queue.empty() and len(self._running) < self._max_concurrent:
                try:
                    task = queue.get_nowait()
                    task.status = TaskStatus.RUNNING
                    self._running[task.task_id] = task
                    return task
                except asyncio.QueueEmpty:
                    continue
        return None

    async def complete(self, task_id: str, result: Optional[TaskResult] = None) -> None:
        async with self._lock:
            if task_id in self._running:
                del self._running[task_id]
            self._completed[task_id] = result or TaskResult(
                task_id=task_id, status=TaskStatus.COMPLETED, completed_at=datetime.now())
            if task_id in self._blocked:
                blocked_ids = self._blocked.pop(task_id)
                for blocked_id in blocked_ids:
                    await self._unblock_task(blocked_id)
```

---

## 6. LangGraph Integration Proposal

```python
"""
LangGraph Integration Assessment

优势:
1. 内置状态管理 - 无需手动管理复杂状态
2. Checkpoint/持久化 - 支持中断恢复
3. 条件边 - 灵活的流程控制
4. 可视化 - 易于调试和理解
5. 人机回环 - 内置支持

建议:
- Phase 1: 使用当前自定义Orchestrator
- Phase 2: 评估LangGraph v0.2+的成熟度
- Phase 3: 如需扩展到更多Agent，考虑迁移
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

class MSRAState(TypedDict):
    current_stage: str
    raw_data_path: str | None
    cleaned_data_path: str | None
    sap_path: str | None
    analysis_results: dict | None
    report_path: str | None
    gate_results: dict
    conflicts: List[dict]
    user_approvals: dict
    completed_tasks: List[str]

def create_msra_graph():
    workflow = StateGraph(MSRAState)
    workflow.add_node("data_validator", data_validator_node)
    workflow.add_node("method_consultant", method_consultant_node)
    workflow.add_node("exec_runner", exec_runner_node)
    workflow.add_node("qc_inspector", qc_inspector_node)
    workflow.add_edge("__start__", "data_validator")
    workflow.add_conditional_edges("qc_inspector", gate_check_decision,
                                   {"continue": "method_consultant", END: END})
    return workflow.compile(checkpointer=MemorySaver())
```

---

## 7. Implementation Roadmap

### Phase 1: Core Infrastructure (Week 1-2)
| Task | Deliverable |
|------|-------------|
| 1.1 | 实现IAgent接口基类 (`iagent.py`) |
| 1.2 | 实现Message Queue系统 (`message_queue.py`) |
| 1.3 | 实现Priority Task Queue (`task_queue.py`) |
| 1.4 | 实现Multi-Level Cache (`cache_system.py`) |
| 1.5 | 编写单元测试 |

### Phase 2: Conflict Resolution (Week 3-4)
| Task | Deliverable |
|------|-------------|
| 2.1 | 实现ConflictResolver (`conflict_resolution.py`) |
| 2.2 | 实现ArbitratorAgent (`arbitrator_agent.py`) |
| 2.3 | 定义冲突分级规则 (`conflict_rules.yaml`) |
| 2.4 | 集成冲突解决到Orchestrator |

### Phase 3: Agent Refactoring (Week 5-6)
| Task | Deliverable |
|------|-------------|
| 3.1 | 重构Data Validator (IAgent-compliant) |
| 3.2 | 重构Method Consultant (IAgent-compliant) |
| 3.3 | 重构Exec Runner/Inference (IAgent-compliant) |
| 3.4 | 重构QC Inspector (IAgent-compliant) |

### Phase 4: Integration & Testing (Week 7-8)
| Task | Deliverable |
|------|-------------|
| 4.1 | 集成所有组件 |
| 4.2 | 端到端测试 |
| 4.3 | 性能基准测试 |
| 4.4 | 发布v1.0 |
