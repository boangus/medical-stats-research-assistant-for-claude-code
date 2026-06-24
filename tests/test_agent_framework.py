"""
MSRA Multi-Agent Framework - Unit Tests

本模块包含核心组件的单元测试。

运行方式:
    pytest tests/test_agent_framework.py -v

Author: MSRA Team
Version: 1.0.0
"""

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

# ========================================
# Test Fixtures
# ========================================

@pytest.fixture
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def message_bus():
    """创建消息总线"""
    from agents.core.communication import MessageBus
    return MessageBus()


@pytest.fixture
def task_queue():
    """创建任务队列"""
    from agents.core.communication import TaskQueue
    return TaskQueue(max_concurrent=5)


@pytest.fixture
def cache():
    """创建缓存"""
    from agents.core.cache import MultiLevelCache
    return MultiLevelCache(l1_size=100, l2_dir="./.test_cache", l2_size_mb=10)


@pytest.fixture
def conflict_resolver():
    """创建冲突解决器"""
    from agents.core.conflict_resolution import ConflictResolver
    return ConflictResolver()


@pytest.fixture
def registry():
    """创建服务注册中心"""
    from agents.core.registry import ServiceRegistry
    return ServiceRegistry()


@pytest.fixture
def monitor():
    """创建资源监控器"""
    from agents.core.monitor import ResourceMonitor
    return ResourceMonitor()


# ========================================
# Interface Tests
# ========================================

class TestInterfaces:
    """测试核心接口"""

    def test_agent_message_creation(self):
        """测试消息创建"""
        from agents.core.interfaces import AgentMessage

        message = AgentMessage.create(
            sender="agent_a",
            recipient="agent_b",
            message_type="request",
            payload={"task": "validate"}
        )

        assert message.sender == "agent_a"
        assert message.recipient == "agent_b"
        assert message.message_type == "request"
        assert message.payload == {"task": "validate"}
        assert message.priority == 5
        assert message.ttl == 300

    def test_agent_message_serialization(self):
        """测试消息序列化"""
        from agents.core.interfaces import AgentMessage

        message = AgentMessage.create(
            sender="agent_a",
            recipient="agent_b",
            message_type="request",
            payload={"key": "value"}
        )

        json_str = message.to_json()
        restored = AgentMessage.from_json(json_str)

        assert restored.sender == message.sender
        assert restored.recipient == message.recipient
        assert restored.payload == message.payload

    def test_conflict_report_creation(self):
        """测试冲突报告创建"""
        from agents.core.interfaces import ConflictLevel, ConflictReport, ConflictType

        conflict = ConflictReport.create(
            source_agent="agent_a",
            target_agent="agent_b",
            conflict_type=ConflictType.DATA_INCONSISTENCY,
            level=ConflictLevel.MODERATE,
            description="Data mismatch",
            evidence={"expected": 100, "actual": 150},
            suggestions=["re_validate", "accept"]
        )

        assert conflict.source_agent == "agent_a"
        assert conflict.conflict_level == ConflictLevel.MODERATE
        assert conflict.resolution_status == "pending"

    def test_task_creation(self):
        """测试任务创建"""
        from agents.core.interfaces import Task, TaskPriority, TaskType

        task = Task(
            task_id="task_001",
            task_type=TaskType.EXECUTION,
            priority=TaskPriority.HIGH,
            description="Test task",
            agent_id="agent_a",
            payload={"data": "test"}
        )

        assert task.task_id == "task_001"
        assert task.priority == TaskPriority.HIGH
        assert task.timeout == 300


# ========================================
# Communication Tests
# ========================================

class TestMessageBus:
    """测试消息总线"""

    @pytest.mark.asyncio
    async def test_publish_and_subscribe(self, message_bus):
        """测试发布订阅"""
        received = []

        async def callback(message):
            received.append(message)
            return True

        await message_bus.subscribe("agent_b", callback)

        from agents.core.interfaces import AgentMessage
        message = AgentMessage.create(
            sender="agent_a",
            recipient="agent_b",
            message_type="request",
            payload={"test": "data"}
        )

        await message_bus.publish("agent_b", message)

        # 启动消息处理循环
        processing_task = asyncio.create_task(message_bus.start_processing())

        # 等待处理
        await asyncio.sleep(0.2)

        # 停止处理
        await message_bus.stop_processing()
        await processing_task

        assert len(received) == 1
        assert received[0].sender == "agent_a"

    @pytest.mark.asyncio
    async def test_priority_queue(self, message_bus):
        """测试优先级队列"""
        from agents.core.interfaces import AgentMessage

        # 发布多个不同优先级的消息
        for priority in [5, 1, 10, 3]:
            message = AgentMessage.create(
                sender="sender",
                recipient="recipient",
                message_type="test",
                payload={"priority": priority},
                priority=priority
            )
            await message_bus.publish("recipient", message)

        # 检查队列大小
        size = await message_bus._queues["recipient"].size()
        assert size == 4


class TestTaskQueue:
    """测试任务队列"""

    @pytest.mark.asyncio
    async def test_enqueue_and_dequeue(self, task_queue):
        """测试任务入队出队"""
        from agents.core.interfaces import Task, TaskPriority, TaskType

        task = Task(
            task_id="task_001",
            task_type=TaskType.EXECUTION,
            priority=TaskPriority.NORMAL,
            description="Test task",
            agent_id="agent_a",
            payload={}
        )

        await task_queue.enqueue(task)

        dequeued = await task_queue.dequeue()

        assert dequeued is not None
        assert dequeued.task_id == "task_001"

    @pytest.mark.asyncio
    async def test_priority_ordering(self, task_queue):
        """测试优先级排序"""
        from agents.core.interfaces import Task, TaskPriority, TaskType

        # 按非优先级顺序入队
        priorities = [TaskPriority.LOW, TaskPriority.CRITICAL, TaskPriority.NORMAL]
        for i, p in enumerate(priorities):
            task = Task(
                task_id=f"task_{i}",
                task_type=TaskType.EXECUTION,
                priority=p,
                description=f"Task {i}",
                agent_id="agent_a",
                payload={}
            )
            await task_queue.enqueue(task)

        # 出队应该是CRITICAL优先
        first = await task_queue.dequeue()
        assert first.priority == TaskPriority.CRITICAL

    @pytest.mark.asyncio
    async def test_task_completion(self, task_queue):
        """测试任务完成"""
        from agents.core.interfaces import Task, TaskPriority, TaskStatus, TaskType

        task = Task(
            task_id="task_001",
            task_type=TaskType.EXECUTION,
            priority=TaskPriority.NORMAL,
            description="Test task",
            agent_id="agent_a",
            payload={}
        )

        await task_queue.enqueue(task)
        dequeued = await task_queue.dequeue()

        await task_queue.complete(dequeued.task_id)

        result = task_queue.get_result(dequeued.task_id)
        assert result is not None
        assert result.status == TaskStatus.COMPLETED


# ========================================
# Cache Tests
# ========================================

class TestCache:
    """测试缓存系统"""

    @pytest.mark.asyncio
    async def test_memory_cache_set_get(self):
        """测试内存缓存"""
        from agents.core.cache import MemoryCache

        cache = MemoryCache(max_size=10)

        await cache.set("key1", "value1")
        result = await cache.get("key1")

        assert result == "value1"

    @pytest.mark.asyncio
    async def test_cache_miss(self):
        """测试缓存未命中"""
        from agents.core.cache import MemoryCache

        cache = MemoryCache(max_size=10)

        result = await cache.get("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_cache_invalidation(self):
        """测试缓存失效"""
        from agents.core.cache import MemoryCache

        cache = MemoryCache(max_size=10)

        await cache.set("key1", "value1", tags=["tag1"])
        await cache.invalidate_by_tags(["tag1"])

        result = await cache.get("key1")

        assert result is None

    @pytest.mark.asyncio
    async def test_lru_eviction(self):
        """测试LRU淘汰"""
        from agents.core.cache import LRUStrategy, MemoryCache

        cache = MemoryCache(max_size=3, strategy=LRUStrategy())

        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")
        await cache.set("key4", "value4")  # 应该淘汰key1

        result = await cache.get("key1")

        assert result is None

    @pytest.mark.asyncio
    async def test_multi_level_cache(self, cache):
        """测试多级缓存"""
        compute_count = 0

        async def compute():
            nonlocal compute_count
            compute_count += 1
            return "computed_value"

        # 第一次应该计算
        result1 = await cache.get("key1", compute_if_missing=compute)
        assert result1 == "computed_value"
        assert compute_count == 1

        # 第二次应该从缓存获取
        result2 = await cache.get("key1", compute_if_missing=compute)
        assert result2 == "computed_value"
        assert compute_count == 1  # 不应该重新计算


# ========================================
# Conflict Resolution Tests
# ========================================

class TestConflictResolution:
    """测试冲突解决"""

    @pytest.mark.asyncio
    async def test_auto_resolve(self, conflict_resolver):
        """测试自动解决"""
        from agents.core.interfaces import ConflictLevel, ConflictReport, ConflictType

        conflict = ConflictReport.create(
            source_agent="agent_a",
            target_agent="agent_b",
            conflict_type=ConflictType.DATA_INCONSISTENCY,
            level=ConflictLevel.TRIVIAL,
            description="Minor format difference",
            evidence={},
            suggestions=["normalize"]
        )

        resolution = await conflict_resolver.resolve(conflict)

        assert resolution.strategy_used.value == "auto_resolve"
        assert resolution.resolved_by == "system"

    @pytest.mark.asyncio
    async def test_voting_resolve(self, conflict_resolver):
        """测试投票解决"""
        from agents.core.interfaces import ConflictLevel, ConflictReport, ConflictType

        # 注册投票者
        mock_voter = Mock()
        mock_voter.agent_id = "voter_1"
        mock_voter.vote_on_conflict = AsyncMock(return_value=Mock(
            voter_id="voter_1",
            choice="option_a",
            confidence=0.8
        ))

        conflict_resolver.register_voter("voter_1", mock_voter)

        conflict = ConflictReport.create(
            source_agent="agent_a",
            target_agent="agent_b",
            conflict_type=ConflictType.RESULT_DIVERGENCE,
            level=ConflictLevel.MODERATE,
            description="Result difference",
            evidence={},
            suggestions=["option_a", "option_b"]
        )

        resolution = await conflict_resolver.resolve(conflict)

        assert resolution.strategy_used.value == "voting"

    @pytest.mark.asyncio
    async def test_conflict_level_strategy_mapping(self, conflict_resolver):
        """测试冲突级别策略映射"""
        from agents.core.interfaces import ConflictLevel, ConflictReport, ConflictType

        # CRITICAL级别应该使用USER_DECISION
        conflict = ConflictReport.create(
            source_agent="agent_a",
            target_agent="agent_b",
            conflict_type=ConflictType.QUALITY_GATE_FAILURE,
            level=ConflictLevel.CRITICAL,
            description="Critical failure",
            evidence={},
            suggestions=["rollback"]
        )

        resolution = await conflict_resolver.resolve(conflict)

        assert resolution.strategy_used.value == "user_decision"


# ========================================
# Registry Tests
# ========================================

class TestServiceRegistry:
    """测试服务注册"""

    @pytest.mark.asyncio
    async def test_register_agent(self, registry):
        """测试Agent注册"""
        from agents.core.interfaces import AgentCapability

        mock_agent = Mock()
        mock_agent.agent_id = "agent_001"
        mock_agent.agent_type = "validator"
        mock_agent.capabilities = [
            AgentCapability(
                name="validate",
                version="1.0",
                input_schema={},
                output_schema={},
                constraints=[],
                dependencies=[],
                quality_metrics={}
            )
        ]

        result = await registry.register(mock_agent)

        assert result is True

        # 验证可以被发现
        agents = await registry.discover(agent_type="validator")
        assert len(agents) == 1
        assert agents[0].agent_id == "agent_001"

    @pytest.mark.asyncio
    async def test_unregister_agent(self, registry):
        """测试Agent注销"""

        mock_agent = Mock()
        mock_agent.agent_id = "agent_001"
        mock_agent.agent_type = "validator"
        mock_agent.capabilities = []

        await registry.register(mock_agent)
        result = await registry.unregister("agent_001")

        assert result is True

        agents = await registry.discover(agent_type="validator")
        assert len(agents) == 0

    @pytest.mark.asyncio
    async def test_discover_by_capability(self, registry):
        """测试按能力发现"""
        from agents.core.interfaces import AgentCapability

        mock_agent = Mock()
        mock_agent.agent_id = "agent_001"
        mock_agent.agent_type = "validator"
        mock_agent.capabilities = [
            AgentCapability(
                name="data_validation",
                version="1.0",
                input_schema={},
                output_schema={},
                constraints=[],
                dependencies=[],
                quality_metrics={}
            )
        ]

        await registry.register(mock_agent)

        agents = await registry.discover(capability="data_validation")
        assert len(agents) == 1

    @pytest.mark.asyncio
    async def test_heartbeat(self, registry):
        """测试心跳"""

        mock_agent = Mock()
        mock_agent.agent_id = "agent_001"
        mock_agent.agent_type = "validator"
        mock_agent.capabilities = []

        await registry.register(mock_agent)

        result = await registry.heartbeat("agent_001")
        assert result is True

        agent = await registry.get_agent("agent_001")
        assert agent.status == "active"


# ========================================
# Monitor Tests
# ========================================

class TestResourceMonitor:
    """测试资源监控"""

    @pytest.mark.asyncio
    async def test_record_task_complete(self, monitor):
        """测试记录任务完成"""
        await monitor.record_task_complete(
            agent_id="agent_001",
            task_id="task_001",
            execution_time=1.5,
            tokens_input=1000,
            tokens_output=500,
            success=True
        )

        metrics = await monitor.get_agent_metrics("agent_001")

        assert metrics is not None
        assert metrics.tasks_completed == 1
        assert metrics.tokens_input == 1000
        assert metrics.tokens_output == 500

    @pytest.mark.asyncio
    async def test_cache_metrics(self, monitor):
        """测试缓存指标"""
        await monitor.record_cache_hit("agent_001", "L1")
        await monitor.record_cache_hit("agent_001", "L1")
        await monitor.record_cache_miss("agent_001")

        metrics = await monitor.get_agent_metrics("agent_001")

        assert metrics.cache_hits == 2
        assert metrics.cache_misses == 1

    @pytest.mark.asyncio
    async def test_summary(self, monitor):
        """测试监控摘要"""
        await monitor.record_task_complete(
            agent_id="agent_001",
            task_id="task_001",
            execution_time=1.0,
            success=True
        )

        await monitor.record_task_complete(
            agent_id="agent_002",
            task_id="task_002",
            execution_time=2.0,
            success=False
        )

        summary = await monitor.get_summary()

        assert summary["totals"]["tasks_completed"] == 1
        assert summary["totals"]["tasks_failed"] == 1

    @pytest.mark.asyncio
    async def test_alert_trigger(self, monitor):
        """测试告警触发"""
        alerts = []

        def alert_callback(alert):
            alerts.append(alert)

        monitor.add_alert_callback(alert_callback)

        # 触发超时告警
        await monitor.record_task_complete(
            agent_id="agent_001",
            task_id="task_001",
            execution_time=500,  # 超过默认阈值300
            success=True
        )

        assert len(alerts) > 0
        assert alerts[0]["type"] == "execution_time"


# ========================================
# Integration Tests
# ========================================

class TestIntegration:
    """集成测试"""

    @pytest.mark.asyncio
    async def test_full_framework_setup(self):
        """测试完整框架设置"""
        from agents.core import create_agent_framework

        (message_bus, task_queue, cache,
         conflict_resolver, registry, monitor) = create_agent_framework()

        assert message_bus is not None
        assert task_queue is not None
        assert cache is not None
        assert conflict_resolver is not None
        assert registry is not None
        assert monitor is not None

    @pytest.mark.asyncio
    async def test_agent_workflow(self):
        """测试Agent工作流"""
        from agents.core import (
            AgentMessage,
            create_agent_framework,
        )

        # 创建框架
        (message_bus, task_queue, cache,
         conflict_resolver, registry, monitor) = create_agent_framework()

        # 模拟消息传递
        received = []

        async def handler(message):
            received.append(message)
            return True

        await message_bus.subscribe("agent_b", handler)

        message = AgentMessage.create(
            sender="agent_a",
            recipient="agent_b",
            message_type="request",
            payload={"action": "validate"}
        )

        await message_bus.publish("agent_b", message)

        # 启动消息处理循环
        processing_task = asyncio.create_task(message_bus.start_processing())
        await asyncio.sleep(0.1)

        # 停止处理
        await message_bus.stop_processing()
        await processing_task

        assert len(received) == 1


# ========================================
# Run Tests
# ========================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
