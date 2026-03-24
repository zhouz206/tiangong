"""
ReviewerAgent — 审核员 Agent

职责：质量检查、代码审查
"""
from typing import TYPE_CHECKING

from ..agent import Agent, TaskContext, TaskResult

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class ReviewerAgent(Agent):
    """
    审核员 Agent
    
    核心能力:
    - 代码审查
    - 质量检查
    - 风险评估
    """
    
    @property
    def role(self) -> str:
        return "reviewer"
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的审核员。

你的职责:
1. 代码审查 — 查找 Bug、安全漏洞、性能问题
2. 质量检查 — 确保符合质量标准
3. 风险评估 — 识别潜在风险

工作原则:
- 细致、全面
- 建设性反馈
- 关注安全和性能
- 遵循最佳实践
"""
    
    async def _default_execute(self, context: TaskContext) -> TaskResult:
        """默认执行逻辑"""
        return TaskResult(
            success=True,
            output={
                "type": "review_report",
                "content": "# 审查完成",
                "issues": [],
                "suggestions": []
            }
        )
