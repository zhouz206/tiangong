"""
MCP 服务端

提供 MCP 工具和服务。
"""
import asyncio
import json
import logging
from typing import Any, Optional, List, Dict, Callable, Awaitable
from dataclasses import dataclass, field
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import time

from .types import (
    MCPRequest,
    MCPResponse,
    MCPError,
    MCPErrorCode,
    MCPMethod,
    ToolDefinition,
    ToolCall,
    ToolResult,
    ResourceDefinition,
    ResourceContent,
    InitializeParams,
    InitializeResult,
    ToolHandler,
)


logger = logging.getLogger(__name__)


@dataclass
class RegisteredTool:
    """已注册的工具"""
    definition: ToolDefinition
    handler: ToolHandler
    enabled: bool = True
    call_count: int = 0
    last_called: Optional[float] = None


@dataclass
class RegisteredResource:
    """已注册的资源"""
    definition: ResourceDefinition
    handler: Callable[[str], Awaitable[ResourceContent]]
    enabled: bool = True


class MCPServer:
    """
    MCP 服务端
    
    提供 MCP 协议实现，支持工具注册和调用。
    
    使用示例:
        server = MCPServer(name="my-service", version="1.0.0")
        
        # 注册工具
        @server.tool(
            name="echo",
            description="Echo back the input message",
            input_schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                },
                "required": ["message"]
            }
        )
        async def echo_handler(args: dict) -> ToolResult:
            return ToolResult(content=[{"type": "text", "text": args.get("message", "")}])
        
        # 启动服务
        app = FastAPI()
        server.mount(app, "/mcp")
    """
    
    def __init__(
        self,
        name: str = "workagent-mcp",
        version: str = "1.0.0",
        description: str = "WorkAgent MCP Server",
    ):
        """
        初始化 MCP 服务端
        
        Args:
            name: 服务名称
            version: 服务版本
            description: 服务描述
        """
        self.name = name
        self.version = version
        self.description = description
        
        self._tools: Dict[str, RegisteredTool] = {}
        self._resources: Dict[str, RegisteredResource] = {}
        self._initialized = False
        self._client_capabilities: dict = {}
        self._request_handlers: List[Callable] = []
        self._response_handlers: List[Callable] = []
    
    def tool(
        self,
        name: str,
        description: str,
        input_schema: Optional[dict] = None,
        annotations: Optional[dict] = None,
    ):
        """
        工具注册装饰器
        
        Args:
            name: 工具名称
            description: 工具描述
            input_schema: JSON Schema 格式的输入模式
            annotations: 工具注解
            
        Returns:
            装饰器函数
        """
        def decorator(handler: ToolHandler):
            tool_def = ToolDefinition(
                name=name,
                description=description,
                input_schema=input_schema or {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                annotations=annotations,
            )
            
            self.register_tool(tool_def, handler)
            return handler
        
        return decorator
    
    def resource(
        self,
        uri: str,
        name: str,
        description: Optional[str] = None,
        mime_type: Optional[str] = None,
    ):
        """
        资源注册装饰器
        
        Args:
            uri: 资源 URI
            name: 资源名称
            description: 资源描述
            mime_type: MIME 类型
            
        Returns:
            装饰器函数
        """
        def decorator(handler: Callable[[str], Awaitable[ResourceContent]]):
            resource_def = ResourceDefinition(
                uri=uri,
                name=name,
                description=description,
                mime_type=mime_type,
            )
            
            self.register_resource(resource_def, handler)
            return handler
        
        return decorator
    
    def register_tool(self, definition: ToolDefinition, handler: ToolHandler) -> None:
        """
        注册工具
        
        Args:
            definition: 工具定义
            handler: 工具处理器
        """
        self._tools[definition.name] = RegisteredTool(
            definition=definition,
            handler=handler,
        )
        logger.info(f"Registered tool: {definition.name}")
    
    def unregister_tool(self, name: str) -> bool:
        """
        注销工具
        
        Args:
            name: 工具名称
            
        Returns:
            是否成功
        """
        if name in self._tools:
            del self._tools[name]
            logger.info(f"Unregistered tool: {name}")
            return True
        return False
    
    def register_resource(
        self,
        definition: ResourceDefinition,
        handler: Callable[[str], Awaitable[ResourceContent]],
    ) -> None:
        """
        注册资源
        
        Args:
            definition: 资源定义
            handler: 资源处理器
        """
        self._resources[definition.uri] = RegisteredResource(
            definition=definition,
            handler=handler,
        )
        logger.info(f"Registered resource: {definition.uri}")
    
    def unregister_resource(self, uri: str) -> bool:
        """
        注销资源
        
        Args:
            uri: 资源 URI
            
        Returns:
            是否成功
        """
        if uri in self._resources:
            del self._resources[uri]
            logger.info(f"Unregistered resource: {uri}")
            return True
        return False
    
    def enable_tool(self, name: str) -> bool:
        """启用工具"""
        if name in self._tools:
            self._tools[name].enabled = True
            return True
        return False
    
    def disable_tool(self, name: str) -> bool:
        """禁用工具"""
        if name in self._tools:
            self._tools[name].enabled = False
            return True
        return False
    
    def get_tool_stats(self, name: str) -> Optional[dict]:
        """获取工具统计信息"""
        if name not in self._tools:
            return None
        
        tool = self._tools[name]
        return {
            "name": name,
            "enabled": tool.enabled,
            "call_count": tool.call_count,
            "last_called": tool.last_called,
        }
    
    def list_tools(self) -> List[ToolDefinition]:
        """列出所有已启用的工具"""
        return [
            tool.definition
            for tool in self._tools.values()
            if tool.enabled
        ]
    
    def list_resources(self) -> List[ResourceDefinition]:
        """列出所有已启用的资源"""
        return [
            resource.definition
            for resource in self._resources.values()
            if resource.enabled
        ]
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """
        处理 MCP 请求
        
        Args:
            request: MCP 请求
            
        Returns:
            MCP 响应
        """
        # 运行请求前处理器
        for handler in self._request_handlers:
            try:
                await handler(request)
            except Exception as e:
                logger.warning(f"Request handler error: {e}")
        
        try:
            method = request.method
            
            if method == MCPMethod.INITIALIZE:
                result = await self._handle_initialize(request.params or {})
            elif method == MCPMethod.INITIALIZED:
                result = {}
            elif method == MCPMethod.TOOLS_LIST:
                result = await self._handle_tools_list()
            elif method == MCPMethod.TOOLS_CALL:
                result = await self._handle_tools_call(request.params or {})
            elif method == MCPMethod.RESOURCES_LIST:
                result = await self._handle_resources_list()
            elif method == MCPMethod.RESOURCES_READ:
                result = await self._handle_resources_read(request.params or {})
            elif method == MCPMethod.PING:
                result = {}
            else:
                return MCPResponse(
                    error=MCPError(
                        code=MCPErrorCode.METHOD_NOT_FOUND,
                        message=f"Method not found: {method}"
                    ),
                    id=request.id,
                )
            
            response = MCPResponse(result=result, id=request.id)
            
        except MCPError as e:
            response = MCPResponse(error=e, id=request.id)
        except Exception as e:
            logger.exception(f"Error handling request: {e}")
            response = MCPResponse(
                error=MCPError(
                    code=MCPErrorCode.INTERNAL_ERROR,
                    message=str(e)
                ),
                id=request.id,
            )
        
        # 运行响应后处理器
        for handler in self._response_handlers:
            try:
                await handler(response)
            except Exception as e:
                logger.warning(f"Response handler error: {e}")
        
        return response
    
    async def _handle_initialize(self, params: dict) -> dict:
        """处理初始化请求"""
        self._client_capabilities = params.get("capabilities", {})
        client_info = params.get("clientInfo", {})
        
        logger.info(
            f"Initialized by client: {client_info.get('name', 'unknown')} "
            f"{client_info.get('version', 'unknown')}"
        )
        
        self._initialized = True
        
        return InitializeResult(
            capabilities={
                "tools": {"listChanged": True},
                "resources": {"listChanged": True},
            },
            server_info={
                "name": self.name,
                "version": self.version,
            }
        ).__dict__
    
    async def _handle_tools_list(self) -> dict:
        """处理工具列表请求"""
        tools = self.list_tools()
        return {"tools": [t.to_dict() for t in tools]}
    
    async def _handle_tools_call(self, params: dict) -> dict:
        """处理工具调用请求"""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        if tool_name not in self._tools:
            raise MCPError(
                code=MCPErrorCode.INVALID_PARAMS,
                message=f"Unknown tool: {tool_name}"
            )
        
        tool = self._tools[tool_name]
        
        if not tool.enabled:
            raise MCPError(
                code=MCPErrorCode.INTERNAL_ERROR,
                message=f"Tool is disabled: {tool_name}"
            )
        
        # 更新统计
        tool.call_count += 1
        tool.last_called = time.time()
        
        try:
            result = await tool.handler(arguments)
            return result.to_dict()
        except Exception as e:
            logger.exception(f"Tool execution error: {tool_name}")
            return ToolResult(
                is_error=True,
                error_message=str(e)
            ).to_dict()
    
    async def _handle_resources_list(self) -> dict:
        """处理资源列表请求"""
        resources = self.list_resources()
        return {"resources": [r.to_dict() for r in resources]}
    
    async def _handle_resources_read(self, params: dict) -> dict:
        """处理资源读取请求"""
        uri = params.get("uri", "")
        
        if uri not in self._resources:
            raise MCPError(
                code=MCPErrorCode.INVALID_PARAMS,
                message=f"Unknown resource: {uri}"
            )
        
        resource = self._resources[uri]
        
        if not resource.enabled:
            raise MCPError(
                code=MCPErrorCode.INTERNAL_ERROR,
                message=f"Resource is disabled: {uri}"
            )
        
        try:
            content = await resource.handler(uri)
            return content.to_dict()
        except Exception as e:
            logger.exception(f"Resource read error: {uri}")
            raise MCPError(
                code=MCPErrorCode.INTERNAL_ERROR,
                message=str(e)
            )
    
    def add_request_handler(self, handler: Callable[[MCPRequest], Awaitable[None]]) -> None:
        """添加请求处理器"""
        self._request_handlers.append(handler)
    
    def add_response_handler(self, handler: Callable[[MCPResponse], Awaitable[None]]) -> None:
        """添加响应处理器"""
        self._response_handlers.append(handler)
    
    def mount(self, app: FastAPI, path: str = "/mcp") -> None:
        """
        将 MCP 服务端挂载到 FastAPI 应用
        
        Args:
            app: FastAPI 应用
            path: 挂载路径
        """
        @app.post(path)
        async def mcp_endpoint(request: Request):
            try:
                data = await request.json()
                mcp_request = MCPRequest.from_dict(data)
                response = await self.handle_request(mcp_request)
                return JSONResponse(content=response.to_dict())
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON")
            except Exception as e:
                logger.exception(f"MCP endpoint error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get(path)
        async def mcp_info():
            """获取服务端信息"""
            return {
                "name": self.name,
                "version": self.version,
                "description": self.description,
                "tools_count": len([t for t in self._tools.values() if t.enabled]),
                "resources_count": len([r for r in self._resources.values() if r.enabled]),
                "initialized": self._initialized,
            }


class MCPServerCluster:
    """
    MCP 服务端集群
    
    管理多个 MCP 服务端实例。
    """
    
    def __init__(self):
        self._servers: Dict[str, MCPServer] = {}
    
    def register_server(self, name: str, server: MCPServer) -> None:
        """注册服务端"""
        self._servers[name] = server
    
    def get_server(self, name: str) -> Optional[MCPServer]:
        """获取服务端"""
        return self._servers.get(name)
    
    def list_servers(self) -> List[str]:
        """列出所有服务端"""
        return list(self._servers.keys())
    
    async def broadcast(self, method: str, params: Optional[dict] = None) -> List[dict]:
        """广播请求到所有服务端"""
        results = []
        for server in self._servers.values():
            try:
                request = MCPRequest(method=method, params=params)
                response = await server.handle_request(request)
                results.append(response.result)
            except Exception as e:
                logger.warning(f"Broadcast to {server.name} failed: {e}")
        return results
