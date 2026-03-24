"""
MCP Client — MCP 客户端
"""
from typing import Any, Dict, List, Optional
from .protocol import Tool, Resource, ToolCall, ToolResult


class MCPClient:
    """
    MCP 客户端
    
    功能:
    - 服务发现
    - 工具调用
    """
    
    def __init__(self, server):
        self.server = server
    
    async def list_tools(self) -> List[Tool]:
        """获取可用工具列表"""
        return self.server.list_tools()
    
    async def list_resources(self) -> List[Resource]:
        """获取可用资源列表"""
        return self.server.list_resources()
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> ToolResult:
        """
        调用工具
        
        Args:
            tool_name: 工具名称
            arguments: 参数
            
        Returns:
            ToolResult: 调用结果
        """
        call = ToolCall(tool_name=tool_name, arguments=arguments or {})
        return await self.server.call_tool(call)
