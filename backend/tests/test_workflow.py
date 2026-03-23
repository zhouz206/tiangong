"""
工作流引擎单元测试
"""
import pytest
import asyncio
from app.core.workflow import (
    Workflow,
    WorkflowEngine,
    WorkflowPhase,
    WorkflowStatus,
    WorkflowTransitionError,
    WorkflowContext,
    get_workflow_engine,
    reset_workflow_engine,
)
from app.core.message import get_message_bus, reset_message_bus


@pytest.fixture
def clean_workflow_engine():
    """清理工作流引擎"""
    reset_workflow_engine()
    reset_message_bus()
    yield
    reset_workflow_engine()
    reset_message_bus()


class TestWorkflowPhase:
    """测试工作流阶段"""

    def test_phase_values(self):
        """测试阶段枚举值"""
        assert WorkflowPhase.INIT.value == "init"
        assert WorkflowPhase.PLANNING.value == "planning"
        assert WorkflowPhase.EXECUTING.value == "executing"
        assert WorkflowPhase.COMPLETED.value == "completed"

    def test_phase_order(self):
        """测试阶段顺序"""
        phases = list(WorkflowPhase)
        assert phases.index(WorkflowPhase.INIT) == 0
        assert phases.index(WorkflowPhase.PLANNING) == 1
        assert phases.index(WorkflowPhase.EXECUTING) == 2
        assert phases.index(WorkflowPhase.COMPLETED) == 3


class TestWorkflow:
    """测试工作流核心功能"""

    @pytest.fixture
    def workflow(self, clean_workflow_engine):
        """创建工作流实例"""
        engine = get_workflow_engine()
        return engine.create_workflow("test-project-123")

    def test_initial_state(self, workflow):
        """测试初始状态"""
        assert workflow.is_phase(WorkflowPhase.INIT)
        assert workflow.status == WorkflowStatus.RUNNING
        assert workflow.project_id == "test-project-123"

    def test_goto_planning(self, workflow):
        """测试进入规划阶段"""
        result = workflow.goto_planning()
        assert result is True
        assert workflow.is_phase(WorkflowPhase.PLANNING)

    def test_goto_executing_from_init_fails(self, workflow):
        """测试从 INIT 直接到 EXECUTING 应该失败"""
        result = workflow.goto_executing()
        assert result is False
        assert workflow.is_phase(WorkflowPhase.INIT)

    def test_full_workflow(self, workflow):
        """测试完整工作流"""
        # INIT -> PLANNING
        assert workflow.goto_planning()
        assert workflow.is_phase(WorkflowPhase.PLANNING)

        # PLANNING -> EXECUTING
        assert workflow.goto_executing()
        assert workflow.is_phase(WorkflowPhase.EXECUTING)

        # EXECUTING -> COMPLETED
        assert workflow.goto_completed()
        assert workflow.is_phase(WorkflowPhase.COMPLETED)

    def test_completed_is_terminal(self, workflow):
        """测试完成阶段是终端状态"""
        workflow.goto_planning()
        workflow.goto_executing()
        workflow.goto_completed()

        # 完成后不能再转换
        with pytest.raises(WorkflowTransitionError):
            workflow.transition_to(WorkflowPhase.PLANNING)

    def test_transition_with_reason(self, workflow):
        """测试带原因的转换"""
        result = workflow.goto_planning(reason="Starting planning")
        assert result is True

        history = workflow.state.get_history()
        assert len(history) >= 1
        assert history[-1].reason == "Starting planning"

    def test_cannot_transition_same_phase(self, workflow):
        """测试不能转换到相同阶段"""
        workflow.goto_planning()
        # 已经是 PLANNING，不能再次转换到 PLANNING
        result = workflow.transition_to(WorkflowPhase.PLANNING)
        assert result is False

    def test_workflow_context(self, workflow):
        """测试工作流上下文"""
        workflow.set_context("key1", "value1")
        assert workflow.get_context("key1") == "value1"
        assert workflow.get_context("nonexistent", "default") == "default"

    def test_workflow_context_update(self, workflow):
        """测试上下文更新"""
        workflow.set_context("counter", 1)
        workflow.set_context("counter", 2)
        assert workflow.get_context("counter") == 2

    def test_pause_and_resume(self, workflow):
        """测试暂停和恢复"""
        workflow.pause()
        assert workflow.status == WorkflowStatus.PAUSED

        workflow.resume()
        assert workflow.status == WorkflowStatus.RUNNING

    def test_fail_workflow(self, workflow):
        """测试失败工作流"""
        workflow.fail("Test error")
        assert workflow.status == WorkflowStatus.FAILED
        assert workflow.error == "Test error"

    def test_can_accept_tasks(self, workflow):
        """测试是否可以接受任务"""
        assert workflow.can_accept_tasks() is False  # INIT 阶段

        workflow.goto_planning()
        assert workflow.can_accept_tasks() is False  # PLANNING 阶段

        workflow.goto_executing()
        assert workflow.can_accept_tasks() is True  # EXECUTING 阶段

    def test_state_snapshot(self, workflow):
        """测试状态快照"""
        workflow.goto_planning()
        snapshot = workflow.get_state_snapshot()

        assert snapshot["project_id"] == "test-project-123"
        assert snapshot["phase"] == "planning"
        assert "context" in snapshot
        assert "data" in snapshot

    def test_phase_change_callback(self, workflow, clean_workflow_engine):
        """测试阶段变更回调"""
        callback_called = []

        def on_phase_change(old_phase, new_phase):
            callback_called.append((old_phase, new_phase))

        workflow.add_phase_change_callback(on_phase_change)
        workflow.goto_planning()

        assert len(callback_called) == 1
        assert callback_called[0] == (WorkflowPhase.INIT, WorkflowPhase.PLANNING)


class TestWorkflowEngine:
    """测试工作流引擎"""

    def test_create_workflow(self, clean_workflow_engine):
        """测试创建工作流"""
        engine = get_workflow_engine()
        workflow = engine.create_workflow("project-1")

        assert workflow is not None
        assert workflow.project_id == "project-1"
        assert workflow.is_phase(WorkflowPhase.INIT)

    def test_get_workflow(self, clean_workflow_engine):
        """测试获取工作流"""
        engine = get_workflow_engine()
        engine.create_workflow("project-1")

        workflow = engine.get_workflow("project-1")
        assert workflow is not None
        assert workflow.project_id == "project-1"

    def test_get_nonexistent_workflow(self, clean_workflow_engine):
        """测试获取不存在的工作流"""
        engine = get_workflow_engine()
        workflow = engine.get_workflow("nonexistent")
        assert workflow is None

    def test_remove_workflow(self, clean_workflow_engine):
        """测试移除工作流"""
        engine = get_workflow_engine()
        engine.create_workflow("project-1")
        engine.remove_workflow("project-1")

        assert engine.get_workflow("project-1") is None

    def test_get_all_workflows(self, clean_workflow_engine):
        """测试获取所有工作流"""
        engine = get_workflow_engine()
        engine.create_workflow("project-1")
        engine.create_workflow("project-2")

        workflows = engine.get_all_workflows()
        assert len(workflows) == 2

    def test_get_active_workflows(self, clean_workflow_engine):
        """测试获取活跃工作流"""
        engine = get_workflow_engine()
        wf1 = engine.create_workflow("project-1")
        wf2 = engine.create_workflow("project-2")

        wf2.fail("Test failure")

        active = engine.get_active_workflows()
        assert len(active) == 1
        assert active[0].project_id == "project-1"

    def test_singleton_workflow_engine(self, clean_workflow_engine):
        """测试引擎单例"""
        engine1 = get_workflow_engine()
        engine2 = get_workflow_engine()
        assert engine1 is engine2


class TestWorkflowContext:
    """测试工作流上下文"""

    def test_context_get_set(self):
        """测试上下文读写"""
        ctx = WorkflowContext("test-project")
        ctx.set("key", "value")
        assert ctx.get("key") == "value"

    def test_context_default(self):
        """测试默认值"""
        ctx = WorkflowContext("test-project")
        assert ctx.get("nonexistent", "default") == "default"
        assert ctx.get("nonexistent") is None

    def test_context_update(self):
        """测试批量更新"""
        ctx = WorkflowContext("test-project")
        ctx.update({"a": 1, "b": 2})
        assert ctx.get("a") == 1
        assert ctx.get("b") == 2

    def test_context_data_copy(self):
        """测试数据副本"""
        ctx = WorkflowContext("test-project")
        ctx.set("key", {"nested": "value"})
        data = ctx.data
        data["key"]["nested"] = "modified"
        # 原始数据不应被修改
        assert ctx.get("key")["nested"] == "value"


class TestWorkflowIntegration:
    """测试工作流集成"""

    def test_workflow_with_message_bus(self, clean_workflow_engine):
        """测试带消息总线的工作流"""
        engine = get_workflow_engine()
        workflow = engine.create_workflow("test-project")

        messages_received = []

        def on_message(msg):
            messages_received.append(msg)

        message_bus = get_message_bus()
        message_bus.subscribe("test-project", on_message)

        workflow.goto_planning()

        # 应该有阶段变更消息
        assert len(messages_received) >= 1

    @pytest.mark.asyncio
    async def test_async_workflow_operations(self, clean_workflow_engine):
        """测试异步工作流操作"""
        engine = get_workflow_engine()
        workflow = engine.create_workflow("async-test")

        # 同步操作
        workflow.goto_planning()
        assert workflow.is_phase(WorkflowPhase.PLANNING)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
