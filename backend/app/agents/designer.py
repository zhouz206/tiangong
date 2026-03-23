"""
设计师 Agent

职责:
- UI/UX 设计
- 设计规范制定
- 视觉设计
- 交互设计
"""
from typing import Any, Optional

from app.core.agent import Agent, AgentCapability, TaskContext, TaskResult
from app.core.message import MessageBus


class DesignerAgent(Agent):
    """
    设计师 Agent

    负责 UI/UX 设计、设计规范、视觉设计和交互设计。
    """

    def __init__(
        self,
        agent_id: str,
        name: str = "Designer",
        message_bus: Optional[MessageBus] = None,
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            role="designer",
            capabilities=[
                AgentCapability.DESIGN,
            ],
            message_bus=message_bus,
        )

        # 设计师特有配置
        self.temperature = 0.7  # 适中温度，平衡创意和一致性
        self.max_tokens = 4096

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的设计师 Agent。

你的职责:
1. 设计直观美观的用户界面
2. 制定和维护设计规范（Design System）
3. 优化用户体验和交互流程
4. 创建视觉元素（图标、插图、配色方案）
5. 确保设计的一致性和可访问性

工作原则:
- 以用户为中心，设计要解决真实用户需求
- 保持简洁，避免不必要的复杂性
- 遵循设计原则（对比、重复、对齐、亲密性）
- 考虑无障碍设计，确保所有人都能使用
- 设计与技术可行性平衡

输出格式:
- 设计规范应包含：色彩系统、字体系统、组件库、间距规范
- 页面设计应包含：布局说明、组件描述、交互说明、响应式规则
- 交互设计应包含：流程图、状态说明、动效描述、反馈机制
"""

    async def execute_task(self, context: TaskContext) -> TaskResult:
        """
        执行设计任务

        处理任务类型:
        - ui_design: UI 设计
        - design_system: 设计规范
        - ux_design: UX/交互设计
        - visual_design: 视觉设计
        - responsive_design: 响应式设计
        """
        try:
            task_type = context.metadata.get("task_type", "general")

            if task_type == "ui_design":
                return await self._do_ui_design(context)
            elif task_type == "design_system":
                return await self._do_design_system(context)
            elif task_type == "ux_design":
                return await self._do_ux_design(context)
            elif task_type == "visual_design":
                return await self._do_visual_design(context)
            elif task_type == "responsive_design":
                return await self._do_responsive_design(context)
            else:
                return await self._do_general_design(context)

        except Exception as e:
            return TaskResult(
                success=False,
                error=f"Design task failed: {str(e)}",
            )

    async def _do_ui_design(self, context: TaskContext) -> TaskResult:
        """执行 UI 设计"""
        page_type = context.task_description

        # 收集需求和品牌信息
        requirements = []
        brand_guidelines = {}
        for output in context.upstream_outputs:
            if isinstance(output, dict):
                if "requirements" in output:
                    requirements.append(output["requirements"])
                if "brand" in output:
                    brand_guidelines = output["brand"]

        design_result = {
            "page_type": page_type,
            "layout": {},
            "components": [],
            "color_scheme": {},
            "typography": {},
            "interactions": [],
            "responsive_rules": [],
        }

        # TODO: 实际实现中生成设计稿描述
        return TaskResult(
            success=True,
            output=design_result,
            metadata={"design_type": "ui"},
        )

    async def _do_design_system(self, context: TaskContext) -> TaskResult:
        """制定设计规范"""
        project_type = context.task_description

        design_system = {
            "project_type": project_type,
            "color_palette": {
                "primary": [],
                "secondary": [],
                "neutral": [],
                "semantic": {},  # success, warning, error, info
            },
            "typography": {
                "font_families": [],
                "font_sizes": [],
                "font_weights": [],
                "line_heights": [],
            },
            "spacing": {
                "scale": [],
                "usage_guidelines": "",
            },
            "components": [],
            "icons": [],
            "accessibility_guidelines": [],
        }

        # TODO: 实际实现中生成完整设计规范
        return TaskResult(
            success=True,
            output=design_system,
            metadata={"design_type": "design_system"},
        )

    async def _do_ux_design(self, context: TaskContext) -> TaskResult:
        """执行 UX/交互设计"""
        feature = context.task_description

        # 收集用户研究和需求信息
        user_research = []
        user_personas = []
        for output in context.upstream_outputs:
            if isinstance(output, dict):
                if "user_research" in output:
                    user_research.append(output["user_research"])
                if "personas" in output:
                    user_personas = output["personas"]

        ux_result = {
            "feature": feature,
            "user_flow": [],
            "wireframes": [],
            "interaction_patterns": [],
            "states": {},  # loading, empty, error, success
            "feedback_mechanisms": [],
            "accessibility_considerations": [],
        }

        # TODO: 实际实现中生成 UX 设计方案
        return TaskResult(
            success=True,
            output=ux_result,
            metadata={"design_type": "ux"},
        )

    async def _do_visual_design(self, context: TaskContext) -> TaskResult:
        """执行视觉设计"""
        design_brief = context.task_description

        visual_result = {
            "brief": design_brief,
            "mood_board": [],
            "style_direction": "",
            "color_exploration": [],
            "visual_elements": [],
            "final_concepts": [],
        }

        # TODO: 实际实现中生成视觉设计方案
        return TaskResult(
            success=True,
            output=visual_result,
            metadata={"design_type": "visual"},
        )

    async def _do_responsive_design(self, context: TaskContext) -> TaskResult:
        """执行响应式设计"""
        page_type = context.task_description

        responsive_result = {
            "page_type": page_type,
            "breakpoints": [
                {"name": "mobile", "width": "320px"},
                {"name": "tablet", "width": "768px"},
                {"name": "desktop", "width": "1024px"},
                {"name": "wide", "width": "1440px"},
            ],
            "layout_adaptations": [],
            "component_behaviors": [],
            "touch_vs_mouse": [],
        }

        # TODO: 实际实现中生成响应式规则
        return TaskResult(
            success=True,
            output=responsive_result,
            metadata={"design_type": "responsive"},
        )

    async def _do_general_design(self, context: TaskContext) -> TaskResult:
        """执行一般设计任务"""
        design_result = {
            "task": context.task_description,
            "concept": "",
            "rationale": "",
            "deliverables": [],
            "recommendations": [],
        }

        return TaskResult(
            success=True,
            output=design_result,
            metadata={"design_type": "general"},
        )

    def create_component_spec(
        self,
        name: str,
        props: list[dict[str, Any]],
        states: list[str],
    ) -> dict[str, Any]:
        """创建组件规范"""
        return {
            "name": name,
            "description": "",
            "props": props,
            "states": states,
            "usage_examples": [],
            "accessibility_notes": "",
        }

    def define_color_token(
        self,
        name: str,
        light_value: str,
        dark_value: str,
        usage: str,
    ) -> dict[str, Any]:
        """定义颜色 Token"""
        return {
            "name": name,
            "light": light_value,
            "dark": dark_value,
            "usage": usage,
        }
