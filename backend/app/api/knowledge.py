"""
知识库 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import uuid

from app.core.database import get_db

router = APIRouter(tags=["knowledge"])


class KnowledgeItem(BaseModel):
    """知识库条目"""
    id: str
    title: str
    content: str
    category: str
    tags: List[str]


class KnowledgeSearchRequest(BaseModel):
    """知识库搜索请求"""
    query: str
    category: Optional[str] = None
    limit: int = 10


class KnowledgeSearchResponse(BaseModel):
    """知识库搜索响应"""
    query: str
    results: List[KnowledgeItem]
    total: int


# 模拟的知识库数据
KNOWLEDGE_BASE = {
    "kb-001": KnowledgeItem(
        id="kb-001",
        title="项目启动指南",
        content="项目启动前需要完成需求分析、资源评估和团队组建。",
        category="project_management",
        tags=["项目管理", "启动"]
    ),
    "kb-002": KnowledgeItem(
        id="kb-002",
        title="代码审查清单",
        content="代码审查需要检查代码规范、单元测试、安全性等方面。",
        category="engineering",
        tags=["代码审查", "质量"]
    ),
    "kb-003": KnowledgeItem(
        id="kb-003",
        title="设计系统规范",
        content="设计系统包括色彩、字体、间距、组件等规范。",
        category="design",
        tags=["设计系统", "规范"]
    ),
}


@router.get("/", response_model=List[KnowledgeItem])
async def list_knowledge(category: Optional[str] = None):
    """获取知识库列表"""
    items = list(KNOWLEDGE_BASE.values())
    if category:
        items = [item for item in items if item.category == category]
    return items


@router.get("/{item_id}", response_model=KnowledgeItem)
async def get_knowledge(item_id: str):
    """获取知识库条目详情"""
    if item_id not in KNOWLEDGE_BASE:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    return KNOWLEDGE_BASE[item_id]


@router.post("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(request: KnowledgeSearchRequest):
    """搜索知识库"""
    results = list(KNOWLEDGE_BASE.values())

    # 简单的关键词搜索
    query_lower = request.query.lower()
    results = [
        item for item in results
        if query_lower in item.title.lower() or
           query_lower in item.content.lower() or
           any(query_lower in tag.lower() for tag in item.tags)
    ]

    if request.category:
        results = [item for item in results if item.category == request.category]

    results = results[:request.limit]

    return KnowledgeSearchResponse(
        query=request.query,
        results=results,
        total=len(results)
    )


@router.post("/knowledge", response_model=KnowledgeItem)
async def create_knowledge(item: KnowledgeItem):
    """创建知识库条目"""
    item_id = f"kb-{str(uuid.uuid4())[:8]}"
    new_item = KnowledgeItem(
        id=item_id,
        title=item.title,
        content=item.content,
        category=item.category,
        tags=item.tags
    )
    KNOWLEDGE_BASE[item_id] = new_item
    return new_item
