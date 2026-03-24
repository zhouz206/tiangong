"""
MCP 内置服务单元测试
"""
import pytest
import asyncio
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

from app.mcp.services.file_system import FileSystemService
from app.mcp.services.database import DatabaseService
from app.mcp.services.http_client import HTTPClientService
from app.mcp.types import ToolResult


# ==================== 文件系统服务测试 ====================

class TestFileSystemService:
    """测试文件系统服务"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def file_service(self, temp_dir):
        """创建文件系统服务"""
        return FileSystemService(
            allowed_roots=[temp_dir],
            max_file_size_mb=1,
            max_read_lines=1000
        )
    
    @pytest.mark.asyncio
    async def test_file_read(self, file_service, temp_dir):
        """测试文件读取"""
        # 创建测试文件
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Hello, World!")
        
        # 读取文件
        result = await file_service._handle_file_read({"path": test_file})
        
        assert result.is_error is False
        assert "Hello, World!" in result.content[0]["text"]
    
    @pytest.mark.asyncio
    async def test_file_read_not_found(self, file_service, temp_dir):
        """测试文件不存在"""
        result = await file_service._handle_file_read({
            "path": os.path.join(temp_dir, "nonexistent.txt")
        })
        
        assert result.is_error is True
        assert "not found" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_file_read_outside_root(self, file_service, temp_dir):
        """测试读取根目录外的文件"""
        result = await file_service._handle_file_read({
            "path": "/etc/passwd"
        })
        
        assert result.is_error is True
        assert "allowed roots" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_file_write(self, file_service, temp_dir):
        """测试文件写入"""
        test_file = os.path.join(temp_dir, "output.txt")
        
        result = await file_service._handle_file_write({
            "path": test_file,
            "content": "Test content"
        })
        
        assert result.is_error is False
        
        # 验证写入
        with open(test_file, "r") as f:
            content = f.read()
        assert content == "Test content"
    
    @pytest.mark.asyncio
    async def test_file_append(self, file_service, temp_dir):
        """测试文件追加"""
        test_file = os.path.join(temp_dir, "append.txt")
        
        # 先写入
        await file_service._handle_file_write({
            "path": test_file,
            "content": "Line 1\n"
        })
        
        # 追加
        result = await file_service._handle_file_write({
            "path": test_file,
            "content": "Line 2\n",
            "append": True
        })
        
        assert result.is_error is False
        
        # 验证
        with open(test_file, "r") as f:
            content = f.read()
        assert "Line 1" in content
        assert "Line 2" in content
    
    @pytest.mark.asyncio
    async def test_file_delete(self, file_service, temp_dir):
        """测试文件删除"""
        test_file = os.path.join(temp_dir, "delete.txt")
        
        # 创建文件
        with open(test_file, "w") as f:
            f.write("To be deleted")
        
        # 删除
        result = await file_service._handle_file_delete({"path": test_file})
        
        assert result.is_error is False
        assert not os.path.exists(test_file)
    
    @pytest.mark.asyncio
    async def test_file_exists(self, file_service, temp_dir):
        """测试文件存在检查"""
        test_file = os.path.join(temp_dir, "exists.txt")
        
        # 创建文件
        with open(test_file, "w") as f:
            f.write("test")
        
        # 检查存在
        result = await file_service._handle_file_exists({"path": test_file})
        assert result.content[0]["text"] == "true"
        
        # 检查不存在
        result = await file_service._handle_file_exists({
            "path": os.path.join(temp_dir, "nonexistent.txt")
        })
        assert result.content[0]["text"] == "false"
    
    @pytest.mark.asyncio
    async def test_file_info(self, file_service, temp_dir):
        """测试文件信息获取"""
        test_file = os.path.join(temp_dir, "info.txt")
        
        with open(test_file, "w") as f:
            f.write("Test content")
        
        result = await file_service._handle_file_info({"path": test_file})
        
        assert result.is_error is False
        
        info = json.loads(result.content[0]["text"])
        assert info["path"] == test_file
        assert info["size"] == 12
        assert info["is_file"] is True
    
    @pytest.mark.asyncio
    async def test_list_directory(self, file_service, temp_dir):
        """测试目录列表"""
        # 创建测试文件
        for i in range(3):
            with open(os.path.join(temp_dir, f"file{i}.txt"), "w") as f:
                f.write(f"Content {i}")
        
        result = await file_service._handle_list_directory({"path": temp_dir})
        
        assert result.is_error is False
        
        items = json.loads(result.content[0]["text"])
        assert len(items) == 3
    
    @pytest.mark.asyncio
    async def test_create_directory(self, file_service, temp_dir):
        """测试创建目录"""
        new_dir = os.path.join(temp_dir, "new_dir")
        
        result = await file_service._handle_create_directory({
            "path": new_dir
        })
        
        assert result.is_error is False
        assert os.path.isdir(new_dir)
    
    @pytest.mark.asyncio
    async def test_create_directory_with_parents(self, file_service, temp_dir):
        """测试创建多级目录"""
        new_dir = os.path.join(temp_dir, "a", "b", "c")
        
        result = await file_service._handle_create_directory({
            "path": new_dir,
            "parents": True
        })
        
        assert result.is_error is False
        assert os.path.isdir(new_dir)
    
    @pytest.mark.asyncio
    async def test_copy_file(self, file_service, temp_dir):
        """测试文件复制"""
        src = os.path.join(temp_dir, "source.txt")
        dst = os.path.join(temp_dir, "dest.txt")
        
        with open(src, "w") as f:
            f.write("Copy me")
        
        result = await file_service._handle_copy_file({
            "source": src,
            "destination": dst
        })
        
        assert result.is_error is False
        assert os.path.exists(dst)
        
        with open(dst, "r") as f:
            assert f.read() == "Copy me"
    
    @pytest.mark.asyncio
    async def test_move_file(self, file_service, temp_dir):
        """测试文件移动"""
        src = os.path.join(temp_dir, "move_src.txt")
        dst = os.path.join(temp_dir, "move_dst.txt")
        
        with open(src, "w") as f:
            f.write("Move me")
        
        result = await file_service._handle_move_file({
            "source": src,
            "destination": dst
        })
        
        assert result.is_error is False
        assert not os.path.exists(src)
        assert os.path.exists(dst)
    
    @pytest.mark.asyncio
    async def test_search_files(self, file_service, temp_dir):
        """测试文件搜索"""
        # 创建测试文件
        for ext in [".txt", ".py", ".md"]:
            with open(os.path.join(temp_dir, f"test{ext}"), "w") as f:
                f.write("test")
        
        result = await file_service._handle_search_files({
            "path": temp_dir,
            "pattern": "*.txt"
        })
        
        assert result.is_error is False
        
        matches = json.loads(result.content[0]["text"])
        assert len(matches) == 1
        assert matches[0].endswith(".txt")
    
    @pytest.mark.asyncio
    async def test_get_tools(self, file_service):
        """测试获取工具列表"""
        tools = file_service.get_tools()
        
        assert len(tools) > 0
        
        tool_names = {t.name for t in tools}
        assert "file_read" in tool_names
        assert "file_write" in tool_names
        assert "list_directory" in tool_names


# ==================== 数据库服务测试 ====================

class TestDatabaseService:
    """测试数据库服务"""
    
    @pytest.fixture
    def temp_db(self):
        """创建临时数据库"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        # 初始化测试表
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        """)
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", 
                      ("Alice", "alice@example.com"))
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", 
                      ("Bob", "bob@example.com"))
        conn.commit()
        conn.close()
        
        yield db_path
        os.unlink(db_path)
    
    @pytest.fixture
    def db_service(self, temp_db):
        """创建数据库服务"""
        return DatabaseService(
            allowed_databases=[temp_db],
            read_only=False,
            max_result_rows=100
        )
    
    @pytest.mark.asyncio
    async def test_query(self, db_service, temp_db):
        """测试查询"""
        result = await db_service._handle_query({
            "database": temp_db,
            "query": "SELECT * FROM users"
        })
        
        assert result.is_error is False
        
        data = json.loads(result.content[0]["text"])
        assert "columns" in data
        assert "rows" in data
        assert len(data["rows"]) == 2
    
    @pytest.mark.asyncio
    async def test_query_with_params(self, db_service, temp_db):
        """测试带参数查询"""
        result = await db_service._handle_query({
            "database": temp_db,
            "query": "SELECT * FROM users WHERE name = ?",
            "params": ["Alice"]
        })
        
        assert result.is_error is False
        
        data = json.loads(result.content[0]["text"])
        assert len(data["rows"]) == 1
        assert data["rows"][0]["name"] == "Alice"
    
    @pytest.mark.asyncio
    async def test_list_tables(self, db_service, temp_db):
        """测试列出表"""
        result = await db_service._handle_list_tables({
            "database": temp_db
        })
        
        assert result.is_error is False
        
        tables = json.loads(result.content[0]["text"])
        assert "users" in tables
    
    @pytest.mark.asyncio
    async def test_describe_table(self, db_service, temp_db):
        """测试表结构查询"""
        result = await db_service._handle_describe_table({
            "database": temp_db,
            "table": "users"
        })
        
        assert result.is_error is False
        
        columns = json.loads(result.content[0]["text"])
        assert len(columns) == 3
        
        column_names = [c["name"] for c in columns]
        assert "id" in column_names
        assert "name" in column_names
        assert "email" in column_names
    
    @pytest.mark.asyncio
    async def test_execute_insert(self, db_service, temp_db):
        """测试插入操作"""
        result = await db_service._handle_execute({
            "database": temp_db,
            "statement": "INSERT INTO users (name, email) VALUES (?, ?)",
            "params": ["Charlie", "charlie@example.com"]
        })
        
        assert result.is_error is False
        
        # 验证插入
        query_result = await db_service._handle_query({
            "database": temp_db,
            "query": "SELECT * FROM users WHERE name = 'Charlie'"
        })
        data = json.loads(query_result.content[0]["text"])
        assert len(data["rows"]) == 1
    
    @pytest.mark.asyncio
    async def test_read_only_mode(self, temp_db):
        """测试只读模式"""
        service = DatabaseService(
            allowed_databases=[temp_db],
            read_only=True
        )
        
        result = await service._handle_execute({
            "database": temp_db,
            "statement": "DELETE FROM users"
        })
        
        assert result.is_error is True
        assert "read-only" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_unauthorized_database(self, db_service, temp_db):
        """测试未授权数据库"""
        result = await db_service._handle_query({
            "database": "/tmp/unauthorized.db",
            "query": "SELECT 1"
        })
        
        assert result.is_error is True
        assert "allowed list" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_transaction(self, db_service, temp_db):
        """测试事务"""
        result = await db_service._handle_transaction({
            "database": temp_db,
            "statements": [
                "INSERT INTO users (name, email) VALUES ('Dave', 'dave@example.com')",
                "INSERT INTO users (name, email) VALUES ('Eve', 'eve@example.com')"
            ]
        })
        
        assert result.is_error is False
        
        # 验证
        query_result = await db_service._handle_query({
            "database": temp_db,
            "query": "SELECT COUNT(*) as count FROM users"
        })
        data = json.loads(query_result.content[0]["text"])
        assert data["rows"][0]["count"] == 4
    
    @pytest.mark.asyncio
    async def test_get_tools(self, db_service):
        """测试获取工具列表"""
        tools = db_service.get_tools()
        
        tool_names = {t.name for t in tools}
        assert "db_query" in tool_names
        assert "db_list_tables" in tool_names
        assert "db_execute" in tool_names


# ==================== HTTP 客户端服务测试 ====================

class TestHTTPClientService:
    """测试 HTTP 客户端服务"""
    
    @pytest.fixture
    def http_service(self):
        """创建 HTTP 服务"""
        return HTTPClientService(
            allowed_hosts=["*"],
            max_response_size_mb=1,
            default_timeout=10.0
        )
    
    @pytest.mark.asyncio
    async def test_validate_url(self, http_service):
        """测试 URL 验证"""
        # 有效 URL
        valid, error = http_service._validate_url("https://example.com/api")
        assert valid is True
        
        # 无效协议
        valid, error = http_service._validate_url("ftp://example.com")
        assert valid is False
        
        # 无效格式
        valid, error = http_service._validate_url("not-a-url")
        assert valid is False
    
    @pytest.mark.asyncio
    async def test_validate_method(self, http_service):
        """测试方法验证"""
        # 允许的方法
        valid, error = http_service._validate_method("GET")
        assert valid is True
        
        valid, error = http_service._validate_method("post")  # 小写
        assert valid is True
        
        # 不允许的方法
        http_service.allowed_methods = ["GET"]
        valid, error = http_service._validate_method("POST")
        assert valid is False
    
    @pytest.mark.asyncio
    async def test_host_deny_list(self):
        """测试主机拒绝列表"""
        service = HTTPClientService(
            allowed_hosts=["*"],
            denied_hosts=["internal.*", "192.168.*"]
        )
        
        valid, error = service._validate_url("http://internal.server/api")
        assert valid is False
        
        valid, error = service._validate_url("http://192.168.1.1/api")
        assert valid is False
        
        valid, error = service._validate_url("http://example.com/api")
        assert valid is True
    
    @pytest.mark.asyncio
    async def test_host_allow_list(self):
        """测试主机允许列表"""
        service = HTTPClientService(
            allowed_hosts=["api.example.com", "*.google.com"],
            denied_hosts=[]
        )
        
        valid, error = service._validate_url("http://api.example.com/v1")
        assert valid is True
        
        valid, error = service._validate_url("http://www.google.com/search")
        assert valid is True
        
        valid, error = service._validate_url("http://other.com/api")
        assert valid is False
    
    @pytest.mark.asyncio
    async def test_get_tools(self, http_service):
        """测试获取工具列表"""
        tools = http_service.get_tools()
        
        tool_names = {t.name for t in tools}
        assert "http_get" in tool_names
        assert "http_post" in tool_names
        assert "http_request" in tool_names
    
    @pytest.mark.asyncio
    async def test_cleanup(self, http_service):
        """测试清理"""
        # 创建客户端
        await http_service._get_client()
        assert http_service._client is not None
        
        # 清理
        await http_service.close()
        assert http_service._client is None or http_service._client.is_closed


# ==================== 运行测试 ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
