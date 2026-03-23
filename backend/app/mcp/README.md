# MCP 集成模块使用指南

## 概述

MCP (Model Context Protocol) 集成模块提供了完整的 MCP 协议实现，包括：

- **MCP 客户端**：调用外部 MCP 服务
- **MCP 服务端**：提供工具和服务
- **服务发现**：注册和发现 MCP 服务
- **安全沙箱**：权限控制和资源隔离
- **内置服务**：文件系统、数据库、HTTP 客户端

## 快速开始

### 1. 创建 MCP 服务端

```python
from app.mcp import MCPServer, ToolResult

# 创建服务端
server = MCPServer(
    name="my-service",
    version="1.0.0",
    description="My MCP Service"
)

# 使用装饰器注册工具
@server.tool(
    name="echo",
    description="Echo back the input message",
    input_schema={
        "type": "object",
        "properties": {
            "message": {"type": "string", "description": "Message to echo"}
        },
        "required": ["message"]
    }
)
async def echo_handler(args: dict) -> ToolResult:
    message = args.get("message", "")
    return ToolResult(content=[{"type": "text", "text": message}])

# 挂载到 FastAPI
from fastapi import FastAPI
app = FastAPI()
server.mount(app, "/mcp")

# 启动服务
# uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. 使用 MCP 客户端

```python
from app.mcp import MCPClient

async with MCPClient("http://localhost:8000/mcp") as client:
    # 初始化连接
    await client.initialize()
    
    # 列出可用工具
    tools = await client.list_tools()
    for tool in tools:
        print(f"Tool: {tool.name} - {tool.description}")
    
    # 调用工具
    result = await client.call_tool(
        name="echo",
        arguments={"message": "Hello, World!"}
    )
    
    if result.is_error:
        print(f"Error: {result.error_message}")
    else:
        print(f"Result: {result.content[0]['text']}")
```

### 3. 使用内置服务

#### 文件系统服务

```python
from app.mcp import FileSystemService, MCPServer

# 创建文件系统服务（限制访问 /tmp 目录）
file_service = FileSystemService(
    allowed_roots=["/tmp", "/workspace"],
    max_file_size_mb=10,
    max_read_lines=10000
)

# 注册到服务端
server = MCPServer(name="workagent")
file_service.register(server)

# 可用工具：
# - file_read: 读取文件
# - file_write: 写入文件
# - file_delete: 删除文件
# - file_exists: 检查文件是否存在
# - file_info: 获取文件信息
# - list_directory: 列出目录内容
# - create_directory: 创建目录
# - copy_file: 复制文件
# - move_file: 移动文件
# - search_files: 搜索文件
```

#### 数据库服务

```python
from app.mcp import DatabaseService

# 创建数据库服务（只读模式）
db_service = DatabaseService(
    allowed_databases=["/tmp/workagent.db"],
    read_only=True,
    max_result_rows=1000
)

db_service.register(server)

# 可用工具：
# - db_query: 执行 SELECT 查询
# - db_list_tables: 列出所有表
# - db_describe_table: 获取表结构
# - db_execute: 执行写操作（需要非只读模式）
# - db_transaction: 执行事务
```

#### HTTP 客户端服务

```python
from app.mcp import HTTPClientService

# 创建 HTTP 服务（限制访问外部 API）
http_service = HTTPClientService(
    allowed_hosts=["api.example.com", "*.google.com"],
    denied_hosts=["192.168.*", "10.*"],  # 拒绝内网
    max_response_size_mb=10
)

http_service.register(server)

# 可用工具：
# - http_get: GET 请求
# - http_post: POST 请求
# - http_put: PUT 请求
# - http_delete: DELETE 请求
# - http_patch: PATCH 请求
# - http_request: 自定义请求
```

### 4. 服务发现

```python
from app.mcp import LocalServiceRegistry, ServiceInfo

# 获取本地注册中心（单例）
registry = await LocalServiceRegistry.get_instance()

# 注册服务
service_info = ServiceInfo(
    name="file-service",
    description="File System Service",
    version="1.0.0",
    endpoint="http://localhost:8000/mcp",
    capabilities=["file", "storage"],
    tools=file_service.get_tools()
)
await registry.register(service_info)

# 发现服务
services = await registry.discover()
for service in services:
    print(f"Service: {service.info.name}")

# 按能力过滤
file_services = await registry.discover(capability="file")

# 查找特定工具
result = await registry.find_tool("file_read")
if result:
    service_name, tool_def = result
    print(f"Tool 'file_read' provided by {service_name}")
```

### 5. 安全沙箱

```python
from app.mcp import (
    SandboxConfig,
    SandboxedExecutor,
    PermissionRule,
    PermissionLevel,
    ResourceType,
    SecurityPolicy
)

# 使用预定义策略
config = SecurityPolicy.default_file_system()

# 或自定义配置
config = SandboxConfig(
    name="custom",
    allowed_resources=[
        PermissionRule(
            resource_type=ResourceType.FILE,
            resource_pattern="/tmp/*",
            level=PermissionLevel.FULL,
            description="Allow full access to /tmp"
        )
    ],
    denied_resources=[
        PermissionRule(
            resource_type=ResourceType.FILE,
            resource_pattern="/etc/*",
            level=PermissionLevel.NONE,
            description="Deny /etc access"
        )
    ],
    max_execution_time=30.0,
    max_memory_mb=512
)

# 创建执行器
executor = SandboxedExecutor(config)

# 在沙箱中执行工具
async def my_tool(args: dict):
    # 工具实现
    return ToolResult(content=[{"type": "text", "text": "OK"}])

result = await executor.execute(
    tool_name="my_tool",
    handler=my_tool,
    arguments={"key": "value"}
)
```

## MCP 协议方法

### 初始化
- `initialize` - 初始化连接
- `initialized` - 初始化完成通知

### 工具
- `tools/list` - 列出可用工具
- `tools/call` - 调用工具

### 资源
- `resources/list` - 列出可用资源
- `resources/read` - 读取资源

### 服务发现
- `discovery/register` - 注册服务
- `discovery/unregister` - 注销服务
- `discovery/list` - 列出服务

### 其他
- `ping` - 心跳检测

## 请求/响应格式

### 请求
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "echo",
    "arguments": {"message": "Hello"}
  },
  "id": 1
}
```

### 成功响应
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {"type": "text", "text": "Hello"}
    ]
  },
  "id": 1
}
```

### 错误响应
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32601,
    "message": "Method not found"
  },
  "id": 1
}
```

## 错误代码

| 代码 | 含义 |
|------|------|
| -32700 | 解析错误 |
| -32600 | 无效请求 |
| -32601 | 方法不存在 |
| -32602 | 无效参数 |
| -32603 | 内部错误 |
| -32000 ~ -32099 | 服务器错误 |

## 最佳实践

### 1. 工具设计
- 使用清晰的工具名称和描述
- 定义完整的输入 JSON Schema
- 处理所有可能的错误情况
- 返回结构化的结果

### 2. 安全配置
- 始终使用沙箱限制资源访问
- 遵循最小权限原则
- 为不同服务使用不同的安全策略
- 记录所有敏感操作

### 3. 性能优化
- 设置合理的超时时间
- 限制响应大小
- 使用连接池管理客户端
- 定期清理临时资源

### 4. 错误处理
- 捕获并记录所有异常
- 返回有意义的错误信息
- 不泄露敏感信息
- 使用 ToolResult.is_error 标记错误

## 运行测试

```bash
# 运行所有 MCP 测试
cd workagent/backend
python3 -m pytest tests/test_mcp.py -v

# 运行服务测试
python3 -m pytest tests/test_mcp_services.py -v

# 运行特定测试
python3 -m pytest tests/test_mcp.py::TestMCPServer -v
```

## 文件结构

```
app/mcp/
├── __init__.py          # 模块导出
├── types.py             # 类型定义
├── client.py            # MCP 客户端
├── server.py            # MCP 服务端
├── discovery.py         # 服务发现
├── sandbox.py           # 安全沙箱
└── services/            # 内置服务
    ├── __init__.py
    ├── file_system.py   # 文件系统服务
    ├── database.py      # 数据库服务
    └── http_client.py   # HTTP 客户端服务

tests/
├── test_mcp.py          # 核心模块测试
└── test_mcp_services.py # 服务测试
```

## 示例项目

查看 `tests/` 目录中的测试文件获取完整的使用示例。
