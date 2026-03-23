"""
Skill 系统

提供可扩展的 Skill 框架，支持动态加载和执行。

使用示例:
    from app.skills import SkillExecutor, get_registry, load_all_builtin
    
    # 加载所有内置 Skill
    load_all_builtin()
    
    # 执行 Skill
    executor = SkillExecutor()
    result = await executor.execute(
        skill_id="code_analysis",
        input_data={"code": "def hello(): pass"},
    )
"""

from .base import (
    Skill,
    SkillCategory,
    SkillStatus,
    SkillContext,
    SkillResult,
    SkillInfo,
    SkillRegistry,
    get_registry,
    reset_registry,
    register_skill,
    get_skill,
)

from .loader import (
    SkillLoader,
    SkillLoaderError,
    SkillNotFoundError,
    SkillLoadError,
    get_loader,
    reset_loader,
    load_builtin,
    load_all_builtin,
)

from .executor import (
    SkillExecutor,
    SkillExecutionError,
    SkillTimeoutError,
    SkillValidationError,
    ExecutionRecord,
    ExecutionStats,
    get_executor,
    reset_executor,
    execute_skill,
)

__all__ = [
    # Base
    "Skill",
    "SkillCategory",
    "SkillStatus",
    "SkillContext",
    "SkillResult",
    "SkillInfo",
    "SkillRegistry",
    "get_registry",
    "reset_registry",
    "register_skill",
    "get_skill",
    # Loader
    "SkillLoader",
    "SkillLoaderError",
    "SkillNotFoundError",
    "SkillLoadError",
    "get_loader",
    "reset_loader",
    "load_builtin",
    "load_all_builtin",
    # Executor
    "SkillExecutor",
    "SkillExecutionError",
    "SkillTimeoutError",
    "SkillValidationError",
    "ExecutionRecord",
    "ExecutionStats",
    "get_executor",
    "reset_executor",
    "execute_skill",
]
