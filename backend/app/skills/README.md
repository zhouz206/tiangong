# Skill 系统

可扩展的 Skill 框架，支持动态加载和执行各种技能。

## 架构

```
skills/
├── base.py          # Skill 基类、注册表
├── loader.py        # Skill 加载器（动态加载）
├── executor.py      # Skill 执行器
├── builtin/         # 内置 Skill
│   ├── code_analysis.py
│   ├── security_scan.py
│   └── formatting.py
└── README.md
```

## 快速开始

### 加载和执行 Skill

```python
from app.skills import (
    load_all_builtin,
    SkillExecutor,
)

# 1. 加载所有内置 Skill
load_all_builtin()

# 2. 创建执行器
executor = SkillExecutor()

# 3. 执行 Skill
result = await executor.execute(
    skill_id="code_analysis",
    input_data={"code": "def hello(): pass"},
    metadata={"project": "my-project"},
)

if result.success:
    print("Output:", result.output)
else:
    print("Error:", result.error)
```

### 便捷函数

```python
from app.skills import execute_skill

result = await execute_skill(
    skill_id="security_scan",
    input_data={"code": "password = 'secret'"},
)
```

## 内置 Skill

### code_analysis - 代码分析

分析代码质量、复杂度和潜在问题。

```python
result = await execute_skill(
    skill_id="code_analysis",
    input_data={
        "code": "def complex():\n    if x:\n        if y:\n            return True",
        "analysis_type": "all",  # complexity | style | structure | all
    },
)

# 输出包含:
# - metrics: 代码指标（行数、函数数、复杂度等）
# - issues: 发现的问题
# - suggestions: 改进建议
```

### security_scan - 安全扫描

扫描代码中的安全漏洞和潜在风险。

```python
result = await execute_skill(
    skill_id="security_scan",
    input_data={
        "code": "password = 'secret'\neval(user_input)",
        "scan_type": "all",  # secrets | injection | unsafe_ops | all
        "severity_threshold": "high",  # critical | high | medium | low | info
    },
)

# 输出包含:
# - vulnerabilities: 安全漏洞列表
# - risk_score: 风险评分 (0-100)
# - summary: 扫描摘要
```

### formatting - 代码格式化

格式化代码以符合风格指南。

```python
result = await execute_skill(
    skill_id="formatting",
    input_data={
        "code": "def hello( ): \n    return 1",
        "language": "python",  # python | javascript | typescript
        "options": {
            "max_line_length": 120,
            "indent_size": 4,
            "sort_imports": True,
        },
    },
)

# 输出包含:
# - formatted_code: 格式化后的代码
# - changes: 所做的更改列表
# - stats: 格式化统计
```

## 自定义 Skill

### 创建 Skill

```python
from app.skills.base import Skill, SkillCategory, SkillContext, SkillResult, SkillInfo

class MyCustomSkill(Skill):
    def get_info(self) -> SkillInfo:
        return SkillInfo(
            skill_id="my_custom_skill",
            name="My Custom Skill",
            description="Does something useful",
            category=SkillCategory.CUSTOM,
            version="1.0.0",
            author="Your Name",
            tags=["custom", "useful"],
        )

    def validate_input(self, context: SkillContext) -> tuple[bool, str]:
        if not context.input_data:
            return False, "Input data is required"
        return True, None

    async def execute(self, context: SkillContext) -> SkillResult:
        # 实现你的逻辑
        data = context.input_data
        
        # 处理...
        
        return SkillResult(
            success=True,
            output={"result": "done"},
            metadata={"processed": True},
        )

# 注册 Skill
from app.skills import register_skill
register_skill(MyCustomSkill())
```

### 从模块加载 Skill

```python
from app.skills import get_loader

loader = get_loader()

# 从 Python 模块加载
skills = loader.load_from_module("my_package.my_skills")

# 从文件加载单个 Skill
skill = loader.load_from_file(
    "/path/to/my_skill.py",
    skill_class_name="MyCustomSkill",
)

# 从目录加载所有 Skill
skills = loader.load_from_directory("/path/to/skills")
```

## API 参考

### Skill 基类

```python
class Skill:
    # 生命周期
    def initialize() -> bool
    def cleanup() -> None
    
    # 执行
    async def execute(context: SkillContext) -> SkillResult
    
    # 验证
    def validate_input(context: SkillContext) -> tuple[bool, str]
    
    # 属性
    @property
    def status() -> SkillStatus
    @property
    def is_initialized() -> bool
    @property
    def is_ready() -> bool
    @property
    def last_executed() -> datetime
    @property
    def execution_count() -> int
```

### SkillRegistry

```python
class SkillRegistry:
    def register(skill: Skill) -> bool
    def unregister(skill_id: str) -> bool
    def get(skill_id: str) -> Optional[Skill]
    def get_all() -> list[Skill]
    def get_by_category(category: SkillCategory) -> list[Skill]
    def get_by_tag(tag: str) -> list[Skill]
    def search(query: str) -> list[Skill]
    def enable(skill_id: str) -> bool
    def disable(skill_id: str) -> bool
    def is_enabled(skill_id: str) -> bool
    def count() -> int
    def clear() -> None
```

### SkillExecutor

```python
class SkillExecutor:
    # 执行
    async def execute(
        skill_id: str,
        input_data: Any,
        metadata: dict = None,
        timeout: int = None,
    ) -> SkillResult
    
    # 批量执行
    async def execute_batch(
        tasks: list[dict],
        max_concurrent: int = None,
    ) -> list[SkillResult]
    
    # 带重试执行
    async def execute_with_retry(
        skill_id: str,
        input_data: Any,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> SkillResult
    
    # 统计
    def get_stats(skill_id: str) -> ExecutionStats
    def get_history(skill_id: str, limit: int = 10) -> list[ExecutionRecord]
    def clear_history(skill_id: str = None) -> None
    def reset_stats(skill_id: str = None) -> None
```

## 错误处理

```python
from app.skills import (
    SkillExecutionError,
    SkillTimeoutError,
    SkillValidationError,
    SkillNotFoundError,
)

try:
    result = await executor.execute(
        skill_id="my_skill",
        input_data={"data": "value"},
        timeout=60,
    )
except SkillTimeoutError as e:
    print("Execution timeout:", e)
except SkillValidationError as e:
    print("Invalid input:", e)
except SkillExecutionError as e:
    print("Execution failed:", e)
```

## 测试

运行 Skill 系统测试：

```bash
cd workagent/backend
python3 -m pytest tests/skills/ -v
```

## 扩展

### 添加新的 Skill 类别

在 `base.py` 的 `SkillCategory` 枚举中添加：

```python
class SkillCategory(str, Enum):
    # ... 现有类别 ...
    MY_CATEGORY = "my_category"
```

### 添加新的 Skill 状态

在 `base.py` 的 `SkillStatus` 枚举中添加：

```python
class SkillStatus(str, Enum):
    # ... 现有状态 ...
    MY_STATUS = "my_status"
```

## 最佳实践

1. **输入验证**: 在 `validate_input()` 中验证所有输入
2. **错误处理**: 返回 `SkillResult(success=False, error="...")` 而不是抛出异常
3. **元数据**: 使用 `metadata` 传递执行时间、资源使用等信息
4. **超时**: 为长时间运行的操作设置合理的超时时间
5. **日志**: 在执行过程中记录关键步骤（使用应用的日志系统）
