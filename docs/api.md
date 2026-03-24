# API 文档

## 基础信息

**Base URL**: `http://localhost:8000`

**API 文档**: `http://localhost:8000/docs` (Swagger UI)

## 端点列表

### 项目跟踪

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/tracking/project/{id}/status` | 获取项目状态 |
| POST | `/api/tracking/milestone/{id}/progress` | 更新里程碑进度 |
| GET | `/api/tracking/task/{id}/logs` | 获取任务日志 |
| POST | `/api/tracking/task/{id}/log` | 创建任务日志 |

### MCP

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/mcp/tools` | 获取工具列表 |
| POST | `/api/mcp/tools/{name}/call` | 调用工具 |

### 知识库

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/knowledge/search` | 搜索知识 |
| POST | `/api/knowledge/documents` | 添加文档 |

## 请求/响应示例

### 获取项目状态

**请求**:
```http
GET /api/tracking/project/project-123/status
```

**响应**:
```json
{
  "project": {
    "id": "project-123",
    "name": "SaaS 应用开发",
    "progress": 75,
    "phase": "executing",
    "status": "active"
  },
  "milestones": [
    {
      "id": "m1",
      "name": "M1 核心引擎",
      "progress": 100,
      "status": "completed"
    }
  ]
}
```

### 调用 MCP 工具

**请求**:
```http
POST /api/mcp/tools/file_read/call
Content-Type: application/json

{
  "path": "/path/to/file.txt"
}
```

**响应**:
```json
{
  "success": true,
  "output": {
    "content": "文件内容..."
  }
}
```
