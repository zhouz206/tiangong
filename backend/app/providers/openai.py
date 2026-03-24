"""
OpenAI Provider — OpenAI 模型提供商
"""
import os
from typing import List
import asyncio

from .base import ModelProvider, ModelMessage, ModelResponse, ModelConfig, ModelUsage, ModelRole


class OpenAIProvider(ModelProvider):
    """
    OpenAI 模型提供商
    
    支持模型:
    - GPT-4o
    - GPT-4o-mini
    - GPT-3.5-turbo
    """
    
    # 模型价格（每 1K tokens，美元）
    PRICING = {
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
    }
    
    @property
    def name(self) -> str:
        return "openai"
    
    def get_available_models(self) -> List[str]:
        return ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
    
    async def chat(self, messages: List[ModelMessage], config: ModelConfig) -> ModelResponse:
        """
        OpenAI 聊天补全
        
        Args:
            messages: 消息列表
            config: 模型配置
            
        Returns:
            ModelResponse: 模型响应
        """
        api_key = config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not provided")
        
        # 模拟响应（实际实现需要调用 OpenAI API）
        await asyncio.sleep(0.1)  # 模拟网络延迟
        
        # 构建请求消息
        openai_messages = [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]
        
        # 模拟响应
        response_content = f"[OpenAI {config.model_name}] 收到 {len(messages)} 条消息"
        
        return ModelResponse(
            content=response_content,
            model=config.model_name,
            usage=ModelUsage(
                prompt_tokens=sum(len(msg.content.split()) for msg in messages),
                completion_tokens=len(response_content.split()),
                total_tokens=sum(len(msg.content.split()) for msg in messages) + len(response_content.split())
            )
        )
    
    async def embed(self, text: str, config: ModelConfig) -> List[float]:
        """
        生成嵌入向量
        
        Args:
            text: 输入文本
            config: 模型配置
            
        Returns:
            List[float]: 嵌入向量
        """
        api_key = config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not provided")
        
        # 模拟嵌入（实际实现需要调用 OpenAI Embedding API）
        await asyncio.sleep(0.05)
        
        # 返回 1536 维模拟向量（text-embedding-ada-002 的维度）
        import hashlib
        hash_bytes = hashlib.sha256(text.encode()).digest()
        base_values = [int(b) / 255.0 for b in hash_bytes]
        vector = (base_values * 100)[:1536]
        
        # 归一化
        norm = sum(v*v for v in vector) ** 0.5
        if norm == 0:
            norm = 1
        return [v / norm for v in vector]
    
    def estimate_cost(self, usage, model: str) -> float:
        """估算成本"""
        if model not in self.PRICING:
            return 0.0
        
        pricing = self.PRICING[model]
        input_cost = (usage.prompt_tokens / 1000) * pricing["input"]
        output_cost = (usage.completion_tokens / 1000) * pricing["output"]
        
        return input_cost + output_cost
