"""
MSRA Multi-Agent Framework - Agent Implementations

具体Agent实现，继承BaseAgent并实现各角色的核心功能。

Author: MSRA Team
Version: 1.0.0
"""

from .data_validator_agent import DataValidatorAgent
from .method_consultant_agent import MethodConsultantAgent
from .exec_runner_agent import ExecRunnerAgent
from .exec_inference_agent import ExecInferenceAgent
from .qc_inspector_agent import QCInspectorAgent
from .hybrid_mode_bridge import (
    HybridModeBridge,
    SubAgentType,
    AgentMode,
    SubAgentTask,
    SubAgentResult,
    create_bridge,
    build_qc_task,
    build_inference_task,
)

__all__ = [
    "DataValidatorAgent",
    "MethodConsultantAgent",
    "ExecRunnerAgent",
    "ExecInferenceAgent",
    "QCInspectorAgent",
    "HybridModeBridge",
    "SubAgentType",
    "AgentMode",
    "SubAgentTask",
    "SubAgentResult",
    "create_bridge",
    "build_qc_task",
    "build_inference_task",
]
