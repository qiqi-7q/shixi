from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.redis_client import RedisService
from app.plugins.auth_plugin import models, schemas


class AuthService:
    @staticmethod
    def verify_password(plain_password: str, stored_password: str) -> bool:
        """直接比较明文密码"""
        return plain_password == stored_password

    @staticmethod
    def get_password_hash(password: str) -> str:
        """直接返回明文密码，不进行加密"""
        return password

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str):
        """验证用户登录"""
        stmt = select(models.User).where(models.User.username == username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return False
        if not AuthService.verify_password(password, user.hashed_password):
            return False
        return user

    @staticmethod
    async def create_user(db: AsyncSession, user: schemas.UserCreate):
        """创建新用户"""
        # 检查用户名是否已存在
        stmt = select(models.User).where(models.User.username == user.username)
        result = await db.execute(stmt)
        db_user = result.scalar_one_or_none()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # # 检查邮箱是否已存在
        # stmt = select(models.User).where(models.User.email == user.email)
        # result = await db.execute(stmt)
        # db_user = result.scalar_one_or_none()
        # if db_user:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Email already registered"
        #     )

        try:
            # 直接存储明文密码
            db_user = models.User(
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                hashed_password=AuthService.get_password_hash(user.password)
            )
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            return db_user
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )

    @staticmethod
    async def get_user(db: AsyncSession, user_id: int):
        """根据ID获取用户"""
        stmt = select(models.User).where(models.User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str):
        """根据用户名获取用户"""
        stmt = select(models.User).where(models.User.username == username)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_password(db: AsyncSession, user_id: int, new_password: str):
        """更新用户密码"""
        stmt = select(models.User).where(models.User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.hashed_password = new_password
        await db.commit()
        await db.refresh(user)
        return user