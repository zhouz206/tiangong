"""
MCP API 路由
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

router = APIRouter(tags=["mcp"])


class MCPTool(BaseModel):
    """MCP 工具"""
    name: str
    description: str
    parameters: Dict[str, Any]


class MCPResource(BaseModel):
    """MCP 资源"""
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None


class MCPInfo(BaseModel):
    """MCP 服务信息"""
    name: str
    version: str
    tools: List[MCPTool]
    resources: List[MCPResource]


# 模拟的 MCP 工具和资源
MCP_TOOLS = [
    MCPTool(
        name="file_read",
        description="读取文件内容",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"}
            },
            "required": ["path"]
        }
    ),
    MCPTool(
        name="file_write",
        description="写入文件内容",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"},
                "content": {"type": "string", "description": "文件内容"}
            },
            "required": ["path", "content"]
        }
    ),
    MCPTool(
        name="file_list",
        description="列出目录内容",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "目录路径"}
            },
            "required": ["path"]
        }
    ),
]

MCP_RESOURCES = [
    MCPResource(
        uri="file:///",
        name="File System",
        description="访问文件系统"
    ),
]


@router.get("/", response_model=MCPInfo)
async def get_mcp_info():
    """获取 MCP 服务信息"""
    return MCPInfo(
        name="workagent-mcp",
        version="1.0.0",
        tools=MCP_TOOLS,
        resources=MCP_RESOURCES
    )


@router.get("/tools", response_model=List[MCPTool])
async def list_mcp_tools():
    """获取 MCP 工具列表"""
    return MCP_TOOLS


@router.get("/resources", response_model=List[MCPResource])
async def list_mcp_resources():
    """获取 MCP 资源列表"""
    return MCP_RESOURCES
