# 前端开发

## 快速开始

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:3000

### 构建

```bash
npm run build
```

### 测试

```bash
npm test
```

## 技术栈

- React 19
- TypeScript 5
- Vite 6
- TailwindCSS 3
- Zustand (状态管理)
- React Router 7

## 目录结构

```
frontend/
├── src/
│   ├── components/  # 组件
│   ├── pages/       # 页面
│   ├── stores/      # 状态管理
│   ├── utils/       # 工具函数
│   ├── App.tsx      # 应用入口
│   └── main.tsx     # React 入口
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## 核心页面

1. **仪表盘** (`/`) - 项目概览、统计卡片
2. **项目列表** (`/projects`) - 创建、筛选、搜索
3. **项目详情** (`/projects/:id`) - 任务流、Agent 状态
4. **Agent** (`/agents`) - 8 个 Agent 角色
5. **知识库** (`/knowledge`) - 文档浏览、搜索
6. **设置** (`/settings`) - 主题、API、模型配置

## 响应式设计

- 移动端：320px - 767px
- 平板：768px - 1023px
- 桌面：1024px+

## 深色模式

使用 `class="dark"` 切换深色模式。
