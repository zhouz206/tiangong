"""
测试分类和标签管理
"""
import pytest
from app.knowledge.taxonomy import TaxonomyManager
from app.knowledge.models import Category, Tag


class TestTaxonomyManager:
    """测试分类管理器"""

    @pytest.fixture
    def taxonomy(self):
        """创建分类管理器实例"""
        return TaxonomyManager()

    def test_get_categories(self, taxonomy):
        """测试获取所有分类"""
        categories = taxonomy.get_categories()

        assert isinstance(categories, list)
        assert len(categories) > 0
        assert all(isinstance(c, Category) for c in categories)

    def test_get_category(self, taxonomy):
        """测试获取单个分类"""
        category = taxonomy.get_category("cat_tech")

        assert category is not None
        assert category.id == "cat_tech"
        assert category.name == "技术文档"

    def test_get_category_not_found(self, taxonomy):
        """测试获取不存在的分类"""
        category = taxonomy.get_category("non_existent")
        assert category is None

    def test_get_category_by_name(self, taxonomy):
        """测试按名称获取分类"""
        category = taxonomy.get_category_by_name("技术文档")

        assert category is not None
        assert category.id == "cat_tech"

    def test_create_category(self, taxonomy):
        """测试创建分类"""
        category = taxonomy.create_category(
            name="新分类",
            description="这是一个新分类",
            rules=["规则 1", "规则 2"],
        )

        assert category.id.startswith("cat_")
        assert category.name == "新分类"
        assert category.description == "这是一个新分类"
        assert category.rules == ["规则 1", "规则 2"]

        # 验证分类被添加
        retrieved = taxonomy.get_category(category.id)
        assert retrieved is not None
        assert retrieved.name == "新分类"

    def test_create_category_with_parent(self, taxonomy):
        """测试创建带父分类的子分类"""
        parent = taxonomy.get_category("cat_tech")

        child = taxonomy.create_category(
            name="子分类",
            description="",
            parent=parent.id,
        )

        assert child.parent == parent.id
        assert child.id in parent.subcategories

    def test_update_category(self, taxonomy):
        """测试更新分类"""
        category = taxonomy.create_category(
            name="原始名称",
            description="原始描述",
        )

        success = taxonomy.update_category(
            category.id,
            name="新名称",
            description="新描述",
            rules=["新规则"],
        )

        assert success is True

        updated = taxonomy.get_category(category.id)
        assert updated.name == "新名称"
        assert updated.description == "新描述"
        assert updated.rules == ["新规则"]

    def test_delete_category(self, taxonomy):
        """测试删除分类"""
        category = taxonomy.create_category(
            name="待删除",
            description="",
        )

        success = taxonomy.delete_category(category.id)

        assert success is True
        assert taxonomy.get_category(category.id) is None

    def test_delete_category_with_children(self, taxonomy):
        """测试删除有子分类的分类（应该失败）"""
        parent = taxonomy.create_category(
            name="父分类",
            description="",
        )
        taxonomy.create_category(
            name="子分类",
            description="",
            parent=parent.id,
        )

        success = taxonomy.delete_category(parent.id)

        assert success is False

    def test_get_tags(self, taxonomy):
        """测试获取所有标签"""
        tags = taxonomy.get_tags()

        assert isinstance(tags, list)
        assert len(tags) > 0
        assert all(isinstance(t, Tag) for t in tags)

    def test_get_tags_by_category(self, taxonomy):
        """测试按分类获取标签"""
        tags = taxonomy.get_tags(category="优先级")

        assert isinstance(tags, list)
        assert all(t.category == "优先级" for t in tags)

    def test_get_tag(self, taxonomy):
        """测试获取单个标签"""
        tag = taxonomy.get_tag("tag_urgent")

        assert tag is not None
        assert tag.id == "tag_urgent"
        assert tag.name == "紧急"

    def test_get_tag_by_name(self, taxonomy):
        """测试按名称获取标签"""
        tag = taxonomy.get_tag_by_name("紧急")

        assert tag is not None
        assert tag.id == "tag_urgent"

    def test_create_tag(self, taxonomy):
        """测试创建标签"""
        tag = taxonomy.create_tag(
            name="新标签",
            category="自定义",
        )

        assert tag.id.startswith("tag_")
        assert tag.name == "新标签"
        assert tag.category == "自定义"
        assert tag.usage_count == 0

    def test_update_tag_usage(self, taxonomy):
        """测试更新标签使用次数"""
        tag = taxonomy.get_tag("tag_urgent")
        initial_count = tag.usage_count

        success = taxonomy.update_tag_usage(tag.id, increment=5)

        assert success is True
        assert taxonomy.get_tag(tag.id).usage_count == initial_count + 5

    def test_delete_tag(self, taxonomy):
        """测试删除标签"""
        tag = taxonomy.create_tag(
            name="待删除",
        )

        success = taxonomy.delete_tag(tag.id)

        assert success is True
        assert taxonomy.get_tag(tag.id) is None

    def test_auto_categorize_tech(self, taxonomy):
        """测试自动分类 - 技术文档"""
        content = "这是一个关于 Python 编程和 API 开发的教程"
        category_id = taxonomy.auto_categorize(content)

        assert category_id == "cat_tech"

    def test_auto_categorize_product(self, taxonomy):
        """测试自动分类 - 产品文档"""
        content = "产品需求文档，包含用户功能和特性说明"
        category_id = taxonomy.auto_categorize(content)

        assert category_id == "cat_product"

    def test_auto_categorize_research(self, taxonomy):
        """测试自动分类 - 研究报告"""
        content = "市场调研报告，分析竞品和市场趋势"
        category_id = taxonomy.auto_categorize(content)

        assert category_id == "cat_research"

    def test_auto_categorize_meeting(self, taxonomy):
        """测试自动分类 - 会议记录"""
        content = "会议纪要，记录了讨论内容和决策"
        category_id = taxonomy.auto_categorize(content)

        assert category_id == "cat_meeting"

    def test_auto_categorize_no_match(self, taxonomy):
        """测试自动分类 - 无匹配"""
        content = "这是一些随机内容，没有特定分类关键词"
        category_id = taxonomy.auto_categorize(content)

        # 可能返回 None 或默认分类
        assert category_id is None or isinstance(category_id, str)

    def test_auto_tag(self, taxonomy):
        """测试自动打标签"""
        content = "这是一个紧急的 API 教程，需要尽快处理"
        tags = taxonomy.auto_tag(content, max_tags=3)

        assert isinstance(tags, list)
        assert len(tags) <= 3

    def test_auto_tag_with_title(self, taxonomy):
        """测试自动打标签（包含标题）"""
        content = "文档内容"
        title = "紧急 API 指南"
        tags = taxonomy.auto_tag(content, title=title, max_tags=5)

        assert isinstance(tags, list)

    def test_suggest_tags_from_content(self, taxonomy):
        """测试从内容推荐标签"""
        content = "这是一个关于机器学习和深度学习的教程，涉及神经网络和算法"
        existing_tags = ["tag_tutorial"]

        suggested = taxonomy.suggest_tags_from_content(content, existing_tags)

        assert isinstance(suggested, list)
        assert len(suggested) <= 5

    def test_add_relationship(self, taxonomy):
        """测试添加关系"""
        relationship = taxonomy.add_relationship(
            source_id="cat_tech",
            target_id="cat_product",
            relationship_type="related_to",
            strength=0.8,
        )

        assert relationship.source_id == "cat_tech"
        assert relationship.target_id == "cat_product"
        assert relationship.relationship_type == "related_to"
        assert relationship.strength == 0.8

    def test_get_related(self, taxonomy):
        """测试获取相关项"""
        taxonomy.add_relationship(
            source_id="item_1",
            target_id="item_2",
            relationship_type="related_to",
        )
        taxonomy.add_relationship(
            source_id="item_1",
            target_id="item_3",
            relationship_type="depends_on",
        )

        related = taxonomy.get_related("item_1")

        assert len(related) == 2

        # 按关系类型过滤
        related_depends = taxonomy.get_related(
            "item_1",
            relationship_type="depends_on",
        )
        assert len(related_depends) == 1

    def test_get_taxonomy_tree(self, taxonomy):
        """测试获取分类树"""
        tree = taxonomy.get_taxonomy_tree()

        assert isinstance(tree, dict)
        # 应该有根分类
        assert len(tree) > 0

    def test_export_taxonomy(self, taxonomy):
        """测试导出分类体系"""
        export = taxonomy.export_taxonomy()

        assert "categories" in export
        assert "tags" in export
        assert "relationships" in export

        assert isinstance(export["categories"], list)
        assert isinstance(export["tags"], list)
        assert isinstance(export["relationships"], list)
