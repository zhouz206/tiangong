"""
MCP Services — MCP 内置服务
"""
import os
import sqlite3
import aiohttp
from typing import Any, Dict, List, Optional


# ============ FileSystem Service ============

async def file_read(arguments: Dict) -> Dict:
    """读取文件"""
    path = arguments.get("path")
    if not path:
        return {"error": "path is required"}
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"content": content, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}


async def file_write(arguments: Dict) -> Dict:
    """写入文件"""
    path = arguments.get("path")
    content = arguments.get("content")
    
    if not path or content is None:
        return {"error": "path and content are required"}
    
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "path": path}
    except Exception as e:
        return {"error": str(e), "success": False}


async def file_list(arguments: Dict) -> Dict:
    """列出目录"""
    path = arguments.get("path", ".")
    
    try:
        items = os.listdir(path)
        return {"items": items, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}


# ============ Database Service ============

async def db_query(arguments: Dict) -> Dict:
    """SQL 查询"""
    db_path = arguments.get("db_path", ":memory:")
    query = arguments.get("query")
    
    if not query:
        return {"error": "query is required"}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        conn.commit()
        conn.close()
        
        return {
            "columns": columns,
            "rows": [dict(zip(columns, row)) for row in rows],
            "success": True
        }
    except Exception as e:
        return {"error": str(e), "success": False}


# ============ HTTP Client Service ============

async def http_request(arguments: Dict) -> Dict:
    """HTTP 请求"""
    url = arguments.get("url")
    method = arguments.get("method", "GET")
    headers = arguments.get("headers", {})
    body = arguments.get("body")
    
    if not url:
        return {"error": "url is required"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=body) as resp:
                return {
                    "status": resp.status,
                    "headers": dict(resp.headers),
                    "body": await resp.text(),
                    "success": True
                }
    except Exception as e:
        return {"error": str(e), "success": False}


# 注册工具配置

FILE_SYSTEM_TOOLS = [
    {
        "name": "file_read",
        "description": "读取文件内容",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"}
            },
            "required": ["path"]
        },
        "handler": file_read
    },
    {
        "name": "file_write",
        "description": "写入文件内容",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"},
                "content": {"type": "string", "description": "文件内容"}
            },
            "required": ["path", "content"]
        },
        "handler": file_write
    },
    {
        "name": "file_list",
        "description": "列出目录内容",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "目录路径", "default": "."}
            }
        },
        "handler": file_list
    }
]

DATABASE_TOOLS = [
    {
        "name": "db_query",
        "description": "执行 SQL 查询",
        "input_schema": {
            "type": "object",
            "properties": {
                "db_path": {"type": "string", "description": "数据库路径", "default": ":memory:"},
                "query": {"type": "string", "description": "SQL 查询语句"}
            },
            "required": ["query"]
        },
        "handler": db_query
    }
]

HTTP_TOOLS = [
    {
        "name": "http_request",
        "description": "发送 HTTP 请求",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "请求 URL"},
                "method": {"type": "string", "description": "HTTP 方法", "default": "GET"},
                "headers": {"type": "object", "description": "请求头"},
                "body": {"type": "object", "description": "请求体"}
            },
            "required": ["url"]
        },
        "handler": http_request
    }
]
