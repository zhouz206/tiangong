"""
Workflow — 工作流引擎
"""
from typing import Dict, Optional, TYPE_CHECKING
from datetime import datetime

from .phase import ProjectPhase, PhaseTransition

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from app.models.project import Project


class Workflow:
    """
    工作流
    
    封装单个项目的工作流状态和管理
    """
    
    def __init__(self, project: "Project"):
        """
        初始化工作流
        
        Args:
            project: 项目实例
        """
        self.project = project
        self.created_at = datetime.now()
    
    @property
    def current_phase(self) -> ProjectPhase:
        """获取当前阶段"""
        return self.project.phase
    
    @property
    def status(self):
        """获取项目状态"""
        return self.project.status
    
    def can_transition_to(self, new_phase: ProjectPhase) -> bool:
        """
        检查是否可以转换到新阶段
        
        Args:
            new_phase: 目标阶段
            
        Returns:
            bool: 是否可以转换
        """
        return PhaseTransition.can_transition(self.current_phase, new_phase)
    
    def transition_to(self, new_phase: ProjectPhase) -> bool:
        """
        转换到新阶段
        
        Args:
            new_phase: 目标阶段
            
        Returns:
            bool: 是否成功转换
        """
        if not self.can_transition_to(new_phase):
            return False
        
        self.project.phase = new_phase
        
        # 如果转换到完成阶段，更新项目状态
        if new_phase == ProjectPhase.COMPLETED:
            from app.models.project import ProjectStatus
            self.project.status = ProjectStatus.COMPLETED
            self.project.completed_at = datetime.now()
        
        return True
    
    def __repr__(self) -> str:
        return f"<Workflow(project={self.project.name}, phase={self.current_phase.value})>"


class WorkflowEngine:
    """
    工作流引擎
    
    管理多个项目的工作流实例
    """
    
    def __init__(self, db: "Session"):
        """
        初始化工作流引擎
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self._workflows: Dict[str, Workflow] = {}
    
    def get_or_create_workflow(self, project: "Project") -> Workflow:
        """
        获取或创建工作流实例
        
        Args:
            project: 项目实例
            
        Returns:
            Workflow: 工作流实例
        """
        if project.id not in self._workflows:
            self._workflows[project.id] = Workflow(project)
        
        return self._workflows[project.id]
    
    def get_workflow(self, project_id: str) -> Optional[Workflow]:
        """
        获取工作流实例
        
        Args:
            project_id: 项目 ID
            
        Returns:
            Optional[Workflow]: 工作流实例或 None
        """
        return self._workflows.get(project_id)
    
    def remove_workflow(self, project_id: str) -> bool:
        """
        移除工作流实例
        
        Args:
            project_id: 项目 ID
            
        Returns:
            bool: 是否成功移除
        """
        if project_id in self._workflows:
            del self._workflows[project_id]
            return True
        return False
    
    def transition_project_phase(self, project_id: str, new_phase: ProjectPhase) -> bool:
        """
        转换项目阶段
        
        Args:
            project_id: 项目 ID
            new_phase: 目标阶段
            
        Returns:
            bool: 是否成功转换
        """
        from app.models.project import Project
        
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return False
        
        workflow = self.get_or_create_workflow(project)
        success = workflow.transition_to(new_phase)
        
        if success:
            self.db.commit()
        
        return success
    
    def __repr__(self) -> str:
        return f"<WorkflowEngine(workflows={len(self._workflows)})>"
