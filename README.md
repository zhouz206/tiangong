# 天工 (TianGong) - 个人与小团队 AI 协作平台

> 取自《天工开物》—— 巧夺天工，协作共创

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)

打造一个轻量、高效、可扩展的 AI 协作平台，让个人开发者和小团队能够像拥有专业团队一样完成复杂工作。

## 🎯 核心特性

- **多 Agent 协作** - 8 个核心 Agent 角色，像专业团队一样协作
- **混合模型支持** - 云端 + 本地模型，智能路由，成本最优
- **能力扩展** - Skill 动态加载，MCP 工具调用
- **知识管理** - 自动归档，语义搜索，知识关联
- **执行追溯** - 完整操作日志，成本分析
- **安全协作** - 三级权限，敏感信息过滤

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (可选)

### 方法一：Docker Compose（推荐）

```bash
# 克隆仓库
git clone https://github.com/yourusername/tiangong.git
cd tiangong

# 启动服务
docker-compose up -d

# 访问应用
# 前端：http://localhost:3000
# 后端 API: http://localhost:8000
# API 文档：http://localhost:8000/docs
```

### 方法二：本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd frontend
npm install
npm run dev
```

## 📦 项目结构

```
tiangong/
├── backend/            # 后端服务
│   ├── app/
│   │   ├── core/       # 核心引擎
│   │   ├── models/     # 数据库模型
│   │   ├── providers/  # 模型提供商
│   │   ├── agents/     # Agent 角色
│   │   ├── knowledge/  # 知识库
│   │   ├── skills/     # Skill 系统
│   │   ├── mcp/        # MCP 协议
│   │   ├── security/   # 安全模块
│   │   ├── api/        # API 路由
│   │   └── utils/      # 工具函数
│   ├── tests/          # 测试
│   └── requirements.txt
├── frontend/           # 前端应用
│   ├── src/
│   │   ├── components/ # 组件
│   │   ├── pages/      # 页面
│   │   ├── stores/     # 状态
│   │   └── utils/      # 工具
│   └── package.json
├── docker/             # 容器化部署
│   └── docker-compose.yml
├── docs/               # 文档
└── README.md
```

## 🎯 开发里程碑

| 里程碑 | 名称 | 周数 | 状态 |
|--------|------|------|------|
| M1 | 核心引擎就绪 | Week 1-3 | 🟡 进行中 |
| M2 | 模型集成完成 | Week 4-5 | ⚪ 未开始 |
| M3 | Agent 能力就绪 | Week 6-7 | ⚪ 未开始 |
| M4 | 知识库与追溯 | Week 8-9 | ⚪ 未开始 |
| M5 | Web 界面完成 | Week 10-12 | ⚪ 未开始 |
| M6 | 发布就绪 | Week 13-14 | ⚪ 未开始 |

## 📚 文档

- [架构设计](docs/architecture.md)
- [快速开始](docs/getting-started.md)
- [Agent 开发指南](docs/agent-guide.md)
- [API 参考](docs/api-reference.md)
- [安全指南](docs/security-guide.md)

## 🤝 贡献

我们欢迎各种形式的贡献！

### 开发流程

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/xxx`)
3. 提交更改 (`git commit -am 'Add some feature'`)
4. 推送到分支 (`git push origin feature/xxx`)
5. 创建 Pull Request

### 代码规范

- **Python**: PEP 8, type hints
- **前端**: TypeScript, React hooks
- **测试覆盖率**: ≥ 70%
- **文档**: 同步更新

## 📄 开源协议

MIT License - 允许商业使用、修改、分发

## 📞 联系方式

- **Issues**: [GitHub Issues](https://github.com/yourusername/tiangong/issues)
- **讨论**: [GitHub Discussions](https://github.com/yourusername/tiangong/discussions)

---

*天工 (TianGong) - 让 AI 像专业团队一样为你工作*