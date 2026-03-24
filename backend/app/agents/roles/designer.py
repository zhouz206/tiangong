"""
DesignerAgent — 设计师 Agent

职责：UI/UX 设计、原型制作
"""
from typing import TYPE_CHECKING

from ..agent import Agent, TaskContext, TaskResult

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class DesignerAgent(Agent):
    """
    设计师 Agent
    
    核心能力:
    - UI 设计
    - UX 设计
    - 原型制作
    """
    
    @property
    def role(self) -> str:
        return "designer"
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的设计师。

你的职责:
1. UI 设计 — 设计美观、一致的界面
2. UX 设计 — 优化用户体验
3. 原型制作 — 制作可交互的原型

工作原则:
- 以用户为中心
- 保持设计一致性
- 简洁优于复杂
- 可访问性优先
"""
    
    async def _default_execute(self, context: TaskContext) -> TaskResult:
        """默认执行逻辑"""
        return TaskResult(
            success=True,
            output={
                "type": "design",
                "content": "# 设计完成"
            }
        )
