"""
MSRA Multi-Agent Framework - Core Interfaces

本模块定义了所有Agent必须遵循的标准接口，确保互操作性和可扩展性。

Author: MSRA Team
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import uuid
import hashlib
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import pickle
import json

# ========================================
# Enums
# ========================================

class AgentStatus(Enum):
    """Agent状态"""
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING = "waiting"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"


class ConflictLevel(Enum):
    """冲突级别"""
    TRIVIAL = 1      # 轻微差异，记录即可
    MINOR = 2        # 小差异，条件通过
    MODERATE = 3     # 中等差异，需确认
    SIGNIFICANT = 4  # 显著差异，阻断
    CRITICAL = 5     # 严重差异，立即上报


class ConflictType(Enum):
    """冲突类型"""
    DATA_INCONSISTENCY = "data_inconsistency"
    METHOD_DISAGREEMENT = "method_disagreement"
    RESULT_DIVERGENCE = "result_divergence"
    QUALITY_GATE_FAILURE = "quality_gate_failure"
    RESOURCE_CONTENTION = "resource_contention"
    PRIORITY_CONFLICT = "priority_conflict"
    TIMING_CONFLICT = "timing_conflict"
    SEMANTIC_MISMATCH = "semantic_mismatch"


class ResolutionStrategy(Enum):
    """解决策略"""
    AUTO_RESOLVE = "auto_resolve"
    VOTING = "voting"
    ARBITRATION = "arbitration"
    USER_DECISION = "user_decision"
    ROLLBACK = "rollback"
    SKIP = "skip"
    MERGE = "merge"


class TaskPriority(Enum):
    """任务优先级"""
    CRITICAL = 1   # 最高优先级
    URGENT = 2     # 紧急
    HIGH = 3       # 高优先级
    NORMAL = 5     # 普通优先级
    LOW = 7        # 低优先级
    BATCH = 9      # 批处理任务


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class TaskType(Enum):
    """任务类型"""
    EXECUTION = "execution"
    VERIFICATION = "verification"
    GATE_CHECK = "gate_check"
    REPORT = "report"
    ORCHESTRATION = "orchestration"


# ========================================
# Dataclasses
# ========================================

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

    @classmethod
    def create(
        cls,
        sender: str,
        recipient: Union[str, List[str]],
        message_type: str,
        payload: Dict[str, Any],
        priority: int = 5,
        ttl: int = 300,
        correlation_id: Optional[str] = None
    ) -> "AgentMessage":
        """创建消息的工厂方法"""
        return cls(
            message_id=str(uuid.uuid4()),
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            payload=payload,
            timestamp=datetime.now(),
            correlation_id=correlation_id,
            ttl=ttl,
            priority=priority
        )

    def to_json(self) -> str:
        """序列化为JSON"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> "AgentMessage":
        """从JSON反序列化"""
        data = json.loads(json_str)
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class Handoff:
    """标准接棒格式"""
    agent_name: str
    completed_work: List[str]
    artifacts: Dict[str, str]  # path -> description
    verification_method: str
    known_issues: List[str]
    pending_decisions: List[str]
    data_summary: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    next_agent: Optional[str] = None
    status: AgentStatus = AgentStatus.IDLE

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["status"] = self.status.value
        return data


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

    @classmethod
    def create(
        cls,
        source_agent: str,
        target_agent: str,
        conflict_type: ConflictType,
        level: ConflictLevel,
        description: str,
        evidence: Dict[str, Any],
        suggestions: List[str]
    ) -> "ConflictReport":
        """创建冲突报告"""
        return cls(
            conflict_id=str(uuid.uuid4()),
            source_agent=source_agent,
            target_agent=target_agent,
            conflict_type=conflict_type.value,
            conflict_level=level,
            description=description,
            evidence=evidence,
            resolution_suggestions=suggestions,
            timestamp=datetime.now()
        )


@dataclass
class ConflictResolution:
    """冲突解决结果"""
    conflict_id: str
    strategy_used: ResolutionStrategy
    resolution: str
    details: Dict[str, Any]
    resolved_by: str
    resolved_at: datetime
    artifacts_created: List[str]


@dataclass
class TaskDependency:
    """任务依赖"""
    task_id: str
    dependency_type: str  # blocks|must_complete|should_complete
    optional: bool = False


@dataclass
class Task:
    """任务定义"""
    task_id: str
    task_type: TaskType
    priority: TaskPriority
    description: str
    agent_id: str
    payload: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    dependencies: List[TaskDependency] = field(default_factory=list)
    parent_task_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other: "Task") -> bool:
        """优先级队列比较"""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.created_at < other.created_at


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    artifacts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    size_bytes: int = 0
    ttl: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    invalidated: bool = False

    def is_expired(self) -> bool:
        if self.ttl:
            from datetime import timedelta
            return datetime.now() > self.created_at + timedelta(seconds=self.ttl)
        return False


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


# ========================================
# Core Interface
# ========================================

class IAgent(ABC):
    """Agent标准接口 - 所有Agent必须实现此接口"""

    @property
    @abstractmethod
    def agent_id(self) -> str:
        """Agent唯一标识"""
        pass

    @property
    @abstractmethod
    def agent_type(self) -> str:
        """Agent类型"""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[AgentCapability]:
        """Agent能力列表"""
        pass

    @property
    def status(self) -> AgentStatus:
        """当前状态"""
        return self._status

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化Agent"""
        pass

    @abstractmethod
    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Handoff:
        """执行任务"""
        pass

    @abstractmethod
    async def receive_message(self, message: AgentMessage) -> AgentMessage:
        """接收消息"""
        pass

    @abstractmethod
    async def send_message(self, message: AgentMessage) -> bool:
        """发送消息"""
        pass

    @abstractmethod
    async def report_conflict(self, conflict: ConflictReport) -> str:
        """上报冲突"""
        pass

    @abstractmethod
    async def get_status(self) -> AgentStatus:
        """获取状态"""
        pass

    @abstractmethod
    async def shutdown(self) -> bool:
        """关闭Agent"""
        pass

    def _generate_id(self) -> str:
        """生成唯一ID"""
        return str(uuid.uuid4())

    def _generate_hash(self, data: str) -> str:
        """生成哈希值"""
        return hashlib.md5(data.encode()).hexdigest()


# ========================================
# Helper Functions
# ========================================

def make_timedelta(seconds: int) -> datetime:
    """创建时间增量"""
    from datetime import timedelta as td
    return td(seconds=seconds)


# ========================================
# Exports
# ========================================

__all__ = [
    # Enums
    "AgentStatus",
    "ConflictLevel",
    "ConflictType",
    "ResolutionStrategy",
    "TaskPriority",
    "TaskStatus",
    "TaskType",
    # Dataclasses
    "AgentMessage",
    "Handoff",
    "ConflictReport",
    "ConflictResolution",
    "TaskDependency",
    "Task",
    "TaskResult",
    "CacheEntry",
    "AgentCapability",
    # Interface
    "IAgent",
]
