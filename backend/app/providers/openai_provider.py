"""
OpenAI 模型提供商实现

支持 GPT-4, GPT-3.5-turbo 等模型。
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


# OpenAI 模型成本（每 1K tokens，美元）
OPENAI_PRICES = {
    "gpt-4": {"prompt": 0.03, "completion": 0.06},
    "gpt-4-32k": {"prompt": 0.06, "completion": 0.12},
    "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
    "gpt-4o": {"prompt": 0.005, "completion": 0.015},
    "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
    "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
    "gpt-3.5-turbo-16k": {"prompt": 0.003, "completion": 0.004},
}


class OpenAIProvider(ModelProvider):
    """
    OpenAI 模型提供商
    
    使用示例:
        provider = OpenAIProvider(api_key="sk-...")
        await provider.initialize()
        response = await provider.chat(
            messages=[ChatMessage(role="user", content="Hello")],
            config=ModelConfig(model_name="gpt-4")
        )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
    ):
        super().__init__("openai")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.organization = organization or os.getenv("OPENAI_ORGANIZATION")
        
        self._client: Optional[Any] = None
        self._async_client: Optional[Any] = None
    
    async def initialize(self) -> None:
        """初始化 OpenAI 客户端"""
        if self._initialized:
            return
        
        if not self.api_key:
            raise ModelProviderAuthenticationError(
                "OpenAI API key is required. Set OPENAI_API_KEY env var or pass api_key parameter."
            )
        
        try:
            # 延迟导入 openai 库
            import openai
            
            # 同步客户端
            self._client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                organization=self.organization,
            )
            
            # 异步客户端
            self._async_client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                organization=self.organization,
            )
            
            # 验证连接
            await self._async_client.models.list()
            self._initialized = True
            
        except ImportError:
            raise ModelProviderUnavailableError(
                "openai package not installed. Run: pip install openai"
            )
        except Exception as e:
            if "API key" in str(e) or "authentication" in str(e).lower():
                raise ModelProviderAuthenticationError(f"OpenAI authentication failed: {e}")
            raise ModelProviderUnavailableError(f"OpenAI service unavailable: {e}")
    
    async def shutdown(self) -> None:
        """关闭 OpenAI 客户端"""
        if self._client:
            # OpenAI 客户端不需要显式关闭
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
        
        config = config or ModelConfig(model_name="gpt-4o-mini")
        self.validate_config(config)
        
        # 转换消息格式
        openai_messages = self._convert_messages(messages)
        
        try:
            response = await self._async_client.chat.completions.create(
                model=config.model_name,
                messages=openai_messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                frequency_penalty=config.frequency_penalty,
                presence_penalty=config.presence_penalty,
                stop=config.stop_sequences,
                stream=False,
            )
            
            # 提取响应
            choice = response.choices[0]
            content = choice.message.content or ""
            
            # 提取使用量
            usage = None
            if response.usage:
                usage = ModelUsage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                )
            
            return ModelResponse(
                content=content,
                model=config.model_name,
                usage=usage,
                finish_reason=choice.finish_reason,
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
        
        config = config or ModelConfig(model_name="gpt-4o-mini", stream=True)
        config.stream = True
        self.validate_config(config)
        
        # 转换消息格式
        openai_messages = self._convert_messages(messages)
        
        try:
            stream = await self._async_client.chat.completions.create(
                model=config.model_name,
                messages=openai_messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                frequency_penalty=config.frequency_penalty,
                presence_penalty=config.presence_penalty,
                stop=config.stop_sequences,
                stream=True,
            )
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise self._handle_error(e)
    
    async def get_embedding(
        self,
        text: str,
        model: Optional[str] = None,
    ) -> List[float]:
        """获取文本嵌入向量"""
        if not self._initialized:
            await self.initialize()
        
        model = model or "text-embedding-3-small"
        
        try:
            response = await self._async_client.embeddings.create(
                model=model,
                input=text,
            )
            return response.data[0].embedding
            
        except Exception as e:
            raise self._handle_error(e)
    
    def get_capabilities(self) -> List[ModelCapability]:
        """获取支持的能力"""
        return [
            ModelCapability.CHAT,
            ModelCapability.COMPLETION,
            ModelCapability.EMBEDDING,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALL,
        ]
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return list(OPENAI_PRICES.keys())
    
    def estimate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str,
    ) -> float:
        """估算成本"""
        pricing = OPENAI_PRICES.get(model, OPENAI_PRICES["gpt-3.5-turbo"])
        prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing["completion"]
        return prompt_cost + completion_cost
    
    def _convert_messages(self, messages: List[ChatMessage]) -> List[dict]:
        """转换消息为 OpenAI 格式"""
        openai_messages = []
        for msg in messages:
            openai_msg = {
                "role": msg.role.value,
                "content": msg.content,
            }
            if msg.name:
                openai_msg["name"] = msg.name
            if msg.function_call:
                openai_msg["function_call"] = msg.function_call
            if msg.tool_calls:
                openai_msg["tool_calls"] = msg.tool_calls
            openai_messages.append(openai_msg)
        return openai_messages
    
    def _handle_error(self, error: Exception) -> Exception:
        """转换错误类型"""
        error_str = str(error).lower()
        
        if "rate limit" in error_str or "429" in error_str:
            return ModelProviderRateLimitError(f"OpenAI rate limit exceeded: {error}")
        
        if "api key" in error_str or "authentication" in error_str:
            return ModelProviderAuthenticationError(f"OpenAI authentication failed: {error}")
        
        return ModelProviderError(f"OpenAI error: {error}")
