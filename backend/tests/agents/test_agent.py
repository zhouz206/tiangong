"""
Agent 和 Skill 测试
"""
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.agents.agent import Agent, TaskContext, TaskResult
from app.agents.skill import Skill, SkillContext, SkillResult


# 测试数据库
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)


# 测试用技能
class TestSkill(Skill):
    """测试技能"""
    
    @property
    def name(self) -> str:
        return "test_skill"
    
    async def execute(self, context: SkillContext) -> SkillResult:
        return SkillResult(
            success=True,
            output={"message": "Skill executed successfully"}
        )


# 测试用 Agent
class TestAgentImpl(Agent):
    """测试 Agent 实现"""
    
    @property
    def role(self) -> str:
        return "test_agent"
    
    async def _default_execute(self, context: TaskContext) -> TaskResult:
        return TaskResult(success=True, output={"message": "Default execute"})


@pytest.fixture
def db_session():
    """创建数据库会话"""
    session = SessionLocal()
    yield session
    session.close()


class TestSkillClass:
    """Skill 测试"""
    
    def test_skill_name(self):
        """测试技能名称"""
        skill = TestSkill()
        assert skill.name == "test_skill"
    
    @pytest.mark.asyncio
    async def test_skill_execute(self):
        """测试技能执行"""
        skill = TestSkill()
        context = SkillContext(task_id="task_1")
        result = await skill.execute(context)
        
        assert result.success is True
        assert result.output["message"] == "Skill executed successfully"


class TestAgentClass:
    """Agent 测试"""
    
    def test_agent_role(self, db_session):
        """测试 Agent 角色"""
        agent = TestAgentImpl(db_session)
        assert agent.role == "test_agent"
    
    def test_agent_load_skill(self, db_session):
        """测试 Agent 装备技能"""
        agent = TestAgentImpl(db_session)
        skill = TestSkill()
        
        agent.load_skill(skill)
        
        assert agent.has_skill("test_skill")
        assert "test_skill" in agent.get_skills()
    
    def test_agent_unload_skill(self, db_session):
        """测试 Agent 卸载技能"""
        agent = TestAgentImpl(db_session)
        skill = TestSkill()
        
        agent.load_skill(skill)
        result = agent.unload_skill("test_skill")
        
        assert result is True
        assert not agent.has_skill("test_skill")
    
    @pytest.mark.asyncio
    async def test_agent_execute_skill(self, db_session):
        """测试 Agent 执行技能"""
        agent = TestAgentImpl(db_session)
        skill = TestSkill()
        agent.load_skill(skill)
        
        context = SkillContext(task_id="task_1")
        result = await agent.execute_skill("test_skill", context)
        
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_agent_execute_task_with_skill(self, db_session):
        """测试 Agent 执行任务（使用技能）"""
        agent = TestAgentImpl(db_session)
        skill = TestSkill()
        agent.load_skill(skill)
        
        context = TaskContext(
            task_id="task_1",
            metadata={"required_skill": "test_skill"}
        )
        result = await agent.execute_task(context)
        
        assert result.success is True
        assert result.output["message"] == "Skill executed successfully"
    
    @pytest.mark.asyncio
    async def test_agent_execute_task_default(self, db_session):
        """测试 Agent 执行任务（默认逻辑）"""
        agent = TestAgentImpl(db_session)
        
        context = TaskContext(task_id="task_1")
        result = await agent.execute_task(context)
        
        assert result.success is True
        assert result.output["message"] == "Default execute"
