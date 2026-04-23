"""
全局配置模块
使用 Pydantic BaseSettings 管理项目配置，支持从环境变量和 .env 文件读取。
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """项目全局配置"""

    # 项目基本信息
    PROJECT_NAME: str = "考研院校数据检索与智能推荐系统"
    API_PREFIX: str = "/api"

    # 数据库配置
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "root123456"
    DB_NAME: str = "kaoyan_db"

    @property
    def DATABASE_URL(self) -> str:
        """构建 SQLAlchemy 数据库连接字符串"""
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    # JWT 认证配置
    JWT_SECRET_KEY: str = "kaoyan-recommendation-system-secret-key-2024"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # Token有效期: 24小时

    # CORS 跨域配置（开发环境允许所有来源，生产环境请按需限制）
    CORS_ORIGINS: list[str] = ["*"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# 全局单例配置对象
settings = Settings()
