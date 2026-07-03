from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.send_email import send_text_email
from app.core.config import settings
from app.core.database import get_db
from app.core.redis_client import redisserve
from app.plugins.auth_plugin import models, schemas, services

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://127.0.0.1:8000/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    """获取当前用户，验证失败返回 None"""
    # 检查token是否在黑名单中
    if await redisserve.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await services.AuthService.get_user_by_username(
        db, username=token_data.username
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def require_admin(current_user: models.User = Depends(get_current_user)):
    """要求管理员权限（含超级管理员）"""
    if current_user.role not in (models.UserRole.ADMIN.value, models.UserRole.SUPERUSER.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，请联系管理员/超管",
        )
    return current_user

async def require_superadmin(current_user: models.User = Depends(get_current_user)):
    """要求超级管理员权限"""
    if not current_user.role ==models.UserRole.SUPERUSER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要超级管理员权限",
        )
    return current_user

@router.get("/users")
async def get_all_users(
    role: str = Query(None, description="按角色过滤：user / admin"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """获取用户列表
    - 超级管理员：查看所有用户
    - 管理员：只能查看普通用户（role=user）
    """
    if current_user.role != models.UserRole.SUPERUSER.value:
        if role and role != models.UserRole.USER.value:
            return {"code": 403, "message": "无权查看该角色用户", "data": []}
        role = models.UserRole.USER.value
    users = await services.AuthService.get_users(
        db, skip=skip, limit=limit, role=role
    )
    return {"code": 200, "message": "获取成功", "data": users}


@router.get("/users/fixsearch")
async def get_users_simple(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=500),
    username: Optional[str] = None,
    role: Optional[str] = Query(None, description="按角色过滤：user / admin"),
    sort_by: Optional[str] = Query(None, description="排序字段名（不提供则不排序）"),
    sort_order: Optional[str] = Query(
        "asc", description="排序方向：asc（升序，默认）/ desc（降序）"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """获取用户列表（固定字段查询，支持排序）
    - 超级管理员：查看所有用户
    - 管理员：只能查看普通用户（role=user）
    """
    if current_user.role != models.UserRole.SUPERUSER.value:
        if role and role != models.UserRole.USER.value:
            return {"code": 403, "message": "无权查看该角色用户", "data": []}
        role = models.UserRole.USER.value

    users = await services.AuthService.get_users_simple(
        db,
        skip=skip,
        limit=limit,
        username=username,
        role=role,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return {"code": 200, "message": "获取成功", "data": users}


@router.post("/users")
async def create_user_by_admin(
    user: schemas.UserAdminCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """管理员创建用户
    - 超级管理员：可创建任意角色（admin / user）
    - 管理员：只能创建普通用户（role=user）
    """
    if current_user.role != models.UserRole.SUPERUSER.value and user.role == models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权创建管理员账号",
        )
    result = await services.AuthService.create_user_by_admin(db=db, user=user)
    return {"code": 201, "message": "创建成功", "data": result}

@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """获取用户详情
    - 超级管理员：可查看任意用户
    - 管理员：只能查看普通用户
    """
    target = await services.AuthService.get_user(db, user_id)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
        )
    if current_user.role != models.UserRole.SUPERUSER.value:
        if target.role == models.UserRole.ADMIN.value or target.role == models.UserRole.SUPERUSER.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看该用户",
            )
    return {"code": 200, "message": "获取成功", "data": target}

@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """更新用户信息
    - 超级管理员：可修改任意用户的 role、is_active 等
    - 管理员：只能修改普通用户的 is_active、email、full_name
    - 不能修改自己
    """
    # if user_id == current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="不能修改自己的信息",
    #     )
    target = await services.AuthService.get_user(db, user_id)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
        )
    if current_user.role != models.UserRole.SUPERUSER.value:
        if target.role == models.UserRole.ADMIN.value or target.role == models.UserRole.SUPERUSER.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改该用户",
            )
        if user_update.role is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改角色",
            )
    result = await services.AuthService.update_user(
        db, user_id, user_update
    )
    return {"code": 200, "message": "更新成功", "data": result}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """删除用户
    - 超级管理员：可删除任意用户（除自己）
    - 管理员：只能删除普通用户
    - 不能删除自己
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己",
        )
    target = await services.AuthService.get_user(db, user_id)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
        )
    if current_user.role != models.UserRole.SUPERUSER.value:
        if target.role == models.UserRole.ADMIN.value or target.role == models.UserRole.SUPERUSER.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除该用户",
            )
    result = await services.AuthService.delete_user(db, user_id)
    return {"code": 200, "message": "删除成功", "data": result.username}

@router.post("/register")
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    result = await services.AuthService.create_user(db=db, user=user)

    # 注册成功后生成token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = services.AuthService.create_access_token(
        data={"sub": result.username}, expires_delta=access_token_expires
    )

    # # 将token存储到Redis
    # await redisserve.set_token(
    #     result.id, access_token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    # )

    return {
        "code": 201,
        "message": "注册成功",
        "data": {"user": result, "access_token": access_token, "token_type": "bearer"},
    }


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    user = await services.AuthService.authenticate_user(
        db, form_data.username, form_data.password
    )

    if not user:
        return {"code": 401, "message": "用户名或密码错误", "data": None}

    if user.is_active == 0:
        return {"code": 403, "message": "该用户已被禁用，请联系管理员", "data": None}

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = services.AuthService.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # # 将token存储到Redis
    # await redisserve.set_token(
    #     user.id, access_token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    # )

    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "userid": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role":user.role,
            "access_token": access_token,
            "token_type": "bearer",
        },
    }


@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: models.User = Depends(get_current_user),
):
    """用户登出"""
    if not current_user:
        return {"code": 401, "message": "Could not validate credentials", "data": None}

    # 将token加入黑名单
    await redisserve.blacklist_token(token)
    await redisserve.delete_token(current_user.id)
    return {"code": 200, "message": "登出成功", "data": current_user.full_name}


@router.get("/me")
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """获取当前用户信息"""

    if not current_user:
        return {"code": 401, "message": "Could not validate credentials", "data": None}
    return {"code": 200, "message": "获取成功", "data": current_user}


@router.put("/password")
async def update_password(
    password_update: schemas.PasswordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """修改密码"""
    if not current_user:
        return {"code": 401, "message": "Could not validate credentials", "data": None}

    # 验证旧密码
    if not services.AuthService.verify_password(
        password_update.old_password, current_user.hashed_password
    ):
        return {"code": 400, "message": "Incorrect old password", "data": None}

    # 更新密码
    await services.AuthService.update_password(
        db, current_user.id, password_update.new_password
    )
    return {"code": 200, "message": "密码修改成功", "data": current_user}


@router.put("/forgetpwd")
async def forget_password(
    username: str = Query(..., description="用户名"),
    db: AsyncSession = Depends(get_db),
):
    """忘记密码"""
    stmt = select(models.User).where(models.User.username == username)
    result = await db.execute(stmt)
    current_user = result.scalar_one_or_none()

    if not current_user:
        return {"code": 400, "message": "用户不存在", "data": None}

    await send_text_email(
        to_email=current_user.email,
        subject="忘记密码邮件",
        body=f"您的新密码是{current_user.hashed_password}",
    )
    return {
        "message": "Password has been sent to your email address",
        "code": 200,
        "data": current_user,
    }