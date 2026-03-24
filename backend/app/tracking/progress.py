"""
ProgressService — 进度计算服务
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.milestone import Milestone, MilestoneStatus
from app.models.task import Task, TaskStatus
from app.models.project import Project


class ProgressService:
    """
    进度计算服务
    
    功能:
    - 更新里程碑进度
    - 更新项目进度
    - 进度自动计算
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def update_milestone_progress(self, milestone_id: str) -> int:
        """
        更新里程碑进度
        
        Args:
            milestone_id: 里程碑 ID
            
        Returns:
            int: 新的进度值 (0-100)
        """
        milestone = self.db.query(Milestone).filter(Milestone.id == milestone_id).first()
        if not milestone:
            return 0
        
        tasks = self.db.query(Task).filter(Task.milestone_id == milestone_id).all()
        if not tasks:
            milestone.progress = 0
            milestone.status = MilestoneStatus.PENDING
            self.db.commit()
            return 0
        
        # 计算进度（按任务数量平均）
        completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]
        progress = int(len(completed_tasks) / len(tasks) * 100)
        
        milestone.progress = progress
        
        # 更新状态
        if progress == 100:
            milestone.status = MilestoneStatus.COMPLETED
        elif progress > 0:
            milestone.status = MilestoneStatus.ACTIVE
        else:
            milestone.status = MilestoneStatus.PENDING
        
        self.db.commit()
        
        # 触发项目进度更新
        self.update_project_progress(milestone.project_id)
        
        return progress
    
    def update_project_progress(self, project_id: str) -> int:
        """
        更新项目进度
        
        Args:
            project_id: 项目 ID
            
        Returns:
            int: 新的进度值 (0-100)
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return 0
        
        milestones = self.db.query(Milestone).filter(Milestone.project_id == project_id).all()
        if not milestones:
            project.progress = 0
            self.db.commit()
            return 0
        
        # 按里程碑进度平均计算
        total_progress = sum(m.progress for m in milestones)
        project.progress = int(total_progress / len(milestones))
        
        self.db.commit()
        
        return project.progress
    
    def get_project_status(self, project_id: str) -> dict:
        """
        获取项目状态
        
        Args:
            project_id: 项目 ID
            
        Returns:
            dict: 项目状态信息
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {}
        
        milestones = self.db.query(Milestone).filter(Milestone.project_id == project_id).all()
        
        return {
            "project": {
                "id": project.id,
                "name": project.name,
                "progress": project.progress,
                "phase": project.phase.value,
                "status": project.status.value
            },
            "milestones": [
                {
                    "id": m.id,
                    "name": m.name,
                    "progress": m.progress,
                    "status": m.status.value
                }
                for m in milestones
            ]
        }
