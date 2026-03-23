"""
代码分析 Skill

分析代码质量、复杂度、代码风格等。
"""
import ast
import os
from pathlib import Path
from typing import Any, Optional

from ..base import Skill, SkillCategory, SkillContext, SkillResult, SkillInfo


class CodeAnalysisSkill(Skill):
    """
    代码分析 Skill

    功能:
    - 代码复杂度分析（圈复杂度）
    - 代码风格检查
    - 代码结构分析
    - 潜在问题检测
    """

    def __init__(self):
        super().__init__()
        self._supported_extensions = {".py", ".js", ".ts", ".java", ".go"}

    def get_info(self) -> SkillInfo:
        return SkillInfo(
            skill_id="code_analysis",
            name="Code Analysis",
            description="分析代码质量、复杂度和潜在问题",
            category=SkillCategory.CODE,
            version="1.0.0",
            author="WorkAgent",
            tags=["code", "analysis", "quality", "complexity"],
            input_schema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "代码内容"},
                    "file_path": {"type": "string", "description": "文件路径"},
                    "analysis_type": {
                        "type": "string",
                        "enum": ["complexity", "style", "structure", "all"],
                    },
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "metrics": {"type": "object", "description": "代码指标"},
                    "issues": {"type": "array", "description": "发现的问题"},
                    "suggestions": {"type": "array", "description": "改进建议"},
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
            analysis_type = data.get("analysis_type", "all")
            
            # 获取代码内容
            code = data.get("code")
            if not code and "file_path" in data:
                code = self._read_file(data["file_path"])
            
            if not code:
                return SkillResult(
                    success=False,
                    error="No code to analyze",
                )

            # 执行分析
            metrics = {}
            issues = []
            suggestions = []

            if analysis_type in ["complexity", "all"]:
                complexity_result = self._analyze_complexity(code)
                metrics.update(complexity_result["metrics"])
                issues.extend(complexity_result["issues"])
                suggestions.extend(complexity_result["suggestions"])

            if analysis_type in ["style", "all"]:
                style_result = self._analyze_style(code)
                metrics.update(style_result["metrics"])
                issues.extend(style_result["issues"])
                suggestions.extend(style_result["suggestions"])

            if analysis_type in ["structure", "all"]:
                structure_result = self._analyze_structure(code)
                metrics.update(structure_result["metrics"])
                issues.extend(structure_result["issues"])
                suggestions.extend(structure_result["suggestions"])

            execution_time = time.time() - start_time

            return SkillResult(
                success=True,
                output={
                    "metrics": metrics,
                    "issues": issues,
                    "suggestions": suggestions,
                },
                metadata={
                    "execution_time": execution_time,
                    "analysis_type": analysis_type,
                    "code_length": len(code),
                },
            )

        except Exception as e:
            return SkillResult(
                success=False,
                error=f"Analysis failed: {str(e)}",
            )

    def _read_file(self, file_path: str) -> str:
        """读取文件内容"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix not in self._supported_extensions:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        
        return path.read_text(encoding="utf-8")

    def _analyze_complexity(self, code: str) -> dict[str, Any]:
        """
        分析代码复杂度

        计算圈复杂度、行数、函数数等指标。
        """
        metrics = {}
        issues = []
        suggestions = []

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                "metrics": {"syntax_error": str(e)},
                "issues": [{"type": "error", "severity": "critical", "message": f"Syntax error: {e}"}],
                "suggestions": [],
            }

        # 基础指标
        lines = code.splitlines()
        metrics["total_lines"] = len(lines)
        metrics["code_lines"] = sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))
        metrics["comment_lines"] = sum(1 for line in lines if line.strip().startswith("#"))
        metrics["blank_lines"] = sum(1 for line in lines if not line.strip())

        # 函数和方法分析
        functions = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        metrics["function_count"] = len(functions)
        metrics["class_count"] = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))

        # 圈复杂度估算
        total_complexity = 0
        high_complexity_funcs = []
        
        for func in functions:
            complexity = self._calculate_function_complexity(func)
            total_complexity += complexity
            
            if complexity > 10:
                high_complexity_funcs.append({
                    "name": func.name,
                    "complexity": complexity,
                    "line": func.lineno,
                })
                issues.append({
                    "type": "complexity",
                    "severity": "warning",
                    "message": f"Function '{func.name}' has high complexity ({complexity})",
                    "line": func.lineno,
                })
                suggestions.append(f"Consider refactoring '{func.name}' to reduce complexity")

        metrics["total_complexity"] = total_complexity
        metrics["average_complexity"] = round(total_complexity / len(functions), 2) if functions else 0

        if high_complexity_funcs:
            metrics["high_complexity_functions"] = high_complexity_funcs

        # 嵌套深度分析
        max_depth = self._calculate_max_nesting_depth(tree)
        metrics["max_nesting_depth"] = max_depth
        
        if max_depth > 4:
            issues.append({
                "type": "nesting",
                "severity": "warning",
                "message": f"Maximum nesting depth is {max_depth}",
            })
            suggestions.append("Reduce nesting depth for better readability")

        return {"metrics": metrics, "issues": issues, "suggestions": suggestions}

    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> int:
        """计算函数的圈复杂度"""
        complexity = 1  # 基础复杂度
        
        for node in ast.walk(func_node):
            # 控制流语句增加复杂度
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                # and/or 操作符
                complexity += len(node.values) - 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1

        return complexity

    def _calculate_max_nesting_depth(self, tree: ast.AST) -> int:
        """计算最大嵌套深度"""
        def get_depth(node, current_depth=0) -> int:
            max_depth = current_depth
            
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                    child_depth = get_depth(child, current_depth + 1)
                    max_depth = max(max_depth, child_depth)
                else:
                    child_depth = get_depth(child, current_depth)
                    max_depth = max(max_depth, child_depth)
            
            return max_depth

        return get_depth(tree)

    def _analyze_style(self, code: str) -> dict[str, Any]:
        """
        分析代码风格

        检查 PEP 8 风格问题。
        """
        metrics = {}
        issues = []
        suggestions = []

        lines = code.splitlines()

        # 检查行长度
        long_lines = []
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                long_lines.append({"line": i, "length": len(line)})
                issues.append({
                    "type": "style",
                    "severity": "info",
                    "message": f"Line {i} exceeds 120 characters ({len(line)} chars)",
                    "line": i,
                })

        metrics["long_lines_count"] = len(long_lines)
        if long_lines:
            metrics["long_lines"] = long_lines
            suggestions.append("Break long lines for better readability")

        # 检查缩进
        inconsistent_indentation = []
        for i, line in enumerate(lines, 1):
            if line and not line.startswith("#"):
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces > 0 and leading_spaces % 4 != 0:
                    inconsistent_indentation.append({"line": i, "spaces": leading_spaces})
                    issues.append({
                        "type": "style",
                        "severity": "warning",
                        "message": f"Line {i} has inconsistent indentation ({leading_spaces} spaces)",
                        "line": i,
                    })

        metrics["indentation_issues"] = len(inconsistent_indentation)
        if inconsistent_indentation:
            suggestions.append("Use 4 spaces for indentation consistently")

        # 检查空白行
        consecutive_blank_lines = 0
        max_consecutive_blank = 0
        for line in lines:
            if not line.strip():
                consecutive_blank_lines += 1
                max_consecutive_blank = max(max_consecutive_blank, consecutive_blank_lines)
            else:
                consecutive_blank_lines = 0

        metrics["max_consecutive_blank_lines"] = max_consecutive_blank
        if max_consecutive_blank > 2:
            issues.append({
                "type": "style",
                "severity": "info",
                "message": f"Found {max_consecutive_blank} consecutive blank lines",
            })
            suggestions.append("Reduce consecutive blank lines to maximum 2")

        return {"metrics": metrics, "issues": issues, "suggestions": suggestions}

    def _analyze_structure(self, code: str) -> dict[str, Any]:
        """
        分析代码结构

        检查导入、类、函数的组织结构。
        """
        metrics = {}
        issues = []
        suggestions = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {"metrics": {}, "issues": [], "suggestions": []}

        # 导入分析
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        metrics["import_count"] = len(imports)

        # 检查导入顺序（标准库、第三方、本地）
        standard_libs = {"os", "sys", "json", "re", "ast", "pathlib", "typing", "datetime", "asyncio"}
        has_mixed_imports = False
        
        for imp in imports:
            if isinstance(imp, ast.ImportFrom) and imp.module:
                module_name = imp.module.split(".")[0]
                if module_name not in standard_libs and module_name.islower():
                    # 可能是第三方或本地导入
                    pass

        # 检查是否有未使用的导入（简单启发式）
        all_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                all_names.add(node.id)

        unused_imports = []
        for imp in imports:
            if isinstance(imp, ast.Import):
                for alias in imp.names:
                    name = alias.asname or alias.name
                    if name not in all_names:
                        unused_imports.append(name)
            elif isinstance(imp, ast.ImportFrom):
                for alias in imp.names:
                    name = alias.asname or alias.name
                    if name not in all_names and name != "*":
                        unused_imports.append(name)

        if unused_imports:
            metrics["unused_imports"] = unused_imports
            issues.append({
                "type": "structure",
                "severity": "warning",
                "message": f"Potentially unused imports: {', '.join(unused_imports[:5])}",
            })
            suggestions.append("Remove unused imports to clean up code")

        # 检查类和方法结构
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        for cls in classes:
            methods = [node for node in cls.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
            
            if len(methods) > 10:
                issues.append({
                    "type": "structure",
                    "severity": "warning",
                    "message": f"Class '{cls.name}' has too many methods ({len(methods)})",
                    "line": cls.lineno,
                })
                suggestions.append(f"Consider splitting class '{cls.name}' into smaller classes")

        return {"metrics": metrics, "issues": issues, "suggestions": suggestions}
