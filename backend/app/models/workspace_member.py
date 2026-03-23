"""
WorkspaceMember - 工作空间成员关系模型
"""
from sqlalchemy import Column, String, Text, ForeignKey, Index, Enum, DateTime, func
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import enum

from app.core.database import Base
from .base import UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from .user import User
    from .workspace import Workspace


class MemberRole(str, enum.Enum):
    """成员角色枚举"""
    OWNER = "owner"  # 所有者 - 完全控制
    COLLABORATOR = "collaborator"  # 协作者 - 可创建/修改任务
    OBSERVER = "observer"  # 观察者 - 只读权限


class WorkspaceMember(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    工作空间成员关系模型 - 用户与工作空间的多对多关系，权限绑定
    
    字段说明:
    - workspace_id: 工作空间 ID
    - user_id: 用户 ID
    - role: 成员角色 (owner/collaborator/observer)
    - joined_at: 加入时间
    - invited_by: 邀请人用户 ID
    - is_active: 是否活跃成员
    - permissions: JSON 细粒度权限扩展
    """
    __tablename__ = "workspace_members"
    
    # 外键
    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # 角色
    role: Mapped[MemberRole] = mapped_column(
        Enum(MemberRole),
        nullable=False,
        default=MemberRole.OBSERVER,
        index=True,
    )
    
    # 加入信息
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
    )
    invited_by: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # 状态
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )
    
    # 扩展权限 (可选，用于细粒度权限)
    permissions: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )
    
    # 关系
    workspace: Mapped["Workspace"] = relationship(
        back_populates="members",
    )
    user: Mapped["User"] = relationship(
        back_populates="memberships",
        foreign_keys=[user_id],
    )
    inviter: Mapped[Optional["User"]] = relationship(
        foreign_keys=[invited_by],
    )
    
    # 索引和约束
    __table_args__ = (
        Index("ix_workspace_members_workspace_active", "workspace_id", "is_active"),
        Index("ix_workspace_members_user_active", "user_id", "is_active"),
        # 联合唯一约束：同一用户在同一工作空间只能有一个成员记录
        Index("uix_workspace_members", "workspace_id", "user_id", unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<WorkspaceMember(workspace_id={self.workspace_id}, user_id={self.user_id}, role={self.role.value})>"
    
    def has_permission(self, permission: str) -> bool:
        """检查是否有指定权限"""
        # 基于角色的权限检查
        role_permissions = {
            MemberRole.OWNER: {"read", "write", "delete", "admin"},
            MemberRole.COLLABORATOR: {"read", "write"},
            MemberRole.OBSERVER: {"read"},
        }
        return permission in role_permissions.get(self.role, set())
