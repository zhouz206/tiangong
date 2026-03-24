"""
WorkflowEngine — 自动工作流编排引擎
"""
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from datetime import datetime

from .quality_gate import QualityGate
from .phase import ProjectPhase, PhaseTransition

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from app.agents.agent import Agent


class WorkflowEngine:
    """
    自动工作流编排引擎
    
    功能:
    - 执行完整 gstack 流程
    - 质量门禁检查
    - 异常处理和降级
    """
    
    # gstack 流程步骤
    GSTACK_STEPS = [
        "office_hours",       # 需求澄清
        "plan_ceo_review",    # 产品审视
        "plan_eng_review",    # 工程规划
        "build",              # 代码实现
        "review",             # 代码审查
        "qa",                 # 质量保证
        "ship",               # 发布提交
        "retro"               # 回顾总结
    ]
    
    def __init__(self, db: "Session", agents: Dict[str, "Agent"] = None):
        """
        初始化工作流引擎
        
        Args:
            db: 数据库会话
            agents: Agent 字典（角色名 -> Agent 实例）
        """
        self.db = db
        self.agents = agents or {}
        self.quality_gate = QualityGate()
        self._results: Dict[str, Any] = {}
    
    def register_agent(self, role: str, agent: "Agent") -> None:
        """
        注册 Agent
        
        Args:
            role: 角色名
            agent: Agent 实例
        """
        self.agents[role] = agent
    
    async def run_workflow(self, user_request: str) -> Dict[str, Any]:
        """
        运行完整 gstack 工作流
        
        Args:
            user_request: 用户需求
            
        Returns:
            工作流执行结果
        """
        self._results = {}
        
        try:
            # Step 1: /office-hours
            self._results["office_hours"] = await self._execute_step(
                "office_hours",
                {"user_request": user_request}
            )
            
            # Step 2: /plan-ceo-review
            self._results["plan_ceo_review"] = await self._execute_step(
                "plan_ceo_review",
                {"design_doc": self._results["office_hours"]}
            )
            
            # Step 3: /plan-eng-review
            self._results["plan_eng_review"] = await self._execute_step(
                "plan_eng_review",
                {"ceo_report": self._results["plan_ceo_review"]}
            )
            
            # Step 4: Build
            self._results["build"] = await self._execute_step(
                "build",
                {"eng_plan": self._results["plan_eng_review"]}
            )
            
            # Step 5: /review
            self._results["review"] = await self._execute_step(
                "review",
                {"code": self._results["build"]}
            )
            
            # 质量门禁检查：审查评分
            if not self.quality_gate.check_review_score(self._results["review"]):
                return self._create_error_result("审查评分未通过")
            
            # Step 6: /qa
            self._results["qa"] = await self._execute_step(
                "qa",
                {"staging_url": "http://localhost:3000"}
            )
            
            # 质量门禁检查：核心流程
            if not self.quality_gate.check_core_flows(self._results["qa"]):
                return self._create_error_result("核心流程未通过")
            
            # Step 7: /ship
            self._results["ship"] = await self._execute_step(
                "ship",
                {"qa_report": self._results["qa"]}
            )
            
            # Step 8: /retro
            self._results["retro"] = await self._execute_step(
                "retro",
                {"release": self._results["ship"]}
            )
            
            return self._create_success_result()
            
        except Exception as e:
            return self._create_error_result(str(e))
    
    async def _execute_step(self, step_name: str, context: Dict) -> Any:
        """
        执行单个步骤
        
        Args:
            step_name: 步骤名称
            context: 上下文数据
            
        Returns:
            执行结果
        """
        # 根据步骤名选择对应的 Agent 和技能
        skill_map = {
            "office_hours": ("project_manager", "skill_office_hours"),
            "plan_ceo_review": ("project_manager", "skill_plan_ceo_review"),
            "plan_eng_review": ("architect", "skill_plan_eng_review"),
            "review": ("reviewer", "skill_review"),
            "qa": ("qa_engineer", "skill_qa"),
            "ship": ("delivery", "skill_ship"),
            "retro": ("project_manager", "skill_retro"),
            "build": ("coder", None),  # Build 不使用技能
        }
        
        if step_name not in skill_map:
            return {"status": "skipped", "step": step_name}
        
        role, skill_name = skill_map[step_name]
        
        if role not in self.agents:
            return {"status": "skipped", "reason": f"Agent '{role}' not registered"}
        
        agent = self.agents[role]
        
        if skill_name:
            # 使用技能执行
            from app.agents.skill import SkillContext
            result = await agent.execute_skill(skill_name, SkillContext(metadata=context))
            return result.output if result.success else {"error": result.error}
        else:
            # Build 步骤：默认实现
            return {"status": "completed", "step": step_name}
    
    def _create_success_result(self) -> Dict[str, Any]:
        """创建成功结果"""
        return {
            "success": True,
            "steps_completed": len([k for k, v in self._results.items() if v]),
            "results": self._results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_error_result(self, error: str) -> Dict[str, Any]:
        """创建错误结果"""
        return {
            "success": False,
            "error": error,
            "partial_results": self._results,
            "timestamp": datetime.now().isoformat()
        }
