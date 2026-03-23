"""
数据库 MCP 服务

提供数据库查询和操作功能。
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import sqlite3
from contextlib import contextmanager

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


@dataclass
class DatabaseConnection:
    """数据库连接配置"""
    db_type: str  # sqlite, mysql, postgresql
    host: Optional[str] = None
    port: Optional[int] = None
    database: str = ""
    username: Optional[str] = None
    password: Optional[str] = None
    path: Optional[str] = None  # SQLite 文件路径


class DatabaseService:
    """
    数据库 MCP 服务
    
    提供安全的数据库查询功能。
    
    使用示例:
        service = DatabaseService(
            allowed_databases=["workagent.db"],
            read_only=True
        )
        server = MCPServer()
        service.register(server)
    """
    
    def __init__(
        self,
        allowed_databases: Optional[List[str]] = None,
        read_only: bool = True,
        max_query_time: float = 30.0,
        max_result_rows: int = 1000,
    ):
        """
        初始化数据库服务
        
        Args:
            allowed_databases: 允许访问的数据库列表
            read_only: 是否只读模式
            max_query_time: 最大查询时间（秒）
            max_result_rows: 最大返回行数
        """
        self.allowed_databases = allowed_databases or []
        self.read_only = read_only
        self.max_query_time = max_query_time
        self.max_result_rows = max_result_rows
        
        # 创建沙箱配置
        self.sandbox_config = self._create_sandbox_config()
        self.executor = SandboxedExecutor(self.sandbox_config)
        
        # 创建 MCP 服务端
        self.server = MCPServer(
            name="database",
            version="1.0.0",
            description="Database MCP Service",
        )
        
        # 注册工具
        self._register_tools()
    
    def _create_sandbox_config(self) -> SandboxConfig:
        """创建沙箱配置"""
        allowed_rules = []
        denied_rules = []
        
        # 添加允许的数据库
        for db in self.allowed_databases:
            allowed_rules.append(PermissionRule(
                resource_type=ResourceType.DATABASE,
                resource_pattern=db,
                level=PermissionLevel.READ if self.read_only else PermissionLevel.WRITE,
                description=f"Allow access to {db}",
            ))
        
        # 默认拒绝所有其他数据库
        denied_rules.append(PermissionRule(
            resource_type=ResourceType.DATABASE,
            resource_pattern="*",
            level=PermissionLevel.NONE,
            description="Deny all other databases",
        ))
        
        return SandboxConfig(
            name="database",
            allowed_resources=allowed_rules,
            denied_resources=denied_rules,
            max_execution_time=self.max_query_time,
        )
    
    def _register_tools(self) -> None:
        """注册工具"""
        
        @self.server.tool(
            name="db_query",
            description="Execute a SQL SELECT query",
            input_schema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Database name or path"
                    },
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query"
                    },
                    "params": {
                        "type": "array",
                        "description": "Query parameters",
                        "items": {"type": "string"}
                    }
                },
                "required": ["database", "query"]
            }
        )
        async def db_query(args: dict) -> ToolResult:
            return await self._handle_query(args)
        
        @self.server.tool(
            name="db_list_tables",
            description="List all tables in a database",
            input_schema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Database name or path"
                    }
                },
                "required": ["database"]
            }
        )
        async def db_list_tables(args: dict) -> ToolResult:
            return await self._handle_list_tables(args)
        
        @self.server.tool(
            name="db_describe_table",
            description="Get table schema/columns",
            input_schema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Database name or path"
                    },
                    "table": {
                        "type": "string",
                        "description": "Table name"
                    }
                },
                "required": ["database", "table"]
            }
        )
        async def db_describe_table(args: dict) -> ToolResult:
            return await self._handle_describe_table(args)
        
        @self.server.tool(
            name="db_execute",
            description="Execute a SQL statement (INSERT, UPDATE, DELETE, etc.)",
            input_schema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Database name or path"
                    },
                    "statement": {
                        "type": "string",
                        "description": "SQL statement"
                    },
                    "params": {
                        "type": "array",
                        "description": "Statement parameters",
                        "items": {"type": "string"}
                    }
                },
                "required": ["database", "statement"]
            }
        )
        async def db_execute(args: dict) -> ToolResult:
            return await self._handle_execute(args)
        
        @self.server.tool(
            name="db_transaction",
            description="Execute multiple SQL statements in a transaction",
            input_schema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Database name or path"
                    },
                    "statements": {
                        "type": "array",
                        "description": "SQL statements to execute",
                        "items": {"type": "string"}
                    }
                },
                "required": ["database", "statements"]
            }
        )
        async def db_transaction(args: dict) -> ToolResult:
            return await self._handle_transaction(args)
    
    def _validate_database(self, database: str) -> tuple[bool, str]:
        """
        验证数据库访问权限
        
        Returns:
            (是否允许，错误信息)
        """
        # 检查是否在允许列表中
        for allowed in self.allowed_databases:
            if database == allowed or database.endswith(f"/{allowed}"):
                return True, ""
        
        return False, f"Database not in allowed list: {self.allowed_databases}"
    
    def _validate_query(self, query: str) -> tuple[bool, str]:
        """
        验证查询语句（安全检查）
        
        Returns:
            (是否安全，错误信息)
        """
        query_upper = query.upper().strip()
        
        if self.read_only:
            # 只读模式下禁止写操作
            forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE"]
            for keyword in forbidden:
                if query_upper.startswith(keyword) or keyword in query_upper:
                    # 允许 SELECT ... INTO 等特殊情况
                    if keyword == "INSERT" and "SELECT" in query_upper:
                        continue
                    return False, f"{keyword} statements not allowed in read-only mode"
        
        # 禁止多语句执行
        if ";" in query.rstrip(";"):
            return False, "Multiple statements not allowed"
        
        return True, ""
    
    @contextmanager
    def _get_connection(self, database: str):
        """获取数据库连接"""
        conn = None
        try:
            # 目前只支持 SQLite
            conn = sqlite3.connect(database, timeout=30.0)
            conn.row_factory = sqlite3.Row
            yield conn
        finally:
            if conn:
                conn.close()
    
    async def _handle_query(self, args: dict) -> ToolResult:
        """处理查询请求"""
        database = args.get("database", "")
        query = args.get("query", "")
        params = args.get("params", [])
        
        # 验证数据库
        allowed, error = self._validate_database(database)
        if not allowed:
            return ToolResult(is_error=True, error_message=error)
        
        # 验证查询
        safe, error = self._validate_query(query)
        if not safe:
            return ToolResult(is_error=True, error_message=error)
        
        try:
            loop = asyncio.get_event_loop()
            
            def execute_query():
                with self._get_connection(database) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    
                    # 获取列名
                    columns = [description[0] for description in cursor.description]
                    
                    # 获取结果（限制行数）
                    rows = []
                    for i, row in enumerate(cursor):
                        if i >= self.max_result_rows:
                            break
                        rows.append(dict(row))
                    
                    return columns, rows
            
            columns, rows = await loop.run_in_executor(None, execute_query)
            
            # 格式化结果
            import json
            result = {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "truncated": len(rows) >= self.max_result_rows,
            }
            
            return ToolResult(content=[
                {"type": "text", "text": json.dumps(result, indent=2, default=str)}
            ])
            
        except sqlite3.Error as e:
            return ToolResult(is_error=True, error_message=f"Database error: {str(e)}")
        except Exception as e:
            return ToolResult(is_error=True, error_message=str(e))
    
    async def _handle_list_tables(self, args: dict) -> ToolResult:
        """处理表列表请求"""
        database = args.get("database", "")
        
        # 验证数据库
        allowed, error = self._validate_database(database)
        if not allowed:
            return ToolResult(is_error=True, error_message=error)
        
        try:
            loop = asyncio.get_event_loop()
            
            def list_tables():
                with self._get_connection(database) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                    )
                    return [row[0] for row in cursor.fetchall()]
            
            tables = await loop.run_in_executor(None, list_tables)
            
            import json
            return ToolResult(content=[
                {"type": "text", "text": json.dumps(tables, indent=2)}
            ])
            
        except sqlite3.Error as e:
            return ToolResult(is_error=True, error_message=f"Database error: {str(e)}")
        except Exception as e:
            return ToolResult(is_error=True, error_message=str(e))
    
    async def _handle_describe_table(self, args: dict) -> ToolResult:
        """处理表结构查询"""
        database = args.get("database", "")
        table = args.get("table", "")
        
        # 验证数据库
        allowed, error = self._validate_database(database)
        if not allowed:
            return ToolResult(is_error=True, error_message=error)
        
        try:
            loop = asyncio.get_event_loop()
            
            def describe_table():
                with self._get_connection(database) as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"PRAGMA table_info({table})")
                    
                    columns = []
                    for row in cursor.fetchall():
                        columns.append({
                            "cid": row[0],
                            "name": row[1],
                            "type": row[2],
                            "notnull": bool(row[3]),
                            "default": row[4],
                            "pk": bool(row[5]),
                        })
                    return columns
            
            columns = await loop.run_in_executor(None, describe_table)
            
            import json
            return ToolResult(content=[
                {"type": "text", "text": json.dumps(columns, indent=2)}
            ])
            
        except sqlite3.Error as e:
            return ToolResult(is_error=True, error_message=f"Database error: {str(e)}")
        except Exception as e:
            return ToolResult(is_error=True, error_message=str(e))
    
    async def _handle_execute(self, args: dict) -> ToolResult:
        """处理执行请求"""
        database = args.get("database", "")
        statement = args.get("statement", "")
        params = args.get("params", [])
        
        # 验证数据库
        allowed, error = self._validate_database(database)
        if not allowed:
            return ToolResult(is_error=True, error_message=error)
        
        # 检查写权限
        if self.read_only:
            return ToolResult(
                is_error=True,
                error_message="Write operations not allowed in read-only mode"
            )
        
        try:
            loop = asyncio.get_event_loop()
            
            def execute_statement():
                with self._get_connection(database) as conn:
                    cursor = conn.cursor()
                    cursor.execute(statement, params)
                    conn.commit()
                    
                    return {
                        "rowcount": cursor.rowcount,
                        "lastrowid": cursor.lastrowid,
                    }
            
            result = await loop.run_in_executor(None, execute_statement)
            
            import json
            return ToolResult(content=[
                {"type": "text", "text": json.dumps(result, indent=2)}
            ])
            
        except sqlite3.Error as e:
            return ToolResult(is_error=True, error_message=f"Database error: {str(e)}")
        except Exception as e:
            return ToolResult(is_error=True, error_message=str(e))
    
    async def _handle_transaction(self, args: dict) -> ToolResult:
        """处理事务请求"""
        database = args.get("database", "")
        statements = args.get("statements", [])
        
        # 验证数据库
        allowed, error = self._validate_database(database)
        if not allowed:
            return ToolResult(is_error=True, error_message=error)
        
        # 检查写权限
        if self.read_only:
            return ToolResult(
                is_error=True,
                error_message="Write operations not allowed in read-only mode"
            )
        
        if not statements:
            return ToolResult(is_error=True, error_message="No statements provided")
        
        try:
            loop = asyncio.get_event_loop()
            
            def execute_transaction():
                with self._get_connection(database) as conn:
                    cursor = conn.cursor()
                    
                    try:
                        for statement in statements:
                            cursor.execute(statement)
                        
                        conn.commit()
                        return {"success": True, "statements_executed": len(statements)}
                        
                    except Exception as e:
                        conn.rollback()
                        return {"success": False, "error": str(e)}
            
            result = await loop.run_in_executor(None, execute_transaction)
            
            import json
            return ToolResult(content=[
                {"type": "text", "text": json.dumps(result, indent=2)}
            ])
            
        except sqlite3.Error as e:
            return ToolResult(is_error=True, error_message=f"Database error: {str(e)}")
        except Exception as e:
            return ToolResult(is_error=True, error_message=str(e))
    
    def register(self, server: Optional[MCPServer] = None) -> MCPServer:
        """注册到 MCP 服务端"""
        if server:
            return server
        return self.server
    
    def get_server(self) -> MCPServer:
        """获取内置 MCP 服务端"""
        return self.server
    
    def get_tools(self) -> List[ToolDefinition]:
        """获取所有工具定义"""
        return self.server.list_tools()
