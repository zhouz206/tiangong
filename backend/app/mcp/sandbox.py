"""
MCP 安全沙箱

提供 MCP 服务的安全隔离和权限控制。
"""
import asyncio
import logging
import os
import re
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional, List, Dict, Set, Callable, Awaitable
import time
import functools

from .types import ToolResult, MCPError, MCPErrorCode


logger = logging.getLogger(__name__)


class PermissionLevel(str, Enum):
    """权限级别"""
    NONE = "none"  # 无权限
    READ = "read"  # 只读
    WRITE = "write"  # 读写
    EXECUTE = "execute"  # 执行
    FULL = "full"  # 完全控制


class ResourceType(str, Enum):
    """资源类型"""
    FILE = "file"
    DIRECTORY = "directory"
    DATABASE = "database"
    NETWORK = "network"
    ENVIRONMENT = "environment"
    PROCESS = "process"


@dataclass
class PermissionRule:
    """权限规则"""
    resource_type: ResourceType
    resource_pattern: str  # 支持通配符的正则表达式
    level: PermissionLevel
    description: str = ""
    
    def matches(self, resource: str) -> bool:
        """检查资源是否匹配规则"""
        # 将通配符转换为正则表达式
        pattern = self.resource_pattern.replace("*", ".*").replace("?", ".")
        return bool(re.match(f"^{pattern}$", resource))


@dataclass
class SandboxConfig:
    """沙箱配置"""
    name: str = "default"
    allowed_resources: List[PermissionRule] = field(default_factory=list)
    denied_resources: List[PermissionRule] = field(default_factory=list)
    max_execution_time: float = 30.0  # 最大执行时间（秒）
    max_memory_mb: int = 512  # 最大内存（MB）
    max_disk_usage_mb: int = 1024  # 最大磁盘使用（MB）
    allowed_network_hosts: List[str] = field(default_factory=list)
    denied_network_hosts: List[str] = field(default_factory=list)
    environment_whitelist: List[str] = field(default_factory=list)
    environment_blacklist: List[str] = field(default_factory=list)


@dataclass
class AuditLog:
    """审计日志"""
    timestamp: float
    action: str
    resource: str
    permission_level: PermissionLevel
    allowed: bool
    details: str = ""
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "action": self.action,
            "resource": self.resource,
            "permission_level": self.permission_level.value,
            "allowed": self.allowed,
            "details": self.details,
        }


class PermissionChecker:
    """
    权限检查器
    
    检查资源访问权限。
    """
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self._audit_logs: List[AuditLog] = []
        self._max_logs = 1000
    
    def check_permission(
        self,
        resource_type: ResourceType,
        resource: str,
        required_level: PermissionLevel,
    ) -> tuple[bool, str]:
        """
        检查权限
        
        Args:
            resource_type: 资源类型
            resource: 资源标识
            required_level: 所需权限级别
            
        Returns:
            (是否允许，原因)
        """
        # 首先检查拒绝规则
        for rule in self.config.denied_resources:
            if rule.resource_type == resource_type and rule.matches(resource):
                reason = f"Denied by rule: {rule.description or rule.resource_pattern}"
                self._log_audit(resource, required_level, False, reason)
                return False, reason
        
        # 然后检查允许规则
        for rule in self.config.allowed_resources:
            if rule.resource_type == resource_type and rule.matches(resource):
                if self._check_level(rule.level, required_level):
                    reason = f"Allowed by rule: {rule.description or rule.resource_pattern}"
                    self._log_audit(resource, required_level, True, reason)
                    return True, ""
                else:
                    reason = f"Insufficient permission level: {rule.level.value} < {required_level.value}"
                    self._log_audit(resource, required_level, False, reason)
                    return False, reason
        
        # 默认拒绝
        reason = "No matching permission rule"
        self._log_audit(resource, required_level, False, reason)
        return False, reason
    
    def _check_level(
        self,
        granted: PermissionLevel,
        required: PermissionLevel,
    ) -> bool:
        """检查权限级别是否足够"""
        level_order = {
            PermissionLevel.NONE: 0,
            PermissionLevel.READ: 1,
            PermissionLevel.WRITE: 2,
            PermissionLevel.EXECUTE: 3,
            PermissionLevel.FULL: 4,
        }
        return level_order.get(granted, 0) >= level_order.get(required, 0)
    
    def _log_audit(
        self,
        resource: str,
        level: PermissionLevel,
        allowed: bool,
        details: str,
    ) -> None:
        """记录审计日志"""
        log = AuditLog(
            timestamp=time.time(),
            action="access",
            resource=resource,
            permission_level=level,
            allowed=allowed,
            details=details,
        )
        
        self._audit_logs.append(log)
        
        # 限制日志数量
        if len(self._audit_logs) > self._max_logs:
            self._audit_logs = self._audit_logs[-self._max_logs:]
    
    def get_audit_logs(self, limit: int = 100) -> List[dict]:
        """获取审计日志"""
        return [log.to_dict() for log in self._audit_logs[-limit:]]
    
    def check_network(self, host: str) -> tuple[bool, str]:
        """检查网络访问权限"""
        # 检查拒绝列表
        for pattern in self.config.denied_network_hosts:
            if re.match(f"^{pattern.replace('*', '.*')}$", host):
                return False, f"Host denied: {host}"
        
        # 检查允许列表（如果有配置）
        if self.config.allowed_network_hosts:
            for pattern in self.config.allowed_network_hosts:
                if re.match(f"^{pattern.replace('*', '.*')}$", host):
                    return True, ""
            return False, f"Host not in allowlist: {host}"
        
        return True, ""
    
    def check_environment(self, var_name: str) -> tuple[bool, str]:
        """检查环境变量访问权限"""
        # 检查黑名单
        if var_name in self.config.environment_blacklist:
            return False, f"Environment variable denied: {var_name}"
        
        # 检查白名单（如果有配置）
        if self.config.environment_whitelist:
            if var_name not in self.config.environment_whitelist:
                return False, f"Environment variable not in allowlist: {var_name}"
        
        return True, ""


class SandboxedExecutor:
    """
    沙箱执行器
    
    在受限环境中执行工具调用。
    """
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self.permission_checker = PermissionChecker(config)
        self._temp_dirs: Set[str] = set()
    
    async def execute(
        self,
        tool_name: str,
        handler: Callable[[dict], Awaitable[ToolResult]],
        arguments: dict,
    ) -> ToolResult:
        """
        在沙箱中执行工具
        
        Args:
            tool_name: 工具名称
            handler: 工具处理器
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        start_time = time.time()
        
        try:
            # 创建临时工作目录
            work_dir = await self._create_work_dir()
            
            # 设置执行上下文
            ctx = SandboxContext(
                work_dir=work_dir,
                config=self.config,
                permission_checker=self.permission_checker,
            )
            
            # 执行超时控制
            try:
                result = await asyncio.wait_for(
                    self._execute_with_context(handler, arguments, ctx),
                    timeout=self.config.max_execution_time,
                )
            except asyncio.TimeoutError:
                return ToolResult(
                    is_error=True,
                    error_message=f"Tool execution timeout: {self.config.max_execution_time}s"
                )
            
            return result
            
        except Exception as e:
            logger.exception(f"Sandbox execution error: {tool_name}")
            return ToolResult(
                is_error=True,
                error_message=str(e)
            )
        finally:
            # 清理临时目录
            await self._cleanup_work_dir()
    
    async def _create_work_dir(self) -> str:
        """创建工作目录"""
        loop = asyncio.get_event_loop()
        work_dir = await loop.run_in_executor(
            None,
            tempfile.mkdtemp,
            f"mcp_sandbox_{os.getpid()}_",
        )
        self._temp_dirs.add(work_dir)
        logger.debug(f"Created sandbox work dir: {work_dir}")
        return work_dir
    
    async def _cleanup_work_dir(self) -> None:
        """清理工作目录"""
        loop = asyncio.get_event_loop()
        
        for work_dir in list(self._temp_dirs):
            try:
                import shutil
                await loop.run_in_executor(
                    None,
                    shutil.rmtree,
                    work_dir,
                )
                self._temp_dirs.discard(work_dir)
                logger.debug(f"Cleaned up sandbox work dir: {work_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup work dir {work_dir}: {e}")
    
    async def _execute_with_context(
        self,
        handler: Callable[[dict], Awaitable[ToolResult]],
        arguments: dict,
        ctx: "SandboxContext",
    ) -> ToolResult:
        """在上下文中执行处理器"""
        # 这里可以添加更多的沙箱控制逻辑
        # 例如：限制文件系统访问、网络访问等
        return await handler(arguments)


@dataclass
class SandboxContext:
    """沙箱上下文"""
    work_dir: str
    config: SandboxConfig
    permission_checker: PermissionChecker
    
    def resolve_path(self, path: str) -> str:
        """
        解析路径（确保在沙箱内）
        
        Args:
            path: 输入路径
            
        Returns:
            解析后的绝对路径
        """
        # 如果是相对路径，加入工作目录
        if not os.path.isabs(path):
            path = os.path.join(self.work_dir, path)
        
        # 规范化路径
        path = os.path.normpath(path)
        
        # 检查是否在允许的文件系统范围内
        allowed, reason = self.permission_checker.check_permission(
            ResourceType.FILE,
            path,
            PermissionLevel.READ,
        )
        
        if not allowed:
            raise PermissionError(f"Path access denied: {reason}")
        
        return path
    
    def check_file_access(self, path: str, level: PermissionLevel) -> tuple[bool, str]:
        """检查文件访问权限"""
        return self.permission_checker.check_permission(
            ResourceType.FILE,
            path,
            level,
        )
    
    def check_network_access(self, host: str) -> tuple[bool, str]:
        """检查网络访问权限"""
        return self.permission_checker.check_network(host)
    
    def check_env_access(self, var_name: str) -> tuple[bool, str]:
        """检查环境变量访问权限"""
        return self.permission_checker.check_environment(var_name)


def sandboxed(
    config: Optional[SandboxConfig] = None,
    resource_type: ResourceType = ResourceType.FILE,
    required_level: PermissionLevel = PermissionLevel.READ,
):
    """
    沙箱装饰器
    
    用于标记需要在沙箱中执行的函数。
    
    使用示例:
        @sandboxed(
            resource_type=ResourceType.DATABASE,
            required_level=PermissionLevel.READ
        )
        async def query_database(args: dict) -> ToolResult:
            ...
    """
    def decorator(func: Callable[[dict], Awaitable[ToolResult]]):
        @functools.wraps(func)
        async def wrapper(arguments: dict, **kwargs):
            # 从 kwargs 获取 permission_checker
            checker = kwargs.get("permission_checker")
            
            if checker:
                # 检查资源访问权限
                resource = arguments.get("resource", arguments.get("path", ""))
                allowed, reason = checker.check_permission(
                    resource_type,
                    resource,
                    required_level,
                )
                
                if not allowed:
                    return ToolResult(
                        is_error=True,
                        error_message=f"Permission denied: {reason}"
                    )
            
            return await func(arguments, **kwargs)
        
        return wrapper
    return decorator


class SecurityPolicy:
    """
    安全策略
    
    定义 MCP 服务的安全策略。
    """
    
    @staticmethod
    def default_file_system() -> SandboxConfig:
        """默认文件系统策略"""
        return SandboxConfig(
            name="file-system-default",
            allowed_resources=[
                PermissionRule(
                    resource_type=ResourceType.FILE,
                    resource_pattern="/tmp/*",
                    level=PermissionLevel.FULL,
                    description="Allow full access to /tmp",
                ),
                PermissionRule(
                    resource_type=ResourceType.FILE,
                    resource_pattern="*.txt",
                    level=PermissionLevel.READ,
                    description="Allow read access to .txt files",
                ),
            ],
            denied_resources=[
                PermissionRule(
                    resource_type=ResourceType.FILE,
                    resource_pattern="/etc/*",
                    level=PermissionLevel.NONE,
                    description="Deny access to /etc",
                ),
                PermissionRule(
                    resource_type=ResourceType.FILE,
                    resource_pattern="*/.ssh/*",
                    level=PermissionLevel.NONE,
                    description="Deny access to SSH keys",
                ),
            ],
            max_execution_time=30.0,
        )
    
    @staticmethod
    def default_database() -> SandboxConfig:
        """默认数据库策略"""
        return SandboxConfig(
            name="database-default",
            allowed_resources=[
                PermissionRule(
                    resource_type=ResourceType.DATABASE,
                    resource_pattern="workagent_*",
                    level=PermissionLevel.READ,
                    description="Allow read access to workagent databases",
                ),
            ],
            denied_resources=[
                PermissionRule(
                    resource_type=ResourceType.DATABASE,
                    resource_pattern="*",
                    level=PermissionLevel.WRITE,
                    description="Deny write access by default",
                ),
            ],
            max_execution_time=60.0,
        )
    
    @staticmethod
    def default_http() -> SandboxConfig:
        """默认 HTTP 策略"""
        return SandboxConfig(
            name="http-default",
            allowed_network_hosts=[
                "localhost",
                "127.0.0.1",
                "*.example.com",
            ],
            denied_network_hosts=[
                "10.*",
                "192.168.*",
                "172.16.*",
                "172.17.*",
                "172.18.*",
                "172.19.*",
                "172.2*",
                "172.30.*",
                "172.31.*",
            ],
            max_execution_time=30.0,
        )
    
    @staticmethod
    def restrictive() -> SandboxConfig:
        """严格模式策略（默认拒绝所有）"""
        return SandboxConfig(
            name="restrictive",
            denied_resources=[
                PermissionRule(
                    resource_type=ResourceType.FILE,
                    resource_pattern="*",
                    level=PermissionLevel.NONE,
                    description="Deny all file access",
                ),
            ],
            max_execution_time=10.0,
        )


class SandboxManager:
    """
    沙箱管理器
    
    管理多个沙箱实例。
    """
    
    def __init__(self):
        self._sandboxes: Dict[str, SandboxedExecutor] = {}
        self._policies: Dict[str, SandboxConfig] = {}
    
    def register_policy(self, name: str, config: SandboxConfig) -> None:
        """注册策略"""
        self._policies[name] = config
        self._sandboxes[name] = SandboxedExecutor(config)
        logger.info(f"Registered sandbox policy: {name}")
    
    def get_executor(self, policy_name: str) -> Optional[SandboxedExecutor]:
        """获取执行器"""
        return self._sandboxes.get(policy_name)
    
    def list_policies(self) -> List[str]:
        """列出所有策略"""
        return list(self._policies.keys())
    
    async def execute(
        self,
        policy_name: str,
        tool_name: str,
        handler: Callable[[dict], Awaitable[ToolResult]],
        arguments: dict,
    ) -> ToolResult:
        """
        使用指定策略执行工具
        
        Args:
            policy_name: 策略名称
            tool_name: 工具名称
            handler: 工具处理器
            arguments: 工具参数
            
        Returns:
            执行结果
        """
        executor = self.get_executor(policy_name)
        
        if not executor:
            return ToolResult(
                is_error=True,
                error_message=f"Unknown policy: {policy_name}"
            )
        
        return await executor.execute(tool_name, handler, arguments)
