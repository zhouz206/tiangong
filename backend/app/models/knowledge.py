"""
KnowledgeDocument - 知识文档模型
"""
from sqlalchemy import Column, String, Text, ForeignKey, Index, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy.types import JSON
import enum

from app.core.database import Base
from .base import UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from .workspace import Workspace
    from .project import Project
    from .task import Task
    from .user import User
    from .audit import AuditLog


class KnowledgeType(str, enum.Enum):
    """知识类型枚举"""
    DOC = "doc"  # 文档
    DISCUSSION = "discussion"  # 讨论
    REFERENCE = "reference"  # 参考资料
    EXPERIENCE = "experience"  # 经验总结
    CODE = "code"  # 代码


class SourceType(str, enum.Enum):
    """来源类型枚举"""
    MANUAL = "manual"  # 手动添加
    AUTO_ARCHIVE = "auto_archive"  # 自动归档
    AGENT_GENERATED = "agent_generated"  # Agent 生成


class KnowledgeDocument(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    知识文档模型 - 知识库系统核心，支持自动归档和语义搜索
    
    字段说明:
    - workspace_id: 所属工作空间 ID
    - project_id: 所属项目 ID (可选)
    - task_id: 所属任务 ID (可选)
    - title: 文档标题
    - content: 文档内容
    - type: 知识类型
    - tags: JSON AI 自动标签
    - vector_id: ChromaDB 向量 ID (用于语义搜索)
    - source_type: 来源类型
    - created_by: 创建者用户 ID
    - metadata: JSON 元数据 (版本、来源等)
    """
    __tablename__ = "knowledge_documents"
    
    # 外键
    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    task_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # 基础信息
    title: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    # 分类
    type: Mapped[KnowledgeType] = mapped_column(
        Enum(KnowledgeType),
        nullable=False,
        default=KnowledgeType.DOC,
        index=True,
    )
    source_type: Mapped[SourceType] = mapped_column(
        Enum(SourceType),
        nullable=False,
        default=SourceType.MANUAL,
        index=True,
    )
    
    # 标签和向量
    tags: Mapped[Optional[list]] = mapped_column(
        JSON,
        nullable=True,
        default=list,
    )
    vector_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    
    # 元数据
    extra_data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
    )
    
    # 关系
    workspace: Mapped["Workspace"] = relationship(
        back_populates="knowledge_documents",
    )
    project: Mapped[Optional["Project"]] = relationship(
        back_populates="knowledge_documents",
    )
    task: Mapped[Optional["Task"]] = relationship(
        back_populates="knowledge_documents",
    )
    created_by_user: Mapped[Optional["User"]] = relationship(
        back_populates="knowledge_documents",
        foreign_keys=[created_by],
    )
    
    # 索引
    __table_args__ = (
        Index("ix_knowledge_workspace_type", "workspace_id", "type"),
        Index("ix_knowledge_workspace_created", "workspace_id", "created_at"),
        Index("ix_knowledge_project", "project_id", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<KnowledgeDocument(id={self.id}, title={self.title}, type={self.type.value})>"
    
    def add_tag(self, tag: str) -> None:
        """添加标签"""
        if self.tags is None:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        """移除标签"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
