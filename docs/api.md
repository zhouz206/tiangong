# 天工 (TianGong) API 文档

> 完整的 REST API 参考

## 📖 目录

1. [基础信息](#基础信息)
2. [认证](#认证)
3. [项目 API](#项目-api)
4. [Agent API](#agent-api)
5. [知识库 API](#知识库-api)
6. [跟踪 API](#跟踪-api)
7. [MCP API](#mcp-api)
8. [错误处理](#错误处理)

---

## 基础信息

**Base URL**: `http://localhost:8000`

**API 文档**: `http://localhost:8000/docs` (Swagger UI)

**数据格式**: JSON

**字符编码**: UTF-8

---

## 认证

### API Key 认证

```http
Authorization: Bearer YOUR_API_KEY
```

### 获取 API Key

```bash
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

---

## 项目 API

### 获取项目列表

```http
GET /api/projects
```

**响应**:
```json
{
  "projects": [
    {
      "id": "project-123",
      "name": "SaaS 应用开发",
      "description": "构建一个现代化的 SaaS 应用",
      "progress": 75,
      "phase": "executing",
      "status": "active",
      "created_at": "2026-03-24T10:00:00Z"
    }
  ],
  "total": 1
}
```

### 获取单个项目

```http
GET /api/projects/{project_id}
```

**响应**:
```json
{
  "id": "project-123",
  "name": "SaaS 应用开发",
  "description": "构建一个现代化的 SaaS 应用",
  "progress": 75,
  "phase": "executing",
  "status": "active",
  "milestones": [
    {
      "id": "m1",
      "name": "M1 核心引擎",
      "progress": 100,
      "status": "completed"
    }
  ],
  "tasks": [
    {
      "id": "task-1",
      "title": "需求分析",
      "status": "completed",
      "assignee": "项目经理"
    }
  ]
}
```

### 创建项目

```http
POST /api/projects
Content-Type: application/json

{
  "name": "新项目",
  "description": "项目描述",
  "template": "software"  // software, content, analysis
}
```

**响应**:
```json
{
  "id": "project-456",
  "name": "新项目",
  "status": "created"
}
```

### 更新项目

```http
PUT /api/projects/{project_id}
Content-Type: application/json

{
  "name": "更新后的名称",
  "description": "更新后的描述"
}
```

### 删除项目

```http
DELETE /api/projects/{project_id}
```

**响应**:
```json
{
  "status": "deleted"
}
```

---

## Agent API

### 获取 Agent 列表

```http
GET /api/agents
```

**响应**:
```json
{
  "agents": [
    {
      "id": "agent-1",
      "role": "project_manager",
      "name": "项目经理 Agent",
      "status": "idle",
      "current_task": null
    },
    {
      "id": "agent-2",
      "role": "coder",
      "name": "程序员 Agent",
      "status": "working",
      "current_task": "task-123"
    }
  ]
}
```

### 获取 Agent 状态

```http
GET /api/agents/{agent_id}/status
```

**响应**:
```json
{
  "id": "agent-1",
  "role": "project_manager",
  "status": "idle",
  "current_task": null,
  "completed_tasks": 15,
  "skills": ["skill_office_hours", "skill_plan_ceo_review", "skill_retro"]
}
```

### 分配任务给 Agent

```http
POST /api/agents/{agent_id}/tasks
Content-Type: application/json

{
  "title": "任务标题",
  "description": "任务描述",
  "priority": "high",
  "due_date": "2026-03-30T00:00:00Z"
}
```

**响应**:
```json
{
  "task_id": "task-456",
  "status": "assigned"
}
```

---

## 知识库 API

### 搜索知识

```http
GET /api/knowledge/search?q=Python 编程&limit=10
```

**响应**:
```json
{
  "results": [
    {
      "id": "doc-1",
      "title": "Python 编程入门",
      "content": "Python 是一种高级编程语言...",
      "category": "技术文档",
      "tags": ["教程", "Python"],
      "score": 0.95
    }
  ],
  "total": 1
}
```

### 添加文档

```http
POST /api/knowledge/documents
Content-Type: application/json

{
  "title": "新文档",
  "content": "文档内容",
  "category": "技术文档",
  "tags": ["标签 1", "标签 2"]
}
```

**响应**:
```json
{
  "id": "doc-2",
  "status": "created"
}
```

### 获取分类列表

```http
GET /api/knowledge/categories
```

**响应**:
```json
{
  "categories": [
    {"id": "tech_doc", "name": "技术文档"},
    {"id": "product_doc", "name": "产品文档"},
    {"id": "research", "name": "研究报告"}
  ]
}
```

### 获取标签列表

```http
GET /api/knowledge/tags
```

**响应**:
```json
{
  "tags": [
    {"id": "urgent", "name": "紧急"},
    {"id": "guide", "name": "指南"},
    {"id": "template", "name": "模板"}
  ]
}
```

---

## 跟踪 API

### 获取项目状态

```http
GET /api/tracking/project/{project_id}/status
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
    },
    {
      "id": "m2",
      "name": "M2 模型集成",
      "progress": 80,
      "status": "active"
    }
  ]
}
```

### 更新里程碑进度

```http
POST /api/tracking/milestone/{milestone_id}/progress
```

**响应**:
```json
{
  "milestone_id": "m1",
  "progress": 100
}
```

### 获取任务日志

```http
GET /api/tracking/task/{task_id}/logs?limit=50
```

**响应**:
```json
{
  "logs": [
    {
      "id": "log-1",
      "action": "start",
      "content": "任务开始执行",
      "actor": "agent_coder",
      "created_at": "2026-03-24T10:00:00Z"
    },
    {
      "id": "log-2",
      "action": "progress",
      "content": "进度更新：50%",
      "actor": "agent_coder",
      "metadata": {"progress": 50},
      "created_at": "2026-03-24T11:00:00Z"
    }
  ]
}
```

### 创建任务日志

```http
POST /api/tracking/task/{task_id}/log
Content-Type: application/json

{
  "action": "complete",
  "content": "任务完成",
  "actor": "agent_coder",
  "metadata": {"output": {"result": "success"}}
}
```

**响应**:
```json
{
  "id": "log-3",
  "action": "complete"
}
```

---

## MCP API

### 获取工具列表

```http
GET /api/mcp/tools
```

**响应**:
```json
{
  "tools": [
    {
      "name": "file_read",
      "description": "读取文件内容",
      "input_schema": {
        "type": "object",
        "properties": {
          "path": {"type": "string"}
        },
        "required": ["path"]
      }
    },
    {
      "name": "db_query",
      "description": "执行 SQL 查询",
      "input_schema": {
        "type": "object",
        "properties": {
          "query": {"type": "string"}
        },
        "required": ["query"]
      }
    }
  ]
}
```

### 调用工具

```http
POST /api/mcp/tools/{tool_name}/call
Content-Type: application/json

{
  "arguments": {
    "path": "/path/to/file.txt"
  }
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

---

## 错误处理

### 错误响应格式

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "项目不存在",
    "details": {
      "project_id": "invalid-id"
    }
  }
}
```

### 常见错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|------------|------|
| `SUCCESS` | 200 | 成功 |
| `BAD_REQUEST` | 400 | 请求参数错误 |
| `UNAUTHORIZED` | 401 | 未授权 |
| `FORBIDDEN` | 403 | 禁止访问 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `CONFLICT` | 409 | 资源冲突 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |

### 错误处理示例

```python
try:
    response = requests.get('/api/projects/invalid-id')
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if response.status_code == 404:
        print("项目不存在")
    elif response.status_code == 401:
        print("未授权访问")
    else:
        print(f"错误：{e}")
```

---

## 速率限制

| 端点 | 限制 |
|------|------|
| 普通 API | 100 请求/分钟 |
| 搜索 API | 30 请求/分钟 |
| MCP 工具调用 | 60 请求/分钟 |

---

*最后更新：2026-03-24*
