"""
FastAPI 应用入口
配置 CORS、注册路由、初始化数据库表。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, search, recommend, workbench, dashboard

# 导入所有模型以确保 SQLAlchemy 能发现并创建表
import app.models  # noqa: F401

# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="基于Python的考研院校数据检索与智能推荐系统后端API",
    version="1.0.0",
)

# 配置 CORS 中间件，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册各模块路由
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(search.router, prefix=settings.API_PREFIX)
app.include_router(recommend.router, prefix=settings.API_PREFIX)
app.include_router(workbench.router, prefix=settings.API_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_PREFIX)


@app.on_event("startup")
def on_startup():
    """应用启动时自动创建数据库表（如果不存在）"""
    Base.metadata.create_all(bind=engine)


@app.get("/", summary="健康检查")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}
