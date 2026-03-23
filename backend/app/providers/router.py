"""
智能模型路由器

根据成本、延迟、可用性等因素智能选择最优模型提供商。
支持成本优先、性能优先、平衡等策略。
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, AsyncIterator
import asyncio
import time

from .base import (
    ModelProvider,
    ModelConfig,
    ModelResponse,
    ChatMessage,
    ModelCapability,
    ModelProviderError,
    ModelProviderRateLimitError,
    ModelProviderUnavailableError,
    count_tokens,
)


class RoutingStrategy(str, Enum):
    """路由策略枚举"""
    COST_FIRST = "cost_first"  # 成本优先
    PERFORMANCE_FIRST = "performance_first"  # 性能优先
    BALANCED = "balanced"  # 平衡模式
    OFFLINE_FIRST = "offline_first"  # 离线优先
    CUSTOM = "custom"  # 自定义策略


@dataclass
class ModelStats:
    """模型统计信息"""
    model_name: str
    provider_name: str
    
    # 成本统计
    avg_cost_per_1k_tokens: float = 0.0
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    
    # 性能统计
    avg_latency_ms: float = 0.0
    success_rate: float = 1.0
    last_error_time: Optional[float] = None
    
    # 可用性
    is_available: bool = True
    is_offline: bool = False
    
    def record_request(
        self,
        latency_ms: float,
        success: bool,
        prompt_tokens: int,
        completion_tokens: int,
        cost: float,
    ):
        """记录请求统计"""
        self.total_requests += 1
        self.total_tokens += prompt_tokens + completion_tokens
        self.total_cost += cost
        
        # 更新平均延迟（指数移动平均）
        alpha = 0.3
        self.avg_latency_ms = alpha * latency_ms + (1 - alpha) * self.avg_latency_ms
        
        # 更新成功率
        if success:
            self.success_rate = min(1.0, self.success_rate + 0.01)
        else:
            self.success_rate = max(0.0, self.success_rate - 0.1)
            self.last_error_time = time.time()
        
        # 更新平均成本
        if self.total_tokens > 0:
            self.avg_cost_per_1k_tokens = (self.total_cost / self.total_tokens) * 1000


@dataclass
class RoutingDecision:
    """路由决策结果"""
    provider: ModelProvider
    model_name: str
    strategy: RoutingStrategy
    reason: str
    estimated_cost: float
    estimated_latency_ms: float


class SmartRouter:
    """
    智能模型路由器
    
    功能:
    - 多模型提供商统一管理
    - 基于策略的智能路由
    - 成本估算和优化
    - 自动降级和重试
    - 性能统计和监控
    
    使用示例:
        router = SmartRouter(strategy=RoutingStrategy.COST_FIRST)
        router.add_provider("ollama", ollama_provider)
        router.add_provider("openai", openai_provider)
        
        response = await router.chat(
            messages=[ChatMessage(role="user", content="Hello")],
            config=ModelConfig(model_name="auto")  # 自动选择
        )
    """
    
    def __init__(
        self,
        strategy: RoutingStrategy = RoutingStrategy.COST_FIRST,
        max_retries: int = 3,
        timeout_seconds: float = 30.0,
    ):
        self.strategy = strategy
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        
        # 提供商注册表
        self._providers: Dict[str, ModelProvider] = {}
        
        # 模型统计
        self._stats: Dict[str, ModelStats] = {}
        
        # 降级映射：主模型 -> 降级模型列表
        self._fallbacks: Dict[str, List[str]] = {}
        
        # 自定义路由函数
        self._custom_router = None
    
    def add_provider(
        self,
        name: str,
        provider: ModelProvider,
        is_offline: bool = False,
    ) -> None:
        """
        添加模型提供商
        
        Args:
            name: 提供商名称
            provider: 提供商实例
            is_offline: 是否为离线模型
        """
        self._providers[name] = provider
        
        # 初始化统计
        for model in provider.get_available_models():
            key = f"{name}/{model}"
            self._stats[key] = ModelStats(
                model_name=model,
                provider_name=name,
                is_offline=is_offline,
            )
    
    def remove_provider(self, name: str) -> None:
        """移除模型提供商"""
        if name in self._providers:
            del self._providers[name]
    
    def set_fallback(self, primary_model: str, fallback_models: List[str]) -> None:
        """
        设置降级模型列表
        
        Args:
            primary_model: 主模型名称 (格式：provider/model)
            fallback_models: 降级模型列表
        """
        self._fallbacks[primary_model] = fallback_models
    
    def set_custom_router(self, router_func) -> None:
        """
        设置自定义路由函数
        
        Args:
            router_func: 函数签名 (messages, available_models) -> (provider_name, model_name)
        """
        self._custom_router = router_func
    
    def set_strategy(self, strategy: RoutingStrategy) -> None:
        """设置路由策略"""
        self.strategy = strategy
    
    async def chat(
        self,
        messages: List[ChatMessage],
        config: Optional[ModelConfig] = None,
        budget_limit: Optional[float] = None,
    ) -> ModelResponse:
        """
        智能路由聊天请求
        
        Args:
            messages: 消息历史
            config: 模型配置（model_name 可为 "auto" 自动选择）
            budget_limit: 预算限制（美元）
            
        Returns:
            模型响应
        """
        config = config or ModelConfig(model_name="auto")
        
        # 自动选择模型
        if config.model_name == "auto":
            decision = self._route(messages, config)
            provider = self._providers[decision.provider.provider_name]
            config.model_name = decision.model_name
        else:
            # 解析模型名称
            provider_name, model_name = self._parse_model_name(config.model_name)
            provider = self._providers.get(provider_name)
            if not provider:
                raise ModelProviderError(f"Unknown provider: {provider_name}")
            config.model_name = model_name
            decision = None
        
        # 检查预算
        if budget_limit is not None and decision:
            if decision.estimated_cost > budget_limit:
                # 寻找更便宜的替代方案
                config.model_name = self._find_cheaper_model(decision, budget_limit)
                provider_name, config.model_name = self._parse_model_name(config.model_name)
                provider = self._providers[provider_name]
        
        # 执行请求（带重试）
        last_error = None
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                response = await asyncio.wait_for(
                    provider.chat(messages, config),
                    timeout=self.timeout_seconds,
                )
                latency_ms = (time.time() - start_time) * 1000
                
                # 记录统计
                self._record_stats(
                    provider_name=provider.provider_name,
                    model_name=config.model_name,
                    latency_ms=latency_ms,
                    success=True,
                    prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                    completion_tokens=response.usage.completion_tokens if response.usage else 0,
                    cost=provider.estimate_cost(
                        response.usage.prompt_tokens if response.usage else 0,
                        response.usage.completion_tokens if response.usage else 0,
                        config.model_name,
                    ),
                )
                
                return response
                
            except ModelProviderRateLimitError as e:
                last_error = e
                # 限流时等待后重试
                await asyncio.sleep(2 ** attempt)
                
            except ModelProviderUnavailableError as e:
                last_error = e
                # 服务不可用时尝试降级
                config.model_name = self._get_fallback_model(f"{provider.provider_name}/{config.model_name}")
                if not config.model_name:
                    break
                provider_name, config.model_name = self._parse_model_name(config.model_name)
                provider = self._providers.get(provider_name)
                if not provider:
                    break
                    
            except Exception as e:
                last_error = e
                # 其他错误继续重试
                
        # 所有重试失败
        raise ModelProviderError(
            f"All retries failed. Last error: {last_error}"
        ) if last_error else ModelProviderError("Request failed")
    
    async def chat_stream(
        self,
        messages: List[ChatMessage],
        config: Optional[ModelConfig] = None,
    ) -> AsyncIterator[str]:
        """流式聊天（不支持自动重试）"""
        config = config or ModelConfig(model_name="auto")
        
        if config.model_name == "auto":
            decision = self._route(messages, config)
            provider = self._providers[decision.provider.provider_name]
            config.model_name = decision.model_name
        else:
            provider_name, model_name = self._parse_model_name(config.model_name)
            provider = self._providers.get(provider_name)
            if not provider:
                raise ModelProviderError(f"Unknown provider: {provider_name}")
            config.model_name = model_name
        
        async for chunk in provider.chat_stream(messages, config):
            yield chunk
    
    async def get_embedding(
        self,
        text: str,
        model: Optional[str] = None,
    ) -> List[float]:
        """获取嵌入向量（使用成本最低的可用模型）"""
        # 寻找支持 embedding 的最便宜模型
        best_provider = None
        best_model = None
        best_cost = float('inf')
        
        for name, provider in self._providers.items():
            if ModelCapability.EMBEDDING in provider.get_capabilities():
                for model_name in provider.get_available_models():
                    cost = provider.estimate_cost(100, 0, model_name)
                    if cost < best_cost:
                        best_cost = cost
                        best_provider = provider
                        best_model = model_name
        
        if not best_provider:
            raise ModelProviderError("No provider supports embeddings")
        
        return await best_provider.get_embedding(text, best_model)
    
    def get_stats(self) -> Dict[str, ModelStats]:
        """获取所有模型统计信息"""
        return dict(self._stats)
    
    def get_total_cost(self) -> float:
        """获取总成本"""
        return sum(s.total_cost for s in self._stats.values())
    
    def get_total_tokens(self) -> int:
        """获取总 token 数"""
        return sum(s.total_tokens for s in self._stats.values())
    
    def _route(self, messages: List[ChatMessage], config: ModelConfig) -> RoutingDecision:
        """
        路由决策
        
        根据策略选择最优模型
        """
        # 自定义路由
        if self.strategy == RoutingStrategy.CUSTOM and self._custom_router:
            provider_name, model_name = self._custom_router(
                messages,
                list(self._providers.keys())
            )
            provider = self._providers[provider_name]
            return RoutingDecision(
                provider=provider,
                model_name=model_name,
                strategy=self.strategy,
                reason="Custom router decision",
                estimated_cost=provider.estimate_cost(
                    count_tokens(str(messages)), 0, model_name
                ),
                estimated_latency_ms=self._stats.get(
                    f"{provider_name}/{model_name}",
                    ModelStats(model_name, provider_name)
                ).avg_latency_ms,
            )
        
        # 估算输入 token 数
        prompt_tokens = count_tokens(str(messages))
        
        # 收集所有可用模型
        candidates = []
        for name, provider in self._providers.items():
            # 检查提供商可用性
            if not provider._initialized:
                continue
            
            for model_name in provider.get_available_models():
                key = f"{name}/{model_name}"
                stats = self._stats.get(key)
                
                # 跳过不可用的模型
                if stats and not stats.is_available:
                    continue
                
                # 计算成本
                cost = provider.estimate_cost(prompt_tokens, 0, model_name)
                
                # 获取延迟
                latency = stats.avg_latency_ms if stats else 0
                
                candidates.append({
                    "provider": provider,
                    "provider_name": name,
                    "model_name": model_name,
                    "cost": cost,
                    "latency": latency,
                    "is_offline": stats.is_offline if stats else False,
                })
        
        if not candidates:
            raise ModelProviderError("No available models")
        
        # 根据策略排序
        if self.strategy == RoutingStrategy.COST_FIRST:
            # 成本优先：按成本升序
            candidates.sort(key=lambda x: x["cost"])
            winner = candidates[0]
            reason = "Lowest cost option"
            
        elif self.strategy == RoutingStrategy.PERFORMANCE_FIRST:
            # 性能优先：按延迟升序
            candidates.sort(key=lambda x: x["latency"] if x["latency"] > 0 else float('inf'))
            winner = candidates[0]
            reason = "Fastest response time"
            
        elif self.strategy == RoutingStrategy.OFFLINE_FIRST:
            # 离线优先：优先本地模型
            offline = [c for c in candidates if c["is_offline"]]
            if offline:
                offline.sort(key=lambda x: x["latency"] if x["latency"] > 0 else float('inf'))
                winner = offline[0]
                reason = "Offline model preferred"
            else:
                candidates.sort(key=lambda x: x["cost"])
                winner = candidates[0]
                reason = "No offline model available, fallback to lowest cost"
            
        else:  # BALANCED
            # 平衡模式：成本 * 0.6 + 延迟 * 0.4（归一化后）
            max_cost = max(c["cost"] for c in candidates) or 1
            max_latency = max(c["latency"] for c in candidates if c["latency"] > 0) or 1
            
            for c in candidates:
                norm_cost = c["cost"] / max_cost
                norm_latency = (c["latency"] / max_latency) if c["latency"] > 0 else 0
                c["score"] = norm_cost * 0.6 + norm_latency * 0.4
            
            candidates.sort(key=lambda x: x["score"])
            winner = candidates[0]
            reason = "Best balance of cost and performance"
        
        return RoutingDecision(
            provider=winner["provider"],
            model_name=winner["model_name"],
            strategy=self.strategy,
            reason=reason,
            estimated_cost=winner["cost"],
            estimated_latency_ms=winner["latency"],
        )
    
    def _parse_model_name(self, model_name: str) -> tuple[str, str]:
        """解析模型名称格式：provider/model"""
        if "/" in model_name:
            parts = model_name.split("/", 1)
            return parts[0], parts[1]
        # 默认使用第一个提供商
        provider_name = list(self._providers.keys())[0]
        return provider_name, model_name
    
    def _find_cheaper_model(self, decision: RoutingDecision, budget: float) -> str:
        """寻找更便宜的模型"""
        prompt_tokens = 1000  # 估算
        
        for name, provider in self._providers.items():
            for model_name in provider.get_available_models():
                cost = provider.estimate_cost(prompt_tokens, 0, model_name)
                if cost <= budget:
                    return f"{name}/{model_name}"
        
        # 没有更便宜的，返回最便宜的
        return f"{decision.provider.provider_name}/{decision.model_name}"
    
    def _get_fallback_model(self, model_key: str) -> Optional[str]:
        """获取降级模型"""
        fallbacks = self._fallbacks.get(model_key, [])
        if fallbacks:
            return fallbacks[0]
        
        # 默认降级到最便宜的离线模型
        for key, stats in self._stats.items():
            if stats.is_offline and stats.is_available:
                return key
        
        return None
    
    def _record_stats(
        self,
        provider_name: str,
        model_name: str,
        latency_ms: float,
        success: bool,
        prompt_tokens: int,
        completion_tokens: int,
        cost: float,
    ):
        """记录统计信息"""
        key = f"{provider_name}/{model_name}"
        if key not in self._stats:
            self._stats[key] = ModelStats(
                model_name=model_name,
                provider_name=provider_name,
            )
        
        self._stats[key].record_request(
            latency_ms=latency_ms,
            success=success,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost,
        )


# 全局路由器实例
_router: Optional[SmartRouter] = None


def get_router() -> SmartRouter:
    """获取全局路由器实例"""
    global _router
    if _router is None:
        _router = SmartRouter()
    return _router


def reset_router() -> None:
    """重置全局路由器"""
    global _router
    _router = None
