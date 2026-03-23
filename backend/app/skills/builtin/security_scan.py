"""
安全扫描 Skill

扫描代码中的安全漏洞和潜在风险。
"""
import ast
import re
from pathlib import Path
from typing import Any, Optional

from ..base import Skill, SkillCategory, SkillContext, SkillResult, SkillInfo


class SecurityScanSkill(Skill):
    """
    安全扫描 Skill

    功能:
    - 检测硬编码敏感信息（密码、密钥、Token）
    - 检测 SQL 注入风险
    - 检测命令注入风险
    - 检测不安全的文件操作
    - 检测不安全的网络请求
    """

    def __init__(self):
        super().__init__()
        # 敏感关键词模式
        self._sensitive_patterns = [
            (r"(?i)(password|passwd|pwd)\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password"),
            (r"(?i)(api_key|apikey|api-key)\s*=\s*['\"][^'\"]+['\"]", "Hardcoded API key"),
            (r"(?i)(secret|secret_key)\s*=\s*['\"][^'\"]+['\"]", "Hardcoded secret"),
            (r"(?i)(token|auth_token|access_token)\s*=\s*['\"][^'\"]+['\"]", "Hardcoded token"),
            (r"(?i)(private_key)\s*=\s*['\"][^'\"]+['\"]", "Hardcoded private key"),
            (r"(?i)(aws_access_key_id|aws_secret_access_key)\s*=\s*['\"][^'\"]+['\"]", "Hardcoded AWS credentials"),
        ]
        
        # 危险函数
        self._dangerous_functions = {
            "eval": "Use of eval() is dangerous and can lead to code injection",
            "exec": "Use of exec() is dangerous and can lead to code injection",
            "compile": "Use of compile() with dynamic code can be dangerous",
            "__import__": "Dynamic import can be dangerous if used with user input",
        }

    def get_info(self) -> SkillInfo:
        return SkillInfo(
            skill_id="security_scan",
            name="Security Scan",
            description="扫描代码中的安全漏洞和潜在风险",
            category=SkillCategory.SECURITY,
            version="1.0.0",
            author="WorkAgent",
            tags=["security", "scan", "vulnerability", "audit"],
            input_schema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "代码内容"},
                    "file_path": {"type": "string", "description": "文件路径"},
                    "scan_type": {
                        "type": "string",
                        "enum": ["all", "secrets", "injection", "unsafe_ops"],
                    },
                    "severity_threshold": {
                        "type": "string",
                        "enum": ["critical", "high", "medium", "low", "info"],
                    },
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "vulnerabilities": {"type": "array", "description": "发现的安全漏洞"},
                    "risk_score": {"type": "number", "description": "风险评分 (0-100)"},
                    "summary": {"type": "object", "description": "扫描摘要"},
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
            scan_type = data.get("scan_type", "all")
            severity_threshold = data.get("severity_threshold", "info")
            
            # 获取代码内容
            code = data.get("code")
            if not code and "file_path" in data:
                code = self._read_file(data["file_path"])
            
            if not code:
                return SkillResult(
                    success=False,
                    error="No code to scan",
                )

            vulnerabilities = []

            # 执行扫描
            if scan_type in ["secrets", "all"]:
                vulnerabilities.extend(self._scan_secrets(code))

            if scan_type in ["injection", "all"]:
                vulnerabilities.extend(self._scan_injection(code))

            if scan_type in ["unsafe_ops", "all"]:
                vulnerabilities.extend(self._scan_unsafe_operations(code))

            # 过滤严重程度
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
            threshold_level = severity_order.get(severity_threshold, 4)
            filtered_vulns = [
                v for v in vulnerabilities
                if severity_order.get(v.get("severity", "info"), 4) <= threshold_level
            ]

            # 计算风险评分
            risk_score = self._calculate_risk_score(filtered_vulns)

            execution_time = time.time() - start_time

            return SkillResult(
                success=True,
                output={
                    "vulnerabilities": filtered_vulns,
                    "risk_score": risk_score,
                    "summary": {
                        "total_issues": len(filtered_vulns),
                        "critical": sum(1 for v in filtered_vulns if v.get("severity") == "critical"),
                        "high": sum(1 for v in filtered_vulns if v.get("severity") == "high"),
                        "medium": sum(1 for v in filtered_vulns if v.get("severity") == "medium"),
                        "low": sum(1 for v in filtered_vulns if v.get("severity") == "low"),
                        "info": sum(1 for v in filtered_vulns if v.get("severity") == "info"),
                    },
                },
                metadata={
                    "execution_time": execution_time,
                    "scan_type": scan_type,
                    "code_length": len(code),
                },
            )

        except Exception as e:
            return SkillResult(
                success=False,
                error=f"Security scan failed: {str(e)}",
            )

    def _read_file(self, file_path: str) -> str:
        """读取文件内容"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return path.read_text(encoding="utf-8")

    def _scan_secrets(self, code: str) -> list[dict[str, Any]]:
        """扫描硬编码的敏感信息"""
        vulnerabilities = []
        lines = code.splitlines()

        for pattern, description in self._sensitive_patterns:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    # 检查是否在注释中
                    code_part = line.split("#")[0] if "#" in line else line
                    if re.search(pattern, code_part):
                        vulnerabilities.append({
                            "type": "hardcoded_secret",
                            "severity": "critical",
                            "description": description,
                            "line": i,
                            "code": line.strip()[:100],
                            "recommendation": "Use environment variables or secure secret management",
                        })

        return vulnerabilities

    def _scan_injection(self, code: str) -> list[dict[str, Any]]:
        """扫描注入风险"""
        vulnerabilities = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return vulnerabilities

        # 检查危险函数调用
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # 检查 eval/exec 等危险函数
                if isinstance(node.func, ast.Name) and node.func.id in self._dangerous_functions:
                    vulnerabilities.append({
                        "type": "code_injection",
                        "severity": "critical",
                        "description": self._dangerous_functions[node.func.id],
                        "line": node.lineno,
                        "recommendation": "Avoid using dynamic code execution. Use safer alternatives.",
                    })

                # 检查 SQL 拼接
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ["execute", "executemany"]:
                        # 检查是否有字符串格式化
                        if node.args and self._has_string_formatting(node.args[0]):
                            vulnerabilities.append({
                                "type": "sql_injection",
                                "severity": "critical",
                                "description": "Potential SQL injection - using string formatting in query",
                                "line": node.lineno,
                                "recommendation": "Use parameterized queries instead of string formatting",
                            })

        # 检查 subprocess 使用
        dangerous_subprocess = ["shell=True", "os.system", "os.popen"]
        for i, line in enumerate(code.splitlines(), 1):
            for pattern in dangerous_subprocess:
                if pattern in line:
                    vulnerabilities.append({
                        "type": "command_injection",
                        "severity": "high",
                        "description": f"Potentially unsafe command execution: {pattern}",
                        "line": i,
                        "code": line.strip()[:100],
                        "recommendation": "Avoid shell=True and use subprocess with list arguments",
                    })

        return vulnerabilities

    def _scan_unsafe_operations(self, code: str) -> list[dict[str, Any]]:
        """扫描不安全的操作"""
        vulnerabilities = []
        lines = code.splitlines()

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return vulnerabilities

        # 检查不安全的文件操作
        unsafe_file_patterns = [
            (r"open\([^)]*\+[^)]*\)", "Path traversal risk - dynamic file path concatenation"),
            (r"os\.remove\([^)]*\+[^)]*\)", "Path traversal risk - dynamic file deletion"),
        ]

        for i, line in enumerate(lines, 1):
            for pattern, description in unsafe_file_patterns:
                if re.search(pattern, line):
                    vulnerabilities.append({
                        "type": "unsafe_file_operation",
                        "severity": "high",
                        "description": description,
                        "line": i,
                        "recommendation": "Validate and sanitize file paths, use pathlib for safe path handling",
                    })

        # 检查不安全的网络请求
        insecure_requests = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    # 检查 verify=False
                    if node.func.attr in ["get", "post", "put", "delete", "request"]:
                        for keyword in node.keywords:
                            if keyword.arg == "verify" and isinstance(keyword.value, ast.Constant) and keyword.value.value is False:
                                insecure_requests.append(node.lineno)

        for line in insecure_requests:
            vulnerabilities.append({
                "type": "insecure_request",
                "severity": "high",
                "description": "SSL certificate verification disabled",
                "line": line,
                "recommendation": "Enable SSL verification (verify=True) for secure connections",
            })

        # 检查 pickle 使用
        for i, line in enumerate(lines, 1):
            if "pickle.load" in line or "pickle.loads" in line:
                vulnerabilities.append({
                    "type": "unsafe_deserialization",
                    "severity": "high",
                    "description": "Use of pickle with untrusted data can lead to code execution",
                    "line": i,
                    "recommendation": "Avoid pickle for untrusted data. Use JSON or other safe formats.",
                })

        # 检查弱加密
        weak_crypto = ["md5", "sha1", "des"]
        for i, line in enumerate(lines, 1):
            for algo in weak_crypto:
                if algo in line.lower() and ("hash" in line.lower() or "encrypt" in line.lower()):
                    vulnerabilities.append({
                        "type": "weak_cryptography",
                        "severity": "medium",
                        "description": f"Use of weak cryptographic algorithm: {algo.upper()}",
                        "line": i,
                        "recommendation": "Use strong algorithms like SHA-256, SHA-3, or AES-256",
                    })

        return vulnerabilities

    def _has_string_formatting(self, node: ast.AST) -> bool:
        """检查节点是否包含字符串格式化"""
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Mod, ast.Add)):
            return True
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "format":
                return True
            if isinstance(node.func, ast.Name) and node.func.id == "format":
                return True
        if isinstance(node, ast.JoinedStr):  # f-string
            return True
        return False

    def _calculate_risk_score(self, vulnerabilities: list[dict]) -> float:
        """
        计算风险评分

        基于漏洞数量和严重程度计算 0-100 的评分。
        """
        if not vulnerabilities:
            return 0.0

        severity_weights = {
            "critical": 25,
            "high": 15,
            "medium": 8,
            "low": 3,
            "info": 1,
        }

        total_score = 0
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "info")
            total_score += severity_weights.get(severity, 1)

        # 限制最高 100 分
        return min(100.0, float(total_score))
