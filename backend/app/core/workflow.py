"""
工作流引擎核心模块

实现 4 阶段工作流引擎：初始化、规划、执行、完成。
"""
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
import asyncio

from .state import WorkflowState, WorkflowPhase, StateManager
from .message import MessageBus, Message, MessageType, get_message_bus


class WorkflowStatus(str, Enum):
    """工作流运行状态"""
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowError(Exception):
    """工作流异常基类"""
    pass


class WorkflowTransitionError(WorkflowError):
    """阶段转换错误"""
    pass


class WorkflowContext:
    """
    工作流上下文

    在项目生命周期内共享，所有 Agent 可访问的上下文信息。
    """

    def __init__(self, project_id: str):
        self.project_id = project_id
        self._data: dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def get(self, key: str, default: Any = None) -> Any:
        """获取上下文值"""
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """设置上下文值"""
        self._data[key] = value
        self.updated_at = datetime.utcnow()

    def update(self, data: dict[str, Any]) -> None:
        """批量更新上下文"""
        self._data.update(data)
        self.updated_at = datetime.utcnow()

    @property
    def data(self) -> dict[str, Any]:
        """获取所有上下文数据 (深拷贝)"""
        import copy
        return copy.deepcopy(self._data)


class Workflow:
    """
    工作流引擎核心类

    4 阶段单向流转:
    INIT -> PLANNING -> EXECUTING -> COMPLETED

    特性:
    - 状态持久化和快照
    - 阶段转换验证
    - 事件通知
    - 错误处理
    """

    def __init__(
        self,
        project_id: str,
        message_bus: Optional[MessageBus] = None,
    ):
        self.project_id = project_id
        self.state_manager = StateManager()
        self.state = self.state_manager.get_state(project_id)
        self.message_bus = message_bus or get_message_bus()
        self.context = WorkflowContext(project_id)
        self.status = WorkflowStatus.RUNNING
        self.error: Optional[str] = None

        # 阶段转换回调
        self._on_phase_change: list[Callable] = []

    def add_phase_change_callback(self, callback: Callable) -> None:
        """添加阶段变更回调"""
        self._on_phase_change.append(callback)

    def _notify_phase_change(
        self,
        old_phase: WorkflowPhase,
        new_phase: WorkflowPhase,
    ) -> None:
        """通知阶段变更"""
        for callback in self._on_phase_change:
            try:
                callback(old_phase, new_phase)
            except Exception as e:
                print(f"Error in phase change callback: {e}")

        # 发送消息通知
        self.message_bus.publish_sync(Message(
            project_id=self.project_id,
            message_type=MessageType.STATUS_UPDATE,
            content=f"Workflow phase changed: {old_phase.value} -> {new_phase.value}",
            metadata={
                "old_phase": old_phase.value,
                "new_phase": new_phase.value,
            },
        ))

    def transition_to(self, new_phase: WorkflowPhase, reason: str = "") -> bool:
        """
        转换到新的工作流阶段

        Args:
            new_phase: 目标阶段
            reason: 转换原因

        Returns:
            转换是否成功

        Raises:
            WorkflowTransitionError: 当转换不合法时
        """
        if self.status != WorkflowStatus.RUNNING:
            raise WorkflowTransitionError(
                f"Cannot transition workflow in status {self.status.value}"
            )

        old_phase = self.state.phase

        # 尝试转换
        if not self.state.transition_to(new_phase, reason):
            # 相同阶段转换返回 False 但不抛异常
            if old_phase == new_phase:
                return False
            raise WorkflowTransitionError(
                f"Cannot transition from {old_phase.value} to {new_phase.value}"
            )

        # 记录快照
        self.state.take_snapshot()

        # 通知回调
        self._notify_phase_change(old_phase, new_phase)

        return True

    def goto_planning(self, reason: str = "Starting planning phase") -> bool:
        """进入规划阶段"""
        if self.state.phase != WorkflowPhase.INIT:
            return False
        return self.transition_to(WorkflowPhase.PLANNING, reason)

    def goto_executing(self, reason: str = "Starting execution phase") -> bool:
        """进入执行阶段"""
        if self.state.phase != WorkflowPhase.PLANNING:
            return False
        return self.transition_to(WorkflowPhase.EXECUTING, reason)

    def goto_completed(self, reason: str = "Workflow completed") -> bool:
        """进入完成阶段"""
        if self.state.phase != WorkflowPhase.EXECUTING:
            return False
        return self.transition_to(WorkflowPhase.COMPLETED, reason)

    def is_phase(self, phase: WorkflowPhase) -> bool:
        """检查是否处于指定阶段"""
        return self.state.phase == phase

    def can_accept_tasks(self) -> bool:
        """检查是否可以接受任务"""
        return self.state.phase == WorkflowPhase.EXECUTING

    def is_completed(self) -> bool:
        """检查是否已完成"""
        return self.state.phase == WorkflowPhase.COMPLETED

    def set_context(self, key: str, value: Any) -> None:
        """设置工作流上下文"""
        self.context.set(key, value)

    def get_context(self, key: str, default: Any = None) -> Any:
        """获取工作流上下文"""
        return self.context.get(key, default)

    def pause(self) -> None:
        """暂停工作流"""
        if self.status == WorkflowStatus.RUNNING:
            self.status = WorkflowStatus.PAUSED

    def resume(self) -> None:
        """恢复工作流"""
        if self.status == WorkflowStatus.PAUSED:
            self.status = WorkflowStatus.RUNNING

    def fail(self, error: str) -> None:
        """标记工作流失败"""
        self.status = WorkflowStatus.FAILED
        self.error = error

    def get_state_snapshot(self) -> dict[str, Any]:
        """获取当前状态快照"""
        return {
            "project_id": self.project_id,
            "phase": self.state.phase.value,
            "status": self.status.value,
            "context": self.context.data,
            "data": self.state.data,
        }


class WorkflowEngine:
    """
    工作流引擎管理器

    管理多个项目的工作流实例，提供统一的创建、获取和销毁接口。
    """

    def __init__(self, message_bus: Optional[MessageBus] = None):
        self._workflows: dict[str, Workflow] = {}
        self.message_bus = message_bus or get_message_bus()

    def create_workflow(self, project_id: str) -> Workflow:
        """
        创建新的工作流实例

        Args:
            project_id: 项目 ID

        Returns:
            新创建的工作流实例
        """
        if project_id in self._workflows:
            return self._workflows[project_id]

        workflow = Workflow(
            project_id=project_id,
            message_bus=self.message_bus,
        )
        self._workflows[project_id] = workflow
        return workflow

    def get_workflow(self, project_id: str) -> Optional[Workflow]:
        """获取项目工作流实例"""
        return self._workflows.get(project_id)

    def remove_workflow(self, project_id: str) -> None:
        """移除项目工作流"""
        if project_id in self._workflows:
            del self._workflows[project_id]

    def get_all_workflows(self) -> dict[str, Workflow]:
        """获取所有工作流实例"""
        return dict(self._workflows)

    def get_active_workflows(self) -> list[Workflow]:
        """获取所有活跃的工作流"""
        return [
            wf for wf in self._workflows.values()
            if wf.status == WorkflowStatus.RUNNING
        ]


# 全局工作流引擎实例
_engine: Optional[WorkflowEngine] = None


def get_workflow_engine() -> WorkflowEngine:
    """获取全局工作流引擎实例"""
    global _engine
    if _engine is None:
        _engine = WorkflowEngine()
    return _engine


def reset_workflow_engine() -> None:
    """重置全局工作流引擎（用于测试）"""
    global _engine
    _engine = None
