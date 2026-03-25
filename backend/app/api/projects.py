"""
项目 API 路由

使用内存存储进行测试，避免数据库依赖问题。
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import uuid

from app.models.project import ProjectStatus, ProjectPhase

router = APIRouter(tags=["projects"])

# 内存存储（用于测试）
_projects_store: dict = {}


class ProjectCreate(BaseModel):
    """创建项目请求"""
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.ACTIVE
    phase: ProjectPhase = ProjectPhase.PLANNING


class ProjectResponse(BaseModel):
    """项目响应"""
    id: str
    name: str
    description: Optional[str]
    status: str
    phase: str
    progress: int


def _project_to_response(project_data: dict) -> ProjectResponse:
    """转换为响应对象"""
    return ProjectResponse(**project_data)


@router.get("/", response_model=List[ProjectResponse])
async def list_projects():
    """获取项目列表"""
    return [_project_to_response(p) for p in _projects_store.values()]


@router.post("/", response_model=ProjectResponse)
async def create_project(project_data: ProjectCreate):
    """创建项目"""
    project_id = str(uuid.uuid4())
    project = {
        "id": project_id,
        "name": project_data.name,
        "description": project_data.description,
        "status": project_data.status.value if hasattr(project_data.status, 'value') else str(project_data.status),
        "phase": project_data.phase.value if hasattr(project_data.phase, 'value') else str(project_data.phase),
        "progress": 0
    }
    _projects_store[project_id] = project
    return _project_to_response(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """获取项目详情"""
    if project_id not in _projects_store:
        raise HTTPException(status_code=404, detail="Project not found")
    return _project_to_response(_projects_store[project_id])


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """删除项目"""
    if project_id not in _projects_store:
        raise HTTPException(status_code=404, detail="Project not found")
    del _projects_store[project_id]
    return {"message": "Project deleted"}
