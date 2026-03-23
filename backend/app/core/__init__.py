"""
天工工作流引擎核心模块

包含工作流引擎、Agent 管理、协调器、状态管理和消息总线。
"""
from .workflow import (
    Workflow,
    WorkflowEngine,
    WorkflowContext,
    WorkflowPhase,
    WorkflowStatus,
    WorkflowError,
    WorkflowTransitionError,
    get_workflow_engine,
    reset_workflow_engine,
)
from .agent import (
    Agent,
    AgentCapability,
    AgentLifecycleManager,
    AgentState,
    TaskContext,
    TaskResult,
    get_lifecycle_manager,
    reset_lifecycle_manager,
)
from .coordinator import (
    Coordinator,
    TaskScheduler,
    TaskAssignment,
    AgentDependency,
    create_coordinator,
)
from .state import (
    WorkflowState,
    StateManager,
    StateSnapshot,
    StateChange,
    WorkflowPhase as StateWorkflowPhase,
    AgentState as StateAgentState,
)
from .message import (
    MessageBus,
    Message,
    MessageType,
    Subscription,
    get_message_bus,
    reset_message_bus,
)

__all__ = [
    # Workflow
    "Workflow",
    "WorkflowEngine",
    "WorkflowContext",
    "WorkflowPhase",
    "WorkflowStatus",
    "WorkflowError",
    "WorkflowTransitionError",
    "get_workflow_engine",
    "reset_workflow_engine",
    # Agent
    "Agent",
    "AgentCapability",
    "AgentLifecycleManager",
    "AgentState",
    "TaskContext",
    "TaskResult",
    "get_lifecycle_manager",
    "reset_lifecycle_manager",
    # Coordinator
    "Coordinator",
    "TaskScheduler",
    "TaskAssignment",
    "AgentDependency",
    "create_coordinator",
    # State
    "WorkflowState",
    "StateManager",
    "StateSnapshot",
    "StateChange",
    "StateWorkflowPhase",
    "StateAgentState",
    # Message
    "MessageBus",
    "Message",
    "MessageType",
    "Subscription",
    "get_message_bus",
    "reset_message_bus",
]
