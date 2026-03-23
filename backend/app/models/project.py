"""
Project - 项目模型
"""
from sqlalchemy import Column, String, Text, ForeignKey, Index, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
import enum
from sqlalchemy.types import JSON

from app.core.database import Base
from .base import UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from .workspace import Workspace
    from .user import User
    from .task import Task
    from .agent import Agent
    from .knowledge import KnowledgeDocument
    from .audit import AuditLog
    from .agent_message import AgentMessage


class ProjectStatus(str, enum.Enum):
    """项目状态枚举"""
    ACTIVE = "active"  # 进行中
    PAUSED = "paused"  # 已暂停
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class ProjectPhase(str, enum.Enum):
    """项目阶段枚举 - 四阶段工作流"""
    PLANNING = "planning"  # 规划阶段
    EXECUTING = "executing"  # 执行阶段
    REVIEWING = "reviewing"  # 审查阶段
    COMPLETED = "completed"  # 完成阶段


class Project(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    项目模型 - 项目生命周期管理，四阶段工作流
    
    字段说明:
    - workspace_id: 所属工作空间 ID
    - name: 项目名称
    - description: 项目描述
    - template_id: 模板项目 ID (自引用)
    - status: 项目状态 (active/paused/completed/cancelled)
    - current_phase: 当前阶段 (planning/executing/reviewing/completed)
    - owner_id: 项目负责人 ID
    - context: JSON 项目上下文 (Agent 共享)
    - completed_at: 完成时间
    """
    __tablename__ = "projects"
    
    # 外键
    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    template_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # 基础信息
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # 状态和阶段
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus),
        nullable=False,
        default=ProjectStatus.ACTIVE,
        index=True,
    )
    current_phase: Mapped[ProjectPhase] = mapped_column(
        Enum(ProjectPhase),
        nullable=False,
        default=ProjectPhase.PLANNING,
        index=True,
    )
    
    # 时间
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # 项目上下文 (Agent 共享信息)
    context: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
    )
    
    # 关系
    workspace: Mapped["Workspace"] = relationship(
        back_populates="projects",
    )
    owner: Mapped[Optional["User"]] = relationship(
        back_populates="projects",
        foreign_keys=[owner_id],
    )
    template: Mapped[Optional["Project"]] = relationship(
        remote_side="Project.id",
        foreign_keys=[template_id],
    )
    tasks: Mapped[List["Task"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    agents: Mapped[List["Agent"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    knowledge_documents: Mapped[List["KnowledgeDocument"]] = relationship(
        back_populates="project",
    )
    messages: Mapped[List["AgentMessage"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    
    # 索引
    __table_args__ = (
        Index("ix_projects_workspace_status", "workspace_id", "status"),
        Index("ix_projects_workspace_phase", "workspace_id", "current_phase"),
        Index("ix_projects_owner_status", "owner_id", "status"),
    )
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, phase={self.current_phase.value})>"
    
    def can_transition_to(self, new_phase: ProjectPhase) -> bool:
        """检查阶段转换是否合法"""
        valid_transitions = {
            ProjectPhase.PLANNING: {ProjectPhase.EXECUTING, ProjectPhase.PLANNING},
            ProjectPhase.EXECUTING: {ProjectPhase.REVIEWING, ProjectPhase.EXECUTING, ProjectPhase.PLANNING},
            ProjectPhase.REVIEWING: {ProjectPhase.COMPLETED, ProjectPhase.EXECUTING, ProjectPhase.REVIEWING},
            ProjectPhase.COMPLETED: {ProjectPhase.COMPLETED},  # 完成阶段不可逆
        }
        return new_phase in valid_transitions.get(self.current_phase, set())
