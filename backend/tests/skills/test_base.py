"""
Skill 基类单元测试
"""
import pytest
from app.skills.base import (
    Skill,
    SkillCategory,
    SkillStatus,
    SkillContext,
    SkillResult,
    SkillInfo,
    SkillRegistry,
    get_registry,
    reset_registry,
    register_skill,
    get_skill,
)


class MockSkill(Skill):
    """用于测试的 Mock Skill"""

    def __init__(self, skill_id: str = "test_skill"):
        super().__init__()
        self._skill_id = skill_id
        self._execute_called = False

    def get_info(self) -> SkillInfo:
        return SkillInfo(
            skill_id=self._skill_id,
            name="Test Skill",
            description="A test skill",
            category=SkillCategory.UTILITY,
            version="1.0.0",
            author="Test",
            tags=["test", "mock"],
        )

    async def execute(self, context: SkillContext) -> SkillResult:
        self._before_execute()
        self._execute_called = True
        result = SkillResult(
            success=True,
            output={"executed": True, "input": context.input_data},
        )
        self._after_execute(result)
        return result


@pytest.fixture
def clean_registry():
    """清理注册表"""
    reset_registry()
    yield
    reset_registry()


class TestSkillCategory:
    """测试 Skill 类别枚举"""

    def test_category_values(self):
        """测试类别枚举值"""
        assert SkillCategory.CODE.value == "code"
        assert SkillCategory.SECURITY.value == "security"
        assert SkillCategory.FORMATTING.value == "formatting"
        assert SkillCategory.ANALYSIS.value == "analysis"
        assert SkillCategory.UTILITY.value == "utility"
        assert SkillCategory.CUSTOM.value == "custom"


class TestSkillStatus:
    """测试 Skill 状态枚举"""

    def test_status_values(self):
        """测试状态枚举值"""
        assert SkillStatus.READY.value == "ready"
        assert SkillStatus.RUNNING.value == "running"
        assert SkillStatus.COMPLETED.value == "completed"
        assert SkillStatus.FAILED.value == "failed"
        assert SkillStatus.DISABLED.value == "disabled"


class TestSkillContext:
    """测试 Skill 上下文"""

    def test_context_creation(self):
        """测试上下文创建"""
        ctx = SkillContext(
            skill_id="test",
            input_data={"key": "value"},
        )

        assert ctx.skill_id == "test"
        assert ctx.input_data == {"key": "value"}
        assert ctx.metadata == {}
        assert ctx.timeout == 300

    def test_context_with_metadata(self):
        """测试带元数据的上下文"""
        ctx = SkillContext(
            skill_id="test",
            input_data="data",
            metadata={"project": "test"},
            timeout=60,
        )

        assert ctx.metadata == {"project": "test"}
        assert ctx.timeout == 60


class TestSkillResult:
    """测试 Skill 结果"""

    def test_success_result(self):
        """测试成功结果"""
        result = SkillResult(success=True, output={"data": "value"})

        assert result.success is True
        assert result.output == {"data": "value"}
        assert result.error is None

    def test_failure_result(self):
        """测试失败结果"""
        result = SkillResult(
            success=False,
            error="Something went wrong",
        )

        assert result.success is False
        assert result.error == "Something went wrong"
        assert result.output is None

    def test_result_with_metadata(self):
        """测试带元数据的结果"""
        result = SkillResult(
            success=True,
            output={},
            metadata={"execution_time": 1.5},
        )

        assert result.metadata["execution_time"] == 1.5

    def test_result_auto_execution_time(self):
        """测试自动执行时间"""
        result = SkillResult(success=True)
        assert "execution_time" in result.metadata
        assert result.metadata["execution_time"] == 0.0


class TestSkillInfo:
    """测试 Skill 元信息"""

    def test_info_creation(self):
        """测试元信息创建"""
        info = SkillInfo(
            skill_id="test",
            name="Test",
            description="Test skill",
            category=SkillCategory.CODE,
        )

        assert info.skill_id == "test"
        assert info.name == "Test"
        assert info.description == "Test skill"
        assert info.category == SkillCategory.CODE
        assert info.version == "1.0.0"
        assert info.author == ""
        assert info.tags == []

    def test_info_with_all_fields(self):
        """测试完整元信息"""
        info = SkillInfo(
            skill_id="test",
            name="Test",
            description="Test",
            category=SkillCategory.CODE,
            version="2.0.0",
            author="Author",
            tags=["tag1", "tag2"],
            input_schema={"type": "object"},
            output_schema={"type": "object"},
        )

        assert info.version == "2.0.0"
        assert info.author == "Author"
        assert info.tags == ["tag1", "tag2"]
        assert info.input_schema == {"type": "object"}


class TestSkill:
    """测试 Skill 基类"""

    @pytest.fixture
    def skill(self):
        """创建测试 Skill"""
        return MockSkill()

    def test_skill_initialization(self, skill):
        """测试 Skill 初始化"""
        assert skill.status == SkillStatus.READY
        assert skill.is_initialized is False
        assert skill.is_ready is True
        assert skill.last_executed is None
        assert skill.execution_count == 0

    def test_get_info(self, skill):
        """测试获取元信息"""
        info = skill.get_info()
        assert info.skill_id == "test_skill"
        assert info.name == "Test Skill"
        assert info.category == SkillCategory.UTILITY

    def test_initialize(self, skill):
        """测试初始化"""
        result = skill.initialize()
        assert result is True
        assert skill.is_initialized is True
        assert skill.status == SkillStatus.READY

    def test_cleanup(self, skill):
        """测试清理"""
        skill.initialize()
        skill.cleanup()
        assert skill.is_initialized is False

    def test_validate_input_default(self, skill):
        """测试默认输入验证"""
        ctx = SkillContext(skill_id="test", input_data={})
        is_valid, error = skill.validate_input(ctx)
        assert is_valid is True
        assert error is None

    @pytest.mark.asyncio
    async def test_execute(self, skill):
        """测试执行"""
        ctx = SkillContext(
            skill_id="test",
            input_data={"test": "data"},
        )

        result = await skill.execute(ctx)

        assert result.success is True
        assert result.output["executed"] is True
        assert result.output["input"] == {"test": "data"}
        assert skill._execute_called is True

    @pytest.mark.asyncio
    async def test_execute_updates_state(self, skill):
        """测试执行更新状态"""
        ctx = SkillContext(skill_id="test", input_data={})

        assert skill.status == SkillStatus.READY
        await skill.execute(ctx)
        assert skill.status == SkillStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_execute_updates_counters(self, skill):
        """测试执行更新计数器"""
        ctx = SkillContext(skill_id="test", input_data={})

        assert skill.execution_count == 0
        assert skill.last_executed is None

        await skill.execute(ctx)

        assert skill.execution_count == 1
        assert skill.last_executed is not None

    def test_repr(self, skill):
        """测试字符串表示"""
        assert repr(skill) == "<Skill test_skill v1.0.0>"


class TestSkillRegistry:
    """测试 Skill 注册表"""

    @pytest.fixture
    def registry(self, clean_registry):
        """创建注册表"""
        return SkillRegistry()

    def test_register_skill(self, registry):
        """测试注册 Skill"""
        skill = MockSkill("skill-1")
        result = registry.register(skill)

        assert result is True
        assert registry.is_registered("skill-1") is True
        assert registry.get("skill-1") is skill

    def test_register_duplicate(self, registry):
        """测试重复注册"""
        skill1 = MockSkill("skill-1")
        skill2 = MockSkill("skill-1")

        assert registry.register(skill1) is True
        assert registry.register(skill2) is False

    def test_unregister_skill(self, registry):
        """测试注销 Skill"""
        skill = MockSkill("skill-1")
        registry.register(skill)

        result = registry.unregister("skill-1")

        assert result is True
        assert registry.is_registered("skill-1") is False
        assert registry.get("skill-1") is None

    def test_get_or_raise(self, registry):
        """测试获取或抛出异常"""
        skill = MockSkill("skill-1")
        registry.register(skill)

        retrieved = registry.get_or_raise("skill-1")
        assert retrieved is skill

        with pytest.raises(KeyError):
            registry.get_or_raise("nonexistent")

    def test_get_all(self, registry):
        """测试获取所有"""
        registry.register(MockSkill("skill-1"))
        registry.register(MockSkill("skill-2"))

        skills = registry.get_all()
        assert len(skills) == 2

    def test_get_info_all(self, registry):
        """测试获取所有元信息"""
        registry.register(MockSkill("skill-1"))
        registry.register(MockSkill("skill-2"))

        infos = registry.get_info_all()
        assert len(infos) == 2
        assert all(isinstance(info, SkillInfo) for info in infos)

    def test_get_by_category(self, registry):
        """测试按类别获取"""
        skill1 = MockSkill("skill-1")
        skill2 = MockSkill("skill-2")
        
        # 修改 skill2 的类别
        original_get_info = skill2.get_info
        skill2.get_info = lambda: SkillInfo(
            skill_id="skill-2",
            name="Test",
            description="Test",
            category=SkillCategory.CODE,
        )

        registry.register(skill1)
        registry.register(skill2)

        code_skills = registry.get_by_category(SkillCategory.CODE)
        assert len(code_skills) == 1
        assert code_skills[0].get_info().skill_id == "skill-2"

    def test_get_by_tag(self, registry):
        """测试按标签获取"""
        skill = MockSkill("skill-1")
        registry.register(skill)

        tagged = registry.get_by_tag("test")
        assert len(tagged) == 1

    def test_search(self, registry):
        """测试搜索"""
        skill = MockSkill("skill-1")
        registry.register(skill)

        results = registry.search("test")
        assert len(results) == 1

        results = registry.search("nonexistent")
        assert len(results) == 0

    def test_enable_disable(self, registry):
        """测试启用禁用"""
        skill = MockSkill("skill-1")
        registry.register(skill)

        assert registry.is_enabled("skill-1") is True

        registry.disable("skill-1")
        assert registry.is_enabled("skill-1") is False

        registry.enable("skill-1")
        assert registry.is_enabled("skill-1") is True

    def test_count(self, registry):
        """测试计数"""
        assert registry.count() == 0

        registry.register(MockSkill("skill-1"))
        assert registry.count() == 1

        registry.register(MockSkill("skill-2"))
        assert registry.count() == 2

    def test_clear(self, registry):
        """测试清空"""
        registry.register(MockSkill("skill-1"))
        registry.register(MockSkill("skill-2"))

        registry.clear()

        assert registry.count() == 0
        assert registry.get("skill-1") is None


class TestGlobalRegistry:
    """测试全局注册表函数"""

    def test_get_registry_singleton(self, clean_registry):
        """测试单例"""
        reg1 = get_registry()
        reg2 = get_registry()
        assert reg1 is reg2

    def test_register_skill_global(self, clean_registry):
        """测试全局注册"""
        skill = MockSkill("global-skill")
        result = register_skill(skill)

        assert result is True
        assert get_skill("global-skill") is skill

    def test_get_skill_global(self, clean_registry):
        """测试全局获取"""
        skill = MockSkill("global-skill")
        register_skill(skill)

        retrieved = get_skill("global-skill")
        assert retrieved is skill

        nonexistent = get_skill("nonexistent")
        assert nonexistent is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
