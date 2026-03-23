"""
状态管理模块

提供工作流引擎的状态容器和状态变更记录功能。
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class WorkflowPhase(str, Enum):
    """工作流阶段枚举 - 简化 4 阶段单向流转"""
    INIT = "init"  # 初始化阶段
    PLANNING = "planning"  # 规划阶段
    EXECUTING = "executing"  # 执行阶段
    COMPLETED = "completed"  # 完成阶段


class AgentState(str, Enum):
    """Agent 运行时状态枚举"""
    IDLE = "idle"  # 空闲
    WORKING = "working"  # 工作中
    WAITING = "waiting"  # 等待上游
    BLOCKED = "blocked"  # 已阻塞


@dataclass
class StateSnapshot:
    """状态快照 - 用于回滚和审计"""
    timestamp: datetime
    phase: WorkflowPhase
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class StateChange:
    """状态变更记录"""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    key: str = ""
    old_value: Any = None
    new_value: Any = None
    reason: str = ""


class WorkflowState:
    """
    工作流状态容器

    管理项目工作流的当前状态，支持状态快照和变更追踪。
    """

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.phase = WorkflowPhase.INIT
        self._data: dict[str, Any] = {}
        self._history: list[StateChange] = []
        self._snapshots: list[StateSnapshot] = []

    @property
    def data(self) -> dict[str, Any]:
        """获取状态数据（深拷贝）"""
        import copy
        return copy.deepcopy(self._data)

    def get(self, key: str, default: Any = None) -> Any:
        """获取状态值"""
        return self._data.get(key, default)

    def set(self, key: str, value: Any, reason: str = "") -> None:
        """设置状态值并记录变更"""
        old_value = self._data.get(key)
        if old_value != value:
            self._data[key] = value
            self._history.append(StateChange(
                key=key,
                old_value=old_value,
                new_value=value,
                reason=reason,
            ))

    def transition_to(self, new_phase: WorkflowPhase, reason: str = "") -> bool:
        """
        转换工作流阶段

        只允许单向流转：INIT -> PLANNING -> EXECUTING -> COMPLETED
        """
        phase_order = list(WorkflowPhase)
        current_idx = phase_order.index(self.phase)
        new_idx = phase_order.index(new_phase)

        # 只允许向前转换
        if new_idx <= current_idx:
            return False

        # 只允许转换到下一阶段
        if new_idx != current_idx + 1:
            return False

        old_phase = self.phase
        self.phase = new_phase
        self._history.append(StateChange(
            key="phase",
            old_value=old_phase,
            new_value=new_phase,
            reason=reason,
        ))
        return True

    def take_snapshot(self) -> StateSnapshot:
        """获取当前状态快照"""
        snapshot = StateSnapshot(
            timestamp=datetime.utcnow(),
            phase=self.phase,
            data=dict(self._data),
        )
        self._snapshots.append(snapshot)
        return snapshot

    def restore_snapshot(self, snapshot: StateSnapshot) -> None:
        """恢复到指定快照状态"""
        self.phase = snapshot.phase
        self._data = dict(snapshot.data)

    def get_history(self) -> list[StateChange]:
        """获取状态变更历史"""
        return list(self._history)

    def get_latest_snapshot(self) -> Optional[StateSnapshot]:
        """获取最新快照"""
        return self._snapshots[-1] if self._snapshots else None


class StateManager:
    """
    状态管理器

    管理多个项目的状态容器，提供按项目隔离的状态管理。
    """

    def __init__(self):
        self._states: dict[str, WorkflowState] = {}

    def get_state(self, project_id: str) -> WorkflowState:
        """获取或创建项目状态容器"""
        if project_id not in self._states:
            self._states[project_id] = WorkflowState(project_id)
        return self._states[project_id]

    def remove_state(self, project_id: str) -> None:
        """移除项目状态"""
        if project_id in self._states:
            del self._states[project_id]

    def get_all_states(self) -> dict[str, WorkflowState]:
        """获取所有项目状态"""
        return dict(self._states)
