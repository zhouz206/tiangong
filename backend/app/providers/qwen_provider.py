"""
Qwen (通义千问) 模型提供商实现

支持 Qwen-Max, Qwen-Plus, Qwen-Turbo 等模型。
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


# Qwen 模型成本（每 1K tokens，人民币）
QWEN_PRICES = {
    "qwen-max": {"prompt": 0.04, "completion": 0.12},
    "qwen-max-longcontext": {"prompt": 0.04, "completion": 0.12},
    "qwen-plus": {"prompt": 0.008, "completion": 0.02},
    "qwen-turbo": {"prompt": 0.002, "completion": 0.006},
    "qwen-long": {"prompt": 0.0005, "completion": 0.002},
    "qwen-vl-max": {"prompt": 0.02, "completion": 0.06},
    "qwen-vl-plus": {"prompt": 0.008, "completion": 0.02},
}


class QwenProvider(ModelProvider):
    """
    Qwen (通义千问) 模型提供商
    
    使用示例:
        provider = QwenProvider(api_key="sk-...")
        await provider.initialize()
        response = await provider.chat(
            messages=[ChatMessage(role="user", content="Hello")],
            config=ModelConfig(model_name="qwen-plus")
        )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        super().__init__("qwen")
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        # DashScope API 基础 URL
        self.base_url = base_url or "https://dashscope.aliyuncs.com/api/v1"
        
        self._initialized = False
        self._session: Optional[Any] = None
    
    async def initialize(self) -> None:
        """初始化 Qwen 客户端"""
        if self._initialized:
            return
        
        if not self.api_key:
            raise ModelProviderAuthenticationError(
                "DashScope API key is required. Set DASHSCOPE_API_KEY env var or pass api_key parameter."
            )
        
        try:
            # 使用 aiohttp 进行异步请求
            import aiohttp
            
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )
            
            self._initialized = True
            
        except ImportError:
            raise ModelProviderUnavailableError(
                "aiohttp package not installed. Run: pip install aiohttp"
            )
        except Exception as e:
            if "api key" in str(e).lower() or "authentication" in str(e).lower():
                raise ModelProviderAuthenticationError(f"DashScope authentication failed: {e}")
            raise ModelProviderUnavailableError(f"DashScope service unavailable: {e}")
    
    async def shutdown(self) -> None:
        """关闭 Qwen 客户端"""
        if self._session:
            await self._session.close()
            self._session = None
        self._initialized = False
    
    async def chat(
        self,
        messages: List[ChatMessage],
        config: Optional[ModelConfig] = None,
    ) -> ModelResponse:
        """发送聊天请求"""
        if not self._initialized:
            await self.initialize()
        
        config = config or ModelConfig(model_name="qwen-plus")
        self.validate_config(config)
        
        # 转换消息格式
        qwen_messages = self._convert_messages(messages)
        
        payload = {
            "model": config.model_name,
            "input": {
                "messages": qwen_messages
            },
            "parameters": {
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
                "top_p": config.top_p,
                "stop": config.stop_sequences,
            }
        }
        
        try:
            async with self._session.post(
                f"{self.base_url}/services/aigc/text-generation/generation",
                json=payload,
            ) as response:
                result = await response.json()
                
                if response.status != 200:
                    raise self._handle_api_error(result)
                
                # 提取响应
                output = result.get("output", {})
                content = output.get("text", "")
                choices = output.get("choices", [])
                finish_reason = choices[0].get("finish_reason") if choices else None
                
                # 提取使用量
                usage = None
                if "usage" in result:
                    usage_data = result["usage"]
                    usage = ModelUsage(
                        prompt_tokens=usage_data.get("input_tokens", 0),
                        completion_tokens=usage_data.get("output_tokens", 0),
                        total_tokens=usage_data.get("total_tokens", 0),
                    )
                
                return ModelResponse(
                    content=content,
                    model=config.model_name,
                    usage=usage,
                    finish_reason=finish_reason,
                    raw_response=result,
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
        
        config = config or ModelConfig(model_name="qwen-plus")
        config.stream = True
        self.validate_config(config)
        
        # 转换消息格式
        qwen_messages = self._convert_messages(messages)
        
        payload = {
            "model": config.model_name,
            "input": {
                "messages": qwen_messages
            },
            "parameters": {
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
                "top_p": config.top_p,
                "stop": config.stop_sequences,
            },
            "stream": True,
        }
        
        try:
            async with self._session.post(
                f"{self.base_url}/services/aigc/text-generation/generation",
                json=payload,
            ) as response:
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data:'):
                        data = line[5:].strip()
                        if data == '[DONE]':
                            break
                        try:
                            import json
                            result = json.loads(data)
                            output = result.get("output", {})
                            text = output.get("text", "")
                            if text:
                                yield text
                        except:
                            continue
                            
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
        
        model = model or "text-embedding-v2"
        
        payload = {
            "model": model,
            "input": {
                "texts": [text]
            },
            "parameters": {
                "text_type": "query"
            }
        }
        
        try:
            async with self._session.post(
                f"{self.base_url}/services/embeddings/text-embedding/text-embedding",
                json=payload,
            ) as response:
                result = await response.json()
                
                if response.status != 200:
                    raise self._handle_api_error(result)
                
                # 提取嵌入向量
                output = result.get("output", {})
                embeddings = output.get("embeddings", [])
                if embeddings:
                    return embeddings[0].get("embedding", [])
                return []
                
        except Exception as e:
            raise self._handle_error(e)
    
    def get_capabilities(self) -> List[ModelCapability]:
        """获取支持的能力"""
        return [
            ModelCapability.CHAT,
            ModelCapability.COMPLETION,
            ModelCapability.EMBEDDING,
            ModelCapability.VISION,
        ]
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return list(QWEN_PRICES.keys())
    
    def estimate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str,
    ) -> float:
        """估算成本（人民币）"""
        pricing = QWEN_PRICES.get(model, QWEN_PRICES["qwen-turbo"])
        prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing["completion"]
        return prompt_cost + completion_cost
    
    def _convert_messages(self, messages: List[ChatMessage]) -> List[dict]:
        """转换消息为 Qwen 格式"""
        qwen_messages = []
        for msg in messages:
            qwen_messages.append({
                "role": msg.role.value,
                "content": msg.content,
            })
        return qwen_messages
    
    def _handle_api_error(self, result: dict) -> Exception:
        """处理 API 错误响应"""
        code = result.get("code", "")
        message = result.get("message", "Unknown error")
        
        if "RateLimit" in code or "429" in str(code):
            return ModelProviderRateLimitError(f"DashScope rate limit exceeded: {message}")
        
        if "InvalidApiKey" in code or "Unauthorized" in str(code):
            return ModelProviderAuthenticationError(f"DashScope authentication failed: {message}")
        
        return ModelProviderError(f"DashScope error [{code}]: {message}")
    
    def _handle_error(self, error: Exception) -> Exception:
        """转换错误类型"""
        if isinstance(error, ModelProviderError):
            return error
        
        error_str = str(error).lower()
        
        if "rate limit" in error_str or "429" in error_str:
            return ModelProviderRateLimitError(f"DashScope rate limit exceeded: {error}")
        
        if "api key" in error_str or "authentication" in error_str:
            return ModelProviderAuthenticationError(f"DashScope authentication failed: {error}")
        
        return ModelProviderError(f"DashScope error: {error}")
