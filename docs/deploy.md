# 部署指南

## Docker 部署（推荐）

### 前提条件

- Docker 20.10+
- Docker Compose 2.0+

### 快速部署

```bash
# 1. 克隆项目
git clone https://github.com/zhouz206/tiangong.git
cd tiangong

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

### 访问服务

- **前端**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

### 数据持久化

数据存储在 `./data` 目录：

```bash
./data/
└── tiangong.db  # SQLite 数据库
```

## 本地开发部署

### 后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

## 生产环境配置

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | 数据库连接 | `sqlite+aiosqlite:///data/tiangong.db` |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 | - |

### 安全建议

1. 使用强密码保护 API
2. 启用 HTTPS
3. 定期备份数据
4. 限制外部访问

## 故障排查

### 后端无法启动

```bash
# 查看日志
docker-compose logs backend

# 重启服务
docker-compose restart backend
```

### 前端无法访问

```bash
# 查看日志
docker-compose logs frontend

# 重建镜像
docker-compose build frontend
docker-compose up -d frontend
```

### 数据库问题

```bash
# 备份数据
cp data/tiangong.db data/tiangong.db.backup

# 重置数据库
rm data/tiangong.db
docker-compose restart backend
```
