"""
语义搜索实现

结合向量搜索和关键词匹配，提供高质量的知识检索。
"""
from typing import Any, Optional
import re
from datetime import datetime

from .models import (
    KnowledgeDocument,
    SearchResult,
    SearchQuery,
    DocumentStatus,
)
from .vector_store import VectorStore, vector_store
from .embedding import EmbeddingService, embedding_service


class SemanticSearch:
    """
    语义搜索引擎

    提供基于向量相似度的语义搜索功能。
    """

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_service: Optional[EmbeddingService] = None,
    ):
        """
        初始化语义搜索引擎

        Args:
            vector_store: 向量存储实例
            embedding_service: 嵌入服务实例
        """
        self.vector_store = vector_store or vector_store
        self.embedding_service = embedding_service or embedding_service

        # 搜索配置
        self.default_limit = 10
        self.default_min_score = 0.5
        self.highlight_max_length = 200

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[list[str]] = None,
        limit: int = 10,
        min_score: float = 0.5,
    ) -> list[SearchResult]:
        """
        执行语义搜索

        Args:
            query: 搜索查询
            category: 过滤分类
            tags: 过滤标签
            limit: 返回结果数量
            min_score: 最小相关性分数

        Returns:
            搜索结果列表
        """
        # 生成查询向量
        query_embedding = self.embedding_service.embed_text(query)

        # 向量搜索
        vector_results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=limit * 2,  # 获取多一些结果用于后续过滤
            category=category,
            tags=tags,
            min_score=min_score,
        )

        # 转换为 SearchResult
        search_results = []
        for result in vector_results:
            # 重建文档对象
            metadata = result.get("metadata", {})
            doc = KnowledgeDocument(
                id=result["id"],
                title=metadata.get("title", ""),
                content=result.get("content", ""),
                category=metadata.get("category", ""),
                tags=metadata.get("tags", "").split(",") if metadata.get("tags") else [],
                status=metadata.get("status", DocumentStatus.DRAFT),
                version=metadata.get("version", "1.0"),
                content_type=metadata.get("content_type", "text"),
                created_at=datetime.fromisoformat(metadata["created_at"]) if metadata.get("created_at") else datetime.now(),
                updated_at=datetime.fromisoformat(metadata["updated_at"]) if metadata.get("updated_at") else datetime.now(),
            )

            # 生成高亮片段
            highlights = self._generate_highlights(result.get("content", ""), query)

            # 生成推荐理由
            reason = self._generate_reason(doc, result["score"], query)

            search_results.append(
                SearchResult(
                    document=doc,
                    score=result["score"],
                    highlights=highlights,
                    reason=reason,
                )
            )

        # 按分数排序并限制数量
        search_results.sort(key=lambda x: x.score, reverse=True)
        return search_results[:limit]

    def hybrid_search(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[list[str]] = None,
        limit: int = 10,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ) -> list[SearchResult]:
        """
        混合搜索：结合语义搜索和关键词匹配

        Args:
            query: 搜索查询
            category: 过滤分类
            tags: 过滤标签
            limit: 返回结果数量
            semantic_weight: 语义搜索权重
            keyword_weight: 关键词匹配权重

        Returns:
            搜索结果列表
        """
        # 获取语义搜索结果
        semantic_results = self.search(
            query=query,
            category=category,
            tags=tags,
            limit=limit * 2,
            min_score=0.3,  # 降低阈值以获取更多候选
        )

        # 如果没有语义搜索结果，直接返回
        if not semantic_results:
            return []

        # 计算关键词匹配分数
        query_keywords = self._extract_keywords(query)

        for result in semantic_results:
            keyword_score = self._compute_keyword_score(
                result.document, query_keywords
            )
            # 加权融合分数
            result.score = (
                result.score * semantic_weight + keyword_score * keyword_weight
            )

        # 重新排序
        semantic_results.sort(key=lambda x: x.score, reverse=True)
        return semantic_results[:limit]

    def _extract_keywords(self, text: str) -> list[str]:
        """提取关键词"""
        # 简单的中文分词：按标点和空格分割
        words = re.split(r"[，。！？；：、\s]+", text)
        # 过滤掉短词和停用词
        stopwords = {"的", "了", "是", "在", "和", "与", "及", "等", "个", "这", "那"}
        keywords = [w for w in words if len(w) > 1 and w not in stopwords]
        return keywords

    def _compute_keyword_score(
        self, document: KnowledgeDocument, keywords: list[str]
    ) -> float:
        """计算关键词匹配分数"""
        if not keywords:
            return 0.0

        content = document.content.lower()
        title = document.title.lower()

        matches = 0
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in title:
                matches += 2  # 标题匹配权重更高
            elif keyword_lower in content:
                matches += 1

        return min(1.0, matches / len(keywords))

    def _generate_highlights(self, content: str, query: str) -> list[str]:
        """生成高亮片段"""
        keywords = self._extract_keywords(query)
        if not keywords:
            return []

        highlights = []
        content_lower = content.lower()

        for keyword in keywords:
            keyword_lower = keyword.lower()
            start = content_lower.find(keyword_lower)
            if start != -1:
                # 提取上下文
                context_start = max(0, start - 50)
                context_end = min(len(content), start + len(keyword) + 150)
                highlight = content[context_start:context_end].strip()
                if len(highlight) > self.highlight_max_length:
                    highlight = highlight[: self.highlight_max_length] + "..."
                if highlight and highlight not in highlights:
                    highlights.append(highlight)

        return highlights[:3]  # 最多 3 个高亮片段

    def _generate_reason(
        self, document: KnowledgeDocument, score: float, query: str
    ) -> str:
        """生成推荐理由"""
        reasons = []

        if score > 0.8:
            reasons.append("高度相关")
        elif score > 0.6:
            reasons.append("较为相关")
        else:
            reasons.append("部分相关")

        if query.lower() in document.title.lower():
            reasons.append("标题匹配")

        if document.tags:
            query_keywords = self._extract_keywords(query)
            matching_tags = [t for t in document.tags if any(k in t for k in query_keywords)]
            if matching_tags:
                reasons.append(f"标签匹配：{', '.join(matching_tags[:2])}")

        return " | ".join(reasons) if reasons else "语义匹配"

    def suggest_related(
        self,
        document_id: str,
        limit: int = 5,
    ) -> list[SearchResult]:
        """
        推荐相关文档

        Args:
            document_id: 文档 ID
            limit: 推荐数量

        Returns:
            相关文档列表
        """
        # 获取原文档
        doc_data = self.vector_store.get_document(document_id)
        if not doc_data:
            return []

        # 使用原文档内容进行相似性搜索
        content = doc_data.get("content", "")
        return self.search(query=content, limit=limit + 1, min_score=0.4)[:limit]

    def search_by_category(
        self,
        category: str,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        按分类搜索文档

        Args:
            category: 分类名称
            limit: 返回数量
            status: 文档状态过滤

        Returns:
            文档列表
        """
        return self.vector_store.list_documents(
            category=category,
            status=status,
            limit=limit,
        )

    def get_search_stats(self) -> dict[str, Any]:
        """获取搜索统计信息"""
        collection_stats = self.vector_store.get_collection_stats()
        return {
            "total_documents": collection_stats.get("count", 0),
            "embedding_model": self.embedding_service.model_name,
            "embedding_dim": self.embedding_service.embedding_dim,
        }


# 默认搜索引擎实例
semantic_search = SemanticSearch()
