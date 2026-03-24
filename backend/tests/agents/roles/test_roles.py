"""
Agent 角色测试
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.agents.roles import (
    ProjectManagerAgent,
    ResearcherAgent,
    CoderAgent,
    DesignerAgent,
    WriterAgent,
    ReviewerAgent,
    DataAnalystAgent,
    KnowledgeManagerAgent,
)
from app.agents.agent import TaskContext


# 测试数据库
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def db_session():
    """创建数据库会话"""
    session = SessionLocal()
    yield session
    session.close()


class TestAgentRoles:
    """Agent 角色测试"""
    
    def test_project_manager_agent(self, db_session):
        """测试项目经理 Agent"""
        agent = ProjectManagerAgent(db_session)
        assert agent.role == "project_manager"
    
    def test_researcher_agent(self, db_session):
        """测试研究员 Agent"""
        agent = ResearcherAgent(db_session)
        assert agent.role == "researcher"
    
    def test_coder_agent(self, db_session):
        """测试程序员 Agent"""
        agent = CoderAgent(db_session)
        assert agent.role == "coder"
    
    def test_designer_agent(self, db_session):
        """测试设计师 Agent"""
        agent = DesignerAgent(db_session)
        assert agent.role == "designer"
    
    def test_writer_agent(self, db_session):
        """测试文案 Agent"""
        agent = WriterAgent(db_session)
        assert agent.role == "writer"
    
    def test_reviewer_agent(self, db_session):
        """测试审核员 Agent"""
        agent = ReviewerAgent(db_session)
        assert agent.role == "reviewer"
    
    def test_data_analyst_agent(self, db_session):
        """测试数据分析师 Agent"""
        agent = DataAnalystAgent(db_session)
        assert agent.role == "data_analyst"
    
    def test_knowledge_manager_agent(self, db_session):
        """测试知识管理员 Agent"""
        agent = KnowledgeManagerAgent(db_session)
        assert agent.role == "knowledge_manager"
    
    @pytest.mark.asyncio
    async def test_project_manager_execute(self, db_session):
        """测试项目经理执行任务"""
        agent = ProjectManagerAgent(db_session)
        context = TaskContext(task_id="task_1")
        result = await agent.execute_task(context)
        
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_coder_execute(self, db_session):
        """测试程序员执行任务"""
        agent = CoderAgent(db_session)
        context = TaskContext(task_id="task_1")
        result = await agent.execute_task(context)
        
        assert result.success is True
        assert result.output["type"] == "code"
