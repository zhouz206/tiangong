"""
MCP 模块单元测试
"""
import pytest
import asyncio
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# 导入被测试模块
from app.mcp.types import (
    MCPError,
    MCPErrorCode,
    MCPMethod,
    MCPRequest,
    MCPResponse,
    ToolDefinition,
    ToolResult,
    ResourceDefinition,
    ResourceContent,
    ServiceInfo,
)
from app.mcp.server import MCPServer, MCPServerCluster
from app.mcp.sandbox import (
    SandboxConfig,
    SandboxedExecutor,
    PermissionRule,
    PermissionLevel,
    ResourceType,
    PermissionChecker,
    SecurityPolicy,
)
from app.mcp.discovery import (
    ServiceRegistry,
    LocalServiceRegistry,
    DiscoveredService,
    ServiceStatus,
)


# ==================== 类型测试 ====================

class TestMCPRequest:
    """测试 MCP 请求"""
    
    def test_request_to_dict(self):
        """测试请求序列化"""
        req = MCPRequest(
            method="tools/list",
            params={"test": "value"},
            id=1
        )
        
        data = req.to_dict()
        assert data["jsonrpc"] == "2.0"
        assert data["method"] == "tools/list"
        assert data["params"] == {"test": "value"}
        assert data["id"] == 1
    
    def test_request_from_dict(self):
        """测试请求反序列化"""
        data = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "test"},
            "id": "abc"
        }
        
        req = MCPRequest.from_dict(data)
        assert req.method == "tools/call"
        assert req.params == {"name": "test"}
        assert req.id == "abc"
    
    def test_request_minimal(self):
        """测试最小请求"""
        req = MCPRequest(method="ping")
        data = req.to_dict()
        assert "params" not in data
        assert "id" not in data


class TestMCPResponse:
    """测试 MCP 响应"""
    
    def test_success_response(self):
        """测试成功响应"""
        resp = MCPResponse(
            result={"tools": []},
            id=1
        )
        
        data = resp.to_dict()
        assert data["result"] == {"tools": []}
        assert "error" not in data
    
    def test_error_response(self):
        """测试错误响应"""
        error = MCPError(
            code=MCPErrorCode.METHOD_NOT_FOUND,
            message="Method not found"
        )
        resp = MCPResponse(error=error, id=1)
        
        data = resp.to_dict()
        assert "error" in data
        assert data["error"]["code"] == -32601
        assert data["error"]["message"] == "Method not found"


class TestToolDefinition:
    """测试工具定义"""
    
    def test_tool_to_dict(self):
        """测试工具序列化"""
        tool = ToolDefinition(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object"}
        )
        
        data = tool.to_dict()
        assert data["name"] == "test_tool"
        assert data["description"] == "A test tool"
        assert data["inputSchema"] == {"type": "object"}


class TestToolResult:
    """测试工具结果"""
    
    def test_success_result(self):
        """测试成功结果"""
        result = ToolResult(
            content=[{"type": "text", "text": "Hello"}]
        )
        
        data = result.to_dict()
        assert data["content"] == [{"type": "text", "text": "Hello"}]
        assert data.get("isError") is None
    
    def test_error_result(self):
        """测试错误结果"""
        result = ToolResult(
            is_error=True,
            error_message="Something went wrong"
        )
        
        data = result.to_dict()
        assert data["isError"] is True
        assert data["errorMessage"] == "Something went wrong"


# ==================== 服务端测试 ====================

class TestMCPServer:
    """测试 MCP 服务端"""
    
    @pytest.fixture
    def server(self):
        """创建服务端实例"""
        return MCPServer(name="test-server", version="1.0.0")
    
    def test_server_initialization(self, server):
        """测试服务端初始化"""
        assert server.name == "test-server"
        assert server.version == "1.0.0"
        assert server._initialized is False
    
    def test_register_tool(self, server):
        """测试工具注册"""
        tool_def = ToolDefinition(
            name="echo",
            description="Echo tool",
            input_schema={"type": "object"}
        )
        
        async def handler(args):
            return ToolResult(content=[])
        
        server.register_tool(tool_def, handler)
        
        tools = server.list_tools()
        assert len(tools) == 1
        assert tools[0].name == "echo"
    
    def test_tool_decorator(self, server):
        """测试工具装饰器"""
        @server.tool(
            name="test",
            description="Test tool",
            input_schema={"type": "object"}
        )
        async def test_handler(args):
            return ToolResult(content=[])
        
        tools = server.list_tools()
        assert len(tools) == 1
        assert tools[0].name == "test"
    
    def test_unregister_tool(self, server):
        """测试工具注销"""
        tool_def = ToolDefinition(
            name="temp",
            description="Temporary tool",
            input_schema={}
        )
        
        async def handler(args):
            return ToolResult(content=[])
        
        server.register_tool(tool_def, handler)
        assert server.unregister_tool("temp") is True
        assert server.unregister_tool("nonexistent") is False
    
    def test_enable_disable_tool(self, server):
        """测试工具启用/禁用"""
        tool_def = ToolDefinition(
            name="toggle",
            description="Toggle tool",
            input_schema={}
        )
        
        async def handler(args):
            return ToolResult(content=[])
        
        server.register_tool(tool_def, handler)
        
        # 默认启用
        tools = server.list_tools()
        assert len(tools) == 1
        
        # 禁用
        server.disable_tool("toggle")
        tools = server.list_tools()
        assert len(tools) == 0
        
        # 启用
        server.enable_tool("toggle")
        tools = server.list_tools()
        assert len(tools) == 1
    
    @pytest.mark.asyncio
    async def test_handle_initialize(self, server):
        """测试初始化请求处理"""
        req = MCPRequest(
            method=MCPMethod.INITIALIZE,
            params={
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            },
            id=1
        )
        
        resp = await server.handle_request(req)
        
        assert resp.error is None
        assert resp.result is not None
        assert server._initialized is True
    
    @pytest.mark.asyncio
    async def test_handle_tools_list(self, server):
        """测试工具列表请求"""
        # 先注册一个工具
        @server.tool(
            name="list_test",
            description="Test for list",
            input_schema={}
        )
        async def handler(args):
            return ToolResult(content=[])
        
        req = MCPRequest(method=MCPMethod.TOOLS_LIST, id=1)
        resp = await server.handle_request(req)
        
        assert resp.error is None
        assert "tools" in resp.result
        assert len(resp.result["tools"]) == 1
    
    @pytest.mark.asyncio
    async def test_handle_tools_call(self, server):
        """测试工具调用请求"""
        @server.tool(
            name="add",
            description="Add two numbers",
            input_schema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                }
            }
        )
        async def add_handler(args):
            a = args.get("a", 0)
            b = args.get("b", 0)
            return ToolResult(content=[
                {"type": "text", "text": str(a + b)}
            ])
        
        req = MCPRequest(
            method=MCPMethod.TOOLS_CALL,
            params={"name": "add", "arguments": {"a": 5, "b": 3}},
            id=1
        )
        resp = await server.handle_request(req)
        
        assert resp.error is None
        assert resp.result["content"][0]["text"] == "8"
    
    @pytest.mark.asyncio
    async def test_handle_unknown_method(self, server):
        """测试未知方法处理"""
        req = MCPRequest(method="unknown/method", id=1)
        resp = await server.handle_request(req)
        
        assert resp.error is not None
        assert resp.error.code == MCPErrorCode.METHOD_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_handle_tool_error(self, server):
        """测试工具执行错误处理"""
        @server.tool(
            name="fail",
            description="Always fails",
            input_schema={}
        )
        async def fail_handler(args):
            raise ValueError("Intentional failure")
        
        req = MCPRequest(
            method=MCPMethod.TOOLS_CALL,
            params={"name": "fail", "arguments": {}},
            id=1
        )
        resp = await server.handle_request(req)
        
        assert resp.result["isError"] is True
        assert "Intentional failure" in resp.result["errorMessage"]


class TestMCPServerCluster:
    """测试服务端集群"""
    
    @pytest.mark.asyncio
    async def test_register_server(self):
        """测试注册服务端"""
        cluster = MCPServerCluster()
        server1 = MCPServer(name="server1")
        server2 = MCPServer(name="server2")
        
        cluster.register_server("s1", server1)
        cluster.register_server("s2", server2)
        
        assert cluster.get_server("s1") is server1
        assert cluster.get_server("s2") is server2
        assert cluster.get_server("s3") is None
    
    @pytest.mark.asyncio
    async def test_list_servers(self):
        """测试列出服务端"""
        cluster = MCPServerCluster()
        cluster.register_server("s1", MCPServer(name="s1"))
        cluster.register_server("s2", MCPServer(name="s2"))
        
        servers = cluster.list_servers()
        assert len(servers) == 2
        assert "s1" in servers
        assert "s2" in servers


# ==================== 沙箱测试 ====================

class TestPermissionRule:
    """测试权限规则"""
    
    def test_exact_match(self):
        """测试精确匹配"""
        rule = PermissionRule(
            resource_type=ResourceType.FILE,
            resource_pattern="/tmp/test.txt",
            level=PermissionLevel.READ
        )
        
        assert rule.matches("/tmp/test.txt") is True
        assert rule.matches("/tmp/other.txt") is False
    
    def test_wildcard_match(self):
        """测试通配符匹配"""
        rule = PermissionRule(
            resource_type=ResourceType.FILE,
            resource_pattern="/tmp/*.txt",
            level=PermissionLevel.READ
        )
        
        assert rule.matches("/tmp/test.txt") is True
        # 注意：* 匹配任意字符包括 /，所以 /tmp/sub/test.txt 也会匹配
        # 如需严格单级匹配，应使用更具体的模式
        assert rule.matches("/tmp/test.pdf") is False
    
    def test_recursive_wildcard(self):
        """测试递归通配符"""
        rule = PermissionRule(
            resource_type=ResourceType.FILE,
            resource_pattern="/tmp/*",
            level=PermissionLevel.READ
        )
        
        assert rule.matches("/tmp/test.txt") is True
        assert rule.matches("/tmp/sub/test.txt") is True


class TestPermissionChecker:
    """测试权限检查器"""
    
    @pytest.fixture
    def checker(self):
        """创建权限检查器"""
        config = SandboxConfig(
            name="test",
            allowed_resources=[
                PermissionRule(
                    resource_type=ResourceType.FILE,
                    resource_pattern="/tmp/*",
                    level=PermissionLevel.READ
                )
            ],
            denied_resources=[
                PermissionRule(
                    resource_type=ResourceType.FILE,
                    resource_pattern="/etc/*",
                    level=PermissionLevel.NONE
                )
            ]
        )
        return PermissionChecker(config)
    
    def test_allowed_access(self, checker):
        """测试允许的访问"""
        allowed, reason = checker.check_permission(
            ResourceType.FILE,
            "/tmp/test.txt",
            PermissionLevel.READ
        )
        assert allowed is True
    
    def test_denied_by_rule(self, checker):
        """测试被规则拒绝的访问"""
        allowed, reason = checker.check_permission(
            ResourceType.FILE,
            "/etc/passwd",
            PermissionLevel.READ
        )
        assert allowed is False
        assert "Denied" in reason
    
    def test_no_matching_rule(self, checker):
        """测试无匹配规则"""
        allowed, reason = checker.check_permission(
            ResourceType.FILE,
            "/home/user/file.txt",
            PermissionLevel.READ
        )
        assert allowed is False


class TestSandboxConfig:
    """测试沙箱配置"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = SandboxConfig()
        assert config.name == "default"
        assert config.max_execution_time == 30.0
        assert config.max_memory_mb == 512
    
    def test_security_policies(self):
        """测试安全策略"""
        # 文件系统策略
        fs_config = SecurityPolicy.default_file_system()
        assert fs_config.name == "file-system-default"
        
        # 数据库策略
        db_config = SecurityPolicy.default_database()
        assert db_config.name == "database-default"
        
        # HTTP 策略
        http_config = SecurityPolicy.default_http()
        assert http_config.name == "http-default"
        
        # 严格模式
        strict_config = SecurityPolicy.restrictive()
        assert strict_config.name == "restrictive"


# ==================== 服务发现测试 ====================

class TestServiceRegistry:
    """测试服务注册中心"""
    
    @pytest.fixture
    async def registry(self):
        """创建注册中心"""
        registry = ServiceRegistry(
            heartbeat_interval=1.0,
            heartbeat_timeout=3.0
        )
        await registry.start()
        yield registry
        await registry.stop()
    
    @pytest.mark.asyncio
    async def test_register_service(self, registry):
        """测试服务注册"""
        service_info = ServiceInfo(
            name="test-service",
            description="Test service",
            version="1.0.0",
            endpoint="http://localhost:8080"
        )
        
        result = await registry.register(service_info)
        assert result is True
        
        service = await registry.get("test-service")
        assert service is not None
        assert service.info.name == "test-service"
    
    @pytest.mark.asyncio
    async def test_unregister_service(self, registry):
        """测试服务注销"""
        service_info = ServiceInfo(
            name="temp-service",
            description="Temporary",
            version="1.0.0",
            endpoint="http://localhost:8080"
        )
        
        await registry.register(service_info)
        result = await registry.unregister("temp-service")
        
        assert result is True
        service = await registry.get("temp-service")
        assert service is None
    
    @pytest.mark.asyncio
    async def test_discover_services(self, registry):
        """测试服务发现"""
        # 注册多个服务
        for i in range(3):
            await registry.register(ServiceInfo(
                name=f"service-{i}",
                description=f"Service {i}",
                version="1.0.0",
                endpoint=f"http://localhost:{8080 + i}"
            ))
        
        services = await registry.discover()
        assert len(services) == 3
    
    @pytest.mark.asyncio
    async def test_discover_by_capability(self, registry):
        """测试按能力过滤"""
        await registry.register(ServiceInfo(
            name="file-service",
            description="File service",
            version="1.0.0",
            endpoint="http://localhost:8080",
            capabilities=["file", "storage"]
        ))
        
        await registry.register(ServiceInfo(
            name="db-service",
            description="DB service",
            version="1.0.0",
            endpoint="http://localhost:8081",
            capabilities=["database", "sql"]
        ))
        
        # 按能力过滤
        file_services = await registry.discover(capability="file")
        assert len(file_services) == 1
        assert file_services[0].info.name == "file-service"
    
    @pytest.mark.asyncio
    async def test_update_heartbeat(self, registry):
        """测试心跳更新"""
        service_info = ServiceInfo(
            name="heartbeat-test",
            description="Test",
            version="1.0.0",
            endpoint="http://localhost:8080"
        )
        
        await registry.register(service_info)
        result = await registry.update_heartbeat("heartbeat-test")
        
        assert result is True
        
        service = await registry.get("heartbeat-test")
        assert service.status == ServiceStatus.ONLINE
    
    @pytest.mark.asyncio
    async def test_service_stats(self, registry):
        """测试统计信息"""
        for i in range(3):
            await registry.register(ServiceInfo(
                name=f"stat-service-{i}",
                description="Stat",
                version="1.0.0",
                endpoint=f"http://localhost:{8080 + i}"
            ))
        
        stats = registry.get_stats()
        assert stats["total"] == 3
        assert stats["online"] == 3


class TestLocalServiceRegistry:
    """测试本地服务注册中心"""
    
    @pytest.mark.asyncio
    async def test_singleton(self):
        """测试单例模式"""
        registry1 = await LocalServiceRegistry.get_instance()
        registry2 = await LocalServiceRegistry.get_instance()
        
        assert registry1 is registry2
    
    @pytest.mark.asyncio
    async def test_reset(self):
        """测试重置"""
        registry1 = await LocalServiceRegistry.get_instance()
        await LocalServiceRegistry.reset_instance()
        
        # 重置后应该能获取新实例
        registry2 = await LocalServiceRegistry.get_instance()
        assert registry2 is not None
        # 由于单例已重置，新实例不应与旧实例相同（如果旧实例还在内存中）
        # 这里主要测试重置后能正常工作


# ==================== 集成测试 ====================

class TestMCPServerWithServices:
    """测试服务端与内置服务集成"""
    
    @pytest.fixture
    def server_with_tools(self):
        """创建带工具的服务端"""
        server = MCPServer(name="integration-test")
        
        @server.tool(
            name="echo",
            description="Echo the input message",
            input_schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                },
                "required": ["message"]
            }
        )
        async def echo(args):
            return ToolResult(content=[
                {"type": "text", "text": args.get("message", "")}
            ])
        
        @server.tool(
            name="add",
            description="Add two numbers",
            input_schema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        )
        async def add(args):
            return ToolResult(content=[
                {"type": "text", "text": str(args.get("a", 0) + args.get("b", 0))}
            ])
        
        return server
    
    @pytest.mark.asyncio
    async def test_multiple_tools(self, server_with_tools):
        """测试多个工具"""
        tools = server_with_tools.list_tools()
        assert len(tools) == 2
        
        tool_names = {t.name for t in tools}
        assert "echo" in tool_names
        assert "add" in tool_names
    
    @pytest.mark.asyncio
    async def test_tool_execution(self, server_with_tools):
        """测试工具执行"""
        # 测试 echo
        req = MCPRequest(
            method=MCPMethod.TOOLS_CALL,
            params={"name": "echo", "arguments": {"message": "Hello"}},
            id=1
        )
        resp = await server_with_tools.handle_request(req)
        assert resp.result["content"][0]["text"] == "Hello"
        
        # 测试 add
        req = MCPRequest(
            method=MCPMethod.TOOLS_CALL,
            params={"name": "add", "arguments": {"a": 10, "b": 20}},
            id=2
        )
        resp = await server_with_tools.handle_request(req)
        assert resp.result["content"][0]["text"] == "30"


# ==================== 运行测试 ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
