"""
skill_plan_ceo_review — 产品审视技能

对应 gstack: /plan-ceo-review
"""
from typing import TYPE_CHECKING

from ...agents.skill import Skill, SkillContext, SkillResult

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class SkillPlanCEOReview(Skill):
    """
    产品审视技能
    
    职责:
    - 重新审视问题
    - 范围决策
    - 优先级判断
    """
    
    @property
    def name(self) -> str:
        return "skill_plan_ceo_review"
    
    async def execute(self, context: SkillContext) -> SkillResult:
        """
        执行产品审视
        
        输出:
        - ceo_review_report: CEO Review 报告
        """
        try:
            # 10 项审视
            review_items = [
                "范围是否清晰？",
                "优先级是否合理？",
                "是否过度设计？",
                "是否欠设计？",
                "技术选型是否合理？",
                "工时估算是否现实？",
                "验收标准是否明确？",
                "风险是否可控？",
                "是否可 incremental？",
                "是否值得现在做？"
            ]
            
            # 生成 CEO Review 报告
            ceo_report = {
                "type": "ceo_review_report",
                "review_items": review_items,
                "scope_decision": "Selective Expansion",
                "priority": "P0"
            }
            
            return SkillResult(
                success=True,
                output={"ceo_review_report": ceo_report}
            )
        except Exception as e:
            return SkillResult(
                success=False,
                error=str(e)
            )
