# 天工前端 - React + TypeScript

天工项目的 Web 界面，基于 React 19 + TypeScript + Vite 6 构建。

## 技术栈

- **框架**: React 19 + TypeScript
- **构建工具**: Vite 6
- **路由**: React Router v7
- **状态管理**: Zustand 5
- **UI 组件**: shadcn/ui + TailwindCSS 3
- **数据请求**: Axios + TanStack Query
- **实时通信**: WebSocket

## 快速开始

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
# 复制环境变量文件
cp .env.example .env

# 启动开发服务器
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

### 代码检查

```bash
npm run lint
```

## 项目结构

```
frontend/
├── src/
│   ├── components/     # React 组件
│   │   ├── ui/        # shadcn/ui 基础组件
│   │   └── layout.tsx # 布局组件
│   ├── pages/         # 页面组件
│   ├── stores/        # Zustand 状态管理
│   ├── utils/         # 工具函数
│   ├── hooks/         # 自定义 Hooks
│   └── lib/           # 库工具
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## 核心页面

| 页面 | 路由 | 功能 |
|------|------|------|
| 仪表盘 | `/` | 项目概览、统计信息 |
| 项目列表 | `/projects` | 项目管理 |
| 项目详情 | `/projects/:id` | 项目详情、Agent 管理 |
| Agent | `/agents` | Agent 配置 |
| 知识库 | `/knowledge` | 文档管理 |
| 设置 | `/settings` | 系统配置 |

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `VITE_API_URL` | 后端 API 地址 | `http://localhost:8000` |
| `VITE_WS_URL` | WebSocket 地址 | `ws://localhost:8000/ws` |

## 开发规范

- 使用函数式组件和 Hooks
- 所有组件使用 TypeScript
- 遵循 ESLint 规则
- 组件文件使用 `.tsx` 扩展名
- 工具函数使用 `.ts` 扩展名

## License

MIT
