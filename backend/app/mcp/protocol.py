"""
MCP Protocol — 协议定义
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Tool:
    """工具定义"""
    name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }


@dataclass
class Resource:
    """资源定义"""
    uri: str
    name: str
    description: str = ""
    mime_type: str = "application/json"
    
    def to_dict(self) -> Dict:
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mime_type
        }


@dataclass
class ToolCall:
    """工具调用"""
    tool_name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "toolName": self.tool_name,
            "arguments": self.arguments
        }


@dataclass
class ToolResult:
    """工具调用结果"""
    success: bool
    output: Any = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error
        }
