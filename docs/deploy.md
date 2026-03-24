# 天工 (TianGong) 部署指南

> 生产环境部署完整指南

## 📖 目录

1. [前提条件](#前提条件)
2. [Docker 部署](#docker-部署)
3. [手动部署](#手动部署)
4. [生产环境配置](#生产环境配置)
5. [监控与日志](#监控与日志)
6. [备份与恢复](#备份与恢复)
7. [故障排查](#故障排查)

---

## 前提条件

### 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 2 核 | 4 核+ |
| 内存 | 4GB | 8GB+ |
| 存储 | 10GB | 50GB+ |
| 操作系统 | Ubuntu 20.04 / macOS 12+ | Ubuntu 22.04 |

### 软件要求

- Docker 20.10+
- Docker Compose 2.0+
- Git

### 网络要求

- 开放端口：80 (HTTP), 443 (HTTPS), 8000 (后端 API)
- 域名（可选，用于生产环境）
- SSL 证书（推荐）

---

## Docker 部署

### 快速部署

```bash
# 1. 克隆项目
git clone https://github.com/zhouz206/tiangong.git
cd tiangong

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 API Key 等

# 3. 启动服务
docker-compose up -d

# 4. 查看状态
docker-compose ps

# 5. 查看日志
docker-compose logs -f
```

### 配置文件

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite+aiosqlite:////app/data/tiangong.db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped
```

**.env.example**:
```bash
# API Keys
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
DASHSCOPE_API_KEY=your-dashscope-key

# 数据库
DATABASE_URL=sqlite+aiosqlite:///data/tiangong.db

# 其他配置
LOG_LEVEL=info
```

### 服务管理

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart

# 重启单个服务
docker-compose restart backend

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh
```

---

## 手动部署

### 后端部署

```bash
# 1. 安装 Python 3.9+
python3 --version

# 2. 创建虚拟环境
cd backend
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
export DATABASE_URL="sqlite+aiosqlite:///data/tiangong.db"
export OPENAI_API_KEY="your-key"

# 5. 初始化数据库
python -c "from app.core.database import init_db; init_db()"

# 6. 启动服务（开发环境）
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 7. 启动服务（生产环境，使用 Gunicorn）
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 前端部署

```bash
# 1. 安装 Node.js 18+
node --version

# 2. 安装依赖
cd frontend
npm install

# 3. 构建生产版本
npm run build

# 4. 部署到 Web 服务器（如 nginx）
# 构建产物在 dist/ 目录
```

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name tiangong.example.com;

    # 前端静态文件
    location / {
        root /var/www/tiangong/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket 支持
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 生产环境配置

### 环境变量

| 变量 | 说明 | 默认值 | 必填 |
|------|------|--------|------|
| `DATABASE_URL` | 数据库连接 | sqlite:///data/tiangong.db | ✅ |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - | ❌ |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 | - | ❌ |
| `DASHSCOPE_API_KEY` | 通义千问 API 密钥 | - | ❌ |
| `LOG_LEVEL` | 日志级别 | info | ❌ |
| `SECRET_KEY` | 加密密钥 | 自动生成 | ✅ |

### 安全建议

1. **使用 HTTPS**
   ```bash
   # 使用 Let's Encrypt 获取免费 SSL 证书
   sudo certbot --nginx -d tiangong.example.com
   ```

2. **配置防火墙**
   ```bash
   # 只开放必要端口
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

3. **定期更新依赖**
   ```bash
   # 后端
   pip install --upgrade -r requirements.txt
   
   # 前端
   npm update
   ```

4. **限制 API 访问**
   ```nginx
   # Nginx 速率限制
   limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
   
   location /api {
       limit_req zone=api burst=20 nodelay;
       proxy_pass http://localhost:8000;
   }
   ```

---

## 监控与日志

### 日志配置

**后端日志**:
```bash
# 查看实时日志
docker-compose logs -f backend

# 查看最近 100 行
docker-compose logs --tail=100 backend

# 导出日志
docker-compose logs backend > backend.log
```

**前端日志**:
```bash
docker-compose logs -f frontend
```

### 健康检查

```bash
# 检查后端健康
curl http://localhost:8000/health

# 检查前端
curl http://localhost:3000

# 检查 API 文档
curl http://localhost:8000/docs
```

### 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| CPU 使用率 | 后端容器 CPU | >80% |
| 内存使用率 | 后端容器内存 | >90% |
| 磁盘使用率 | 数据目录 | >85% |
| API 响应时间 | 平均响应时间 | >2s |
| 错误率 | HTTP 5xx 错误 | >1% |

---

## 备份与恢复

### 数据备份

```bash
# 1. 停止服务
docker-compose down

# 2. 备份数据目录
tar -czf tiangong-backup-$(date +%Y%m%d).tar.gz data/

# 3. 备份到远程服务器
scp tiangong-backup-*.tar.gz user@backup-server:/backups/

# 4. 启动服务
docker-compose up -d
```

### 数据恢复

```bash
# 1. 停止服务
docker-compose down

# 2. 恢复数据
tar -xzf tiangong-backup-20260324.tar.gz

# 3. 启动服务
docker-compose up -d
```

### 自动备份脚本

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/tiangong"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据
cd /opt/tiangong
tar -czf $BACKUP_DIR/tiangong-$DATE.tar.gz data/

# 删除 7 天前的备份
find $BACKUP_DIR -name "tiangong-*.tar.gz" -mtime +7 -delete

echo "Backup completed: tiangong-$DATE.tar.gz"
```

**配置 cron**:
```bash
# 每天凌晨 2 点备份
0 2 * * * /opt/tiangong/backup.sh
```

---

## 故障排查

### 常见问题

#### 1. 后端无法启动

```bash
# 查看日志
docker-compose logs backend

# 检查端口占用
lsof -i :8000

# 检查数据库
ls -la data/

# 重新启动
docker-compose restart backend
```

#### 2. 前端无法访问

```bash
# 查看日志
docker-compose logs frontend

# 检查构建
docker-compose exec frontend ls /usr/share/nginx/html

# 重新构建
docker-compose build frontend
docker-compose up -d frontend
```

#### 3. 数据库错误

```bash
# 检查数据库文件
ls -la data/tiangong.db

# 备份并重建
cp data/tiangong.db data/tiangong.db.backup
rm data/tiangong.db
docker-compose restart backend
```

#### 4. API 调用失败

```bash
# 检查 API Key 配置
docker-compose exec backend env | grep API_KEY

# 测试 API
curl http://localhost:8000/health

# 查看后端日志
docker-compose logs -f backend | grep ERROR
```

### 联系支持

- GitHub Issues: https://github.com/zhouz206/tiangong/issues
- 邮箱：support@tiangong.ai

---

*最后更新：2026-03-24*
