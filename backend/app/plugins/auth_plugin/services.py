from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.redis_client import RedisService
from app.plugins.auth_plugin import models, schemas
from app.utils.all_orderby import universal_sort


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
        if not AuthService.verify_password(password, user.password):
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
                detail="账号已存在"
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
                password=AuthService.get_password_hash(user.password),
                role=models.UserRole.USER.value
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
    async def get_users(
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100,
            role: Optional[str] = None, ):
        """获取用户列表(支持角色过滤)，返回分页信息"""
        from sqlalchemy import func

        stmt = select(models.User)
        count_stmt = select(func.count(models.User.id))

        if role:
            stmt = stmt.where(models.User.role == role)
            count_stmt = count_stmt.where(models.User.role == role)

        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.offset(skip).limit(limit).order_by(models.User.id.asc())
        result = await db.execute(stmt)
        items = [schemas.UserResponse.model_validate(user) for user in result.scalars().all()]
        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    @staticmethod
    async def get_users_simple(
            db: AsyncSession,
            skip: int = 0,
            limit: int = 10,
            username: Optional[str] = None,
            role: Optional[str] = None,
            sort_by: Optional[str] = None,
            sort_order: Optional[str] = None,
    ):
        """获取用户列表（固定字段查询，支持排序）"""
        from sqlalchemy import func

        stmt = select(models.User)
        count_stmt = select(func.count(models.User.id))

        if username:
            stmt = stmt.where(models.User.username.icontains(username))
            count_stmt = count_stmt.where(models.User.username.icontains(username))
        if role:
            stmt = stmt.where(models.User.role == role)
            count_stmt = count_stmt.where(models.User.role == role)

        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        if not sort_by:
            stmt = stmt.order_by(models.User.id.asc()).offset(skip).limit(limit)
            result = await db.execute(stmt)
            data_list = [schemas.UserResponse.model_validate(user) for user in result.scalars().all()]
        else:
            stmt = stmt.order_by(models.User.id.asc())
            result = await db.execute(stmt)
            data_list = [schemas.UserResponse.model_validate(user) for user in result.scalars().all()]

            if sort_by not in schemas.USER_WHITELIST:
                sort_by = "id"

            valid_order = sort_order.lower() if sort_order else "asc"
            if valid_order not in ("asc", "desc"):
                valid_order = "asc"
            data_list = universal_sort(data_list, sort_by, valid_order)
            data_list = data_list[skip: skip + limit]

        return {
            "items": data_list,
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, update_data: schemas.UserUpdate):
        """更新用户信息"""
        stmt = select(models.User).where(models.User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(user, field, value)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int):
        """删除用户"""
        stmt = select(models.User).where(models.User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )
        await db.delete(user)
        await db.commit()
        return user

    @staticmethod
    async def create_user_by_admin(
            db: AsyncSession, user: schemas.UserAdminCreate
    ):
        """管理员创建用户"""
        stmt = select(models.User).where(models.User.username == user.username)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="账号已存在",
            )
        try:
            db_user = models.User(
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                password=AuthService.get_password_hash(user.password),
                role=user.role.value if user.role else models.UserRole.USER.value,
            )
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            return db_user
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建用户失败: {str(e)}",
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

        user.password = new_password
        await db.commit()
        await db.refresh(user)
        return user