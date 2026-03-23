"""
状态管理模块单元测试
"""
import pytest
from datetime import datetime
from app.core.state import (
    WorkflowPhase,
    AgentState,
    StateSnapshot,
    StateChange,
    WorkflowState,
    StateManager,
)


class TestWorkflowPhase:
    """测试工作流阶段枚举"""

    def test_phase_values(self):
        """测试阶段枚举值"""
        assert WorkflowPhase.INIT.value == "init"
        assert WorkflowPhase.PLANNING.value == "planning"
        assert WorkflowPhase.EXECUTING.value == "executing"
        assert WorkflowPhase.COMPLETED.value == "completed"

    def test_phase_order(self):
        """测试阶段顺序"""
        phases = list(WorkflowPhase)
        assert len(phases) == 4
        assert phases[0] == WorkflowPhase.INIT
        assert phases[1] == WorkflowPhase.PLANNING
        assert phases[2] == WorkflowPhase.EXECUTING
        assert phases[3] == WorkflowPhase.COMPLETED

    def test_phase_comparison(self):
        """测试阶段比较"""
        assert WorkflowPhase.INIT != WorkflowPhase.PLANNING
        assert WorkflowPhase.PLANNING == WorkflowPhase.PLANNING


class TestAgentState:
    """测试 Agent 状态枚举"""

    def test_state_values(self):
        """测试状态枚举值"""
        assert AgentState.IDLE.value == "idle"
        assert AgentState.WORKING.value == "working"
        assert AgentState.WAITING.value == "waiting"
        assert AgentState.BLOCKED.value == "blocked"


class TestStateSnapshot:
    """测试状态快照"""

    def test_snapshot_creation(self):
        """测试快照创建"""
        snapshot = StateSnapshot(
            timestamp=datetime.utcnow(),
            phase=WorkflowPhase.PLANNING,
            data={"key": "value"},
        )
        assert snapshot.phase == WorkflowPhase.PLANNING
        assert snapshot.data == {"key": "value"}
        assert isinstance(snapshot.timestamp, datetime)

    def test_snapshot_default_data(self):
        """测试快照默认数据"""
        snapshot = StateSnapshot(
            timestamp=datetime.utcnow(),
            phase=WorkflowPhase.INIT,
        )
        assert snapshot.data == {}


class TestStateChange:
    """测试状态变更记录"""

    def test_state_change_creation(self):
        """测试变更记录创建"""
        change = StateChange(
            key="phase",
            old_value=WorkflowPhase.INIT,
            new_value=WorkflowPhase.PLANNING,
            reason="Starting planning",
        )
        assert change.key == "phase"
        assert change.old_value == WorkflowPhase.INIT
        assert change.new_value == WorkflowPhase.PLANNING
        assert change.reason == "Starting planning"
        assert isinstance(change.timestamp, datetime)

    def test_state_change_default_timestamp(self):
        """测试默认时间戳"""
        change = StateChange()
        assert change.key == ""
        assert change.old_value is None
        assert change.new_value is None
        assert change.reason == ""
        assert isinstance(change.timestamp, datetime)


class TestWorkflowState:
    """测试工作流状态容器"""

    @pytest.fixture
    def workflow_state(self):
        """创建工作流状态实例"""
        return WorkflowState("test-project-123")

    def test_initial_state(self, workflow_state):
        """测试初始状态"""
        assert workflow_state.project_id == "test-project-123"
        assert workflow_state.phase == WorkflowPhase.INIT
        assert workflow_state.data == {}

    def test_get_set_state(self, workflow_state):
        """测试状态读写"""
        workflow_state.set("key1", "value1")
        assert workflow_state.get("key1") == "value1"

    def test_get_with_default(self, workflow_state):
        """测试带默认值的获取"""
        assert workflow_state.get("nonexistent", "default") == "default"
        assert workflow_state.get("nonexistent") is None

    def test_state_change_history(self, workflow_state):
        """测试状态变更历史"""
        workflow_state.set("key1", "value1", reason="Initial value")
        workflow_state.set("key1", "value2", reason="Updated value")

        history = workflow_state.get_history()
        assert len(history) == 2
        assert history[0].key == "key1"
        assert history[0].old_value is None
        assert history[0].new_value == "value1"
        assert history[1].old_value == "value1"
        assert history[1].new_value == "value2"

    def test_no_change_no_history(self, workflow_state):
        """测试相同值不记录历史"""
        workflow_state.set("key1", "value1")
        workflow_state.set("key1", "value1")  # 相同值

        history = workflow_state.get_history()
        assert len(history) == 1  # 只记录一次

    def test_transition_init_to_planning(self, workflow_state):
        """测试 INIT -> PLANNING 转换"""
        result = workflow_state.transition_to(WorkflowPhase.PLANNING, "Start planning")
        assert result is True
        assert workflow_state.phase == WorkflowPhase.PLANNING

    def test_transition_planning_to_executing(self, workflow_state):
        """测试 PLANNING -> EXECUTING 转换"""
        workflow_state.transition_to(WorkflowPhase.PLANNING)
        result = workflow_state.transition_to(WorkflowPhase.EXECUTING)
        assert result is True
        assert workflow_state.phase == WorkflowPhase.EXECUTING

    def test_transition_executing_to_completed(self, workflow_state):
        """测试 EXECUTING -> COMPLETED 转换"""
        workflow_state.transition_to(WorkflowPhase.PLANNING)
        workflow_state.transition_to(WorkflowPhase.EXECUTING)
        result = workflow_state.transition_to(WorkflowPhase.COMPLETED)
        assert result is True
        assert workflow_state.phase == WorkflowPhase.COMPLETED

    def test_cannot_transition_backward(self, workflow_state):
        """测试不能向后转换"""
        workflow_state.transition_to(WorkflowPhase.PLANNING)
        result = workflow_state.transition_to(WorkflowPhase.INIT)
        assert result is False
        assert workflow_state.phase == WorkflowPhase.PLANNING

    def test_cannot_skip_phase(self, workflow_state):
        """测试不能跳过阶段"""
        result = workflow_state.transition_to(WorkflowPhase.EXECUTING)
        assert result is False
        assert workflow_state.phase == WorkflowPhase.INIT

    def test_cannot_transition_to_same_phase(self, workflow_state):
        """测试不能转换到相同阶段"""
        workflow_state.transition_to(WorkflowPhase.PLANNING)
        result = workflow_state.transition_to(WorkflowPhase.PLANNING)
        assert result is False

    def test_transition_records_history(self, workflow_state):
        """测试转换记录历史"""
        workflow_state.transition_to(WorkflowPhase.PLANNING, "Test reason")

        history = workflow_state.get_history()
        assert len(history) == 1
        assert history[0].key == "phase"
        assert history[0].old_value == WorkflowPhase.INIT
        assert history[0].new_value == WorkflowPhase.PLANNING
        assert history[0].reason == "Test reason"

    def test_take_snapshot(self, workflow_state):
        """测试获取快照"""
        workflow_state.set("key1", "value1")
        workflow_state.transition_to(WorkflowPhase.PLANNING)

        snapshot = workflow_state.take_snapshot()

        assert snapshot.phase == WorkflowPhase.PLANNING
        assert snapshot.data == {"key1": "value1"}
        assert isinstance(snapshot.timestamp, datetime)

    def test_multiple_snapshots(self, workflow_state):
        """测试多个快照"""
        workflow_state.take_snapshot()
        workflow_state.transition_to(WorkflowPhase.PLANNING)
        workflow_state.take_snapshot()

        assert len(workflow_state._snapshots) == 2

    def test_get_latest_snapshot(self, workflow_state):
        """测试获取最新快照"""
        workflow_state.set("key1", "value1")
        snapshot1 = workflow_state.take_snapshot()

        workflow_state.set("key1", "value2")
        snapshot2 = workflow_state.take_snapshot()

        latest = workflow_state.get_latest_snapshot()
        assert latest == snapshot2
        assert latest.data["key1"] == "value2"

    def test_get_latest_snapshot_empty(self, workflow_state):
        """测试没有快照时返回 None"""
        assert workflow_state.get_latest_snapshot() is None

    def test_restore_snapshot(self, workflow_state):
        """测试恢复快照"""
        workflow_state.set("key1", "value1")
        workflow_state.transition_to(WorkflowPhase.PLANNING)
        snapshot = workflow_state.take_snapshot()

        # 修改状态
        workflow_state.set("key1", "value2")
        workflow_state.transition_to(WorkflowPhase.EXECUTING)

        # 恢复快照
        workflow_state.restore_snapshot(snapshot)

        assert workflow_state.phase == WorkflowPhase.PLANNING
        assert workflow_state.get("key1") == "value1"

    def test_data_property_returns_copy(self, workflow_state):
        """测试 data 属性返回副本"""
        workflow_state.set("key1", {"nested": "value"})
        data = workflow_state.data
        data["key1"]["nested"] = "modified"

        # 原始数据不应被修改
        assert workflow_state.get("key1")["nested"] == "value"


class TestStateManager:
    """测试状态管理器"""

    @pytest.fixture
    def state_manager(self):
        """创建状态管理器实例"""
        return StateManager()

    def test_get_state_creates_new(self, state_manager):
        """测试获取状态创建新的"""
        state = state_manager.get_state("project-1")
        assert state is not None
        assert state.project_id == "project-1"
        assert state.phase == WorkflowPhase.INIT

    def test_get_state_returns_same(self, state_manager):
        """测试获取状态返回相同的实例"""
        state1 = state_manager.get_state("project-1")
        state2 = state_manager.get_state("project-1")
        assert state1 is state2

    def test_remove_state(self, state_manager):
        """测试移除状态"""
        state_manager.get_state("project-1")
        state_manager.remove_state("project-1")

        # 再次获取会创建新的
        state = state_manager.get_state("project-1")
        assert state is not None
        assert state.phase == WorkflowPhase.INIT  # 新的实例，初始状态

    def test_get_all_states(self, state_manager):
        """测试获取所有状态"""
        state_manager.get_state("project-1")
        state_manager.get_state("project-2")

        states = state_manager.get_all_states()
        assert len(states) == 2
        assert "project-1" in states
        assert "project-2" in states

    def test_remove_nonexistent_state(self, state_manager):
        """测试移除不存在的状态不报错"""
        state_manager.remove_state("nonexistent")  # 应该不抛出异常


class TestWorkflowStateIntegration:
    """测试工作流状态集成"""

    def test_full_workflow_lifecycle(self):
        """测试完整工作流生命周期"""
        state = WorkflowState("integration-test")

        # 初始状态
        assert state.phase == WorkflowPhase.INIT

        # 进入规划阶段
        assert state.transition_to(WorkflowPhase.PLANNING, "Start planning")
        assert state.phase == WorkflowPhase.PLANNING

        # 设置一些状态数据
        state.set("plan", "Test plan")
        state.set("tasks", ["task1", "task2"])

        # 进入执行阶段
        assert state.transition_to(WorkflowPhase.EXECUTING, "Start execution")
        assert state.phase == WorkflowPhase.EXECUTING

        # 更新状态
        state.set("completed_tasks", ["task1"])

        # 获取快照
        snapshot = state.take_snapshot()
        assert snapshot.phase == WorkflowPhase.EXECUTING
        assert "plan" in snapshot.data

        # 进入完成阶段
        assert state.transition_to(WorkflowPhase.COMPLETED, "All done")
        assert state.phase == WorkflowPhase.COMPLETED

        # 验证历史记录
        history = state.get_history()
        assert len(history) >= 4  # 3 次阶段转换 + 至少 1 次数据设置

    def test_multiple_projects_isolation(self):
        """测试多项目状态隔离"""
        manager = StateManager()

        state1 = manager.get_state("project-1")
        state2 = manager.get_state("project-2")

        # 设置不同的数据
        state1.set("key", "value1")
        state2.set("key", "value2")

        # 验证隔离
        assert state1.get("key") == "value1"
        assert state2.get("key") == "value2"

        # 不同的阶段转换
        state1.transition_to(WorkflowPhase.PLANNING)
        assert state1.phase == WorkflowPhase.PLANNING
        assert state2.phase == WorkflowPhase.INIT  # 不受影响


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
