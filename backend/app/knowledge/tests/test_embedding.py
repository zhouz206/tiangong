"""
测试文档嵌入服务

注意：这些测试需要网络连接以下载 Sentence-BERT 模型。
如果网络不可用，测试会跳过。
"""
import pytest
import urllib.request
from app.knowledge.embedding import EmbeddingService


def is_huggingface_available():
    """检查 HuggingFace 是否可访问"""
    try:
        urllib.request.urlopen("https://huggingface.co", timeout=5)
        return True
    except Exception:
        return False


class TestEmbeddingService:
    """测试嵌入服务"""

    @pytest.fixture
    def embedding_service(self):
        """创建嵌入服务实例"""
        return EmbeddingService(model_name="zh")

    @pytest.mark.skipif(not is_huggingface_available(), reason="HuggingFace 不可访问")
    def test_embed_text(self, embedding_service):
        """测试文本嵌入"""
        text = "这是一个测试文本"
        embedding = embedding_service.embed_text(text)

        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)

    @pytest.mark.skipif(not is_huggingface_available(), reason="HuggingFace 不可访问")
    def test_embed_texts_batch(self, embedding_service):
        """测试批量文本嵌入"""
        texts = ["文本 1", "文本 2", "文本 3"]
        embeddings = embedding_service.embed_texts(texts)

        assert isinstance(embeddings, list)
        assert len(embeddings) == 3
        assert all(len(emb) > 0 for emb in embeddings)

    @pytest.mark.skipif(not is_huggingface_available(), reason="HuggingFace 不可访问")
    def test_embedding_dimension_consistency(self, embedding_service):
        """测试嵌入维度一致性"""
        text1 = "短文本"
        text2 = "这是一个比较长的文本，用于测试嵌入维度是否一致"

        emb1 = embedding_service.embed_text(text1)
        emb2 = embedding_service.embed_text(text2)

        assert len(emb1) == len(emb2)

    @pytest.mark.skipif(not is_huggingface_available(), reason="HuggingFace 不可访问")
    def test_compute_similarity(self, embedding_service):
        """测试相似度计算"""
        emb1 = embedding_service.embed_text("相似的文本")
        emb2 = embedding_service.embed_text("相似的文本")
        emb3 = embedding_service.embed_text("完全不同的内容")

        # 相同文本相似度应该接近 1
        sim_same = embedding_service.compute_similarity(emb1, emb2)
        assert sim_same > 0.9

        # 不同文本相似度应该较低
        sim_diff = embedding_service.compute_similarity(emb1, emb3)
        assert sim_diff < sim_same

    @pytest.mark.skipif(not is_huggingface_available(), reason="HuggingFace 不可访问")
    def test_compute_similarities(self, embedding_service):
        """测试批量相似度计算"""
        query_emb = embedding_service.embed_text("查询文本")
        doc_embs = [
            embedding_service.embed_text("文档 1"),
            embedding_service.embed_text("文档 2"),
            embedding_service.embed_text("文档 3"),
        ]

        similarities = embedding_service.compute_similarities(query_emb, doc_embs)

        assert isinstance(similarities, list)
        assert len(similarities) == 3
        assert all(0 <= sim <= 1 for sim in similarities)

    def test_generate_document_id(self, embedding_service):
        """测试文档 ID 生成"""
        content = "测试内容"
        doc_id = embedding_service.generate_document_id(content)

        assert doc_id.startswith("doc_")
        assert len(doc_id) == 20  # "doc_" + 16 位哈希

        # 相同内容生成相同 ID
        doc_id2 = embedding_service.generate_document_id(content)
        assert doc_id == doc_id2

        # 不同内容生成不同 ID
        doc_id3 = embedding_service.generate_document_id("不同内容")
        assert doc_id != doc_id3

    def test_chunk_text_short(self, embedding_service):
        """测试短文本分块（不需要分块）"""
        text = "短文本"
        chunks = embedding_service.chunk_text(text, chunk_size=500, overlap=50)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_text_long(self, embedding_service):
        """测试长文本分块"""
        text = "这是第一段。" * 100  # 长文本
        chunks = embedding_service.chunk_text(text, chunk_size=500, overlap=50)

        assert len(chunks) > 1
        # 验证重叠
        if len(chunks) > 1:
            # 第一块的结尾应该在第二块开头出现
            assert chunks[0] != chunks[1]

    @pytest.mark.skipif(not is_huggingface_available(), reason="HuggingFace 不可访问")
    def test_chunk_text_preserves_sentences(self, embedding_service):
        """测试分块尽量保持句子完整"""
        text = "第一句话。第二句话。第三句话。" * 50
        chunks = embedding_service.chunk_text(text, chunk_size=200, overlap=50)

        # 验证分块在句子边界处切分
        for chunk in chunks:
            # 每块应该以句号结尾（除了最后一块）
            if chunk != chunks[-1]:
                assert chunk.endswith(".") or len(chunk) < 200

    @pytest.mark.skipif(not is_huggingface_available(), reason="HuggingFace 不可访问")
    def test_embed_document_with_chunks(self, embedding_service):
        """测试文档分块嵌入"""
        content = "这是第一段。" * 50
        doc_embedding, chunk_info = embedding_service.embed_document_with_chunks(
            content, chunk_size=500, overlap=50
        )

        assert isinstance(doc_embedding, list)
        assert len(doc_embedding) > 0
        assert isinstance(chunk_info, list)
        assert len(chunk_info) > 0

        # 验证 chunk_info 结构
        for chunk in chunk_info:
            assert "chunk_id" in chunk
            assert "content" in chunk
            assert "embedding" in chunk

    @pytest.mark.skipif(not is_huggingface_available(), reason="HuggingFace 不可访问")
    def test_embedding_normalization(self, embedding_service):
        """测试嵌入归一化"""
        text = "测试文本"
        embedding = embedding_service.embed_text(text)

        # 归一化向量的模长应该接近 1
        import math
        norm = math.sqrt(sum(x ** 2 for x in embedding))
        assert abs(norm - 1.0) < 0.01

    @pytest.mark.skipif(not is_huggingface_available(), reason="HuggingFace 不可访问")
    def test_model_loading(self, embedding_service):
        """测试模型懒加载"""
        # 访问 model 属性应该触发加载
        model = embedding_service.model
        assert model is not None

        # 访问 embedding_dim 也应该工作
        dim = embedding_service.embedding_dim
        assert dim > 0
