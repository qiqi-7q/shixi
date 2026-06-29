# app/core/database.py
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

# 使用 aiomysql 驱动
DATABASE_URL = f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}?charset=utf8mb4"

# 异步数据库引擎
engine = create_async_engine(
    DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=True,
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
