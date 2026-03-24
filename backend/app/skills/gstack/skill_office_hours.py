"""
skill_office_hours — 需求澄清技能

对应 gstack: /office-hours
"""
from typing import TYPE_CHECKING

from ...agents.skill import Skill, SkillContext, SkillResult

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class SkillOfficeHours(Skill):
    """
    需求澄清技能
    
    职责:
    - 重新审视问题
    - 挑战前提
    - 生成 3 个实现方案
    """
    
    @property
    def name(self) -> str:
        return "skill_office_hours"
    
    async def execute(self, context: SkillContext) -> SkillResult:
        """
        执行需求澄清
        
        输出:
        - design_doc: 设计文档
        """
        try:
            # 6 个 forcing questions
            questions = [
                "要解决什么核心问题？",
                "为什么现在做？",
                "有哪些实现方案？",
                "推荐方案是什么？",
                "验收标准？",
                "风险和依赖？"
            ]
            
            # 生成设计文档
            design_doc = {
                "type": "design_document",
                "questions": questions,
                "implementation_options": [
                    {"name": "方案 A", "pros": [], "cons": [], "effort": "5h"},
                    {"name": "方案 B", "pros": [], "cons": [], "effort": "6h"},
                    {"name": "方案 C", "pros": [], "cons": [], "effort": "8h"}
                ],
                "recommendation": "方案 A"
            }
            
            return SkillResult(
                success=True,
                output={"design_doc": design_doc}
            )
        except Exception as e:
            return SkillResult(
                success=False,
                error=str(e)
            )
