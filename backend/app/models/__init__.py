"""
数据库模型导出

所有 SQLAlchemy 模型在此统一导出，便于导入使用。
"""

from app.core.database import Base
from .base import UUIDMixin, TimestampMixin, SoftDeleteMixin

from .user import User
from .workspace import Workspace
from .workspace_member import WorkspaceMember, MemberRole
from .project import Project, ProjectStatus, ProjectPhase
from .task import Task, TaskStatus, TaskPriority
from .agent import Agent, AgentStatus, AgentRole
from .model_config import ModelConfig, ModelProvider
from .knowledge import KnowledgeDocument, KnowledgeType, SourceType
from .audit import AuditLog, ActorType
from .agent_message import AgentMessage, MessageType

# 所有模型的列表，便于批量操作
__all__ = [
    # 基类
    "Base",
    "UUIDMixin",
    "TimestampMixin",
    "SoftDeleteMixin",
    # 核心模型
    "User",
    "Workspace",
    "WorkspaceMember",
    "Project",
    "Task",
    "Agent",
    "ModelConfig",
    "KnowledgeDocument",
    "AuditLog",
    "AgentMessage",
    # 枚举类型
    "MemberRole",
    "ProjectStatus",
    "ProjectPhase",
    "TaskStatus",
    "TaskPriority",
    "AgentStatus",
    "AgentRole",
    "ModelProvider",
    "KnowledgeType",
    "SourceType",
    "ActorType",
    "MessageType",
]
