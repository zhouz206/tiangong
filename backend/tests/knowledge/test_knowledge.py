"""
知识库测试（简化版 - 不依赖 ChromaDB）
"""
import pytest
from app.knowledge.embedding import EmbeddingService
from app.knowledge.taxonomy import TaxonomyManager


class TestEmbeddingService:
    """EmbeddingService 测试"""
    
    def test_embed(self):
        """测试嵌入生成"""
        service = EmbeddingService(model_name=None)  # 使用模拟嵌入
        embedding = service.embed("测试文本")
        
        assert len(embedding) == 384
        assert isinstance(embedding, list)
        assert all(isinstance(v, float) for v in embedding)
    
    def test_embed_batch(self):
        """测试批量嵌入"""
        service = EmbeddingService(model_name=None)
        embeddings = service.embed_batch(["文本 1", "文本 2", "文本 3"])
        
        assert len(embeddings) == 3
        assert all(len(e) == 384 for e in embeddings)
    
    def test_embed_consistency(self):
        """测试嵌入一致性"""
        service = EmbeddingService(model_name=None)
        
        embedding1 = service.embed("相同文本")
        embedding2 = service.embed("相同文本")
        
        assert embedding1 == embedding2


class TestTaxonomyManager:
    """TaxonomyManager 测试"""
    
    def test_get_categories(self):
        """测试获取分类"""
        manager = TaxonomyManager()
        categories = manager.get_categories()
        
        assert len(categories) >= 5
        assert any(cat["name"] == "技术文档" for cat in categories)
        assert any(cat["name"] == "产品文档" for cat in categories)
    
    def test_create_category(self):
        """测试创建分类"""
        manager = TaxonomyManager()
        category = manager.create_category("custom", "自定义分类", "描述")
        
        assert category["id"] == "custom"
        assert category["name"] == "自定义分类"
    
    def test_create_tag(self):
        """测试创建标签"""
        manager = TaxonomyManager()
        tag = manager.create_tag("python", "Python", "tech_doc")
        
        assert tag["id"] == "python"
        assert tag["name"] == "Python"
    
    def test_get_tags(self):
        """测试获取标签"""
        manager = TaxonomyManager()
        manager.create_tag("test_tag", "测试标签")
        
        tags = manager.get_tags()
        assert len(tags) >= 1
    
    def test_auto_categorize_tech(self):
        """测试自动分类 - 技术文档"""
        manager = TaxonomyManager()
        
        tech_text = "这是一篇关于 Python 代码和架构设计的技术文档"
        category = manager.auto_categorize(tech_text)
        
        assert category == "tech_doc"
    
    def test_auto_categorize_product(self):
        """测试自动分类 - 产品文档"""
        manager = TaxonomyManager()
        
        product_text = "这是一篇产品需求文档，包含功能设计和用户故事"
        category = manager.auto_categorize(product_text)
        
        assert category == "product_doc"
    
    def test_auto_categorize_meeting(self):
        """测试自动分类 - 会议记录"""
        manager = TaxonomyManager()
        
        meeting_text = "会议纪要：讨论了项目进度和下一步计划"
        category = manager.auto_categorize(meeting_text)
        
        assert category == "meeting"
    
    def test_auto_tag_urgent(self):
        """测试自动打标签 - 紧急"""
        manager = TaxonomyManager()
        
        text = "这是一篇紧急的 Python 教程指南"
        tags = manager.auto_tag(text)
        
        assert "urgent" in tags
        assert "guide" in tags
    
    def test_auto_tag_best_practice(self):
        """测试自动打标签 - 最佳实践"""
        manager = TaxonomyManager()
        
        text = "Python 开发最佳实践和经验总结"
        tags = manager.auto_tag(text)
        
        assert "best_practice" in tags
