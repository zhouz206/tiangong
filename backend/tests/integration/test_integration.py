"""
前后端集成测试

测试前端与后端的真实交互
"""
import pytest
import os
import sys

# 获取项目根目录
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'backend'))

from fastapi.testclient import TestClient
from app.main import app


class TestBackendAPI:
    """后端 API 集成测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        # 每次测试前重置项目存储
        from app.api import projects
        projects._projects_store.clear()

        with TestClient(app) as client:
            yield client

    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_api_docs(self, client):
        """测试 API 文档可访问"""
        # 测试 OpenAPI JSON
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

        # 测试 docs 页面
        response = client.get("/docs")
        assert response.status_code == 200

        # 测试 redoc 页面
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_projects_endpoint(self, client):
        """测试项目端点"""
        # 获取项目列表（初始为空）
        response = client.get("/api/projects/projects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # 创建项目
        project_data = {
            "name": "测试项目",
            "description": "这是一个测试项目",
            "status": "active",
            "phase": "planning"
        }
        response = client.post("/api/projects/projects", json=project_data)
        assert response.status_code == 200
        created = response.json()
        assert created["name"] == project_data["name"]
        assert created["description"] == project_data["description"]
        assert "id" in created

        # 获取项目详情
        project_id = created["id"]
        response = client.get(f"/api/projects/projects/{project_id}")
        assert response.status_code == 200
        fetched = response.json()
        assert fetched["id"] == project_id
        assert fetched["name"] == project_data["name"]

    def test_agents_endpoint(self, client):
        """测试 Agent 端点"""
        # 获取 Agent 列表
        response = client.get("/api/agents/agents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # 获取单个 Agent 详情
        agent_id = "coder"
        response = client.get(f"/api/agents/agents/{agent_id}")
        assert response.status_code == 200
        agent = response.json()
        assert agent["id"] == f"agent-{agent_id}"
        assert agent["role"] == agent_id
        assert "capabilities" in agent

        # 执行 Agent 任务
        execute_data = {
            "task": "编写一个 Python 函数",
            "context": {"language": "python"}
        }
        response = client.post(f"/api/agents/agents/{agent_id}/execute", json=execute_data)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "result" in result

    def test_knowledge_endpoint(self, client):
        """测试知识库端点"""
        # 获取知识库列表
        response = client.get("/api/knowledge/knowledge")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # 获取单个知识库条目
        item_id = "kb-001"
        response = client.get(f"/api/knowledge/knowledge/{item_id}")
        assert response.status_code == 200
        item = response.json()
        assert item["id"] == item_id
        assert "title" in item
        assert "content" in item

        # 搜索知识库
        search_data = {
            "query": "项目",
            "limit": 5
        }
        response = client.post("/api/knowledge/knowledge/search", json=search_data)
        assert response.status_code == 200
        result = response.json()
        assert "query" in result
        assert "results" in result
        assert "total" in result


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

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        # 每次测试前重置项目存储
        from app.api import projects
        projects._projects_store.clear()

        with TestClient(app) as client:
            yield client

    def test_full_workflow(self, client):
        """测试完整工作流：创建项目 -> 查看 Agent -> 搜索知识"""
        # 1. 健康检查
        response = client.get("/health")
        assert response.status_code == 200

        # 2. 创建项目
        project_data = {
            "name": "端到端测试项目",
            "description": "测试完整工作流",
            "status": "active",
            "phase": "planning"
        }
        response = client.post("/api/projects/projects", json=project_data)
        assert response.status_code == 200
        project = response.json()
        assert project["name"] == project_data["name"]

        # 3. 获取可用 Agent
        response = client.get("/api/agents/agents")
        assert response.status_code == 200
        agents = response.json()
        assert len(agents) > 0

        # 4. 搜索相关知识
        search_data = {"query": "代码", "limit": 5}
        response = client.post("/api/knowledge/knowledge/search", json=search_data)
        assert response.status_code == 200
        search_result = response.json()
        assert "results" in search_result

        # 5. 获取 MCP 工具信息
        response = client.get("/api/mcp/mcp")
        assert response.status_code == 200
        mcp_info = response.json()
        assert "tools" in mcp_info

    def test_agent_execution_flow(self, client):
        """测试 Agent 执行流程"""
        # 1. 列出可用 Agent
        response = client.get("/api/agents/agents")
        assert response.status_code == 200
        agents = response.json()

        # 2. 对每个 Agent 执行测试任务
        test_tasks = {
            "coder": "编写一个计算斐波那契数列的函数",
            "designer": "设计一个登录页面的 UI",
            "researcher": "调研最新的 AI 发展趋势"
        }

        for agent_role, task in test_tasks.items():
            if agent_role in ["coder", "designer", "researcher"]:
                # 执行任务
                response = client.post(
                    f"/api/agents/agents/{agent_role}/execute",
                    json={"task": task}
                )
                assert response.status_code == 200
                result = response.json()
                assert result["success"] is True, f"Agent {agent_role} 执行失败"
                assert "result" in result
                assert result["result"]["task"] == task
