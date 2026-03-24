"""
Milestone - 里程碑模型
"""
from sqlalchemy import Column, String, Text, ForeignKey, Enum, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from typing import List, TYPE_CHECKING

from .base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from .project import Project
    from .task import Task


class MilestoneStatus(str, enum.Enum):
    """里程碑状态"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class Milestone(Base, UUIDMixin, TimestampMixin):
    """
    里程碑模型
    
    字段:
    - project_id: 所属项目 ID
    - name: 里程碑名称
    - description: 描述
    - order: 排序
    - status: 状态
    - progress: 进度 (0-100)
    """
    __tablename__ = "milestones"
    
    # 外键
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 基础信息
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # 排序
    order = Column(Integer, nullable=False, default=0)
    
    # 状态和进度
    status = Column(Enum(MilestoneStatus), nullable=False, default=MilestoneStatus.PENDING, index=True)
    progress = Column(Integer, nullable=False, default=0)
    
    # 关系
    project: Mapped["Project"] = relationship("Project", back_populates="milestones")
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="milestone",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    
    # 索引
    __table_args__ = (
        Index("ix_milestones_project_order", "project_id", "order"),
    )
    
    def __repr__(self) -> str:
        return f"<Milestone(id={self.id}, name={self.name}, progress={self.progress})>"
