"""
SmartRouter — 智能路由
"""
import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

from .base import ModelProvider, ModelMessage, ModelResponse, ModelConfig, ModelUsage


class RouterStrategy(str, Enum):
    """路由策略"""
    COST_FIRST = "cost_first"      # 成本优先
    PERFORMANCE_FIRST = "performance_first"  # 性能优先
    BALANCED = "balanced"          # 平衡模式
    OFFLINE_FIRST = "offline_first"  # 离线优先


@dataclass
class ModelStats:
    """模型统计"""
    request_count: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_latency: float = 0.0
    success_rate: float = 1.0
    last_error: Optional[str] = None


@dataclass
class FallbackConfig:
    """降级配置"""
    max_retries: int = 3
    fallback_models: List[str] = field(default_factory=list)
    timeout_seconds: int = 30


class SmartRouter:
    """
    智能路由器
    
    功能:
    - 多提供商统一管理
    - 智能路由（成本/性能/平衡）
    - 自动降级和重试
    - 统计追踪
    """
    
    def __init__(self, strategy: RouterStrategy = RouterStrategy.BALANCED):
        self.strategy = strategy
        self._providers: Dict[str, ModelProvider] = {}
        self._stats: Dict[str, ModelStats] = {}
        self._fallback_config = FallbackConfig()
    
    def register_provider(self, name: str, provider: ModelProvider) -> None:
        """注册提供商"""
        self._providers[name] = provider
        self._stats[name] = ModelStats()
    
    def unregister_provider(self, name: str) -> bool:
        """注销提供商"""
        if name in self._providers:
            del self._providers[name]
            del self._stats[name]
            return True
        return False
    
    def get_available_models(self) -> List[str]:
        """获取所有可用模型"""
        models = []
        for provider in self._providers.values():
            models.extend(provider.get_available_models())
        return models
    
    async def chat(self, messages: List[ModelMessage], config: ModelConfig) -> ModelResponse:
        """
        智能路由聊天请求
        
        Args:
            messages: 消息列表
            config: 模型配置
            
        Returns:
            ModelResponse: 模型响应
        """
        # 选择最佳提供商
        provider_name = self._select_provider(config.model_name)
        
        # 尝试请求（带降级）
        for attempt in range(self._fallback_config.max_retries):
            try:
                response = await self._call_provider(provider_name, messages, config)
                self._update_stats(provider_name, response.usage, success=True)
                return response
            except Exception as e:
                self._update_stats(provider_name, ModelUsage(), success=False, error=str(e))
                
                # 降级到备用模型
                if attempt < self._fallback_config.max_retries - 1:
                    provider_name = self._get_fallback_provider(provider_name)
        
        # 所有尝试失败
        raise RuntimeError(f"All providers failed after {self._fallback_config.max_retries} attempts")
    
    def _select_provider(self, model_name: str) -> str:
        """根据策略选择提供商"""
        if self.strategy == RouterStrategy.COST_FIRST:
            return self._select_cheapest_provider()
        elif self.strategy == RouterStrategy.PERFORMANCE_FIRST:
            return self._select_fastest_provider()
        elif self.strategy == RouterStrategy.OFFLINE_FIRST:
            return self._select_offline_provider()
        else:  # BALANCED
            return self._select_balanced_provider()
    
    def _select_cheapest_provider(self) -> str:
        """选择最便宜的提供商"""
        if not self._providers:
            raise ValueError("No providers registered")
        # 简化实现：返回第一个
        return list(self._providers.keys())[0]
    
    def _select_fastest_provider(self) -> str:
        """选择最快的提供商"""
        if not self._stats:
            return list(self._providers.keys())[0]
        
        fastest = min(self._stats.items(), key=lambda x: x[1].avg_latency)
        return fastest[0]
    
    def _select_offline_provider(self) -> str:
        """选择离线提供商（Ollama）"""
        if "ollama" in self._providers:
            return "ollama"
        return list(self._providers.keys())[0]
    
    def _select_balanced_provider(self) -> str:
        """选择平衡的提供商（考虑成功率和延迟）"""
        if not self._stats:
            return list(self._providers.keys())[0]
        
        # 计算综合得分（成功率 * 0.7 + (1 - 归一化延迟) * 0.3）
        best_score = 0
        best_provider = list(self._providers.keys())[0]
        
        for name, stats in self._stats.items():
            score = stats.success_rate * 0.7 + (1 - min(stats.avg_latency / 10, 1)) * 0.3
            if score > best_score:
                best_score = score
                best_provider = name
        
        return best_provider
    
    def _get_fallback_provider(self, current: str) -> str:
        """获取降级提供商"""
        available = [name for name in self._providers.keys() if name != current]
        if available:
            return available[0]
        return current
    
    async def _call_provider(self, name: str, messages: List[ModelMessage], config: ModelConfig) -> ModelResponse:
        """调用提供商"""
        if name not in self._providers:
            raise ValueError(f"Provider '{name}' not registered")
        
        provider = self._providers[name]
        return await provider.chat(messages, config)
    
    def _update_stats(self, provider_name: str, usage: ModelUsage, success: bool, error: str = None) -> None:
        """更新统计"""
        if provider_name not in self._stats:
            self._stats[provider_name] = ModelStats()
        
        stats = self._stats[provider_name]
        stats.request_count += 1
        stats.total_tokens += usage.total_tokens
        
        # 更新成功率（指数移动平均）
        alpha = 0.1
        stats.success_rate = stats.success_rate * (1 - alpha) + (1.0 if success else 0.0) * alpha
        
        if error:
            stats.last_error = error
    
    def get_stats(self, provider_name: str = None) -> Dict[str, ModelStats]:
        """获取统计信息"""
        if provider_name:
            return self._stats.get(provider_name, ModelStats())
        return self._stats
