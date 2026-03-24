"""
模型测试
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.project import Project, ProjectStatus, ProjectPhase
from app.models.milestone import Milestone, MilestoneStatus
from app.models.task import Task, TaskStatus, TaskPriority

# 测试数据库
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def session():
    """创建测试会话"""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


class TestProject:
    """Project 模型测试"""
    
    def test_create_project(self, session):
        """测试创建项目"""
        project = Project(name="测试项目", description="测试描述")
        session.add(project)
        session.commit()
        
        assert project.id is not None
        assert project.name == "测试项目"
        assert project.status == ProjectStatus.ACTIVE
        assert project.phase == ProjectPhase.PLANNING
        assert project.progress == 0
    
    def test_project_phase_transition(self, session):
        """测试项目阶段转换"""
        project = Project(name="测试项目")
        session.add(project)
        session.commit()
        
        # PLANNING → EXECUTING (合法)
        assert project.can_transition_to(ProjectPhase.EXECUTING)
        
        # PLANNING → COMPLETED (非法)
        assert not project.can_transition_to(ProjectPhase.COMPLETED)
    
    def test_project_milestone_relationship(self, session):
        """测试项目与里程碑关系"""
        project = Project(name="测试项目")
        milestone = Milestone(name="M1", order=1)
        project.milestones.append(milestone)
        session.add(project)
        session.commit()
        
        assert len(project.milestones) == 1
        assert project.milestones[0].name == "M1"


class TestMilestone:
    """Milestone 模型测试"""
    
    def test_create_milestone(self, session):
        """测试创建里程碑"""
        project = Project(name="测试项目")
        milestone = Milestone(name="M1", order=1)
        project.milestones.append(milestone)
        session.add(project)
        session.commit()
        
        assert milestone.id is not None
        assert milestone.name == "M1"
        assert milestone.order == 1
        assert milestone.status == MilestoneStatus.PENDING
        assert milestone.progress == 0
    
    def test_milestone_task_relationship(self, session):
        """测试里程碑与任务关系"""
        project = Project(name="测试项目")
        milestone = Milestone(name="M1", order=1)
        task = Task(title="任务 1")
        milestone.tasks.append(task)
        session.add(project)
        session.commit()
        
        assert len(milestone.tasks) == 1
        assert milestone.tasks[0].title == "任务 1"


class TestTask:
    """Task 模型测试"""
    
    def test_create_task(self, session):
        """测试创建任务"""
        project = Project(name="测试项目")
        session.add(project)
        session.commit()
        
        milestone = Milestone(name="M1", order=1, project_id=project.id)
        session.add(milestone)
        session.commit()
        
        task = Task(title="任务 1", priority=TaskPriority.HIGH, milestone_id=milestone.id)
        session.add(task)
        session.commit()
        
        assert task.id is not None
        assert task.title == "任务 1"
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.PENDING
    
    def test_task_can_start(self, session):
        """测试任务可以开始（无依赖）"""
        project = Project(name="测试项目")
        session.add(project)
        session.commit()
        
        milestone = Milestone(name="M1", order=1, project_id=project.id)
        session.add(milestone)
        session.commit()
        
        task = Task(title="任务 1", milestone_id=milestone.id)
        session.add(task)
        session.commit()
        
        assert task.status == TaskStatus.PENDING
