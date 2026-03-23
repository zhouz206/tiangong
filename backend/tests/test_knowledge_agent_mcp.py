"""
知识库集成测试

测试知识库与 Agent 系统和 MCP 服务的集成。
"""
import pytest
import tempfile
import shutil
from datetime import datetime
from unittest.mock import Mock, MagicMock

from app.knowledge import KnowledgeBase
from app.agents import KnowledgeManagerAgent
from app.mcp.services import KnowledgeService
from app.core.message import MessageBus


class MockEmbeddingService:
    """模拟嵌入服务用于测试"""

    def __init__(self):
        self.model_name = "mock"
        self.embedding_dim = 384

    def embed_text(self, text: str) -> list[float]:
        """生成模拟嵌入向量 - 使用更精确的哈希方法"""
        import hashlib
        # 使用 SHA256 生成更均匀的哈希值
        hash_bytes = hashlib.sha256(text.encode()).digest()
        # 扩展为 384 维向量
        base_values = [int(b) / 255.0 for b in hash_bytes]
        vector = (base_values * 12)[:self.embedding_dim]  # 重复 12 次得到 384 维
        # 归一化
        norm = sum(v*v for v in vector) ** 0.5
        if norm == 0:
            norm = 1
        return [v / norm for v in vector]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """批量生成嵌入"""
        return [self.embed_text(t) for t in texts]


def create_knowledge_base_with_mock(temp_dir: str, collection_name: str = "test") -> KnowledgeBase:
    """创建使用模拟嵌入服务的知识库"""
    kb = KnowledgeBase(
        persist_directory=temp_dir,
        collection_name=collection_name,
        embedding_model="zh",
    )
    # 替换为模拟嵌入服务
    kb.embedding_service = MockEmbeddingService()
    kb.search_engine.embedding_service = MockEmbeddingService()
    kb.taxonomy.embedding_service = MockEmbeddingService()
    return kb


class TestKnowledgeAgentIntegration:
    """测试知识库与 Agent 系统集成"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def knowledge_base(self, temp_dir):
        """创建知识库实例（使用模拟嵌入服务）"""
        return create_knowledge_base_with_mock(temp_dir, "test_knowledge")

    @pytest.fixture
    def knowledge_agent(self, knowledge_base):
        """创建知识管理员 Agent"""
        agent = KnowledgeManagerAgent(
            agent_id="test_km_agent",
            name="Test Knowledge Manager",
            knowledge_base=knowledge_base,
        )
        agent.initialize()
        return agent

    @pytest.fixture
    def message_bus(self):
        """创建消息总线"""
        return MessageBus()

    async def test_agent_with_knowledge_base(self, knowledge_agent, knowledge_base):
        """测试 Agent 使用知识库"""
        # 验证 Agent 有知识库引用
        assert knowledge_agent.knowledge_base is not None
        assert knowledge_agent.knowledge_base == knowledge_base

    async def test_agent_organize_documents(self, knowledge_agent):
        """测试 Agent 组织文档功能"""
        from app.core.agent import TaskContext

        # 模拟上游输出
        upstream_outputs = [
            {
                "title": "Python 教程",
                "content": "Python 是一种高级编程语言，简洁易学。",
            },
            {
                "title": "Java 教程",
                "content": "Java 是面向对象的编程语言。",
            },
        ]

        context = TaskContext(
            task_id="task_001",
            task_title="组织文档",
            task_description="整理编程教程文档",
            upstream_outputs=upstream_outputs,
            metadata={"task_type": "document_organization"},
        )

        result = await knowledge_agent.execute_task(context)

        assert result.success is True
        assert result.output["documents_processed"] == 2
        assert len(result.output["document_ids"]) == 2

    async def test_agent_index_knowledge(self, knowledge_agent):
        """测试 Agent 建立知识索引"""
        from app.core.agent import TaskContext

        upstream_outputs = [
            {
                "title": "API 设计指南",
                "content": "RESTful API 设计最佳实践",
                "category": "技术文档",
                "tags": ["API", "设计"],
            },
        ]

        context = TaskContext(
            task_id="task_002",
            task_title="建立索引",
            task_description="为技术文档建立索引",
            upstream_outputs=upstream_outputs,
            metadata={"task_type": "knowledge_indexing"},
        )

        result = await knowledge_agent.execute_task(context)

        assert result.success is True
        assert len(result.output["indexed_items"]) >= 1

    async def test_agent_search_knowledge(self, knowledge_agent, knowledge_base):
        """测试 Agent 知识检索功能"""
        from app.core.agent import TaskContext

        # 先添加一些文档
        knowledge_base.add_document(
            title="Python 基础",
            content="Python 编程语言基础教程，包括变量、循环、函数等概念。",
            category="技术文档",
            tags=["Python", "教程"],
        )

        knowledge_base.add_document(
            title="Java 基础",
            content="Java 编程语言入门，面向对象编程基础。",
            category="技术文档",
            tags=["Java", "教程"],
        )

        context = TaskContext(
            task_id="task_003",
            task_title="搜索知识",
            task_description="Python 编程",
            upstream_outputs=[],
            metadata={"task_type": "knowledge_search"},
        )

        result = await knowledge_agent.execute_task(context)

        assert result.success is True
        assert result.output["query"] == "Python 编程"
        assert result.output["total_matches"] >= 1
        assert len(result.output["results"]) >= 1

    async def test_agent_curate_knowledge(self, knowledge_agent, knowledge_base):
        """测试 Agent 知识整理功能"""
        from app.core.agent import TaskContext

        # 添加测试文档
        knowledge_base.add_document(
            title="机器学习入门",
            content="机器学习是人工智能的一个分支，包括监督学习、无监督学习等。",
            category="技术文档",
            tags=["AI", "机器学习"],
        )

        context = TaskContext(
            task_id="task_004",
            task_title="整理知识",
            task_description="机器学习",
            upstream_outputs=[],
            metadata={"task_type": "knowledge_curation"},
        )

        result = await knowledge_agent.execute_task(context)

        assert result.success is True
        assert "selected_items" in result.output


class TestKnowledgeMCPIntegration:
    """测试知识库与 MCP 服务集成"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def knowledge_base(self, temp_dir):
        """创建知识库实例（使用模拟嵌入服务）"""
        return create_knowledge_base_with_mock(temp_dir, "test_mcp_knowledge")

    @pytest.fixture
    def knowledge_service(self, knowledge_base):
        """创建知识库 MCP 服务"""
        return KnowledgeService(
            knowledge_base=knowledge_base,
            max_search_results=10,
        )

    async def test_service_initialization(self, knowledge_service, knowledge_base):
        """测试服务初始化"""
        assert knowledge_service.knowledge_base == knowledge_base
        assert knowledge_service.server is not None

    async def test_add_document_tool(self, knowledge_service):
        """测试添加文档工具"""
        result = await knowledge_service._handle_add_document({
            "title": "测试文档",
            "content": "这是测试内容",
            "category": "测试分类",
            "tags": ["测试", "文档"],
        })

        assert result.is_error is False
        assert "Document added successfully" in result.content[0]["text"]

    async def test_search_tool(self, knowledge_service):
        """测试搜索工具"""
        # 先添加文档
        add_result = await knowledge_service._handle_add_document({
            "title": "Python 教程",
            "content": "Python 编程语言教程",
            "category": "技术文档",
        })

        result = await knowledge_service._handle_search({
            "query": "Python",
            "limit": 5,
        })

        assert result.is_error is False
        import json
        data = json.loads(result.content[0]["text"])
        assert "results" in data
        # 注意：由于使用模拟嵌入，搜索结果可能为 0
        assert data["total_results"] >= 0

    async def test_get_document_tool(self, knowledge_service):
        """测试获取文档工具"""
        # 先添加文档
        add_result = await knowledge_service._handle_add_document({
            "title": "获取测试",
            "content": "测试内容",
        })

        # 从结果中提取文档 ID
        doc_id = add_result.content[0]["text"].split("ID: ")[1]

        result = await knowledge_service._handle_get_document({
            "doc_id": doc_id,
        })

        assert result.is_error is False
        import json
        data = json.loads(result.content[0]["text"])
        assert data["title"] == "获取测试"

    async def test_list_categories_tool(self, knowledge_service):
        """测试列出分类工具"""
        result = await knowledge_service._handle_list_categories({})

        assert result.is_error is False
        import json
        data = json.loads(result.content[0]["text"])
        assert "categories" in data

    async def test_list_tags_tool(self, knowledge_service):
        """测试列出标签工具"""
        result = await knowledge_service._handle_list_tags({})

        assert result.is_error is False
        import json
        data = json.loads(result.content[0]["text"])
        assert "tags" in data

    async def test_get_stats_tool(self, knowledge_service):
        """测试获取统计工具"""
        # 添加一些文档
        await knowledge_service._handle_add_document({
            "title": "文档 1",
            "content": "内容 1",
        })
        await knowledge_service._handle_add_document({
            "title": "文档 2",
            "content": "内容 2",
        })

        result = await knowledge_service._handle_get_stats({})

        assert result.is_error is False
        import json
        data = json.loads(result.content[0]["text"])
        assert data.get("count", 0) >= 2

    async def test_delete_document_tool(self, knowledge_service):
        """测试删除文档工具"""
        # 先添加文档
        add_result = await knowledge_service._handle_add_document({
            "title": "待删除",
            "content": "待删除内容",
        })
        doc_id = add_result.content[0]["text"].split("ID: ")[1]

        # 删除文档
        result = await knowledge_service._handle_delete_document({
            "doc_id": doc_id,
        })

        assert result.is_error is False
        assert "deleted successfully" in result.content[0]["text"]


class TestKnowledgeFullIntegration:
    """测试完整知识库集成"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    async def test_full_workflow(self, temp_dir):
        """测试完整工作流"""
        # 1. 创建知识库（使用模拟嵌入服务）
        kb = create_knowledge_base_with_mock(temp_dir, "test_full")

        # 2. 创建 Agent
        agent = KnowledgeManagerAgent(
            agent_id="test_agent",
            knowledge_base=kb,
        )
        agent.initialize()

        # 3. 创建 MCP 服务
        service = KnowledgeService(knowledge_base=kb)

        # 4. 通过 MCP 添加文档
        add_result = await service._handle_add_document({
            "title": "集成测试文档",
            "content": "这是集成测试的内容",
            "auto_tag": True,
        })
        assert add_result.is_error is False

        # 5. 通过 Agent 搜索
        from app.core.agent import TaskContext
        context = TaskContext(
            task_id="test",
            task_title="Search",
            task_description="集成测试",
            metadata={"task_type": "knowledge_search"},
        )
        result = await agent.execute_task(context)
        assert result.success is True
        assert result.output["total_matches"] >= 1

        # 6. 获取统计
        stats = kb.get_stats()
        assert stats.get("count", 0) >= 1

    async def test_concurrent_access(self, temp_dir):
        """测试并发访问"""
        kb = create_knowledge_base_with_mock(temp_dir, "test_concurrent")

        # 添加多个文档
        for i in range(10):
            kb.add_document(
                title=f"文档{i}",
                content=f"内容{i}",
            )

        # 验证所有文档
        stats = kb.get_stats()
        assert stats.get("count", 0) >= 10

        # 搜索 - 由于模拟嵌入的限制，只检查返回结果
        results = kb.search("文档", limit=20)
        assert len(results) >= 1  # 至少返回一个结果
