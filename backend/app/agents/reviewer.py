"""
审核员 Agent

职责:
- 代码质量审查
- 文档审查
- 设计审查
- 合规性检查
"""
from typing import Any, Optional

from app.core.agent import Agent, AgentCapability, TaskContext, TaskResult
from app.core.message import MessageBus


class ReviewerAgent(Agent):
    """
    审核员 Agent

    负责代码质量审查、文档审查、设计审查和合规性检查。
    """

    def __init__(
        self,
        agent_id: str,
        name: str = "Reviewer",
        message_bus: Optional[MessageBus] = None,
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            role="reviewer",
            capabilities=[
                AgentCapability.CODE_REVIEW,
                AgentCapability.DATA_ANALYSIS,
            ],
            message_bus=message_bus,
        )

        # 审核员特有配置
        self.temperature = 0.1  # 低温，审查需要严格一致
        self.max_tokens = 4096

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的审核员 Agent。

你的职责:
1. 审查代码质量，发现潜在问题和改进空间
2. 审查文档的准确性、完整性和可读性
3. 审查设计方案的合理性和一致性
4. 检查合规性和安全性问题
5. 提供建设性的改进建议

工作原则:
- 客观公正，基于事实和标准进行评估
- 细致全面，不放过任何潜在问题
- 建议具体可行，说明原因和解决方案
- 平衡严格和效率，优先关注重要问题
- 保持建设性语气，帮助团队提升质量

输出格式:
- 审查报告应包含：审查范围、发现的问题、严重程度、改进建议、总体评价
- 问题描述应包含：位置、问题说明、潜在影响、修复建议
- 合规检查应包含：检查项、结果、证据、风险等级
"""

    async def execute_task(self, context: TaskContext) -> TaskResult:
        """
        执行审查任务

        处理任务类型:
        - code_review: 代码审查
        - doc_review: 文档审查
        - design_review: 设计审查
        - security_review: 安全审查
        - compliance_check: 合规检查
        """
        try:
            task_type = context.metadata.get("task_type", "general")

            if task_type == "code_review":
                return await self._review_code(context)
            elif task_type == "doc_review":
                return await self._review_document(context)
            elif task_type == "design_review":
                return await self._review_design(context)
            elif task_type == "security_review":
                return await self._review_security(context)
            elif task_type == "compliance_check":
                return await self._check_compliance(context)
            else:
                return await self._do_general_review(context)

        except Exception as e:
            return TaskResult(
                success=False,
                error=f"Review task failed: {str(e)}",
            )

    async def _review_code(self, context: TaskContext) -> TaskResult:
        """代码审查"""
        code_target = context.task_description

        # 收集待审查代码
        code_snippets = []
        coding_standards = []
        for output in context.upstream_outputs:
            if isinstance(output, dict):
                if "code" in output:
                    code_snippets.append(output["code"])
                if "standards" in output:
                    coding_standards.append(output["standards"])

        review_result = {
            "target": code_target,
            "issues": [],
            "code_smells": [],
            "bugs": [],
            "vulnerabilities": [],
            "performance_concerns": [],
            "suggestions": [],
            "positive_feedback": [],
            "overall_score": 0.0,
            "approval_recommendation": False,
        }

        # TODO: 实际实现中分析代码
        return TaskResult(
            success=True,
            output=review_result,
            metadata={"review_type": "code"},
        )

    async def _review_document(self, context: TaskContext) -> TaskResult:
        """文档审查"""
        doc_target = context.task_description

        # 收集待审查文档
        documents = []
        for output in context.upstream_outputs:
            if isinstance(output, dict) and "content" in output:
                documents.append(output["content"])

        review_result = {
            "target": doc_target,
            "clarity_issues": [],
            "accuracy_issues": [],
            "completeness_issues": [],
            "style_issues": [],
            "grammar_errors": [],
            "suggestions": [],
            "overall_score": 0.0,
        }

        # TODO: 实际实现中审查文档
        return TaskResult(
            success=True,
            output=review_result,
            metadata={"review_type": "document"},
        )

    async def _review_design(self, context: TaskContext) -> TaskResult:
        """设计审查"""
        design_target = context.task_description

        # 收集设计方案
        designs = []
        design_principles = []
        for output in context.upstream_outputs:
            if isinstance(output, dict):
                if "design" in output:
                    designs.append(output["design"])
                if "principles" in output:
                    design_principles.append(output["principles"])

        review_result = {
            "target": design_target,
            "usability_issues": [],
            "consistency_issues": [],
            "accessibility_issues": [],
            "technical_feasibility": "",
            "suggestions": [],
            "overall_score": 0.0,
            "approval_recommendation": False,
        }

        # TODO: 实际实现中审查设计
        return TaskResult(
            success=True,
            output=review_result,
            metadata={"review_type": "design"},
        )

    async def _review_security(self, context: TaskContext) -> TaskResult:
        """安全审查"""
        security_target = context.task_description

        # 收集相关信息
        architecture = []
        data_flows = []
        for output in context.upstream_outputs:
            if isinstance(output, dict):
                if "architecture" in output:
                    architecture.append(output["architecture"])
                if "data_flow" in output:
                    data_flows.append(output["data_flow"])

        security_result = {
            "target": security_target,
            "threats_identified": [],
            "vulnerabilities": [],
            "risk_assessment": {},
            "mitigation_recommendations": [],
            "security_score": 0.0,
        }

        # TODO: 实际实现中进行安全分析
        return TaskResult(
            success=True,
            output=security_result,
            metadata={"review_type": "security"},
        )

    async def _check_compliance(self, context: TaskContext) -> TaskResult:
        """合规检查"""
        compliance_domain = context.task_description

        # 收集合规要求
        requirements = []
        standards = []
        for output in context.upstream_outputs:
            if isinstance(output, dict):
                if "requirements" in output:
                    requirements.append(output["requirements"])
                if "standards" in output:
                    standards.append(output["standards"])

        compliance_result = {
            "domain": compliance_domain,
            "checklist": [],
            "compliant_items": [],
            "non_compliant_items": [],
            "remediation_required": [],
            "compliance_score": 0.0,
        }

        # TODO: 实际实现中进行合规检查
        return TaskResult(
            success=True,
            output=compliance_result,
            metadata={"review_type": "compliance"},
        )

    async def _do_general_review(self, context: TaskContext) -> TaskResult:
        """执行一般审查任务"""
        review_result = {
            "target": context.task_description,
            "findings": [],
            "issues": [],
            "suggestions": [],
            "overall_assessment": "",
            "score": 0.0,
        }

        return TaskResult(
            success=True,
            output=review_result,
            metadata={"review_type": "general"},
        )

    def create_review_checklist(
        self,
        review_type: str,
        items: list[str],
    ) -> dict[str, Any]:
        """创建审查清单"""
        return {
            "review_type": review_type,
            "checklist": [{"item": item, "checked": False} for item in items],
        }

    def create_issue_report(
        self,
        title: str,
        severity: str,
        location: str,
        description: str,
        recommendation: str,
    ) -> dict[str, Any]:
        """创建问题报告"""
        return {
            "title": title,
            "severity": severity,  # critical, high, medium, low
            "location": location,
            "description": description,
            "recommendation": recommendation,
            "status": "open",
        }
