"""
工作流测试
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.project import Project, ProjectStatus, ProjectPhase
from app.workflow.workflow import Workflow, WorkflowEngine
from app.workflow.phase import ProjectPhase as Phase, PhaseTransition


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


class TestPhaseTransition:
    """阶段转换测试"""
    
    def test_planning_to_executing(self):
        """测试 PLANNING → EXECUTING"""
        assert PhaseTransition.can_transition(Phase.PLANNING, Phase.EXECUTING)
    
    def test_planning_to_completed(self):
        """测试 PLANNING → COMPLETED (非法)"""
        assert not PhaseTransition.can_transition(Phase.PLANNING, Phase.COMPLETED)
    
    def test_completed_is_final(self):
        """测试 COMPLETED 是终态"""
        transitions = PhaseTransition.get_valid_transitions(Phase.COMPLETED)
        assert transitions == {Phase.COMPLETED}
    
    def test_get_valid_transitions(self):
        """测试获取合法转换列表"""
        transitions = PhaseTransition.get_valid_transitions(Phase.PLANNING)
        assert Phase.EXECUTING in transitions
        assert Phase.PLANNING in transitions
        assert Phase.COMPLETED not in transitions


class TestWorkflow:
    """工作流测试"""
    
    def test_workflow_creation(self, db_session):
        """测试工作流创建"""
        project = Project(name="测试项目")
        db_session.add(project)
        db_session.commit()
        
        workflow = Workflow(project)
        
        assert workflow.current_phase == Phase.PLANNING
        assert workflow.project.name == "测试项目"
    
    def test_workflow_transition(self, db_session):
        """测试工作流阶段转换"""
        project = Project(name="测试项目")
        db_session.add(project)
        db_session.commit()
        
        workflow = Workflow(project)
        
        # PLANNING → EXECUTING
        assert workflow.can_transition_to(Phase.EXECUTING)
        success = workflow.transition_to(Phase.EXECUTING)
        assert success is True
        assert workflow.current_phase == Phase.EXECUTING
    
    def test_workflow_invalid_transition(self, db_session):
        """测试非法阶段转换"""
        project = Project(name="测试项目")
        db_session.add(project)
        db_session.commit()
        
        workflow = Workflow(project)
        
        # PLANNING → COMPLETED (非法)
        assert not workflow.can_transition_to(Phase.COMPLETED)
        success = workflow.transition_to(Phase.COMPLETED)
        assert success is False
        assert workflow.current_phase == Phase.PLANNING
    
    def test_workflow_complete(self, db_session):
        """测试完成项目"""
        project = Project(name="测试项目", phase=Phase.REVIEWING)
        db_session.add(project)
        db_session.commit()
        
        workflow = Workflow(project)
        success = workflow.transition_to(Phase.COMPLETED)
        
        assert success is True
        assert workflow.current_phase == Phase.COMPLETED
        assert project.completed_at is not None


class TestWorkflowEngine:
    """工作流引擎测试"""
    
    def test_get_or_create_workflow(self, db_session):
        """测试获取或创建工作流"""
        engine = WorkflowEngine(db_session)
        
        project = Project(name="测试项目")
        db_session.add(project)
        db_session.commit()
        
        workflow1 = engine.get_or_create_workflow(project)
        workflow2 = engine.get_or_create_workflow(project)
        
        assert workflow1 is workflow2
    
    def test_transition_project_phase(self, db_session):
        """测试转换项目阶段"""
        engine = WorkflowEngine(db_session)
        
        project = Project(name="测试项目")
        db_session.add(project)
        db_session.commit()
        
        success = engine.transition_project_phase(project.id, Phase.EXECUTING)
        
        assert success is True
        
        # 从数据库重新查询
        project_from_db = db_session.query(Project).filter(Project.id == project.id).first()
        assert project_from_db.phase == Phase.EXECUTING
