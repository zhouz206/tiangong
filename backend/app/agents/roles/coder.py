"""
CoderAgent — 程序员 Agent

职责：代码编写、调试、测试
"""
from typing import TYPE_CHECKING

from ..agent import Agent, TaskContext, TaskResult

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class CoderAgent(Agent):
    """
    程序员 Agent
    
    核心能力:
    - 代码生成
    - 调试
    - 单元测试
    """
    
    @property
    def role(self) -> str:
        return "coder"
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的程序员。

你的职责:
1. 代码编写 — 编写清晰、可维护的代码
2. 调试 — 定位并修复 Bug
3. 测试 — 编写单元测试

工作原则:
- 代码要清晰、简洁
- 遵循最佳实践
- 编写测试
- 及时重构
"""
    
    async def _default_execute(self, context: TaskContext) -> TaskResult:
        """默认执行逻辑"""
        return TaskResult(
            success=True,
            output={
                "type": "code",
                "content": "# 代码实现完成"
            }
        )
