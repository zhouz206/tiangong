"""
Pytest 配置文件

提供全局的 pytest 配置和 fixture。
"""
import pytest
import asyncio
import sys
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# 配置 pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于异步测试"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# 导入数据库 fixture
from tests.test_models import db_session, test_user, test_workspace, test_project

__all__ = ["db_session", "test_user", "test_workspace", "test_project"]
