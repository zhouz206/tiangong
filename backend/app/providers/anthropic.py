"""
Anthropic Provider — Anthropic 模型提供商
"""
import os
from typing import List
import asyncio

from .base import ModelProvider, ModelMessage, ModelResponse, ModelConfig, ModelUsage, ModelRole


class AnthropicProvider(ModelProvider):
    """
    Anthropic 模型提供商
    
    支持模型:
    - Claude-3.5-Sonnet
    - Claude-3-Haiku
    - Claude-3-Opus
    """
    
    # 模型价格（每 1K tokens，美元）
    PRICING = {
        "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "claude-3-opus": {"input": 0.015, "output": 0.075}
    }
    
    @property
    def name(self) -> str:
        return "anthropic"
    
    def get_available_models(self) -> List[str]:
        return ["claude-3-5-sonnet", "claude-3-haiku", "claude-3-opus"]
    
    async def chat(self, messages: List[ModelMessage], config: ModelConfig) -> ModelResponse:
        """
        Anthropic 聊天补全
        
        Args:
            messages: 消息列表
            config: 模型配置
            
        Returns:
            ModelResponse: 模型响应
        """
        api_key = config.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key not provided")
        
        # 模拟响应
        await asyncio.sleep(0.1)
        
        # Anthropic 格式：system 消息分离
        system_messages = [m for m in messages if m.role == ModelRole.SYSTEM]
        user_messages = [m for m in messages if m.role != ModelRole.SYSTEM]
        
        system_content = "\n".join([m.content for m in system_messages]) if system_messages else ""
        
        # 模拟响应
        response_content = f"[Anthropic {config.model_name}] 收到 {len(user_messages)} 条用户消息"
        if system_content:
            response_content += f"，系统提示：{system_content[:50]}..."
        
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
        
        Anthropic 不提供嵌入服务，抛出异常
        """
        raise NotImplementedError("Anthropic does not support embeddings")
    
    def estimate_cost(self, usage, model: str) -> float:
        """估算成本"""
        if model not in self.PRICING:
            return 0.0
        
        pricing = self.PRICING[model]
        input_cost = (usage.prompt_tokens / 1000) * pricing["input"]
        output_cost = (usage.completion_tokens / 1000) * pricing["output"]
        
        return input_cost + output_cost
