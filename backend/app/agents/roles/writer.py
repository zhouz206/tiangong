"""
WriterAgent — 文案 Agent

职责：内容撰写、编辑、校对
"""
from typing import TYPE_CHECKING

from ..agent import Agent, TaskContext, TaskResult

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class WriterAgent(Agent):
    """
    文案 Agent
    
    核心能力:
    - 内容撰写
    - 编辑
    - 校对
    """
    
    @property
    def role(self) -> str:
        return "writer"
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的文案。

你的职责:
1. 内容撰写 — 撰写清晰、有吸引力的内容
2. 编辑 — 优化内容结构和表达
3. 校对 — 检查语法、拼写错误

工作原则:
- 内容要准确
- 表达要清晰
- 风格要一致
- 注意目标受众
"""
    
    async def _default_execute(self, context: TaskContext) -> TaskResult:
        """默认执行逻辑"""
        return TaskResult(
            success=True,
            output={
                "type": "content",
                "content": "# 内容撰写完成"
            }
        )
