"""
Agent 基类和生命周期管理

提供 Agent 运行时抽象，定义 Agent 接口和生命周期管理。
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from .state import AgentState
from .message import Message, MessageType, MessageBus
from .workflow import Workflow


class AgentCapability(str, Enum):
    """Agent 能力枚举"""
    CODE_GENERATION = "code_generation"  # 代码生成
    CODE_REVIEW = "code_review"  # 代码审查
    RESEARCH = "research"  # 研究分析
    DESIGN = "design"  # 设计
    WRITING = "writing"  # 文案写作
    DATA_ANALYSIS = "data_analysis"  # 数据分析
    PLANNING = "planning"  # 规划
    KNOWLEDGE_MANAGEMENT = "knowledge_management"  # 知识管理


@dataclass
class TaskContext:
    """任务上下文"""
    task_id: str
    task_title: str
    task_description: str
    upstream_outputs: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    """
    任务执行结果

    Attributes:
        success: 是否成功
        output: 输出数据
        error: 错误信息
        metadata: 附加元数据
    """
    success: bool
    output: Any = None
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


class Agent(ABC):
    """
    Agent 基类

    所有 Agent 实现必须继承此类并实现核心抽象方法。

    生命周期:
    1. initialize() - 初始化
    2. on_task_assigned() - 任务分配
    3. execute_task() - 执行任务
    4. on_task_completed() / on_task_failed() - 任务完成
    5. shutdown() - 关闭
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        capabilities: list[AgentCapability],
        message_bus: Optional[MessageBus] = None,
    ):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.message_bus = message_bus

        # 运行时状态
        self.state = AgentState.IDLE
        self.current_task: Optional[TaskContext] = None
        self.upstream_agents: list[str] = []
        self.downstream_agents: list[str] = []

        # 配置
        self.system_prompt = ""
        self.temperature = 0.7
        self.max_tokens = 2048

    @abstractmethod
    async def execute_task(self, context: TaskContext) -> TaskResult:
        """
        执行任务（子类必须实现）

        Args:
            context: 任务上下文

        Returns:
            任务执行结果
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """获取系统提示词（子类必须实现）"""
        pass

    def initialize(self) -> None:
        """初始化 Agent"""
        self.state = AgentState.IDLE
        self.system_prompt = self.get_system_prompt()

    def shutdown(self) -> None:
        """关闭 Agent"""
        self.state = AgentState.IDLE
        self.current_task = None

    async def on_task_assigned(
        self,
        task_id: str,
        task_title: str,
        task_description: str,
        upstream_outputs: Optional[list[dict[str, Any]]] = None,
    ) -> None:
        """
        任务分配回调

        Args:
            task_id: 任务 ID
            task_title: 任务标题
            task_description: 任务描述
            upstream_outputs: 上游任务输出列表
        """
        self.state = AgentState.WORKING
        self.current_task = TaskContext(
            task_id=task_id,
            task_title=task_title,
            task_description=task_description,
            upstream_outputs=upstream_outputs or [],
        )

    async def on_task_completed(self, result: TaskResult) -> None:
        """
        任务完成回调

        Args:
            result: 任务执行结果
        """
        self.state = AgentState.IDLE

        # 通知下游 Agent
        if self.downstream_agents and result.success:
            self._notify_downstream(result)

        self.current_task = None

    async def on_task_failed(self, error: str) -> None:
        """
        任务失败回调

        Args:
            error: 错误信息
        """
        self.state = AgentState.BLOCKED
        self.current_task = None

    def _notify_downstream(self, result: TaskResult) -> None:
        """通知下游 Agent"""
        if not self.message_bus:
            return

        for downstream_id in self.downstream_agents:
            self.message_bus.publish_sync(Message(
                project_id=self._get_current_project_id(),
                message_type=MessageType.TASK_HANDOFF,
                sender_id=self.agent_id,
                receiver_id=downstream_id,
                content=f"Upstream agent {self.name} completed task",
                metadata={"result": result.output},
            ))

    def _get_current_project_id(self) -> Optional[str]:
        """获取当前项目 ID（从任务上下文或子类实现）"""
        if self.current_task:
            return self.current_task.metadata.get("project_id")
        return None

    def can_accept_task(self) -> bool:
        """检查是否可以接受任务"""
        return self.state == AgentState.IDLE

    def is_waiting_for_upstream(self) -> bool:
        """检查是否正在等待上游"""
        return self.state == AgentState.WAITING

    def set_upstream_agents(self, agent_ids: list[str]) -> None:
        """设置上游 Agent 列表"""
        self.upstream_agents = agent_ids

    def set_downstream_agents(self, agent_ids: list[str]) -> None:
        """设置下游 Agent 列表"""
        self.downstream_agents = agent_ids

    def has_capability(self, capability: AgentCapability) -> bool:
        """检查是否具有指定能力"""
        return capability in self.capabilities

    def get_status(self) -> dict[str, Any]:
        """获取 Agent 状态"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "state": self.state.value,
            "current_task": self.current_task.task_id if self.current_task else None,
            "upstream_agents": self.upstream_agents,
            "downstream_agents": self.downstream_agents,
        }


class AgentLifecycleManager:
    """
    Agent 生命周期管理器

    管理 Agent 的创建、初始化、回收等生命周期操作。
    """

    def __init__(self):
        self._agents: dict[str, Agent] = {}
        self._initialized: set[str] = set()

    def register(self, agent: Agent) -> None:
        """
        注册 Agent

        Args:
            agent: Agent 实例
        """
        self._agents[agent.agent_id] = agent

    def unregister(self, agent_id: str) -> None:
        """注销 Agent"""
        if agent_id in self._agents:
            self.shutdown(agent_id)
            del self._agents[agent_id]

    def get(self, agent_id: str) -> Optional[Agent]:
        """获取 Agent 实例"""
        return self._agents.get(agent_id)

    def get_all(self) -> list[Agent]:
        """获取所有 Agent"""
        return list(self._agents.values())

    def initialize(self, agent_id: str) -> bool:
        """
        初始化 Agent

        Args:
            agent_id: Agent ID

        Returns:
            是否初始化成功
        """
        agent = self.get(agent_id)
        if not agent:
            return False

        if agent_id not in self._initialized:
            agent.initialize()
            self._initialized.add(agent_id)
        return True

    def shutdown(self, agent_id: str) -> bool:
        """
        关闭 Agent

        Args:
            agent_id: Agent ID

        Returns:
            是否关闭成功
        """
        agent = self.get(agent_id)
        if not agent:
            return False

        agent.shutdown()
        self._initialized.discard(agent_id)
        return True

    def is_initialized(self, agent_id: str) -> bool:
        """检查 Agent 是否已初始化"""
        return agent_id in self._initialized

    def get_active_agents(self) -> list[Agent]:
        """获取所有活跃的 Agent"""
        return [a for a in self._agents.values() if a.can_accept_task()]

    def get_agents_by_role(self, role: str) -> list[Agent]:
        """按角色获取 Agent 列表"""
        return [a for a in self._agents.values() if a.role == role]

    def get_agents_by_capability(self, capability: AgentCapability) -> list[Agent]:
        """按能力获取 Agent 列表"""
        return [
            a for a in self._agents.values()
            if a.has_capability(capability)
        ]


# 全局生命周期管理器实例
_lifecycle_manager: Optional[AgentLifecycleManager] = None


def get_lifecycle_manager() -> AgentLifecycleManager:
    """获取全局生命周期管理器实例"""
    global _lifecycle_manager
    if _lifecycle_manager is None:
        _lifecycle_manager = AgentLifecycleManager()
    return _lifecycle_manager


def reset_lifecycle_manager() -> None:
    """重置全局生命周期管理器（用于测试）"""
    global _lifecycle_manager
    _lifecycle_manager = None
