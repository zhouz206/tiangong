"""
模型提供商单元测试
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.providers.base import (
    ModelProvider,
    ModelConfig,
    ModelResponse,
    ModelUsage,
    ChatMessage,
    ModelCapability,
    ModelRole,
    count_tokens,
)
from app.providers.router import (
    SmartRouter,
    RoutingStrategy,
    ModelStats,
)


class TestModelConfig:
    """测试模型配置"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = ModelConfig(model_name="gpt-4")
        assert config.model_name == "gpt-4"
        assert config.temperature == 0.7
        assert config.max_tokens == 2048
        assert config.stream is False
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = ModelConfig(
            model_name="claude-3",
            temperature=0.5,
            max_tokens=1024,
            top_p=0.9,
        )
        assert config.temperature == 0.5
        assert config.max_tokens == 1024
        assert config.top_p == 0.9


class TestChatMessage:
    """测试聊天消息"""
    
    def test_create_message(self):
        """测试创建消息"""
        msg = ChatMessage(
            role=ModelRole.USER,
            content="Hello",
        )
        assert msg.role == ModelRole.USER
        assert msg.content == "Hello"
    
    def test_message_with_metadata(self):
        """测试带元数据的消息"""
        msg = ChatMessage(
            role=ModelRole.ASSISTANT,
            content="Hi there",
            name="assistant",
        )
        assert msg.name == "assistant"


class TestModelUsage:
    """测试模型使用量"""
    
    def test_usage_calculation(self):
        """测试使用量计算"""
        usage = ModelUsage(
            prompt_tokens=100,
            completion_tokens=50,
        )
        assert usage.total_tokens == 150
    
    def test_usage_explicit_total(self):
        """测试显式指定总 token 数"""
        usage = ModelUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=200,
        )
        assert usage.total_tokens == 200


class TestModelResponse:
    """测试模型响应"""
    
    def test_create_response(self):
        """测试创建响应"""
        response = ModelResponse(
            content="Hello",
            model="gpt-4",
        )
        assert response.content == "Hello"
        assert response.model == "gpt-4"
    
    def test_response_with_usage(self):
        """测试带使用量的响应"""
        response = ModelResponse(
            content="Hello",
            model="gpt-4",
            usage=ModelUsage(prompt_tokens=10, completion_tokens=5),
        )
        assert response.usage.total_tokens == 15


class TestCountTokens:
    """测试 token 计数"""
    
    def test_english_text(self):
        """测试英文文本"""
        text = "Hello world"
        tokens = count_tokens(text)
        assert tokens > 0
    
    def test_chinese_text(self):
        """测试中文文本"""
        text = "你好世界"
        tokens = count_tokens(text)
        assert tokens > 0
    
    def test_mixed_text(self):
        """测试混合文本"""
        text = "Hello 世界"
        tokens = count_tokens(text)
        assert tokens > 0


class TestSmartRouter:
    """测试智能路由器"""
    
    @pytest.fixture
    def router(self):
        """创建路由器实例"""
        return SmartRouter(strategy=RoutingStrategy.COST_FIRST)
    
    def test_add_provider(self, router):
        """测试添加提供商"""
        mock_provider = MagicMock()
        mock_provider.provider_name = "mock"
        mock_provider.get_available_models.return_value = ["model-1", "model-2"]
        mock_provider._initialized = True
        
        router.add_provider("mock", mock_provider, is_offline=True)
        
        assert "mock" in router._providers
        assert "mock/model-1" in router._stats
        assert "mock/model-2" in router._stats
    
    def test_set_fallback(self, router):
        """测试设置降级模型"""
        router.set_fallback("openai/gpt-4", ["openai/gpt-3.5-turbo", "ollama/llama3.2"])
        
        assert "openai/gpt-4" in router._fallbacks
        assert router._fallbacks["openai/gpt-4"] == ["openai/gpt-3.5-turbo", "ollama/llama3.2"]
    
    def test_parse_model_name_with_provider(self, router):
        """测试解析带提供商的模型名称"""
        provider_name, model_name = router._parse_model_name("openai/gpt-4")
        assert provider_name == "openai"
        assert model_name == "gpt-4"
    
    def test_parse_model_name_without_provider(self, router):
        """测试解析不带提供商的模型名称"""
        # 添加一个模拟提供商
        mock_provider = MagicMock()
        mock_provider.provider_name = "default"
        mock_provider.get_available_models.return_value = ["model-1"]
        mock_provider._initialized = True
        router.add_provider("default", mock_provider)
        
        provider_name, model_name = router._parse_model_name("gpt-4")
        assert provider_name == "default"
        assert model_name == "gpt-4"


class TestRoutingStrategy:
    """测试路由策略"""
    
    @pytest.fixture
    def router_with_providers(self):
        """创建带提供商的路由器"""
        router = SmartRouter(strategy=RoutingStrategy.COST_FIRST)
        
        # 添加模拟提供商
        mock_openai = MagicMock()
        mock_openai.provider_name = "openai"
        mock_openai.get_available_models.return_value = ["gpt-4", "gpt-3.5-turbo"]
        mock_openai._initialized = True
        mock_openai.estimate_cost.side_effect = lambda p, c, m: 0.03 if m == "gpt-4" else 0.001
        
        mock_ollama = MagicMock()
        mock_ollama.provider_name = "ollama"
        mock_ollama.get_available_models.return_value = ["llama3.2"]
        mock_ollama._initialized = True
        mock_ollama.estimate_cost.return_value = 0.0
        
        router.add_provider("openai", mock_openai)
        router.add_provider("ollama", mock_ollama, is_offline=True)
        
        return router
    
    def test_cost_first_strategy(self, router_with_providers):
        """测试成本优先策略"""
        router = router_with_providers
        router.strategy = RoutingStrategy.COST_FIRST
        
        messages = [ChatMessage(role=ModelRole.USER, content="Hello")]
        config = ModelConfig(model_name="auto")
        
        decision = router._route(messages, config)
        
        # 成本优先应该选择 Ollama（免费）
        assert decision.provider.provider_name == "ollama"
    
    def test_offline_first_strategy(self, router_with_providers):
        """测试离线优先策略"""
        router = router_with_providers
        router.strategy = RoutingStrategy.OFFLINE_FIRST
        
        messages = [ChatMessage(role=ModelRole.USER, content="Hello")]
        config = ModelConfig(model_name="auto")
        
        decision = router._route(messages, config)
        
        # 离线优先应该选择 Ollama
        assert decision.provider.provider_name == "ollama"
        assert "Offline" in decision.reason
    
    def test_performance_first_strategy(self, router_with_providers):
        """测试性能优先策略"""
        router = router_with_providers
        router.strategy = RoutingStrategy.PERFORMANCE_FIRST
        
        # 设置不同的延迟
        router._stats["openai/gpt-4"].avg_latency_ms = 500
        router._stats["ollama/llama3.2"].avg_latency_ms = 1000
        
        messages = [ChatMessage(role=ModelRole.USER, content="Hello")]
        config = ModelConfig(model_name="auto")
        
        decision = router._route(messages, config)
        
        # 性能优先应该选择延迟更低的
        assert decision.provider.provider_name == "openai"


class TestModelStats:
    """测试模型统计"""
    
    def test_record_successful_request(self):
        """测试记录成功请求"""
        stats = ModelStats(
            model_name="gpt-4",
            provider_name="openai",
        )
        
        stats.record_request(
            latency_ms=500,
            success=True,
            prompt_tokens=100,
            completion_tokens=50,
            cost=0.005,
        )
        
        assert stats.total_requests == 1
        assert stats.total_tokens == 150
        assert stats.total_cost == 0.005
        assert stats.avg_latency_ms == 500
        assert stats.success_rate == 1.0
    
    def test_record_failed_request(self):
        """测试记录失败请求"""
        stats = ModelStats(
            model_name="gpt-4",
            provider_name="openai",
        )
        
        stats.record_request(
            latency_ms=0,
            success=False,
            prompt_tokens=0,
            completion_tokens=0,
            cost=0.0,
        )
        
        assert stats.success_rate < 1.0
    
    def test_exponential_moving_average(self):
        """测试指数移动平均"""
        stats = ModelStats(
            model_name="gpt-4",
            provider_name="openai",
        )
        
        # 记录多次请求
        stats.record_request(1000, True, 100, 50, 0.01)
        stats.record_request(200, True, 100, 50, 0.01)
        
        # 第二次延迟应该影响平均值
        assert stats.avg_latency_ms < 1000
        assert stats.avg_latency_ms > 200
