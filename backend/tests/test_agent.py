"""
Agent 单元测试
"""
import pytest
from app.core.agent import (
    Agent,
    AgentCapability,
    AgentState,
    TaskContext,
    TaskResult,
    AgentLifecycleManager,
    get_lifecycle_manager,
    reset_lifecycle_manager,
)
from app.core.message import MessageBus


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
            output={"task_id": context.task_id, "result": "completed"},
        )


@pytest.fixture
def clean_lifecycle_manager():
    """清理生命周期管理器"""
    reset_lifecycle_manager()
    yield
    reset_lifecycle_manager()


class TestAgentCapability:
    """测试 Agent 能力枚举"""

    def test_capability_values(self):
        """测试能力枚举值"""
        assert AgentCapability.CODE_GENERATION.value == "code_generation"
        assert AgentCapability.CODE_REVIEW.value == "code_review"
        assert AgentCapability.RESEARCH.value == "research"
        assert AgentCapability.DESIGN.value == "design"
        assert AgentCapability.WRITING.value == "writing"
        assert AgentCapability.DATA_ANALYSIS.value == "data_analysis"
        assert AgentCapability.PLANNING.value == "planning"
        assert AgentCapability.KNOWLEDGE_MANAGEMENT.value == "knowledge_management"


class TestAgent:
    """测试 Agent 基类"""

    @pytest.fixture
    def agent(self):
        """创建测试 Agent"""
        return MockAgent()

    def test_agent_initialization(self, agent):
        """测试 Agent 初始化"""
        assert agent.agent_id == "test-agent"
        assert agent.name == "Test Agent"
        assert agent.role == "test_role"
        assert agent.state == AgentState.IDLE
        assert len(agent.capabilities) == 1

    def test_has_capability(self, agent):
        """测试能力检查"""
        assert agent.has_capability(AgentCapability.PLANNING) is True
        assert agent.has_capability(AgentCapability.CODE_GENERATION) is False

    def test_can_accept_task(self, agent):
        """测试任务接受检查"""
        assert agent.can_accept_task() is True

    def test_initialize(self, agent, clean_lifecycle_manager):
        """测试初始化"""
        agent.state = AgentState.WORKING
        agent.initialize()
        assert agent.state == AgentState.IDLE

    def test_shutdown(self, agent):
        """测试关闭"""
        agent.state = AgentState.WORKING
        agent.shutdown()
        assert agent.state == AgentState.IDLE
        assert agent.current_task is None

    @pytest.mark.asyncio
    async def test_on_task_assigned(self, agent):
        """测试任务分配回调"""
        await agent.on_task_assigned(
            task_id="task-123",
            task_title="Test Task",
            task_description="Test Description",
        )

        assert agent.state == AgentState.WORKING
        assert agent.current_task is not None
        assert agent.current_task.task_id == "task-123"

    @pytest.mark.asyncio
    async def test_on_task_completed(self, agent):
        """测试任务完成回调"""
        agent.state = AgentState.WORKING
        result = TaskResult(success=True, output={"result": "done"})

        await agent.on_task_completed(result)

        assert agent.state == AgentState.IDLE
        assert agent.current_task is None

    @pytest.mark.asyncio
    async def test_on_task_failed(self, agent):
        """测试任务失败回调"""
        agent.state = AgentState.WORKING

        await agent.on_task_failed("Test error")

        assert agent.state == AgentState.BLOCKED
        assert agent.current_task is None

    @pytest.mark.asyncio
    async def test_execute_task(self, agent):
        """测试任务执行"""
        context = TaskContext(
            task_id="task-123",
            task_title="Test",
            task_description="Test Description",
        )

        result = await agent.execute_task(context)

        assert result.success is True
        assert result.output["task_id"] == "task-123"

    def test_set_upstream_agents(self, agent):
        """测试设置上游 Agent"""
        agent.set_upstream_agents(["agent-1", "agent-2"])
        assert agent.upstream_agents == ["agent-1", "agent-2"]

    def test_set_downstream_agents(self, agent):
        """测试设置下游 Agent"""
        agent.set_downstream_agents(["agent-3", "agent-4"])
        assert agent.downstream_agents == ["agent-3", "agent-4"]

    def test_get_status(self, agent):
        """测试获取状态"""
        status = agent.get_status()

        assert status["agent_id"] == "test-agent"
        assert status["name"] == "Test Agent"
        assert status["role"] == "test_role"
        assert status["state"] == "idle"

    def test_system_prompt(self, agent):
        """测试系统提示词"""
        assert agent.get_system_prompt() == "Test system prompt"
        assert agent.system_prompt == ""  # 初始化前为空

    def test_agent_with_message_bus(self):
        """测试带消息总线的 Agent"""
        message_bus = MessageBus()
        agent = MockAgent(message_bus=message_bus)

        assert agent.message_bus is message_bus


class TestTaskContext:
    """测试任务上下文"""

    def test_task_context_creation(self):
        """测试任务上下文创建"""
        ctx = TaskContext(
            task_id="task-123",
            task_title="Test Task",
            task_description="Test Description",
        )

        assert ctx.task_id == "task-123"
        assert ctx.task_title == "Test Task"
        assert ctx.task_description == "Test Description"
        assert ctx.upstream_outputs == []
        assert ctx.metadata == {}

    def test_task_context_with_upstream_outputs(self):
        """测试带上游输出的任务上下文"""
        ctx = TaskContext(
            task_id="task-123",
            task_title="Test",
            task_description="Test",
            upstream_outputs=[{"agent": "upstream", "result": "data"}],
        )

        assert len(ctx.upstream_outputs) == 1

    def test_task_context_with_metadata(self):
        """测试带元数据的任务上下文"""
        ctx = TaskContext(
            task_id="task-123",
            task_title="Test",
            task_description="Test",
            metadata={"project_id": "proj-123"},
        )

        assert ctx.metadata["project_id"] == "proj-123"


class TestTaskResult:
    """测试任务结果"""

    def test_success_result(self):
        """测试成功结果"""
        result = TaskResult(success=True, output={"data": "value"})

        assert result.success is True
        assert result.output == {"data": "value"}
        assert result.error is None

    def test_failure_result(self):
        """测试失败结果"""
        result = TaskResult(
            success=False,
            error="Something went wrong",
        )

        assert result.success is False
        assert result.error == "Something went wrong"
        assert result.output is None

    def test_result_with_metadata(self):
        """测试带元数据的结果"""
        result = TaskResult(
            success=True,
            output={},
            metadata={"type": "test"},
        )

        assert result.metadata["type"] == "test"


class TestAgentLifecycleManager:
    """测试 Agent 生命周期管理器"""

    @pytest.fixture
    def manager(self, clean_lifecycle_manager):
        """创建生命周期管理器"""
        return get_lifecycle_manager()

    def test_register_agent(self, manager):
        """测试注册 Agent"""
        agent = MockAgent("agent-1")
        manager.register(agent)

        assert manager.get("agent-1") is agent

    def test_unregister_agent(self, manager):
        """测试注销 Agent"""
        agent = MockAgent("agent-1")
        manager.register(agent)
        manager.unregister("agent-1")

        assert manager.get("agent-1") is None

    def test_initialize_agent(self, manager):
        """测试初始化 Agent"""
        agent = MockAgent("agent-1")
        manager.register(agent)

        assert manager.initialize("agent-1") is True
        assert manager.is_initialized("agent-1") is True

    def test_shutdown_agent(self, manager):
        """测试关闭 Agent"""
        agent = MockAgent("agent-1")
        manager.register(agent)
        manager.initialize("agent-1")

        assert manager.shutdown("agent-1") is True
        assert manager.is_initialized("agent-1") is False

    def test_get_all_agents(self, manager):
        """测试获取所有 Agent"""
        manager.register(MockAgent("agent-1"))
        manager.register(MockAgent("agent-2"))

        agents = manager.get_all()
        assert len(agents) == 2

    def test_get_active_agents(self, manager):
        """测试获取活跃 Agent"""
        agent1 = MockAgent("agent-1")
        agent2 = MockAgent("agent-2")

        manager.register(agent1)
        manager.register(agent2)

        # 模拟 agent2 忙碌
        agent2.state = AgentState.WORKING

        active = manager.get_active_agents()
        assert len(active) == 1
        assert active[0].agent_id == "agent-1"

    def test_get_agents_by_role(self, manager):
        """测试按角色获取 Agent"""
        agent1 = MockAgent("agent-1")
        agent1.role = "manager"

        agent2 = MockAgent("agent-2")
        agent2.role = "coder"

        manager.register(agent1)
        manager.register(agent2)

        managers = manager.get_agents_by_role("manager")
        assert len(managers) == 1
        assert managers[0].agent_id == "agent-1"

    def test_get_agents_by_capability(self, manager):
        """测试按能力获取 Agent"""
        agent1 = MockAgent("agent-1")
        agent1.capabilities = [AgentCapability.PLANNING]

        agent2 = MockAgent("agent-2")
        agent2.capabilities = [AgentCapability.CODE_GENERATION]

        manager.register(agent1)
        manager.register(agent2)

        planners = manager.get_agents_by_capability(AgentCapability.PLANNING)
        assert len(planners) == 1
        assert planners[0].agent_id == "agent-1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
