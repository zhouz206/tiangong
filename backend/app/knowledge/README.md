# 知识库模块 (Knowledge Base)

完整的知识库管理系统，提供向量存储、语义搜索、自动分类和归档功能。

## 功能特性

- ✅ **ChromaDB 向量存储** - 持久化向量数据库，支持高效相似度搜索
- ✅ **Sentence-BERT 嵌入** - 多语言文档嵌入生成（支持中文）
- ✅ **语义搜索** - 基于向量相似度的智能搜索，支持混合搜索
- ✅ **知识分类** - 自动分类和标签系统
- ✅ **自动归档** - 基于规则的文档自动归档

## 快速开始

### 基本使用

```python
from app.knowledge import KnowledgeBase

# 初始化知识库
kb = KnowledgeBase(
    persist_directory="./data/chroma",
    collection_name="knowledge_documents",
    embedding_model="zh",  # 中文优化模型
)

# 添加文档
doc_id = kb.add_document(
    title="Python 入门教程",
    content="Python 是一种高级编程语言...",
    category="技术文档",
    tags=["教程", "Python"],
    auto_categorize=True,  # 自动分类
    auto_tag=True,         # 自动打标签
)

# 搜索文档
results = kb.search(
    query="Python 编程基础",
    category="技术文档",
    limit=10,
    min_score=0.5,
)

for result in results:
    print(f"标题：{result.document.title}")
    print(f"分数：{result.score}")
    print(f"内容：{result.document.content[:100]}...")
    print("---")

# 混合搜索（语义 + 关键词）
results = kb.search("API 设计", hybrid=True, limit=10)
```

### 高级功能

#### 自动分类和打标签

```python
from app.knowledge import knowledge_base

# 自动分类
category = kb.auto_categorize(
    content="这是一个关于机器学习和深度学习的教程",
    title="AI 技术报告",
)
print(f"推荐分类：{category}")

# 自动打标签
tags = kb.auto_tag(
    content="紧急的 API 开发指南，包含最佳实践",
    title="API 文档",
    max_tags=5,
)
print(f"推荐标签：{tags}")
```

#### 分类和标签管理

```python
# 获取所有分类
categories = kb.get_categories()
for cat in categories:
    print(f"{cat['id']}: {cat['name']}")

# 获取所有标签
tags = kb.get_tags()
for tag in tags:
    print(f"{tag['id']}: {tag['name']} (使用{tag['usage_count']}次)")

# 创建新分类
new_cat = kb.taxonomy.create_category(
    name="最佳实践",
    description="项目最佳实践和指南",
    rules=["包含实践建议", "经过验证"],
)

# 创建新标签
new_tag = kb.taxonomy.create_tag(
    name="v2.0",
    category="版本",
)
```

#### 自动归档

```python
# 查看归档规则
rules = kb.archiver.get_rules()
for rule in rules:
    print(f"{rule.name}: {rule.condition_type} -> {rule.action}")

# 创建自定义归档规则
kb.archiver.create_rule(
    name="发布超 1 年文档",
    condition_type="age_published",
    condition_value=365,  # 天
    action="archive",
)

# 执行归档（模拟）
result = kb.run_archival(dry_run=True)
print(f"将归档 {result['archived']} 个文档")

# 执行实际归档
result = kb.run_archival(dry_run=False)

# 恢复已归档文档
kb.archiver.restore_document("doc_xxx")

# 查看归档统计
stats = kb.archiver.get_archive_stats()
print(f"总文档：{stats['total_documents']}")
print(f"已归档：{stats['archived_documents']}")
```

#### 文档管理

```python
# 获取文档
doc = kb.get_document("doc_xxx")
print(f"标题：{doc.title}")
print(f"分类：{doc.category}")
print(f"标签：{doc.tags}")
print(f"状态：{doc.status}")

# 更新文档
kb.update_document(
    "doc_xxx",
    title="新标题",
    content="新内容",
    category="新分类",
    tags=["新标签"],
)

# 删除文档
kb.delete_document("doc_xxx")
```

#### 搜索功能

```python
# 基本搜索
results = kb.search("查询文本", limit=10)

# 带过滤的搜索
results = kb.search(
    "查询文本",
    category="技术文档",
    tags=["教程", "API"],
    limit=10,
    min_score=0.6,
)

# 混合搜索（语义 + 关键词）
results = kb.search("查询文本", hybrid=True)

# 获取搜索统计
stats = kb.search_engine.get_search_stats()
print(f"总文档数：{stats['total_documents']}")
print(f"嵌入模型：{stats['embedding_model']}")
print(f"嵌入维度：{stats['embedding_dim']}")
```

## 模块结构

```
knowledge/
├── __init__.py          # 主模块，导出 KnowledgeBase
├── models.py            # 数据模型定义
├── vector_store.py      # ChromaDB 向量存储
├── embedding.py         # Sentence-BERT 嵌入服务
├── search.py            # 语义搜索引擎
├── taxonomy.py          # 分类和标签管理
├── archive.py           # 自动归档系统
├── tests/               # 单元测试
│   ├── test_models.py
│   ├── test_embedding.py
│   ├── test_vector_store.py
│   ├── test_taxonomy.py
│   └── test_archive.py
└── README.md            # 本文档
```

## 数据模型

### KnowledgeDocument
- `id`: 文档唯一标识
- `title`: 文档标题
- `content`: 文档内容
- `category`: 所属分类
- `tags`: 标签列表
- `status`: 文档状态 (draft/review/published/archived/deprecated)
- `version`: 版本号
- `embedding`: 向量嵌入
- `metadata`: 元数据
- `created_at/updated_at`: 时间戳

### Category
- `id`: 分类唯一标识
- `name`: 分类名称
- `parent`: 父分类 ID
- `description`: 分类描述
- `rules`: 分类规则

### Tag
- `id`: 标签唯一标识
- `name`: 标签名称
- `category`: 所属分类
- `usage_count`: 使用次数

## 默认分类体系

- **技术文档** - 代码、技术方案、架构设计
- **产品文档** - 需求、设计、用户手册
- **研究报告** - 调研、分析、市场报告
- **流程规范** - SOP、规范、制度
- **会议记录** - 纪要、讨论记录

## 默认标签库

- **优先级**: 紧急、重要
- **类型**: 参考资料、模板、指南、教程
- **技术**: API
- **质量**: 最佳实践

## 归档规则

- **草稿超 30 天未更新** → 自动归档
- **标记为废弃的文档** → 自动归档
- **审核中超 90 天未处理** → 发送通知

## 运行测试

```bash
# 运行所有知识库测试
cd workagent/backend
pytest tests/test_knowledge_integration.py -v

# 运行单个测试文件
pytest app/knowledge/tests/test_models.py -v
pytest app/knowledge/tests/test_embedding.py -v
pytest app/knowledge/tests/test_vector_store.py -v
pytest app/knowledge/tests/test_taxonomy.py -v
pytest app/knowledge/tests/test_archive.py -v

# 运行特定测试
pytest app/knowledge/tests/test_models.py::TestKnowledgeDocument::test_create_document -v

# 带覆盖率报告
pytest app/knowledge/tests/ --cov=app.knowledge --cov-report=html
```

## 依赖

```txt
chromadb==0.4.22
sentence-transformers==2.3.1
```

## 性能优化建议

1. **批量嵌入**: 使用 `embed_texts()` 而非多次调用 `embed_text()`
2. **搜索限制**: 设置合理的 `limit` 和 `min_score` 减少返回结果
3. **分类过滤**: 搜索时指定 `category` 缩小范围
4. **定期归档**: 定期运行归档保持知识库精简
5. **持久化**: 使用本地持久化避免重复加载

## 常见问题

### Q: 如何更换嵌入模型？
```python
kb = KnowledgeBase(embedding_model="en")  # 英文优化
kb = KnowledgeBase(embedding_model="large")  # 更大更准确
kb = KnowledgeBase(embedding_model="paraphrase-multilingual-mpnet-base-v2")  # 自定义
```

### Q: 如何备份知识库？
直接备份 `persist_directory` 目录即可，ChromaDB 会自动持久化所有数据。

### Q: 如何重置知识库？
```python
kb.vector_store.reset_collection()
```

### Q: 中文支持如何？
默认使用 `paraphrase-multilingual-MiniLM-L12-v2` 模型，对中文有良好支持。

## 扩展开发

### 添加新的归档规则类型

在 `archive.py` 的 `_check_condition` 方法中添加新的条件类型：

```python
elif condition_type == "custom_condition":
    # 自定义逻辑
    return some_check(metadata, condition_value)
```

### 添加新的分类

```python
kb.taxonomy.create_category(
    name="新分类",
    description="描述",
    rules=["规则 1", "规则 2"],
)
```

### 自定义自动分类逻辑

扩展 `TaxonomyManager` 类，重写 `auto_categorize` 方法，可以集成机器学习模型进行更智能的分类。

## 许可证

内部使用
