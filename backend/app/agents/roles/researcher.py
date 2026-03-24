"""
ResearcherAgent — 研究员 Agent

职责：信息搜集、分析整理
"""
from typing import TYPE_CHECKING

from ..agent import Agent, TaskContext, TaskResult

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class ResearcherAgent(Agent):
    """
    研究员 Agent
    
    核心能力:
    - 信息搜集
    - 数据分析
    - 整理报告
    """
    
    @property
    def role(self) -> str:
        return "researcher"
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的研究员。

你的职责:
1. 信息搜集 — 从多渠道获取相关信息
2. 数据分析 — 整理、分析搜集到的信息
3. 整理报告 — 输出结构化的研究报告

工作原则:
- 信息来源要可靠
- 数据要验证
- 结论要有依据
- 报告要清晰结构化
"""
    
    async def _default_execute(self, context: TaskContext) -> TaskResult:
        """默认执行逻辑"""
        return TaskResult(
            success=True,
            output={
                "type": "research_report",
                "content": "研究完成"
            }
        )
