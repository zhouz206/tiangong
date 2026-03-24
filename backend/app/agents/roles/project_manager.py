"""
ProjectManagerAgent — 项目经理 Agent

职责：协调进度、需求澄清、回顾总结
"""
from typing import TYPE_CHECKING

from ..agent import Agent, TaskContext, TaskResult

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class ProjectManagerAgent(Agent):
    """
    项目经理 Agent
    
    核心能力:
    - 需求澄清 (office_hours)
    - 产品审视 (plan_ceo_review)
    - 回顾总结 (retro)
    """
    
    @property
    def role(self) -> str:
        return "project_manager"
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的项目经理。

你的职责:
1. 需求澄清 — 重新审视问题，挑战前提
2. 产品审视 — 范围决策、优先级判断
3. 回顾总结 — 完成统计、问题识别、改进计划

工作原则:
- 多问为什么，挖掘真实需求
- 挑战前提，避免错误假设
- 关注价值，而非功能列表
- 及时回顾，持续改进
"""
    
    async def _default_execute(self, context: TaskContext) -> TaskResult:
        """默认执行逻辑"""
        task_type = context.metadata.get("task_type", "general")
        
        if task_type == "office_hours":
            return await self._office_hours(context)
        elif task_type == "plan_ceo_review":
            return await self._plan_ceo_review(context)
        elif task_type == "retro":
            return await self._retro(context)
        else:
            return await self._general(context)
    
    async def _office_hours(self, context: TaskContext) -> TaskResult:
        """需求澄清"""
        return TaskResult(
            success=True,
            output={
                "type": "design_doc",
                "content": "需求澄清完成"
            }
        )
    
    async def _plan_ceo_review(self, context: TaskContext) -> TaskResult:
        """产品审视"""
        return TaskResult(
            success=True,
            output={
                "type": "ceo_review_report",
                "content": "产品审视完成"
            }
        )
    
    async def _retro(self, context: TaskContext) -> TaskResult:
        """回顾总结"""
        return TaskResult(
            success=True,
            output={
                "type": "retro_report",
                "content": "回顾总结完成"
            }
        )
    
    async def _general(self, context: TaskContext) -> TaskResult:
        """通用任务"""
        return TaskResult(
            success=True,
            output={
                "type": "general",
                "content": "项目经理处理完成"
            }
        )
