from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")


class Settings(BaseSettings):

    # 项目启动配置(.env中配置)
    SERVER_HOST: str = "localhost"
    SERVER_PORT: int = 8000

    # MySQL配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "shang"
    MYSQL_DATABASE: str = "data_platform_test"

    # 是否开启数据库日志打印
    DB_ECHO: bool = False
    
    # Redis配置
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = "shang"
    REDIS_MAX_CONNECTIONS: int = 30
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 2592000  # 30天

    # 数据库连接池
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # 项目根目录（app文件夹）
    BASE_DIR: Path = Path(__file__).parent.parent
    # 静态文件目录
    STATIC_DIR: Path = BASE_DIR / "static"
    # 上传文件目录
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    # 日志目录
    LOG_DIR: Path = BASE_DIR / "logs"
    
    # 日志文件保留天数
    BACKUPCOUNT: int = 7

    # 1. 邮箱配置（核心！根据你的邮箱修改）
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

    # 零云平台数据接口配置
    DURATION_URL: str = (
        "https://dataasset.leapmotor.com/data-asset-api/v1/api/data?id=13"
    )
    DURATION_SERVICE_KEY: str = "3IsPMD39ot9pxZy"
    MILEAGE_URL: str = (
        "https://dataasset.leapmotor.com/data-asset-api/v1/api/data?id=14"
    )
    MILEAGE_SERVICE_KEY: str = "3J5FlzV0T132zOW"

    # MinIO配置
    MINIO_HOST:str = "10.192.8.193"
    MINIO_WEB_PORT:int = 8011
    MINIO_API_PORT:int = 8010
    MINIO_ROOT_USER:str = "minioadmin"
    MINIO_ROOT_PASSWORD:str = "MinIO.123456"
    MINIO_BUCKET: str = "lpatmp"
    MINIO_PATH: str = "dev"  # .env 中配置

    # 高级搜索配置
    ADVANCED_OPERATORS_MAP: dict = {
        # 高级搜索支持的操作符（使用 SQLAlchemy 正确语法）
        "icontains": lambda x, y: x.icontains(y),  # 包含（不区分大小写）
        "eq": lambda x, y: x == y,  # 等于
        "not_eq": lambda x, y: x != y,  # 不等于
        "startswith": lambda x, y: x.startswith(y),  # 开头是
        "endswith": lambda x, y: x.endswith(y),  # 结尾是
        "between": lambda x, y: x.between(y[0], y[1]),  # 在范围内（y是数组）
        "not_between": lambda x, y: ~(x.between(y[0], y[1])),  # 不在范围内
        "lt": lambda x, y: x < y,  # 小于
        "lte": lambda x, y: x <= y,  # 小于等于
        "gt": lambda x, y: x > y,  # 大于
        "gte": lambda x, y: x >= y,  # 大于等于
    }

    # 支持的操作符列表（用于接口验证）
    ADVANCED_OPERATORS: set[str] = {
        "icontains",
        "eq",
        "not_eq",
        "startswith",
        "endswith",
        "between",
        "not_between",
        "lt",
        "lte",
        "gt",
        "gte",
    }

    class Config:
        env_file = ".env"


settings = Settings()
