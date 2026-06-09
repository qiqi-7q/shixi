from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MySQL配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DATABASE: str = "auto_test_platform"

    # Redis配置s
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://127.0.0.1:6379"
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = "redis123"
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 数据库连接池
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    class Config:
        env_file = ".env"


settings = Settings()
