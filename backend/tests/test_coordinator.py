"""
协调器单元测试
"""
import pytest
import asyncio
from app.core.coordinator import (
    Coordinator,
    TaskScheduler,
    TaskAssignment,
    AgentDependency,
    create_coordinator,
)
from app.core.agent import (
    Agent,
    AgentCapability,
    TaskContext,
    TaskResult,
    AgentLifecycleManager,
    AgentState,
)
from app.core.message import MessageBus, MessageType
from app.core.message import MessageBus, get_message_bus, reset_message_bus


class MockAgent(Agent):
    """用于测试的 Mock Agent"""

    def __init__(self, agent_id: str = "test-agent", **kwargs):
        super().__init__(
            agent_id=agent_id,
            name="Test Agent",
            role="test_role",
            capabilities=[AgentCapability.PLANNING],
            **kwargs,
        )

    def get_system_prompt(self) -> str:
        return "Test system prompt"

    async def execute_task(self, context: TaskContext) -> TaskResult:
        return TaskResult(
            success=True,
            output={"task_id": context.task_id},
        )


@pytest.fixture
def clean_coordinator():
    """清理协调器"""
    reset_message_bus()
    yield
    reset_message_bus()


@pytest.fixture
def coordinator(clean_coordinator):
    """创建协调器实例"""
    return create_coordinator()


class TestTaskAssignment:
    """测试任务分配"""

    def test_task_assignment_creation(self):
        """测试任务分配创建"""
        assignment = TaskAssignment(
            task_id="task-123",
            agent_id="agent-1",
        )

        assert assignment.task_id == "task-123"
        assert assignment.agent_id == "agent-1"
        assert assignment.status == "pending"
        assert assignment.result is None


class TestAgentDependency:
    """测试 Agent 依赖"""

    def test_dependency_creation(self):
        """测试依赖创建"""
        dep = AgentDependency(
            agent_id="agent-1",
            upstream_ids=["agent-2", "agent-3"],
            downstream_ids=["agent-4"],
        )

        assert dep.agent_id == "agent-1"
        assert dep.upstream_ids == ["agent-2", "agent-3"]
        assert dep.downstream_ids == ["agent-4"]


class TestCoordinator:
    """测试协调器"""

    def test_register_agent(self, coordinator):
        """测试注册 Agent"""
        agent = MockAgent("agent-1")
        coordinator.register_agent(agent)

        assert coordinator.lifecycle_manager.get("agent-1") is agent

    def test_register_agent_with_dependencies(self, coordinator):
        """测试注册带依赖的 Agent"""
        agent = MockAgent("agent-1")
        coordinator.register_agent(
            agent,
            upstream_ids=["agent-2"],
            downstream_ids=["agent-3"],
        )

        dep = coordinator.get_agent_dependency("agent-1")
        assert dep.upstream_ids == ["agent-2"]
        assert dep.downstream_ids == ["agent-3"]
        assert agent.upstream_agents == ["agent-2"]
        assert agent.downstream_agents == ["agent-3"]

    def test_unregister_agent(self, coordinator):
        """测试注销 Agent"""
        agent = MockAgent("agent-1")
        coordinator.register_agent(agent)
        coordinator.unregister_agent("agent-1")

        assert coordinator.lifecycle_manager.get("agent-1") is None
        assert coordinator.get_agent_dependency("agent-1") is None

    def test_assign_to_project(self, coordinator):
        """测试分配到项目"""
        agent = MockAgent("agent-1")
        coordinator.register_agent(agent)
        coordinator.assign_to_project("project-1", "agent-1")

        agents = coordinator.get_project_agents("project-1")
        assert len(agents) == 1
        assert agents[0].agent_id == "agent-1"

    def test_get_project_agents_empty(self, coordinator):
        """测试获取空项目的 Agent"""
        agents = coordinator.get_project_agents("nonexistent")
        assert len(agents) == 0

    @pytest.mark.asyncio
    async def test_assign_task_success(self, coordinator):
        """测试成功分配任务"""
        agent = MockAgent("agent-1")
        coordinator.register_agent(agent)
        coordinator.assign_to_project("project-1", "agent-1")

        result = await coordinator.assign_task(
            task_id="task-123",
            task_title="Test Task",
            task_description="Test Description",
            agent_id="agent-1",
            project_id="project-1",
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_assign_task_nonexistent_agent(self, coordinator):
        """测试分配任务给不存在的 Agent"""
        result = await coordinator.assign_task(
            task_id="task-123",
            task_title="Test",
            task_description="Test",
            agent_id="nonexistent",
            project_id="project-1",
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_assign_task_busy_agent(self, coordinator):
        """测试分配任务给忙碌的 Agent"""
        agent = MockAgent("agent-1")
        agent.state = AgentState.WORKING
        coordinator.register_agent(agent)

        result = await coordinator.assign_task(
            task_id="task-123",
            task_title="Test",
            task_description="Test",
            agent_id="agent-1",
            project_id="project-1",
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_complete_task(self, coordinator):
        """测试完成任务"""
        agent = MockAgent("agent-1")
        coordinator.register_agent(agent)
        coordinator.assign_to_project("project-1", "agent-1")

        # 先分配任务
        await coordinator.assign_task(
            task_id="task-123",
            task_title="Test",
            task_description="Test",
            agent_id="agent-1",
            project_id="project-1",
        )

        # 完成任务
        result = TaskResult(success=True, output={"result": "done"})
        await coordinator.complete_task("task-123", result, "project-1")

        assignment = coordinator.get_assignment("task-123")
        assert assignment.status == "completed"

    @pytest.mark.asyncio
    async def test_complete_task_failure(self, coordinator):
        """测试任务完成失败"""
        agent = MockAgent("agent-1")
        coordinator.register_agent(agent)
        coordinator.assign_to_project("project-1", "agent-1")

        await coordinator.assign_task(
            task_id="task-123",
            task_title="Test",
            task_description="Test",
            agent_id="agent-1",
            project_id="project-1",
        )

        result = TaskResult(success=False, error="Test error")
        await coordinator.complete_task("task-123", result, "project-1")

        assignment = coordinator.get_assignment("task-123")
        assert assignment.status == "failed"

    def test_get_assignment(self, coordinator):
        """测试获取任务分配"""
        assignment = TaskAssignment(
            task_id="task-123",
            agent_id="agent-1",
        )
        coordinator._assignments["task-123"] = assignment

        retrieved = coordinator.get_assignment("task-123")
        assert retrieved is assignment

    def test_get_nonexistent_assignment(self, coordinator):
        """测试获取不存在的分配"""
        assignment = coordinator.get_assignment("nonexistent")
        assert assignment is None

    def test_clear_project(self, coordinator):
        """测试清空项目"""
        coordinator._project_agents["project-1"] = ["agent-1"]
        coordinator.clear_project("project-1")

        assert "project-1" not in coordinator._project_agents

    def test_get_pending_tasks(self, coordinator):
        """测试获取待处理任务"""
        coordinator._assignments = {
            "task-1": TaskAssignment(task_id="task-1", agent_id="agent-1"),
            "task-2": TaskAssignment(
                task_id="task-2",
                agent_id="agent-1",
                status="completed",
            ),
        }

        pending = coordinator.get_pending_tasks()
        assert len(pending) == 1
        assert pending[0].task_id == "task-1"

    def test_get_running_tasks(self, coordinator):
        """测试获取运行中任务"""
        coordinator._assignments = {
            "task-1": TaskAssignment(
                task_id="task-1",
                agent_id="agent-1",
                status="running",
            ),
            "task-2": TaskAssignment(
                task_id="task-2",
                agent_id="agent-1",
                status="pending",
            ),
        }

        running = coordinator.get_running_tasks()
        assert len(running) == 1
        assert running[0].task_id == "task-1"


class TestTaskScheduler:
    """测试任务调度器"""

    @pytest.fixture
    def scheduler(self, coordinator):
        """创建调度器"""
        return TaskScheduler(coordinator)

    def test_schedule_task(self, scheduler, coordinator):
        """测试调度任务"""
        coordinator.register_agent(MockAgent("agent-1"))

        scheduler.schedule_task(
            task_id="task-123",
            task_title="Test",
            task_description="Test",
            agent_id="agent-1",
            project_id="project-1",
        )

        assert len(scheduler._pending_schedules) == 1

    @pytest.mark.asyncio
    async def test_execute_scheduled_tasks(self, scheduler, coordinator):
        """测试执行调度的任务"""
        agent = MockAgent("agent-1")
        coordinator.register_agent(agent)
        coordinator.assign_to_project("project-1", "agent-1")

        scheduler.schedule_task(
            task_id="task-123",
            task_title="Test",
            task_description="Test",
            agent_id="agent-1",
            project_id="project-1",
        )

        results = await scheduler.execute_scheduled_tasks()

        assert len(results) == 1
        assert results[0] is True
        assert len(scheduler._pending_schedules) == 0

    def test_clear_schedules(self, scheduler):
        """测试清空调度"""
        scheduler._pending_schedules = [{"task_id": "task-1"}]
        scheduler.clear_schedules()

        assert len(scheduler._pending_schedules) == 0


class TestCoordinatorIntegration:
    """测试协调器集成"""

    @pytest.mark.asyncio
    async def test_trigger_downstream_agents(self, coordinator):
        """测试触发下游 Agent"""
        # 创建上游 Agent
        upstream = MockAgent("upstream-agent")
        # 创建下游 Agent
        downstream = MockAgent("downstream-agent")

        # 注册上游 Agent，指定下游
        coordinator.register_agent(
            upstream,
            downstream_ids=["downstream-agent"],
        )
        # 注册下游 Agent，指定上游
        coordinator.register_agent(
            downstream,
            upstream_ids=["upstream-agent"],
        )

        coordinator.assign_to_project("project-1", "upstream-agent")
        coordinator.assign_to_project("project-1", "downstream-agent")

        # 先分配任务给上游
        await coordinator.assign_task(
            task_id="task-1",
            task_title="Upstream Task",
            task_description="Test",
            agent_id="upstream-agent",
            project_id="project-1",
        )

        # 上游完成任务
        result = TaskResult(success=True, output={"data": "from upstream"})
        await coordinator.complete_task("task-1", result, "project-1")

        # 下游应该收到手递手消息
        message_bus = coordinator.message_bus
        messages = message_bus.get_history("project-1")

        handoff_messages = [
            m for m in messages
            if m.message_type == MessageType.TASK_HANDOFF
        ]
        assert len(handoff_messages) >= 1

    def test_create_coordinator_function(self):
        """测试创建协调器函数"""
        coordinator = create_coordinator()
        assert isinstance(coordinator, Coordinator)

    def test_create_coordinator_with_dependencies(self):
        """测试创建带依赖的协调器"""
        lifecycle_manager = AgentLifecycleManager()
        message_bus = MessageBus()

        coordinator = create_coordinator(
            lifecycle_manager=lifecycle_manager,
            message_bus=message_bus,
        )

        assert coordinator.lifecycle_manager is lifecycle_manager
        assert coordinator.message_bus is message_bus


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
