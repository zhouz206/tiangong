"""
MCP 客户端

用于调用外部 MCP 服务。
"""
import asyncio
import json
import logging
from typing import Any, Optional, List, Dict
import httpx

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
)


logger = logging.getLogger(__name__)


class MCPClient:
    """
    MCP 客户端
    
    用于连接和调用外部 MCP 服务。
    
    使用示例:
        client = MCPClient("http://localhost:8080/mcp")
        await client.initialize()
        
        # 列出可用工具
        tools = await client.list_tools()
        
        # 调用工具
        result = await client.call_tool("file_read", {"path": "/tmp/test.txt"})
    """
    
    def __init__(
        self,
        endpoint: str,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        初始化 MCP 客户端
        
        Args:
            endpoint: MCP 服务端点 URL
            timeout: 请求超时时间（秒）
            headers: 额外的 HTTP 头
        """
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout
        self.headers = headers or {}
        self._client: Optional[httpx.AsyncClient] = None
        self._initialized = False
        self._server_capabilities: dict = {}
        self._request_id = 0
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def connect(self) -> None:
        """建立连接"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.endpoint,
                timeout=httpx.Timeout(self.timeout),
                headers=self.headers,
            )
    
    async def close(self) -> None:
        """关闭连接"""
        if self._client:
            await self._client.aclose()
            self._client = None
        self._initialized = False
    
    async def initialize(self) -> InitializeResult:
        """
        初始化 MCP 连接
        
        Returns:
            初始化结果
        """
        if not self._client:
            await self.connect()
        
        params = InitializeParams()
        response = await self._send_request(
            method=MCPMethod.INITIALIZE,
            params=params.__dict__
        )
        
        result = InitializeResult(
            protocol_version=response.get("protocolVersion", "2024-11-05"),
            capabilities=response.get("capabilities", {}),
            server_info=response.get("serverInfo", {}),
        )
        
        self._server_capabilities = result.capabilities
        self._initialized = True
        
        # 发送 initialized 通知
        await self._send_notification(MCPMethod.INITIALIZED)
        
        return result
    
    async def _send_request(
        self,
        method: str,
        params: Optional[dict] = None,
    ) -> Any:
        """
        发送 MCP 请求
        
        Args:
            method: 方法名
            params: 请求参数
            
        Returns:
            响应结果
            
        Raises:
            MCPError: 当请求失败时
        """
        if not self._client:
            raise RuntimeError("Client not connected")
        
        self._request_id += 1
        request = MCPRequest(
            method=method,
            params=params,
            id=self._request_id,
        )
        
        logger.debug(f"Sending MCP request: {method}")
        
        try:
            response = await self._client.post(
                "/mcp",
                json=request.to_dict(),
            )
            response.raise_for_status()
            
            response_data = response.json()
            mcp_response = MCPResponse(
                jsonrpc=response_data.get("jsonrpc", "2.0"),
                result=response_data.get("result"),
                error=MCPError(**response_data["error"]) if response_data.get("error") else None,
                id=response_data.get("id"),
            )
            
            if mcp_response.error:
                raise MCPClientError(
                    mcp_response.error.code,
                    mcp_response.error.message,
                    mcp_response.error.data
                )
            
            return mcp_response.result
            
        except httpx.HTTPError as e:
            raise MCPClientError(
                MCPErrorCode.INTERNAL_ERROR,
                f"HTTP error: {str(e)}"
            )
        except json.JSONDecodeError as e:
            raise MCPClientError(
                MCPErrorCode.PARSE_ERROR,
                f"Invalid JSON response: {str(e)}"
            )
    
    async def _send_notification(self, method: str, params: Optional[dict] = None) -> None:
        """发送通知（不需要响应）"""
        if not self._client:
            return
        
        request = MCPRequest(method=method, params=params)
        try:
            await self._client.post("/mcp", json=request.to_dict())
        except Exception as e:
            logger.warning(f"Failed to send notification {method}: {e}")
    
    async def list_tools(self) -> List[ToolDefinition]:
        """
        列出可用工具
        
        Returns:
            工具定义列表
        """
        if not self._initialized:
            await self.initialize()
        
        result = await self._send_request(MCPMethod.TOOLS_LIST)
        tools_data = result.get("tools", [])
        
        return [
            ToolDefinition(
                name=t.get("name", ""),
                description=t.get("description", ""),
                input_schema=t.get("inputSchema", {}),
                annotations=t.get("annotations"),
            )
            for t in tools_data
        ]
    
    async def call_tool(
        self,
        name: str,
        arguments: Optional[dict] = None,
    ) -> ToolResult:
        """
        调用工具
        
        Args:
            name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具调用结果
        """
        if not self._initialized:
            await self.initialize()
        
        result = await self._send_request(
            MCPMethod.TOOLS_CALL,
            {"name": name, "arguments": arguments or {}}
        )
        
        if isinstance(result, dict):
            return ToolResult(
                content=result.get("content", []),
                is_error=result.get("isError", False),
                error_message=result.get("errorMessage"),
            )
        
        return ToolResult(content=[{"type": "text", "text": str(result)}])
    
    async def list_resources(self) -> List[ResourceDefinition]:
        """
        列出可用资源
        
        Returns:
            资源定义列表
        """
        if not self._initialized:
            await self.initialize()
        
        result = await self._send_request(MCPMethod.RESOURCES_LIST)
        resources_data = result.get("resources", [])
        
        return [
            ResourceDefinition(
                uri=r.get("uri", ""),
                name=r.get("name", ""),
                description=r.get("description"),
                mime_type=r.get("mimeType"),
            )
            for r in resources_data
        ]
    
    async def read_resource(self, uri: str) -> ResourceContent:
        """
        读取资源
        
        Args:
            uri: 资源 URI
            
        Returns:
            资源内容
        """
        if not self._initialized:
            await self.initialize()
        
        result = await self._send_request(
            MCPMethod.RESOURCES_READ,
            {"uri": uri}
        )
        
        if isinstance(result, dict):
            return ResourceContent(
                uri=result.get("uri", uri),
                mime_type=result.get("mimeType"),
                text=result.get("text"),
                blob=result.get("blob"),
            )
        
        return ResourceContent(uri=uri, text=str(result))
    
    async def ping(self) -> bool:
        """
        发送心跳检测
        
        Returns:
            是否成功
        """
        try:
            await self._send_request(MCPMethod.PING)
            return True
        except Exception:
            return False
    
    @property
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized
    
    @property
    def capabilities(self) -> dict:
        """获取服务端能力"""
        return self._server_capabilities


class MCPClientError(Exception):
    """MCP 客户端错误"""
    
    def __init__(
        self,
        code: MCPErrorCode = MCPErrorCode.INTERNAL_ERROR,
        message: str = "Unknown error",
        data: Optional[Any] = None,
    ):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)
    
    def to_error(self) -> MCPError:
        return MCPError(code=self.code, message=self.message, data=self.data)


class MCPClientPool:
    """
    MCP 客户端连接池
    
    管理多个 MCP 客户端连接。
    """
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self._clients: Dict[str, MCPClient] = {}
        self._lock = asyncio.Lock()
    
    async def get_client(self, endpoint: str) -> MCPClient:
        """获取或创建客户端"""
        async with self._lock:
            if endpoint not in self._clients:
                if len(self._clients) >= self.max_connections:
                    # 简单的 LRU 策略：关闭最早的客户端
                    oldest_endpoint = next(iter(self._clients))
                    await self._clients[oldest_endpoint].close()
                    del self._clients[oldest_endpoint]
                
                client = MCPClient(endpoint)
                await client.initialize()
                self._clients[endpoint] = client
            
            return self._clients[endpoint]
    
    async def close_all(self) -> None:
        """关闭所有客户端"""
        async with self._lock:
            for client in self._clients.values():
                await client.close()
            self._clients.clear()
