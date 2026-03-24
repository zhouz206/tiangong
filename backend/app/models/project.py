"""
Project - 项目模型
"""
from sqlalchemy import Column, String, Text, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from typing import List, TYPE_CHECKING

from .base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from .milestone import Milestone


class ProjectStatus(str, enum.Enum):
    """项目状态"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectPhase(str, enum.Enum):
    """项目阶段"""
    PLANNING = "planning"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"


class Project(Base, UUIDMixin, TimestampMixin):
    """
    项目模型
    
    字段:
    - name: 项目名称
    - description: 项目描述
    - status: 项目状态
    - phase: 项目阶段
    - progress: 进度 (0-100)
    """
    __tablename__ = "projects"
    
    # 基础信息
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # 状态和阶段
    status = Column(Enum(ProjectStatus), nullable=False, default=ProjectStatus.ACTIVE, index=True)
    phase = Column(Enum(ProjectPhase), nullable=False, default=ProjectPhase.PLANNING, index=True)
    
    # 进度
    progress = Column(Integer, nullable=False, default=0)
    
    # 关系
    milestones: Mapped[List["Milestone"]] = relationship(
        "Milestone",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, phase={self.phase.value})>"
    
    def can_transition_to(self, new_phase: ProjectPhase) -> bool:
        """检查阶段转换是否合法"""
        valid_transitions = {
            ProjectPhase.PLANNING: {ProjectPhase.EXECUTING, ProjectPhase.PLANNING},
            ProjectPhase.EXECUTING: {ProjectPhase.REVIEWING, ProjectPhase.EXECUTING, ProjectPhase.PLANNING},
            ProjectPhase.REVIEWING: {ProjectPhase.COMPLETED, ProjectPhase.EXECUTING, ProjectPhase.REVIEWING},
            ProjectPhase.COMPLETED: {ProjectPhase.COMPLETED},
        }
        return new_phase in valid_transitions.get(self.phase, set())
