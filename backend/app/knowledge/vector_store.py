"""
VectorStore — ChromaDB 向量存储
"""
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.config import Settings


class VectorStore:
    """
    ChromaDB 向量存储

    功能:
    - 添加文档
    - 语义搜索
    - 持久化存储
    """

    def __init__(self, persist_directory: str = "./data/chroma", collection_name: str = "knowledge"):
        """
        初始化向量存储

        Args:
            persist_directory: 持久化目录
            collection_name: 集合名称
        """
        self.client = chromadb.Client(Settings(
            is_persistent=True,
            persist_directory=persist_directory
        ))
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_document(self, doc_id: str, text: str, metadata: Optional[Dict] = None, embedding: Optional[List[float]] = None) -> None:
        """
        添加文档
        
        Args:
            doc_id: 文档 ID
            text: 文档内容
            metadata: 元数据
            embedding: 嵌入向量（必须，ChromaDB 需要一致维度）
        """
        params = {
            "ids": [doc_id],
            "documents": [text],
            "metadatas": [metadata or {}]
        }
        if embedding is not None:
            params["embeddings"] = [embedding]
        
        self.collection.add(**params)
    
    def search(self, query_embedding: List[float], limit: int = 5) -> List[Dict]:
        """
        语义搜索
        
        Args:
            query_embedding: 查询嵌入向量
            limit: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit
        )
        
        if not results['ids'] or not results['ids'][0]:
            return []
        
        return [
            {
                "id": results['ids'][0][i],
                "document": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i] if 'distances' in results else None
            }
            for i in range(len(results['ids'][0]))
        ]
    
    def delete_document(self, doc_id: str) -> None:
        """删除文档"""
        self.collection.delete(ids=[doc_id])
    
    def count(self) -> int:
        """获取文档数量"""
        return self.collection.count()
    
    def clear(self) -> None:
        """清空集合"""
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"}
        )
