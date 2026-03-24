"""
Skill — 技能基类

技能是独立可复用的能力模块，Agent 可以装备多个技能。
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class SkillContext:
    """
    技能执行上下文
    
    字段:
    - task_id: 关联任务 ID
    - project_id: 项目 ID
    - metadata: 扩展元数据
    """
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class SkillResult:
    """
    技能执行结果
    
    字段:
    - success: 是否成功
    - output: 输出数据
    - error: 错误信息（如果失败）
    - metadata: 扩展元数据
    """
    success: bool
    output: Any = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)


class Skill(ABC):
    """
    技能基类
    
    所有技能必须继承此类并实现 execute 方法。
    
    使用示例:
        class SkillReview(Skill):
            name = "skill_review"
            
            async def execute(self, context: SkillContext) -> SkillResult:
                # 执行代码审查
                ...
                return SkillResult(success=True, output=review_report)
    """
    
    @property
    def name(self) -> str:
        """技能名称（必须唯一）"""
        return "unknown"
    
    async def execute(self, context: SkillContext) -> SkillResult:
        """
        执行技能
        
        Args:
            context: 技能执行上下文
            
        Returns:
            SkillResult: 执行结果
        """
        pass
    
    def __repr__(self) -> str:
        return f"<Skill(name={self.name})>"
