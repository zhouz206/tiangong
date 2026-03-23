"""
AgentMessage - Agent 消息模型
"""
from sqlalchemy import Column, Text, ForeignKey, Index, Enum, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy.types import JSON
import enum

from app.core.database import Base
from .base import UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from .project import Project
    from .task import Task
    from .agent import Agent


class MessageType(str, enum.Enum):
    """消息类型枚举"""
    TASK_HANDOFF = "task_handoff"  # 任务传递
    DISCUSSION = "discussion"  # 讨论
    NOTIFICATION = "notification"  # 通知
    RESULT = "result"  # 结果


class AgentMessage(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Agent 消息模型 - Agent 间通信和局部讨论记录
    
    字段说明:
    - project_id: 所属项目 ID
    - task_id: 所属任务 ID (可选)
    - sender_agent_id: 发送者 Agent ID
    - receiver_agent_id: 接收者 Agent ID (空表示广播)
    - content: 消息内容
    - message_type: 消息类型
    - is_private: 是否私有消息 (局部讨论标记)
    - parent_message_id: 父消息 ID (回复链)
    - metadata: JSON 附加信息
    - is_read: 是否已读
    - read_at: 读取时间
    """
    __tablename__ = "agent_messages"
    
    # 外键
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sender_agent_id: Mapped[str] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    receiver_agent_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    parent_message_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("agent_messages.id", ondelete="CASCADE"),
        nullable=True,
    )
    
    # 消息内容
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    # 消息类型
    message_type: Mapped[MessageType] = mapped_column(
        Enum(MessageType),
        nullable=False,
        default=MessageType.DISCUSSION,
        index=True,
    )
    
    # 隐私标记
    is_private: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    
    # 已读状态
    is_read: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # 附加信息
    extra_data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
    )
    
    # 关系
    project: Mapped["Project"] = relationship(
        back_populates="messages",
    )
    task: Mapped[Optional["Task"]] = relationship(
        back_populates="messages",
    )
    sender_agent: Mapped["Agent"] = relationship(
        back_populates="messages_sent",
        foreign_keys=[sender_agent_id],
    )
    receiver_agent: Mapped[Optional["Agent"]] = relationship(
        back_populates="messages_received",
        foreign_keys=[receiver_agent_id],
    )
    parent_message: Mapped[Optional["AgentMessage"]] = relationship(
        remote_side="AgentMessage.id",
        foreign_keys=[parent_message_id],
    )
    replies: Mapped[List["AgentMessage"]] = relationship(
        remote_side="AgentMessage.id",
        foreign_keys=[parent_message_id],
    )
    
    # 索引
    __table_args__ = (
        Index("ix_agent_messages_project_created", "project_id", "created_at"),
        Index("ix_agent_messages_task", "task_id", "created_at"),
        Index("ix_agent_messages_sender", "sender_agent_id", "created_at"),
        Index("ix_agent_messages_type", "message_type", "created_at"),
        Index("ix_agent_messages_private", "is_private", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<AgentMessage(id={self.id}, type={self.message_type.value}, private={self.is_private})>"
    
    def mark_as_read(self) -> None:
        """标记为已读"""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    def is_reply(self) -> bool:
        """检查是否是回复消息"""
        return self.parent_message_id is not None
