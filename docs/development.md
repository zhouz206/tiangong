# 天工 (TianGong) 开发文档

> 开发者指南 — 从零开始构建 AI 协作平台

## 📖 目录

1. [项目架构](#项目架构)
2. [开发环境](#开发环境)
3. [代码规范](#代码规范)
4. [测试指南](#测试指南)
5. [调试技巧](#调试技巧)
6. [常见问题](#常见问题)

---

## 项目架构

### 目录结构

```
workagent-v7/
├── backend/              # 后端服务
│   ├── app/
│   │   ├── models/      # 数据库模型 (M1)
│   │   ├── agents/      # Agent 系统 (M2, M5)
│   │   ├── skills/      # 技能系统 (M6)
│   │   ├── workflow/    # 工作流引擎 (M3, M8)
│   │   ├── coordination/# 协调器 (M4)
│   │   ├── providers/   # 模型提供商 (M2 补充)
│   │   ├── knowledge/   # 知识库 (M7)
│   │   ├── mcp/         # MCP 协议 (M10)
│   │   ├── tracking/    # 项目跟踪 (M11)
│   │   └── tracking/    # 项目跟踪 (M11)
│   ├── tests/           # 测试
│   └── requirements.txt # 依赖
├── frontend/            # 前端应用 (M9)
│   ├── src/
│   │   ├── components/  # UI 组件
│   │   ├── pages/       # 页面
│   │   ├── stores/      # 状态管理
│   │   └── utils/       # 工具函数
│   └── package.json
├── docker/              # Docker 配置 (M12)
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── docker-compose.yml
│   └── nginx.conf
└── docs/                # 文档
```

### 模块依赖关系

```
┌─────────────────┐
│   Frontend      │
│   (M9 Web 界面)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     API         │
│   (FastAPI)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Workflow       │
│  Engine (M3,M8) │
└────────┬────────┘
         │
    ┌────┴────┬────────────┬──────────┐
    ▼         ▼            ▼          ▼
┌───────┐ ┌───────┐ ┌──────────┐ ┌────────┐
│Agents │ │Models │ │Knowledge │ │  MCP   │
│ (M5)  │ │ (M2)  │ │   (M7)   │ │ (M10)  │
└───────┘ └───────┘ └──────────┘ └────────┘
```

---

## 开发环境

### 后端开发

```bash
# 1. 创建虚拟环境
cd backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装开发依赖
pip install pytest pytest-asyncio pytest-cov black flake8

# 4. 启动开发服务器
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. 访问 API 文档
open http://localhost:8000/docs
```

### 前端开发

```bash
# 1. 安装依赖
cd frontend
npm install

# 2. 启动开发服务器
npm run dev

# 3. 访问前端
open http://localhost:3000

# 4. 运行测试
npm test
```

### Docker 开发

```bash
# 1. 构建镜像
docker-compose build

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

---

## 代码规范

### Python 规范

```python
# 1. 类型注解
def greet(name: str) -> str:
    return f"Hello, {name}"

# 2. 文档字符串
class Agent:
    """Agent 基类"""
    
    async def execute_task(self, context: TaskContext) -> TaskResult:
        """
        执行任务
        
        Args:
            context: 任务上下文
            
        Returns:
            TaskResult: 执行结果
        """
        pass

# 3. 异常处理
try:
    result = await api_call()
except APIError as e:
    logger.error(f"API call failed: {e}")
    raise
```

### TypeScript 规范

```typescript
// 1. 类型定义
interface Project {
  id: string;
  name: string;
  progress: number;
}

// 2. React 组件
interface Props {
  title: string;
  onClick: () => void;
}

const Button: React.FC<Props> = ({ title, onClick }) => {
  return <button onClick={onClick}>{title}</button>;
};

// 3. 异步操作
const fetchData = async (): Promise<Data> => {
  const response = await api.get('/data');
  return response.data;
};
```

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 变量 | snake_case (Python), camelCase (TS) | `user_name`, `userName` |
| 类 | PascalCase | `ProjectManager`, `AgentCard` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRIES`, `API_BASE` |
| 函数 | snake_case (Python), camelCase (TS) | `get_user`, `getUser` |

---

## 测试指南

### 运行测试

```bash
# 后端测试
cd backend
pytest tests/ -v                    # 运行所有测试
pytest tests/ -v --cov=app          # 带覆盖率
pytest tests/models/ -v             # 测试特定模块

# 前端测试
cd frontend
npm test                            # 运行测试
npm test -- --coverage              # 带覆盖率
```

### 编写测试

```python
# 后端测试示例
import pytest
from app.models.project import Project

def test_create_project(db_session):
    """测试创建项目"""
    project = Project(name="测试项目")
    db_session.add(project)
    db_session.commit()
    
    assert project.id is not None
    assert project.name == "测试项目"
```

```typescript
// 前端测试示例
import { test, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Dashboard from './pages/dashboard';

test('Dashboard 渲染统计卡片', () => {
  render(<Dashboard />);
  
  expect(screen.getByText('仪表盘')).toBeInTheDocument();
  expect(screen.getByText('总项目数')).toBeInTheDocument();
});
```

### 测试覆盖率目标

| 模块 | 目标覆盖率 |
|------|------------|
| 核心模型 | ≥80% |
| Agent 系统 | ≥80% |
| 工作流引擎 | ≥80% |
| API 层 | ≥70% |
| 前端组件 | ≥70% |

---

## 调试技巧

### 后端调试

```python
# 1. 使用 logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Processing {count} items")

# 2. 使用断点
import pdb; pdb.set_trace()

# 3. 使用 FastAPI 调试模式
# uvicorn app.main:app --reload --log-level debug
```

### 前端调试

```typescript
// 1. 使用 React DevTools
// 安装浏览器扩展

// 2. 使用 console.log
console.log('State:', state);

// 3. 使用 React Query DevTools
// import { ReactQueryDevtools } from 'react-query/devtools'
```

### 常见问题排查

```bash
# 1. 后端无法启动
# 检查端口占用
lsof -i :8000

# 2. 前端构建失败
# 清理 node_modules
rm -rf node_modules package-lock.json
npm install

# 3. Docker 无法启动
# 查看日志
docker-compose logs backend
docker-compose logs frontend
```

---

## 常见问题

### Q: 如何添加新的 Agent 角色？

A: 在 `backend/app/agents/roles/` 目录下创建新文件：

```python
# backend/app/agents/roles/new_role.py
from ..agent import Agent, TaskContext, TaskResult

class NewRoleAgent(Agent):
    @property
    def role(self) -> str:
        return "new_role"
    
    async def _default_execute(self, context: TaskContext) -> TaskResult:
        # 实现逻辑
        return TaskResult(success=True, output={})
```

### Q: 如何添加新的 MCP 服务？

A: 在 `backend/app/mcp/services/` 目录下创建新文件：

```python
# backend/app/mcp/services/new_service.py
async def new_tool(arguments: dict) -> dict:
    """新工具"""
    # 实现逻辑
    return {"result": "success"}
```

### Q: 如何配置新的模型提供商？

A: 在 `backend/app/providers/` 目录下创建新文件：

```python
# backend/app/providers/new_provider.py
from .base import ModelProvider, ModelResponse, ModelConfig

class NewProvider(ModelProvider):
    @property
    def name(self) -> str:
        return "new_provider"
    
    async def chat(self, messages, config) -> ModelResponse:
        # 实现逻辑
        return ModelResponse(content="...", model=config.model_name)
```

### Q: 如何部署到生产环境？

A: 参考 [部署指南](deploy.md)

---

*最后更新：2026-03-24*
