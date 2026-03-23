"""
HTTP 客户端 MCP 服务

提供 HTTP 请求功能。
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

import httpx

from ..types import ToolDefinition, ToolResult
from ..server import MCPServer
from ..sandbox import (
    SandboxConfig,
    SandboxedExecutor,
    PermissionRule,
    PermissionLevel,
    ResourceType,
)


logger = logging.getLogger(__name__)


@dataclass
class HTTPRequest:
    """HTTP 请求配置"""
    method: str
    url: str
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, str]] = None
    data: Optional[Dict[str, Any]] = None
    json: Optional[Dict[str, Any]] = None
    timeout: float = 30.0
    follow_redirects: bool = True
    max_redirects: int = 10


class HTTPClientService:
    """
    HTTP 客户端 MCP 服务
    
    提供安全的 HTTP 请求功能。
    
    使用示例:
        service = HTTPClientService(
            allowed_hosts=["api.example.com", "localhost:*"],
            denied_hosts=["internal.*"]
        )
        server = MCPServer()
        service.register(server)
    """
    
    def __init__(
        self,
        allowed_hosts: Optional[List[str]] = None,
        denied_hosts: Optional[List[str]] = None,
        allowed_methods: Optional[List[str]] = None,
        max_response_size_mb: int = 10,
        default_timeout: float = 30.0,
    ):
        """
        初始化 HTTP 客户端服务
        
        Args:
            allowed_hosts: 允许访问的主机列表（支持通配符）
            denied_hosts: 拒绝访问的主机列表
            allowed_methods: 允许的 HTTP 方法
            max_response_size_mb: 最大响应大小（MB）
            default_timeout: 默认超时时间（秒）
        """
        self.allowed_hosts = allowed_hosts or ["*"]
        self.denied_hosts = denied_hosts or []
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        self.max_response_size_mb = max_response_size_mb
        self.default_timeout = default_timeout
        
        # 创建沙箱配置
        self.sandbox_config = self._create_sandbox_config()
        self.executor = SandboxedExecutor(self.sandbox_config)
        
        # 创建 HTTP 客户端
        self._client: Optional[httpx.AsyncClient] = None
        
        # 创建 MCP 服务端
        self.server = MCPServer(
            name="http-client",
            version="1.0.0",
            description="HTTP Client MCP Service",
        )
        
        # 注册工具
        self._register_tools()
    
    def _create_sandbox_config(self) -> SandboxConfig:
        """创建沙箱配置"""
        # 网络访问规则
        allowed_network = self.allowed_hosts.copy()
        denied_network = self.denied_hosts.copy()
        
        # 默认拒绝内网地址（除非明确允许）
        if "*" not in self.allowed_hosts:
            denied_network.extend([
                "10.*",
                "192.168.*",
                "172.16.*",
                "172.17.*",
                "172.18.*",
                "172.19.*",
                "172.2*",
                "172.30.*",
                "172.31.*",
                "127.*",
            ])
        
        return SandboxConfig(
            name="http-client",
            allowed_network_hosts=allowed_network,
            denied_network_hosts=denied_network,
            max_execution_time=self.default_timeout,
        )
    
    def _register_tools(self) -> None:
        """注册工具"""
        
        @self.server.tool(
            name="http_get",
            description="Send an HTTP GET request",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Request URL"
                    },
                    "headers": {
                        "type": "object",
                        "description": "Request headers",
                        "additionalProperties": {"type": "string"}
                    },
                    "params": {
                        "type": "object",
                        "description": "Query parameters",
                        "additionalProperties": {"type": "string"}
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Request timeout in seconds",
                        "default": self.default_timeout
                    },
                    "follow_redirects": {
                        "type": "boolean",
                        "description": "Follow redirects",
                        "default": True
                    }
                },
                "required": ["url"]
            }
        )
        async def http_get(args: dict) -> ToolResult:
            return await self._handle_request("GET", args)
        
        @self.server.tool(
            name="http_post",
            description="Send an HTTP POST request",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Request URL"
                    },
                    "headers": {
                        "type": "object",
                        "description": "Request headers",
                        "additionalProperties": {"type": "string"}
                    },
                    "data": {
                        "type": "object",
                        "description": "Form data"
                    },
                    "json": {
                        "type": "object",
                        "description": "JSON body"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Request timeout in seconds",
                        "default": self.default_timeout
                    },
                    "follow_redirects": {
                        "type": "boolean",
                        "description": "Follow redirects",
                        "default": True
                    }
                },
                "required": ["url"]
            }
        )
        async def http_post(args: dict) -> ToolResult:
            return await self._handle_request("POST", args)
        
        @self.server.tool(
            name="http_put",
            description="Send an HTTP PUT request",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Request URL"
                    },
                    "headers": {
                        "type": "object",
                        "description": "Request headers",
                        "additionalProperties": {"type": "string"}
                    },
                    "data": {
                        "type": "object",
                        "description": "Form data"
                    },
                    "json": {
                        "type": "object",
                        "description": "JSON body"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Request timeout in seconds",
                        "default": self.default_timeout
                    }
                },
                "required": ["url"]
            }
        )
        async def http_put(args: dict) -> ToolResult:
            return await self._handle_request("PUT", args)
        
        @self.server.tool(
            name="http_delete",
            description="Send an HTTP DELETE request",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Request URL"
                    },
                    "headers": {
                        "type": "object",
                        "description": "Request headers",
                        "additionalProperties": {"type": "string"}
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Request timeout in seconds",
                        "default": self.default_timeout
                    }
                },
                "required": ["url"]
            }
        )
        async def http_delete(args: dict) -> ToolResult:
            return await self._handle_request("DELETE", args)
        
        @self.server.tool(
            name="http_patch",
            description="Send an HTTP PATCH request",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Request URL"
                    },
                    "headers": {
                        "type": "object",
                        "description": "Request headers",
                        "additionalProperties": {"type": "string"}
                    },
                    "json": {
                        "type": "object",
                        "description": "JSON body"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Request timeout in seconds",
                        "default": self.default_timeout
                    }
                },
                "required": ["url"]
            }
        )
        async def http_patch(args: dict) -> ToolResult:
            return await self._handle_request("PATCH", args)
        
        @self.server.tool(
            name="http_request",
            description="Send a custom HTTP request",
            input_schema={
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "description": "HTTP method"
                    },
                    "url": {
                        "type": "string",
                        "description": "Request URL"
                    },
                    "headers": {
                        "type": "object",
                        "description": "Request headers",
                        "additionalProperties": {"type": "string"}
                    },
                    "params": {
                        "type": "object",
                        "description": "Query parameters",
                        "additionalProperties": {"type": "string"}
                    },
                    "data": {
                        "type": "object",
                        "description": "Form data"
                    },
                    "json": {
                        "type": "object",
                        "description": "JSON body"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Request timeout in seconds",
                        "default": self.default_timeout
                    },
                    "follow_redirects": {
                        "type": "boolean",
                        "description": "Follow redirects",
                        "default": True
                    }
                },
                "required": ["method", "url"]
            }
        )
        async def http_request(args: dict) -> ToolResult:
            method = args.pop("method", "GET")
            return await self._handle_request(method, args)
    
    def _validate_url(self, url: str) -> tuple[bool, str]:
        """
        验证 URL
        
        Returns:
            (是否有效，错误信息)
        """
        try:
            parsed = httpx.URL(url)
        except Exception as e:
            return False, f"Invalid URL: {str(e)}"
        
        # 检查协议
        if parsed.scheme not in ["http", "https"]:
            return False, f"Unsupported protocol: {parsed.scheme}"
        
        # 检查主机
        host = parsed.host
        
        # 检查拒绝列表
        for pattern in self.denied_hosts:
            import fnmatch
            if fnmatch.fnmatch(host, pattern):
                return False, f"Host denied: {host}"
        
        # 检查允许列表
        if "*" not in self.allowed_hosts:
            allowed = False
            for pattern in self.allowed_hosts:
                import fnmatch
                if fnmatch.fnmatch(host, pattern):
                    allowed = True
                    break
            
            if not allowed:
                return False, f"Host not in allowlist: {host}"
        
        return True, ""
    
    def _validate_method(self, method: str) -> tuple[bool, str]:
        """验证 HTTP 方法"""
        method = method.upper()
        if method not in self.allowed_methods:
            return False, f"Method not allowed: {method}"
        return True, ""
    
    async def _get_client(self) -> httpx.AsyncClient:
        """获取 HTTP 客户端"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                follow_redirects=True,
                timeout=httpx.Timeout(self.default_timeout),
                limits=httpx.Limits(
                    max_keepalive_connections=10,
                    max_connections=50,
                ),
            )
        return self._client
    
    async def _handle_request(self, method: str, args: dict) -> ToolResult:
        """处理 HTTP 请求"""
        url = args.get("url", "")
        headers = args.get("headers")
        params = args.get("params")
        data = args.get("data")
        json_body = args.get("json")
        timeout = args.get("timeout", self.default_timeout)
        follow_redirects = args.get("follow_redirects", True)
        
        # 验证 URL
        valid, error = self._validate_url(url)
        if not valid:
            return ToolResult(is_error=True, error_message=error)
        
        # 验证方法
        valid, error = self._validate_method(method)
        if not valid:
            return ToolResult(is_error=True, error_message=error)
        
        client = None
        try:
            client = await self._get_client()
            
            # 发送请求
            response = await client.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                data=data if data else None,
                json=json_body if json_body else None,
                timeout=timeout,
                follow_redirects=follow_redirects,
            )
            
            # 检查响应大小
            content_length = len(response.content)
            max_size = self.max_response_size_mb * 1024 * 1024
            if content_length > max_size:
                return ToolResult(
                    is_error=True,
                    error_message=f"Response too large: {content_length} bytes (max: {max_size})"
                )
            
            # 构建响应
            result = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "url": str(response.url),
                "elapsed_ms": int(response.elapsed.total_seconds() * 1000),
            }
            
            # 尝试解析 JSON
            try:
                result["body"] = response.json()
                result["content_type"] = "application/json"
            except Exception:
                # 如果不是 JSON，返回文本
                try:
                    result["body"] = response.text
                    result["content_type"] = response.headers.get("content-type", "text/plain")
                except Exception:
                    result["body"] = f"<binary data, {content_length} bytes>"
                    result["content_type"] = "application/octet-stream"
            
            import json
            return ToolResult(content=[
                {"type": "text", "text": json.dumps(result, indent=2, default=str)}
            ])
            
        except httpx.TimeoutException as e:
            return ToolResult(is_error=True, error_message=f"Request timeout: {str(e)}")
        except httpx.ConnectError as e:
            return ToolResult(is_error=True, error_message=f"Connection error: {str(e)}")
        except httpx.HTTPError as e:
            return ToolResult(is_error=True, error_message=f"HTTP error: {str(e)}")
        except Exception as e:
            return ToolResult(is_error=True, error_message=str(e))
    
    async def close(self) -> None:
        """关闭 HTTP 客户端"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    def register(self, server: Optional[MCPServer] = None) -> MCPServer:
        """注册到 MCP 服务端"""
        if server:
            return server
        return self.server
    
    def get_server(self) -> MCPServer:
        """获取内置 MCP 服务端"""
        return self.server
    
    def get_tools(self) -> List[ToolDefinition]:
        """获取所有工具定义"""
        return self.server.list_tools()
