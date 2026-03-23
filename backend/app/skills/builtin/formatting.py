"""
代码格式化 Skill

格式化代码以符合风格指南。
"""
import re
from pathlib import Path
from typing import Any, Optional

from ..base import Skill, SkillCategory, SkillContext, SkillResult, SkillInfo


class FormattingSkill(Skill):
    """
    代码格式化 Skill

    功能:
    - Python 代码格式化（PEP 8）
    - 缩进标准化
    - 空白行规范化
    - 导入排序
    - 行长度调整
    """

    def __init__(self):
        super().__init__()
        self._default_max_line_length = 120
        self._default_indent_size = 4

    def get_info(self) -> SkillInfo:
        return SkillInfo(
            skill_id="formatting",
            name="Code Formatting",
            description="格式化代码以符合风格指南",
            category=SkillCategory.FORMATTING,
            version="1.0.0",
            author="WorkAgent",
            tags=["formatting", "style", "pep8", "cleanup"],
            input_schema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "代码内容"},
                    "file_path": {"type": "string", "description": "文件路径"},
                    "language": {
                        "type": "string",
                        "enum": ["python", "javascript", "typescript"],
                    },
                    "options": {
                        "type": "object",
                        "properties": {
                            "max_line_length": {"type": "number"},
                            "indent_size": {"type": "number"},
                            "sort_imports": {"type": "boolean"},
                        },
                    },
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "formatted_code": {"type": "string", "description": "格式化后的代码"},
                    "changes": {"type": "array", "description": "所做的更改列表"},
                    "stats": {"type": "object", "description": "格式化统计"},
                },
            },
        )

    def validate_input(self, context: SkillContext) -> tuple[bool, Optional[str]]:
        if not context.input_data:
            return False, "Input data is required"
        
        data = context.input_data
        if not isinstance(data, dict):
            return False, "Input data must be a dictionary"
        
        has_code = "code" in data
        has_file = "file_path" in data
        
        if not has_code and not has_file:
            return False, "Either 'code' or 'file_path' must be provided"
        
        return True, None

    async def execute(self, context: SkillContext) -> SkillResult:
        import time
        start_time = time.time()
        
        try:
            data = context.input_data
            language = data.get("language", "python")
            options = data.get("options", {})
            
            # 获取代码内容
            code = data.get("code")
            if not code and "file_path" in data:
                code = self._read_file(data["file_path"])
            
            if not code:
                return SkillResult(
                    success=False,
                    error="No code to format",
                )

            # 根据语言选择格式化器
            if language == "python":
                formatted_code, changes = self._format_python(code, options)
            elif language in ["javascript", "typescript"]:
                formatted_code, changes = self._format_javascript(code, options)
            else:
                return SkillResult(
                    success=False,
                    error=f"Unsupported language: {language}",
                )

            # 计算统计
            original_lines = len(code.splitlines())
            formatted_lines = len(formatted_code.splitlines())
            
            stats = {
                "original_lines": original_lines,
                "formatted_lines": formatted_lines,
                "lines_changed": abs(formatted_lines - original_lines),
                "changes_count": len(changes),
            }

            execution_time = time.time() - start_time

            return SkillResult(
                success=True,
                output={
                    "formatted_code": formatted_code,
                    "changes": changes,
                    "stats": stats,
                },
                metadata={
                    "execution_time": execution_time,
                    "language": language,
                    "original_length": len(code),
                    "formatted_length": len(formatted_code),
                },
            )

        except Exception as e:
            return SkillResult(
                success=False,
                error=f"Formatting failed: {str(e)}",
            )

    def _read_file(self, file_path: str) -> str:
        """读取文件内容"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return path.read_text(encoding="utf-8")

    def _format_python(self, code: str, options: dict) -> tuple[str, list[str]]:
        """
        格式化 Python 代码

        遵循 PEP 8 风格指南。
        """
        changes = []
        max_line_length = options.get("max_line_length", self._default_max_line_length)
        indent_size = options.get("indent_size", self._default_indent_size)
        sort_imports = options.get("sort_imports", True)

        lines = code.splitlines()

        # 1. 标准化缩进（制表符转空格）
        new_lines = []
        for i, line in enumerate(lines, 1):
            original = line
            # 制表符转空格
            line = line.replace("\t", " " * indent_size)
            if line != original:
                changes.append(f"Line {i}: Converted tabs to spaces")
            new_lines.append(line)
        lines = new_lines

        # 2. 去除行尾空格
        new_lines = []
        for i, line in enumerate(lines, 1):
            original = line
            line = line.rstrip()
            if line != original:
                changes.append(f"Line {i}: Removed trailing whitespace")
            new_lines.append(line)
        lines = new_lines

        # 3. 规范化空白行
        lines = self._normalize_blank_lines(lines, changes)

        # 4. 排序导入
        if sort_imports:
            lines, import_changes = self._sort_imports(lines)
            changes.extend(import_changes)

        # 5. 检查超长行
        for i, line in enumerate(lines, 1):
            if len(line) > max_line_length:
                changes.append(f"Line {i}: Exceeds max length ({len(line)} > {max_line_length})")

        # 6. 确保文件末尾有换行
        formatted_code = "\n".join(lines)
        if not formatted_code.endswith("\n"):
            formatted_code += "\n"
            changes.append("Added newline at end of file")

        return formatted_code, changes

    def _normalize_blank_lines(self, lines: list[str], changes: list[str]) -> list[str]:
        """规范化空白行"""
        result = []
        consecutive_blank = 0
        last_code_line = -1

        for i, line in enumerate(lines):
            if not line.strip():
                consecutive_blank += 1
                if consecutive_blank > 2:
                    changes.append(f"Line {i + 1}: Removed extra blank line")
                    continue
            else:
                # 在顶级定义之间确保有 2 个空白行
                if last_code_line >= 0 and consecutive_blank == 0:
                    # 检查是否是类或函数定义
                    stripped = line.strip()
                    if stripped.startswith(("def ", "class ", "async def ")):
                        prev_stripped = lines[last_code_line].strip() if last_code_line >= 0 else ""
                        if not prev_stripped.startswith(("def ", "class ", "async def ", "@", "#")):
                            # 在顶级定义前添加空行
                            result.append("")
                            changes.append(f"Line {i + 1}: Added blank line before definition")

                consecutive_blank = 0
                last_code_line = len(result)

            result.append(line)

        # 移除开头的多余空白行
        while result and not result[0].strip():
            result.pop(0)
            if changes:
                changes[0] = changes[0].replace("Line 1", "Line 1")  # 保持第一条变更

        return result

    def _sort_imports(self, lines: list[str]) -> tuple[list[str], list[str]]:
        """排序导入语句"""
        changes = []
        
        import_lines = []
        other_lines = []
        in_import_block = False
        import_start_line = None

        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 检测导入语句
            is_import = (
                stripped.startswith("import ") or
                stripped.startswith("from ")
            )
            
            if is_import:
                if not in_import_block:
                    import_start_line = i
                    in_import_block = True
                import_lines.append((i, line))
            else:
                if in_import_block and import_lines:
                    # 导入块结束，排序并添加
                    sorted_imports = self._sort_import_statements([line for _, line in import_lines])
                    if sorted_imports != [line for _, line in import_lines]:
                        changes.append(f"Lines {import_start_line + 1}-{i}: Sorted imports")
                    other_lines.extend(sorted_imports)
                    import_lines = []
                    in_import_block = False
                
                other_lines.append(line)

        # 处理末尾的导入
        if import_lines:
            sorted_imports = self._sort_import_statements([line for _, line in import_lines])
            if sorted_imports != [line for _, line in import_lines]:
                changes.append(f"Lines {import_start_line + 1}-{len(lines)}: Sorted imports")
            other_lines.extend(sorted_imports)

        return other_lines, changes

    def _sort_import_statements(self, imports: list[str]) -> list[str]:
        """排序导入语句列表"""
        # 分类：标准库、第三方、本地
        standard_libs = {
            "os", "sys", "json", "re", "ast", "pathlib", "typing", "datetime",
            "asyncio", "collections", "itertools", "functools", "abc", "dataclasses",
            "logging", "unittest", "pytest", "time", "random", "math", "string",
        }

        def get_import_key(import_line: str) -> tuple[int, str]:
            stripped = import_line.strip()
            if stripped.startswith("from "):
                match = re.match(r"from\s+([\w.]+)", stripped)
                if match:
                    module = match.group(1).split(".")[0]
                    if module in standard_libs:
                        return (0, stripped)
                    elif module.startswith("_") or module[0].isupper():
                        return (2, stripped)  # 本地
                    else:
                        return (1, stripped)  # 第三方
            elif stripped.startswith("import "):
                match = re.match(r"import\s+([\w.]+)", stripped)
                if match:
                    module = match.group(1).split(".")[0]
                    if module in standard_libs:
                        return (0, stripped)
                    elif module.startswith("_") or module[0].isupper():
                        return (2, stripped)
                    else:
                        return (1, stripped)
            return (3, stripped)

        return sorted(imports, key=get_import_key)

    def _format_javascript(self, code: str, options: dict) -> tuple[str, list[str]]:
        """
        格式化 JavaScript/TypeScript 代码

        基础格式化实现。
        """
        changes = []
        max_line_length = options.get("max_line_length", self._default_max_line_length)
        indent_size = options.get("indent_size", 2)  # JS 通常用 2 空格

        lines = code.splitlines()

        # 1. 制表符转空格
        new_lines = []
        for i, line in enumerate(lines, 1):
            original = line
            line = line.replace("\t", " " * indent_size)
            if line != original:
                changes.append(f"Line {i}: Converted tabs to spaces")
            new_lines.append(line)
        lines = new_lines

        # 2. 去除行尾空格
        new_lines = []
        for i, line in enumerate(lines, 1):
            original = line
            line = line.rstrip()
            if line != original:
                changes.append(f"Line {i}: Removed trailing whitespace")
            new_lines.append(line)
        lines = new_lines

        # 3. 检查超长行
        for i, line in enumerate(lines, 1):
            if len(line) > max_line_length:
                changes.append(f"Line {i}: Exceeds max length ({len(line)} > {max_line_length})")

        formatted_code = "\n".join(lines)
        if not formatted_code.endswith("\n"):
            formatted_code += "\n"
            changes.append("Added newline at end of file")

        return formatted_code, changes
