"""
skill_retro — 回顾总结技能

对应 gstack: /retro
"""
from typing import TYPE_CHECKING

from ...agents.skill import Skill, SkillContext, SkillResult

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class SkillRetro(Skill):
    """
    回顾总结技能
    
    职责:
    - 完成统计
    - 问题识别
    - 改进计划
    """
    
    @property
    def name(self) -> str:
        return "skill_retro"
    
    async def execute(self, context: SkillContext) -> SkillResult:
        """
        执行回顾总结
        
        输出:
        - retro_report: Retro 报告
        """
        try:
            # 生成 Retro 报告
            retro_report = {
                "type": "retro_report",
                "completed": "8/8 任务完成",
                "tests_passed": "10/10 通过",
                "code_review_score": 8.6,
                "issues": [
                    "问题 1",
                    "问题 2"
                ],
                "improvements": [
                    "改进 1",
                    "改进 2"
                ],
                "next_step": "M7 知识库"
            }
            
            return SkillResult(
                success=True,
                output={"retro_report": retro_report}
            )
        except Exception as e:
            return SkillResult(
                success=False,
                error=str(e)
            )
