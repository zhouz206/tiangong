"""
ExecutionLog — 执行日志模型
"""
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import declarative_base, relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy.types import JSON

Base = declarative_base()


class ExecutionLog(Base):
    __tablename__ = "execution_logs"
    
    id = Column(String(36), primary_key=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    task_id = Column(String(36), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    content = Column(Text, nullable=True)
    actor = Column(String(100), nullable=False)
    log_metadata = Column("metadata", JSON, nullable=True, default=dict)
    
    __table_args__ = (
        Index("ix_execution_logs_task_action", "task_id", "action"),
        Index("ix_execution_logs_created", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<ExecutionLog(task_id={self.task_id}, action={self.action})>"
