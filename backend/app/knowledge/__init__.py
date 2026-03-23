"""
知识库模块

提供完整的知识库管理功能：
- 向量存储 (ChromaDB)
- 文档嵌入 (Sentence-BERT)
- 语义搜索
- 分类和标签
- 自动归档

使用示例:
    from app.knowledge import KnowledgeBase

    kb = KnowledgeBase()
    
    # 添加文档
    kb.add_document(title="API 文档", content="...", category="tech")
    
    # 搜索
    results = kb.search("如何使用 API")
    
    # 自动分类
    category = kb.auto_categorize(content)
"""

from typing import Optional
from .models import (
    KnowledgeDocument,
    DocumentStatus,
    DocumentType,
    Category,
    Tag,
    SearchQuery,
    SearchResult,
    ArchiveRule,
    TaxonomyRelationship,
)

from .vector_store import VectorStore, vector_store
from .embedding import EmbeddingService, embedding_service
from .search import SemanticSearch, semantic_search
from .taxonomy import TaxonomyManager, taxonomy_manager
from .archive import AutoArchiver, auto_archiver


class KnowledgeBase:
    """
    知识库统一接口

    整合所有知识管理功能，提供简洁的 API。
    """

    def __init__(
        self,
        persist_directory: str = "./data/chroma",
        collection_name: str = "knowledge_documents",
        embedding_model: str = "zh",
    ):
        """
        初始化知识库

        Args:
            persist_directory: 向量存储持久化目录
            collection_name: 集合名称
            embedding_model: 嵌入模型名称
        """
        self.vector_store = VectorStore(
            persist_directory=persist_directory,
            collection_name=collection_name,
        )
        self.embedding_service = EmbeddingService(model_name=embedding_model)
        self.search_engine = SemanticSearch(
            vector_store=self.vector_store,
            embedding_service=self.embedding_service,
        )
        self.taxonomy = TaxonomyManager(
            embedding_service=self.embedding_service,
        )
        self.archiver = AutoArchiver(
            vector_store=self.vector_store,
        )

    def add_document(
        self,
        title: str,
        content: str,
        category: Optional[str] = None,
        tags: Optional[list[str]] = None,
        auto_categorize: bool = True,
        auto_tag: bool = True,
    ) -> str:
        """
        添加文档到知识库

        Args:
            title: 文档标题
            content: 文档内容
            category: 分类（可选，自动分类如果不提供）
            tags: 标签列表（可选，自动打标签如果不提供）
            auto_categorize: 是否自动分类
            auto_tag: 是否自动打标签

        Returns:
            文档 ID
        """
        from .models import KnowledgeDocument, DocumentType
        from datetime import datetime
        import uuid

        # 生成文档 ID
        doc_id = f"doc_{uuid.uuid4().hex[:16]}"

        # 自动分类
        if not category and auto_categorize:
            category_id = self.taxonomy.auto_categorize(content, title)
            if category_id:
                category_obj = self.taxonomy.get_category(category_id)
                category = category_obj.name if category_obj else "技术文档"

        # 默认分类
        if not category:
            category = "未分类"

        # 自动打标签
        if auto_tag:
            auto_tags = self.taxonomy.auto_tag(content, title)
            tag_names = [
                self.taxonomy.get_tag(tid).name
                for tid in auto_tags
                if self.taxonomy.get_tag(tid)
            ]
            tags = list(set((tags or []) + tag_names))

        # 生成嵌入
        embedding = self.embedding_service.embed_text(content)

        # 创建文档对象
        doc = KnowledgeDocument(
            id=doc_id,
            title=title,
            content=content,
            category=category,
            tags=tags or [],
            content_type=DocumentType.TEXT,
            embedding=embedding,
        )

        # 添加到向量存储
        self.vector_store.add_document(doc, embedding)

        return doc_id

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[list[str]] = None,
        limit: int = 10,
        min_score: float = 0.5,
        hybrid: bool = False,
    ) -> list[SearchResult]:
        """
        搜索知识库

        Args:
            query: 搜索查询
            category: 过滤分类
            tags: 过滤标签
            limit: 返回数量
            min_score: 最小相关性分数
            hybrid: 是否使用混合搜索

        Returns:
            搜索结果列表
        """
        if hybrid:
            return self.search_engine.hybrid_search(
                query=query,
                category=category,
                tags=tags,
                limit=limit,
            )
        else:
            return self.search_engine.search(
                query=query,
                category=category,
                tags=tags,
                limit=limit,
                min_score=min_score,
            )

    def get_document(self, doc_id: str) -> Optional[KnowledgeDocument]:
        """获取文档"""
        doc_data = self.vector_store.get_document(doc_id)
        if not doc_data:
            return None

        metadata = doc_data.get("metadata", {})
        return KnowledgeDocument(
            id=doc_id,
            title=metadata.get("title", ""),
            content=doc_data.get("content", ""),
            category=metadata.get("category", ""),
            tags=metadata.get("tags", "").split(",") if metadata.get("tags") else [],
            status=metadata.get("status", "draft"),
            version=metadata.get("version", "1.0"),
            content_type=metadata.get("content_type", "text"),
            metadata=metadata,
        )

    def update_document(
        self,
        doc_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> bool:
        """更新文档"""
        doc_data = self.vector_store.get_document(doc_id)
        if not doc_data:
            return False

        metadata = doc_data.get("metadata", {})
        new_content = content or doc_data.get("content", "")

        # 重新生成嵌入
        embedding = self.embedding_service.embed_text(new_content)

        doc = KnowledgeDocument(
            id=doc_id,
            title=title or metadata.get("title", ""),
            content=new_content,
            category=category or metadata.get("category", ""),
            tags=tags or (metadata.get("tags", "").split(",") if metadata.get("tags") else []),
            status=metadata.get("status", "draft"),
            metadata=metadata,
        )

        return self.vector_store.update_document(doc, embedding)

    def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        return self.vector_store.delete_document(doc_id)

    def auto_categorize(self, content: str, title: str = "") -> Optional[str]:
        """自动分类"""
        return self.taxonomy.auto_categorize(content, title)

    def auto_tag(self, content: str, title: str = "", max_tags: int = 5) -> list[str]:
        """自动打标签"""
        tag_ids = self.taxonomy.auto_tag(content, title, max_tags)
        return [
            self.taxonomy.get_tag(tid).name
            for tid in tag_ids
            if self.taxonomy.get_tag(tid)
        ]

    def get_categories(self) -> list[dict]:
        """获取所有分类"""
        return [
            {"id": c.id, "name": c.name, "description": c.description}
            for c in self.taxonomy.get_categories()
        ]

    def get_tags(self) -> list[dict]:
        """获取所有标签"""
        return [
            {"id": t.id, "name": t.name, "category": t.category, "usage_count": t.usage_count}
            for t in self.taxonomy.get_tags()
        ]

    def run_archival(self, dry_run: bool = False) -> dict:
        """执行归档"""
        return self.archiver.run_archival(dry_run=dry_run)

    def get_stats(self) -> dict:
        """获取统计信息"""
        collection_stats = self.vector_store.get_collection_stats()
        archive_stats = self.archiver.get_archive_stats()
        search_stats = self.search_engine.get_search_stats()

        return {
            **collection_stats,
            **archive_stats,
            **search_stats,
        }


# 默认知识库实例
knowledge_base = KnowledgeBase()


# 导出所有内容
__all__ = [
    # 模型
    "KnowledgeDocument",
    "DocumentStatus",
    "DocumentType",
    "Category",
    "Tag",
    "SearchQuery",
    "SearchResult",
    "ArchiveRule",
    "TaxonomyRelationship",
    # 核心类
    "VectorStore",
    "EmbeddingService",
    "SemanticSearch",
    "TaxonomyManager",
    "AutoArchiver",
    "KnowledgeBase",
    # 默认实例
    "vector_store",
    "embedding_service",
    "semantic_search",
    "taxonomy_manager",
    "auto_archiver",
    "knowledge_base",
]
