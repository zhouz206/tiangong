"""
前后端集成测试

测试前端与后端的真实交互
"""
import pytest
import os

# 获取项目根目录
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class TestBackendAPI:
    """后端 API 集成测试（需要运行的服务）"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需要运行的后端服务")
    async def test_health_check(self):
        """测试健康检查"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/health") as resp:
                assert resp.status == 200
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需要运行的后端服务")
    async def test_api_docs(self):
        """测试 API 文档可访问"""
        pass
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需要运行的后端服务")
    async def test_projects_endpoint(self):
        """测试项目端点"""
        pass
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需要运行的后端服务")
    async def test_agents_endpoint(self):
        """测试 Agent 端点"""
        pass
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需要运行的后端服务")
    async def test_knowledge_endpoint(self):
        """测试知识库端点"""
        pass


class TestFrontendBuild:
    """前端构建测试"""
    
    def test_frontend_build_exists(self):
        """测试前端构建产物存在"""
        assert os.path.exists(os.path.join(PROJECT_ROOT, "frontend/package.json"))
        assert os.path.exists(os.path.join(PROJECT_ROOT, "frontend/vite.config.ts"))
    
    def test_frontend_dependencies(self):
        """测试前端依赖配置"""
        import json
        
        with open(os.path.join(PROJECT_ROOT, "frontend/package.json")) as f:
            package = json.load(f)
        
        assert "react" in package.get("dependencies", {})
        assert "react-dom" in package.get("dependencies", {})
        assert "react-router-dom" in package.get("dependencies", {})
    
    def test_frontend_scripts(self):
        """测试前端脚本配置"""
        import json
        
        with open(os.path.join(PROJECT_ROOT, "frontend/package.json")) as f:
            package = json.load(f)
        
        scripts = package.get("scripts", {})
        assert "dev" in scripts
        assert "build" in scripts


class TestDockerIntegration:
    """Docker 集成测试"""
    
    def test_docker_compose_exists(self):
        """测试 docker-compose.yml 存在"""
        assert os.path.exists(os.path.join(PROJECT_ROOT, "docker/docker-compose.yml"))
    
    def test_dockerfile_backend_exists(self):
        """测试后端 Dockerfile 存在"""
        assert os.path.exists(os.path.join(PROJECT_ROOT, "docker/Dockerfile.backend"))
    
    def test_dockerfile_frontend_exists(self):
        """测试前端 Dockerfile 存在"""
        assert os.path.exists(os.path.join(PROJECT_ROOT, "docker/Dockerfile.frontend"))
    
    def test_docker_compose_valid_yaml(self):
        """测试 docker-compose.yml 是有效的 YAML"""
        import yaml
        
        with open(os.path.join(PROJECT_ROOT, "docker/docker-compose.yml")) as f:
            config = yaml.safe_load(f)
        
        assert "services" in config
        assert "backend" in config["services"]
        assert "frontend" in config["services"]


class TestEndToEnd:
    """端到端流程测试"""
    
    @pytest.mark.skip(reason="需要运行中的服务")
    def test_full_workflow(self):
        """测试完整工作流"""
        pass
    
    @pytest.mark.skip(reason="需要运行中的服务")
    def test_agent_execution_flow(self):
        """测试 Agent 执行流程"""
        pass
