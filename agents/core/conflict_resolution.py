"""
MSRA Multi-Agent Framework - Conflict Resolution System

本模块实现了冲突检测、上报和解决机制，包括仲裁Agent和多种解决策略。

Author: MSRA Team
Version: 1.0.0
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

from .interfaces import (
    ConflictReport,
    ConflictResolution,
    ConflictLevel,
    ConflictType,
    ResolutionStrategy,
    AgentMessage,
    Handoff,
    AgentStatus,
)

if TYPE_CHECKING:
    from .communication import MessageBus


# ========================================
# Conflict Resolver
# ========================================

class ConflictResolver:
    """冲突解决器"""

    def __init__(self, message_bus: Optional["MessageBus"] = None):
        self._message_bus = message_bus
        self._resolution_history: List[ConflictResolution] = []
        self._pending_conflicts: Dict[str, ConflictReport] = {}
        self._voters: Dict[str, Any] = {}
        self._user_callback: Optional[callable] = None

        # 冲突类型 -> 解决策略映射
        self._strategy_map: Dict[ConflictType, ResolutionStrategy] = {
            ConflictType.DATA_INCONSISTENCY: ResolutionStrategy.AUTO_RESOLVE,
            ConflictType.METHOD_DISAGREEMENT: ResolutionStrategy.ARBITRATION,
            ConflictType.RESULT_DIVERGENCE: ResolutionStrategy.VOTING,
            ConflictType.QUALITY_GATE_FAILURE: ResolutionStrategy.ARBITRATION,
            ConflictType.RESOURCE_CONTENTION: ResolutionStrategy.AUTO_RESOLVE,
            ConflictType.PRIORITY_CONFLICT: ResolutionStrategy.ARBITRATION,
            ConflictType.TIMING_CONFLICT: ResolutionStrategy.AUTO_RESOLVE,
            ConflictType.SEMANTIC_MISMATCH: ResolutionStrategy.MERGE,
        }

        # 冲突级别 -> 最小策略映射
        self._level_strategy_min: Dict[ConflictLevel, ResolutionStrategy] = {
            ConflictLevel.TRIVIAL: ResolutionStrategy.AUTO_RESOLVE,
            ConflictLevel.MINOR: ResolutionStrategy.AUTO_RESOLVE,
            ConflictLevel.MODERATE: ResolutionStrategy.VOTING,
            ConflictLevel.SIGNIFICANT: ResolutionStrategy.ARBITRATION,
            ConflictLevel.CRITICAL: ResolutionStrategy.USER_DECISION,
        }

        # 解决规则
        self._resolution_rules: Dict[tuple, str] = {
            (ConflictType.DATA_INCONSISTENCY.value, "missing"): "fill_with_default",
            (ConflictType.DATA_INCONSISTENCY.value, "duplicate"): "keep_first",
            (ConflictType.DATA_INCONSISTENCY.value, "outlier"): "flag_and_exclude",
            (ConflictType.TIMING_CONFLICT.value, "order"): "timestamp_based",
            (ConflictType.SEMANTIC_MISMATCH.value, "format"): "normalize",
            (ConflictType.SEMANTIC_MISMATCH.value, "unit"): "convert_and_normalize",
        }

    def register_voter(self, agent_id: str, voter: Any) -> None:
        """注册投票者"""
        self._voters[agent_id] = voter

    def set_user_callback(self, callback: callable) -> None:
        """设置用户回调"""
        self._user_callback = callback

    async def resolve(self, conflict: ConflictReport) -> ConflictResolution:
        """解决冲突"""
        self._pending_conflicts[conflict.conflict_id] = conflict

        # 确定解决策略
        try:
            conflict_type = ConflictType(conflict.conflict_type)
        except ValueError:
            conflict_type = ConflictType.DATA_INCONSISTENCY

        base_strategy = self._strategy_map.get(
            conflict_type,
            ResolutionStrategy.ARBITRATION
        )
        min_strategy = self._level_strategy_min.get(
            conflict.conflict_level,
            ResolutionStrategy.ARBITRATION
        )

        # 选择更严格的策略
        strategy = self._choose_stricter(base_strategy, min_strategy)

        # 执行解决
        if strategy == ResolutionStrategy.AUTO_RESOLVE:
            resolution = await self._auto_resolve(conflict)
        elif strategy == ResolutionStrategy.VOTING:
            resolution = await self._voting_resolve(conflict)
        elif strategy == ResolutionStrategy.ARBITRATION:
            resolution = await self._arbitration_resolve(conflict)
        elif strategy == ResolutionStrategy.USER_DECISION:
            resolution = await self._user_decision(conflict)
        elif strategy == ResolutionStrategy.MERGE:
            resolution = await self._merge_resolve(conflict)
        elif strategy == ResolutionStrategy.ROLLBACK:
            resolution = await self._rollback_resolve(conflict)
        else:
            resolution = await self._default_resolve(conflict)

        # 更新历史
        self._resolution_history.append(resolution)
        conflict.resolution_status = "resolved"

        return resolution

    def _choose_stricter(
        self,
        strategy1: ResolutionStrategy,
        strategy2: ResolutionStrategy
    ) -> ResolutionStrategy:
        """选择更严格的策略"""
        priority = {
            ResolutionStrategy.AUTO_RESOLVE: 1,
            ResolutionStrategy.SKIP: 1,
            ResolutionStrategy.MERGE: 2,
            ResolutionStrategy.VOTING: 3,
            ResolutionStrategy.ARBITRATION: 4,
            ResolutionStrategy.USER_DECISION: 5,
            ResolutionStrategy.ROLLBACK: 6,
        }
        p1 = priority.get(strategy1, 3)
        p2 = priority.get(strategy2, 3)
        return strategy1 if p1 > p2 else strategy2

    async def _auto_resolve(self, conflict: ConflictReport) -> ConflictResolution:
        """自动解决"""
        resolution = self._apply_resolution_rules(conflict)

        return ConflictResolution(
            conflict_id=conflict.conflict_id,
            strategy_used=ResolutionStrategy.AUTO_RESOLVE,
            resolution=resolution,
            details={
                "rule_based": True,
                "conflict_type": conflict.conflict_type,
                "evidence": conflict.evidence
            },
            resolved_by="system",
            resolved_at=datetime.now(),
            artifacts_created=[]
        )

    async def _voting_resolve(self, conflict: ConflictReport) -> ConflictResolution:
        """投票解决"""
        voters = self._get_qualified_voters(conflict)
        votes = []

        for voter in voters:
            try:
                if hasattr(voter, 'vote_on_conflict'):
                    vote = await voter.vote_on_conflict(conflict)
                else:
                    # 默认投票
                    vote = ConflictVote(
                        voter_id=voter.agent_id if hasattr(voter, 'agent_id') else str(voter),
                        choice=conflict.resolution_suggestions[0] if conflict.resolution_suggestions else "accept",
                        confidence=0.5
                    )
                votes.append(vote)
            except Exception as e:
                logger.error(f"Voter {voter} failed: {e}")

        # 统计票数
        vote_counts: Dict[str, int] = defaultdict(int)
        for vote in votes:
            vote_counts[vote.choice] += 1

        # 选择多数票
        winner = max(vote_counts, key=vote_counts.get)

        return ConflictResolution(
            conflict_id=conflict.conflict_id,
            strategy_used=ResolutionStrategy.VOTING,
            resolution=winner,
            details={
                "votes": dict(vote_counts),
                "voters": [v.voter_id for v in votes],
                "total_voters": len(voters)
            },
            resolved_by="voting",
            resolved_at=datetime.now(),
            artifacts_created=[]
        )

    async def _arbitration_resolve(
        self,
        conflict: ConflictReport
    ) -> ConflictResolution:
        """仲裁解决 - 使用仲裁规则"""
        rules = self._get_arbitration_rules(conflict.conflict_type)

        # 确定权威来源
        primary = rules.get("primary_source", "qc_inspector")
        fallback = rules.get("fallback", "source_agent")
        tie_breaker = rules.get("tie_breaker", "user")

        # 基于证据选择
        if conflict.evidence.get("primary_evidence"):
            decision = primary
        elif conflict.evidence.get("fallback_available"):
            decision = fallback
        else:
            decision = tie_breaker

        return ConflictResolution(
            conflict_id=conflict.conflict_id,
            strategy_used=ResolutionStrategy.ARBITRATION,
            resolution=f"adopt_{decision}_recommendation",
            details={
                "rules_applied": rules,
                "decision_basis": "evidence_and_precedence",
                "primary_agent": primary,
                "fallback_agent": fallback
            },
            resolved_by="arbitration",
            resolved_at=datetime.now(),
            artifacts_created=[f"arbitration_rationale_{conflict.conflict_id}.md"]
        )

    async def _user_decision(
        self,
        conflict: ConflictReport
    ) -> ConflictResolution:
        """用户决定"""
        if self._user_callback:
            # 异步等待用户决定
            decision = await self._user_callback(conflict)
        else:
            # 默认决策
            decision = conflict.resolution_suggestions[0] if conflict.resolution_suggestions else "proceed_with_warning"

        return ConflictResolution(
            conflict_id=conflict.conflict_id,
            strategy_used=ResolutionStrategy.USER_DECISION,
            resolution=decision,
            details={
                "conflict_level": conflict.conflict_level.value,
                "escalation_reason": "critical_conflict"
            },
            resolved_by="user",
            resolved_at=datetime.now(),
            artifacts_created=[]
        )

    async def _merge_resolve(self, conflict: ConflictReport) -> ConflictResolution:
        """合并解决"""
        # 尝试合并冲突双方的输出
        merged = self._merge_outputs(
            conflict.evidence.get("output_a"),
            conflict.evidence.get("output_b")
        )

        return ConflictResolution(
            conflict_id=conflict.conflict_id,
            strategy_used=ResolutionStrategy.MERGE,
            resolution="merged_successfully",
            details={
                "merge_strategy": "union",
                "original_outputs": ["output_a", "output_b"]
            },
            resolved_by="system",
            resolved_at=datetime.now(),
            artifacts_created=[f"merged_output_{conflict.conflict_id}.json"]
        )

    async def _rollback_resolve(self, conflict: ConflictReport) -> ConflictResolution:
        """回滚解决"""
        return ConflictResolution(
            conflict_id=conflict.conflict_id,
            strategy_used=ResolutionStrategy.ROLLBACK,
            resolution="rollback_to_previous_state",
            details={
                "rollback_target": conflict.evidence.get("rollback_point"),
                "reason": "incompatible_state"
            },
            resolved_by="system",
            resolved_at=datetime.now(),
            artifacts_created=[]
        )

    async def _default_resolve(self, conflict: ConflictReport) -> ConflictResolution:
        """默认解决"""
        return ConflictResolution(
            conflict_id=conflict.conflict_id,
            strategy_used=ResolutionStrategy.AUTO_RESOLVE,
            resolution="use_primary_source",
            details={"fallback": True},
            resolved_by="system",
            resolved_at=datetime.now(),
            artifacts_created=[]
        )

    def _apply_resolution_rules(self, conflict: ConflictReport) -> str:
        """应用解决规则"""
        rule_key = (conflict.conflict_type, conflict.description)
        return self._resolution_rules.get(rule_key, "use_source_agent_result")

    def _get_qualified_voters(self, conflict: ConflictReport) -> List[Any]:
        """获取合格的投票者"""
        # 排除冲突双方
        excluded = {conflict.source_agent, conflict.target_agent}

        # 返回其他注册的投票者
        return [
            v for agent_id, v in self._voters.items()
            if agent_id not in excluded
        ]

    def _get_arbitration_rules(self, conflict_type: str) -> Dict[str, str]:
        """获取仲裁规则"""
        rules_map = {
            ConflictType.DATA_INCONSISTENCY.value: {
                "primary_source": "data_validator",
                "fallback": "method_consultant",
                "tie_breaker": "qc_inspector"
            },
            ConflictType.METHOD_DISAGREEMENT.value: {
                "primary_source": "method_consultant",
                "fallback": "exec_inference",
                "tie_breaker": "qc_inspector"
            },
            ConflictType.RESULT_DIVERGENCE.value: {
                "primary_source": "exec_inference",
                "fallback": "qc_inspector",
                "tie_breaker": "orchestrator"
            },
            ConflictType.QUALITY_GATE_FAILURE.value: {
                "primary_source": "qc_inspector",
                "fallback": "source_agent",
                "tie_breaker": "user"
            }
        }
        return rules_map.get(conflict_type, {
            "primary_source": "qc_inspector",
            "fallback": "source_agent",
            "tie_breaker": "user"
        })

    def _merge_outputs(self, output_a: Any, output_b: Any) -> Any:
        """合并输出"""
        if output_a is None:
            return output_b
        if output_b is None:
            return output_a

        # 尝试合并字典
        if isinstance(output_a, dict) and isinstance(output_b, dict):
            merged = output_a.copy()
            merged.update(output_b)
            return merged

        # 尝试合并列表
        if isinstance(output_a, list) and isinstance(output_b, list):
            return output_a + output_b

        # 默认返回第一个
        return output_a

    def get_resolution_history(
        self,
        agent_id: Optional[str] = None,
        start_time: Optional[datetime] = None
    ) -> List[ConflictResolution]:
        """获取解决历史"""
        history = self._resolution_history

        if agent_id:
            history = [
                r for r in history
                if agent_id in r.details.get("voters", [])
                or agent_id in r.resolved_by
            ]

        if start_time:
            history = [
                r for r in history
                if r.resolved_at >= start_time
            ]

        return history

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        strategy_counts: Dict[str, int] = defaultdict(int)
        for r in self._resolution_history:
            strategy_counts[r.strategy_used.value] += 1

        return {
            "total_resolved": len(self._resolution_history),
            "pending": len(self._pending_conflicts),
            "by_strategy": dict(strategy_counts),
            "voters_registered": len(self._voters)
        }


@dataclass
class ConflictVote:
    """投票"""
    voter_id: str
    choice: str
    confidence: float


# ========================================
# Exports
# ========================================

__all__ = [
    "ConflictResolver",
    "ConflictVote",
]
