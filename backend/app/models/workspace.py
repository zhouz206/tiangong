"""
Workspace - 工作空间模型
"""
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy.types import JSON

from app.core.database import Base
from .base import UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from .user import User
    from .workspace_member import WorkspaceMember
    from .project import Project
    from .agent import Agent
    from .model_config import ModelConfig
    from .knowledge import KnowledgeDocument
    from .audit import AuditLog


class Workspace(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    工作空间模型 - 顶级资源容器，数据隔离边界
    
    字段说明:
    - name: 工作空间名称
    - description: 工作空间描述
    - owner_id: 所有者用户 ID
    - slug: URL 友好的唯一标识
    - is_active: 是否激活
    - settings: JSON 配置 (主题、通知等)
    - quota_limit: 资源配额限制
    """
    __tablename__ = "workspaces"
    
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
    
    # 所有者
    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # URL 标识
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    
    # 状态
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )
    
    # 扩展配置
    settings: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
    )
    quota_limit: Mapped[Optional[int]] = mapped_column(
        nullable=True,
    )
    
    # 关系
    owner: Mapped["User"] = relationship(
        back_populates="workspaces",
        foreign_keys=[owner_id],
    )
    members: Mapped[List["WorkspaceMember"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    projects: Mapped[List["Project"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    agents: Mapped[List["Agent"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    model_configs: Mapped[List["ModelConfig"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    knowledge_documents: Mapped[List["KnowledgeDocument"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    
    # 索引
    __table_args__ = (
        Index("ix_workspaces_owner_active", "owner_id", "is_active"),
        Index("ix_workspaces_slug_active", "slug", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<Workspace(id={self.id}, name={self.name}, slug={self.slug})>"
