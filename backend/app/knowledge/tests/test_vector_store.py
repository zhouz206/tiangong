"""
测试 ChromaDB 向量存储
"""
import pytest
import tempfile
import shutil
from pathlib import Path

from app.knowledge.vector_store import VectorStore
from app.knowledge.models import KnowledgeDocument, DocumentStatus, DocumentType


class TestVectorStore:
    """测试向量存储"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def vector_store(self, temp_dir):
        """创建向量存储实例"""
        return VectorStore(
            persist_directory=temp_dir,
            collection_name="test_collection",
        )

    @pytest.fixture
    def sample_document(self):
        """创建示例文档"""
        return KnowledgeDocument(
            id="doc_test_001",
            title="测试文档",
            content="这是一个测试文档的内容",
            category="技术文档",
            tags=["测试", "示例"],
            status=DocumentStatus.DRAFT,
        )

    @pytest.fixture
    def sample_embedding(self):
        """创建示例嵌入"""
        return [0.1] * 384  # 模拟 384 维嵌入

    def test_add_document(self, vector_store, sample_document, sample_embedding):
        """测试添加文档"""
        success = vector_store.add_document(sample_document, sample_embedding)

        assert success is True

        # 验证文档被添加
        result = vector_store.get_document("doc_test_001")
        assert result is not None
        assert result["metadata"]["title"] == "测试文档"

    def test_update_document(self, vector_store, sample_document, sample_embedding):
        """测试更新文档"""
        # 先添加
        vector_store.add_document(sample_document, sample_embedding)

        # 更新内容
        sample_document.content = "更新后的内容"
        sample_document.updated_at = sample_document.updated_at  # 更新时间

        success = vector_store.update_document(sample_document, sample_embedding)

        assert success is True

        # 验证更新
        result = vector_store.get_document("doc_test_001")
        assert result["content"] == "更新后的内容"

    def test_delete_document(self, vector_store, sample_document, sample_embedding):
        """测试删除文档"""
        # 先添加
        vector_store.add_document(sample_document, sample_embedding)

        # 删除
        success = vector_store.delete_document("doc_test_001")

        assert success is True

        # 验证删除
        result = vector_store.get_document("doc_test_001")
        assert result is None

    def test_search(self, vector_store, sample_embedding):
        """测试向量搜索"""
        # 添加多个文档
        docs = [
            KnowledgeDocument(
                id=f"doc_{i}",
                title=f"文档{i}",
                content=f"这是文档{i}的内容",
                category="技术文档",
                tags=["测试"],
            )
            for i in range(5)
        ]

        for doc in docs:
            vector_store.add_document(doc, sample_embedding)

        # 搜索
        results = vector_store.search(
            query_embedding=sample_embedding,
            n_results=3,
        )

        assert len(results) <= 3
        assert all("id" in r for r in results)
        assert all("score" in r for r in results)

    def test_search_with_category_filter(self, vector_store, sample_embedding):
        """测试带分类过滤的搜索"""
        # 添加不同分类的文档
        docs = [
            KnowledgeDocument(
                id="doc_tech",
                title="技术文档",
                content="技术内容",
                category="技术文档",
            ),
            KnowledgeDocument(
                id="doc_product",
                title="产品文档",
                content="产品内容",
                category="产品文档",
            ),
        ]

        for doc in docs:
            vector_store.add_document(doc, sample_embedding)

        # 按分类搜索
        results = vector_store.search(
            query_embedding=sample_embedding,
            n_results=10,
            category="技术文档",
        )

        assert len(results) >= 1
        assert all(r["metadata"]["category"] == "技术文档" for r in results)

    def test_search_with_min_score(self, vector_store, sample_embedding):
        """测试最小分数过滤"""
        # 添加文档
        doc = KnowledgeDocument(
            id="doc_001",
            title="测试",
            content="内容",
            category="分类",
        )
        vector_store.add_document(doc, sample_embedding)

        # 搜索，设置很高的最小分数
        results = vector_store.search(
            query_embedding=sample_embedding,
            n_results=10,
            min_score=0.99,
        )

        # 所有结果分数都应该 >= 0.99
        assert all(r["score"] >= 0.99 for r in results)

    def test_get_document_not_found(self, vector_store):
        """测试获取不存在的文档"""
        result = vector_store.get_document("non_existent_id")
        assert result is None

    def test_list_documents(self, vector_store, sample_embedding):
        """测试列出文档"""
        # 添加多个文档
        for i in range(5):
            doc = KnowledgeDocument(
                id=f"doc_{i}",
                title=f"文档{i}",
                content=f"内容{i}",
                category="技术文档",
            )
            vector_store.add_document(doc, sample_embedding)

        # 列出所有文档
        documents = vector_store.list_documents(limit=10)

        assert len(documents) == 5
        assert all("id" in d for d in documents)
        assert all("metadata" in d for d in documents)

    def test_list_documents_with_filter(self, vector_store, sample_embedding):
        """测试带过滤的文档列表"""
        # 添加不同状态的文档
        docs = [
            KnowledgeDocument(
                id="doc_draft",
                title="草稿",
                content="内容",
                category="技术文档",
                status=DocumentStatus.DRAFT,
            ),
            KnowledgeDocument(
                id="doc_published",
                title="已发布",
                content="内容",
                category="技术文档",
                status=DocumentStatus.PUBLISHED,
            ),
        ]

        for doc in docs:
            vector_store.add_document(doc, sample_embedding)

        # 按状态过滤
        documents = vector_store.list_documents(
            status=DocumentStatus.DRAFT,
            limit=10,
        )

        assert len(documents) == 1
        assert documents[0]["metadata"]["status"] == DocumentStatus.DRAFT

    def test_get_collection_stats(self, vector_store, sample_embedding):
        """测试获取集合统计"""
        # 添加一些文档
        for i in range(3):
            doc = KnowledgeDocument(
                id=f"doc_{i}",
                title=f"文档{i}",
                content=f"内容{i}",
                category="分类",
            )
            vector_store.add_document(doc, sample_embedding)

        stats = vector_store.get_collection_stats()

        assert "name" in stats
        assert "count" in stats
        assert stats["count"] == 3

    def test_reset_collection(self, vector_store, sample_embedding):
        """测试重置集合"""
        # 添加文档
        doc = KnowledgeDocument(
            id="doc_001",
            title="测试",
            content="内容",
            category="分类",
        )
        vector_store.add_document(doc, sample_embedding)

        # 重置
        success = vector_store.reset_collection()

        assert success is True

        # 验证集合为空
        stats = vector_store.get_collection_stats()
        assert stats["count"] == 0

    def test_persistence(self, temp_dir):
        """测试持久化"""
        # 创建第一个存储
        store1 = VectorStore(
            persist_directory=temp_dir,
            collection_name="persist_test",
        )

        doc = KnowledgeDocument(
            id="doc_persist",
            title="持久化测试",
            content="测试内容",
            category="分类",
        )
        embedding = [0.1] * 384
        store1.add_document(doc, embedding)

        # 创建第二个存储（同一目录）
        store2 = VectorStore(
            persist_directory=temp_dir,
            collection_name="persist_test",
        )

        # 验证数据存在
        result = store2.get_document("doc_persist")
        assert result is not None
        assert result["metadata"]["title"] == "持久化测试"
