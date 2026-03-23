"""
项目经理 Agent

职责:
- 项目整体规划和管理
- 任务分解和分配
- 进度跟踪和协调
- 风险管理
"""
from typing import Any, Optional

from app.core.agent import Agent, AgentCapability, TaskContext, TaskResult
from app.core.message import MessageBus


class ProjectManagerAgent(Agent):
    """
    项目经理 Agent

    负责项目整体规划、任务分解、进度跟踪和团队协调。
    """

    def __init__(
        self,
        agent_id: str,
        name: str = "Project Manager",
        message_bus: Optional[MessageBus] = None,
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            role="project_manager",
            capabilities=[
                AgentCapability.PLANNING,
                AgentCapability.KNOWLEDGE_MANAGEMENT,
            ],
            message_bus=message_bus,
        )

        # 项目经理特有配置
        self.temperature = 0.5  # 更保守的温度
        self.max_tokens = 4096  # 需要更多 token 用于规划

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的项目经理 Agent。

你的职责:
1. 理解项目目标，制定详细的项目计划
2. 将大目标分解为可执行的具体任务
3. 协调各个 Agent 的工作，确保任务顺利流转
4. 跟踪项目进度，识别并解决阻塞问题
5. 管理项目风险，制定应急预案

工作原则:
- 保持清晰的沟通，确保所有 Agent 理解任务目标
- 优先处理关键路径上的任务
- 定期检查项目状态，及时调整计划
- 记录重要决策和项目上下文

输出格式:
- 规划输出应包含：目标、里程碑、任务列表、依赖关系、时间估算
- 协调消息应清晰指明：任务内容、负责人、截止时间、期望产出
"""

    async def execute_task(self, context: TaskContext) -> TaskResult:
        """
        执行项目管理任务

        处理任务类型:
        - project_planning: 项目规划
        - task_breakdown: 任务分解
        - progress_review: 进度审查
        - risk_assessment: 风险评估
        """
        try:
            task_type = context.metadata.get("task_type", "general")

            if task_type == "project_planning":
                return await self._do_project_planning(context)
            elif task_type == "task_breakdown":
                return await self._do_task_breakdown(context)
            elif task_type == "progress_review":
                return await self._do_progress_review(context)
            elif task_type == "risk_assessment":
                return await self._do_risk_assessment(context)
            else:
                return await self._do_general_management(context)

        except Exception as e:
            return TaskResult(
                success=False,
                error=f"Project manager task failed: {str(e)}",
            )

    async def _do_project_planning(self, context: TaskContext) -> TaskResult:
        """执行项目规划"""
        # 收集上游信息（如需求分析结果）
        requirements = ""
        for output in context.upstream_outputs:
            if isinstance(output, dict) and "content" in output:
                requirements += str(output["content"]) + "\n"

        # 生成项目计划
        plan = {
            "project_goal": context.task_description,
            "requirements_summary": requirements,
            "milestones": [],
            "tasks": [],
            "dependencies": [],
            "timeline": {},
        }

        # TODO: 实际实现中调用 LLM 生成计划
        # 这里返回结构化框架
        return TaskResult(
            success=True,
            output=plan,
            metadata={"plan_type": "project_plan"},
        )

    async def _do_task_breakdown(self, context: TaskContext) -> TaskResult:
        """执行任务分解"""
        # 分析输入的任务/目标
        goal = context.task_description

        # 生成任务分解
        breakdown = {
            "goal": goal,
            "subtasks": [],
            "assignments": {},  # task -> agent
            "dependencies": [],
        }

        # TODO: 实际实现中调用 LLM 分解任务
        return TaskResult(
            success=True,
            output=breakdown,
            metadata={"breakdown_type": "task_list"},
        )

    async def _do_progress_review(self, context: TaskContext) -> TaskResult:
        """执行进度审查"""
        # 收集各 Agent 的进度报告
        progress_data = []
        for output in context.upstream_outputs:
            if isinstance(output, dict):
                progress_data.append(output)

        review = {
            "completed_tasks": [],
            "in_progress_tasks": [],
            "blocked_tasks": [],
            "overall_progress": 0.0,
            "risks": [],
            "recommendations": [],
        }

        # TODO: 实际实现中分析进度数据
        return TaskResult(
            success=True,
            output=review,
            metadata={"review_type": "progress"},
        )

    async def _do_risk_assessment(self, context: TaskContext) -> TaskResult:
        """执行风险评估"""
        # 分析项目状态和历史问题
        risks = []

        # 常见风险类型
        risk_categories = [
            "technical",
            "schedule",
            "resource",
            "communication",
        ]

        assessment = {
            "identified_risks": risks,
            "risk_matrix": {},  # risk -> (probability, impact)
            "mitigation_plans": [],
            "contingency_reserves": {},
        }

        # TODO: 实际实现中调用 LLM 分析风险
        return TaskResult(
            success=True,
            output=assessment,
            metadata={"assessment_type": "risk"},
        )

    async def _do_general_management(self, context: TaskContext) -> TaskResult:
        """执行一般管理任务"""
        # 通用管理逻辑
        result = {
            "summary": context.task_description,
            "actions": [],
            "decisions": [],
            "notes": [],
        }

        return TaskResult(
            success=True,
            output=result,
            metadata={"type": "general_management"},
        )

    def create_milestone(self, name: str, tasks: list[str], deadline: str) -> dict[str, Any]:
        """创建里程碑"""
        return {
            "name": name,
            "tasks": tasks,
            "deadline": deadline,
            "status": "pending",
        }

    def assign_task_to_agent(
        self,
        task_id: str,
        agent_role: str,
        priority: str = "medium",
    ) -> dict[str, Any]:
        """创建任务分配建议"""
        return {
            "task_id": task_id,
            "target_role": agent_role,
            "priority": priority,
            "status": "suggested",
        }
