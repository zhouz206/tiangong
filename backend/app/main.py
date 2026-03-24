"""
天工 (TianGong) - FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, sync_engine, get_db

# 创建数据库表
Base.metadata.create_all(bind=sync_engine)

# 创建 FastAPI 应用
app = FastAPI(
    title="天工 TianGong",
    description="AI 协作平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "天工 TianGong",
        "version": "1.0.0",
        "description": "AI 协作平台"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


# TODO: 添加 API 路由
# from app.api import projects, agents, knowledge, tracking, mcp
# app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
# app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
# app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
# app.include_router(tracking.router, prefix="/api/tracking", tags=["tracking"])
# app.include_router(mcp.router, prefix="/api/mcp", tags=["mcp"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
