"""
Agent — Agent 基类

Agent = 角色 + 技能组合
"""
from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from datetime import datetime

from .skill import Skill, SkillContext, SkillResult

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


@dataclass
class TaskContext:
    """任务执行上下文"""
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    milestone_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class TaskResult:
    """任务执行结果"""
    success: bool
    output: Any = None
    error: Optional[str] = None
    actual_minutes: float = 0.0
    metadata: dict = field(default_factory=dict)


class Agent(ABC):
    """Agent 基类"""
    
    def __init__(self, db: "Session"):
        self.db = db
        self._skills: Dict[str, Skill] = {}
        self._current_task_id: Optional[str] = None
        self._start_time: Optional[datetime] = None
    
    @property
    def role(self) -> str:
        """Agent 角色名称"""
        return "unknown"
    
    def load_skill(self, skill: Skill) -> None:
        """装备技能"""
        self._skills[skill.name] = skill
    
    def unload_skill(self, skill_name: str) -> bool:
        """卸载技能"""
        if skill_name in self._skills:
            del self._skills[skill_name]
            return True
        return False
    
    def has_skill(self, skill_name: str) -> bool:
        """检查是否装备了某个技能"""
        return skill_name in self._skills
    
    def get_skills(self) -> List[str]:
        """获取已装备的技能列表"""
        return list(self._skills.keys())
    
    async def execute_skill(self, skill_name: str, context: SkillContext) -> SkillResult:
        """执行技能"""
        if skill_name not in self._skills:
            return SkillResult(success=False, error=f"Skill '{skill_name}' not found")
        
        skill = self._skills[skill_name]
        return await skill.execute(context)
    
    async def execute_task(self, context: TaskContext) -> TaskResult:
        """执行任务"""
        self._current_task_id = context.task_id
        self._start_time = datetime.now()
        
        try:
            skill_name = context.metadata.get("required_skill")
            
            if skill_name and self.has_skill(skill_name):
                skill_context = SkillContext(
                    task_id=context.task_id,
                    project_id=context.project_id,
                    metadata=context.metadata
                )
                skill_result = await self.execute_skill(skill_name, skill_context)
                
                if skill_result.success:
                    return self._create_success_result(skill_result.output)
                else:
                    return self._create_error_result(skill_result.error)
            else:
                return await self._default_execute(context)
                
        except Exception as e:
            return self._create_error_result(str(e))
        
        finally:
            self._current_task_id = None
            self._start_time = None
    
    async def _default_execute(self, context: TaskContext) -> TaskResult:
        """默认执行逻辑（子类可重写）"""
        return TaskResult(success=False, error="No skill specified and no default implementation")
    
    def _create_success_result(self, output: Any) -> TaskResult:
        """创建成功结果"""
        actual_minutes = 0.0
        if self._start_time:
            actual_minutes = (datetime.now() - self._start_time).total_seconds() / 60.0
        return TaskResult(success=True, output=output, actual_minutes=actual_minutes)
    
    def _create_error_result(self, error: str) -> TaskResult:
        """创建错误结果"""
        actual_minutes = 0.0
        if self._start_time:
            actual_minutes = (datetime.now() - self._start_time).total_seconds() / 60.0
        return TaskResult(success=False, error=error, actual_minutes=actual_minutes)
    
    def __repr__(self) -> str:
        return f"<Agent(role={self.role}, skills={self.get_skills()})>"
