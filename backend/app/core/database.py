# app/core/database.py
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

# 使用 aiomysql 驱动
DATABASE_URL_MYSQL = f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}?charset=utf8mb4"

# MariaDB 数据库连接
DATABASE_URL_MariaDB = f"mysql+aiomysql://{settings.MariaDB_USER}:{settings.MariaDB_PASSWORD}@{settings.MariaDB_HOST}:{settings.MariaDB_PORT}/{settings.MariaDB_DATABASE}?charset=utf8mb4"

# 异步数据库引擎
engine = create_async_engine(
    DATABASE_URL_MYSQL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DB_ECHO,
)

SessionLocal = async_sessionmaker(autoflush=False, bind=engine, expire_on_commit=False)

Base = declarative_base()

async_engine = engine


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as async_session:
        try:
            yield async_session
            await async_session.commit()
        except Exception as e:
            print(f"Database error: {e}")
            await async_session.rollback()
            raise e


# 使用 asyncpg 驱动连接 PostgreSQL
DATABASE_URL_PG = (
    f"postgresql+asyncpg://{settings.PG_USER}:{settings.PG_PASSWORD}"
    f"@{settings.PG_HOST}:{settings.PG_PORT}/{settings.PG_DATABASE}"
)

# PostgreSQL 异步数据库引擎
engine_pg = create_async_engine(
    DATABASE_URL_PG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=False,
)

SessionLocalPG = async_sessionmaker(
    autoflush=False, bind=engine_pg, expire_on_commit=False
)

# 权限管理模块专用的 declarative_base
BasePG = declarative_base()


async def get_db_pg() -> AsyncGenerator[AsyncSession, None]:
    """PostgreSQL 数据库会话依赖注入"""
    async with SessionLocalPG() as async_session:
        try:
            yield async_session
            await async_session.commit()
        except Exception as e:
            print(f"PostgreSQL database error: {e}")
            await async_session.rollback()
            raise e