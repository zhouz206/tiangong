# 天工 (TianGong) v1.0

> 让 AI 像专业团队一样为你工作

## 🎯 项目简介

天工是一个轻量、高效、可扩展的 AI 协作平台，让个人开发者和小团队能够像拥有专业团队一样完成复杂工作。

**核心特性：**
- 🤖 **多 Agent 协作** — 8 个预置角色（项目经理、程序员、设计师等）
- 🎯 **gstack 流程内建** — Think→Plan→Build→Review→Test→Ship→Reflect
- 🔧 **MCP 能力扩展** — 文件系统、数据库、HTTP 客户端
- 📚 **知识库** — ChromaDB 向量存储、语义搜索
- 📊 **项目跟踪** — 实时进度、执行日志
- 🌐 **Web 界面** — React + TypeScript、响应式设计

## 🚀 快速开始

### 方式一：Docker（推荐）

```bash
# 克隆项目
git clone https://github.com/zhouz206/tiangong.git
cd tiangong

# 启动服务
docker-compose up -d

# 访问前端
open http://localhost:3000

# 访问后端 API
open http://localhost:8000/docs
```

### 方式二：本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

## 📦 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: SQLite + SQLAlchemy
- **向量库**: ChromaDB
- **AI 模型**: OpenAI / Anthropic / Qwen / Ollama

### 前端
- **框架**: React 19 + TypeScript 5
- **构建**: Vite 6
- **样式**: TailwindCSS 3
- **状态**: Zustand

### 部署
- **容器**: Docker + Docker Compose
- **Web 服务**: nginx

## 📖 文档

- [API 文档](docs/api.md)
- [部署指南](docs/deploy.md)
- [开发指南](docs/development.md)

## 🏆 里程碑

| 里程碑 | 主题 | 状态 |
|--------|------|------|
| M1 | 项目骨架 + 核心模型 | ✅ |
| M2 | Agent 基类 + 技能系统 | ✅ |
| M3 | 工作流引擎 + 协调器 | ✅ |
| M4 | 协调器 + MessageBus | ✅ |
| M5 | 8 个 Agent 角色 | ✅ |
| M6 | 8 个 gstack 技能 | ✅ |
| M7 | 知识库 | ✅ |
| M8 | 自动工作流编排 | ✅ |
| M9 | Web 界面 | ✅ |
| M10 | MCP 能力扩展 | ✅ |
| M11 | 项目跟踪 | ✅ |
| M12 | 发布准备 | ✅ |
| M13 | 全流程集成验证 | ✅ |

**测试覆盖**: 122/122 测试通过 (100%)

## 📄 开源协议

MIT License

---

*天工 (TianGong) - 取自《天工开物》—— 巧夺天工，协作共创*
