"""
MSRA Multi-Agent Framework - Quick Start Guide

本示例展示如何使用多Agent框架构建协作系统。

Author: MSRA Team
Version: 1.0.0
"""

import asyncio
from typing import Dict, Any, List

# ========================================
# Example 1: Basic Framework Setup
# ========================================

async def example_basic_setup():
    """基本框架设置"""
    from agents.core import create_agent_framework

    # 创建完整框架
    (message_bus, task_queue, cache,
     conflict_resolver, registry, monitor) = create_agent_framework(
        max_concurrent=10,
        l1_cache_size=1000,
        l2_cache_dir="./.msra_cache",
        l2_cache_mb=100
    )

    print("✅ Framework created successfully")
    print(f"   - MessageBus: {message_bus}")
    print(f"   - TaskQueue: {task_queue}")
    print(f"   - Cache: {cache}")
    print(f"   - ConflictResolver: {conflict_resolver}")
    print(f"   - Registry: {registry}")
    print(f"   - Monitor: {monitor}")

    return message_bus, task_queue, cache, conflict_resolver, registry, monitor


# ========================================
# Example 2: Create Custom Agent
# ========================================

from agents.core.base_agent import BaseAgent
from agents.core.interfaces import AgentCapability, Handoff


class CustomAnalyzerAgent(BaseAgent):
    """自定义分析Agent示例"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            agent_id="custom_analyzer",
            agent_type="analyzer",
            config=config
        )

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="statistical_analysis",
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data_path": {"type": "string"},
                        "method": {"type": "string"}
                    },
                    "required": ["data_path"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "results": {"type": "object"},
                        "report_path": {"type": "string"}
                    }
                },
                constraints=["must_follow_sap"],
                dependencies=[],
                quality_metrics={
                    "accuracy": "分析结果准确性"
                }
            )
        ]

    async def execute(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Handoff:
        """执行分析任务"""
        self._status = "processing"

        data_path = task.get("data_path")
        method = task.get("method", "ttest")

        # 模拟分析执行
        results = {
            "method": method,
            "statistic": 2.5,
            "p_value": 0.012,
            "effect_size": 0.8
        }

        self._status = "completed"

        return self._create_handoff(
            completed_work=[
                f"执行{method}分析",
                "生成结果报告"
            ],
            artifacts={
                "./output/analysis_results.json": "分析结果"
            },
            verification_method="检查p值和效应量",
            known_issues=[],
            pending_decisions=[],
            data_summary=results,
            next_agent="report_expert"
        )


async def example_custom_agent():
    """自定义Agent示例"""
    # 创建框架
    from agents.core import create_agent_framework
    (message_bus, task_queue, cache,
     conflict_resolver, registry, monitor) = create_agent_framework()

    # 创建Agent
    agent = CustomAnalyzerAgent()

    # 设置依赖
    agent.set_dependencies(
        message_bus=message_bus,
        task_queue=task_queue,
        cache=cache,
        conflict_resolver=conflict_resolver
    )

    # 初始化
    await agent.initialize({})

    # 注册到服务注册中心
    await registry.register(agent)

    # 执行任务
    handoff = await agent.execute(
        task={"data_path": "./data/sample.csv", "method": "anova"},
        context={"output_dir": "./output"}
    )

    print("✅ Agent executed successfully")
    print(f"   - Completed: {handoff.completed_work}")
    print(f"   - Artifacts: {handoff.artifacts}")
    print(f"   - Data Summary: {handoff.data_summary}")

    return agent


# ========================================
# Example 3: Message Passing
# ========================================

async def example_message_passing():
    """消息传递示例"""
    from agents.core import create_agent_framework, AgentMessage

    (message_bus, task_queue, cache,
     conflict_resolver, registry, monitor) = create_agent_framework()

    # 订阅消息
    received_messages = []

    async def message_handler(message: AgentMessage):
        received_messages.append(message)
        print(f"📩 Received: {message.message_type} from {message.sender}")

        # 发送响应
        response = AgentMessage.create(
            sender="agent_b",
            recipient=message.sender,
            message_type="response",
            payload={"status": "processed"},
            correlation_id=message.message_id
        )
        await message_bus.publish(message.sender, response)

    await message_bus.subscribe("agent_b", message_handler)

    # 发送请求
    request = AgentMessage.create(
        sender="agent_a",
        recipient="agent_b",
        message_type="request",
        payload={"task": "analyze", "data": "sample.csv"},
        priority=3
    )

    await message_bus.publish("agent_b", request)

    # 等待处理
    await asyncio.sleep(0.2)

    print(f"✅ Messages received: {len(received_messages)}")

    return message_bus


# ========================================
# Example 4: Task Queue
# ========================================

async def example_task_queue():
    """任务队列示例"""
    from agents.core import (
        create_agent_framework,
        Task,
        TaskType,
        TaskPriority,
        TaskDependency
    )

    (message_bus, task_queue, cache,
     conflict_resolver, registry, monitor) = create_agent_framework()

    # 创建任务
    task1 = Task(
        task_id="task_001",
        task_type=TaskType.EXECUTION,
        priority=TaskPriority.HIGH,
        description="Data validation",
        agent_id="data_validator",
        payload={"data_path": "./data/sample.csv"}
    )

    task2 = Task(
        task_id="task_002",
        task_type=TaskType.EXECUTION,
        priority=TaskPriority.NORMAL,
        description="Analysis execution",
        agent_id="exec_runner",
        payload={"sap_path": "./docs/SAP.md"},
        dependencies=[
            TaskDependency(
                task_id="task_001",
                dependency_type="must_complete",
                optional=False
            )
        ]
    )

    # 入队任务
    await task_queue.enqueue(task1)
    await task_queue.enqueue(task2)

    # 检查状态
    status = task_queue.get_status()
    print("✅ Task Queue Status:")
    print(f"   - Queued tasks: {sum(status['queues'].values())}")
    print(f"   - Blocked tasks: {sum(len(v) for v in task_queue._blocked.values())}")

    # 处理任务
    first_task = await task_queue.dequeue()
    if first_task:
        print(f"   - Processing: {first_task.task_id}")
        await task_queue.complete(first_task.task_id)

    # 检查依赖解锁
    status = task_queue.get_status()
    print(f"   - After completion: {status}")

    return task_queue


# ========================================
# Example 5: Conflict Resolution
# ========================================

async def example_conflict_resolution():
    """冲突解决示例"""
    from agents.core import (
        create_agent_framework,
        ConflictReport,
        ConflictType,
        ConflictLevel
    )

    (message_bus, task_queue, cache,
     conflict_resolver, registry, monitor) = create_agent_framework()

    # 注册投票者
    class MockVoter:
        def __init__(self, agent_id):
            self.agent_id = agent_id

        async def vote_on_conflict(self, conflict):
            from agents.core.conflict_resolution import ConflictVote
            return ConflictVote(
                voter_id=self.agent_id,
                choice="re_validate",
                confidence=0.8
            )

    conflict_resolver.register_voter("method_consultant", MockVoter("method_consultant"))
    conflict_resolver.register_voter("exec_inference", MockVoter("exec_inference"))

    # 创建冲突报告
    conflict = ConflictReport.create(
        source_agent="data_validator",
        target_agent="method_consultant",
        conflict_type=ConflictType.DATA_INCONSISTENCY,
        level=ConflictLevel.MODERATE,
        description="Missing value rate discrepancy",
        evidence={
            "expected": "<5%",
            "actual": "15%",
            "variable": "age"
        },
        suggestions=["re_validate", "accept_with_note", "exclude_variable"]
    )

    # 解决冲突
    resolution = await conflict_resolver.resolve(conflict)

    print("✅ Conflict Resolved:")
    print(f"   - Strategy: {resolution.strategy_used.value}")
    print(f"   - Resolution: {resolution.resolution}")
    print(f"   - Resolved by: {resolution.resolved_by}")

    # 获取统计
    stats = conflict_resolver.get_stats()
    print(f"   - Total resolved: {stats['total_resolved']}")

    return conflict_resolver


# ========================================
# Example 6: Caching
# ========================================

async def example_caching():
    """缓存示例"""
    from agents.core import create_agent_framework

    (message_bus, task_queue, cache,
     conflict_resolver, registry, monitor) = create_agent_framework()

    # 计算计数器
    compute_count = 0

    async def expensive_computation():
        nonlocal compute_count
        compute_count += 1
        await asyncio.sleep(0.1)  # 模拟耗时操作
        return {"result": "computed_value", "count": compute_count}

    # 第一次调用 - 应该计算
    result1 = await cache.get(
        "expensive_key",
        compute_if_missing=expensive_computation,
        ttl=3600,
        tags=["computation"]
    )
    print(f"✅ First call: computed={compute_count}")

    # 第二次调用 - 应该从缓存获取
    result2 = await cache.get(
        "expensive_key",
        compute_if_missing=expensive_computation
    )
    print(f"✅ Second call: computed={compute_count} (should be same)")

    # 检查缓存统计
    stats = cache.get_stats()
    print(f"   - L1 hits: {stats['L1']['hits']}")
    print(f"   - L1 hit rate: {stats['L1']['hit_rate']:.2%}")

    # 失效缓存
    await cache.invalidate_by_tags(["computation"])

    # 第三次调用 - 应该重新计算
    result3 = await cache.get(
        "expensive_key",
        compute_if_missing=expensive_computation
    )
    print(f"✅ Third call (after invalidation): computed={compute_count}")

    return cache


# ========================================
# Example 7: Resource Monitoring
# ========================================

async def example_monitoring():
    """资源监控示例"""
    from agents.core import create_agent_framework

    (message_bus, task_queue, cache,
     conflict_resolver, registry, monitor) = create_agent_framework()

    # 记录任务执行
    await monitor.record_task_start("agent_001", "task_001")

    # 模拟执行
    await asyncio.sleep(0.1)

    await monitor.record_task_complete(
        agent_id="agent_001",
        task_id="task_001",
        execution_time=0.1,
        tokens_input=1500,
        tokens_output=800,
        success=True
    )

    # 记录缓存操作
    await monitor.record_cache_hit("agent_001", "L1")
    await monitor.record_cache_hit("agent_001", "L1")
    await monitor.record_cache_miss("agent_001")

    # 获取摘要
    summary = await monitor.get_summary()

    print("✅ Monitoring Summary:")
    print(f"   - Total tasks completed: {summary['totals']['tasks_completed']}")
    print(f"   - Total tokens input: {summary['totals']['tokens_input']}")
    print(f"   - Cache hit rate: {summary['totals']['cache_hit_rate']:.2%}")

    # 获取仪表板数据
    dashboard = await monitor.get_dashboard_data()
    print(f"   - Agents tracked: {len(dashboard['agents'])}")

    return monitor


# ========================================
# Example 8: Service Registry
# ========================================

async def example_service_registry():
    """服务注册示例"""
    from agents.core import (
        create_agent_framework,
        AgentCapability
    )

    (message_bus, task_queue, cache,
     conflict_resolver, registry, monitor) = create_agent_framework()

    # 创建模拟Agent
    class MockAgent:
        def __init__(self, agent_id, agent_type, capabilities):
            self.agent_id = agent_id
            self.agent_type = agent_type
            self.capabilities = capabilities

    # 注册多个Agent
    validator = MockAgent(
        "data_validator_001",
        "validator",
        [AgentCapability(
            name="data_validation",
            version="1.0",
            input_schema={},
            output_schema={},
            constraints=[],
            dependencies=[],
            quality_metrics={}
        )]
    )

    analyzer = MockAgent(
        "method_consultant_001",
        "consultant",
        [AgentCapability(
            name="method_selection",
            version="1.0",
            input_schema={},
            output_schema={},
            constraints=[],
            dependencies=[],
            quality_metrics={}
        )]
    )

    await registry.register(validator, priority=3)
    await registry.register(analyzer, priority=5)

    # 发现服务
    validators = await registry.discover(agent_type="validator")
    print(f"✅ Found {len(validators)} validators")

    # 按能力发现
    agents_with_validation = await registry.discover(capability="data_validation")
    print(f"✅ Found {len(agents_with_validation)} agents with data_validation capability")

    # 负载均衡选择
    selected = await registry.discover_one(agent_type="validator")
    print(f"✅ Selected agent: {selected.agent_id}")

    # 获取统计
    stats = registry.get_stats()
    print(f"   - Total agents: {stats['total_agents']}")
    print(f"   - By type: {stats['by_type']}")

    return registry


# ========================================
# Main Entry Point
# ========================================

async def main():
    """运行所有示例"""
    print("=" * 60)
    print("MSRA Multi-Agent Framework - Examples")
    print("=" * 60)

    print("\n📌 Example 1: Basic Setup")
    await example_basic_setup()

    print("\n📌 Example 2: Custom Agent")
    await example_custom_agent()

    print("\n📌 Example 3: Message Passing")
    await example_message_passing()

    print("\n📌 Example 4: Task Queue")
    await example_task_queue()

    print("\n📌 Example 5: Conflict Resolution")
    await example_conflict_resolution()

    print("\n📌 Example 6: Caching")
    await example_caching()

    print("\n📌 Example 7: Monitoring")
    await example_monitoring()

    print("\n📌 Example 8: Service Registry")
    await example_service_registry()

    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
