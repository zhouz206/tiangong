"""
Skill 执行器单元测试
"""
import pytest
from app.skills.base import reset_registry, SkillContext, SkillResult
from app.skills.loader import reset_loader
from app.skills.executor import (
    SkillExecutor,
    SkillExecutionError,
    SkillTimeoutError,
    SkillValidationError,
    ExecutionRecord,
    ExecutionStats,
    get_executor,
    reset_executor,
    execute_skill,
)


@pytest.fixture
def clean_executor():
    """清理执行器、注册表和加载器"""
    reset_registry()
    reset_loader()
    reset_executor()
    yield
    reset_registry()
    reset_loader()
    reset_executor()


class TestExecutionRecord:
    """测试执行记录"""

    def test_record_creation(self):
        """测试记录创建"""
        from datetime import datetime
        record = ExecutionRecord(
            skill_id="test",
            start_time=datetime.utcnow(),
        )

        assert record.skill_id == "test"
        assert record.success is False
        assert record.error is None
        assert record.duration == 0.0

    def test_record_with_result(self):
        """测试带结果的记录"""
        from datetime import datetime
        start = datetime.utcnow()
        record = ExecutionRecord(
            skill_id="test",
            start_time=start,
            success=True,
            result={"output": "data"},
        )

        assert record.success is True
        assert record.result == {"output": "data"}


class TestExecutionStats:
    """测试执行统计"""

    def test_stats_defaults(self):
        """测试默认统计"""
        stats = ExecutionStats()

        assert stats.total_executions == 0
        assert stats.successful_executions == 0
        assert stats.failed_executions == 0
        assert stats.total_duration == 0.0
        assert stats.avg_duration == 0.0
        assert stats.success_rate == 0.0

    def test_stats_calculations(self):
        """测试统计计算"""
        stats = ExecutionStats(
            total_executions=10,
            successful_executions=8,
            failed_executions=2,
            total_duration=100.0,
        )

        assert stats.avg_duration == 10.0
        assert stats.success_rate == 0.8

    def test_stats_last_execution(self):
        """测试最后执行时间"""
        from datetime import datetime
        now = datetime.utcnow()
        stats = ExecutionStats(last_execution=now)

        assert stats.last_execution == now


class TestSkillExecutor:
    """测试 Skill 执行器"""

    @pytest.fixture
    def executor(self, clean_executor):
        """创建执行器"""
        # 先加载内置 Skill
        from app.skills.loader import load_all_builtin
        load_all_builtin()
        return SkillExecutor()

    @pytest.mark.asyncio
    async def test_executor_initialization(self, executor):
        """测试执行器初始化"""
        assert executor.registry is not None
        assert executor.loader is not None
        assert executor._max_concurrent == 10

    @pytest.mark.asyncio
    async def test_execute_code_analysis(self, executor):
        """测试执行代码分析"""
        result = await executor.execute(
            skill_id="code_analysis",
            input_data={
                "code": "def hello():\n    return 'world'",
                "analysis_type": "all",
            },
        )

        assert result.success is True
        assert "metrics" in result.output
        assert "issues" in result.output
        assert "suggestions" in result.output

    @pytest.mark.asyncio
    async def test_execute_security_scan(self, executor):
        """测试执行安全扫描"""
        result = await executor.execute(
            skill_id="security_scan",
            input_data={
                "code": "password = 'secret123'\nprint(password)",
                "scan_type": "all",
            },
        )

        assert result.success is True
        assert "vulnerabilities" in result.output
        assert "risk_score" in result.output
        # 应该检测到硬编码密码
        assert len(result.output["vulnerabilities"]) > 0

    @pytest.mark.asyncio
    async def test_execute_formatting(self, executor):
        """测试执行格式化"""
        code = "def hello( ): \n    return 'world'\n\n\n\n"
        result = await executor.execute(
            skill_id="formatting",
            input_data={
                "code": code,
                "language": "python",
            },
        )

        assert result.success is True
        assert "formatted_code" in result.output
        assert "changes" in result.output

    @pytest.mark.asyncio
    async def test_execute_not_found(self, executor):
        """测试执行不存在的 Skill"""
        with pytest.raises(SkillExecutionError) as exc_info:
            await executor.execute(
                skill_id="nonexistent",
                input_data={},
            )
        assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_execute_with_metadata(self, executor):
        """测试带元数据执行"""
        result = await executor.execute(
            skill_id="code_analysis",
            input_data={"code": "x = 1"},
            metadata={"project": "test"},
        )

        assert result.success is True
        assert "execution_time" in result.metadata

    @pytest.mark.asyncio
    async def test_execute_with_timeout(self, executor):
        """测试带超时执行"""
        result = await executor.execute(
            skill_id="code_analysis",
            input_data={"code": "x = 1"},
            timeout=60,
        )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_get_stats(self, executor):
        """测试获取统计"""
        await executor.execute(
            skill_id="code_analysis",
            input_data={"code": "x = 1"},
        )

        stats = executor.get_stats("code_analysis")
        assert stats is not None
        assert stats.total_executions >= 1

    @pytest.mark.asyncio
    async def test_get_all_stats(self, executor):
        """测试获取所有统计"""
        await executor.execute(
            skill_id="code_analysis",
            input_data={"code": "x = 1"},
        )
        await executor.execute(
            skill_id="formatting",
            input_data={"code": "x = 1"},
        )

        all_stats = executor.get_all_stats()
        assert len(all_stats) >= 2

    @pytest.mark.asyncio
    async def test_get_history(self, executor):
        """测试获取执行历史"""
        await executor.execute(
            skill_id="code_analysis",
            input_data={"code": "x = 1"},
        )

        history = executor.get_history("code_analysis", limit=10)
        assert len(history) >= 1
        assert history[0].skill_id == "code_analysis"

    @pytest.mark.asyncio
    async def test_clear_history(self, executor):
        """测试清空历史"""
        await executor.execute(
            skill_id="code_analysis",
            input_data={"code": "x = 1"},
        )

        executor.clear_history("code_analysis")
        history = executor.get_history("code_analysis")
        assert len(history) == 0

    @pytest.mark.asyncio
    async def test_reset_stats(self, executor):
        """测试重置统计"""
        await executor.execute(
            skill_id="code_analysis",
            input_data={"code": "x = 1"},
        )

        executor.reset_stats("code_analysis")
        stats = executor.get_stats("code_analysis")
        assert stats is None

    @pytest.mark.asyncio
    async def test_execute_batch(self, executor):
        """测试批量执行"""
        tasks = [
            {"skill_id": "code_analysis", "input_data": {"code": "x = 1"}},
            {"skill_id": "formatting", "input_data": {"code": "x = 1"}},
        ]

        results = await executor.execute_batch(tasks, max_concurrent=2)

        assert len(results) == 2
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_execute_with_retry_success(self, executor):
        """测试带重试执行（成功）"""
        result = await executor.execute_with_retry(
            skill_id="code_analysis",
            input_data={"code": "x = 1"},
            max_retries=3,
        )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_concurrent_execution(self, executor):
        """测试并发执行"""
        tasks = [
            {"skill_id": "code_analysis", "input_data": {"code": f"x = {i}"}}
            for i in range(5)
        ]

        results = await executor.execute_batch(tasks, max_concurrent=3)

        assert len(results) == 5
        assert all(r.success for r in results)


class TestSkillExecutorValidation:
    """测试执行器验证"""

    @pytest.fixture
    def executor(self, clean_executor):
        from app.skills.loader import load_all_builtin
        load_all_builtin()
        return SkillExecutor()

    @pytest.mark.asyncio
    async def test_execute_disabled_skill(self, executor):
        """测试执行已禁用的 Skill"""
        # 禁用 Skill
        executor.registry.disable("code_analysis")

        with pytest.raises(SkillExecutionError) as exc_info:
            await executor.execute(
                skill_id="code_analysis",
                input_data={"code": "x = 1"},
            )
        assert "disabled" in str(exc_info.value).lower()


class TestGlobalExecutor:
    """测试全局执行器"""

    def test_get_executor_singleton(self, clean_executor):
        """测试单例"""
        exec1 = get_executor()
        exec2 = get_executor()
        assert exec1 is exec2


class TestExecuteSkillFunction:
    """测试 execute_skill 便捷函数"""

    @pytest.mark.asyncio
    async def test_execute_skill_function(self, clean_executor):
        """测试便捷函数执行"""
        from app.skills.loader import load_all_builtin
        load_all_builtin()

        result = await execute_skill(
            skill_id="code_analysis",
            input_data={"code": "x = 1"},
        )

        assert result.success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
