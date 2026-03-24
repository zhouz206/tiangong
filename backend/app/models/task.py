"""
Task - 任务模型
"""
from sqlalchemy import Column, String, Text, ForeignKey, Enum, Index
from sqlalchemy.orm import Mapped, relationship
import enum
from typing import Optional, TYPE_CHECKING

from .base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from .milestone import Milestone


class TaskStatus(str, enum.Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    """任务优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base, UUIDMixin, TimestampMixin):  # type: ignore
    """
    任务模型
    
    字段:
    - milestone_id: 所属里程碑 ID
    - title: 任务标题
    - description: 描述
    - status: 状态
    - priority: 优先级
    - upstream_task_id: 上游任务 ID（依赖）
    """
    __tablename__ = "tasks"
    
    # 外键
    milestone_id = Column(String(36), ForeignKey("milestones.id", ondelete="CASCADE"), nullable=False, index=True)
    upstream_task_id = Column(String(36), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    
    # 基础信息
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    
    # 状态和优先级
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING, index=True)
    priority = Column(Enum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM, index=True)
    
    # 关系
    milestone: Mapped["Milestone"] = relationship("Milestone", back_populates="tasks")
    upstream_task: Mapped[Optional["Task"]] = relationship(
        "Task",
        remote_side="Task.id",
        foreign_keys=[upstream_task_id],
    )
    
    # 索引
    __table_args__ = (
        Index("ix_tasks_milestone_status", "milestone_id", "status"),
    )
    
    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, status={self.status.value})>"
    
    def is_blocked(self) -> bool:
        """检查任务是否被阻塞"""
        if self.status == TaskStatus.BLOCKED:
            return True
        if self.upstream_task and self.upstream_task.status != TaskStatus.COMPLETED:
            return True
        return False
    
    def can_start(self) -> bool:
        """检查任务是否可以开始"""
        return self.status == TaskStatus.PENDING and not self.is_blocked()
