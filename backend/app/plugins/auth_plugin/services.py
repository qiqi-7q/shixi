from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
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
    def authenticate_user(db: Session, username: str, password: str):
        """验证用户登录"""
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user:
            return False
        if not AuthService.verify_password(password, user.hashed_password):
            return False
        return user

    @staticmethod
    def create_user(db: Session, user: schemas.UserCreate):
        """创建新用户"""
        # 检查用户名是否已存在
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # 检查邮箱是否已存在
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        try:
            # 直接存储明文密码
            db_user = models.User(
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                hashed_password=AuthService.get_password_hash(user.password)  # 实际上存储的是明文
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )

    @staticmethod
    def get_user(db: Session, user_id: int):
        """根据ID获取用户"""
        return db.query(models.User).filter(models.User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str):
        """根据用户名获取用户"""
        return db.query(models.User).filter(models.User.username == username).first()

    @staticmethod
    def update_password(db: Session, user_id: int, new_password: str):
        """更新用户密码"""
        user = AuthService.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.hashed_password = new_password  # 直接存储明文
        db.commit()
        db.refresh(user)
        return user