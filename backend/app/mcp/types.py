"""
MCP 类型定义

定义 MCP 协议相关的核心数据类型。
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, List, Callable, Awaitable, Union
import time


class MCPErrorCode(int, Enum):
    """MCP 错误代码"""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR_START = -32000
    SERVER_ERROR_END = -32099


class MCPMethod(str, Enum):
    """MCP 方法枚举"""
    # 初始化
    INITIALIZE = "initialize"
    INITIALIZED = "initialized"
    
    # 工具相关
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    
    # 资源相关
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    
    # 提示相关
    PROMPTS_LIST = "prompts/list"
    PROMPTS_GET = "prompts/get"
    
    # 服务发现
    DISCOVERY_REGISTER = "discovery/register"
    DISCOVERY_UNREGISTER = "discovery/unregister"
    DISCOVERY_LIST = "discovery/list"
    
    # 心跳
    PING = "ping"


@dataclass
class MCPError:
    """MCP 错误"""
    code: MCPErrorCode
    message: str
    data: Optional[Any] = None
    
    def to_dict(self) -> dict:
        return {
            "code": self.code.value,
            "message": self.message,
            "data": self.data
        }


@dataclass
class MCPRequest:
    """MCP 请求"""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Optional[dict] = None
    id: Optional[Union[str, int]] = None
    
    def to_dict(self) -> dict:
        result = {
            "jsonrpc": self.jsonrpc,
            "method": self.method,
        }
        if self.params is not None:
            result["params"] = self.params
        if self.id is not None:
            result["id"] = self.id
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> "MCPRequest":
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            method=data.get("method", ""),
            params=data.get("params"),
            id=data.get("id")
        )


@dataclass
class MCPResponse:
    """MCP 响应"""
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[MCPError] = None
    id: Optional[Union[str, int]] = None
    
    def to_dict(self) -> dict:
        result = {
            "jsonrpc": self.jsonrpc,
            "id": self.id,
        }
        if self.error is not None:
            result["error"] = self.error.to_dict()
        else:
            result["result"] = self.result
        return result


@dataclass
class ToolDefinition:
    """工具定义"""
    name: str
    description: str
    input_schema: dict = field(default_factory=dict)
    annotations: Optional[dict] = None
    
    def to_dict(self) -> dict:
        result = {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }
        if self.annotations:
            result["annotations"] = self.annotations
        return result


@dataclass
class ToolCall:
    """工具调用"""
    name: str
    arguments: dict = field(default_factory=dict)


@dataclass
class ToolResult:
    """工具调用结果"""
    content: List[dict] = field(default_factory=list)
    is_error: bool = False
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        if self.is_error:
            return {
                "isError": True,
                "errorMessage": self.error_message
            }
        return {"content": self.content}


@dataclass
class ResourceDefinition:
    """资源定义"""
    uri: str
    name: str
    description: Optional[str] = None
    mime_type: Optional[str] = None
    
    def to_dict(self) -> dict:
        result = {
            "uri": self.uri,
            "name": self.name,
        }
        if self.description:
            result["description"] = self.description
        if self.mime_type:
            result["mimeType"] = self.mime_type
        return result


@dataclass
class ResourceContent:
    """资源内容"""
    uri: str
    mime_type: Optional[str] = None
    text: Optional[str] = None
    blob: Optional[str] = None  # base64 编码
    
    def to_dict(self) -> dict:
        result = {"uri": self.uri}
        if self.mime_type:
            result["mimeType"] = self.mime_type
        if self.text is not None:
            result["text"] = self.text
        if self.blob is not None:
            result["blob"] = self.blob
        return result


@dataclass
class ServiceInfo:
    """服务信息"""
    name: str
    description: str
    version: str
    endpoint: str
    capabilities: List[str] = field(default_factory=list)
    tools: List[ToolDefinition] = field(default_factory=list)
    resources: List[ResourceDefinition] = field(default_factory=list)
    registered_at: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "endpoint": self.endpoint,
            "capabilities": self.capabilities,
            "tools": [t.to_dict() for t in self.tools],
            "resources": [r.to_dict() for r in self.resources],
            "registered_at": self.registered_at,
            "last_heartbeat": self.last_heartbeat,
        }


@dataclass
class InitializeParams:
    """初始化参数"""
    protocol_version: str = "2024-11-05"
    capabilities: dict = field(default_factory=dict)
    client_info: dict = field(default_factory=lambda: {"name": "workagent", "version": "1.0.0"})


@dataclass
class InitializeResult:
    """初始化结果"""
    protocol_version: str = "2024-11-05"
    capabilities: dict = field(default_factory=dict)
    server_info: dict = field(default_factory=lambda: {"name": "workagent-mcp", "version": "1.0.0"})


# 工具处理器类型
ToolHandler = Callable[[dict], Awaitable[ToolResult]]
