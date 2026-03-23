"""
Sentence-BERT 文档嵌入实现

使用预训练模型生成文档的向量嵌入。
"""
from sentence_transformers import SentenceTransformer
from typing import Optional, Union
import numpy as np
import hashlib


class EmbeddingService:
    """
    文档嵌入服务类

    使用 Sentence-BERT 模型生成文本的向量表示。
    """

    # 可用的预训练模型
    AVAILABLE_MODELS = {
        "zh": "paraphrase-multilingual-MiniLM-L12-v2",  # 支持中文的多语言模型
        "en": "all-MiniLM-L6-v2",  # 英文优化模型
        "large": "paraphrase-multilingual-mpnet-base-v2",  # 更大更准确的多语言模型
    }

    def __init__(self, model_name: str = "zh"):
        """
        初始化嵌入服务

        Args:
            model_name: 模型名称或预设键 (zh/en/large)
        """
        # 解析模型名称
        if model_name in self.AVAILABLE_MODELS:
            self.model_name = self.AVAILABLE_MODELS[model_name]
        else:
            self.model_name = model_name

        self._model: Optional[SentenceTransformer] = None
        self._embedding_dim: Optional[int] = None

    @property
    def model(self) -> SentenceTransformer:
        """懒加载模型"""
        if self._model is None:
            print(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            # 获取嵌入维度
            test_embedding = self._model.encode("test")
            self._embedding_dim = len(test_embedding)
        return self._model

    @property
    def embedding_dim(self) -> int:
        """获取嵌入维度"""
        if self._embedding_dim is None:
            _ = self.model  # 触发模型加载
        return self._embedding_dim

    def embed_text(self, text: str) -> list[float]:
        """
        生成文本的向量嵌入

        Args:
            text: 输入文本

        Returns:
            向量嵌入列表
        """
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,  # 归一化便于余弦相似度计算
        )
        return embedding.tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        批量生成文本的向量嵌入

        Args:
            texts: 文本列表

        Returns:
            向量嵌入列表的列表
        """
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=len(texts) > 10,  # 大量文本时显示进度
        )
        return embeddings.tolist()

    def compute_similarity(
        self,
        embedding1: list[float],
        embedding2: list[float],
    ) -> float:
        """
        计算两个向量的余弦相似度

        Args:
            embedding1: 第一个向量
            embedding2: 第二个向量

        Returns:
            相似度分数 (0-1)
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # 余弦相似度
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)

    def compute_similarities(
        self,
        query_embedding: list[float],
        document_embeddings: list[list[float]],
    ) -> list[float]:
        """
        计算查询向量与多个文档向量的相似度

        Args:
            query_embedding: 查询向量
            document_embeddings: 文档向量列表

        Returns:
            相似度分数列表
        """
        similarities = []
        for doc_emb in document_embeddings:
            sim = self.compute_similarity(query_embedding, doc_emb)
            similarities.append(sim)
        return similarities

    def generate_document_id(self, content: str) -> str:
        """
        基于内容生成文档 ID

        Args:
            content: 文档内容

        Returns:
            文档 ID (哈希值前 16 位)
        """
        hash_obj = hashlib.sha256(content.encode("utf-8"))
        return f"doc_{hash_obj.hexdigest()[:16]}"

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> list[str]:
        """
        将长文本分块

        Args:
            text: 输入文本
            chunk_size: 每块字符数
            overlap: 块间重叠字符数

        Returns:
            文本块列表
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # 尝试在句子边界处切分
            if end < len(text):
                last_period = chunk.rfind(".")
                last_newline = chunk.rfind("\n")
                split_point = max(last_period, last_newline)
                if split_point > chunk_size // 2:
                    chunk = chunk[: split_point + 1]
                    end = start + split_point + 1

            chunks.append(chunk.strip())
            start = end - overlap

        return chunks

    def embed_document_with_chunks(
        self,
        content: str,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> tuple[list[float], list[dict]]:
        """
        对长文档进行分块嵌入

        Args:
            content: 文档内容
            chunk_size: 每块大小
            overlap: 重叠大小

        Returns:
            (文档整体嵌入，分块信息列表)
        """
        chunks = self.chunk_text(content, chunk_size, overlap)

        # 生成每个块的嵌入
        chunk_embeddings = self.embed_texts(chunks)

        # 文档整体嵌入：所有块嵌入的平均值
        doc_embedding = np.mean(chunk_embeddings, axis=0).tolist()

        # 分块信息
        chunk_info = [
            {
                "chunk_id": f"chunk_{i}",
                "content": chunk,
                "embedding": emb,
            }
            for i, (chunk, emb) in enumerate(zip(chunks, chunk_embeddings))
        ]

        return doc_embedding, chunk_info


# 默认嵌入服务实例
embedding_service = EmbeddingService(model_name="zh")
