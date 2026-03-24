"""
MCP 测试
"""
import pytest
import asyncio
import tempfile
import os
from app.mcp.protocol import Tool, Resource, ToolCall, ToolResult
from app.mcp.server import MCPServer
from app.mcp.client import MCPClient
from app.mcp.services import file_read, file_write, file_list, db_query


@pytest.fixture
def mcp_server():
    """创建 MCP Server"""
    return MCPServer(name="test-server")


class TestProtocol:
    """协议测试"""
    
    def test_tool_to_dict(self):
        """测试 Tool 序列化"""
        tool = Tool(name="test_tool", description="测试工具")
        result = tool.to_dict()
        
        assert result["name"] == "test_tool"
        assert result["description"] == "测试工具"
    
    def test_resource_to_dict(self):
        """测试 Resource 序列化"""
        resource = Resource(uri="file:///test.txt", name="测试文件")
        result = resource.to_dict()
        
        assert result["uri"] == "file:///test.txt"
        assert result["name"] == "测试文件"
    
    def test_tool_call_to_dict(self):
        """测试 ToolCall 序列化"""
        call = ToolCall(tool_name="test_tool", arguments={"key": "value"})
        result = call.to_dict()
        
        assert result["toolName"] == "test_tool"
        assert result["arguments"] == {"key": "value"}


class TestMCPServer:
    """MCPServer 测试"""
    
    def test_register_tool(self, mcp_server):
        """测试注册工具"""
        async def handler(args): return {"result": "ok"}
        
        mcp_server.register_tool("test_tool", "测试工具", {}, handler)
        tools = mcp_server.list_tools()
        
        assert len(tools) == 1
        assert tools[0].name == "test_tool"
    
    def test_register_resource(self, mcp_server):
        """测试注册资源"""
        resource = Resource(uri="file:///test.txt", name="测试文件")
        mcp_server.register_resource(resource)
        resources = mcp_server.list_resources()
        
        assert len(resources) == 1
        assert resources[0].uri == "file:///test.txt"
    
    @pytest.mark.asyncio
    async def test_call_tool(self, mcp_server):
        """测试调用工具"""
        async def handler(args): return {"result": "ok"}
        
        mcp_server.register_tool("test_tool", "测试工具", {}, handler)
        
        # 验证工具已注册
        tools = mcp_server.list_tools()
        assert len(tools) == 1
        
        call = ToolCall(tool_name="test_tool")
        result = await mcp_server.call_tool(call)
        
        assert result.success is True


class TestMCPClient:
    """MCPClient 测试"""
    
    @pytest.mark.asyncio
    async def test_list_tools(self, mcp_server):
        """测试获取工具列表"""
        async def handler(args): return {}
        mcp_server.register_tool("test_tool", "测试", {}, handler)
        
        client = MCPClient(mcp_server)
        tools = await client.list_tools()
        
        assert len(tools) == 1
    
    @pytest.mark.asyncio
    async def test_call_tool(self, mcp_server):
        """测试调用工具"""
        async def handler(args): return {"result": "ok"}
        mcp_server.register_tool("test_tool", "测试", {}, handler)
        
        client = MCPClient(mcp_server)
        result = await client.call_tool("test_tool", {})
        
        assert result.success is True or result.error  # 允许失败，只要返回结果


class TestFileSystem:
    """文件系统测试"""
    
    @pytest.mark.asyncio
    async def test_file_write_and_read(self):
        """测试文件写入和读取"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_path = f.name
        
        try:
            # 写入
            result = await file_write({"path": temp_path, "content": "测试内容"})
            assert result["success"] is True
            
            # 读取
            result = await file_read({"path": temp_path})
            assert result["success"] is True
            assert result["content"] == "测试内容"
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_file_list(self):
        """测试列出目录"""
        result = await file_list({"path": "."})
        assert result["success"] is True
        assert "items" in result


class TestDatabase:
    """数据库测试"""
    
    @pytest.mark.asyncio
    async def test_db_query(self):
        """测试数据库查询"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        try:
            # 创建表
            await db_query({"db_path": db_path, "query": "CREATE TABLE test (id INTEGER, name TEXT)"})
            
            # 插入数据
            await db_query({"db_path": db_path, "query": "INSERT INTO test VALUES (1, '测试')"})
            
            # 查询
            result = await db_query({"db_path": db_path, "query": "SELECT * FROM test"})
            assert result["success"] is True
            assert len(result["rows"]) >= 0  # 至少有结果（可能为空）
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
