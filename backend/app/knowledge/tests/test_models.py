"""
测试知识数据模型
"""
import pytest
from datetime import datetime
from app.knowledge.models import (
    KnowledgeDocument,
    DocumentStatus,
    DocumentType,
    Category,
    Tag,
    SearchQuery,
    SearchResult,
    ArchiveRule,
)


class TestKnowledgeDocument:
    """测试知识文档模型"""

    def test_create_document(self):
        """测试创建文档"""
        doc = KnowledgeDocument(
            id="doc_test_001",
            title="测试文档",
            content="这是测试内容",
            category="技术文档",
            tags=["测试", "示例"],
        )

        assert doc.id == "doc_test_001"
        assert doc.title == "测试文档"
        assert doc.content == "这是测试内容"
        assert doc.category == "技术文档"
        assert doc.tags == ["测试", "示例"]
        assert doc.status == DocumentStatus.DRAFT
        assert doc.version == "1.0"

    def test_document_default_values(self):
        """测试文档默认值"""
        doc = KnowledgeDocument(
            id="doc_001",
            title="标题",
            content="内容",
            category="分类",
        )

        assert doc.status == DocumentStatus.DRAFT
        assert doc.version == "1.0"
        assert doc.tags == []
        assert doc.content_type == DocumentType.TEXT
        assert doc.embedding is None

    def test_document_with_embedding(self):
        """测试带嵌入的文档"""
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        doc = KnowledgeDocument(
            id="doc_002",
            title="带嵌入的文档",
            content="内容",
            category="分类",
            embedding=embedding,
        )

        assert doc.embedding == embedding

    def test_document_status_enum(self):
        """测试文档状态枚举"""
        assert DocumentStatus.DRAFT == "draft"
        assert DocumentStatus.PUBLISHED == "published"
        assert DocumentStatus.ARCHIVED == "archived"

    def test_document_type_enum(self):
        """测试文档类型枚举"""
        assert DocumentType.TEXT == "text"
        assert DocumentType.MARKDOWN == "markdown"
        assert DocumentType.CODE == "code"


class TestCategory:
    """测试分类模型"""

    def test_create_category(self):
        """测试创建分类"""
        category = Category(
            id="cat_tech",
            name="技术文档",
            description="技术相关的文档",
            rules=["包含代码", "技术方案"],
        )

        assert category.id == "cat_tech"
        assert category.name == "技术文档"
        assert category.description == "技术相关的文档"
        assert category.rules == ["包含代码", "技术方案"]
        assert category.parent is None
        assert category.subcategories == []

    def test_category_with_parent(self):
        """测试带父分类的子分类"""
        parent = Category(id="cat_parent", name="父分类", description="")
        child = Category(
            id="cat_child",
            name="子分类",
            description="",
            parent=parent.id,
        )

        assert child.parent == "cat_parent"


class TestTag:
    """测试标签模型"""

    def test_create_tag(self):
        """测试创建标签"""
        tag = Tag(
            id="tag_urgent",
            name="紧急",
            category="优先级",
        )

        assert tag.id == "tag_urgent"
        assert tag.name == "紧急"
        assert tag.category == "优先级"
        assert tag.usage_count == 0

    def test_tag_usage_count(self):
        """测试标签使用次数"""
        tag = Tag(id="tag_001", name="测试", usage_count=5)
        assert tag.usage_count == 5


class TestSearchQuery:
    """测试搜索查询模型"""

    def test_create_search_query(self):
        """测试创建搜索查询"""
        query = SearchQuery(
            query="如何学习 Python",
            category="技术文档",
            tags=["教程", "入门"],
            limit=10,
        )

        assert query.query == "如何学习 Python"
        assert query.category == "技术文档"
        assert query.tags == ["教程", "入门"]
        assert query.limit == 10
        assert query.min_score == 0.5

    def test_search_query_defaults(self):
        """测试搜索查询默认值"""
        query = SearchQuery(query="测试")

        assert query.limit == 10
        assert query.min_score == 0.5
        assert query.tags == []
        assert query.category is None


class TestSearchResult:
    """测试搜索结果模型"""

    def test_create_search_result(self):
        """测试创建搜索结果"""
        doc = KnowledgeDocument(
            id="doc_001",
            title="结果文档",
            content="内容",
            category="分类",
        )
        result = SearchResult(
            document=doc,
            score=0.85,
            highlights=["高亮片段"],
            reason="高度相关",
        )

        assert result.document.id == "doc_001"
        assert result.score == 0.85
        assert result.highlights == ["高亮片段"]
        assert result.reason == "高度相关"


class TestArchiveRule:
    """测试归档规则模型"""

    def test_create_archive_rule(self):
        """测试创建归档规则"""
        rule = ArchiveRule(
            id="rule_001",
            name="草稿超 30 天",
            condition_type="age_draft",
            condition_value=30,
            action="archive",
        )

        assert rule.id == "rule_001"
        assert rule.name == "草稿超 30 天"
        assert rule.condition_type == "age_draft"
        assert rule.condition_value == 30
        assert rule.action == "archive"
        assert rule.enabled is True

    def test_archive_rule_disabled(self):
        """测试禁用的归档规则"""
        rule = ArchiveRule(
            id="rule_002",
            name="测试规则",
            condition_type="status",
            condition_value="deprecated",
            enabled=False,
        )

        assert rule.enabled is False
