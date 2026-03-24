"""
KnowledgeManagerAgent — 知识管理员 Agent

职责：文档整理、知识归档
"""
from typing import TYPE_CHECKING

from ..agent import Agent, TaskContext, TaskResult

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class KnowledgeManagerAgent(Agent):
    """
    知识管理员 Agent
    
    核心能力:
    - 知识管理
    - 文档归档
    - 知识检索
    """
    
    @property
    def role(self) -> str:
        return "knowledge_manager"
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的知识管理员。

你的职责:
1. 知识管理 — 组织、分类项目知识
2. 文档归档 — 整理项目产出物
3. 知识检索 — 支持知识查找和推荐

工作原则:
- 分类要清晰
- 标签要准确
- 及时归档
- 便于检索
"""
    
    async def _default_execute(self, context: TaskContext) -> TaskResult:
        """默认执行逻辑"""
        return TaskResult(
            success=True,
            output={
                "type": "knowledge_archive",
                "content": "# 知识归档完成"
            }
        )
