"""
ModelConfig - 模型配置模型
"""
from sqlalchemy import Column, String, ForeignKey, Index, Enum, Integer, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy.types import JSON
import enum

from app.core.database import Base
from .base import UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from .workspace import Workspace
    from .agent import Agent


class ModelProvider(str, enum.Enum):
    """模型提供商枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    QWEN = "qwen"
    OLLAMA = "ollama"


class ModelConfig(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    模型配置模型 - 模型提供商配置和路由策略
    
    字段说明:
    - workspace_id: 所属工作空间 ID
    - name: 配置名称
    - provider: 模型提供商
    - api_key_encrypted: 加密的 API 密钥
    - endpoint: 本地模型端点 (用于 Ollama 等)
    - model_name: 模型名称
    - context_limit: 上下文长度限制
    - priority: 路由优先级 (数字越小优先级越高)
    - cost_per_token: 每 token 成本
    - is_offline: 是否离线模型
    - is_active: 是否激活
    - fallback_model_ids: JSON 降级模型列表
    - rate_limit: API 限流配置 (每分钟请求数)
    """
    __tablename__ = "model_configs"
    
    # 外键
    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # 基础信息
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    provider: Mapped[ModelProvider] = mapped_column(
        Enum(ModelProvider),
        nullable=False,
        index=True,
    )
    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    
    # API 配置
    api_key_encrypted: Mapped[Optional[str]] = mapped_column(
        nullable=True,
    )
    endpoint: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    
    # 模型参数
    context_limit: Mapped[int] = mapped_column(
        default=4096,
        nullable=False,
    )
    priority: Mapped[int] = mapped_column(
        default=1,
        nullable=False,
    )
    cost_per_token: Mapped[float] = mapped_column(
        default=0.0,
        nullable=False,
    )
    rate_limit: Mapped[Optional[int]] = mapped_column(
        nullable=True,
    )
    
    # 状态
    is_offline: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        index=True,
    )
    
    # 降级策略
    fallback_model_ids: Mapped[Optional[list]] = mapped_column(
        JSON,
        nullable=True,
        default=list,
    )
    
    # 关系
    workspace: Mapped["Workspace"] = relationship(
        back_populates="model_configs",
    )
    agents: Mapped[List["Agent"]] = relationship(
        back_populates="model_config",
    )
    
    # 索引
    __table_args__ = (
        Index("ix_model_configs_provider_active", "provider", "is_active"),
        Index("ix_model_configs_workspace_priority", "workspace_id", "priority"),
    )
    
    def __repr__(self) -> str:
        return f"<ModelConfig(id={self.id}, name={self.name}, provider={self.provider.value})>"
    
    def get_full_model_name(self) -> str:
        """获取完整模型名称"""
        if self.provider == ModelProvider.OLLAMA and self.endpoint:
            return f"{self.endpoint}/{self.model_name}"
        return self.model_name
    
    def add_fallback(self, model_id: str):
        """添加降级模型"""
        if self.fallback_model_ids is None:
            self.fallback_model_ids = []
        if model_id not in self.fallback_model_ids:
            self.fallback_model_ids.append(model_id)
    
    def remove_fallback(self, model_id: str):
        """移除降级模型"""
        if self.fallback_model_ids and model_id in self.fallback_model_ids:
            self.fallback_model_ids.remove(model_id)
