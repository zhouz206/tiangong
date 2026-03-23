"""
Anthropic (Claude) 模型提供商实现

支持 Claude-3.5-Sonnet, Claude-3-Opus 等模型。
"""
import os
from typing import Any, List, AsyncIterator, Optional
import asyncio

from .base import (
    ModelProvider,
    ModelConfig,
    ModelResponse,
    ModelUsage,
    ChatMessage,
    ModelCapability,
    ModelProviderError,
    ModelProviderRateLimitError,
    ModelProviderAuthenticationError,
    ModelProviderUnavailableError,
)


# Anthropic 模型成本（每 1K tokens，美元）
ANTHROPIC_PRICES = {
    "claude-3-5-sonnet-20241022": {"prompt": 0.003, "completion": 0.015},
    "claude-3-5-haiku-20241022": {"prompt": 0.0008, "completion": 0.004},
    "claude-3-opus-20240229": {"prompt": 0.015, "completion": 0.075},
    "claude-3-sonnet-20240229": {"prompt": 0.003, "completion": 0.015},
    "claude-3-haiku-20240307": {"prompt": 0.00025, "completion": 0.00125},
}


class AnthropicProvider(ModelProvider):
    """
    Anthropic (Claude) 模型提供商
    
    使用示例:
        provider = AnthropicProvider(api_key="sk-ant-...")
        await provider.initialize()
        response = await provider.chat(
            messages=[ChatMessage(role="user", content="Hello")],
            config=ModelConfig(model_name="claude-3-5-sonnet-20241022")
        )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        super().__init__("anthropic")
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = base_url
        
        self._client: Optional[Any] = None
        self._async_client: Optional[Any] = None
    
    async def initialize(self) -> None:
        """初始化 Anthropic 客户端"""
        if self._initialized:
            return
        
        if not self.api_key:
            raise ModelProviderAuthenticationError(
                "Anthropic API key is required. Set ANTHROPIC_API_KEY env var or pass api_key parameter."
            )
        
        try:
            # 延迟导入 anthropic 库
            import anthropic
            
            # 同步客户端
            self._client = anthropic.Anthropic(
                api_key=self.api_key,
                base_url=self.base_url,
            )
            
            # 异步客户端
            self._async_client = anthropic.AsyncAnthropic(
                api_key=self.api_key,
                base_url=self.base_url,
            )
            
            self._initialized = True
            
        except ImportError:
            raise ModelProviderUnavailableError(
                "anthropic package not installed. Run: pip install anthropic"
            )
        except Exception as e:
            if "api key" in str(e).lower() or "authentication" in str(e).lower():
                raise ModelProviderAuthenticationError(f"Anthropic authentication failed: {e}")
            raise ModelProviderUnavailableError(f"Anthropic service unavailable: {e}")
    
    async def shutdown(self) -> None:
        """关闭 Anthropic 客户端"""
        self._client = None
        self._async_client = None
        self._initialized = False
    
    async def chat(
        self,
        messages: List[ChatMessage],
        config: Optional[ModelConfig] = None,
    ) -> ModelResponse:
        """发送聊天请求"""
        if not self._initialized:
            await self.initialize()
        
        config = config or ModelConfig(model_name="claude-3-5-haiku-20241022")
        self.validate_config(config)
        
        # 转换消息格式（Anthropic 需要分离 system 和 messages）
        system_prompt, anthropic_messages = self._convert_messages(messages)
        
        try:
            response = await self._async_client.messages.create(
                model=config.model_name,
                max_tokens=config.max_tokens,
                messages=anthropic_messages,
                system=system_prompt,
                temperature=config.temperature,
                top_p=config.top_p,
            )
            
            # 提取响应
            content = response.content[0].text if response.content else ""
            
            # 提取使用量
            usage = None
            if hasattr(response, 'usage'):
                usage = ModelUsage(
                    prompt_tokens=response.usage.input_tokens,
                    completion_tokens=response.usage.output_tokens,
                    total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                )
            
            return ModelResponse(
                content=content,
                model=config.model_name,
                usage=usage,
                finish_reason=response.stop_reason,
                raw_response=response,
            )
            
        except Exception as e:
            raise self._handle_error(e)
    
    async def chat_stream(
        self,
        messages: List[ChatMessage],
        config: Optional[ModelConfig] = None,
    ) -> AsyncIterator[str]:
        """流式聊天请求"""
        if not self._initialized:
            await self.initialize()
        
        config = config or ModelConfig(model_name="claude-3-5-haiku-20241022")
        self.validate_config(config)
        
        # 转换消息格式
        system_prompt, anthropic_messages = self._convert_messages(messages)
        
        try:
            async with self._async_client.messages.stream(
                model=config.model_name,
                max_tokens=config.max_tokens,
                messages=anthropic_messages,
                system=system_prompt,
                temperature=config.temperature,
                top_p=config.top_p,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            raise self._handle_error(e)
    
    async def get_embedding(
        self,
        text: str,
        model: Optional[str] = None,
    ) -> List[float]:
        """
        获取文本嵌入向量
        
        Anthropic 暂不提供嵌入模型，抛出异常
        """
        raise ModelProviderError(
            "Anthropic does not provide embedding models. "
            "Use OpenAI or other providers for embeddings."
        )
    
    def get_capabilities(self) -> List[ModelCapability]:
        """获取支持的能力"""
        return [
            ModelCapability.CHAT,
            ModelCapability.COMPLETION,
            ModelCapability.VISION,
        ]
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return list(ANTHROPIC_PRICES.keys())
    
    def estimate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str,
    ) -> float:
        """估算成本"""
        pricing = ANTHROPIC_PRICES.get(model, ANTHROPIC_PRICES["claude-3-haiku-20240307"])
        prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing["completion"]
        return prompt_cost + completion_cost
    
    def _convert_messages(self, messages: List[ChatMessage]) -> tuple[str, List[dict]]:
        """
        转换消息为 Anthropic 格式
        
        Anthropic 要求:
        - system 提示词单独传递
        - messages 只包含 user 和 assistant 角色
        
        Returns:
            (system_prompt, messages)
        """
        system_prompt = ""
        anthropic_messages = []
        
        for msg in messages:
            if msg.role.value == "system":
                system_prompt = msg.content
            elif msg.role.value in ("user", "assistant"):
                anthropic_messages.append({
                    "role": msg.role.value,
                    "content": msg.content,
                })
        
        return system_prompt, anthropic_messages
    
    def _handle_error(self, error: Exception) -> Exception:
        """转换错误类型"""
        error_str = str(error).lower()
        
        if "rate limit" in error_str or "429" in error_str:
            return ModelProviderRateLimitError(f"Anthropic rate limit exceeded: {error}")
        
        if "api key" in error_str or "authentication" in error_str:
            return ModelProviderAuthenticationError(f"Anthropic authentication failed: {error}")
        
        return ModelProviderError(f"Anthropic error: {error}")
