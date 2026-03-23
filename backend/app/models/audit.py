"""
AuditLog - 审计日志模型
"""
from sqlalchemy import Column, String, ForeignKey, Index, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy.types import JSON
import enum

from app.core.database import Base
from .base import UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from .workspace import Workspace
    from .user import User
    from .agent import Agent


class ActorType(str, enum.Enum):
    """执行者类型枚举"""
    USER = "user"
    AGENT = "agent"


class AuditLog(Base, UUIDMixin, TimestampMixin):
    """
    审计日志模型 - 执行追溯系统核心，完整操作记录
    
    字段说明:
    - workspace_id: 所属工作空间 ID
    - actor_id: 执行者 ID (用户或 Agent)
    - actor_type: 执行者类型 (user/agent)
    - action: 操作类型 (create/modify/delete/approve 等)
    - resource_type: 资源类型 (project/task/agent 等)
    - resource_id: 资源 ID
    - timestamp: 操作时间
    - before: JSON 变更前内容
    - after: JSON 变更后内容
    - metadata: JSON 附加信息 (model, tokens 等)
    - ip_address: IP 地址 (可选，安全审计)
    """
    __tablename__ = "audit_logs"
    
    # 注意：AuditLog 不使用 SoftDeleteMixin，审计日志不应被删除
    
    # 外键
    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # 执行者信息
    actor_id: Mapped[Optional[str]] = mapped_column(
        nullable=True,
        index=True,
    )
    actor_type: Mapped[Optional[ActorType]] = mapped_column(
        Enum(ActorType),
        nullable=True,
        index=True,
    )
    
    # 操作信息
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    resource_id: Mapped[str] = mapped_column(
        nullable=False,
        index=True,
    )
    
    # 时间 (使用单独的 timestamp 字段以便查询)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        index=True,
    )
    
    # 变更内容
    before: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )
    after: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )
    
    # 附加信息
    extra_data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),  # IPv6 最大长度
        nullable=True,
    )
    
    # 关系
    workspace: Mapped["Workspace"] = relationship(
        # 注意：不使用 back_populates，因为 Workspace 模型中已移除 audit_logs 关系
    )
    actor_user: Mapped[Optional["User"]] = relationship(
        foreign_keys=[actor_id],
        primaryjoin="and_(AuditLog.actor_id == User.id, AuditLog.actor_type == 'user')",
    )
    actor_agent: Mapped[Optional["Agent"]] = relationship(
        foreign_keys=[actor_id],
        primaryjoin="and_(AuditLog.actor_id == Agent.id, AuditLog.actor_type == 'agent')",
    )
    
    # 索引
    __table_args__ = (
        Index("ix_audit_logs_resource", "resource_type", "resource_id", "timestamp"),
        Index("ix_audit_logs_actor", "actor_id", "actor_type", "timestamp"),
        Index("ix_audit_logs_workspace_action", "workspace_id", "action"),
    )
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, resource={self.resource_type}:{self.resource_id})>"
    
    @classmethod
    def create_log(
        cls,
        workspace_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        actor_id: Optional[str] = None,
        actor_type: Optional[ActorType] = None,
        before: Optional[dict] = None,
        after: Optional[dict] = None,
        metadata: Optional[dict] = None,
        ip_address: Optional[str] = None,
    ) -> "AuditLog":
        """创建审计日志的便捷方法"""
        return cls(
            workspace_id=workspace_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            actor_id=actor_id,
            actor_type=actor_type,
            before=before,
            after=after,
            metadata=metadata or {},
            ip_address=ip_address,
        )
