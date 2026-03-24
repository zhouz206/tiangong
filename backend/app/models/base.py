"""
Base 模型类
"""
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import String
import uuid
from datetime import datetime


class Base(DeclarativeBase):
    """SQLAlchemy 基类"""
    pass


class UUIDMixin:
    """UUID 主键混入"""
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


class TimestampMixin:
    """时间戳混入"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SoftDeleteMixin:
    """软删除混入"""
    deleted_at = Column(DateTime, nullable=True)
