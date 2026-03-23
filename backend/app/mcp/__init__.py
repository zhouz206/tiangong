"""
MCP (Model Context Protocol) 集成模块

提供 MCP 客户端、服务端、服务发现、安全沙箱和内置服务。

使用示例:
    from app.mcp import (
        MCPServer,
        MCPClient,
        LocalServiceRegistry,
        SandboxedExecutor,
        FileSystemService,
        DatabaseService,
        HTTPClientService,
    )
    
    # 创建服务端
    server = MCPServer(name="my-service", version="1.0.0")
    
    # 注册工具
    @server.tool(
        name="echo",
        description="Echo back the input",
        input_schema={
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            },
            "required": ["message"]
        }
    )
    async def echo_handler(args: dict):
        return ToolResult(content=[{"type": "text", "text": args.get("message", "")}])
    
    # 使用内置服务
    file_service = FileSystemService(allowed_roots=["/tmp"])
    file_service.register(server)
    
    # 挂载到 FastAPI
    from fastapi import FastAPI
    app = FastAPI()
    server.mount(app, "/mcp")
"""

# 类型定义
from .types import (
    MCPError,
    MCPErrorCode,
    MCPMethod,
    MCPRequest,
    MCPResponse,
    ToolDefinition,
    ToolCall,
    ToolResult,
    ResourceDefinition,
    ResourceContent,
    ServiceInfo,
    InitializeParams,
    InitializeResult,
    ToolHandler,
)

# 客户端
from .client import MCPClient, MCPClientError, MCPClientPool

# 服务端
from .server import MCPServer, MCPServerCluster, RegisteredTool, RegisteredResource

# 服务发现
from .discovery import (
    ServiceRegistry,
    ServiceDiscoveryClient,
    LocalServiceRegistry,
    DiscoveredService,
    ServiceStatus,
)

# 安全沙箱
from .sandbox import (
    SandboxConfig,
    SandboxedExecutor,
    SandboxContext,
    SandboxManager,
    PermissionChecker,
    PermissionRule,
    PermissionLevel,
    ResourceType,
    AuditLog,
    SecurityPolicy,
    sandboxed,
)

# 内置服务
from .services import (
    FileSystemService,
    DatabaseService,
    HTTPClientService,
)

__all__ = [
    # 类型
    "MCPError",
    "MCPErrorCode",
    "MCPMethod",
    "MCPRequest",
    "MCPResponse",
    "ToolDefinition",
    "ToolCall",
    "ToolResult",
    "ResourceDefinition",
    "ResourceContent",
    "ServiceInfo",
    "InitializeParams",
    "InitializeResult",
    "ToolHandler",
    
    # 客户端
    "MCPClient",
    "MCPClientError",
    "MCPClientPool",
    
    # 服务端
    "MCPServer",
    "MCPServerCluster",
    "RegisteredTool",
    "RegisteredResource",
    
    # 服务发现
    "ServiceRegistry",
    "ServiceDiscoveryClient",
    "LocalServiceRegistry",
    "DiscoveredService",
    "ServiceStatus",
    
    # 安全沙箱
    "SandboxConfig",
    "SandboxedExecutor",
    "SandboxContext",
    "SandboxManager",
    "PermissionChecker",
    "PermissionRule",
    "PermissionLevel",
    "ResourceType",
    "AuditLog",
    "SecurityPolicy",
    "sandboxed",
    
    # 内置服务
    "FileSystemService",
    "DatabaseService",
    "HTTPClientService",
]
