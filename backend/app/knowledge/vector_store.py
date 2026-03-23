"""
ChromaDB 向量存储实现

提供向量数据库的增删改查操作，支持持久化存储。
"""
import chromadb
from chromadb.config import Settings
from typing import Any, Optional
import asyncio
from datetime import datetime
import os

from .models import KnowledgeDocument, DocumentStatus, SearchResult, SearchQuery


class VectorStore:
    """
    ChromaDB 向量存储类

    负责文档向量的存储、检索和管理。
    """

    def __init__(
        self,
        persist_directory: str = "./data/chroma",
        collection_name: str = "knowledge_documents",
    ):
        """
        初始化向量存储

        Args:
            persist_directory: 持久化目录
            collection_name: 集合名称
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # 确保持久化目录存在
        os.makedirs(persist_directory, exist_ok=True)

        # 初始化 ChromaDB 客户端（持久化模式）
        self.client = chromadb.PersistentClient(path=persist_directory)

        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Knowledge documents with embeddings"},
        )

    def add_document(
        self,
        document: KnowledgeDocument,
        embedding: list[float],
    ) -> bool:
        """
        添加文档到向量存储

        Args:
            document: 知识文档
            embedding: 文档的向量嵌入

        Returns:
            是否添加成功
        """
        try:
            # 准备元数据
            metadata = {
                "title": document.title,
                "category": document.category,
                "tags": ",".join(document.tags) if document.tags else "",
                "status": document.status,
                "version": document.version,
                "content_type": document.content_type,
                "created_at": document.created_at.isoformat(),
                "updated_at": document.updated_at.isoformat(),
            }

            # 添加到集合
            self.collection.add(
                ids=[document.id],
                embeddings=[embedding],
                documents=[document.content],
                metadatas=[metadata],
            )

            return True
        except Exception as e:
            print(f"Error adding document to vector store: {e}")
            return False

    def update_document(
        self,
        document: KnowledgeDocument,
        embedding: list[float],
    ) -> bool:
        """
        更新文档的向量嵌入

        Args:
            document: 知识文档
            embedding: 新的向量嵌入

        Returns:
            是否更新成功
        """
        try:
            metadata = {
                "title": document.title,
                "category": document.category,
                "tags": ",".join(document.tags) if document.tags else "",
                "status": document.status,
                "version": document.version,
                "content_type": document.content_type,
                "updated_at": document.updated_at.isoformat(),
            }

            self.collection.update(
                ids=[document.id],
                embeddings=[embedding],
                documents=[document.content],
                metadatas=[metadata],
            )

            return True
        except Exception as e:
            print(f"Error updating document in vector store: {e}")
            return False

    def delete_document(self, document_id: str) -> bool:
        """
        删除文档

        Args:
            document_id: 文档 ID

        Returns:
            是否删除成功
        """
        try:
            self.collection.delete(ids=[document_id])
            return True
        except Exception as e:
            print(f"Error deleting document from vector store: {e}")
            return False

    def search(
        self,
        query_embedding: list[float],
        n_results: int = 10,
        category: Optional[str] = None,
        tags: Optional[list[str]] = None,
        min_score: float = 0.5,
    ) -> list[dict[str, Any]]:
        """
        向量相似度搜索

        Args:
            query_embedding: 查询向量
            n_results: 返回结果数量
            category: 过滤分类
            tags: 过滤标签
            min_score: 最小相似度分数

        Returns:
            搜索结果列表
        """
        try:
            # 构建 where 过滤条件
            where = None
            if category:
                where = {"category": category}

            # 执行搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"],
            )

            # 处理结果
            search_results = []
            if results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    distance = results["distances"][0][i] if results["distances"] else 0
                    # ChromaDB 返回的是距离，转换为相似度分数
                    score = 1 - distance

                    if score >= min_score:
                        metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                        search_results.append({
                            "id": doc_id,
                            "content": results["documents"][0][i] if results["documents"] else "",
                            "metadata": metadata,
                            "score": score,
                        })

            return search_results
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return []

    def get_document(self, document_id: str) -> Optional[dict[str, Any]]:
        """
        获取单个文档

        Args:
            document_id: 文档 ID

        Returns:
            文档信息，不存在返回 None
        """
        try:
            results = self.collection.get(
                ids=[document_id],
                include=["documents", "metadatas", "embeddings"],
            )

            if results["ids"] and results["ids"][0]:
                return {
                    "id": results["ids"][0],
                    "content": results["documents"][0] if results["documents"] else "",
                    "metadata": results["metadatas"][0] if results["metadatas"] else {},
                    "embedding": results["embeddings"][0] if results["embeddings"] else None,
                }
            return None
        except Exception as e:
            print(f"Error getting document from vector store: {e}")
            return None

    def list_documents(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        列出文档

        Args:
            category: 过滤分类
            status: 过滤状态
            limit: 返回数量限制

        Returns:
            文档列表
        """
        try:
            # 构建过滤条件
            where = {}
            if category:
                where["category"] = category
            if status:
                where["status"] = status

            where_clause = None if not where else where

            results = self.collection.get(
                where=where_clause,
                include=["metadatas"],
                limit=limit,
            )

            documents = []
            if results["ids"]:
                for i, doc_id in enumerate(results["ids"]):
                    metadata = results["metadatas"][i] if results["metadatas"] else {}
                    documents.append({
                        "id": doc_id,
                        "metadata": metadata,
                    })

            return documents
        except Exception as e:
            print(f"Error listing documents: {e}")
            return []

    def get_collection_stats(self) -> dict[str, Any]:
        """
        获取集合统计信息

        Returns:
            统计信息字典
        """
        try:
            return {
                "name": self.collection.name,
                "count": self.collection.count(),
                "metadata": self.collection.metadata,
            }
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {"error": str(e)}

    def reset_collection(self) -> bool:
        """
        重置集合（删除所有数据）

        Returns:
            是否成功
        """
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Knowledge documents with embeddings"},
            )
            return True
        except Exception as e:
            print(f"Error resetting collection: {e}")
            return False


# 默认向量存储实例
vector_store = VectorStore()
