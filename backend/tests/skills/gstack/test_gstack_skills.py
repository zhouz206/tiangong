"""
gstack 技能测试
"""
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.skills.gstack import (
    SkillOfficeHours,
    SkillPlanCEOReview,
    SkillPlanEngReview,
    SkillPlanDesignReview,
    SkillReview,
    SkillQA,
    SkillShip,
    SkillRetro,
)
from app.agents.skill import SkillContext


# 测试数据库
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def db_session():
    """创建数据库会话"""
    session = SessionLocal()
    yield session
    session.close()


class TestGstackSkills:
    """gstack 技能测试"""
    
    def test_skill_office_hours(self, db_session):
        """测试 skill_office_hours"""
        skill = SkillOfficeHours()
        assert skill.name == "skill_office_hours"
    
    def test_skill_plan_ceo_review(self, db_session):
        """测试 skill_plan_ceo_review"""
        skill = SkillPlanCEOReview()
        assert skill.name == "skill_plan_ceo_review"
    
    def test_skill_plan_eng_review(self, db_session):
        """测试 skill_plan_eng_review"""
        skill = SkillPlanEngReview()
        assert skill.name == "skill_plan_eng_review"
    
    def test_skill_plan_design_review(self, db_session):
        """测试 skill_plan_design_review"""
        skill = SkillPlanDesignReview()
        assert skill.name == "skill_plan_design_review"
    
    def test_skill_review(self, db_session):
        """测试 skill_review"""
        skill = SkillReview()
        assert skill.name == "skill_review"
    
    def test_skill_qa(self, db_session):
        """测试 skill_qa"""
        skill = SkillQA()
        assert skill.name == "skill_qa"
    
    def test_skill_ship(self, db_session):
        """测试 skill_ship"""
        skill = SkillShip()
        assert skill.name == "skill_ship"
    
    def test_skill_retro(self, db_session):
        """测试 skill_retro"""
        skill = SkillRetro()
        assert skill.name == "skill_retro"
    
    @pytest.mark.asyncio
    async def test_skill_office_hours_execute(self, db_session):
        """测试 skill_office_hours 执行"""
        skill = SkillOfficeHours()
        context = SkillContext(task_id="task_1")
        result = await skill.execute(context)
        
        assert result.success is True
        assert "design_doc" in result.output
    
    @pytest.mark.asyncio
    async def test_skill_review_execute(self, db_session):
        """测试 skill_review 执行"""
        skill = SkillReview()
        context = SkillContext(task_id="task_1")
        result = await skill.execute(context)
        
        assert result.success is True
        assert result.output["review_report"]["overall_score"] >= 8.0
