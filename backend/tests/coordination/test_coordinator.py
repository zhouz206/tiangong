"""
协调器测试
"""
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.agents.agent import Agent, TaskContext, TaskResult
from app.agents.skill import Skill, SkillContext, SkillResult
from app.coordination.message import MessageBus, MessageType, Message
from app.coordination.coordinator import Coordinator, TaskScheduler


# 测试数据库
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)


# 测试用 Agent
class TestAgentImpl(Agent):
    @property
    def role(self) -> str:
        return "test_agent"
    
    async def _default_execute(self, context: TaskContext) -> TaskResult:
        return TaskResult(success=True, output={"message": "Executed"})


@pytest.fixture
def db_session():
    """创建数据库会话"""
    session = SessionLocal()
    yield session
    session.close()


class TestMessageBus:
    """MessageBus 测试"""
    
    def test_subscribe_and_publish(self):
        """测试订阅和发布"""
        bus = MessageBus()
        received = []
        
        def callback(msg):
            received.append(msg)
        
        bus.subscribe("project_1", callback)
        
        msg = Message(
            type=MessageType.STATUS_UPDATE,
            channel="project_1",
            sender="agent_1",
            content={"status": "running"}
        )
        
        asyncio.run(bus.publish(msg, async_mode=False))
        
        assert len(received) == 1
        assert received[0].type == MessageType.STATUS_UPDATE
    
    def test_unsubscribe(self):
        """测试取消订阅"""
        bus = MessageBus()
        received = []
        
        def callback(msg):
            received.append(msg)
        
        bus.subscribe("project_1", callback)
        bus.unsubscribe("project_1", callback)
        
        msg = Message(
            type=MessageType.STATUS_UPDATE,
            channel="project_1",
            sender="agent_1",
            content={}
        )
        
        asyncio.run(bus.publish(msg, async_mode=False))
        
        assert len(received) == 0
    
    def test_message_history(self):
        """测试消息历史"""
        bus = MessageBus()
        
        for i in range(5):
            msg = Message(
                type=MessageType.STATUS_UPDATE,
                channel="project_1",
                sender="agent_1",
                content={"index": i}
            )
            asyncio.run(bus.publish(msg, async_mode=False))
        
        history = bus.get_history("project_1")
        assert len(history) == 5
    
    def test_get_history_limit(self):
        """测试历史消息限制"""
        bus = MessageBus()
        
        for i in range(10):
            msg = Message(
                type=MessageType.STATUS_UPDATE,
                channel="project_1",
                sender="agent_1",
                content={"index": i}
            )
            asyncio.run(bus.publish(msg, async_mode=False))
        
        history = bus.get_history("project_1", limit=5)
        assert len(history) == 5
    
    def test_clear_history(self):
        """测试清空历史"""
        bus = MessageBus()
        
        msg = Message(
            type=MessageType.STATUS_UPDATE,
            channel="project_1",
            sender="agent_1",
            content={}
        )
        asyncio.run(bus.publish(msg, async_mode=False))
        
        bus.clear_history("project_1")
        history = bus.get_history("project_1")
        assert len(history) == 0


class TestCoordinator:
    """Coordinator 测试"""
    
    def test_register_agent(self, db_session):
        """测试注册 Agent"""
        coordinator = Coordinator(db_session)
        agent = TestAgentImpl(db_session)
        
        coordinator.register_agent("agent_1", agent)
        
        assert coordinator.get_agent("agent_1") is agent
    
    def test_unregister_agent(self, db_session):
        """测试注销 Agent"""
        coordinator = Coordinator(db_session)
        agent = TestAgentImpl(db_session)
        
        coordinator.register_agent("agent_1", agent)
        result = coordinator.unregister_agent("agent_1")
        
        assert result is True
        assert coordinator.get_agent("agent_1") is None
    
    def test_get_agents_by_role(self, db_session):
        """测试按角色获取 Agent"""
        coordinator = Coordinator(db_session)
        agent1 = TestAgentImpl(db_session)
        agent2 = TestAgentImpl(db_session)
        
        coordinator.register_agent("agent_1", agent1)
        coordinator.register_agent("agent_2", agent2)
        
        agents = coordinator.get_agents_by_role("test_agent")
        assert len(agents) == 2
    
    def test_assign_task(self, db_session):
        """测试分配任务"""
        coordinator = Coordinator(db_session)
        agent = TestAgentImpl(db_session)
        
        coordinator.register_agent("agent_1", agent)
        result = coordinator.assign_task("agent_1", {"task_id": "task_1"})
        
        assert result is True


class TestTaskScheduler:
    """TaskScheduler 测试"""
    
    def test_add_and_get_task(self):
        """测试添加和获取任务"""
        scheduler = TaskScheduler()
        
        scheduler.add_task({"task_id": "task_1"})
        scheduler.add_task({"task_id": "task_2"})
        
        task1 = scheduler.get_next_task()
        task2 = scheduler.get_next_task()
        task3 = scheduler.get_next_task()
        
        assert task1["task_id"] == "task_1"
        assert task2["task_id"] == "task_2"
        assert task3 is None
