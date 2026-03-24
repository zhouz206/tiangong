"""
Qwen Provider — 阿里云通义千问模型提供商
"""
import os
from typing import List
import asyncio

from .base import ModelProvider, ModelMessage, ModelResponse, ModelConfig, ModelUsage, ModelRole


class QwenProvider(ModelProvider):
    """
    Qwen (通义千问) 模型提供商
    
    支持模型:
    - Qwen-Max
    - Qwen-Plus
    - Qwen-Turbo
    """
    
    # 模型价格（每 1K tokens，人民币）
    PRICING = {
        "qwen-max": {"input": 0.04, "output": 0.12},
        "qwen-plus": {"input": 0.008, "output": 0.02},
        "qwen-turbo": {"input": 0.002, "output": 0.006}
    }
    
    @property
    def name(self) -> str:
        return "qwen"
    
    def get_available_models(self) -> List[str]:
        return ["qwen-max", "qwen-plus", "qwen-turbo"]
    
    async def chat(self, messages: List[ModelMessage], config: ModelConfig) -> ModelResponse:
        """
        Qwen 聊天补全
        
        Args:
            messages: 消息列表
            config: 模型配置
            
        Returns:
            ModelResponse: 模型响应
        """
        api_key = config.api_key or os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("DashScope API key not provided")
        
        # 模拟响应
        await asyncio.sleep(0.1)
        
        # 模拟响应
        response_content = f"[Qwen {config.model_name}] 收到 {len(messages)} 条消息"
        
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
        生成嵌入向量（通义千问支持）
        
        Args:
            text: 输入文本
            config: 模型配置
            
        Returns:
            List[float]: 嵌入向量
        """
        api_key = config.api_key or os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("DashScope API key not provided")
        
        # 模拟响应
        await asyncio.sleep(0.05)
        
        # 返回 1536 维模拟向量
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
        """估算成本（人民币）"""
        if model not in self.PRICING:
            return 0.0
        
        pricing = self.PRICING[model]
        input_cost = (usage.prompt_tokens / 1000) * pricing["input"]
        output_cost = (usage.completion_tokens / 1000) * pricing["output"]
        
        return input_cost + output_cost
