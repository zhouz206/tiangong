"""
Skill 基类和注册表

提供 Skill 系统的核心抽象，定义 Skill 接口和注册管理机制。
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Type


class SkillCategory(str, Enum):
    """Skill 类别枚举"""
    CODE = "code"  # 代码相关
    SECURITY = "security"  # 安全相关
    FORMATTING = "formatting"  # 格式化相关
    ANALYSIS = "analysis"  # 分析相关
    UTILITY = "utility"  # 工具类
    CUSTOM = "custom"  # 自定义


class SkillStatus(str, Enum):
    """Skill 状态枚举"""
    READY = "ready"  # 就绪
    RUNNING = "running"  # 运行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    DISABLED = "disabled"  # 已禁用


@dataclass
class SkillContext:
    """
    Skill 执行上下文

    Attributes:
        skill_id: Skill ID
        input_data: 输入数据
        metadata: 附加元数据（如项目路径、文件列表等）
        timeout: 超时时间（秒）
    """
    skill_id: str
    input_data: Any
    metadata: dict[str, Any] = field(default_factory=dict)
    timeout: int = 300  # 默认 5 分钟超时


@dataclass
class SkillResult:
    """
    Skill 执行结果

    Attributes:
        success: 是否成功
        output: 输出数据
        error: 错误信息
        metadata: 附加元数据（执行时间、资源使用等）
    """
    success: bool
    output: Any = None
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if "execution_time" not in self.metadata:
            self.metadata["execution_time"] = 0.0


@dataclass
class SkillInfo:
    """
    Skill 元信息

    Attributes:
        skill_id: Skill 唯一标识
        name: Skill 名称
        description: Skill 描述
        category: Skill 类别
        version: 版本号
        author: 作者
        tags: 标签列表
        input_schema: 输入数据 schema 描述
        output_schema: 输出数据 schema 描述
    """
    skill_id: str
    name: str
    description: str
    category: SkillCategory
    version: str = "1.0.0"
    author: str = ""
    tags: list[str] = field(default_factory=list)
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)


class Skill(ABC):
    """
    Skill 基类

    所有 Skill 实现必须继承此类并实现核心抽象方法。

    生命周期:
    1. initialize() - 初始化
    2. execute() - 执行
    3. cleanup() - 清理

    使用示例:
        class CodeAnalysisSkill(Skill):
            def get_info(self) -> SkillInfo:
                return SkillInfo(
                    skill_id="code_analysis",
                    name="Code Analysis",
                    description="Analyze code quality and structure",
                    category=SkillCategory.CODE,
                )

            async def execute(self, context: SkillContext) -> SkillResult:
                # 实现代码分析逻辑
                return SkillResult(success=True, output={...})
    """

    def __init__(self):
        self._status = SkillStatus.READY
        self._initialized = False
        self._last_executed: Optional[datetime] = None
        self._execution_count = 0

    @abstractmethod
    def get_info(self) -> SkillInfo:
        """
        获取 Skill 元信息（子类必须实现）

        Returns:
            Skill 元信息
        """
        pass

    @abstractmethod
    async def execute(self, context: SkillContext) -> SkillResult:
        """
        执行 Skill（子类必须实现）

        Args:
            context: Skill 执行上下文

        Returns:
            Skill 执行结果
        """
        pass

    def initialize(self) -> bool:
        """
        初始化 Skill

        子类可以重写此方法进行资源初始化。

        Returns:
            是否初始化成功
        """
        self._initialized = True
        self._status = SkillStatus.READY
        return True

    def cleanup(self) -> None:
        """
        清理 Skill 资源

        子类可以重写此方法释放资源。
        """
        self._initialized = False
        self._status = SkillStatus.READY

    def validate_input(self, context: SkillContext) -> tuple[bool, Optional[str]]:
        """
        验证输入数据

        子类可以重写此方法进行输入验证。

        Args:
            context: Skill 执行上下文

        Returns:
            (是否有效，错误信息)
        """
        return True, None

    @property
    def status(self) -> SkillStatus:
        """获取 Skill 状态"""
        return self._status

    @property
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized

    @property
    def is_ready(self) -> bool:
        """检查是否就绪"""
        return self._status == SkillStatus.READY

    @property
    def last_executed(self) -> Optional[datetime]:
        """获取最后执行时间"""
        return self._last_executed

    @property
    def execution_count(self) -> int:
        """获取执行次数"""
        return self._execution_count

    def _before_execute(self) -> None:
        """执行前回调"""
        self._status = SkillStatus.RUNNING

    def _after_execute(self, result: SkillResult) -> None:
        """
        执行后回调

        Args:
            result: 执行结果
        """
        self._last_executed = datetime.utcnow()
        self._execution_count += 1
        self._status = SkillStatus.COMPLETED if result.success else SkillStatus.FAILED

    def __repr__(self) -> str:
        info = self.get_info()
        return f"<Skill {info.skill_id} v{info.version}>"


class SkillRegistry:
    """
    Skill 注册表

    管理 Skill 的注册、查找和生命周期。支持按 ID、类别、标签查找。

    使用示例:
        registry = SkillRegistry()
        registry.register(CodeAnalysisSkill())
        skill = registry.get("code_analysis")
        skills = registry.get_by_category(SkillCategory.CODE)
    """

    def __init__(self):
        self._skills: dict[str, Skill] = {}
        self._disabled: set[str] = set()

    def register(self, skill: Skill) -> bool:
        """
        注册 Skill

        Args:
            skill: Skill 实例

        Returns:
            是否注册成功
        """
        info = skill.get_info()
        skill_id = info.skill_id

        if skill_id in self._skills:
            return False

        # 初始化 Skill
        if not skill.initialize():
            return False

        self._skills[skill_id] = skill
        return True

    def unregister(self, skill_id: str) -> bool:
        """
        注销 Skill

        Args:
            skill_id: Skill ID

        Returns:
            是否注销成功
        """
        if skill_id not in self._skills:
            return False

        skill = self._skills[skill_id]
        skill.cleanup()
        del self._skills[skill_id]
        self._disabled.discard(skill_id)
        return True

    def get(self, skill_id: str) -> Optional[Skill]:
        """
        获取 Skill 实例

        Args:
            skill_id: Skill ID

        Returns:
            Skill 实例，不存在则返回 None
        """
        return self._skills.get(skill_id)

    def get_or_raise(self, skill_id: str) -> Skill:
        """
        获取 Skill 实例（不存在则抛出异常）

        Args:
            skill_id: Skill ID

        Returns:
            Skill 实例

        Raises:
            KeyError: Skill 不存在
        """
        if skill_id not in self._skills:
            raise KeyError(f"Skill not found: {skill_id}")
        return self._skills[skill_id]

    def get_all(self) -> list[Skill]:
        """获取所有已注册的 Skill"""
        return list(self._skills.values())

    def get_info_all(self) -> list[SkillInfo]:
        """获取所有 Skill 的元信息"""
        return [skill.get_info() for skill in self._skills.values()]

    def get_by_category(self, category: SkillCategory) -> list[Skill]:
        """
        按类别获取 Skill 列表

        Args:
            category: Skill 类别

        Returns:
            Skill 列表
        """
        return [
            skill for skill in self._skills.values()
            if skill.get_info().category == category
        ]

    def get_by_tag(self, tag: str) -> list[Skill]:
        """
        按标签获取 Skill 列表

        Args:
            tag: 标签

        Returns:
            Skill 列表
        """
        return [
            skill for skill in self._skills.values()
            if tag in skill.get_info().tags
        ]

    def search(self, query: str) -> list[Skill]:
        """
        搜索 Skill

        在名称、描述、标签中搜索。

        Args:
            query: 搜索关键词

        Returns:
            匹配的 Skill 列表
        """
        query_lower = query.lower()
        results = []
        for skill in self._skills.values():
            info = skill.get_info()
            if (query_lower in info.name.lower() or
                query_lower in info.description.lower() or
                any(query_lower in tag.lower() for tag in info.tags)):
                results.append(skill)
        return results

    def enable(self, skill_id: str) -> bool:
        """启用 Skill"""
        if skill_id in self._disabled:
            self._disabled.discard(skill_id)
            return True
        return skill_id in self._skills

    def disable(self, skill_id: str) -> bool:
        """禁用 Skill"""
        if skill_id in self._skills:
            self._disabled.add(skill_id)
            return True
        return False

    def is_enabled(self, skill_id: str) -> bool:
        """检查 Skill 是否启用"""
        return skill_id in self._skills and skill_id not in self._disabled

    def is_registered(self, skill_id: str) -> bool:
        """检查 Skill 是否已注册"""
        return skill_id in self._skills

    def count(self) -> int:
        """获取已注册 Skill 数量"""
        return len(self._skills)

    def clear(self) -> None:
        """清空所有注册"""
        for skill in self._skills.values():
            skill.cleanup()
        self._skills.clear()
        self._disabled.clear()


# 全局注册表实例
_registry: Optional[SkillRegistry] = None


def get_registry() -> SkillRegistry:
    """获取全局 Skill 注册表实例"""
    global _registry
    if _registry is None:
        _registry = SkillRegistry()
    return _registry


def reset_registry() -> None:
    """重置全局注册表（用于测试）"""
    global _registry
    if _registry is not None:
        _registry.clear()
    _registry = None


def register_skill(skill: Skill) -> bool:
    """便捷函数：注册 Skill 到全局注册表"""
    return get_registry().register(skill)


def get_skill(skill_id: str) -> Optional[Skill]:
    """便捷函数：从全局注册表获取 Skill"""
    return get_registry().get(skill_id)
