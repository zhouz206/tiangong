"""
Tracking API — 项目跟踪 REST API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

from app.core.database import get_db
from .models import ExecutionLog
from .progress import ProgressService

router = APIRouter(tags=["tracking"])


@router.get("/project/{project_id}/status")
async def get_project_status(project_id: str, db: Session = Depends(get_db)):
    """获取项目状态"""
    service = ProgressService(db)
    status = service.get_project_status(project_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return status


@router.post("/milestone/{milestone_id}/progress")
async def update_milestone_progress(milestone_id: str, db: Session = Depends(get_db)):
    """更新里程碑进度"""
    service = ProgressService(db)
    progress = service.update_milestone_progress(milestone_id)
    
    return {"milestone_id": milestone_id, "progress": progress}


@router.get("/task/{task_id}/logs")
async def get_task_logs(task_id: str, limit: int = 100, db: Session = Depends(get_db)):
    """获取任务执行日志"""
    logs = db.query(ExecutionLog).filter(
        ExecutionLog.task_id == task_id
    ).order_by(ExecutionLog.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "action": log.action,
            "content": log.content,
            "actor": log.actor,
            "metadata": log.metadata,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]


@router.post("/task/{task_id}/log")
async def create_task_log(
    task_id: str,
    action: str,
    content: str = None,
    actor: str = None,
    metadata: dict = None,
    db: Session = Depends(get_db)
):
    """创建任务执行日志"""
    log = ExecutionLog(
        task_id=task_id,
        action=action,
        content=content,
        actor=actor or "system",
        metadata=metadata or {}
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    
    return {"id": log.id, "action": log.action}
