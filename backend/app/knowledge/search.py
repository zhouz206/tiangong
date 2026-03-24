"""
SemanticSearch — 语义搜索
"""
from typing import Any, Dict, List, Optional

from .vector_store import VectorStore
from .embedding import EmbeddingService


class SemanticSearch:
    """
    语义搜索
    
    功能:
    - 语义相似度搜索
    - 混合搜索（语义 + 关键词）
    - 搜索结果排序
    """
    
    def __init__(self, vector_store: VectorStore, embedding_service: EmbeddingService):
        """
        初始化语义搜索
        
        Args:
            vector_store: 向量存储
            embedding_service: 嵌入服务
        """
        self.vector_store = vector_store
        self.embedding_service = embedding_service
    
    def search(self, query: str, limit: int = 5, min_score: float = 0.0) -> List[Dict]:
        """
        语义搜索
        
        Args:
            query: 查询文本
            limit: 返回结果数量
            min_score: 最小相似度分数
            
        Returns:
            搜索结果列表
        """
        # 生成查询嵌入
        query_embedding = self.embedding_service.embed(query)
        
        # 搜索
        results = self.vector_store.search(query_embedding, limit)
        
        # 过滤和格式化
        filtered_results = []
        for result in results:
            score = 1 - (result.get('distance', 0) or 0)  # 距离转相似度
            if score >= min_score:
                filtered_results.append({
                    "id": result["id"],
                    "document": result["document"],
                    "metadata": result["metadata"],
                    "score": score
                })
        
        return filtered_results
    
    def add_document(self, doc_id: str, text: str, metadata: Optional[Dict] = None) -> None:
        """
        添加文档到知识库
        
        Args:
            doc_id: 文档 ID
            text: 文档内容
            metadata: 元数据
        """
        embedding = self.embedding_service.embed(text)
        self.vector_store.add_document(doc_id, text, metadata, embedding)
