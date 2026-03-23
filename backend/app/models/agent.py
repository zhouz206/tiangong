"""
Agent - Agent 配置模型
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
    from .model_config import ModelConfig
    from .audit import AuditLog
    from .agent_message import AgentMessage


class AgentStatus(str, enum.Enum):
    """Agent 状态枚举"""
    ACTIVE = "active"  # 活跃
    INACTIVE = "inactive"  # 非活跃
    BUSY = "busy"  # 忙碌


class AgentRole(str, enum.Enum):
    """Agent 角色枚举 - 8 个核心角色"""
    MANAGER = "manager"  # 项目经理
    RESEARCHER = "researcher"  # 研究员
    PROGRAMMER = "programmer"  # 程序员
    DESIGNER = "designer"  # 设计师
    WRITER = "writer"  # 文案
    REVIEWER = "reviewer"  # 审核员
    DATA_ANALYST = "data_analyst"  # 数据分析师
    KNOWLEDGE_MANAGER = "knowledge_manager"  # 知识管理员


class Agent(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Agent 配置模型 - Agent 角色定义和配置
    
    字段说明:
    - workspace_id: 所属工作空间 ID
    - project_id: 所属项目 ID (可选，项目级 Agent)
    - name: Agent 名称
    - role: Agent 角色 (8 个核心角色之一)
    - description: Agent 描述
    - system_prompt: 系统提示词
    - model_config_id: 模型配置 ID
    - status: Agent 状态
    - capabilities: JSON 能力声明
    - skills: JSON 已启用 Skill 列表
    - mcp_services: JSON 已启用 MCP 服务
    - upstream_agents: JSON 上游 Agent IDs
    - downstream_agents: JSON 下游 Agent IDs
    - current_task_id: 当前任务 ID
    - temperature: 模型温度参数
    - max_tokens: 最大 token 数
    """
    __tablename__ = "agents"
    
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
    model_config_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("model_configs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    current_task_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("tasks.id", ondelete="SET NULL", use_alter=True),
        nullable=True,
    )
    
    # 基础信息
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    role: Mapped[AgentRole] = mapped_column(
        Enum(AgentRole),
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    system_prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    # 状态
    status: Mapped[AgentStatus] = mapped_column(
        Enum(AgentStatus),
        nullable=False,
        default=AgentStatus.ACTIVE,
        index=True,
    )
    
    # 模型参数
    temperature: Mapped[float] = mapped_column(
        default=0.7,
        nullable=False,
    )
    max_tokens: Mapped[int] = mapped_column(
        default=2048,
        nullable=False,
    )
    
    # 能力和配置 (JSON)
    capabilities: Mapped[Optional[list]] = mapped_column(
        JSON,
        nullable=True,
        default=list,
    )
    skills: Mapped[Optional[list]] = mapped_column(
        JSON,
        nullable=True,
        default=list,
    )
    mcp_services: Mapped[Optional[list]] = mapped_column(
        JSON,
        nullable=True,
        default=list,
    )
    upstream_agents: Mapped[Optional[list]] = mapped_column(
        JSON,
        nullable=True,
        default=list,
    )
    downstream_agents: Mapped[Optional[list]] = mapped_column(
        JSON,
        nullable=True,
        default=list,
    )
    
    # 关系
    workspace: Mapped["Workspace"] = relationship(
        back_populates="agents",
    )
    project: Mapped[Optional["Project"]] = relationship(
        back_populates="agents",
    )
    model_config: Mapped[Optional["ModelConfig"]] = relationship(
        back_populates="agents",
    )
    assigned_tasks: Mapped[List["Task"]] = relationship(
        back_populates="assignee",
        foreign_keys="Task.assignee_id",
    )
    current_task: Mapped[Optional["Task"]] = relationship(
        foreign_keys=[current_task_id],
    )
    messages_sent: Mapped[List["AgentMessage"]] = relationship(
        back_populates="sender_agent",
        foreign_keys="AgentMessage.sender_agent_id",
    )
    messages_received: Mapped[List["AgentMessage"]] = relationship(
        back_populates="receiver_agent",
        foreign_keys="AgentMessage.receiver_agent_id",
    )
    
    # 索引
    __table_args__ = (
        Index("ix_agents_workspace_role", "workspace_id", "role"),
        Index("ix_agents_project_status", "project_id", "status"),
    )
    
    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, name={self.name}, role={self.role.value})>"
    
    def can_accept_task(self) -> bool:
        """检查 Agent 是否可以接受任务"""
        return self.status == AgentStatus.ACTIVE and self.current_task_id is None
    
    def add_skill(self, skill_name: str):
        """添加 Skill"""
        if self.skills is None:
            self.skills = []
        if skill_name not in self.skills:
            self.skills.append(skill_name)
    
    def remove_skill(self, skill_name: str):
        """移除 Skill"""
        if self.skills and skill_name in self.skills:
            self.skills.remove(skill_name)
