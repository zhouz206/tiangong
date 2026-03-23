"""
知识管理员 Agent

职责:
- 知识文档管理
- 知识库维护
- 信息分类和标签
- 知识检索和推荐

集成知识库模块 (app.knowledge) 提供实际的存储和检索能力。
"""
from typing import Any, Optional

from app.core.agent import Agent, AgentCapability, TaskContext, TaskResult
from app.core.message import MessageBus

# 知识库集成
try:
    from app.knowledge import KnowledgeBase
    KNOWLEDGE_MODULE_AVAILABLE = True
except ImportError:
    KnowledgeBase = None
    KNOWLEDGE_MODULE_AVAILABLE = False


class KnowledgeManagerAgent(Agent):
    """
    知识管理员 Agent

    负责知识文档管理、知识库维护、信息分类和知识检索。
    """

    def __init__(
        self,
        agent_id: str,
        name: str = "Knowledge Manager",
        message_bus: Optional[MessageBus] = None,
        knowledge_base: Optional[KnowledgeBase] = None,
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            role="knowledge_manager",
            capabilities=[
                AgentCapability.KNOWLEDGE_MANAGEMENT,
                AgentCapability.DATA_ANALYSIS,
            ],
            message_bus=message_bus,
        )

        # 知识管理员特有配置
        self.temperature = 0.3  # 较低温度，分类需要一致性
        self.max_tokens = 4096

        # 知识库实例（注入依赖）
        self.knowledge_base = knowledge_base

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的知识管理员 Agent。

你的职责:
1. 管理和组织项目知识文档
2. 维护知识库的结构和内容
3. 对信息进行分类和打标签
4. 建立知识之间的关联
5. 支持知识检索和推荐

工作原则:
- 分类体系要清晰、一致、可扩展
- 标签要准确、简洁、有意义
- 知识要及时更新，淘汰过期内容
- 建立知识间的关联，形成知识网络
- 考虑用户检索习惯，优化可发现性

输出格式:
- 文档管理应包含：文档 ID、标题、分类、标签、版本、状态
- 分类体系应包含：类别层级、类别说明、包含规则
- 知识检索应包含：查询结果、相关性评分、推荐理由
"""

    async def execute_task(self, context: TaskContext) -> TaskResult:
        """
        执行知识管理任务

        处理任务类型:
        - document_organization: 文档组织
        - knowledge_indexing: 知识索引
        - taxonomy_management: 分类管理
        - knowledge_search: 知识检索
        - knowledge_curation: 知识整理
        """
        try:
            task_type = context.metadata.get("task_type", "general")

            if task_type == "document_organization":
                return await self._organize_documents(context)
            elif task_type == "knowledge_indexing":
                return await self._index_knowledge(context)
            elif task_type == "taxonomy_management":
                return await self._manage_taxonomy(context)
            elif task_type == "knowledge_search":
                return await self._search_knowledge(context)
            elif task_type == "knowledge_curation":
                return await self._curate_knowledge(context)
            else:
                return await self._do_general_knowledge_management(context)

        except Exception as e:
            return TaskResult(
                success=False,
                error=f"Knowledge management task failed: {str(e)}",
            )

    async def _organize_documents(self, context: TaskContext) -> TaskResult:
        """组织文档"""
        org_scope = context.task_description

        # 收集待组织文档
        documents = []
        for output in context.upstream_outputs:
            if isinstance(output, dict):
                if "document" in output:
                    documents.append(output["document"])
                if "content" in output:
                    documents.append({"content": output["content"], "title": output.get("title", "Untitled")})

        org_result = {
            "scope": org_scope,
            "documents_processed": len(documents),
            "categories_assigned": [],
            "tags_assigned": [],
            "relationships_found": [],
            "gaps_identified": [],
            "document_ids": [],
        }

        # 使用知识库模块实际组织文档
        if self.knowledge_base and KNOWLEDGE_MODULE_AVAILABLE:
            for doc in documents:
                try:
                    doc_id = self.knowledge_base.add_document(
                        title=doc.get("title", "Untitled"),
                        content=doc.get("content", ""),
                        auto_categorize=True,
                        auto_tag=True,
                    )
                    org_result["document_ids"].append(doc_id)
                except Exception as e:
                    org_result["gaps_identified"].append(f"Failed to add document: {str(e)}")

            # 获取统计信息
            stats = self.knowledge_base.get_stats()
            org_result["total_documents"] = stats.get("count", 0)
            org_result["categories"] = self.knowledge_base.get_categories()
            org_result["tags"] = self.knowledge_base.get_tags()

        return TaskResult(
            success=True,
            output=org_result,
            metadata={"km_type": "organization"},
        )

    async def _index_knowledge(self, context: TaskContext) -> TaskResult:
        """建立知识索引"""
        index_scope = context.task_description

        # 收集知识内容
        knowledge_items = []
        for output in context.upstream_outputs:
            if isinstance(output, dict) and "content" in output:
                knowledge_items.append(output)

        index_result = {
            "scope": index_scope,
            "indexed_items": [],
            "keywords_extracted": [],
            "entities_extracted": [],
            "search_keywords": {},
        }

        # 使用知识库模块建立索引
        if self.knowledge_base and KNOWLEDGE_MODULE_AVAILABLE:
            for item in knowledge_items:
                try:
                    doc_id = self.knowledge_base.add_document(
                        title=item.get("title", "Untitled"),
                        content=item.get("content", ""),
                        category=item.get("category"),
                        tags=item.get("tags"),
                        auto_categorize=not item.get("category"),
                        auto_tag=not item.get("tags"),
                    )
                    index_result["indexed_items"].append(doc_id)
                except Exception as e:
                    index_result["keywords_extracted"].append(f"Error: {str(e)}")

            # 获取所有标签作为关键词
            tags = self.knowledge_base.get_tags()
            index_result["keywords_extracted"] = [t["name"] for t in tags[:20]]

        return TaskResult(
            success=True,
            output=index_result,
            metadata={"km_type": "indexing"},
        )

    async def _manage_taxonomy(self, context: TaskContext) -> TaskResult:
        """管理分类体系"""
        taxonomy_domain = context.task_description

        # 收集现有分类信息
        existing_categories = []
        for output in context.upstream_outputs:
            if isinstance(output, dict) and "categories" in output:
                existing_categories.extend(output["categories"])

        taxonomy_result = {
            "domain": taxonomy_domain,
            "categories": [],
            "subcategories": {},
            "relationships": [],
            "changes_made": [],
            "recommended_updates": [],
        }

        # TODO: 实际实现中管理分类体系
        return TaskResult(
            success=True,
            output=taxonomy_result,
            metadata={"km_type": "taxonomy"},
        )

    async def _search_knowledge(self, context: TaskContext) -> TaskResult:
        """知识检索"""
        query = context.task_description

        # 收集检索上下文
        search_context = {}
        for output in context.upstream_outputs:
            if isinstance(output, dict):
                search_context.update(output)

        search_result = {
            "query": query,
            "results": [],
            "total_matches": 0,
            "categories_covered": [],
            "related_queries": [],
            "suggestions": [],
        }

        # 使用知识库模块实际检索
        if self.knowledge_base and KNOWLEDGE_MODULE_AVAILABLE:
            try:
                # 执行语义搜索
                category_filter = search_context.get("category")
                tags_filter = search_context.get("tags")
                limit = search_context.get("limit", 10)
                use_hybrid = search_context.get("hybrid", False)

                results = self.knowledge_base.search(
                    query=query,
                    category=category_filter,
                    tags=tags_filter,
                    limit=limit,
                    hybrid=use_hybrid,
                )

                search_result["total_matches"] = len(results)
                search_result["results"] = [
                    {
                        "id": r.document.id,
                        "title": r.document.title,
                        "content": r.document.content[:500] if r.document.content else "",
                        "category": r.document.category,
                        "tags": r.document.tags,
                        "score": r.score,
                        "highlights": r.highlights,
                        "reason": r.reason,
                    }
                    for r in results
                ]

                # 统计涉及的分类
                categories = set(r.document.category for r in results)
                search_result["categories_covered"] = list(categories)

                # 生成相关查询建议
                if results:
                    search_result["related_queries"] = [
                        f"{query} {r.document.category}" for r in results[:3]
                    ]

            except Exception as e:
                search_result["suggestions"] = [f"Search error: {str(e)}"]

        return TaskResult(
            success=True,
            output=search_result,
            metadata={"km_type": "search"},
        )

    async def _curate_knowledge(self, context: TaskContext) -> TaskResult:
        """知识整理和筛选"""
        curation_topic = context.task_description

        # 收集待整理知识
        knowledge_pool = []
        for output in context.upstream_outputs:
            if isinstance(output, dict) and "content" in output:
                knowledge_pool.append(output)

        curation_result = {
            "topic": curation_topic,
            "selected_items": [],
            "quality_scores": {},
            "relevance_scores": {},
            "summary": "",
            "recommendations": [],
            "outdated_items": [],
        }

        # 使用知识库模块进行整理
        if self.knowledge_base and KNOWLEDGE_MODULE_AVAILABLE:
            # 检索相关知识
            try:
                results = self.knowledge_base.search(
                    query=curation_topic,
                    limit=20,
                )

                curation_result["selected_items"] = [
                    {"id": r.document.id, "title": r.document.title, "score": r.score}
                    for r in results[:10]
                ]

                # 按相关性评分
                for item in curation_result["selected_items"]:
                    curation_result["relevance_scores"][item["id"]] = item["score"]
                    curation_result["quality_scores"][item["id"]] = min(1.0, item["score"] * 1.2)

                curation_result["summary"] = f"Found {len(results)} relevant items for '{curation_topic}'"

                # 识别可能过时的内容（低分结果）
                curation_result["outdated_items"] = [
                    {"id": r.document.id, "title": r.document.title, "score": r.score}
                    for r in results if r.score < 0.5
                ]

            except Exception as e:
                curation_result["recommendations"] = [f"Curation error: {str(e)}"]

        return TaskResult(
            success=True,
            output=curation_result,
            metadata={"km_type": "curation"},
        )

    async def _do_general_knowledge_management(self, context: TaskContext) -> TaskResult:
        """执行一般知识管理任务"""
        km_result = {
            "task": context.task_description,
            "actions_taken": [],
            "documents_affected": [],
            "updates_made": [],
            "summary": "",
        }

        # 使用知识库模块处理一般任务
        if self.knowledge_base and KNOWLEDGE_MODULE_AVAILABLE:
            try:
                stats = self.knowledge_base.get_stats()
                km_result["summary"] = f"Knowledge base contains {stats.get('count', 0)} documents"
                km_result["actions_taken"] = ["Retrieved knowledge base statistics"]
                km_result["updates_made"] = [f"Total documents: {stats.get('count', 0)}"]
            except Exception as e:
                km_result["actions_taken"].append(f"Error: {str(e)}")

        return TaskResult(
            success=True,
            output=km_result,
            metadata={"km_type": "general"},
        )

    def create_document_meta(
        self,
        title: str,
        content_type: str,
        category: str,
        tags: list[str],
    ) -> dict[str, Any]:
        """创建文档元数据"""
        return {
            "title": title,
            "content_type": content_type,
            "category": category,
            "tags": tags,
            "version": "1.0",
            "status": "draft",
            "created_at": None,
            "updated_at": None,
        }

    def create_category(
        self,
        name: str,
        parent: Optional[str],
        description: str,
        rules: list[str],
    ) -> dict[str, Any]:
        """创建分类"""
        return {
            "name": name,
            "parent": parent,
            "description": description,
            "rules": rules,
            "subcategories": [],
        }

    def assign_tags(
        self,
        content_id: str,
        suggested_tags: list[str],
        auto_approve: bool = False,
    ) -> dict[str, Any]:
        """分配标签"""
        return {
            "content_id": content_id,
            "suggested_tags": suggested_tags,
            "approved_tags": suggested_tags if auto_approve else [],
            "status": "approved" if auto_approve else "pending",
        }

    def link_knowledge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
    ) -> dict[str, Any]:
        """建立知识关联"""
        return {
            "source_id": source_id,
            "target_id": target_id,
            "relationship_type": relationship_type,  # related_to, depends_on, extends, etc.
            "strength": 1.0,
        }
