"""
模型基类和通用 Mixin

注意：所有模型必须从 app.core.database 导入 Base 并继承它。
此文件仅提供可重用的 Mixin 类。
"""
from sqlalchemy import Column, DateTime, func, String
from sqlalchemy.orm import declared_attr
from typing import Optional
import uuid


class UUIDMixin:
    """UUID 主键 Mixin"""
    @declared_attr
    def id(cls):
        return Column(
            String(36),
            primary_key=True,
            default=lambda: str(uuid.uuid4()),
            index=True,
        )


class TimestampMixin:
    """时间戳 Mixin - 自动管理 created_at 和 updated_at"""
    @declared_attr
    def created_at(cls):
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
            index=True,
        )
    
    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
            index=True,
        )


class SoftDeleteMixin:
    """软删除 Mixin - 使用 deleted_at 标记删除"""
    @declared_attr
    def deleted_at(cls):
        return Column(
            DateTime(timezone=True),
            nullable=True,
            index=True,
            default=None,
        )


# 注意：BaseModel 已废弃，请直接使用 app.core.database.Base
# 并在模型中混合使用上述 Mixin 类