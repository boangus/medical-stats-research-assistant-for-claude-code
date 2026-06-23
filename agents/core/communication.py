"""
MSRA Multi-Agent Framework - Communication Protocol

本模块实现了Agent间的通信协议，包括消息队列、优先级调度和确认机制。

Author: MSRA Team
Version: 1.0.0
"""

import asyncio
import uuid
import json
import logging
from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

from .interfaces import (
    AgentMessage,
    AgentStatus,
    TaskPriority,
    TaskStatus,
    Task,
    TaskResult,
    TaskDependency,
    ConflictReport,
    ConflictResolution,
    ResolutionStrategy,
    ConflictLevel,
    ConflictType,
    Handoff,
)


# ========================================
# Message Queue
# ========================================

class QueuedMessage:
    """队列消息"""
    def __init__(
        self,
        message: AgentMessage,
        queued_at: datetime,
        attempts: int = 0,
        last_attempt: Optional[datetime] = None,
        status: str = "pending"
    ):
        self.message = message
        self.queued_at = queued_at
        self.attempts = attempts
        self.last_attempt = last_attempt
        self.status = status


class PriorityMessageQueue:
    """优先级消息队列"""

    def __init__(self):
        self._queues: Dict[int, List[QueuedMessage]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def enqueue(self, message: AgentMessage) -> str:
        """入队消息"""
        async with self._lock:
            queued = QueuedMessage(
                message=message,
                queued_at=datetime.now()
            )
            self._queues[message.priority].append(queued)
            return message.message_id

    async def dequeue(self) -> Optional[QueuedMessage]:
        """出队消息（最高优先级）"""
        async with self._lock:
            for priority in range(1, 11):
                if self._queues[priority]:
                    return self._queues[priority].pop(0)
            return None

    async def peek(self, priority: Optional[int] = None) -> Optional[QueuedMessage]:
        """查看队首消息"""
        async with self._lock:
            if priority:
                return self._queues[priority][0] if self._queues[priority] else None
            for p in range(1, 11):
                if self._queues[p]:
                    return self._queues[p][0]
            return None

    async def size(self) -> int:
        """获取队列大小"""
        async with self._lock:
            return sum(len(q) for q in self._queues.values())

    async def get_by_recipient(self, recipient: str) -> List[QueuedMessage]:
        """获取指定接收者的所有消息"""
        async with self._lock:
            result = []
            for queue in self._queues.values():
                for qm in queue:
                    if qm.message.recipient == recipient:
                        result.append(qm)
            return result


class MessageBus:
    """消息总线 - 异步消息通信中枢"""

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        exponential_backoff: bool = True
    ):
        self._queues: Dict[str, PriorityMessageQueue] = defaultdict(PriorityMessageQueue)
        self._subscriptions: Dict[str, List[Callable]] = defaultdict(list)
        self._processing: Dict[str, asyncio.Task] = {}
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._exponential_backoff = exponential_backoff
        self._running = False
        self._lock = asyncio.Lock()
        self._message_handlers: Dict[str, Callable] = {}

    async def publish(
        self,
        recipient: str,
        message: AgentMessage
    ) -> str:
        """发布消息到指定队列"""
        return await self._queues[recipient].enqueue(message)

    async def broadcast(
        self,
        recipients: List[str],
        message: AgentMessage
    ) -> List[str]:
        """广播消息到多个队列"""
        message_ids = []
        for recipient in recipients:
            msg_copy = AgentMessage(
                message_id=str(uuid.uuid4()),
                sender=message.sender,
                recipient=recipient,
                message_type=message.message_type,
                payload=message.payload,
                priority=message.priority,
                ttl=message.ttl
            )
            msg_id = await self._queues[recipient].enqueue(msg_copy)
            message_ids.append(msg_id)
        return message_ids

    async def subscribe(
        self,
        agent_id: str,
        callback: Callable[[AgentMessage], Any]
    ) -> None:
        """订阅消息"""
        self._subscriptions[agent_id].append(callback)

    async def register_handler(
        self,
        message_type: str,
        handler: Callable[[AgentMessage], Any]
    ) -> None:
        """注册消息处理器"""
        self._message_handlers[message_type] = handler

    async def start_processing(self) -> None:
        """启动消息处理循环"""
        self._running = True
        while self._running:
            try:
                await self._process_queues()
            except Exception as e:
                logger.error(f"Error in message processing: {e}", exc_info=True)
            await asyncio.sleep(0.1)

    async def stop_processing(self) -> None:
        """停止消息处理"""
        self._running = False

    async def _process_queues(self) -> None:
        """处理所有队列"""
        for agent_id, queue in list(self._queues.items()):
            if agent_id not in self._processing:
                msg = await queue.dequeue()
                if msg:
                    self._processing[agent_id] = asyncio.create_task(
                        self._process_message(msg)
                    )

    async def _process_message(self, queued: QueuedMessage) -> None:
        """处理单条消息"""
        message = queued.message
        recipient = message.recipient if isinstance(message.recipient, str) else message.recipient[0]

        try:
            # 调用订阅者回调
            if recipient in self._subscriptions:
                for callback in self._subscriptions[recipient]:
                    result = await callback(message)
                    if result:
                        await self._send_ack(message, "delivered", result)

            # 调用消息类型处理器
            if message.message_type in self._message_handlers:
                handler = self._message_handlers[message.message_type]
                await handler(message)

        except Exception as e:
            queued.attempts += 1
            queued.last_attempt = datetime.now()

            if queued.attempts < message.max_retries:
                delay = self._retry_delay * (
                    2 ** (queued.attempts - 1)
                ) if self._exponential_backoff else self._retry_delay

                await asyncio.sleep(delay)
                recipient = message.recipient if isinstance(message.recipient, str) else message.recipient[0]
                await self._queues[recipient].enqueue(message)
            else:
                await self._send_nack(message, str(e))

        finally:
            # 清理处理任务
            if recipient in self._processing:
                del self._processing[recipient]

    async def _send_ack(
        self,
        original: AgentMessage,
        status: str,
        result: Any = None
    ) -> None:
        """发送确认"""
        ack = AgentMessage.create(
            sender="message_bus",
            recipient=original.sender,
            message_type="ack",
            payload={
                "original_id": original.message_id,
                "status": status,
                "result": result
            },
            correlation_id=original.message_id,
            priority=10  # 低优先级
        )
        await self._queues[original.sender].enqueue(ack)

    async def _send_nack(
        self,
        original: AgentMessage,
        error: str
    ) -> None:
        """发送否认"""
        nack = AgentMessage.create(
            sender="message_bus",
            recipient=original.sender,
            message_type="nack",
            payload={
                "original_id": original.message_id,
                "error": error
            },
            correlation_id=original.message_id,
            priority=10
        )
        recipient = original.sender
        await self._queues[recipient].enqueue(nack)

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "queues": {k: v._queues for k, v in self._queues.items()},
            "subscriptions": {k: len(v) for k, v in self._subscriptions.items()},
            "processing": len(self._processing),
            "handlers": len(self._message_handlers)
        }


# ========================================
# Task Priority Queue
# ========================================

class TaskQueue:
    """任务优先级队列"""

    def __init__(self, max_concurrent: int = 10):
        self._queues: Dict[TaskPriority, asyncio.PriorityQueue] = {
            priority: asyncio.PriorityQueue()
            for priority in TaskPriority
        }
        self._running: Dict[str, Task] = {}
        self._completed: Dict[str, TaskResult] = {}
        self._blocked: Dict[str, List[str]] = {}
        self._pending_tasks: Dict[str, Task] = {}
        self._max_concurrent = max_concurrent
        self._lock = asyncio.Lock()

    async def enqueue(self, task: Task) -> str:
        """入队任务"""
        async with self._lock:
            can_run = await self._check_dependencies(task)

            if can_run:
                await self._queues[task.priority].put(task)
                self._pending_tasks[task.task_id] = task
                task.status = TaskStatus.QUEUED
            else:
                for dep in task.dependencies:
                    if dep.task_id not in self._blocked:
                        self._blocked[dep.task_id] = []
                    self._blocked[dep.task_id].append(task.task_id)

            return task.task_id

    async def dequeue(self) -> Optional[Task]:
        """出队任务"""
        async with self._lock:
            for priority in TaskPriority:
                queue = self._queues[priority]
                if not queue.empty() and len(self._running) < self._max_concurrent:
                    try:
                        task = queue.get_nowait()
                        del self._pending_tasks[task.task_id]
                        task.status = TaskStatus.RUNNING
                        self._running[task.task_id] = task
                        return task
                    except asyncio.QueueEmpty:
                        continue
        return None

    async def complete(
        self,
        task_id: str,
        result: Optional[TaskResult] = None
    ) -> None:
        """完成任务"""
        async with self._lock:
            if task_id in self._running:
                del self._running[task_id]

            self._completed[task_id] = result or TaskResult(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                completed_at=datetime.now()
            )

            if task_id in self._blocked:
                blocked_ids = self._blocked.pop(task_id)
                for blocked_id in blocked_ids:
                    await self._unblock_task(blocked_id)

    async def fail(self, task_id: str, error: str) -> None:
        """任务失败"""
        async with self._lock:
            if task_id in self._running:
                del self._running[task_id]

            self._completed[task_id] = TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                error=error,
                completed_at=datetime.now()
            )

    async def _check_dependencies(self, task: Task) -> bool:
        """检查依赖是否满足"""
        for dep in task.dependencies:
            if dep.task_id not in self._completed:
                return False
            completed_task = self._completed[dep.task_id]
            if completed_task.status != TaskStatus.COMPLETED:
                if not dep.optional and dep.dependency_type == "blocks":
                    return False
        return True

    async def _unblock_task(self, task_id: str) -> None:
        """解锁任务 - O(1) 查找"""
        async with self._lock:
            if task_id in self._pending_tasks:
                task = self._pending_tasks[task_id]
                can_run = await self._check_dependencies(task)
                if can_run:
                    await self._queues[task.priority].put(task)
                    task.status = TaskStatus.QUEUED

    def get_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        return {
            "running": len(self._running),
            "max_concurrent": self._max_concurrent,
            "completed": len(self._completed),
            "queues": {
                priority.name: queue.qsize()
                for priority, queue in self._queues.items()
            },
            "blocked": {k: len(v) for k, v in self._blocked.items()}
        }

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        if task_id in self._running:
            return self._running[task_id]
        return None

    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """获取任务结果"""
        return self._completed.get(task_id)


# ========================================
# Exports
# ========================================

__all__ = [
    "QueuedMessage",
    "PriorityMessageQueue",
    "MessageBus",
    "TaskQueue",
]
