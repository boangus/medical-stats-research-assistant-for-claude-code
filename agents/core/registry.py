"""
MSRA Multi-Agent Framework - Service Registry

本模块实现Agent服务注册与发现机制，支持动态Agent管理。

Author: MSRA Team
Version: 1.0.0
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable, TYPE_CHECKING
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging

if TYPE_CHECKING:
    from .interfaces import IAgent, AgentCapability


@dataclass
class AgentRegistration:
    """Agent注册信息"""
    agent_id: str
    agent_type: str
    capabilities: List[str]
    endpoint: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    status: str = "active"
    priority: int = 5  # 1-10, 1最高


class ServiceRegistry:
    """
    服务注册中心

    功能:
    - Agent注册与注销
    - 心跳检测
    - 服务发现
    - 负载均衡
    - 健康检查
    """

    def __init__(
        self,
        heartbeat_timeout: int = 60,
        cleanup_interval: int = 30
    ):
        self._registry: Dict[str, AgentRegistration] = {}
        self._type_index: Dict[str, List[str]] = {}  # type -> agent_ids
        self._capability_index: Dict[str, List[str]] = {}  # capability -> agent_ids
        self._lock = asyncio.Lock()
        self._heartbeat_timeout = heartbeat_timeout
        self._cleanup_interval = cleanup_interval
        self._logger = logging.getLogger("service_registry")
        self._running = False
        self._cleanup_task: Optional[asyncio.Task] = None

        # 负载均衡策略
        self._load_balancer = RoundRobinLoadBalancer()

    async def register(
        self,
        agent: "IAgent",
        endpoint: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        priority: int = 5
    ) -> bool:
        """
        注册Agent

        Args:
            agent: Agent实例
            endpoint: 可选的端点地址
            metadata: 额外元数据
            priority: 优先级(1-10)

        Returns:
            bool: 注册是否成功
        """
        async with self._lock:
            agent_id = agent.agent_id
            agent_type = agent.agent_type
            capabilities = [c.name for c in agent.capabilities]

            # 创建注册信息
            registration = AgentRegistration(
                agent_id=agent_id,
                agent_type=agent_type,
                capabilities=capabilities,
                endpoint=endpoint,
                metadata=metadata or {},
                priority=priority,
                status="active"
            )

            # 添加到注册表
            self._registry[agent_id] = registration

            # 更新类型索引
            if agent_type not in self._type_index:
                self._type_index[agent_type] = []
            if agent_id not in self._type_index[agent_type]:
                self._type_index[agent_type].append(agent_id)

            # 更新能力索引
            for cap in capabilities:
                if cap not in self._capability_index:
                    self._capability_index[cap] = []
                if agent_id not in self._capability_index[cap]:
                    self._capability_index[cap].append(agent_id)

            self._logger.info(f"Agent registered: {agent_id} (type={agent_type})")
            return True

    async def unregister(self, agent_id: str) -> bool:
        """注销Agent"""
        async with self._lock:
            if agent_id not in self._registry:
                return False

            registration = self._registry[agent_id]

            # 从类型索引移除
            if registration.agent_type in self._type_index:
                if agent_id in self._type_index[registration.agent_type]:
                    self._type_index[registration.agent_type].remove(agent_id)

            # 从能力索引移除
            for cap in registration.capabilities:
                if cap in self._capability_index:
                    if agent_id in self._capability_index[cap]:
                        self._capability_index[cap].remove(agent_id)

            # 从注册表移除
            del self._registry[agent_id]

            self._logger.info(f"Agent unregistered: {agent_id}")
            return True

    async def heartbeat(self, agent_id: str) -> bool:
        """更新心跳"""
        async with self._lock:
            if agent_id not in self._registry:
                return False

            self._registry[agent_id].last_heartbeat = datetime.now()
            self._registry[agent_id].status = "active"
            return True

    async def discover(
        self,
        agent_type: Optional[str] = None,
        capability: Optional[str] = None
    ) -> List[AgentRegistration]:
        """
        发现Agent

        Args:
            agent_type: 按类型过滤
            capability: 按能力过滤

        Returns:
            List[AgentRegistration]: 匹配的Agent列表
        """
        async with self._lock:
            if agent_type:
                agent_ids = self._type_index.get(agent_type, [])
            elif capability:
                agent_ids = self._capability_index.get(capability, [])
            else:
                agent_ids = list(self._registry.keys())

            return [
                self._registry[aid] for aid in agent_ids
                if aid in self._registry and self._registry[aid].status == "active"
            ]

    async def discover_one(
        self,
        agent_type: Optional[str] = None,
        capability: Optional[str] = None
    ) -> Optional[AgentRegistration]:
        """发现一个Agent（负载均衡）"""
        agents = await self.discover(agent_type, capability)
        if not agents:
            return None

        return self._load_balancer.select(agents)

    async def get_agent(self, agent_id: str) -> Optional[AgentRegistration]:
        """获取指定Agent信息"""
        return self._registry.get(agent_id)

    async def get_all(self) -> Dict[str, AgentRegistration]:
        """获取所有注册的Agent"""
        return self._registry.copy()

    async def start_cleanup(self) -> None:
        """启动清理任务"""
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop_cleanup(self) -> None:
        """停止清理任务"""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    async def _cleanup_loop(self) -> None:
        """清理过期Agent"""
        while self._running:
            await asyncio.sleep(self._cleanup_interval)
            await self._cleanup_expired()

    async def _cleanup_expired(self) -> None:
        """清理超时Agent"""
        async with self._lock:
            now = datetime.now()
            timeout = timedelta(seconds=self._heartbeat_timeout)

            expired = [
                agent_id for agent_id, reg in self._registry.items()
                if now - reg.last_heartbeat > timeout
            ]

            for agent_id in expired:
                self._registry[agent_id].status = "inactive"
                self._logger.warning(f"Agent inactive due to heartbeat timeout: {agent_id}")

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_agents": len(self._registry),
            "active_agents": sum(1 for r in self._registry.values() if r.status == "active"),
            "inactive_agents": sum(1 for r in self._registry.values() if r.status == "inactive"),
            "by_type": {
                t: len(ids) for t, ids in self._type_index.items()
            },
            "by_capability": {
                c: len(ids) for c, ids in self._capability_index.items()
            }
        }


class LoadBalancer:
    """负载均衡器基类"""

    def select(self, agents: List[AgentRegistration]) -> AgentRegistration:
        raise NotImplementedError


class RoundRobinLoadBalancer(LoadBalancer):
    """轮询负载均衡"""

    def __init__(self):
        self._index = 0

    def select(self, agents: List[AgentRegistration]) -> AgentRegistration:
        if not agents:
            raise ValueError("No agents available")

        # 按优先级排序
        sorted_agents = sorted(agents, key=lambda a: a.priority)

        # 选择最高优先级组
        highest_priority = sorted_agents[0].priority
        candidates = [a for a in sorted_agents if a.priority == highest_priority]

        # 轮询选择
        selected = candidates[self._index % len(candidates)]
        self._index += 1

        return selected


class LeastLoadedLoadBalancer(LoadBalancer):
    """最少负载负载均衡"""

    def select(self, agents: List[AgentRegistration]) -> AgentRegistration:
        if not agents:
            raise ValueError("No agents available")

        # 选择负载最少的（基于元数据中的load字段）
        return min(
            agents,
            key=lambda a: a.metadata.get("load", 0)
        )


# ========================================
# Global Registry Instance
# ========================================

_global_registry: Optional[ServiceRegistry] = None


def get_registry() -> ServiceRegistry:
    """获取全局注册中心"""
    global _global_registry
    if _global_registry is None:
        _global_registry = ServiceRegistry()
    return _global_registry


def init_registry(
    heartbeat_timeout: int = 60,
    cleanup_interval: int = 30
) -> ServiceRegistry:
    """初始化全局注册中心"""
    global _global_registry
    _global_registry = ServiceRegistry(heartbeat_timeout, cleanup_interval)
    return _global_registry


# ========================================
# Exports
# ========================================

__all__ = [
    "ServiceRegistry",
    "AgentRegistration",
    "LoadBalancer",
    "RoundRobinLoadBalancer",
    "LeastLoadedLoadBalancer",
    "get_registry",
    "init_registry",
]
