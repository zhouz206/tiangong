# 天工 (TianGong) v7

**Agent 技能系统 + gstack 能力封装**

## 快速开始

### 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 运行测试

```bash
cd backend
python -m pytest tests/ -v
```

## 项目结构

```
workagent-v7/
├── backend/
│   ├── app/
│   │   ├── models/      # 数据库模型 (M1)
│   │   ├── agents/      # Agent 基类 + 技能系统 (M2)
│   │   ├── workflow/    # 工作流引擎 (M3)
│   │   ├── coordination/# 协调器 + MessageBus (M4)
│   │   ├── providers/   # 模型管理 (M5)
│   │   ├── skills/      # 技能系统 (M6)
│   │   ├── knowledge/   # 知识库 (M7)
│   │   ├── tracking/    # 项目跟踪 (M11)
│   │   └── mcp/         # MCP 协议 (M10)
│   ├── tests/           # 测试
│   ├── config.py        # 配置
│   └── requirements.txt # 依赖
└── TODO.md              # 待办事项
```

## 里程碑

| 里程碑 | 主题 | 状态 |
|--------|------|------|
| M1 | 项目骨架 + 核心模型 | ✅ 完成 |
| M2 | Agent 基类 + 技能系统 | ✅ 完成 |
| M3 | 工作流引擎 + 协调器 | ✅ 完成 |
| M4 | 协调器 + MessageBus | ✅ 完成 |
| M5-M11 | 项目骨架 | ✅ 完成 |
| M12 | 发布准备 | ⏳ 进行中 |

## 测试状态

- **M1**: 7/7 测试通过 ✅
- **M2**: 8/8 测试通过 ✅
- **M3**: 10/10 测试通过 ✅

**总计**: 25/25 测试通过

## 技术栈

- **后端**: Python 3.9 + SQLAlchemy 2.0
- **数据库**: SQLite (aiosqlite)
- **测试**: pytest + pytest-asyncio

## License

MIT
