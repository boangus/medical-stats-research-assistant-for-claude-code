"""
MSRA Multi-Agent Framework - Base Agent Implementation

本模块提供Agent基类实现，简化具体Agent的开发。

Author: MSRA Team
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
from abc import abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from datetime import datetime
import logging

from .interfaces import (
    IAgent,
    AgentStatus,
    AgentMessage,
    AgentCapability,
    Handoff,
    ConflictReport,
    ConflictLevel,
    ConflictType,
)

if TYPE_CHECKING:
    from .communication import MessageBus, TaskQueue
    from .cache import MultiLevelCache
    from .conflict_resolution import ConflictResolver


class BaseAgent(IAgent):
    """
    Agent基类 - 提供通用功能实现

    具体Agent只需实现:
    - execute(): 核心执行逻辑
    - get_capabilities(): 能力声明
    """

    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        config: Optional[Dict[str, Any]] = None
    ):
        self._agent_id = agent_id
        self._agent_type = agent_type
        self._config = config or {}
        self._status = AgentStatus.IDLE
        self._message_bus: Optional[MessageBus] = None
        self._task_queue: Optional[TaskQueue] = None
        self._cache: Optional[MultiLevelCache] = None
        self._conflict_resolver: Optional[ConflictResolver] = None
        self._logger = logging.getLogger(f"agent.{agent_id}")
        self._message_handlers: Dict[str, callable] = {}
        self._initialized = False

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def agent_type(self) -> str:
        return self._agent_type

    @property
    def status(self) -> AgentStatus:
        return self._status

    @property
    @abstractmethod
    def capabilities(self) -> List[AgentCapability]:
        pass

    def set_dependencies(
        self,
        message_bus: Optional[MessageBus] = None,
        task_queue: Optional[TaskQueue] = None,
        cache: Optional[MultiLevelCache] = None,
        conflict_resolver: Optional[ConflictResolver] = None
    ) -> None:
        """设置依赖组件"""
        if message_bus:
            self._message_bus = message_bus
        if task_queue:
            self._task_queue = task_queue
        if cache:
            self._cache = cache
        if conflict_resolver:
            self._conflict_resolver = conflict_resolver

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化Agent"""
        try:
            self._config.update(config)
            self._status = AgentStatus.IDLE

            # 注册消息处理器
            await self._register_message_handlers()

            # 订阅消息
            if self._message_bus:
                await self._message_bus.subscribe(
                    self._agent_id,
                    self._handle_message
                )

            self._initialized = True
            self._logger.info(f"Agent {self._agent_id} initialized")
            return True

        except Exception as e:
            self._logger.error(f"Failed to initialize: {e}")
            return False

    async def shutdown(self) -> bool:
        """关闭Agent"""
        try:
            self._status = AgentStatus.IDLE
            self._initialized = False
            self._logger.info(f"Agent {self._agent_id} shutdown")
            return True
        except Exception as e:
            self._logger.error(f"Failed to shutdown: {e}")
            return False

    async def receive_message(self, message: AgentMessage) -> AgentMessage:
        """接收消息"""
        self._logger.debug(f"Received message: {message.message_type}")

        handler = self._message_handlers.get(message.message_type)
        if handler:
            return await handler(message)

        return AgentMessage.create(
            sender=self._agent_id,
            recipient=message.sender,
            message_type="response",
            payload={"status": "unknown_message_type"},
            correlation_id=message.message_id
        )

    async def send_message(self, message: AgentMessage) -> bool:
        """发送消息"""
        if not self._message_bus:
            self._logger.error("Message bus not configured")
            return False

        try:
            recipient = message.recipient if isinstance(message.recipient, str) else message.recipient[0]
            await self._message_bus.publish(recipient, message)
            return True
        except Exception as e:
            self._logger.error(f"Failed to send message: {e}")
            return False

    async def report_conflict(self, conflict: ConflictReport) -> str:
        """上报冲突"""
        if not self._conflict_resolver:
            self._logger.warning("Conflict resolver not configured")
            return "no_resolver"

        # 发送冲突消息到仲裁者
        if self._message_bus:
            message = AgentMessage.create(
                sender=self._agent_id,
                recipient="arbitrator",
                message_type="conflict_report",
                payload={"conflict": conflict},
                priority=1  # 高优先级
            )
            await self.send_message(message)

        return conflict.conflict_id

    async def get_status(self) -> AgentStatus:
        """获取状态"""
        return self._status

    @abstractmethod
    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Handoff:
        """执行任务 - 子类必须实现"""
        pass

    # ========================================
    # Helper Methods
    # ========================================

    async def _register_message_handlers(self) -> None:
        """注册消息处理器 - 子类可覆盖"""
        self._message_handlers = {
            "request": self._handle_request,
            "ack": self._handle_ack,
            "nack": self._handle_nack,
            "task": self._handle_task,
            "conflict_report": self._handle_conflict_report,
        }

    async def _handle_message(self, message: AgentMessage) -> None:
        """处理接收到的消息"""
        try:
            response = await self.receive_message(message)
            if response and message.message_type == "request":
                await self.send_message(response)
        except Exception as e:
            self._logger.error(f"Error handling message: {e}")

    async def _handle_request(self, message: AgentMessage) -> AgentMessage:
        """处理请求消息"""
        return AgentMessage.create(
            sender=self._agent_id,
            recipient=message.sender,
            message_type="response",
            payload={"status": "received"},
            correlation_id=message.message_id
        )

    async def _handle_ack(self, message: AgentMessage) -> AgentMessage:
        """处理确认消息"""
        self._logger.debug(f"ACK received: {message.correlation_id}")
        return None

    async def _handle_nack(self, message: AgentMessage) -> AgentMessage:
        """处理否认消息"""
        self._logger.warning(f"NACK received: {message.payload.get('error')}")
        return None

    async def _handle_task(self, message: AgentMessage) -> AgentMessage:
        """处理任务消息"""
        task = message.payload.get("task", {})
        context = message.payload.get("context", {})

        self._status = AgentStatus.PROCESSING
        try:
            handoff = await self.execute(task, context)
            self._status = AgentStatus.COMPLETED

            return AgentMessage.create(
                sender=self._agent_id,
                recipient=message.sender,
                message_type="response",
                payload={"handoff": handoff.to_dict()},
                correlation_id=message.message_id
            )
        except Exception as e:
            self._status = AgentStatus.FAILED
            return AgentMessage.create(
                sender=self._agent_id,
                recipient=message.sender,
                message_type="response",
                payload={"error": str(e)},
                correlation_id=message.message_id
            )

    async def _handle_conflict_report(self, message: AgentMessage) -> AgentMessage:
        """处理冲突报告"""
        conflict_data = message.payload.get("conflict")
        if conflict_data and self._conflict_resolver:
            # 子类可覆盖此方法实现特定冲突处理
            pass
        return None

    def _create_handoff(
        self,
        completed_work: List[str],
        artifacts: Dict[str, str],
        verification_method: str,
        known_issues: List[str] = None,
        pending_decisions: List[str] = None,
        data_summary: Dict[str, Any] = None,
        next_agent: Optional[str] = None
    ) -> Handoff:
        """创建标准接棒格式"""
        return Handoff(
            agent_name=self._agent_id,
            completed_work=completed_work,
            artifacts=artifacts,
            verification_method=verification_method,
            known_issues=known_issues or [],
            pending_decisions=pending_decisions or [],
            data_summary=data_summary or {},
            next_agent=next_agent,
            status=self._status
        )

    def _create_conflict(
        self,
        target_agent: str,
        conflict_type: ConflictType,
        level: ConflictLevel,
        description: str,
        evidence: Dict[str, Any],
        suggestions: List[str]
    ) -> ConflictReport:
        """创建冲突报告"""
        return ConflictReport.create(
            source_agent=self._agent_id,
            target_agent=target_agent,
            conflict_type=conflict_type,
            level=level,
            description=description,
            evidence=evidence,
            suggestions=suggestions
        )


# ========================================
# Exports
# ========================================

__all__ = ["BaseAgent"]
