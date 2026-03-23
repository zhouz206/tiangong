"""
User - 用户模型
"""
from sqlalchemy import Column, String, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from app.core.database import Base
from .base import UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from .workspace import Workspace, WorkspaceMember
    from .project import Project
    from .knowledge import KnowledgeDocument
    from .audit import AuditLog


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    用户模型 - 系统用户身份管理
    
    字段说明:
    - email: 唯一邮箱地址，用于登录
    - name: 用户显示名称
    - hashed_password: 加密后的密码
    - is_active: 账户是否激活
    - is_superuser: 是否超级管理员
    - last_login_at: 最后登录时间
    - avatar_url: 头像 URL
    - github_id: GitHub OAuth ID (可选)
    - google_id: Google OAuth ID (可选)
    """
    __tablename__ = "users"
    
    # 基础信息
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    
    # 账户状态
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )
    is_superuser: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )
    
    # 扩展信息
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    github_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
    )
    google_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
    )
    
    # 关系
    workspaces: Mapped[List["Workspace"]] = relationship(
        back_populates="owner",
        foreign_keys="Workspace.owner_id",
    )
    memberships: Mapped[List["WorkspaceMember"]] = relationship(
        back_populates="user",
        foreign_keys="WorkspaceMember.user_id",
    )
    projects: Mapped[List["Project"]] = relationship(
        back_populates="owner",
        foreign_keys="Project.owner_id",
    )
    knowledge_documents: Mapped[List["KnowledgeDocument"]] = relationship(
        back_populates="created_by_user",
        foreign_keys="KnowledgeDocument.created_by",
    )
    # 注意：audit_logs 关系已移除，因为 actor_id 没有外键约束
    # 可以通过查询获取：session.query(AuditLog).filter(AuditLog.actor_id == user.id, AuditLog.actor_type == 'user')
    
    # 索引
    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
