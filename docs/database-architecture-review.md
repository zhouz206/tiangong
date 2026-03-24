# 天工项目数据库架构审查报告

**审查类型**: /plan-eng-review (gstack 标准流程)  
**审查日期**: 2026-03-23  
**审查人**: 墨菲斯  
**需求版本**: README-v5.0  
**文档参考**: workagent/README-v5.md

---

## 1. 执行摘要

本次审查针对天工 (TianGong) 项目的数据库架构设计进行全面评估。项目定位为**个人与小团队 AI 协作平台**，目标用户为 1-10 人的小型团队。

### 审查结论

| 评估维度 | 状态 | 说明 |
|----------|------|------|
| 需求覆盖度 | ⚠️ 待完善 | 核心 8 模型需补充 3 个关联模型 |
| 技术风险 | 🟡 中等 | 向量库选型、并发控制需验证 |
| 索引设计 | ⚠️ 待确认 | 需补充复合索引和全文索引 |
| 整体评级 | **B+** | 架构方向正确，细节需完善 |

---

## 2. 需求与架构映射分析

### 2.1 核心需求提取 (from README-v5.md)

| 需求类别 | 关键需求 | 优先级 |
|----------|----------|--------|
| **工作空间** | 单工作空间优先，支持多工作空间，三级权限 | P0 |
| **项目管理** | 四阶段工作流 (规划→执行→审查→完成) | P0 |
| **Agent 系统** | 8 个核心角色，Skill/MCP 扩展 | P0 |
| **模型管理** | 混合模型支持，智能路由 | P1 |
| **知识库** | 自动归档，语义搜索，向量存储 | P1 |
| **执行追溯** | 操作日志，成本分析 | P2 |
| **安全** | 敏感信息过滤，密钥加密 | P0 |

### 2.2 已设计模型清单

根据任务描述，已设计 8 个核心模型：

1. **User** (用户)
2. **Workspace** (工作空间，三级权限)
3. **WorkspaceMember** (成员关系)
4. **Project** (项目，4 阶段工作流)
5. **Task** (任务)
6. **Agent** (8 个核心角色)
7. **ModelConfig** (模型配置)
8. **Permission** (权限)

### 2.3 需求 - 模型覆盖矩阵

| 需求 | User | Workspace | WorkspaceMember | Project | Task | Agent | ModelConfig | Permission | 缺失 |
|------|------|-----------|-----------------|---------|------|-------|-------------|------------|------|
| 工作空间管理 | ✅ | ✅ | ✅ | | | | | ✅ | - |
| 项目生命周期 | | ✅ | | ✅ | ✅ | ✅ | | | - |
| Agent 协作 | | | | ✅ | ✅ | ✅ | | | ⚠️ |
| 模型路由 | | | | | | | ✅ | | - |
| 知识库 | | ✅ | | ✅ | | | | | 🔴 |
| 执行追溯 | ✅ | | | ✅ | ✅ | ✅ | | | 🔴 |
| 安全权限 | ✅ | ✅ | ✅ | | | | | ✅ | - |

**缺失模型识别**:
- 🔴 **KnowledgeDocument** (知识文档) - 知识库系统核心
- 🔴 **AuditLog** (审计日志) - 执行追溯系统核心
- 🔴 **AgentMessage** (Agent 消息) - Agent 协作和局部讨论

---

## 3. 模型设计审查

### 3.1 User (用户)

**职责**: 系统用户身份管理

**建议字段**:
```python
id: UUID (PK)
email: str (unique, indexed)
name: str
hashed_password: str
is_active: bool (default=True)
is_superuser: bool (default=False)
created_at: datetime
updated_at: datetime
last_login_at: datetime (nullable)
```

**审查意见**:
- ✅ 基础字段完整
- ⚠️ 需考虑 OAuth 集成 (github_id, google_id 等 nullable 字段)
- ⚠️ 需添加 `avatar_url` 字段支持头像

### 3.2 Workspace (工作空间)

**职责**: 顶级资源容器，数据隔离边界

**建议字段**:
```python
id: UUID (PK)
name: str (indexed)
description: str (nullable)
owner_id: UUID (FK → User, indexed)
slug: str (unique, indexed)  # URL 友好标识
is_active: bool (default=True)
created_at: datetime
updated_at: datetime
deleted_at: datetime (nullable, 软删除)
```

**审查意见**:
- ✅ 所有者关系明确
- ✅ 软删除支持 (deleted_at)
- ⚠️ 需添加 `settings: JSONB` 字段存储工作空间配置
- ⚠️ 需添加 `quota_limit: Integer` 支持资源配额

### 3.3 WorkspaceMember (成员关系)

**职责**: 用户与工作空间的多对多关系，权限绑定

**建议字段**:
```python
id: UUID (PK)
workspace_id: UUID (FK → Workspace, indexed)
user_id: UUID (FK → User, indexed)
role: Enum['owner', 'collaborator', 'observer'] (indexed)
joined_at: datetime
invited_by: UUID (FK → User, nullable)
is_active: bool (default=True)
unique_constraint: (workspace_id, user_id)
```

**审查意见**:
- ✅ 三级权限模型清晰 (owner/collaborator/observer)
- ✅ 联合唯一约束必要
- ⚠️ 需添加 `permissions: JSONB` 支持细粒度权限扩展
- ⚠️ 需添加索引 `(workspace_id, is_active)` 支持活跃成员查询

### 3.4 Project (项目)

**职责**: 项目生命周期管理，四阶段工作流

**建议字段**:
```python
id: UUID (PK)
workspace_id: UUID (FK → Workspace, indexed)
name: str (indexed)
description: str (nullable)
template_id: UUID (FK → Project, nullable, 自引用)
status: Enum['planning', 'executing', 'reviewing', 'completed', 'paused', 'cancelled'] (indexed)
current_phase: Enum['planning', 'executing', 'reviewing', 'completed'] (indexed)
owner_id: UUID (FK → User, indexed)
created_at: datetime
updated_at: datetime
completed_at: datetime (nullable)
deleted_at: datetime (nullable)
```

**审查意见**:
- ✅ 四阶段工作流支持 (current_phase)
- ✅ 状态管理完整 (含 paused/cancelled)
- ✅ 模板继承支持 (template_id 自引用)
- ⚠️ 需添加 `context: JSONB` 存储项目上下文 (Agent 共享)
- ⚠️ 需添加索引 `(workspace_id, status)` 支持项目列表筛选

### 3.5 Task (任务)

**职责**: 项目内具体工作单元

**建议字段**:
```python
id: UUID (PK)
project_id: UUID (FK → Project, indexed)
title: str
description: Text (nullable)
status: Enum['pending', 'in_progress', 'blocked', 'completed', 'cancelled'] (indexed)
priority: Enum['low', 'medium', 'high', 'urgent'] (indexed)
assignee_id: UUID (FK → Agent, nullable, indexed)
upstream_task_id: UUID (FK → Task, nullable, 自引用)
due_date: datetime (nullable)
started_at: datetime (nullable)
completed_at: datetime (nullable)
created_at: datetime
updated_at: datetime
```

**审查意见**:
- ✅ 状态机完整
- ✅ 优先级支持
- ✅ 简单依赖支持 (upstream_task_id)
- ⚠️ 需添加 `output: JSONB` 存储任务产出物元数据
- ⚠️ 需添加 `metadata: JSONB` 存储扩展信息
- ⚠️ 需添加索引 `(project_id, status)` 支持任务看板
- ⚠️ 需添加索引 `(assignee_id, status)` 支持 Agent 任务列表

### 3.6 Agent (Agent 配置)

**职责**: Agent 角色定义和配置

**建议字段**:
```python
id: UUID (PK)
workspace_id: UUID (FK → Workspace, indexed)
project_id: UUID (FK → Project, nullable, indexed)  # 项目级 Agent
name: str (indexed)
role: str (indexed)  # 8 个核心角色之一
description: str (nullable)
system_prompt: Text
model_config_id: UUID (FK → ModelConfig, nullable, indexed)
status: Enum['active', 'inactive', 'busy'] (indexed)
capabilities: JSONB (default=[])
skills: JSONB (default=[])  # 已启用 Skill 列表
mcp_services: JSONB (default=[])  # 已启用 MCP 服务
upstream_agents: JSONB (default=[])  # 上游 Agent IDs
downstream_agents: JSONB (default=[])  # 下游 Agent IDs
created_at: datetime
updated_at: datetime
```

**审查意见**:
- ✅ 支持工作空间级和项目级 Agent
- ✅ 能力声明支持 (JSONB)
- ✅ 协作关系配置 (upstream/downstream)
- ⚠️ 需添加 `current_task_id: UUID` 跟踪当前任务
- ⚠️ 需添加索引 `(workspace_id, role)` 支持角色筛选
- ⚠️ 需考虑 `temperature`, `max_tokens` 等模型参数是否内嵌或外引

### 3.7 ModelConfig (模型配置)

**职责**: 模型提供商配置和路由策略

**建议字段**:
```python
id: UUID (PK)
workspace_id: UUID (FK → Workspace, indexed)
name: str (indexed)
provider: Enum['openai', 'anthropic', 'qwen', 'ollama'] (indexed)
api_key_encrypted: Text (nullable)  # 加密存储
endpoint: str (nullable)  # 本地模型端点
model_name: str (indexed)
context_limit: Integer
priority: Integer (default=1, 路由优先级)
cost_per_token: Decimal (default=0.0)
is_offline: bool (default=False)
is_active: bool (default=True)
fallback_model_ids: JSONB (default=[])  # 降级模型列表
created_at: datetime
updated_at: datetime
```

**审查意见**:
- ✅ 混合模型支持 (云端 + 本地)
- ✅ 密钥加密存储
- ✅ 路由优先级支持
- ✅ 降级策略支持 (fallback_model_ids)
- ⚠️ 需添加 `rate_limit: Integer` 支持 API 限流配置
- ⚠️ 需添加索引 `(provider, is_active)` 支持路由筛选

### 3.8 Permission (权限)

**职责**: 细粒度权限定义 (可选，如三级权限足够可简化)

**建议字段**:
```python
id: UUID (PK)
workspace_id: UUID (FK → Workspace, indexed)
name: str (unique, indexed)  # 如 'workspace.read', 'project.create'
description: str
resource_type: Enum['workspace', 'project', 'task', 'agent', 'knowledge', 'audit'] (indexed)
actions: JSONB (default=['read', 'write', 'delete'])
is_system: bool (default=False)  # 系统预置权限
created_at: datetime
```

**审查意见**:
- ⚠️ **架构决策点**: 需求明确三级权限 (owner/collaborator/observer)
  - **方案 A**: 保留此表，支持未来细粒度扩展
  - **方案 B**: 移除此表，权限逻辑硬编码在 WorkspaceMember.role 中
- ✅ 如保留，设计合理
- ⚠️ 推荐**方案 B** (简化架构，符合 v5.0 轻量优先原则)

---

## 4. 缺失模型设计

### 4.1 KnowledgeDocument (知识文档) 🔴

**职责**: 知识库系统核心，支持自动归档和语义搜索

**建议字段**:
```python
id: UUID (PK)
workspace_id: UUID (FK → Workspace, indexed)
project_id: UUID (FK → Project, nullable, indexed)
task_id: UUID (FK → Task, nullable)
title: str (indexed)
content: Text
type: Enum['doc', 'discussion', 'reference', 'experience', 'code'] (indexed)
tags: JSONB (default=[])  # AI 自动标签
vector_id: str (nullable, indexed)  # ChromaDB 向量 ID
source_type: Enum['manual', 'auto_archive', 'agent_generated'] (indexed)
created_by: UUID (FK → User, indexed)
created_at: datetime
updated_at: datetime
```

**审查意见**:
- 🔴 **必须补充** - 知识库系统核心模型
- ✅ 支持多种知识类型 (v5.0 3.5.1 节)
- ✅ 向量 ID 关联 ChromaDB
- ⚠️ 需添加 `metadata: JSONB` 存储版本、来源等元数据
- ⚠️ 需添加全文索引 `(title, content)` 支持混合搜索

### 4.2 AuditLog (审计日志) 🔴

**职责**: 执行追溯系统核心，完整操作记录

**建议字段**:
```python
id: UUID (PK)
workspace_id: UUID (FK → Workspace, indexed)
actor_id: UUID (nullable, indexed)  # User 或 Agent ID
actor_type: Enum['user', 'agent'] (indexed)
action: str (indexed)  # create, modify, delete, approve
resource_type: str (indexed)  # project, task, agent
resource_id: UUID (indexed)
timestamp: datetime (indexed)
before: JSONB (nullable)  # 变更前内容
after: JSONB (nullable)  # 变更后内容
metadata: JSONB (default={})  # 附加信息 (model, tokens 等)
ip_address: str (nullable)  # 可选，安全审计
```

**审查意见**:
- 🔴 **必须补充** - 执行追溯系统核心 (v5.0 3.6 节)
- ✅ 支持用户和 Agent 操作记录
- ✅ 前后状态对比 (before/after)
- ⚠️ 需考虑分区表策略 (按时间分区，避免单表过大)
- ⚠️ 需添加索引 `(resource_type, resource_id, timestamp)` 支持追溯查询
- ⚠️ 需添加 `retention_days: Integer` 配置支持自动清理

### 4.3 AgentMessage (Agent 消息) 🔴

**职责**: Agent 间通信和局部讨论记录

**建议字段**:
```python
id: UUID (PK)
project_id: UUID (FK → Project, indexed)
task_id: UUID (FK → Task, nullable, indexed)
sender_agent_id: UUID (FK → Agent, indexed)
receiver_agent_id: UUID (FK → Agent, nullable)  # 空表示广播
content: Text
message_type: Enum['task_handoff', 'discussion', 'notification', 'result'] (indexed)
is_private: bool (default=False)  # 局部讨论标记
parent_message_id: UUID (FK → AgentMessage, nullable)  # 回复链
metadata: JSONB (default={})
created_at: datetime
```

**审查意见**:
- 🔴 **必须补充** - Agent 协作机制核心 (v5.0 3.3.4 节)
- ✅ 支持任务传递和局部讨论
- ✅ 私有消息支持 (is_private)
- ⚠️ 需添加索引 `(project_id, created_at)` 支持消息时间线
- ⚠️ 需添加 `is_read: bool` 和 `read_at: datetime` 支持已读标记

---

## 5. 技术风险识别

### 5.1 高风险 🟠

| 风险 | 描述 | 影响 | 缓解措施 |
|------|------|------|----------|
| **向量库选型** | ChromaDB 生产稳定性待验证 | 知识库功能受阻 | P0 阶段用 SQLite + 全文搜索，MVP 后再集成 ChromaDB |
| **并发控制** | SQLite 默认不支持高并发写入 | 多用户协作冲突 | 生产环境强制 MySQL，SQLite 仅用于开发/个人模式 |
| **密钥加密** | API 密钥加密存储实现复杂度高 | 安全风险 | 使用成熟库 (cryptography), 系统密钥链优先 |

### 5.2 中风险 🟡

| 风险 | 描述 | 影响 | 缓解措施 |
|------|------|------|----------|
| **JSONB 滥用** | 过度使用 JSONB 导致查询性能下降 | 系统响应慢 | 核心查询字段必须关系型，JSONB 仅用于扩展配置 |
| **软删除一致性** | 软删除导致外键约束复杂化 | 数据不一致 | 统一使用 `deleted_at`，查询时加 `WHERE deleted_at IS NULL` |
| **Agent 状态同步** | Agent 状态 (busy/inactive) 并发更新 | 任务分配冲突 | 使用乐观锁 (version 字段) 或 Redis 分布式锁 |

### 5.3 低风险 🟢

| 风险 | 描述 | 影响 | 缓解措施 |
|------|------|------|----------|
| **模型路由延迟** | 智能路由增加调用延迟 | 用户体验下降 | 路由决策缓存，异步降级 |
| **审计日志膨胀** | 日志量快速增长 | 存储成本增加 | 定期归档，冷热数据分离 |

---

## 6. 索引设计确认

### 6.1 单列索引 (必须)

| 表 | 字段 | 理由 |
|----|------|------|
| User | email | 登录查询 |
| Workspace | owner_id, slug | 工作空间查找 |
| WorkspaceMember | workspace_id, user_id, role | 权限验证 |
| Project | workspace_id, status, current_phase | 项目列表筛选 |
| Task | project_id, status, assignee_id | 任务看板 |
| Agent | workspace_id, role, status | Agent 筛选 |
| ModelConfig | workspace_id, provider, is_active | 路由筛选 |
| KnowledgeDocument | workspace_id, type, vector_id | 知识检索 |
| AuditLog | workspace_id, actor_id, timestamp, resource_id | 追溯查询 |
| AgentMessage | project_id, sender_agent_id, message_type | 消息查询 |

### 6.2 复合索引 (推荐)

| 表 | 字段组合 | 理由 |
|----|----------|------|
| WorkspaceMember | (workspace_id, is_active) | 活跃成员查询 |
| Project | (workspace_id, status, deleted_at) | 项目列表 (含筛选) |
| Task | (project_id, status, priority) | 任务看板 (含优先级) |
| Task | (assignee_id, status, updated_at) | Agent 任务列表 |
| AuditLog | (resource_type, resource_id, timestamp) | 资源追溯时间线 |
| AgentMessage | (project_id, created_at DESC) | 消息时间线 |
| KnowledgeDocument | (workspace_id, type, created_at DESC) | 知识列表 |

### 6.3 全文索引 (可选)

| 表 | 字段 | 技术 |
|----|------|------|
| User | name | SQLite FTS5 / MySQL FULLTEXT |
| Workspace | name, description | SQLite FTS5 / MySQL FULLTEXT |
| Project | name, description | SQLite FTS5 / MySQL FULLTEXT |
| Task | title, description | SQLite FTS5 / MySQL FULLTEXT |
| KnowledgeDocument | title, content | SQLite FTS5 / MySQL FULLTEXT + 向量搜索 |

---

## 7. 架构优化建议

### 7.1 立即执行 (P0)

1. **补充 3 个缺失模型**: KnowledgeDocument, AuditLog, AgentMessage
2. **简化权限模型**: 移除 Permission 表，权限逻辑内嵌到 WorkspaceMember.role
3. **添加软删除支持**: 所有核心表添加 `deleted_at` 字段
4. **添加审计字段**: 所有表添加 `created_at`, `updated_at`

### 7.2 短期优化 (P1)

1. **JSONB 规范化**: 定义 JSON Schema 验证，避免脏数据
2. **索引审查**: 基于实际查询模式调整索引
3. **分区策略**: AuditLog 按时间分区 (月/季度)
4. **外键约束**: 启用外键，设置合适的 `ON DELETE` 策略

### 7.3 长期规划 (P2)

1. **读写分离**: 审计日志和知识库查询走只读副本
2. **缓存层**: Redis 缓存热点数据 (项目状态、Agent 配置)
3. **数据归档**: 完成/取消的项目定期归档到冷存储
4. **多租户增强**: 如未来支持 SaaS，需添加 `tenant_id`

---

## 8. 最终模型清单 (11 个)

| 序号 | 模型名 | 类别 | 状态 |
|------|--------|------|------|
| 1 | User | 用户 | ✅ 已设计 |
| 2 | Workspace | 工作空间 | ✅ 已设计 |
| 3 | WorkspaceMember | 成员关系 | ✅ 已设计 |
| 4 | Project | 项目 | ✅ 已设计 |
| 5 | Task | 任务 | ✅ 已设计 |
| 6 | Agent | Agent 配置 | ✅ 已设计 |
| 7 | ModelConfig | 模型配置 | ✅ 已设计 |
| 8 | ~~Permission~~ | 权限 | ❌ 建议移除 (简化) |
| 9 | KnowledgeDocument | 知识文档 | 🔴 需补充 |
| 10 | AuditLog | 审计日志 | 🔴 需补充 |
| 11 | AgentMessage | Agent 消息 | 🔴 需补充 |

**最终推荐**: **10 个模型** (移除 Permission，补充 3 个)

---

## 9. 审查结论

### 9.1 架构评分

| 维度 | 得分 | 说明 |
|------|------|------|
| 需求覆盖 | 8/10 | 补充 3 个模型后覆盖完整 |
| 可扩展性 | 9/10 | JSONB 扩展字段设计良好 |
| 性能 | 7/10 | 索引需完善，分区策略待实施 |
| 安全性 | 8/10 | 密钥加密、审计日志支持 |
| 简洁性 | 8/10 | 移除 Permission 表后更轻量 |
| **综合** | **8.0/10** | **B+ 级架构** |

### 9.2 关键决策

1. **权限模型**: 采用简化方案 (WorkspaceMember.role)，移除 Permission 表
2. **向量库**: MVP 阶段用 SQLite FTS5，后续集成 ChromaDB
3. **数据库**: 开发用 SQLite，生产强制 MySQL
4. **软删除**: 统一使用 `deleted_at`，硬删除仅用于数据清理

### 9.3 下一步行动

1. [ ] 更新 README-v5.md 补充 3 个缺失模型说明
2. [ ] 编写 SQLAlchemy 模型代码
3. [ ] 创建 Alembic 迁移脚本
4. [ ] 编写模型单元测试
5. [ ] 性能基准测试 (索引有效性验证)

---

**审查人**: 墨菲斯 🖤  
**审查完成时间**: 2026-03-23 21:52  
**下次审查**: 模型代码实现后 (预计 2026-03-30)
