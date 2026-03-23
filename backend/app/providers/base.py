"""
模型提供商统一接口

定义模型调用的抽象基类，所有模型提供商必须实现此接口。
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, List, AsyncIterator
import asyncio


class ModelRole(str, Enum):
    """模型角色枚举"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ModelCapability(str, Enum):
    """模型能力枚举"""
    CHAT = "chat"  # 对话聊天
    COMPLETION = "completion"  # 文本补全
    EMBEDDING = "embedding"  # 向量嵌入
    VISION = "vision"  # 图像理解
    FUNCTION_CALL = "function_call"  # 函数调用


@dataclass
class ChatMessage:
    """聊天消息"""
    role: ModelRole
    content: str
    name: Optional[str] = None
    function_call: Optional[dict] = None
    tool_calls: Optional[list] = None


@dataclass
class ModelUsage:
    """模型使用量统计"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    def __post_init__(self):
        if self.total_tokens == 0:
            self.total_tokens = self.prompt_tokens + self.completion_tokens


@dataclass
class ModelResponse:
    """模型响应"""
    content: str
    model: str
    usage: Optional[ModelUsage] = None
    finish_reason: Optional[str] = None
    raw_response: Optional[Any] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelConfig:
    """模型配置"""
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[List[str]] = None
    stream: bool = False


class ModelProvider(ABC):
    """
    模型提供商抽象基类
    
    所有模型提供商实现必须继承此类并实现核心抽象方法。
    
    使用示例:
        provider = OpenAIProvider(api_key="...")
        response = await provider.chat(
            messages=[ChatMessage(role="user", content="Hello")],
            config=ModelConfig(model_name="gpt-4")
        )
    """
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """初始化模型提供商（如建立连接、验证 API 密钥等）"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """关闭模型提供商（如释放连接、清理资源等）"""
        pass
    
    @abstractmethod
    async def chat(
        self,
        messages: List[ChatMessage],
        config: Optional[ModelConfig] = None,
    ) -> ModelResponse:
        """
        发送聊天请求
        
        Args:
            messages: 消息历史列表
            config: 模型配置
            
        Returns:
            模型响应
        """
        pass
    
    @abstractmethod
    async def chat_stream(
        self,
        messages: List[ChatMessage],
        config: Optional[ModelConfig] = None,
    ) -> AsyncIterator[str]:
        """
        流式聊天请求
        
        Args:
            messages: 消息历史列表
            config: 模型配置
            
        Yields:
            响应文本片段
        """
        pass
    
    @abstractmethod
    async def get_embedding(
        self,
        text: str,
        model: Optional[str] = None,
    ) -> List[float]:
        """
        获取文本嵌入向量
        
        Args:
            text: 输入文本
            model: 嵌入模型名称
            
        Returns:
            嵌入向量
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[ModelCapability]:
        """获取模型支持的能力列表"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        pass
    
    @abstractmethod
    def estimate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str,
    ) -> float:
        """
        估算成本
        
        Args:
            prompt_tokens: 输入 token 数
            completion_tokens: 输出 token 数
            model: 模型名称
            
        Returns:
            估算成本（美元）
        """
        pass
    
    async def is_available(self) -> bool:
        """检查模型服务是否可用"""
        try:
            await self.initialize()
            return True
        except Exception:
            return False
    
    def validate_config(self, config: ModelConfig) -> None:
        """验证模型配置"""
        if config.temperature < 0 or config.temperature > 2:
            raise ValueError("temperature must be between 0 and 2")
        if config.max_tokens < 1:
            raise ValueError("max_tokens must be positive")
        if config.top_p < 0 or config.top_p > 1:
            raise ValueError("top_p must be between 0 and 1")


class ModelProviderError(Exception):
    """模型提供商错误基类"""
    pass


class ModelProviderUnavailableError(ModelProviderError):
    """模型服务不可用"""
    pass


class ModelProviderRateLimitError(ModelProviderError):
    """API 限流错误"""
    pass


class ModelProviderAuthenticationError(ModelProviderError):
    """认证失败"""
    pass


def count_tokens(text: str) -> int:
    """
    估算文本 token 数
    
    简单估算：英文约 4 字符/token，中文约 2 字符/token
    """
    # 简单估算公式
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    other_chars = len(text) - chinese_chars
    return chinese_chars * 2 + other_chars // 4


def create_provider(provider_type: str, **kwargs) -> ModelProvider:
    """
    工厂函数：创建模型提供商实例
    
    Args:
        provider_type: 提供商类型 (openai, anthropic, qwen, ollama)
        **kwargs: 提供商特定参数
        
    Returns:
        模型提供商实例
    """
    # 延迟导入避免循环依赖
    if provider_type == "openai":
        from .openai_provider import OpenAIProvider
        return OpenAIProvider(**kwargs)
    elif provider_type == "anthropic":
        from .anthropic_provider import AnthropicProvider
        return AnthropicProvider(**kwargs)
    elif provider_type == "qwen":
        from .qwen_provider import QwenProvider
        return QwenProvider(**kwargs)
    elif provider_type == "ollama":
        from .ollama_provider import OllamaProvider
        return OllamaProvider(**kwargs)
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
