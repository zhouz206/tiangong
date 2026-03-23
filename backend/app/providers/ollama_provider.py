"""
Ollama 本地模型提供商实现

支持本地运行的 Llama、Qwen、Mistral 等开源模型。
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
    ModelProviderUnavailableError,
)


class OllamaProvider(ModelProvider):
    """
    Ollama 本地模型提供商
    
    使用示例:
        provider = OllamaProvider(host="http://localhost:11434")
        await provider.initialize()
        response = await provider.chat(
            messages=[ChatMessage(role="user", content="Hello")],
            config=ModelConfig(model_name="llama3.2")
        )
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        model: Optional[str] = None,
    ):
        super().__init__("ollama")
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.default_model = model or "llama3.2"
        
        self._initialized = False
        self._session: Optional[Any] = None
        self._available_models: List[str] = []
    
    async def initialize(self) -> None:
        """初始化 Ollama 客户端"""
        if self._initialized:
            return
        
        try:
            # 使用 aiohttp 进行异步请求
            import aiohttp
            
            self._session = aiohttp.ClientSession()
            
            # 验证 Ollama 服务是否可用
            async with self._session.get(f"{self.host}/api/tags") as response:
                if response.status != 200:
                    raise ModelProviderUnavailableError(
                        f"Ollama service not available at {self.host}"
                    )
                result = await response.json()
                self._available_models = [m["name"] for m in result.get("models", [])]
            
            self._initialized = True
            
        except ImportError:
            raise ModelProviderUnavailableError(
                "aiohttp package not installed. Run: pip install aiohttp"
            )
        except Exception as e:
            raise ModelProviderUnavailableError(f"Ollama service unavailable: {e}")
    
    async def shutdown(self) -> None:
        """关闭 Ollama 客户端"""
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
        
        config = config or ModelConfig(model_name=self.default_model)
        self.validate_config(config)
        
        # 转换消息格式
        ollama_messages = self._convert_messages(messages)
        
        payload = {
            "model": config.model_name,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens,
                "top_p": config.top_p,
            }
        }
        
        if config.stop_sequences:
            payload["options"]["stop"] = config.stop_sequences
        
        try:
            async with self._session.post(
                f"{self.host}/api/chat",
                json=payload,
            ) as response:
                result = await response.json()
                
                if response.status != 200:
                    raise ModelProviderError(f"Ollama error: {result}")
                
                # 提取响应
                message = result.get("message", {})
                content = message.get("content", "")
                
                # 提取使用量
                usage = None
                if "prompt_eval_count" in result or "eval_count" in result:
                    usage = ModelUsage(
                        prompt_tokens=result.get("prompt_eval_count", 0),
                        completion_tokens=result.get("eval_count", 0),
                        total_tokens=(
                            result.get("prompt_eval_count", 0) + 
                            result.get("eval_count", 0)
                        ),
                    )
                
                return ModelResponse(
                    content=content,
                    model=config.model_name,
                    usage=usage,
                    finish_reason="stop" if result.get("done", False) else None,
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
        
        config = config or ModelConfig(model_name=self.default_model)
        self.validate_config(config)
        
        # 转换消息格式
        ollama_messages = self._convert_messages(messages)
        
        payload = {
            "model": config.model_name,
            "messages": ollama_messages,
            "stream": True,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens,
                "top_p": config.top_p,
            }
        }
        
        try:
            async with self._session.post(
                f"{self.host}/api/chat",
                json=payload,
            ) as response:
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line:
                        try:
                            import json
                            result = json.loads(line)
                            message = result.get("message", {})
                            content = message.get("content", "")
                            if content:
                                yield content
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
        
        model = model or "nomic-embed-text"
        
        payload = {
            "model": model,
            "prompt": text,
        }
        
        try:
            async with self._session.post(
                f"{self.host}/api/embeddings",
                json=payload,
            ) as response:
                result = await response.json()
                
                if response.status != 200:
                    raise ModelProviderError(f"Ollama error: {result}")
                
                return result.get("embedding", [])
                
        except Exception as e:
            raise self._handle_error(e)
    
    def get_capabilities(self) -> List[ModelCapability]:
        """获取支持的能力"""
        return [
            ModelCapability.CHAT,
            ModelCapability.COMPLETION,
            ModelCapability.EMBEDDING,
        ]
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return self._available_models
    
    def estimate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str,
    ) -> float:
        """
        估算成本
        
        Ollama 是本地模型，成本为 0（不计 API 费用）
        """
        return 0.0
    
    def _convert_messages(self, messages: List[ChatMessage]) -> List[dict]:
        """转换消息为 Ollama 格式"""
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg.role.value,
                "content": msg.content,
            })
        return ollama_messages
    
    def _handle_error(self, error: Exception) -> Exception:
        """转换错误类型"""
        if isinstance(error, ModelProviderError):
            return error
        
        return ModelProviderError(f"Ollama error: {error}")
    
    async def pull_model(self, model_name: str) -> bool:
        """
        拉取模型到本地
        
        Args:
            model_name: 模型名称
            
        Returns:
            是否成功
        """
        if not self._initialized:
            await self.initialize()
        
        payload = {
            "name": model_name,
            "stream": False,
        }
        
        try:
            async with self._session.post(
                f"{self.host}/api/pull",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=600),  # 10 分钟超时
            ) as response:
                return response.status == 200
        except Exception:
            return False
    
    async def list_local_models(self) -> List[dict]:
        """列出本地已下载的模型"""
        if not self._initialized:
            await self.initialize()
        
        try:
            async with self._session.get(f"{self.host}/api/tags") as response:
                result = await response.json()
                return result.get("models", [])
        except Exception:
            return []
