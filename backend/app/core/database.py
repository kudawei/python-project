"""
数据库连接与会话管理模块
使用 SQLAlchemy 创建引擎和会话工厂，提供 FastAPI 依赖注入的数据库会话。
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

from app.core.config import settings

# 创建数据库引擎，设置连接池参数
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,         # 连接池大小
    max_overflow=20,      # 最大溢出连接数
    pool_recycle=3600,    # 连接回收时间(秒)
    echo=False,           # 生产环境关闭SQL日志
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类，所有 Model 继承此基类
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI 依赖注入函数
    为每个请求提供独立的数据库会话，请求结束后自动关闭。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
