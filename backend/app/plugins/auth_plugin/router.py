from datetime import timedelta

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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    """获取当前用户，验证失败返回 None"""

    # 检查token是否在黑名单中
    if redisserve.is_token_blacklisted(token):
        return None

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = schemas.TokenData(username=username)
    except JWTError:
        return None

    user = await services.AuthService.get_user_by_username(db, username=token_data.username)
    return user


@router.post("/register")
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    result = await services.AuthService.create_user(db=db, user=user)
    
    # 注册成功后生成token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = services.AuthService.create_access_token(
        data={"sub": result.username}, expires_delta=access_token_expires
    )
    
    # 将token存储到Redis
    await redisserve.set_token(
        result.id, access_token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return {"code": 201, "message": "注册成功", "data": {"user": result, "access_token": access_token, "token_type": "bearer"}}


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    user = await services.AuthService.authenticate_user(
        db, form_data.username, form_data.password
    )

    if not user:
        return {"code": 401, "message": "Incorrect username or password", "data": None}

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = services.AuthService.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # 将token存储到Redis
    await redisserve.set_token(
        user.id, access_token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return {"code": 200, "message": "登录成功", "data": {"username": user.username,"full_name": user.full_name, "access_token": access_token, "token_type": "bearer"}}


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
    return {"message": "Password has been sent to your email address","code":200,"data":current_user}
