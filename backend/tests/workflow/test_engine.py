"""
工作流引擎测试
"""
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.agents.agent import Agent, TaskContext, TaskResult
from app.agents.skill import Skill, SkillContext, SkillResult
from app.workflow.engine import WorkflowEngine
from app.workflow.quality_gate import QualityGate


# 测试数据库
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)


# 测试用 Agent
class TestAgent(Agent):
    @property
    def role(self) -> str:
        return "test_agent"
    
    async def _default_execute(self, context: TaskContext) -> TaskResult:
        return TaskResult(success=True, output={"message": "Executed"})


# 测试用 Skill
class TestSkill(Skill):
    @property
    def name(self) -> str:
        return "test_skill"
    
    async def execute(self, context: SkillContext) -> SkillResult:
        return SkillResult(success=True, output={"result": "Skill executed"})


@pytest.fixture
def db_session():
    """创建数据库会话"""
    session = SessionLocal()
    yield session
    session.close()


class TestQualityGate:
    """QualityGate 测试"""
    
    def test_check_review_score_pass(self):
        """测试审查评分通过"""
        gate = QualityGate()
        result = {"overall_score": 8.5}
        
        assert gate.check_review_score(result) is True
    
    def test_check_review_score_fail(self):
        """测试审查评分失败"""
        gate = QualityGate()
        result = {"overall_score": 6.0}
        
        assert gate.check_review_score(result) is False
    
    def test_check_test_coverage_pass(self):
        """测试测试覆盖率通过"""
        gate = QualityGate()
        result = {"coverage": 0.85}  # 85%
        
        assert gate.check_test_coverage(result) is True
    
    def test_check_test_coverage_fail(self):
        """测试测试覆盖率失败"""
        gate = QualityGate()
        result = {"coverage": 50}
        
        assert gate.check_test_coverage(result) is False
    
    def test_check_core_flows_pass(self):
        """测试核心流程通过"""
        gate = QualityGate()
        result = {"core_flows_passed": True}
        
        assert gate.check_core_flows(result) is True
    
    def test_check_core_flows_fail(self):
        """测试核心流程失败"""
        gate = QualityGate()
        result = {"core_flows_passed": False}
        
        assert gate.check_core_flows(result) is False
    
    def test_check_all(self):
        """测试全部检查"""
        gate = QualityGate()
        results = {
            "review": {"overall_score": 9.0},
            "test": {"coverage": 90},
            "qa": {"core_flows_passed": True}
        }
        
        checks = gate.check_all(results)
        
        assert checks["review_score"] is True
        assert checks["test_coverage"] is True
        assert checks["core_flows"] is True
        assert gate.all_passed(checks) is True
    
    def test_all_passed_partial(self):
        """测试部分通过"""
        gate = QualityGate()
        checks = {
            "review_score": True,
            "test_coverage": False,
            "core_flows": True
        }
        
        assert gate.all_passed(checks) is False


class TestWorkflowEngine:
    """WorkflowEngine 测试"""
    
    def test_register_agent(self, db_session):
        """测试注册 Agent"""
        engine = WorkflowEngine(db_session)
        agent = TestAgent(db_session)
        
        engine.register_agent("test_agent", agent)
        
        assert "test_agent" in engine.agents
    
    @pytest.mark.asyncio
    async def test_run_workflow_partial(self, db_session):
        """测试运行部分工作流"""
        engine = WorkflowEngine(db_session)
        
        # 不注册 Agent，测试跳过逻辑
        result = await engine.run_workflow("测试需求")
        
        # 应该有部分步骤被跳过
        assert "office_hours" in result.get("partial_results", {})
    
    def test_create_success_result(self, db_session):
        """测试创建成功结果"""
        engine = WorkflowEngine(db_session)
        result = engine._create_success_result()
        
        assert result["success"] is True
        assert "timestamp" in result
    
    def test_create_error_result(self, db_session):
        """测试创建错误结果"""
        engine = WorkflowEngine(db_session)
        result = engine._create_error_result("测试错误")
        
        assert result["success"] is False
        assert result["error"] == "测试错误"
