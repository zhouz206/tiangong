"""
TaxonomyManager — 分类和标签管理
"""
from typing import Dict, List, Optional


class TaxonomyManager:
    """
    分类和标签管理
    
    功能:
    - 分类管理
    - 标签管理
    - 自动分类
    """
    
    def __init__(self):
        """初始化管理器"""
        self._categories: Dict[str, dict] = {}
        self._tags: Dict[str, dict] = {}
        
        # 初始化默认分类
        self._init_default_categories()
    
    def _init_default_categories(self):
        """初始化默认分类"""
        default_categories = [
            {"id": "tech_doc", "name": "技术文档", "description": "代码、技术方案、架构设计"},
            {"id": "product_doc", "name": "产品文档", "description": "需求、设计、用户手册"},
            {"id": "research", "name": "研究报告", "description": "调研、分析、市场报告"},
            {"id": "process", "name": "流程规范", "description": "SOP、规范、制度"},
            {"id": "meeting", "name": "会议记录", "description": "纪要、讨论记录"}
        ]
        
        for cat in default_categories:
            self._categories[cat["id"]] = cat
    
    def create_category(self, cat_id: str, name: str, description: str = "") -> dict:
        """创建分类"""
        category = {"id": cat_id, "name": name, "description": description}
        self._categories[cat_id] = category
        return category
    
    def get_categories(self) -> List[dict]:
        """获取所有分类"""
        return list(self._categories.values())
    
    def create_tag(self, tag_id: str, name: str, category_id: Optional[str] = None) -> dict:
        """创建标签"""
        tag = {"id": tag_id, "name": name, "category_id": category_id}
        self._tags[tag_id] = tag
        return tag
    
    def get_tags(self) -> List[dict]:
        """获取所有标签"""
        return list(self._tags.values())
    
    def auto_categorize(self, text: str) -> Optional[str]:
        """
        自动分类
        
        Args:
            text: 文档内容
            
        Returns:
            分类 ID
        """
        # 简单的关键词匹配（后续可用 ML 模型改进）
        keywords_map = {
            "tech_doc": ["代码", "技术", "架构", "API", "数据库", "开发"],
            "product_doc": ["产品", "需求", "设计", "用户", "功能"],
            "research": ["调研", "分析", "报告", "研究", "市场"],
            "process": ["流程", "规范", "制度", "SOP", "标准"],
            "meeting": ["会议", "纪要", "讨论", "记录"]
        }
        
        # 统计每个分类的匹配关键词数
        scores = {}
        for cat_id, keywords in keywords_map.items():
            score = sum(1 for kw in keywords if kw in text.lower())
            scores[cat_id] = score
        
        # 返回得分最高的分类
        if not scores or max(scores.values()) == 0:
            return None
        
        return max(scores, key=scores.get)
    
    def auto_tag(self, text: str, max_tags: int = 5) -> List[str]:
        """
        自动打标签
        
        Args:
            text: 文档内容
            max_tags: 最大标签数
            
        Returns:
            标签 ID 列表
        """
        # 简单的关键词提取（后续可用 NLP 改进）
        common_tags = {
            "urgent": ["紧急", "优先", "重要"],
            "guide": ["指南", "教程", "指导"],
            "template": ["模板", "样例", "示例"],
            "best_practice": ["最佳实践", "实践", "经验"]
        }
        
        matched_tags = []
        for tag_id, keywords in common_tags.items():
            if any(kw in text.lower() for kw in keywords):
                matched_tags.append(tag_id)
        
        return matched_tags[:max_tags]
