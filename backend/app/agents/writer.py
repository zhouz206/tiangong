"""
文案 Agent

职责:
- 产品文案撰写
- 技术文档编写
- 营销内容创作
- 用户指南编写
"""
from typing import Any, Optional

from app.core.agent import Agent, AgentCapability, TaskContext, TaskResult
from app.core.message import MessageBus


class WriterAgent(Agent):
    """
    文案 Agent

    负责产品文案、技术文档、营销内容和用户指南的撰写。
    """

    def __init__(
        self,
        agent_id: str,
        name: str = "Writer",
        message_bus: Optional[MessageBus] = None,
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            role="writer",
            capabilities=[
                AgentCapability.WRITING,
                AgentCapability.KNOWLEDGE_MANAGEMENT,
            ],
            message_bus=message_bus,
        )

        # 文案特有配置
        self.temperature = 0.7  # 适中温度，平衡创意和准确性
        self.max_tokens = 4096

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的文案 Agent。

你的职责:
1. 撰写清晰、准确的产品文案
2. 编写技术文档和 API 文档
3. 创作营销内容和品牌故事
4. 编写用户指南和帮助文档
5. 确保文案风格一致且符合品牌调性

工作原则:
- 语言简洁明了，避免冗长和晦涩
- 以用户为中心，用用户能理解的方式表达
- 保持一致的语调和专业术语
- 技术文档要准确，营销文案要有吸引力
- 考虑国际化和本地化需求

输出格式:
- 产品文案应包含：标题、副标题、正文、CTA
- 技术文档应包含：概述、快速开始、API 参考、示例代码、FAQ
- 营销文案应包含：价值主张、核心卖点、社会证明、行动号召
- 用户指南应包含：前置条件、操作步骤、常见问题、故障排除
"""

    async def execute_task(self, context: TaskContext) -> TaskResult:
        """
        执行文案任务

        处理任务类型:
        - product_copy: 产品文案
        - technical_docs: 技术文档
        - marketing_content: 营销内容
        - user_guide: 用户指南
        - api_docs: API 文档
        """
        try:
            task_type = context.metadata.get("task_type", "general")

            if task_type == "product_copy":
                return await self._write_product_copy(context)
            elif task_type == "technical_docs":
                return await self._write_technical_docs(context)
            elif task_type == "marketing_content":
                return await self._write_marketing_content(context)
            elif task_type == "user_guide":
                return await self._write_user_guide(context)
            elif task_type == "api_docs":
                return await self._write_api_docs(context)
            else:
                return await self._do_general_writing(context)

        except Exception as e:
            return TaskResult(
                success=False,
                error=f"Writing task failed: {str(e)}",
            )

    async def _write_product_copy(self, context: TaskContext) -> TaskResult:
        """撰写产品文案"""
        product_feature = context.task_description

        # 收集产品信息和品牌指南
        product_info = {}
        brand_voice = {}
        for output in context.upstream_outputs:
            if isinstance(output, dict):
                if "product" in output:
                    product_info = output["product"]
                if "brand" in output:
                    brand_voice = output["brand"]

        copy_result = {
            "feature": product_feature,
            "headline": "",
            "subheadline": "",
            "body_copy": "",
            "cta_buttons": [],
            "microcopy": [],  # 按钮文本、提示语等
            "tone": brand_voice.get("tone", "professional"),
        }

        # TODO: 实际实现中调用 LLM 生成文案
        return TaskResult(
            success=True,
            output=copy_result,
            metadata={"writing_type": "product_copy"},
        )

    async def _write_technical_docs(self, context: TaskContext) -> TaskResult:
        """编写技术文档"""
        doc_topic = context.task_description

        # 收集技术信息
        technical_specs = []
        code_examples = []
        for output in context.upstream_outputs:
            if isinstance(output, dict):
                if "spec" in output:
                    technical_specs.append(output["spec"])
                if "code" in output:
                    code_examples.append(output["code"])

        docs_result = {
            "topic": doc_topic,
            "overview": "",
            "quick_start": "",
            "detailed_guide": "",
            "code_examples": code_examples,
            "troubleshooting": [],
            "faq": [],
            "glossary": [],
        }

        # TODO: 实际实现中生成技术文档
        return TaskResult(
            success=True,
            output=docs_result,
            metadata={"writing_type": "technical_docs"},
        )

    async def _write_marketing_content(self, context: TaskContext) -> TaskResult:
        """创作营销内容"""
        campaign_topic = context.task_description

        # 收集市场和竞品信息
        market_info = {}
        target_audience = []
        for output in context.upstream_outputs:
            if isinstance(output, dict):
                if "market" in output:
                    market_info = output["market"]
                if "audience" in output:
                    target_audience = output["audience"]

        marketing_result = {
            "campaign": campaign_topic,
            "value_proposition": "",
            "key_messages": [],
            "content_pieces": [],  # 博客、社交媒体、邮件等
            "headlines": [],
            "social_proof": [],
            "ctas": [],
        }

        # TODO: 实际实现中生成营销内容
        return TaskResult(
            success=True,
            output=marketing_result,
            metadata={"writing_type": "marketing"},
        )

    async def _write_user_guide(self, context: TaskContext) -> TaskResult:
        """编写用户指南"""
        guide_topic = context.task_description

        # 收集产品功能信息
        features = []
        workflows = []
        for output in context.upstream_outputs:
            if isinstance(output, dict):
                if "features" in output:
                    features.extend(output["features"])
                if "workflows" in output:
                    workflows.extend(output["workflows"])

        guide_result = {
            "topic": guide_topic,
            "prerequisites": [],
            "steps": [],
            "screenshots_needed": [],
            "tips_and_tricks": [],
            "common_issues": [],
            "related_topics": [],
        }

        # TODO: 实际实现中生成用户指南
        return TaskResult(
            success=True,
            output=guide_result,
            metadata={"writing_type": "user_guide"},
        )

    async def _write_api_docs(self, context: TaskContext) -> TaskResult:
        """编写 API 文档"""
        api_info = context.task_description

        # 收集 API 规范
        api_specs = []
        for output in context.upstream_outputs:
            if isinstance(output, dict):
                if "endpoints" in output:
                    api_specs.append(output)

        api_docs_result = {
            "api_name": api_info,
            "authentication": "",
            "base_url": "",
            "endpoints": [],
            "data_models": [],
            "error_codes": [],
            "rate_limits": "",
            "sdks": [],
        }

        # TODO: 实际实现中生成 API 文档
        return TaskResult(
            success=True,
            output=api_docs_result,
            metadata={"writing_type": "api_docs"},
        )

    async def _do_general_writing(self, context: TaskContext) -> TaskResult:
        """执行一般写作任务"""
        writing_result = {
            "topic": context.task_description,
            "content": "",
            "outline": [],
            "key_points": [],
            "references": [],
        }

        # 整合上游信息
        for output in context.upstream_outputs:
            if isinstance(output, dict) and "content" in output:
                writing_result["key_points"].append(output["content"])

        return TaskResult(
            success=True,
            output=writing_result,
            metadata={"writing_type": "general"},
        )

    def create_content_outline(self, topic: str, sections: list[str]) -> dict[str, Any]:
        """创建内容大纲"""
        return {
            "topic": topic,
            "sections": sections,
            "estimated_length": "",
            "target_audience": "",
        }

    def define_brand_voice(
        self,
        personality: list[str],
        tone_variations: dict[str, str],
        dos_and_donts: list[str],
    ) -> dict[str, Any]:
        """定义品牌语调"""
        return {
            "personality": personality,
            "tone_variations": tone_variations,
            "dos_and_donts": dos_and_donts,
        }
