"""
文件系统 MCP 服务

提供文件读写、目录操作等功能。
"""
import asyncio
import logging
import os
import shutil
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from ..types import ToolDefinition, ToolResult, ResourceDefinition, ResourceContent
from ..server import MCPServer
from ..sandbox import (
    SandboxConfig,
    SandboxedExecutor,
    PermissionRule,
    PermissionLevel,
    ResourceType,
    SecurityPolicy,
)


logger = logging.getLogger(__name__)


class FileSystemService:
    """
    文件系统 MCP 服务
    
    提供安全的文件操作功能。
    
    使用示例:
        service = FileSystemService(allowed_roots=["/tmp", "/workspace"])
        server = MCPServer()
        service.register(server)
    """
    
    def __init__(
        self,
        allowed_roots: Optional[List[str]] = None,
        max_file_size_mb: int = 10,
        max_read_lines: int = 10000,
    ):
        """
        初始化文件系统服务
        
        Args:
            allowed_roots: 允许访问的根目录列表
            max_file_size_mb: 最大文件大小（MB）
            max_read_lines: 最大读取行数
        """
        self.allowed_roots = allowed_roots or ["/tmp"]
        self.max_file_size_mb = max_file_size_mb
        self.max_read_lines = max_read_lines
        
        # 创建沙箱配置
        self.sandbox_config = self._create_sandbox_config()
        self.executor = SandboxedExecutor(self.sandbox_config)
        
        # 创建 MCP 服务端
        self.server = MCPServer(
            name="file-system",
            version="1.0.0",
            description="File System MCP Service",
        )
        
        # 注册工具
        self._register_tools()
    
    def _create_sandbox_config(self) -> SandboxConfig:
        """创建沙箱配置"""
        allowed_rules = []
        denied_rules = []
        
        # 添加允许的根目录（使用递归通配符）
        for root in self.allowed_roots:
            # 允许根目录本身
            allowed_rules.append(PermissionRule(
                resource_type=ResourceType.FILE,
                resource_pattern=root,
                level=PermissionLevel.FULL,
                description=f"Allow access to {root}",
            ))
            # 允许根目录下的所有文件
            allowed_rules.append(PermissionRule(
                resource_type=ResourceType.FILE,
                resource_pattern=f"{root}/*",
                level=PermissionLevel.FULL,
                description=f"Allow access under {root}",
            ))
        
        # 添加默认拒绝规则
        denied_rules.extend([
            PermissionRule(
                resource_type=ResourceType.FILE,
                resource_pattern="/etc/*",
                level=PermissionLevel.NONE,
                description="Deny /etc access",
            ),
            PermissionRule(
                resource_type=ResourceType.FILE,
                resource_pattern="/root/*",
                level=PermissionLevel.NONE,
                description="Deny /root access",
            ),
            PermissionRule(
                resource_type=ResourceType.FILE,
                resource_pattern="*/.ssh/*",
                level=PermissionLevel.NONE,
                description="Deny SSH keys access",
            ),
            PermissionRule(
                resource_type=ResourceType.FILE,
                resource_pattern="*/.gnupg/*",
                level=PermissionLevel.NONE,
                description="Deny GPG keys access",
            ),
        ])
        
        return SandboxConfig(
            name="file-system",
            allowed_resources=allowed_rules,
            denied_resources=denied_rules,
            max_execution_time=30.0,
        )
    
    def _register_tools(self) -> None:
        """注册工具"""
        
        @self.server.tool(
            name="file_read",
            description="Read contents of a file",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to read"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding (default: utf-8)",
                        "default": "utf-8"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum lines to read",
                        "default": self.max_read_lines
                    }
                },
                "required": ["path"]
            }
        )
        async def file_read(args: dict) -> ToolResult:
            return await self._handle_file_read(args)
        
        @self.server.tool(
            name="file_write",
            description="Write contents to a file",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding (default: utf-8)",
                        "default": "utf-8"
                    },
                    "append": {
                        "type": "boolean",
                        "description": "Append to file instead of overwrite",
                        "default": False
                    }
                },
                "required": ["path", "content"]
            }
        )
        async def file_write(args: dict) -> ToolResult:
            return await self._handle_file_write(args)
        
        @self.server.tool(
            name="file_delete",
            description="Delete a file",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to delete"
                    }
                },
                "required": ["path"]
            }
        )
        async def file_delete(args: dict) -> ToolResult:
            return await self._handle_file_delete(args)
        
        @self.server.tool(
            name="file_exists",
            description="Check if a file exists",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to check"
                    }
                },
                "required": ["path"]
            }
        )
        async def file_exists(args: dict) -> ToolResult:
            return await self._handle_file_exists(args)
        
        @self.server.tool(
            name="file_info",
            description="Get file information (size, modified time, etc.)",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path"
                    }
                },
                "required": ["path"]
            }
        )
        async def file_info(args: dict) -> ToolResult:
            return await self._handle_file_info(args)
        
        @self.server.tool(
            name="list_directory",
            description="List contents of a directory",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "List recursively",
                        "default": False
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern to filter files"
                    }
                },
                "required": ["path"]
            }
        )
        async def list_directory(args: dict) -> ToolResult:
            return await self._handle_list_directory(args)
        
        @self.server.tool(
            name="create_directory",
            description="Create a directory",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to create"
                    },
                    "parents": {
                        "type": "boolean",
                        "description": "Create parent directories if needed",
                        "default": False
                    }
                },
                "required": ["path"]
            }
        )
        async def create_directory(args: dict) -> ToolResult:
            return await self._handle_create_directory(args)
        
        @self.server.tool(
            name="copy_file",
            description="Copy a file",
            input_schema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source file path"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination file path"
                    }
                },
                "required": ["source", "destination"]
            }
        )
        async def copy_file(args: dict) -> ToolResult:
            return await self._handle_copy_file(args)
        
        @self.server.tool(
            name="move_file",
            description="Move or rename a file",
            input_schema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source file path"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination file path"
                    }
                },
                "required": ["source", "destination"]
            }
        )
        async def move_file(args: dict) -> ToolResult:
            return await self._handle_move_file(args)
        
        @self.server.tool(
            name="search_files",
            description="Search for files matching a pattern",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Root directory to search"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern (e.g., '*.py')"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Search recursively",
                        "default": True
                    }
                },
                "required": ["path", "pattern"]
            }
        )
        async def search_files(args: dict) -> ToolResult:
            return await self._handle_search_files(args)
    
    async def _validate_path(self, path: str, level: PermissionLevel = PermissionLevel.READ) -> tuple[bool, str, str]:
        """
        验证路径
        
        Returns:
            (是否有效，规范化的路径，错误信息)
        """
        # 规范化路径
        path = os.path.normpath(os.path.expanduser(path))
        
        # 检查是否在允许的根目录下
        is_allowed = False
        for root in self.allowed_roots:
            root = os.path.normpath(os.path.expanduser(root))
            if path == root or path.startswith(root + os.sep):
                is_allowed = True
                break
        
        if not is_allowed:
            return False, path, f"Path not in allowed roots: {self.allowed_roots}"
        
        # 检查沙箱权限
        allowed, reason = self.executor.permission_checker.check_permission(
            ResourceType.FILE,
            path,
            level,
        )
        
        if not allowed:
            return False, path, reason
        
        return True, path, ""
    
    async def _handle_file_read(self, args: dict) -> ToolResult:
        """处理文件读取"""
        path = args.get("path", "")
        encoding = args.get("encoding", "utf-8")
        limit = args.get("limit", self.max_read_lines)
        
        valid, norm_path, error = await self._validate_path(path)
        if not valid:
            return ToolResult(is_error=True, error_message=error)
        
        try:
            # 检查文件大小
            file_size = os.path.getsize(norm_path)
            max_size = self.max_file_size_mb * 1024 * 1024
            if file_size > max_size:
                return ToolResult(
                    is_error=True,
                    error_message=f"File too large: {file_size} bytes (max: {max_size})"
                )
            
            # 读取文件
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(
                None,
                lambda: Path(norm_path).read_text(encoding=encoding),
            )
            
            # 限制行数
            lines = content.splitlines()
            if len(lines) > limit:
                lines = lines[:limit]
                content = "\n".join(lines)
                content += f"\n... (truncated, showing {limit} of {len(lines)} lines)"
            
            return ToolResult(content=[
                {"type": "text", "text": content}
            ])
            
        except FileNotFoundError:
            return ToolResult(is_error=True, error_message=f"File not found: {norm_path}")
        except PermissionError:
            return ToolResult(is_error=True, error_message=f"Permission denied: {norm_path}")
        except Exception as e:
            return ToolResult(is_error=True, error_message=str(e))
    
    async def _handle_file_write(self, args: dict) -> ToolResult:
        """处理文件写入"""
        path = args.get("path", "")
        content = args.get("content", "")
        encoding = args.get("encoding", "utf-8")
        append = args.get("append", False)
        
        valid, norm_path, error = await self._validate_path(path, PermissionLevel.WRITE)
        if not valid:
            return ToolResult(is_error=True, error_message=error)
        
        try:
            loop = asyncio.get_event_loop()
            
            if append:
                await loop.run_in_executor(
                    None,
                    lambda: Path(norm_path).write_text(
                        (Path(norm_path).read_text() if Path(norm_path).exists() else "") + content,
                        encoding=encoding
                    ),
                )
            else:
                await loop.run_in_executor(
                    None,
                    lambda: Path(norm_path).write_text(content, encoding=encoding),
                )
            
            return ToolResult(content=[
                {"type": "text", "text": f"Successfully wrote {len(content)} bytes to {norm_path}"}
            ])
            
        except PermissionError:
            return ToolResult(is_error=True, error_message=f"Permission denied: {norm_path}")
        except Exception as e:
            return ToolResult(is_error=True, error_message=str(e))
    
    async def _handle_file_delete(self, args: dict) -> ToolResult:
        """处理文件删除"""
        path = args.get("path", "")
        
        valid, norm_path, error = await self._validate_path(path, PermissionLevel.WRITE)
        if not valid:
            return ToolResult(is_error=True, error_message=error)
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: os.remove(norm_path),
            )
            
            return ToolResult(content=[
                {"type": "text", "text": f"Successfully deleted: {norm_path}"}
            ])
            
        except FileNotFoundError:
            return ToolResult(is_error=True, error_message=f"File not found: {norm_path}")
        except PermissionError:
            return ToolResult(is_error=True, error_message=f"Permission denied: {norm_path}")
        except Exception as e:
            return ToolResult(is_error=True, error_message=str(e))
    
    async def _handle_file_exists(self, args: dict) -> ToolResult:
        """处理文件存在检查"""
        path = args.get("path", "")
        
        valid, norm_path, _ = await self._validate_path(path)
        if not valid:
            return ToolResult(content=[
                {"type": "text", "text": "false"}
            ])
        
        exists = os.path.exists(norm_path)
        return ToolResult(content=[
            {"type": "text", "text": "true" if exists else "false"}
        ])
    
    async def _handle_file_info(self, args: dict) -> ToolResult:
        """处理文件信息获取"""
        path = args.get("path", "")
        
        valid, norm_path, error = await self._validate_path(path)
        if not valid:
            return ToolResult(is_error=True, error_message=error)
        
        try:
            stat = os.stat(norm_path)
            info = {
                "path": norm_path,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "is_file": os.path.isfile(norm_path),
                "is_directory": os.path.isdir(norm_path),
                "is_symlink": os.path.islink(norm_path),
            }
            
            import json
            return ToolResult(content=[
                {"type": "text", "text": json.dumps(info, indent=2)}
            ])
            
        except Exception as e:
            return ToolResult(is_error=True, error_message=str(e))
    
    async def _handle_list_directory(self, args: dict) -> ToolResult:
        """处理目录列表"""
        path = args.get("path", "")
        recursive = args.get("recursive", False)
        pattern = args.get("pattern")
        
        valid, norm_path, error = await self._validate_path(path)
        if not valid:
            return ToolResult(is_error=True, error_message=error)
        
        if not os.path.isdir(norm_path):
            return ToolResult(is_error=True, error_message=f"Not a directory: {norm_path}")
        
        try:
            import fnmatch
            
            items = []
            
            if recursive:
                for root, dirs, files in os.walk(norm_path):
                    for name in dirs + files:
                        full_path = os.path.join(root, name)
                        if pattern and not fnmatch.fnmatch(name, pattern):
                            continue
                        items.append({
                            "path": full_path,
                            "name": name,
                            "is_directory": os.path.isdir(full_path),
                        })
            else:
                for name in os.listdir(norm_path):
                    full_path = os.path.join(norm_path, name)
                    if pattern and not fnmatch.fnmatch(name, pattern):
                        continue
                    items.append({
                        "path": full_path,
                        "name": name,
                        "is_directory": os.path.isdir(full_path),
                    })
            
            import json
            return ToolResult(content=[
                {"type": "text", "text": json.dumps(items, indent=2)}
            ])
            
        except PermissionError:
            return ToolResult(is_error=True, error_message=f"Permission denied: {norm_path}")
        except Exception as e:
            return ToolResult(is_error=True, error_message=str(e))
    
    async def _handle_create_directory(self, args: dict) -> ToolResult:
        """处理目录创建"""
        path = args.get("path", "")
        parents = args.get("parents", False)
        
        valid, norm_path, error = await self._validate_path(path, PermissionLevel.WRITE)
        if not valid:
            return ToolResult(is_error=True, error_message=error)
        
        try:
            loop = asyncio.get_event_loop()
            
            if parents:
                await loop.run_in_executor(
                    None,
                    lambda: Path(norm_path).mkdir(parents=True, exist_ok=True),
                )
            else:
                await loop.run_in_executor(
                    None,
                    lambda: os.mkdir(norm_path),
                )
            
            return ToolResult(content=[
                {"type": "text", "text": f"Successfully created directory: {norm_path}"}
            ])
            
        except FileExistsError:
            return ToolResult(is_error=True, error_message=f"Directory already exists: {norm_path}")
        except PermissionError:
            return ToolResult(is_error=True, error_message=f"Permission denied: {norm_path}")
        except Exception as e:
            return ToolResult(is_error=True, error_message=str(e))
    
    async def _handle_copy_file(self, args: dict) -> ToolResult:
        """处理文件复制"""
        source = args.get("source", "")
        destination = args.get("destination", "")
        
        valid, norm_source, error = await self._validate_path(source)
        if not valid:
            return ToolResult(is_error=True, error_message=error)
        
        valid, norm_dest, error = await self._validate_path(destination, PermissionLevel.WRITE)
        if not valid:
            return ToolResult(is_error=True, error_message=error)
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: shutil.copy2(norm_source, norm_dest),
            )
            
            return ToolResult(content=[
                {"type": "text", "text": f"Successfully copied: {norm_source} -> {norm_dest}"}
            ])
            
        except FileNotFoundError:
            return ToolResult(is_error=True, error_message=f"Source not found: {norm_source}")
        except PermissionError:
            return ToolResult(is_error=True, error_message="Permission denied")
        except Exception as e:
            return ToolResult(is_error=True, error_message=str(e))
    
    async def _handle_move_file(self, args: dict) -> ToolResult:
        """处理文件移动"""
        source = args.get("source", "")
        destination = args.get("destination", "")
        
        valid, norm_source, error = await self._validate_path(source, PermissionLevel.WRITE)
        if not valid:
            return ToolResult(is_error=True, error_message=error)
        
        valid, norm_dest, error = await self._validate_path(destination, PermissionLevel.WRITE)
        if not valid:
            return ToolResult(is_error=True, error_message=error)
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: shutil.move(norm_source, norm_dest),
            )
            
            return ToolResult(content=[
                {"type": "text", "text": f"Successfully moved: {norm_source} -> {norm_dest}"}
            ])
            
        except FileNotFoundError:
            return ToolResult(is_error=True, error_message=f"Source not found: {norm_source}")
        except PermissionError:
            return ToolResult(is_error=True, error_message="Permission denied")
        except Exception as e:
            return ToolResult(is_error=True, error_message=str(e))
    
    async def _handle_search_files(self, args: dict) -> ToolResult:
        """处理文件搜索"""
        path = args.get("path", "")
        pattern = args.get("pattern", "")
        recursive = args.get("recursive", True)
        
        valid, norm_path, error = await self._validate_path(path)
        if not valid:
            return ToolResult(is_error=True, error_message=error)
        
        try:
            import fnmatch
            
            matches = []
            
            if recursive:
                for root, dirs, files in os.walk(norm_path):
                    for name in files:
                        if fnmatch.fnmatch(name, pattern):
                            matches.append(os.path.join(root, name))
            else:
                for name in os.listdir(norm_path):
                    if fnmatch.fnmatch(name, pattern):
                        full_path = os.path.join(norm_path, name)
                        if os.path.isfile(full_path):
                            matches.append(full_path)
            
            import json
            return ToolResult(content=[
                {"type": "text", "text": json.dumps(matches, indent=2)}
            ])
            
        except PermissionError:
            return ToolResult(is_error=True, error_message=f"Permission denied: {norm_path}")
        except Exception as e:
            return ToolResult(is_error=True, error_message=str(e))
    
    def register(self, server: Optional[MCPServer] = None) -> MCPServer:
        """
        注册到 MCP 服务端
        
        Args:
            server: 目标服务端，None 则使用内置服务端
            
        Returns:
            MCP 服务端
        """
        if server:
            # 将所有工具注册到目标服务端
            for tool in self.server.list_tools():
                # 找到对应的处理器并重新注册
                pass  # TODO: 实现工具迁移
            return server
        return self.server
    
    def get_server(self) -> MCPServer:
        """获取内置 MCP 服务端"""
        return self.server
    
    def get_tools(self) -> List[ToolDefinition]:
        """获取所有工具定义"""
        return self.server.list_tools()
