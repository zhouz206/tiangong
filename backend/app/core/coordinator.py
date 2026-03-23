"""
Agent 协调器模块

负责任务分配和 Agent 间协调，管理 Agent 依赖关系。
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .message import MessageBus, Message, MessageType, get_message_bus
from .agent import Agent, TaskContext, TaskResult, AgentLifecycleManager
from .workflow import Workflow, WorkflowPhase


@dataclass
class TaskAssignment:
    """任务分配记录"""
    task_id: str
    agent_id: str
    project_id: str = ""
    assigned_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[TaskResult] = None


@dataclass
class AgentDependency:
    """Agent 依赖关系"""
    agent_id: str
    upstream_ids: list[str] = field(default_factory=list)
    downstream_ids: list[str] = field(default_factory=list)


class Coordinator:
    """
    Agent 协调器

    职责:
    - 任务分配给合适的 Agent
    - 管理 Agent 依赖关系
    - 触发下游任务执行
    - 监控任务执行状态
    """

    def __init__(
        self,
        lifecycle_manager: Optional[AgentLifecycleManager] = None,
        message_bus: Optional[MessageBus] = None,
    ):
        self.lifecycle_manager = lifecycle_manager or AgentLifecycleManager()
        self.message_bus = message_bus or get_message_bus()

        # 依赖关系管理
        self._dependencies: dict[str, AgentDependency] = {}

        # 任务分配记录
        self._assignments: dict[str, TaskAssignment] = {}

        # 项目 -> Agent 映射
        self._project_agents: dict[str, list[str]] = {}

    def register_agent(
        self,
        agent: Agent,
        upstream_ids: Optional[list[str]] = None,
        downstream_ids: Optional[list[str]] = None,
    ) -> None:
        """
        注册 Agent 及其依赖关系

        Args:
            agent: Agent 实例
            upstream_ids: 上游 Agent ID 列表
            downstream_ids: 下游 Agent ID 列表
        """
        self.lifecycle_manager.register(agent)

        dep = AgentDependency(
            agent_id=agent.agent_id,
            upstream_ids=upstream_ids or [],
            downstream_ids=downstream_ids or [],
        )
        self._dependencies[agent.agent_id] = dep

        # 设置 Agent 的依赖关系
        agent.set_upstream_agents(upstream_ids or [])
        agent.set_downstream_agents(downstream_ids or [])

    def unregister_agent(self, agent_id: str) -> None:
        """注销 Agent"""
        if agent_id in self._dependencies:
            del self._dependencies[agent_id]
        self.lifecycle_manager.unregister(agent_id)

    def assign_to_project(self, project_id: str, agent_id: str) -> None:
        """将 Agent 分配到项目"""
        if project_id not in self._project_agents:
            self._project_agents[project_id] = []
        if agent_id not in self._project_agents[project_id]:
            self._project_agents[project_id].append(agent_id)

    def get_project_agents(self, project_id: str) -> list[Agent]:
        """获取项目下的所有 Agent"""
        agent_ids = self._project_agents.get(project_id, [])
        agents = []
        for agent_id in agent_ids:
            agent = self.lifecycle_manager.get(agent_id)
            if agent:
                agents.append(agent)
        return agents

    async def assign_task(
        self,
        task_id: str,
        task_title: str,
        task_description: str,
        agent_id: str,
        project_id: str,
        upstream_outputs: Optional[list[dict[str, Any]]] = None,
    ) -> bool:
        """
        分配任务给 Agent

        Args:
            task_id: 任务 ID
            task_title: 任务标题
            task_description: 任务描述
            agent_id: Agent ID
            project_id: 项目 ID
            upstream_outputs: 上游任务输出

        Returns:
            分配是否成功
        """
        agent = self.lifecycle_manager.get(agent_id)
        if not agent:
            return False

        if not agent.can_accept_task():
            return False

        # 检查上游依赖是否完成（仅检查当前项目的任务）
        dep = self._dependencies.get(agent_id)
        if dep and dep.upstream_ids:
            for upstream_id in dep.upstream_ids:
                if not self._is_project_agent_task_completed(upstream_id, project_id):
                    # 上游未完成，等待
                    agent.state = type('AgentState').WAITING if hasattr(agent.state, 'WAITING') else agent.state
                    return False

        # 创建任务分配记录
        assignment = TaskAssignment(
            task_id=task_id,
            agent_id=agent_id,
            project_id=project_id,
        )
        self._assignments[task_id] = assignment

        # 通知 Agent
        await agent.on_task_assigned(
            task_id=task_id,
            task_title=task_title,
            task_description=task_description,
            upstream_outputs=upstream_outputs,
        )

        # 发送任务分配消息
        self.message_bus.publish_sync(Message(
            project_id=project_id,
            message_type=MessageType.TASK_ASSIGN,
            receiver_id=agent_id,
            content=f"Task assigned: {task_title}",
            metadata={
                "task_id": task_id,
                "task_title": task_title,
            },
        ))

        return True

    async def complete_task(
        self,
        task_id: str,
        result: TaskResult,
        project_id: str,
    ) -> None:
        """
        完成任务并触发下游

        Args:
            task_id: 任务 ID
            result: 任务结果
            project_id: 项目 ID
        """
        assignment = self._assignments.get(task_id)
        if not assignment:
            return

        agent_id = assignment.agent_id
        agent = self.lifecycle_manager.get(agent_id)
        if not agent:
            return

        # 更新分配记录
        assignment.status = "completed" if result.success else "failed"
        assignment.result = result

        # 通知 Agent
        if result.success:
            await agent.on_task_completed(result)
        else:
            await agent.on_task_failed(result.error or "Unknown error")

        # 触发下游 Agent
        if result.success:
            await self._trigger_downstream_agents(agent_id, result, project_id)

    async def _trigger_downstream_agents(
        self,
        upstream_agent_id: str,
        result: TaskResult,
        project_id: str,
    ) -> None:
        """触发下游 Agent 执行"""
        dep = self._dependencies.get(upstream_agent_id)
        if not dep:
            return

        for downstream_id in dep.downstream_ids:
            downstream_agent = self.lifecycle_manager.get(downstream_id)
            if not downstream_agent:
                continue

            if not downstream_agent.can_accept_task():
                continue

            # 发送手递手消息
            self.message_bus.publish_sync(Message(
                project_id=project_id,
                message_type=MessageType.TASK_HANDOFF,
                sender_id=upstream_agent_id,
                receiver_id=downstream_id,
                content=f"Upstream agent {upstream_agent_id} completed, passing result",
                metadata={"result": result.output},
            ))

    def _is_agent_task_completed(self, agent_id: str) -> bool:
        """检查 Agent 的当前任务是否完成"""
        # 遍历所有分配记录，查找该 Agent 的最新任务
        for assignment in self._assignments.values():
            if assignment.agent_id == agent_id:
                return assignment.status in ("completed", "failed")
        # 没有任务记录，认为已完成（无需等待）
        return True

    def _is_project_agent_task_completed(self, agent_id: str, project_id: str) -> bool:
        """检查指定项目的 Agent 任务是否完成"""
        # 仅检查当前项目的任务分配记录
        for assignment in self._assignments.values():
            if assignment.agent_id == agent_id and assignment.project_id == project_id:
                return assignment.status in ("completed", "failed")
        # 没有任务记录，认为已完成（无需等待）
        return True

    def get_assignment(self, task_id: str) -> Optional[TaskAssignment]:
        """获取任务分配记录"""
        return self._assignments.get(task_id)

    def get_agent_dependency(self, agent_id: str) -> Optional[AgentDependency]:
        """获取 Agent 依赖关系"""
        return self._dependencies.get(agent_id)

    def get_pending_tasks(self) -> list[TaskAssignment]:
        """获取所有待处理任务"""
        return [
            a for a in self._assignments.values()
            if a.status == "pending"
        ]

    def get_running_tasks(self) -> list[TaskAssignment]:
        """获取所有运行中任务"""
        return [
            a for a in self._assignments.values()
            if a.status == "running"
        ]

    def clear_project(self, project_id: str) -> None:
        """清空项目相关状态"""
        if project_id in self._project_agents:
            del self._project_agents[project_id]


class TaskScheduler:
    """
    任务调度器

    根据工作流阶段和 Agent 状态调度任务执行。
    """

    def __init__(self, coordinator: Coordinator):
        self.coordinator = coordinator
        self._pending_schedules: list[dict[str, Any]] = []

    def schedule_task(
        self,
        task_id: str,
        task_title: str,
        task_description: str,
        agent_id: str,
        project_id: str,
        upstream_outputs: Optional[list[dict[str, Any]]] = None,
    ) -> None:
        """
        调度任务（不立即执行）

        Args:
            task_id: 任务 ID
            task_title: 任务标题
            task_description: 任务描述
            agent_id: Agent ID
            project_id: 项目 ID
            upstream_outputs: 上游任务输出
        """
        self._pending_schedules.append({
            "task_id": task_id,
            "task_title": task_title,
            "task_description": task_description,
            "agent_id": agent_id,
            "project_id": project_id,
            "upstream_outputs": upstream_outputs or [],
        })

    async def execute_scheduled_tasks(self) -> list[bool]:
        """执行所有调度的任务"""
        results = []
        for schedule in self._pending_schedules:
            result = await self.coordinator.assign_task(**schedule)
            results.append(result)
        self._pending_schedules.clear()
        return results

    def clear_schedules(self) -> None:
        """清空调度队列"""
        self._pending_schedules.clear()


def create_coordinator(
    lifecycle_manager: Optional[AgentLifecycleManager] = None,
    message_bus: Optional[MessageBus] = None,
) -> Coordinator:
    """创建协调器实例"""
    return Coordinator(
        lifecycle_manager=lifecycle_manager,
        message_bus=message_bus,
    )
