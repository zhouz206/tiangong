"""
内置 Skill 单元测试
"""
import pytest
from app.skills.base import SkillContext, SkillResult
from app.skills.builtin.code_analysis import CodeAnalysisSkill
from app.skills.builtin.security_scan import SecurityScanSkill
from app.skills.builtin.formatting import FormattingSkill


class TestCodeAnalysisSkill:
    """测试代码分析 Skill"""

    @pytest.fixture
    def skill(self):
        return CodeAnalysisSkill()

    def test_get_info(self, skill):
        """测试获取元信息"""
        info = skill.get_info()
        assert info.skill_id == "code_analysis"
        assert info.name == "Code Analysis"
        assert info.category.value == "code"
        assert "code" in info.tags

    def test_validate_input_empty(self, skill):
        """测试空输入验证"""
        ctx = SkillContext(skill_id="code_analysis", input_data=None)
        is_valid, error = skill.validate_input(ctx)
        assert is_valid is False
        assert "required" in error.lower()

    def test_validate_input_no_code_or_file(self, skill):
        """测试无代码无文件验证"""
        ctx = SkillContext(skill_id="code_analysis", input_data={})
        is_valid, error = skill.validate_input(ctx)
        assert is_valid is False

    def test_validate_input_with_code(self, skill):
        """测试带代码验证"""
        ctx = SkillContext(
            skill_id="code_analysis",
            input_data={"code": "x = 1"},
        )
        is_valid, error = skill.validate_input(ctx)
        assert is_valid is True
        assert error is None

    @pytest.mark.asyncio
    async def test_execute_complexity_analysis(self, skill):
        """测试复杂度分析"""
        code = """
def simple():
    return 1

def complex():
    if x > 1:
        if y > 2:
            if z > 3:
                return True
    return False
"""
        ctx = SkillContext(
            skill_id="code_analysis",
            input_data={"code": code, "analysis_type": "complexity"},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        assert "metrics" in result.output
        assert "function_count" in result.output["metrics"]

    @pytest.mark.asyncio
    async def test_execute_style_analysis(self, skill):
        """测试风格分析"""
        code = "x=1  \ny = 2  \n"  # 有空格问题
        ctx = SkillContext(
            skill_id="code_analysis",
            input_data={"code": code, "analysis_type": "style"},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        assert "issues" in result.output

    @pytest.mark.asyncio
    async def test_execute_structure_analysis(self, skill):
        """测试结构分析"""
        code = """
import os
import sys
import unused_module

def hello():
    pass
"""
        ctx = SkillContext(
            skill_id="code_analysis",
            input_data={"code": code, "analysis_type": "structure"},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        assert "metrics" in result.output

    @pytest.mark.asyncio
    async def test_execute_all_analysis(self, skill):
        """测试完整分析"""
        code = "def hello():\n    return 'world'"
        ctx = SkillContext(
            skill_id="code_analysis",
            input_data={"code": code},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        assert "metrics" in result.output
        assert "issues" in result.output
        assert "suggestions" in result.output

    @pytest.mark.asyncio
    async def test_execute_syntax_error(self, skill):
        """测试语法错误处理"""
        code = "def invalid(\n    return 1"  # 语法错误
        ctx = SkillContext(
            skill_id="code_analysis",
            input_data={"code": code},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        # 应该检测到语法错误
        assert "syntax_error" in str(result.output).lower() or result.output.get("issues")

    @pytest.mark.asyncio
    async def test_execute_metadata(self, skill):
        """测试执行元数据"""
        ctx = SkillContext(
            skill_id="code_analysis",
            input_data={"code": "x = 1"},
        )

        result = await skill.execute(ctx)

        assert "execution_time" in result.metadata
        assert "code_length" in result.metadata


class TestSecurityScanSkill:
    """测试安全扫描 Skill"""

    @pytest.fixture
    def skill(self):
        return SecurityScanSkill()

    def test_get_info(self, skill):
        """测试获取元信息"""
        info = skill.get_info()
        assert info.skill_id == "security_scan"
        assert info.name == "Security Scan"
        assert info.category.value == "security"
        assert "security" in info.tags

    def test_validate_input_empty(self, skill):
        """测试空输入验证"""
        ctx = SkillContext(skill_id="security_scan", input_data=None)
        is_valid, error = skill.validate_input(ctx)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_scan_hardcoded_password(self, skill):
        """测试检测硬编码密码"""
        code = "password = 'secret123'"
        ctx = SkillContext(
            skill_id="security_scan",
            input_data={"code": code, "scan_type": "secrets"},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        assert len(result.output["vulnerabilities"]) > 0
        vuln_types = [v["type"] for v in result.output["vulnerabilities"]]
        assert "hardcoded_secret" in vuln_types

    @pytest.mark.asyncio
    async def test_scan_api_key(self, skill):
        """测试检测 API 密钥"""
        code = "api_key = 'sk-1234567890'"
        ctx = SkillContext(
            skill_id="security_scan",
            input_data={"code": code, "scan_type": "secrets"},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        vuln_types = [v["type"] for v in result.output["vulnerabilities"]]
        assert "hardcoded_secret" in vuln_types

    @pytest.mark.asyncio
    async def test_scan_eval_usage(self, skill):
        """测试检测 eval 使用"""
        code = "result = eval(user_input)"
        ctx = SkillContext(
            skill_id="security_scan",
            input_data={"code": code, "scan_type": "injection"},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        vuln_types = [v["type"] for v in result.output["vulnerabilities"]]
        assert "code_injection" in vuln_types

    @pytest.mark.asyncio
    async def test_scan_shell_true(self, skill):
        """测试检测 shell=True"""
        code = "subprocess.run(cmd, shell=True)"
        ctx = SkillContext(
            skill_id="security_scan",
            input_data={"code": code, "scan_type": "injection"},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        vuln_types = [v["type"] for v in result.output["vulnerabilities"]]
        assert "command_injection" in vuln_types

    @pytest.mark.asyncio
    async def test_scan_ssl_verify_false(self, skill):
        """测试检测 SSL 验证禁用"""
        code = "requests.get(url, verify=False)"
        ctx = SkillContext(
            skill_id="security_scan",
            input_data={"code": code, "scan_type": "unsafe_ops"},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        vuln_types = [v["type"] for v in result.output["vulnerabilities"]]
        assert "insecure_request" in vuln_types

    @pytest.mark.asyncio
    async def test_scan_pickle_usage(self, skill):
        """测试检测 pickle 使用"""
        code = "data = pickle.loads(user_data)"
        ctx = SkillContext(
            skill_id="security_scan",
            input_data={"code": code, "scan_type": "unsafe_ops"},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        vuln_types = [v["type"] for v in result.output["vulnerabilities"]]
        assert "unsafe_deserialization" in vuln_types

    @pytest.mark.asyncio
    async def test_risk_score_calculation(self, skill):
        """测试风险评分计算"""
        code = "password = 'secret'\neval(x)"
        ctx = SkillContext(
            skill_id="security_scan",
            input_data={"code": code},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        assert "risk_score" in result.output
        assert result.output["risk_score"] > 0

    @pytest.mark.asyncio
    async def test_severity_filter(self, skill):
        """测试严重程度过滤"""
        code = "password = 'secret'"
        ctx = SkillContext(
            skill_id="security_scan",
            input_data={
                "code": code,
                "severity_threshold": "critical",
            },
        )

        result = await skill.execute(ctx)

        assert result.success is True
        # 只应该包含 critical 级别
        for vuln in result.output["vulnerabilities"]:
            assert vuln["severity"] == "critical"

    @pytest.mark.asyncio
    async def test_scan_summary(self, skill):
        """测试扫描摘要"""
        code = "password = 'secret'"
        ctx = SkillContext(
            skill_id="security_scan",
            input_data={"code": code},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        assert "summary" in result.output
        summary = result.output["summary"]
        assert "total_issues" in summary
        assert "critical" in summary


class TestFormattingSkill:
    """测试格式化 Skill"""

    @pytest.fixture
    def skill(self):
        return FormattingSkill()

    def test_get_info(self, skill):
        """测试获取元信息"""
        info = skill.get_info()
        assert info.skill_id == "formatting"
        assert info.name == "Code Formatting"
        assert info.category.value == "formatting"
        assert "formatting" in info.tags

    def test_validate_input_empty(self, skill):
        """测试空输入验证"""
        ctx = SkillContext(skill_id="formatting", input_data=None)
        is_valid, error = skill.validate_input(ctx)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_format_remove_trailing_whitespace(self, skill):
        """测试去除行尾空格"""
        code = "x = 1  \ny = 2  \n"
        ctx = SkillContext(
            skill_id="formatting",
            input_data={"code": code, "language": "python"},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        formatted = result.output["formatted_code"]
        assert "  \n" not in formatted

    @pytest.mark.asyncio
    async def test_format_convert_tabs(self, skill):
        """测试制表符转换"""
        code = "def hello():\n\treturn 1\n"
        ctx = SkillContext(
            skill_id="formatting",
            input_data={"code": code, "language": "python"},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        formatted = result.output["formatted_code"]
        assert "\t" not in formatted

    @pytest.mark.asyncio
    async def test_format_normalize_blank_lines(self, skill):
        """测试空白行规范化"""
        code = "x = 1\n\n\n\ny = 2\n"
        ctx = SkillContext(
            skill_id="formatting",
            input_data={"code": code, "language": "python"},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        formatted = result.output["formatted_code"]
        # 不应该有超过 2 个连续空白行
        assert "\n\n\n\n" not in formatted

    @pytest.mark.asyncio
    async def test_format_sort_imports(self, skill):
        """测试导入排序"""
        code = """import os
import mymodule
import sys
"""
        ctx = SkillContext(
            skill_id="formatting",
            input_data={"code": code, "language": "python"},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        # 标准库应该排在前面
        formatted = result.output["formatted_code"]
        lines = formatted.split("\n")
        import_lines = [l for l in lines if l.startswith("import ")]
        if len(import_lines) >= 2:
            assert import_lines[0].startswith("import os") or import_lines[0].startswith("import sys")

    @pytest.mark.asyncio
    async def test_format_add_newline_at_end(self, skill):
        """测试添加文件末尾换行"""
        code = "x = 1"  # 没有末尾换行
        ctx = SkillContext(
            skill_id="formatting",
            input_data={"code": code, "language": "python"},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        formatted = result.output["formatted_code"]
        assert formatted.endswith("\n")

    @pytest.mark.asyncio
    async def test_format_changes_tracking(self, skill):
        """测试更改追踪"""
        code = "x=1  \n"
        ctx = SkillContext(
            skill_id="formatting",
            input_data={"code": code, "language": "python"},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        assert "changes" in result.output
        assert len(result.output["changes"]) > 0

    @pytest.mark.asyncio
    async def test_format_stats(self, skill):
        """测试格式化统计"""
        code = "x = 1"
        ctx = SkillContext(
            skill_id="formatting",
            input_data={"code": code, "language": "python"},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        assert "stats" in result.output
        stats = result.output["stats"]
        assert "original_lines" in stats
        assert "formatted_lines" in stats
        assert "changes_count" in stats

    @pytest.mark.asyncio
    async def test_format_javascript(self, skill):
        """测试 JavaScript 格式化"""
        code = "function hello( ) { \n    return 1;\n}\n"
        ctx = SkillContext(
            skill_id="formatting",
            input_data={"code": code, "language": "javascript"},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        formatted = result.output["formatted_code"]
        assert formatted is not None

    @pytest.mark.asyncio
    async def test_format_options(self, skill):
        """测试格式化选项"""
        code = "x = 1"
        ctx = SkillContext(
            skill_id="formatting",
            input_data={
                "code": code,
                "language": "python",
                "options": {
                    "max_line_length": 80,
                    "indent_size": 2,
                    "sort_imports": False,
                },
            },
        )

        result = await skill.execute(ctx)

        assert result.success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
