"""
知识库集成测试

测试知识库模块的整体功能和集成。
"""
import pytest
import tempfile
import shutil
from datetime import datetime, timedelta

from app.knowledge import KnowledgeBase
from app.knowledge.models import DocumentStatus


class TestKnowledgeBaseIntegration:
    """测试知识库整体集成"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def kb(self, temp_dir):
        """创建知识库实例"""
        return KnowledgeBase(
            persist_directory=temp_dir,
            collection_name="test_knowledge",
            embedding_model="zh",
        )

    def test_add_document(self, kb):
        """测试添加文档"""
        doc_id = kb.add_document(
            title="Python 入门教程",
            content="Python 是一种高级编程语言，简洁易学。本教程介绍 Python 基础语法。",
            category="技术文档",
            tags=["教程", "Python"],
        )

        assert doc_id.startswith("doc_")

        # 验证文档存在
        doc = kb.get_document(doc_id)
        assert doc is not None
        assert doc.title == "Python 入门教程"
        assert doc.category == "技术文档"

    def test_add_document_auto_categorize(self, kb):
        """测试自动分类"""
        doc_id = kb.add_document(
            title="产品需求文档",
            content="本产品需求文档描述了用户功能需求和特性。包括市场调研和竞品分析。",
            auto_categorize=True,
            auto_tag=True,
        )

        doc = kb.get_document(doc_id)
        assert doc is not None
        # 应该自动分类为产品文档或研究报告
        assert doc.category in ["产品文档", "研究报告", "未分类"]

    def test_add_document_auto_tag(self, kb):
        """测试自动打标签"""
        doc_id = kb.add_document(
            title="API 开发指南",
            content="这是一个关于 API 接口开发的教程，包含最佳实践和示例代码。",
            auto_tag=True,
        )

        doc = kb.get_document(doc_id)
        assert doc is not None
        assert len(doc.tags) > 0

    def test_search(self, kb):
        """测试搜索功能"""
        # 添加多个文档
        kb.add_document(
            title="Python 教程",
            content="Python 编程语言基础教程，涵盖变量、函数、类等概念。",
            category="技术文档",
            tags=["Python", "教程"],
        )
        kb.add_document(
            title="Java 教程",
            content="Java 编程语言入门，面向对象编程基础。",
            category="技术文档",
            tags=["Java", "教程"],
        )
        kb.add_document(
            title="产品需求文档",
            content="产品功能需求和设计说明。",
            category="产品文档",
            tags=["需求", "产品"],
        )

        # 搜索 Python 相关内容
        results = kb.search("Python 编程", limit=5)

        assert len(results) > 0
        assert any("Python" in r.document.title for r in results)

    def test_search_with_category_filter(self, kb):
        """测试带分类过滤的搜索"""
        kb.add_document(
            title="技术文档 1",
            content="技术内容",
            category="技术文档",
        )
        kb.add_document(
            title="产品文档 1",
            content="产品内容",
            category="产品文档",
        )

        # 只搜索技术文档
        results = kb.search("文档", category="技术文档", limit=10)

        assert all(r.document.category == "技术文档" for r in results)

    def test_search_hybrid(self, kb):
        """测试混合搜索"""
        kb.add_document(
            title="API 接口设计",
            content="RESTful API 设计原则和最佳实践",
            category="技术文档",
            tags=["API", "设计"],
        )

        results = kb.search("API 设计", limit=5, hybrid=True)

        assert len(results) > 0

    def test_update_document(self, kb):
        """测试更新文档"""
        doc_id = kb.add_document(
            title="原始标题",
            content="原始内容",
            category="分类",
        )

        success = kb.update_document(
            doc_id,
            title="新标题",
            content="新内容",
        )

        assert success is True

        doc = kb.get_document(doc_id)
        assert doc.title == "新标题"
        assert doc.content == "新内容"

    def test_delete_document(self, kb):
        """测试删除文档"""
        doc_id = kb.add_document(
            title="待删除",
            content="内容",
            category="分类",
        )

        success = kb.delete_document(doc_id)

        assert success is True
        assert kb.get_document(doc_id) is None

    def test_get_categories(self, kb):
        """测试获取分类"""
        categories = kb.get_categories()

        assert isinstance(categories, list)
        assert len(categories) > 0
        assert all("id" in c and "name" in c for c in categories)

    def test_get_tags(self, kb):
        """测试获取标签"""
        tags = kb.get_tags()

        assert isinstance(tags, list)
        assert len(tags) > 0
        assert all("id" in t and "name" in t for t in tags)

    def test_auto_categorize(self, kb):
        """测试自动分类功能"""
        category = kb.auto_categorize(
            content="这是一个关于机器学习和人工智能的技术文档",
            title="AI 技术报告",
        )

        assert category is not None

    def test_auto_tag(self, kb):
        """测试自动打标签功能"""
        tags = kb.auto_tag(
            content="这是一个紧急的 API 开发教程",
            title="API 指南",
            max_tags=3,
        )

        assert isinstance(tags, list)
        assert len(tags) <= 3

    def test_run_archival(self, kb):
        """测试运行归档"""
        # 添加一个超期草稿
        old_doc_id = kb.add_document(
            title="旧草稿",
            content="35 天前的草稿",
            category="技术文档",
        )

        # 手动设置文档为旧（实际场景中由时间自然流逝）
        # 这里测试归档逻辑
        result = kb.run_archival(dry_run=True)

        assert isinstance(result, dict)
        assert "total_processed" in result
        assert "archived" in result

    def test_get_stats(self, kb):
        """测试获取统计信息"""
        # 添加一些文档
        for i in range(3):
            kb.add_document(
                title=f"文档{i}",
                content=f"内容{i}",
                category="分类",
            )

        stats = kb.get_stats()

        assert "total_documents" in stats or "count" in stats
        assert stats.get("total_documents", 0) >= 3 or stats.get("count", 0) >= 3

    def test_full_workflow(self, kb):
        """测试完整工作流程"""
        # 1. 添加文档
        doc_id = kb.add_document(
            title="完整测试文档",
            content="这是一个用于测试完整工作流程的文档。包含技术内容和最佳实践。",
            category="技术文档",
            tags=["测试", "工作流"],
        )

        # 2. 搜索文档
        results = kb.search("完整测试", limit=5)
        assert len(results) > 0

        # 3. 更新文档
        kb.update_document(
            doc_id,
            content="更新后的内容，添加了更多信息。",
        )

        # 4. 获取文档
        doc = kb.get_document(doc_id)
        assert doc is not None
        assert "更新后的内容" in doc.content

        # 5. 获取统计
        stats = kb.get_stats()
        assert stats is not None

    def test_concurrent_documents(self, kb):
        """测试多个文档的并发处理"""
        doc_ids = []
        for i in range(10):
            doc_id = kb.add_document(
                title=f"并发测试文档{i}",
                content=f"这是第{i}个测试文档的内容",
                category="技术文档",
                tags=[f"标签{i % 3}"],
            )
            doc_ids.append(doc_id)

        # 验证所有文档都存在
        for doc_id in doc_ids:
            doc = kb.get_document(doc_id)
            assert doc is not None

        # 搜索应该返回多个结果
        results = kb.search("并发测试", limit=20)
        assert len(results) >= 10

    def test_search_relevance_ranking(self, kb):
        """测试搜索相关性排序"""
        # 添加不同相关度的文档
        kb.add_document(
            title="Python 高级编程",
            content="深入讲解 Python 高级特性，包括装饰器、元类、异步编程等。",
            category="技术文档",
        )
        kb.add_document(
            title="Python 基础",
            content="Python 入门基础教程，变量、循环、函数。",
            category="技术文档",
        )
        kb.add_document(
            title="其他内容",
            content="与 Python 无关的内容",
            category="技术文档",
        )

        results = kb.search("Python 高级", limit=10)

        # 第一个结果应该是最相关的
        assert len(results) > 0
        assert "高级" in results[0].document.title or results[0].score > 0.5

    def test_document_metadata_preservation(self, kb):
        """测试文档元数据保留"""
        doc_id = kb.add_document(
            title="元数据测试",
            content="内容",
            category="技术文档",
            tags=["测试"],
        )

        doc = kb.get_document(doc_id)

        # 验证元数据
        assert doc.id == doc_id
        assert doc.title == "元数据测试"
        assert doc.category == "技术文档"
        assert "测试" in doc.tags
        assert doc.status == DocumentStatus.DRAFT
        assert doc.version == "1.0"
        assert doc.created_at is not None
        assert doc.updated_at is not None
