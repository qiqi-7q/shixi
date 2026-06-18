from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MySQL配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DATABASE: str = "data_platform_test"

    # Redis配置s
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://127.0.0.1:6379/"
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = "123456"
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 数据库连接池
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # 邮箱配置（核心！根据你的邮箱修改）
    # 发件人邮箱
    MAIL_USERNAME: str = "2634808@leapmotor.com"
    # 邮箱授权码（不是登录密码！）
    MAIL_PASSWORD: str = "Sqy123456."
    # 发件人邮箱
    MAIL_FROM: str = "shang_qingyuan@leapmotor.com"
    # 发件人名称
    MAIL_FROM_NAME: str = "自动化测试平台官方"
    # SMTP 服务器地址
    MAIL_SERVER: str = "mail.leapmotor.com"
    # 邮箱是否需要 STARTTLS 加密
    MAIL_STARTTLS: bool = True
    # 邮箱是否需要 SSL 加密
    MAIL_SSL_TLS: bool = False
    # 邮箱是否需要验证证书
    VALIDATE_CERTS: bool = True
    # 邮箱是否需要使用认证
    USE_CREDENTIALS: bool = True
    # SMTP 端口（465 是 SSL 安全端口）
    MAIL_PORT: int = 587




    # 高级搜索配置
    ADVANCED_OPERATORS_MAP: dict = {
        # 高级搜索支持的操作符（使用 SQLAlchemy 正确语法）
        "icontains": lambda x, y: x.ilike(f"%{y}%"),  # 包含（不区分大小写）
        "eq": lambda x, y: x == y,                # 等于
        "not_eq": lambda x, y: x != y,             # 不等于
        "startswith": lambda x, y: x.like(f"{y}%"),   # 开头是
        "endswith": lambda x, y: x.like(f"%{y}"),     # 结尾是
        "between": lambda x, y: x.between(y[0], y[1]),  # 在范围内（y是数组）
        "not_between": lambda x, y: ~(x.between(y[0], y[1])),  # 不在范围内
    }

    # 支持的操作符列表（用于接口验证）
    ADVANCED_OPERATORS: set[str] = {
        "icontains", "eq", "not_eq", "startswith", "endswith", "between", "not_between"
    }

    class Config:
        env_file = ".env"


settings = Settings()
