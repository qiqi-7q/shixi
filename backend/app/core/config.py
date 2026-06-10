from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MySQL配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "123456"
    MYSQL_DATABASE: str = "data_platform_test"

    # Redis配置s
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://127.0.0.1:6379/"
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = "redis123"
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 数据库连接池
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # 1. 邮箱配置（核心！根据你的邮箱修改）
    # 发件人邮箱
    MAIL_USERNAME: str = "1422547400@qq.com"
    # 邮箱授权码（不是登录密码！）
    MAIL_PASSWORD: str = "ryapzywouobjfggb"
    # 发件人邮箱
    MAIL_FROM: str = "1422547400@qq.com"
    # 发件人名称
    MAIL_FROM_NAME: str = "自动化测试平台官方"
    # SMTP 服务器地址
    MAIL_SERVER: str = "smtp.qq.com"
    # SMTP 端口（465 是 SSL 安全端口）
    MAIL_PORT: int = 465
    

    class Config:
        env_file = ".env"


settings = Settings()
