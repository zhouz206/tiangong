"""
知识库 MCP 服务

提供通过 MCP 协议访问知识库的功能。
"""
import logging
from typing import Optional, List, Any

from ..types import ToolDefinition, ToolResult
from ..server import MCPServer
from ..sandbox import (
    SandboxConfig,
    SandboxedExecutor,
    PermissionRule,
    PermissionLevel,
    ResourceType,
)

logger = logging.getLogger(__name__)


class KnowledgeService:
    """
    知识库 MCP 服务

    提供安全的知识库访问功能，包括：
    - 文档添加
    - 文档搜索
    - 文档管理
    - 分类和标签管理

    使用示例:
        service = KnowledgeService(knowledge_base=kb)
        server = MCPServer()
        service.register(server)
    """

    def __init__(
        self,
        knowledge_base: Any = None,
        allowed_categories: Optional[List[str]] = None,
        max_search_results: int = 20,
    ):
        """
        初始化知识库服务

        Args:
            knowledge_base: KnowledgeBase 实例
            allowed_categories: 允许访问的分类列表
            max_search_results: 最大搜索结果数量
        """
        self.knowledge_base = knowledge_base
        self.allowed_categories = allowed_categories
        self.max_search_results = max_search_results

        # 创建 MCP 服务端
        self.server = MCPServer(
            name="knowledge-service",
            version="1.0.0",
            description="Knowledge Base MCP Service",
        )

        # 创建沙箱配置
        self.sandbox_config = self._create_sandbox_config()
        self.executor = SandboxedExecutor(self.sandbox_config)

        # 注册工具
        self._register_tools()

    def _create_sandbox_config(self) -> SandboxConfig:
        """创建沙箱配置"""
        allowed_rules = [
            PermissionRule(
                resource_type=ResourceType.FILE,
                resource_pattern="*/data/chroma/*",
                level=PermissionLevel.READ,
                description="Allow knowledge base access",
            ),
        ]

        denied_rules = [
            PermissionRule(
                resource_type=ResourceType.FILE,
                resource_pattern="*/.env*",
                level=PermissionLevel.NONE,
                description="Deny environment file access",
            ),
            PermissionRule(
                resource_type=ResourceType.FILE,
                resource_pattern="*/secrets/*",
                level=PermissionLevel.NONE,
                description="Deny secrets access",
            ),
        ]

        return SandboxConfig(
            name="knowledge-service",
            allowed_resources=allowed_rules,
            denied_resources=denied_rules,
            max_execution_time=30.0,
        )

    def _register_tools(self) -> None:
        """注册工具"""

        @self.server.tool(
            name="knowledge_add_document",
            description="Add a document to the knowledge base",
            input_schema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Document title"
                    },
                    "content": {
                        "type": "string",
                        "description": "Document content"
                    },
                    "category": {
                        "type": "string",
                        "description": "Document category (optional, auto-categorized if not provided)"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Document tags (optional, auto-tagged if not provided)"
                    },
                    "auto_categorize": {
                        "type": "boolean",
                        "description": "Whether to auto-categorize",
                        "default": True
                    },
                    "auto_tag": {
                        "type": "boolean",
                        "description": "Whether to auto-tag",
                        "default": True
                    }
                },
                "required": ["title", "content"]
            }
        )
        async def knowledge_add_document(args: dict) -> ToolResult:
            return await self._handle_add_document(args)

        @self.server.tool(
            name="knowledge_search",
            description="Search the knowledge base",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return",
                        "default": 10
                    },
                    "min_score": {
                        "type": "number",
                        "description": "Minimum relevance score",
                        "default": 0.5
                    },
                    "hybrid": {
                        "type": "boolean",
                        "description": "Use hybrid search (semantic + keyword)",
                        "default": False
                    }
                },
                "required": ["query"]
            }
        )
        async def knowledge_search(args: dict) -> ToolResult:
            return await self._handle_search(args)

        @self.server.tool(
            name="knowledge_get_document",
            description="Get a document by ID",
            input_schema={
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "Document ID"
                    }
                },
                "required": ["doc_id"]
            }
        )
        async def knowledge_get_document(args: dict) -> ToolResult:
            return await self._handle_get_document(args)

        @self.server.tool(
            name="knowledge_update_document",
            description="Update an existing document",
            input_schema={
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "Document ID"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title"
                    },
                    "content": {
                        "type": "string",
                        "description": "New content"
                    },
                    "category": {
                        "type": "string",
                        "description": "New category"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "New tags"
                    }
                },
                "required": ["doc_id"]
            }
        )
        async def knowledge_update_document(args: dict) -> ToolResult:
            return await self._handle_update_document(args)

        @self.server.tool(
            name="knowledge_delete_document",
            description="Delete a document",
            input_schema={
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "Document ID"
                    }
                },
                "required": ["doc_id"]
            }
        )
        async def knowledge_delete_document(args: dict) -> ToolResult:
            return await self._handle_delete_document(args)

        @self.server.tool(
            name="knowledge_list_categories",
            description="List all categories",
            input_schema={
                "type": "object",
                "properties": {}
            }
        )
        async def knowledge_list_categories(args: dict) -> ToolResult:
            return await self._handle_list_categories(args)

        @self.server.tool(
            name="knowledge_list_tags",
            description="List all tags",
            input_schema={
                "type": "object",
                "properties": {}
            }
        )
        async def knowledge_list_tags(args: dict) -> ToolResult:
            return await self._handle_list_tags(args)

        @self.server.tool(
            name="knowledge_get_stats",
            description="Get knowledge base statistics",
            input_schema={
                "type": "object",
                "properties": {}
            }
        )
        async def knowledge_get_stats(args: dict) -> ToolResult:
            return await self._handle_get_stats(args)

        @self.server.tool(
            name="knowledge_suggest_related",
            description="Suggest related documents for a given document ID",
            input_schema={
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "Document ID to find related documents"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum suggestions",
                        "default": 5
                    }
                },
                "required": ["doc_id"]
            }
        )
        async def knowledge_suggest_related(args: dict) -> ToolResult:
            return await self._handle_suggest_related(args)

    async def _handle_add_document(self, args: dict) -> ToolResult:
        """处理添加文档"""
        if not self.knowledge_base:
            return ToolResult(
                is_error=True,
                error_message="Knowledge base not initialized",
            )

        try:
            title = args.get("title", "")
            content = args.get("content", "")
            category = args.get("category")
            tags = args.get("tags")
            auto_categorize = args.get("auto_categorize", True)
            auto_tag = args.get("auto_tag", True)

            doc_id = self.knowledge_base.add_document(
                title=title,
                content=content,
                category=category,
                tags=tags,
                auto_categorize=auto_categorize,
                auto_tag=auto_tag,
            )

            return ToolResult(content=[
                {"type": "text", "text": f"Document added successfully. ID: {doc_id}"}
            ])

        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return ToolResult(
                is_error=True,
                error_message=f"Failed to add document: {str(e)}",
            )

    async def _handle_search(self, args: dict) -> ToolResult:
        """处理搜索"""
        if not self.knowledge_base:
            return ToolResult(
                is_error=True,
                error_message="Knowledge base not initialized",
            )

        try:
            query = args.get("query", "")
            category = args.get("category")
            tags = args.get("tags")
            limit = min(args.get("limit", 10), self.max_search_results)
            min_score = args.get("min_score", 0.5)
            hybrid = args.get("hybrid", False)

            results = self.knowledge_base.search(
                query=query,
                category=category,
                tags=tags,
                limit=limit,
                min_score=min_score,
                hybrid=hybrid,
            )

            # 格式化结果
            formatted_results = []
            for r in results:
                formatted_results.append({
                    "id": r.document.id,
                    "title": r.document.title,
                    "content": r.document.content[:300] if r.document.content else "",
                    "category": r.document.category,
                    "tags": r.document.tags,
                    "score": r.score,
                    "highlights": r.highlights,
                    "reason": r.reason,
                })

            import json
            return ToolResult(content=[
                {"type": "text", "text": json.dumps({
                    "query": query,
                    "total_results": len(results),
                    "results": formatted_results,
                }, indent=2, ensure_ascii=False)}
            ])

        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            return ToolResult(
                is_error=True,
                error_message=f"Search failed: {str(e)}",
            )

    async def _handle_get_document(self, args: dict) -> ToolResult:
        """处理获取文档"""
        if not self.knowledge_base:
            return ToolResult(
                is_error=True,
                error_message="Knowledge base not initialized",
            )

        try:
            doc_id = args.get("doc_id", "")
            doc = self.knowledge_base.get_document(doc_id)

            if not doc:
                return ToolResult(
                    is_error=True,
                    error_message=f"Document not found: {doc_id}",
                )

            import json
            return ToolResult(content=[
                {"type": "text", "text": json.dumps({
                    "id": doc.id,
                    "title": doc.title,
                    "content": doc.content,
                    "category": doc.category,
                    "tags": doc.tags,
                    "status": doc.status,
                    "version": doc.version,
                }, indent=2, ensure_ascii=False)}
            ])

        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return ToolResult(
                is_error=True,
                error_message=f"Failed to get document: {str(e)}",
            )

    async def _handle_update_document(self, args: dict) -> ToolResult:
        """处理更新文档"""
        if not self.knowledge_base:
            return ToolResult(
                is_error=True,
                error_message="Knowledge base not initialized",
            )

        try:
            doc_id = args.get("doc_id", "")

            success = self.knowledge_base.update_document(
                doc_id=doc_id,
                title=args.get("title"),
                content=args.get("content"),
                category=args.get("category"),
                tags=args.get("tags"),
            )

            if success:
                return ToolResult(content=[
                    {"type": "text", "text": f"Document updated successfully: {doc_id}"}
                ])
            else:
                return ToolResult(
                    is_error=True,
                    error_message=f"Failed to update document: {doc_id}",
                )

        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return ToolResult(
                is_error=True,
                error_message=f"Failed to update document: {str(e)}",
            )

    async def _handle_delete_document(self, args: dict) -> ToolResult:
        """处理删除文档"""
        if not self.knowledge_base:
            return ToolResult(
                is_error=True,
                error_message="Knowledge base not initialized",
            )

        try:
            doc_id = args.get("doc_id", "")

            success = self.knowledge_base.delete_document(doc_id)

            if success:
                return ToolResult(content=[
                    {"type": "text", "text": f"Document deleted successfully: {doc_id}"}
                ])
            else:
                return ToolResult(
                    is_error=True,
                    error_message=f"Failed to delete document: {doc_id}",
                )

        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return ToolResult(
                is_error=True,
                error_message=f"Failed to delete document: {str(e)}",
            )

    async def _handle_list_categories(self, args: dict) -> ToolResult:
        """处理列出分类"""
        if not self.knowledge_base:
            return ToolResult(
                is_error=True,
                error_message="Knowledge base not initialized",
            )

        try:
            categories = self.knowledge_base.get_categories()

            import json
            return ToolResult(content=[
                {"type": "text", "text": json.dumps({
                    "total_categories": len(categories),
                    "categories": categories,
                }, indent=2, ensure_ascii=False)}
            ])

        except Exception as e:
            logger.error(f"Error listing categories: {e}")
            return ToolResult(
                is_error=True,
                error_message=f"Failed to list categories: {str(e)}",
            )

    async def _handle_list_tags(self, args: dict) -> ToolResult:
        """处理列出标签"""
        if not self.knowledge_base:
            return ToolResult(
                is_error=True,
                error_message="Knowledge base not initialized",
            )

        try:
            tags = self.knowledge_base.get_tags()

            import json
            return ToolResult(content=[
                {"type": "text", "text": json.dumps({
                    "total_tags": len(tags),
                    "tags": tags,
                }, indent=2, ensure_ascii=False)}
            ])

        except Exception as e:
            logger.error(f"Error listing tags: {e}")
            return ToolResult(
                is_error=True,
                error_message=f"Failed to list tags: {str(e)}",
            )

    async def _handle_get_stats(self, args: dict) -> ToolResult:
        """处理获取统计信息"""
        if not self.knowledge_base:
            return ToolResult(
                is_error=True,
                error_message="Knowledge base not initialized",
            )

        try:
            stats = self.knowledge_base.get_stats()

            import json
            return ToolResult(content=[
                {"type": "text", "text": json.dumps(stats, indent=2, ensure_ascii=False)}
            ])

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return ToolResult(
                is_error=True,
                error_message=f"Failed to get stats: {str(e)}",
            )

    async def _handle_suggest_related(self, args: dict) -> ToolResult:
        """处理推荐相关文档"""
        if not self.knowledge_base:
            return ToolResult(
                is_error=True,
                error_message="Knowledge base not initialized",
            )

        try:
            doc_id = args.get("doc_id", "")
            limit = args.get("limit", 5)

            # 使用搜索引擎的推荐功能
            from app.knowledge.search import semantic_search

            results = semantic_search.suggest_related(doc_id, limit)

            formatted_results = [
                {
                    "id": r.document.id,
                    "title": r.document.title,
                    "category": r.document.category,
                    "score": r.score,
                }
                for r in results
            ]

            import json
            return ToolResult(content=[
                {"type": "text", "text": json.dumps({
                    "source_doc_id": doc_id,
                    "related_documents": formatted_results,
                }, indent=2, ensure_ascii=False)}
            ])

        except Exception as e:
            logger.error(f"Error suggesting related: {e}")
            return ToolResult(
                is_error=True,
                error_message=f"Failed to suggest related: {str(e)}",
            )

    def register(self, server: Optional[MCPServer] = None) -> MCPServer:
        """
        注册到 MCP 服务端

        Args:
            server: 目标服务端，None 则使用内置服务端

        Returns:
            MCP 服务端
        """
        if server:
            # 将所有工具注册到目标服务端
            for tool in self.server.list_tools():
                pass  # TODO: 实现工具迁移
            return server
        return self.server

    def get_server(self) -> MCPServer:
        """获取内置 MCP 服务端"""
        return self.server

    def get_tools(self) -> List[ToolDefinition]:
        """获取所有工具定义"""
        return self.server.list_tools()
