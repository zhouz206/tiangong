"""
天工项目配置
"""
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent

# 数据库配置
DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR}/data/tiangong.db"

# 确保数据目录存在
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
