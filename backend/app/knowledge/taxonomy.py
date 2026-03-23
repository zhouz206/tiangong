"""
知识分类和标签系统

实现文档分类、标签管理、自动分类等功能。
"""
from typing import Any, Optional
from datetime import datetime
import re
from collections import Counter

from .models import (
    KnowledgeDocument,
    Category,
    Tag,
    DocumentStatus,
    TaxonomyRelationship,
)
from .embedding import EmbeddingService, embedding_service


class TaxonomyManager:
    """
    分类和标签管理器

    负责知识分类体系的管理、标签分配和自动分类。
    """

    # 默认分类体系
    DEFAULT_CATEGORIES = [
        Category(
            id="cat_tech",
            name="技术文档",
            description="技术相关的文档和资料",
            rules=["包含代码", "技术方案", "架构设计"],
        ),
        Category(
            id="cat_product",
            name="产品文档",
            description="产品需求、设计、说明文档",
            rules=["需求文档", "产品设计", "用户手册"],
        ),
        Category(
            id="cat_research",
            name="研究报告",
            description="调研报告、分析报告",
            rules=["市场分析", "竞品分析", "技术调研"],
        ),
        Category(
            id="cat_process",
            name="流程规范",
            description="工作流程、规范标准",
            rules=["SOP", "规范", "制度", "流程"],
        ),
        Category(
            id="cat_meeting",
            name="会议记录",
            description="会议纪要、讨论记录",
            rules=["会议纪要", "讨论记录", "决策记录"],
        ),
    ]

    # 默认标签库
    DEFAULT_TAGS = [
        Tag(id="tag_urgent", name="紧急", category="优先级"),
        Tag(id="tag_important", name="重要", category="优先级"),
        Tag(id="tag_reference", name="参考资料", category="类型"),
        Tag(id="tag_template", name="模板", category="类型"),
        Tag(id="tag_guide", name="指南", category="类型"),
        Tag(id="tag_api", name="API", category="技术"),
        Tag(id="tag_tutorial", name="教程", category="类型"),
        Tag(id="tag_best_practice", name="最佳实践", category="质量"),
    ]

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
    ):
        """
        初始化分类管理器

        Args:
            embedding_service: 嵌入服务实例
        """
        self.embedding_service = embedding_service or embedding_service

        # 内存存储分类和标签
        self._categories: dict[str, Category] = {
            cat.id: cat for cat in self.DEFAULT_CATEGORIES
        }
        self._tags: dict[str, Tag] = {tag.id: tag for tag in self.DEFAULT_TAGS}

        # 分类关系
        self._relationships: list[TaxonomyRelationship] = []

        # 关键词到分类的映射（用于自动分类）
        self._category_keywords: dict[str, list[str]] = {
            "cat_tech": ["代码", "技术", "架构", "开发", "编程", "api", "接口", "系统"],
            "cat_product": ["产品", "需求", "设计", "用户", "功能", "特性"],
            "cat_research": ["调研", "分析", "研究", "报告", "市场", "竞品"],
            "cat_process": ["流程", "规范", "制度", "sop", "标准", "规定"],
            "cat_meeting": ["会议", "纪要", "讨论", "决策", "记录"],
        }

    def get_categories(self) -> list[Category]:
        """获取所有分类"""
        return list(self._categories.values())

    def get_category(self, category_id: str) -> Optional[Category]:
        """获取单个分类"""
        return self._categories.get(category_id)

    def get_category_by_name(self, name: str) -> Optional[Category]:
        """根据名称获取分类"""
        for cat in self._categories.values():
            if cat.name == name:
                return cat
        return None

    def create_category(
        self,
        name: str,
        description: str = "",
        parent: Optional[str] = None,
        rules: Optional[list[str]] = None,
    ) -> Category:
        """
        创建新分类

        Args:
            name: 分类名称
            description: 分类描述
            parent: 父分类 ID
            rules: 分类规则

        Returns:
            创建的分类
        """
        category_id = f"cat_{name.lower().replace(' ', '_')}"
        category = Category(
            id=category_id,
            name=name,
            parent=parent,
            description=description,
            rules=rules or [],
        )
        self._categories[category_id] = category

        # 如果有父分类，添加到父分类的子分类列表
        if parent and parent in self._categories:
            self._categories[parent].subcategories.append(category_id)

        return category

    def update_category(
        self,
        category_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        rules: Optional[list[str]] = None,
    ) -> bool:
        """更新分类信息"""
        category = self._categories.get(category_id)
        if not category:
            return False

        if name:
            category.name = name
        if description:
            category.description = description
        if rules is not None:
            category.rules = rules

        return True

    def delete_category(self, category_id: str) -> bool:
        """
        删除分类

        Args:
            category_id: 分类 ID

        Returns:
            是否删除成功
        """
        if category_id not in self._categories:
            return False

        # 检查是否有子分类
        category = self._categories[category_id]
        if category.subcategories:
            return False  # 有子分类不能删除

        # 从父分类中移除
        if category.parent and category.parent in self._categories:
            parent = self._categories[category.parent]
            if category_id in parent.subcategories:
                parent.subcategories.remove(category_id)

        del self._categories[category_id]
        return True

    def get_tags(self, category: Optional[str] = None) -> list[Tag]:
        """获取标签列表"""
        if category:
            return [t for t in self._tags.values() if t.category == category]
        return list(self._tags.values())

    def get_tag(self, tag_id: str) -> Optional[Tag]:
        """获取单个标签"""
        return self._tags.get(tag_id)

    def get_tag_by_name(self, name: str) -> Optional[Tag]:
        """根据名称获取标签"""
        for tag in self._tags.values():
            if tag.name == name:
                return tag
        return None

    def create_tag(
        self,
        name: str,
        category: Optional[str] = None,
    ) -> Tag:
        """
        创建新标签

        Args:
            name: 标签名称
            category: 所属分类

        Returns:
            创建的标签
        """
        tag_id = f"tag_{name.lower().replace(' ', '_')}"
        tag = Tag(
            id=tag_id,
            name=name,
            category=category,
        )
        self._tags[tag_id] = tag
        return tag

    def update_tag_usage(self, tag_id: str, increment: int = 1) -> bool:
        """更新标签使用次数"""
        tag = self._tags.get(tag_id)
        if not tag:
            return False
        tag.usage_count += increment
        return True

    def delete_tag(self, tag_id: str) -> bool:
        """删除标签"""
        if tag_id in self._tags:
            del self._tags[tag_id]
            return True
        return False

    def auto_categorize(self, content: str, title: str = "") -> Optional[str]:
        """
        自动分类文档

        Args:
            content: 文档内容
            title: 文档标题

        Returns:
            推荐的分类 ID
        """
        text = f"{title} {content}".lower()

        # 基于关键词匹配
        category_scores: dict[str, int] = {}
        for cat_id, keywords in self._category_keywords.items():
            score = sum(1 for kw in keywords if kw.lower() in text)
            category_scores[cat_id] = score

        # 返回得分最高的分类
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            if best_category[1] > 0:  # 至少有 1 个关键词匹配
                return best_category[0]

        return None

    def auto_tag(
        self,
        content: str,
        title: str = "",
        max_tags: int = 5,
    ) -> list[str]:
        """
        自动打标签

        Args:
            content: 文档内容
            title: 文档标题
            max_tags: 最大标签数量

        Returns:
            推荐的标签 ID 列表
        """
        text = f"{title} {content}".lower()
        tag_scores: dict[str, int] = {}

        # 计算每个标签的匹配分数
        for tag_id, tag in self._tags.items():
            tag_name = tag.name.lower()
            if tag_name in text:
                # 标题中出现权重更高
                score = 2 if tag_name in title.lower() else 1
                tag_scores[tag_id] = score

        # 按分数排序
        sorted_tags = sorted(tag_scores.items(), key=lambda x: x[1], reverse=True)

        # 返回前 N 个标签
        return [tag_id for tag_id, _ in sorted_tags[:max_tags]]

    def suggest_tags_from_content(
        self,
        content: str,
        existing_tags: list[str],
    ) -> list[str]:
        """
        基于内容推荐新标签

        Args:
            content: 文档内容
            existing_tags: 已有标签 ID 列表

        Returns:
            推荐的新标签名称列表
        """
        # 提取内容中的关键词
        keywords = self._extract_keywords(content)

        # 过滤掉已有标签
        existing_names = {
            self._tags[tid].name.lower() for tid in existing_tags if tid in self._tags
        }

        # 推荐新标签
        suggested = []
        for kw in keywords:
            if kw not in existing_names and len(kw) >= 2:
                suggested.append(kw)

        return suggested[:5]

    def _extract_keywords(self, text: str, max_keywords: int = 10) -> list[str]:
        """提取关键词"""
        # 简单的中文关键词提取
        # 实际项目中可以使用 jieba 等分词工具
        words = re.split(r"[，。！？；：、\s]+", text)

        # 过滤
        stopwords = {
            "的", "了", "是", "在", "和", "与", "及", "等", "个", "这", "那",
            "我们", "你们", "他们", "这个", "那个", "可以", "应该", "需要",
        }
        keywords = [
            w for w in words
            if len(w) >= 2 and w not in stopwords
        ]

        # 按频率排序
        counter = Counter(keywords)
        return [kw for kw, _ in counter.most_common(max_keywords)]

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        strength: float = 1.0,
    ) -> TaxonomyRelationship:
        """
        添加分类/文档关系

        Args:
            source_id: 源 ID
            target_id: 目标 ID
            relationship_type: 关系类型
            strength: 关系强度

        Returns:
            创建的关系
        """
        relationship = TaxonomyRelationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            strength=strength,
        )
        self._relationships.append(relationship)
        return relationship

    def get_related(
        self,
        item_id: str,
        relationship_type: Optional[str] = None,
    ) -> list[TaxonomyRelationship]:
        """获取相关项"""
        related = [
            r for r in self._relationships
            if r.source_id == item_id or r.target_id == item_id
        ]
        if relationship_type:
            related = [r for r in related if r.relationship_type == relationship_type]
        return related

    def get_taxonomy_tree(self) -> dict[str, Any]:
        """
        获取分类树结构

        Returns:
            分类树字典
        """
        tree = {}

        # 找到根分类（没有父分类的）
        roots = [c for c in self._categories.values() if not c.parent]

        def build_tree(category: Category) -> dict[str, Any]:
            node = {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "children": [],
            }
            for child_id in category.subcategories:
                if child_id in self._categories:
                    child = self._categories[child_id]
                    node["children"].append(build_tree(child))
            return node

        for root in roots:
            tree[root.id] = build_tree(root)

        return tree

    def export_taxonomy(self) -> dict[str, Any]:
        """导出分类体系"""
        return {
            "categories": [c.dict() for c in self._categories.values()],
            "tags": [t.dict() for t in self._tags.values()],
            "relationships": [r.dict() for r in self._relationships],
        }


# 默认分类管理器实例
taxonomy_manager = TaxonomyManager()
