"""
MCP Server — MCP 服务端
"""
import asyncio
from typing import Any, Callable, Dict, List, Optional
from .protocol import Tool, Resource, ToolCall, ToolResult


class MCPServer:
    """
    MCP 服务器
    
    功能:
    - 工具注册
    - 资源注册
    - 请求处理
    """
    
    def __init__(self, name: str = "mcp-server"):
        self.name = name
        self._tools: Dict[str, Dict] = {}
        self._resources: Dict[str, Resource] = {}
    
    def register_tool(self, name: str, description: str, input_schema: Dict, handler: Callable) -> None:
        """注册工具"""
        tool = Tool(name=name, description=description, input_schema=input_schema)
        self._tools[name] = {"tool": tool, "handler": handler}
    
    def register_resource(self, resource: Resource) -> None:
        """注册资源"""
        self._resources[resource.uri] = resource
    
    def list_tools(self) -> List[Tool]:
        """获取工具列表"""
        return [item["tool"] for item in self._tools.values()]
    
    def list_resources(self) -> List[Resource]:
        """获取资源列表"""
        return list(self._resources.values())
    
    async def call_tool(self, call: ToolCall) -> ToolResult:
        """
        调用工具
        
        Args:
            call: 工具调用
            
        Returns:
            ToolResult: 调用结果
        """
        if call.tool_name not in self._tools:
            return ToolResult(
                success=False,
                error=f"Tool '{call.tool_name}' not found"
            )
        
        try:
            handler = self._tools[call.tool_name]["handler"]
            output = await handler(call.arguments) if asyncio.iscoroutinefunction(handler) else handler(call.arguments)
            return ToolResult(success=True, output=output)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def get_resource(self, uri: str) -> Optional[Resource]:
        """获取资源"""
        return self._resources.get(uri)
