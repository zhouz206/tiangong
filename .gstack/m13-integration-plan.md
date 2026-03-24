# M13 全流程集成验证计划

**阶段**: gstack Test → Ship
**目标**: 验证端到端流程完整性
**验收标准**: 所有核心流程通过

---

## 验证范围

### 1. 后端集成验证
- [ ] Agent 系统端到端测试
- [ ] 工作流引擎完整流程
- [ ] 知识库 CRUD 操作
- [ ] MCP 服务调用
- [ ] 项目跟踪日志

### 2. 前端集成验证
- [ ] 项目创建 → 执行 → 完成 全流程
- [ ] Agent 配置 → 任务分配 → 结果查看
- [ ] 知识库上传 → 搜索 → 删除
- [ ] 仪表盘数据实时更新

### 3. API 集成验证
- [ ] 所有 REST 端点响应正常
- [ ] 错误处理符合预期
- [ ] 认证/授权机制有效

### 4. 构建与部署验证
- [ ] Docker 构建成功
- [ ] docker-compose 启动正常
- [ ] 生产构建无错误

---

## 执行步骤

### Step 1: 后端集成测试
```bash
cd backend
pytest tests/integration/ -v --tb=short
```

### Step 2: 前端 E2E 检查
```bash
cd frontend
npm run build
npm test -- --run
```

### Step 3: API 健康检查
```bash
# 启动后端后执行
curl http://localhost:8000/health
curl http://localhost:8000/api/projects
curl http://localhost:8000/api/agents
```

### Step 4: Docker 验证
```bash
cd docker
docker-compose config
docker-compose build
```

---

## 验收报告

生成 `M13_INTEGRATION_REPORT.md` 包含：
- 测试结果汇总
- 通过的流程列表
- 发现的问题（如有）
- 发布建议

---

*创建时间：2026-03-25*
