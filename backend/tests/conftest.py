"""
Pytest 配置文件

提供全局的 pytest 配置和 fixture。
"""
import pytest
import sys
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
