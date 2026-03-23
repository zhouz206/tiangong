"""
Task - 任务模型
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
    from .project import Project
    from .agent import Agent
    from .knowledge import KnowledgeDocument
    from .audit import AuditLog
    from .agent_message import AgentMessage


class TaskStatus(str, enum.Enum):
    """任务状态枚举"""
    PENDING = "pending"  # 待处理
    IN_PROGRESS = "in_progress"  # 进行中
    BLOCKED = "blocked"  # 已阻塞
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class TaskPriority(str, enum.Enum):
    """任务优先级枚举"""
    LOW = "low"  # 低
    MEDIUM = "medium"  # 中
    HIGH = "high"  # 高
    URGENT = "urgent"  # 紧急


class Task(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    任务模型 - 项目内具体工作单元
    
    字段说明:
    - project_id: 所属项目 ID
    - title: 任务标题
    - description: 任务描述
    - status: 任务状态
    - priority: 优先级
    - assignee_id: 执行 Agent ID
    - upstream_task_id: 上游任务 ID (依赖关系)
    - due_date: 截止日期
    - started_at: 开始时间
    - completed_at: 完成时间
    - output: JSON 任务产出物元数据
    - metadata: JSON 扩展信息
    """
    __tablename__ = "tasks"
    
    # 外键
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assignee_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("agents.id", ondelete="SET NULL", use_alter=True),
        nullable=True,
        index=True,
    )
    upstream_task_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # 基础信息
    title: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # 状态和优先级
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus),
        nullable=False,
        default=TaskStatus.PENDING,
        index=True,
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority),
        nullable=False,
        default=TaskPriority.MEDIUM,
        index=True,
    )
    
    # 时间
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # 产出物和元数据
    output: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
    )
    extra_data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
    )
    
    # 关系
    project: Mapped["Project"] = relationship(
        back_populates="tasks",
    )
    assignee: Mapped[Optional["Agent"]] = relationship(
        back_populates="assigned_tasks",
        foreign_keys=[assignee_id],
    )
    upstream_task: Mapped[Optional["Task"]] = relationship(
        remote_side="Task.id",
        foreign_keys=[upstream_task_id],
    )
    downstream_tasks: Mapped[List["Task"]] = relationship(
        remote_side="Task.id",
        foreign_keys=[upstream_task_id],
    )
    knowledge_documents: Mapped[List["KnowledgeDocument"]] = relationship(
        back_populates="task",
    )
    messages: Mapped[List["AgentMessage"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )
    
    # 索引
    __table_args__ = (
        Index("ix_tasks_project_status", "project_id", "status"),
        Index("ix_tasks_project_priority", "project_id", "priority"),
        Index("ix_tasks_assignee_status", "assignee_id", "status"),
        Index("ix_tasks_assignee_updated", "assignee_id", "updated_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, status={self.status.value})>"
    
    def is_blocked(self) -> bool:
        """检查任务是否被阻塞"""
        if self.status == TaskStatus.BLOCKED:
            return True
        # 检查上游任务是否完成
        if self.upstream_task and self.upstream_task.status != TaskStatus.COMPLETED:
            return True
        return False
    
    def can_start(self) -> bool:
        """检查任务是否可以开始"""
        if self.status != TaskStatus.PENDING:
            return False
        return not self.is_blocked()
