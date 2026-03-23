"""
知识库数据模型

定义知识文档、分类、标签等核心数据结构。
"""
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class DocumentStatus(str, Enum):
    """文档状态"""
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class DocumentType(str, Enum):
    """文档类型"""
    TEXT = "text"
    CODE = "code"
    IMAGE = "image"
    PDF = "pdf"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    YAML = "yaml"


class KnowledgeDocument(BaseModel):
    """知识文档模型"""
    id: str = Field(..., description="文档唯一标识")
    title: str = Field(..., description="文档标题")
    content: str = Field(..., description="文档内容")
    content_type: DocumentType = Field(default=DocumentType.TEXT, description="内容类型")
    category: str = Field(..., description="所属分类")
    tags: list[str] = Field(default_factory=list, description="标签列表")
    status: DocumentStatus = Field(default=DocumentStatus.DRAFT, description="文档状态")
    version: str = Field(default="1.0", description="版本号")
    embedding: Optional[list[float]] = Field(default=None, description="向量嵌入")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    archived_at: Optional[datetime] = Field(default=None, description="归档时间")

    class Config:
        use_enum_values = True


class Category(BaseModel):
    """分类模型"""
    id: str = Field(..., description="分类唯一标识")
    name: str = Field(..., description="分类名称")
    parent: Optional[str] = Field(default=None, description="父分类 ID")
    description: str = Field(default="", description="分类描述")
    rules: list[str] = Field(default_factory=list, description="分类规则")
    subcategories: list[str] = Field(default_factory=list, description="子分类 ID 列表")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class Tag(BaseModel):
    """标签模型"""
    id: str = Field(..., description="标签唯一标识")
    name: str = Field(..., description="标签名称")
    category: Optional[str] = Field(default=None, description="所属分类")
    usage_count: int = Field(default=0, description="使用次数")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class SearchQuery(BaseModel):
    """搜索查询模型"""
    query: str = Field(..., description="搜索查询文本")
    category: Optional[str] = Field(default=None, description="过滤分类")
    tags: list[str] = Field(default_factory=list, description="过滤标签")
    limit: int = Field(default=10, description="返回结果数量")
    min_score: float = Field(default=0.5, description="最小相关性分数")


class SearchResult(BaseModel):
    """搜索结果模型"""
    document: KnowledgeDocument = Field(..., description="匹配的文档")
    score: float = Field(..., description="相关性分数")
    highlights: list[str] = Field(default_factory=list, description="高亮片段")
    reason: str = Field(default="", description="推荐理由")


class ArchiveRule(BaseModel):
    """归档规则模型"""
    id: str = Field(..., description="规则唯一标识")
    name: str = Field(..., description="规则名称")
    condition_type: str = Field(..., description="条件类型：age, status, category")
    condition_value: Any = Field(..., description="条件值")
    action: str = Field(default="archive", description="执行动作：archive, delete, notify")
    enabled: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class TaxonomyRelationship(BaseModel):
    """分类关系模型"""
    source_id: str = Field(..., description="源分类/文档 ID")
    target_id: str = Field(..., description="目标分类/文档 ID")
    relationship_type: str = Field(..., description="关系类型：related_to, depends_on, extends, part_of")
    strength: float = Field(default=1.0, description="关系强度 0-1")
    metadata: dict[str, Any] = Field(default_factory=dict, description="关系元数据")
