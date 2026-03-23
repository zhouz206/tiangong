"""
程序员 Agent

职责:
- 代码编写和实现
- 代码重构
- Bug 修复
- 单元测试编写
"""
from typing import Any, Optional

from app.core.agent import Agent, AgentCapability, TaskContext, TaskResult
from app.core.message import MessageBus


class CoderAgent(Agent):
    """
    程序员 Agent

    负责代码编写、实现功能、修复 Bug 和单元测试。
    """

    def __init__(
        self,
        agent_id: str,
        name: str = "Coder",
        message_bus: Optional[MessageBus] = None,
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            role="coder",
            capabilities=[
                AgentCapability.CODE_GENERATION,
                AgentCapability.CODE_REVIEW,
            ],
            message_bus=message_bus,
        )

        # 程序员特有配置
        self.temperature = 0.2  # 低温度，代码需要精确
        self.max_tokens = 4096

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的程序员 Agent。

你的职责:
1. 根据需求文档和设计规范编写高质量代码
2. 实现功能模块，确保代码可维护、可扩展
3. 修复 Bug 和技术债务
4. 编写单元测试，确保代码质量
5. 遵循编码规范和最佳实践

工作原则:
- 代码简洁清晰，避免过度设计
- 函数职责单一，保持高内聚低耦合
- 命名语义化，注释说明"为什么"而非"是什么"
- 优先复用现有代码，避免重复造轮子
- 编写可测试的代码，保持高覆盖率

输出格式:
- 代码实现应包含：完整代码、关键说明、使用示例
- Bug 修复应包含：问题描述、原因分析、修复方案、验证方法
- 重构应包含：重构目标、改动说明、影响范围、测试建议
"""

    async def execute_task(self, context: TaskContext) -> TaskResult:
        """
        执行编程任务

        处理任务类型:
        - implement_feature: 功能实现
        - fix_bug: Bug 修复
        - refactor: 代码重构
        - write_tests: 单元测试编写
        - code_review: 代码审查
        """
        try:
            task_type = context.metadata.get("task_type", "general")

            if task_type == "implement_feature":
                return await self._implement_feature(context)
            elif task_type == "fix_bug":
                return await self._fix_bug(context)
            elif task_type == "refactor":
                return await self._refactor_code(context)
            elif task_type == "write_tests":
                return await self._write_tests(context)
            elif task_type == "code_review":
                return await self._code_review(context)
            else:
                return await self._general_coding(context)

        except Exception as e:
            return TaskResult(
                success=False,
                error=f"Coding task failed: {str(e)}",
            )

    async def _implement_feature(self, context: TaskContext) -> TaskResult:
        """实现功能"""
        feature_desc = context.task_description

        # 收集上游输出（设计文档、规范等）
        design_docs = []
        specs = []
        for output in context.upstream_outputs:
            if isinstance(output, dict):
                if "design" in output:
                    design_docs.append(output["design"])
                if "spec" in output:
                    specs.append(output["spec"])

        code_result = {
            "feature": feature_desc,
            "files": [],
            "code_changes": [],
            "dependencies": [],
            "implementation_notes": "",
        }

        # TODO: 实际实现中调用 LLM 生成代码
        return TaskResult(
            success=True,
            output=code_result,
            metadata={"task_type": "feature_implementation"},
        )

    async def _fix_bug(self, context: TaskContext) -> TaskResult:
        """修复 Bug"""
        bug_desc = context.task_description

        # 收集 Bug 相关信息
        error_logs = []
        repro_steps = []
        for output in context.upstream_outputs:
            if isinstance(output, dict):
                if "logs" in output:
                    error_logs.append(output["logs"])
                if "steps" in output:
                    repro_steps.append(output["steps"])

        fix_result = {
            "bug_description": bug_desc,
            "root_cause": "",
            "fix_location": [],
            "code_changes": [],
            "verification_steps": [],
            "prevention_measures": [],
        }

        # TODO: 实际实现中分析 Bug 并生成修复代码
        return TaskResult(
            success=True,
            output=fix_result,
            metadata={"task_type": "bug_fix"},
        )

    async def _refactor_code(self, context: TaskContext) -> TaskResult:
        """代码重构"""
        refactor_target = context.task_description

        refactor_result = {
            "target": refactor_target,
            "refactor_type": "",  # extract, rename, restructure, etc.
            "before_code": "",
            "after_code": "",
            "improvements": [],
            "affected_files": [],
            "testing_required": True,
        }

        # TODO: 实际实现中生成重构代码
        return TaskResult(
            success=True,
            output=refactor_result,
            metadata={"task_type": "refactor"},
        )

    async def _write_tests(self, context: TaskContext) -> TaskResult:
        """编写测试"""
        test_target = context.task_description

        # 收集被测代码信息
        code_context = []
        for output in context.upstream_outputs:
            if isinstance(output, dict) and "code" in output:
                code_context.append(output["code"])

        test_result = {
            "target": test_target,
            "test_cases": [],
            "test_code": [],
            "coverage_estimate": 0.0,
            "edge_cases_covered": [],
        }

        # TODO: 实际实现中生成测试代码
        return TaskResult(
            success=True,
            output=test_result,
            metadata={"task_type": "tests"},
        )

    async def _code_review(self, context: TaskContext) -> TaskResult:
        """代码审查"""
        review_target = context.task_description

        # 收集待审查代码
        code_snippets = []
        for output in context.upstream_outputs:
            if isinstance(output, dict) and "code" in output:
                code_snippets.append(output["code"])

        review_result = {
            "target": review_target,
            "issues": [],
            "suggestions": [],
            "positive_feedback": [],
            "overall_assessment": "",
            "approval_recommendation": False,
        }

        # TODO: 实际实现中审查代码
        return TaskResult(
            success=True,
            output=review_result,
            metadata={"task_type": "code_review"},
        )

    async def _general_coding(self, context: TaskContext) -> TaskResult:
        """一般编程任务"""
        coding_result = {
            "task": context.task_description,
            "code": "",
            "explanation": "",
            "usage_example": "",
        }

        return TaskResult(
            success=True,
            output=coding_result,
            metadata={"task_type": "general_coding"},
        )

    def generate_code(
        self,
        language: str,
        description: str,
        requirements: list[str],
    ) -> dict[str, Any]:
        """生成代码框架"""
        return {
            "language": language,
            "description": description,
            "requirements": requirements,
            "code": "",
            "status": "generated",
        }

    def create_file_structure(
        self,
        project_type: str,
        files: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """创建文件结构"""
        return {
            "project_type": project_type,
            "files": files,
            "structure": {},
        }
