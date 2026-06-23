"""
MSRA Multi-Agent Framework - Resource Monitor

本模块实现资源监控仪表板，追踪Agent执行状态、Token消耗、缓存效率等指标。

Author: MSRA Team
Version: 1.0.0
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import json
import logging


@dataclass
class MetricPoint:
    """指标数据点"""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class AgentMetrics:
    """Agent指标"""
    agent_id: str
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time: float = 0.0
    avg_execution_time: float = 0.0
    tokens_input: int = 0
    tokens_output: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    conflicts_resolved: int = 0
    last_activity: Optional[datetime] = None


class ResourceMonitor:
    """
    资源监控仪表板

    功能:
    - Agent执行指标追踪
    - Token消耗监控
    - 缓存效率监控
    - 任务队列状态
    - 冲突统计
    - 告警机制
    """

    def __init__(
        self,
        alert_thresholds: Optional[Dict[str, float]] = None,
        history_retention_hours: int = 24
    ):
        self._agent_metrics: Dict[str, AgentMetrics] = defaultdict(
            lambda: AgentMetrics(agent_id="unknown")
        )
        self._metric_history: Dict[str, List[MetricPoint]] = defaultdict(list)
        self._alerts: List[Dict[str, Any]] = []
        self._alert_callbacks: List[Callable] = []
        self._lock = asyncio.Lock()
        self._logger = logging.getLogger("resource_monitor")

        # 告警阈值
        self._alert_thresholds = alert_thresholds or {
            "token_usage_per_task": 50000,
            "task_failure_rate": 0.1,
            "cache_hit_rate": 0.5,
            "execution_time": 300,  # seconds
            "queue_size": 100,
        }

        self._history_retention = timedelta(hours=history_retention_hours)

    async def record_task_start(
        self,
        agent_id: str,
        task_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """记录任务开始"""
        async with self._lock:
            self._agent_metrics[agent_id].agent_id = agent_id
            self._agent_metrics[agent_id].last_activity = datetime.now()

            await self._record_metric(
                f"task.start.{agent_id}",
                1,
                {"task_id": task_id}
            )

    async def record_task_complete(
        self,
        agent_id: str,
        task_id: str,
        execution_time: float,
        tokens_input: int = 0,
        tokens_output: int = 0,
        success: bool = True
    ) -> None:
        """记录任务完成"""
        async with self._lock:
            metrics = self._agent_metrics[agent_id]
            metrics.agent_id = agent_id

            if success:
                metrics.tasks_completed += 1
            else:
                metrics.tasks_failed += 1

            metrics.total_execution_time += execution_time
            metrics.avg_execution_time = (
                metrics.total_execution_time /
                (metrics.tasks_completed + metrics.tasks_failed)
            )
            metrics.tokens_input += tokens_input
            metrics.tokens_output += tokens_output
            metrics.last_activity = datetime.now()

            # 记录指标
            await self._record_metric(
                f"task.complete.{agent_id}",
                execution_time,
                {"task_id": task_id, "success": str(success)}
            )

            await self._record_metric(
                f"tokens.input.{agent_id}",
                tokens_input,
                {"task_id": task_id}
            )

            await self._record_metric(
                f"tokens.output.{agent_id}",
                tokens_output,
                {"task_id": task_id}
            )

            # 检查告警
            await self._check_alerts(agent_id, {
                "execution_time": execution_time,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "failure_rate": metrics.tasks_failed / max(1, metrics.tasks_completed + metrics.tasks_failed)
            })

    async def record_cache_hit(self, agent_id: str, level: str = "L1") -> None:
        """记录缓存命中"""
        async with self._lock:
            self._agent_metrics[agent_id].cache_hits += 1
            await self._record_metric(
                f"cache.hit.{agent_id}",
                1,
                {"level": level}
            )

    async def record_cache_miss(self, agent_id: str) -> None:
        """记录缓存未命中"""
        async with self._lock:
            self._agent_metrics[agent_id].cache_misses += 1
            await self._record_metric(
                f"cache.miss.{agent_id}",
                1
            )

    async def record_conflict(
        self,
        agent_id: str,
        conflict_type: str,
        resolution_strategy: str
    ) -> None:
        """记录冲突"""
        async with self._lock:
            self._agent_metrics[agent_id].conflicts_resolved += 1
            await self._record_metric(
                f"conflict.{agent_id}",
                1,
                {"type": conflict_type, "strategy": resolution_strategy}
            )

    async def record_queue_status(
        self,
        queue_name: str,
        size: int,
        running: int
    ) -> None:
        """记录队列状态"""
        await self._record_metric(
            f"queue.size.{queue_name}",
            size
        )
        await self._record_metric(
            f"queue.running.{queue_name}",
            running
        )

        # 检查队列告警
        if size > self._alert_thresholds.get("queue_size", 100):
            await self._trigger_alert(
                "queue_size",
                f"Queue {queue_name} size ({size}) exceeds threshold",
                {"queue": queue_name, "size": size}
            )

    async def get_agent_metrics(self, agent_id: str) -> Optional[AgentMetrics]:
        """获取Agent指标"""
        return self._agent_metrics.get(agent_id)

    async def get_all_metrics(self) -> Dict[str, AgentMetrics]:
        """获取所有Agent指标"""
        return dict(self._agent_metrics)

    async def get_metric_history(
        self,
        metric_name: str,
        since: Optional[datetime] = None
    ) -> List[MetricPoint]:
        """获取指标历史"""
        history = self._metric_history.get(metric_name, [])

        if since:
            history = [p for p in history if p.timestamp >= since]

        return history

    async def get_summary(self) -> Dict[str, Any]:
        """获取监控摘要"""
        total_completed = sum(m.tasks_completed for m in self._agent_metrics.values())
        total_failed = sum(m.tasks_failed for m in self._agent_metrics.values())
        total_tokens_input = sum(m.tokens_input for m in self._agent_metrics.values())
        total_tokens_output = sum(m.tokens_output for m in self._agent_metrics.values())
        total_cache_hits = sum(m.cache_hits for m in self._agent_metrics.values())
        total_cache_misses = sum(m.cache_misses for m in self._agent_metrics.values())

        return {
            "timestamp": datetime.now().isoformat(),
            "agents": {
                agent_id: {
                    "tasks_completed": m.tasks_completed,
                    "tasks_failed": m.tasks_failed,
                    "success_rate": m.tasks_completed / max(1, m.tasks_completed + m.tasks_failed),
                    "avg_execution_time": m.avg_execution_time,
                    "tokens_input": m.tokens_input,
                    "tokens_output": m.tokens_output,
                    "cache_hit_rate": m.cache_hits / max(1, m.cache_hits + m.cache_misses),
                    "last_activity": m.last_activity.isoformat() if m.last_activity else None
                }
                for agent_id, m in self._agent_metrics.items()
            },
            "totals": {
                "tasks_completed": total_completed,
                "tasks_failed": total_failed,
                "success_rate": total_completed / max(1, total_completed + total_failed),
                "tokens_input": total_tokens_input,
                "tokens_output": total_tokens_output,
                "cache_hit_rate": total_cache_hits / max(1, total_cache_hits + total_cache_misses)
            },
            "alerts": len(self._alerts),
            "recent_alerts": self._alerts[-5:] if self._alerts else []
        }

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """获取仪表板数据"""
        summary = await self.get_summary()

        # 添加趋势数据
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)

        trends = {}
        for metric_name in ["tokens.input", "tokens.output", "task.complete"]:
            history = await self.get_metric_history(metric_name, hour_ago)
            if history:
                trends[metric_name] = {
                    "points": [
                        {"time": p.timestamp.isoformat(), "value": p.value}
                        for p in history
                    ]
                }

        return {
            **summary,
            "trends": trends
        }

    def add_alert_callback(self, callback: Callable) -> None:
        """添加告警回调"""
        self._alert_callbacks.append(callback)

    async def _record_metric(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """记录指标"""
        point = MetricPoint(
            timestamp=datetime.now(),
            value=value,
            tags=tags or {}
        )
        self._metric_history[name].append(point)

        # 清理过期数据
        cutoff = datetime.now() - self._history_retention
        self._metric_history[name] = [
            p for p in self._metric_history[name]
            if p.timestamp >= cutoff
        ]

    async def _check_alerts(
        self,
        agent_id: str,
        metrics: Dict[str, float]
    ) -> None:
        """检查告警条件"""
        # 检查执行时间
        if metrics.get("execution_time", 0) > self._alert_thresholds.get("execution_time", 300):
            await self._trigger_alert(
                "execution_time",
                f"Agent {agent_id} execution time ({metrics['execution_time']:.1f}s) exceeds threshold",
                {"agent_id": agent_id, "execution_time": metrics["execution_time"]}
            )

        # 检查Token使用
        total_tokens = metrics.get("tokens_input", 0) + metrics.get("tokens_output", 0)
        if total_tokens > self._alert_thresholds.get("token_usage_per_task", 50000):
            await self._trigger_alert(
                "token_usage",
                f"Agent {agent_id} token usage ({total_tokens}) exceeds threshold",
                {"agent_id": agent_id, "tokens": total_tokens}
            )

        # 检查失败率
        if metrics.get("failure_rate", 0) > self._alert_thresholds.get("task_failure_rate", 0.1):
            await self._trigger_alert(
                "failure_rate",
                f"Agent {agent_id} failure rate ({metrics['failure_rate']:.1%}) exceeds threshold",
                {"agent_id": agent_id, "failure_rate": metrics["failure_rate"]}
            )

    async def _trigger_alert(
        self,
        alert_type: str,
        message: str,
        details: Dict[str, Any]
    ) -> None:
        """触发告警"""
        alert = {
            "type": alert_type,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }

        self._alerts.append(alert)
        self._logger.warning(f"Alert: {message}")

        # 调用回调
        for callback in self._alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert)
                else:
                    callback(alert)
            except Exception as e:
                self._logger.error(f"Alert callback error: {e}")

    async def export_metrics(self, format: str = "json") -> str:
        """导出指标"""
        summary = await self.get_summary()

        if format == "json":
            return json.dumps(summary, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")


# ========================================
# Global Monitor Instance
# ========================================

_global_monitor: Optional[ResourceMonitor] = None


def get_monitor() -> ResourceMonitor:
    """获取全局监控器"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = ResourceMonitor()
    return _global_monitor


def init_monitor(
    alert_thresholds: Optional[Dict[str, float]] = None,
    history_retention_hours: int = 24
) -> ResourceMonitor:
    """初始化全局监控器"""
    global _global_monitor
    _global_monitor = ResourceMonitor(alert_thresholds, history_retention_hours)
    return _global_monitor


# ========================================
# Exports
# ========================================

__all__ = [
    "ResourceMonitor",
    "AgentMetrics",
    "MetricPoint",
    "get_monitor",
    "init_monitor",
]
