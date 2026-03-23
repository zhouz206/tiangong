"""
模型提供商模块

提供统一的模型接口和多个提供商实现：
- OpenAI (GPT-4, GPT-3.5-turbo)
- Anthropic (Claude-3.5-Sonnet)
- Qwen (通义千问)
- Ollama (本地模型)

智能路由器支持成本优先、性能优先等策略。
"""

from .base import (
    ModelProvider,
    ModelConfig,
    ModelResponse,
    ModelUsage,
    ChatMessage,
    ModelCapability,
    ModelRole,
    ModelProviderError,
    ModelProviderUnavailableError,
    ModelProviderRateLimitError,
    ModelProviderAuthenticationError,
    count_tokens,
    create_provider,
)

from .openai_provider import OpenAIProvider, OPENAI_PRICES
from .anthropic_provider import AnthropicProvider, ANTHROPIC_PRICES
from .qwen_provider import QwenProvider, QWEN_PRICES
from .ollama_provider import OllamaProvider

from .router import (
    SmartRouter,
    RoutingStrategy,
    RoutingDecision,
    ModelStats,
    get_router,
    reset_router,
)


__all__ = [
    # 基类和通用类型
    "ModelProvider",
    "ModelConfig",
    "ModelResponse",
    "ModelUsage",
    "ChatMessage",
    "ModelCapability",
    "ModelRole",
    "ModelProviderError",
    "ModelProviderUnavailableError",
    "ModelProviderRateLimitError",
    "ModelProviderAuthenticationError",
    "count_tokens",
    "create_provider",
    
    # 提供商实现
    "OpenAIProvider",
    "OPENAI_PRICES",
    "AnthropicProvider",
    "ANTHROPIC_PRICES",
    "QwenProvider",
    "QWEN_PRICES",
    "OllamaProvider",
    
    # 智能路由
    "SmartRouter",
    "RoutingStrategy",
    "RoutingDecision",
    "ModelStats",
    "get_router",
    "reset_router",
]
