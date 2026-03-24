"""
Providers 测试
"""
import pytest
import asyncio
from app.providers.base import ModelMessage, ModelResponse, ModelUsage, ModelConfig, ModelRole
from app.providers.router import SmartRouter, RouterStrategy, ModelStats
from app.providers.openai import OpenAIProvider
from app.providers.anthropic import AnthropicProvider
from app.providers.qwen import QwenProvider
from app.providers.ollama import OllamaProvider


@pytest.fixture
def model_config():
    """模型配置"""
    return ModelConfig(
        api_key="test-key",
        model_name="test-model"
    )


@pytest.fixture
def messages():
    """测试消息"""
    return [
        ModelMessage(role=ModelRole.SYSTEM, content="你是一个助手"),
        ModelMessage(role=ModelRole.USER, content="你好")
    ]


class TestModelBase:
    """基础类测试"""
    
    def test_model_message(self):
        """测试 ModelMessage"""
        msg = ModelMessage(role=ModelRole.USER, content="测试")
        assert msg.role == ModelRole.USER
        assert msg.content == "测试"
    
    def test_model_response(self):
        """测试 ModelResponse"""
        response = ModelResponse(
            content="测试响应",
            model="test-model",
            usage=ModelUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        )
        assert response.content == "测试响应"
        assert response.usage.total_tokens == 15
    
    def test_model_config(self):
        """测试 ModelConfig"""
        config = ModelConfig(
            api_key="test-key",
            model_name="gpt-4o",
            temperature=0.7
        )
        assert config.api_key == "test-key"
        assert config.model_name == "gpt-4o"


class TestOpenAIProvider:
    """OpenAI Provider 测试"""
    
    @pytest.mark.asyncio
    async def test_chat(self, model_config, messages):
        """测试聊天"""
        provider = OpenAIProvider()
        response = await provider.chat(messages, model_config)
        
        assert isinstance(response, ModelResponse)
        assert "OpenAI" in response.content
    
    def test_get_available_models(self):
        """测试获取可用模型"""
        provider = OpenAIProvider()
        models = provider.get_available_models()
        
        assert len(models) > 0
        assert "gpt-4o" in models
    
    def test_estimate_cost(self):
        """测试成本估算"""
        provider = OpenAIProvider()
        usage = ModelUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
        
        cost = provider.estimate_cost(usage, "gpt-4o")
        assert cost > 0


class TestAnthropicProvider:
    """Anthropic Provider 测试"""
    
    @pytest.mark.asyncio
    async def test_chat(self, model_config, messages):
        """测试聊天"""
        provider = AnthropicProvider()
        response = await provider.chat(messages, model_config)
        
        assert isinstance(response, ModelResponse)
        assert "Anthropic" in response.content
    
    @pytest.mark.asyncio
    async def test_embed_not_implemented(self, model_config):
        """测试嵌入（应抛出异常）"""
        provider = AnthropicProvider()
        
        with pytest.raises(NotImplementedError):
            await provider.embed("测试文本", model_config)


class TestQwenProvider:
    """Qwen Provider 测试"""
    
    @pytest.mark.asyncio
    async def test_chat(self, model_config, messages):
        """测试聊天"""
        provider = QwenProvider()
        response = await provider.chat(messages, model_config)
        
        assert isinstance(response, ModelResponse)
        assert "Qwen" in response.content
    
    @pytest.mark.asyncio
    async def test_embed(self, model_config):
        """测试嵌入"""
        provider = QwenProvider()
        embedding = await provider.embed("测试文本", model_config)
        
        assert len(embedding) == 1536


class TestOllamaProvider:
    """Ollama Provider 测试"""
    
    @pytest.mark.asyncio
    async def test_chat(self, model_config, messages):
        """测试聊天"""
        provider = OllamaProvider()
        response = await provider.chat(messages, model_config)
        
        assert isinstance(response, ModelResponse)
        assert "Ollama" in response.content
    
    def test_zero_cost(self):
        """测试零成本"""
        provider = OllamaProvider()
        usage = ModelUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
        
        cost = provider.estimate_cost(usage, "llama3")
        assert cost == 0.0


class TestSmartRouter:
    """SmartRouter 测试"""
    
    def test_register_provider(self):
        """测试注册提供商"""
        router = SmartRouter()
        provider = OpenAIProvider()
        
        router.register_provider("openai", provider)
        
        assert "openai" in router._providers
    
    def test_unregister_provider(self):
        """测试注销提供商"""
        router = SmartRouter()
        provider = OpenAIProvider()
        
        router.register_provider("openai", provider)
        result = router.unregister_provider("openai")
        
        assert result is True
        assert "openai" not in router._providers
    
    @pytest.mark.asyncio
    async def test_chat_with_fallback(self, messages):
        """测试带降级的聊天"""
        router = SmartRouter(strategy=RouterStrategy.COST_FIRST)
        provider = OpenAIProvider()
        
        router.register_provider("openai", provider)
        
        config = ModelConfig(api_key="test-key", model_name="gpt-4o")
        response = await router.chat(messages, config)
        
        assert isinstance(response, ModelResponse)
    
    def test_get_stats(self):
        """测试获取统计"""
        router = SmartRouter()
        router.register_provider("openai", OpenAIProvider())
        
        stats = router.get_stats("openai")
        assert isinstance(stats, ModelStats)
        assert stats.request_count == 0
    
    def test_select_offline_provider(self):
        """测试选择离线提供商"""
        router = SmartRouter(strategy=RouterStrategy.OFFLINE_FIRST)
        
        router.register_provider("openai", OpenAIProvider())
        router.register_provider("ollama", OllamaProvider())
        
        selected = router._select_offline_provider()
        assert selected == "ollama"
