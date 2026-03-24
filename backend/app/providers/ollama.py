"""
Ollama Provider — 本地 Ollama 模型提供商
"""
import os
from typing import List
import asyncio

from .base import ModelProvider, ModelMessage, ModelResponse, ModelConfig, ModelUsage, ModelRole


class OllamaProvider(ModelProvider):
    """
    Ollama 本地模型提供商
    
    支持模型:
    - Llama 3
    - Qwen 2.5
    - Mistral
    - 等任何 Ollama 支持的模型
    """
    
    @property
    def name(self) -> str:
        return "ollama"
    
    def get_available_models(self) -> List[str]:
        # 实际实现需要调用 Ollama API 获取本地模型列表
        return ["llama3", "qwen2.5", "mistral", "gemma"]
    
    async def chat(self, messages: List[ModelMessage], config: ModelConfig) -> ModelResponse:
        """
        Ollama 聊天补全
        
        Args:
            messages: 消息列表
            config: 模型配置
            
        Returns:
            ModelResponse: 模型响应
        """
        base_url = config.base_url or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        
        # 模拟响应
        await asyncio.sleep(0.1)
        
        # 模拟响应
        response_content = f"[Ollama {config.model_name}] 本地模型收到 {len(messages)} 条消息"
        
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
        生成嵌入向量（Ollama 支持 nomic-embed-text 等嵌入模型）
        
        Args:
            text: 输入文本
            config: 模型配置
            
        Returns:
            List[float]: 嵌入向量
        """
        base_url = config.base_url or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        
        # 模拟响应
        await asyncio.sleep(0.05)
        
        # 返回 768 维模拟向量（nomic-embed-text 的维度）
        import hashlib
        hash_bytes = hashlib.sha256(text.encode()).digest()
        base_values = [int(b) / 255.0 for b in hash_bytes]
        vector = (base_values * 50)[:768]
        
        # 归一化
        norm = sum(v*v for v in vector) ** 0.5
        if norm == 0:
            norm = 1
        return [v / norm for v in vector]
    
    def estimate_cost(self, usage, model: str) -> float:
        """本地模型，零成本"""
        return 0.0
    
    async def pull_model(self, model_name: str) -> bool:
        """
        拉取模型
        
        Args:
            model_name: 模型名称
            
        Returns:
            bool: 是否成功
        """
        # 实际实现需要调用 Ollama API
        await asyncio.sleep(0.5)
        return True
    
    async def list_local_models(self) -> List[str]:
        """
        列出本地模型
        
        Returns:
            List[str]: 模型列表
        """
        # 实际实现需要调用 Ollama API
        return self.get_available_models()
