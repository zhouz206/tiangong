"""
Skill 加载器

支持动态加载 Skill 模块，包括内置 Skill 和外部 Skill 包。
"""
import importlib
import importlib.util
import inspect
import os
import sys
from pathlib import Path
from typing import Optional, Type

from .base import Skill, SkillRegistry, get_registry


class SkillLoaderError(Exception):
    """Skill 加载错误基类"""
    pass


class SkillNotFoundError(SkillLoaderError):
    """Skill 未找到"""
    pass


class SkillLoadError(SkillLoaderError):
    """Skill 加载失败"""
    pass


class SkillLoader:
    """
    Skill 加载器

    支持从以下位置加载 Skill:
    1. 内置 Skill 包 (app.skills.builtin)
    2. 外部 Python 模块路径
    3. 外部 Skill 目录

    使用示例:
        loader = SkillLoader()
        
        # 加载内置 Skill
        loader.load_builtin("code_analysis")
        
        # 从模块路径加载
        loader.load_from_module("my_package.my_skills")
        
        # 从目录加载所有 Skill
        loader.load_from_directory("/path/to/skills")
        
        # 加载所有内置 Skill
        loader.load_all_builtin()
    """

    def __init__(self, registry: Optional[SkillRegistry] = None):
        """
        初始化 Skill 加载器

        Args:
            registry: Skill 注册表实例，默认使用全局注册表
        """
        self.registry = registry or get_registry()
        self._builtin_module = "app.skills.builtin"
        self._loaded_modules: set[str] = set()

    def load_builtin(self, skill_name: str) -> Skill:
        """
        加载内置 Skill

        Args:
            skill_name: Skill 名称（对应 builtin 目录下的模块名）

        Returns:
            加载的 Skill 实例

        Raises:
            SkillNotFoundError: Skill 不存在
            SkillLoadError: 加载失败
        """
        module_name = f"{self._builtin_module}.{skill_name}"
        
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as e:
            raise SkillNotFoundError(f"Builtin skill not found: {skill_name}") from e
        except ImportError as e:
            raise SkillLoadError(f"Failed to import builtin skill {skill_name}: {e}") from e

        return self._extract_skill_from_module(module, module_name)

    def load_all_builtin(self) -> list[Skill]:
        """
        加载所有内置 Skill

        自动扫描 builtin 目录下的所有模块并加载。

        Returns:
            加载的 Skill 列表
        """
        builtin_path = self._get_builtin_path()
        if not builtin_path.exists():
            return []

        skills = []
        for file_path in builtin_path.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
            
            skill_name = file_path.stem
            try:
                skill = self.load_builtin(skill_name)
                skills.append(skill)
            except (SkillNotFoundError, SkillLoadError):
                # 跳过无法加载的模块
                continue

        return skills

    def load_from_module(self, module_path: str, skill_class_name: Optional[str] = None) -> list[Skill]:
        """
        从 Python 模块加载 Skill

        Args:
            module_path: 模块路径（如 "my_package.my_skills"）
            skill_class_name: Skill 类名，如果为 None 则自动发现所有 Skill 类

        Returns:
            加载的 Skill 列表

        Raises:
            SkillLoadError: 加载失败
        """
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            raise SkillLoadError(f"Failed to import module {module_path}: {e}") from e

        self._loaded_modules.add(module_path)
        return self._extract_skills_from_module(module, module_path, skill_class_name)

    def load_from_file(self, file_path: str, skill_class_name: Optional[str] = None) -> Skill:
        """
        从 Python 文件加载单个 Skill

        Args:
            file_path: Python 文件路径
            skill_class_name: Skill 类名

        Returns:
            加载的 Skill 实例

        Raises:
            SkillNotFoundError: Skill 类不存在
            SkillLoadError: 加载失败
        """
        path = Path(file_path)
        if not path.exists():
            raise SkillNotFoundError(f"File not found: {file_path}")

        module_name = path.stem
        spec = importlib.util.spec_from_file_location(module_name, path)
        
        if spec is None or spec.loader is None:
            raise SkillLoadError(f"Cannot load module from {file_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            raise SkillLoadError(f"Failed to execute module {file_path}: {e}") from e

        return self._extract_skill_from_module(module, module_name, skill_class_name)

    def load_from_directory(self, directory: str) -> list[Skill]:
        """
        从目录加载所有 Skill

        递归扫描目录下的所有 Python 文件并加载 Skill。

        Args:
            directory: 目录路径

        Returns:
            加载的 Skill 列表
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            return []

        skills = []
        
        # 加载目录下的直接模块
        for file_path in dir_path.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
            
            try:
                skill = self.load_from_file(str(file_path))
                skills.append(skill)
            except (SkillNotFoundError, SkillLoadError):
                continue

        # 递归加载子目录
        for subdir in dir_path.iterdir():
            if subdir.is_dir() and not subdir.name.startswith("_"):
                # 检查是否是 Python 包（有 __init__.py）
                if (subdir / "__init__.py").exists():
                    try:
                        loaded = self.load_from_directory(str(subdir))
                        skills.extend(loaded)
                    except Exception:
                        continue

        return skills

    def reload(self, skill_id: str) -> Optional[Skill]:
        """
        重新加载 Skill

        先卸载再重新加载。

        Args:
            skill_id: Skill ID

        Returns:
            重新加载的 Skill 实例，失败返回 None
        """
        # 先卸载
        self.registry.unregister(skill_id)
        
        # 尝试重新加载
        try:
            return self.load_builtin(skill_id)
        except (SkillNotFoundError, SkillLoadError):
            return None

    def unload(self, skill_id: str) -> bool:
        """
        卸载 Skill

        Args:
            skill_id: Skill ID

        Returns:
            是否卸载成功
        """
        return self.registry.unregister(skill_id)

    def get_loaded_modules(self) -> set[str]:
        """获取已加载的模块列表"""
        return self._loaded_modules.copy()

    def _get_builtin_path(self) -> Path:
        """获取内置 Skill 目录路径"""
        # 查找 builtin 模块的路径
        try:
            module = importlib.import_module(self._builtin_module)
            module_file = getattr(module, "__file__", None)
            if module_file:
                return Path(module_file).parent
        except ImportError:
            pass

        # 回退到相对路径
        base_path = Path(__file__).parent
        return base_path / "builtin"

    def _extract_skill_from_module(
        self,
        module,
        module_name: str,
        class_name: Optional[str] = None,
    ) -> Skill:
        """
        从模块中提取 Skill 实例

        Args:
            module: Python 模块
            module_name: 模块名
            class_name: Skill 类名，如果为 None 则自动发现

        Returns:
            Skill 实例

        Raises:
            SkillNotFoundError: Skill 类不存在
            SkillLoadError: 加载失败
        """
        skill_classes = self._find_skill_classes(module, class_name)

        if not skill_classes:
            if class_name:
                raise SkillNotFoundError(f"Skill class not found: {class_name}")
            else:
                raise SkillNotFoundError(f"No Skill class found in module {module_name}")

        if len(skill_classes) > 1 and not class_name:
            raise SkillLoadError(
                f"Multiple Skill classes found in {module_name}, "
                f"please specify class_name"
            )

        skill_class = skill_classes[0]
        
        try:
            skill = skill_class()
        except Exception as e:
            raise SkillLoadError(f"Failed to instantiate skill: {e}") from e

        # 注册到注册表
        info = skill.get_info()
        if not self.registry.register(skill):
            raise SkillLoadError(f"Failed to register skill: {info.skill_id}")

        return skill

    def _extract_skills_from_module(
        self,
        module,
        module_name: str,
        class_name: Optional[str] = None,
    ) -> list[Skill]:
        """
        从模块中提取所有 Skill 实例

        Args:
            module: Python 模块
            module_name: 模块名
            class_name: 指定的 Skill 类名，如果为 None 则加载所有

        Returns:
            Skill 实例列表
        """
        if class_name:
            try:
                skill = self._extract_skill_from_module(module, module_name, class_name)
                return [skill]
            except (SkillNotFoundError, SkillLoadError):
                return []

        skill_classes = self._find_skill_classes(module)
        skills = []

        for skill_class in skill_classes:
            try:
                skill = skill_class()
                info = skill.get_info()
                if self.registry.register(skill):
                    skills.append(skill)
            except Exception:
                # 跳过无法实例化的 Skill
                continue

        return skills

    def _find_skill_classes(
        self,
        module,
        class_name: Optional[str] = None,
    ) -> list[Type[Skill]]:
        """
        在模块中查找 Skill 类

        Args:
            module: Python 模块
            class_name: 指定的类名，如果为 None 则查找所有

        Returns:
            Skill 类列表
        """
        skill_classes = []

        for name, obj in inspect.getmembers(module, inspect.isclass):
            # 检查是否是 Skill 子类且不是 Skill 基类本身
            if issubclass(obj, Skill) and obj is not Skill:
                # 如果指定了类名，只匹配该类
                if class_name:
                    if name == class_name:
                        skill_classes.append(obj)
                        break
                else:
                    # 检查是否在当前模块定义（排除导入的类）
                    if obj.__module__ == module.__name__:
                        skill_classes.append(obj)

        return skill_classes


# 全局加载器实例
_loader: Optional[SkillLoader] = None


def get_loader() -> SkillLoader:
    """获取全局 Skill 加载器实例"""
    global _loader
    if _loader is None:
        _loader = SkillLoader()
    return _loader


def reset_loader() -> None:
    """重置全局加载器（用于测试）"""
    global _loader
    _loader = None


def load_builtin(skill_name: str) -> Skill:
    """便捷函数：加载内置 Skill"""
    return get_loader().load_builtin(skill_name)


def load_all_builtin() -> list[Skill]:
    """便捷函数：加载所有内置 Skill"""
    return get_loader().load_all_builtin()
