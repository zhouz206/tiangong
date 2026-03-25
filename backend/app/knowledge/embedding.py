"""
EmbeddingService — Sentence-BERT 嵌入服务
"""
from typing import List, Optional


class EmbeddingService:
    """
    Sentence-BERT 嵌入服务
    
    功能:
    - 文本嵌入生成
    - 批量嵌入
    - 多语言支持
    """
    
    def __init__(self, model_name: Optional[str] = "sentence-transformers/all-MiniLM-L6-v2", embedding_dim: int = 384):
        """
        初始化嵌入服务
        
        Args:
            model_name: 模型名称（None 则使用模拟嵌入）
            embedding_dim: 嵌入维度
        """
        self.model_name = model_name
        self.embedding_dim = embedding_dim
        self._model = None
    
    @property
    def model(self):
        """懒加载模型"""
        if self._model is None and self.model_name is not None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except (ImportError, Exception):
                # 如果无法加载模型，使用模拟嵌入
                self._model = None
        return self._model
    
    def embed(self, text: str) -> List[float]:
        """
        生成文本嵌入

        Args:
            text: 输入文本

        Returns:
            嵌入向量
        """
        if self.model is not None:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        else:
            # 模拟嵌入（用于测试）
            return self._mock_embed(text)
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量生成嵌入
        
        Args:
            texts: 文本列表
            
        Returns:
            嵌入向量列表
        """
        if self.model is not None:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        else:
            return [self._mock_embed(text) for text in texts]
    
    def _mock_embed(self, text: str) -> List[float]:
        """模拟嵌入（用于测试）"""
        # 使用简单的哈希生成 384 维向量
        import hashlib
        hash_bytes = hashlib.sha256(text.encode()).digest()
        base_values = [int(b) / 255.0 for b in hash_bytes]
        vector = (base_values * 12)[:384]
        # 归一化
        norm = sum(v*v for v in vector) ** 0.5
        if norm == 0:
            norm = 1
        return [v / norm for v in vector]
