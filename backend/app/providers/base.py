"""
ModelProvider — 模型提供商抽象基类
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class ModelRole(str, Enum):
    """模型角色"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ModelMessage:
    """模型消息"""
    role: ModelRole
    content: str


@dataclass
class ModelUsage:
    """模型使用量"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class ModelResponse:
    """模型响应"""
    content: str
    model: str
    usage: ModelUsage = field(default_factory=ModelUsage)
    finish_reason: str = "stop"


@dataclass
class ModelConfig:
    """模型配置"""
    api_key: str
    base_url: Optional[str] = None
    model_name: str = "default"
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 30


class ModelProvider(ABC):
    """
    模型提供商抽象基类
    
    所有模型提供商必须实现此类
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """提供商名称"""
        pass
    
    @abstractmethod
    async def chat(self, messages: List[ModelMessage], config: ModelConfig) -> ModelResponse:
        """
        聊天补全
        
        Args:
            messages: 消息列表
            config: 模型配置
            
        Returns:
            ModelResponse: 模型响应
        """
        pass
    
    @abstractmethod
    async def embed(self, text: str, config: ModelConfig) -> List[float]:
        """
        生成嵌入向量
        
        Args:
            text: 输入文本
            config: 模型配置
            
        Returns:
            List[float]: 嵌入向量
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        pass
    
    def estimate_cost(self, usage: ModelUsage, model: str) -> float:
        """
        估算成本
        
        Args:
            usage: 使用量
            model: 模型名称
            
        Returns:
            float: 估算成本（美元）
        """
        return 0.0  # 默认返回 0，子类重写
