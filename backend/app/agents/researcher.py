"""
研究员 Agent

职责:
- 信息搜集和整理
- 竞品分析
- 技术方案调研
- 最佳实践研究
"""
from typing import Any, Optional

from app.core.agent import Agent, AgentCapability, TaskContext, TaskResult
from app.core.message import MessageBus


class ResearcherAgent(Agent):
    """
    研究员 Agent

    负责信息搜集、技术分析、竞品研究和最佳实践整理。
    """

    def __init__(
        self,
        agent_id: str,
        name: str = "Researcher",
        message_bus: Optional[MessageBus] = None,
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            role="researcher",
            capabilities=[
                AgentCapability.RESEARCH,
                AgentCapability.DATA_ANALYSIS,
            ],
            message_bus=message_bus,
        )

        # 研究员特有配置
        self.temperature = 0.3  # 较低温度，更精确
        self.max_tokens = 4096

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的研究员 Agent。

你的职责:
1. 搜集和整理项目相关的技术文档、资料和信息
2. 进行竞品分析，找出优缺点和差异化机会
3. 研究技术方案，对比不同实现方式的优劣
4. 整理最佳实践，为团队提供技术建议
5. 追踪行业趋势和新技术动态

工作原则:
- 信息来源必须可靠，优先参考官方文档和权威来源
- 分析客观全面，同时考虑优点和缺点
- 结论要有数据或事实支撑
- 输出结构清晰，便于团队理解和使用

输出格式:
- 研究报告应包含：背景、方法、发现、分析、建议
- 技术方案对比应包含：方案描述、优缺点、适用场景、风险评估
- 竞品分析应包含：功能对比、用户体验、技术实现、市场定位
"""

    async def execute_task(self, context: TaskContext) -> TaskResult:
        """
        执行研究任务

        处理任务类型:
        - market_research: 市场调研
        - technical_research: 技术调研
        - competitor_analysis: 竞品分析
        - best_practices: 最佳实践研究
        - documentation: 文档整理
        """
        try:
            task_type = context.metadata.get("task_type", "general")

            if task_type == "market_research":
                return await self._do_market_research(context)
            elif task_type == "technical_research":
                return await self._do_technical_research(context)
            elif task_type == "competitor_analysis":
                return await self._do_competitor_analysis(context)
            elif task_type == "best_practices":
                return await self._do_best_practices(context)
            elif task_type == "documentation":
                return await self._do_documentation(context)
            else:
                return await self._do_general_research(context)

        except Exception as e:
            return TaskResult(
                success=False,
                error=f"Research task failed: {str(e)}",
            )

    async def _do_market_research(self, context: TaskContext) -> TaskResult:
        """执行市场调研"""
        research_topic = context.task_description

        research_result = {
            "topic": research_topic,
            "market_size": "",
            "target_audience": [],
            "market_trends": [],
            "opportunities": [],
            "threats": [],
            "sources": [],
        }

        # TODO: 实际实现中调用搜索工具和 LLM 分析
        return TaskResult(
            success=True,
            output=research_result,
            metadata={"research_type": "market"},
        )

    async def _do_technical_research(self, context: TaskContext) -> TaskResult:
        """执行技术调研"""
        technology = context.task_description

        research_result = {
            "technology": technology,
            "overview": "",
            "key_features": [],
            "pros": [],
            "cons": [],
            "use_cases": [],
            "alternatives": [],
            "learning_resources": [],
            "recommendation": "",
        }

        # TODO: 实际实现中调用 LLM 进行技术分析
        return TaskResult(
            success=True,
            output=research_result,
            metadata={"research_type": "technical"},
        )

    async def _do_competitor_analysis(self, context: TaskContext) -> TaskResult:
        """执行竞品分析"""
        product_domain = context.task_description

        analysis_result = {
            "domain": product_domain,
            "competitors": [],
            "feature_comparison": {},
            "strengths_weaknesses": {},
            "market_positioning": {},
            "recommendations": [],
        }

        # TODO: 实际实现中分析竞品信息
        return TaskResult(
            success=True,
            output=analysis_result,
            metadata={"analysis_type": "competitor"},
        )

    async def _do_best_practices(self, context: TaskContext) -> TaskResult:
        """研究最佳实践"""
        domain = context.task_description

        practices_result = {
            "domain": domain,
            "principles": [],
            "patterns": [],
            "anti_patterns": [],
            "tools": [],
            "checklist": [],
            "references": [],
        }

        # TODO: 实际实现中整理最佳实践
        return TaskResult(
            success=True,
            output=practices_result,
            metadata={"type": "best_practices"},
        )

    async def _do_documentation(self, context: TaskContext) -> TaskResult:
        """整理文档"""
        doc_topic = context.task_description

        doc_result = {
            "topic": doc_topic,
            "summary": "",
            "key_points": [],
            "structured_content": {},
            "glossary": [],
            "references": [],
        }

        # 处理上游输出的文档内容
        for output in context.upstream_outputs:
            if isinstance(output, dict) and "content" in output:
                doc_result["key_points"].append(output["content"])

        return TaskResult(
            success=True,
            output=doc_result,
            metadata={"type": "documentation"},
        )

    async def _do_general_research(self, context: TaskContext) -> TaskResult:
        """执行一般研究任务"""
        research_result = {
            "topic": context.task_description,
            "findings": [],
            "analysis": "",
            "conclusions": [],
            "recommendations": [],
            "sources": [],
        }

        # 整合上游信息
        for output in context.upstream_outputs:
            if isinstance(output, dict):
                research_result["findings"].append(output)

        return TaskResult(
            success=True,
            output=research_result,
            metadata={"type": "general_research"},
        )

    def create_research_outline(self, topic: str, sections: list[str]) -> dict[str, Any]:
        """创建研究大纲"""
        return {
            "topic": topic,
            "sections": sections,
            "status": "outline",
        }

    def evaluate_source(self, source_url: str, criteria: dict[str, Any]) -> dict[str, Any]:
        """评估信息源可靠性"""
        return {
            "url": source_url,
            "criteria": criteria,
            "score": 0.0,
            "reliability": "unknown",
        }
