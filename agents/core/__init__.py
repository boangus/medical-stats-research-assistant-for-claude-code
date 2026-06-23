"""
MSRA Multi-Agent Framework - Core Module

本模块提供了多Agent系统的核心基础设施，包括：
- 标准Agent接口 (IAgent)
- 通信协议和消息队列
- 多级缓存系统
- 冲突解决机制
- 任务优先级队列
- 服务注册与发现
- 资源监控仪表板

Author: MSRA Team
Version: 1.0.0
"""

from .interfaces import (
    # Enums
    AgentStatus,
    ConflictLevel,
    ConflictType,
    ResolutionStrategy,
    TaskPriority,
    TaskStatus,
    TaskType,
    # Dataclasses
    AgentMessage,
    Handoff,
    ConflictReport,
    ConflictResolution,
    TaskDependency,
    Task,
    TaskResult,
    CacheEntry,
    AgentCapability,
    # Interface
    IAgent,
)

from .base_agent import BaseAgent

from .communication import (
    QueuedMessage,
    PriorityMessageQueue,
    MessageBus,
    TaskQueue,
)

from .cache import (
    CacheStrategy,
    LRUStrategy,
    LFUStrategy,
    TTLEvictionStrategy,
    MemoryCache,
    LocalDiskCache,
    MultiLevelCache,
    get_cache,
    init_cache,
)

from .conflict_resolution import (
    ConflictResolver,
    ConflictVote,
)

from .registry import (
    ServiceRegistry,
    AgentRegistration,
    LoadBalancer,
    RoundRobinLoadBalancer,
    LeastLoadedLoadBalancer,
    get_registry,
    init_registry,
)

from .monitor import (
    ResourceMonitor,
    AgentMetrics,
    MetricPoint,
    get_monitor,
    init_monitor,
)

# ========================================
# Version Info
# ========================================

__version__ = "1.0.0"
__author__ = "MSRA Team"


# ========================================
# Exports
# ========================================

__all__ = [
    # Version
    "__version__",
    "__author__",
    # Interfaces
    "IAgent",
    "BaseAgent",
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
    # Communication
    "MessageBus",
    "TaskQueue",
    "PriorityMessageQueue",
    "QueuedMessage",
    # Cache
    "CacheStrategy",
    "LRUStrategy",
    "LFUStrategy",
    "TTLEvictionStrategy",
    "MemoryCache",
    "LocalDiskCache",
    "MultiLevelCache",
    "get_cache",
    "init_cache",
    # Conflict Resolution
    "ConflictResolver",
    "ConflictVote",
    # Registry
    "ServiceRegistry",
    "AgentRegistration",
    "LoadBalancer",
    "RoundRobinLoadBalancer",
    "LeastLoadedLoadBalancer",
    "get_registry",
    "init_registry",
    # Monitor
    "ResourceMonitor",
    "AgentMetrics",
    "MetricPoint",
    "get_monitor",
    "init_monitor",
]


# ========================================
# Quick Setup Helper
# ========================================

def create_agent_framework(
    max_concurrent: int = 10,
    l1_cache_size: int = 1000,
    l2_cache_dir: str = "./.msra_cache",
    l2_cache_mb: int = 100,
    heartbeat_timeout: int = 60,
    history_retention_hours: int = 24
) -> tuple:
    """
    创建完整的Agent框架

    Returns:
        tuple: (MessageBus, TaskQueue, MultiLevelCache, ConflictResolver, ServiceRegistry, ResourceMonitor)
    """
    # 初始化缓存
    cache = init_cache(l1_cache_size, l2_cache_dir, l2_cache_mb)

    # 初始化消息总线
    message_bus = MessageBus()

    # 初始化任务队列
    task_queue = TaskQueue(max_concurrent=max_concurrent)

    # 初始化冲突解决器
    conflict_resolver = ConflictResolver(message_bus)

    # 初始化服务注册中心
    registry = init_registry(heartbeat_timeout=heartbeat_timeout)

    # 初始化资源监控器
    monitor = init_monitor(history_retention_hours=history_retention_hours)

    return message_bus, task_queue, cache, conflict_resolver, registry, monitor
