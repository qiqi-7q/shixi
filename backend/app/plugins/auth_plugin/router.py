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
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 检查token是否在黑名单中
    if redisserve.is_token_blacklisted(token):
        raise credentials_exception

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = await services.AuthService.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    return await services.AuthService.create_user(db=db, user=user)


@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    user = await services.AuthService.authenticate_user(
        db, form_data.username, form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = services.AuthService.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # 将token存储到Redis
    await redisserve.set_token(
        user.id, access_token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: models.User = Depends(get_current_user),
):
    """用户登出"""
    # 将token加入黑名单
    RedisService.blacklist_token(token)
    RedisService.delete_token(current_user.id)
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.put("/password")
async def update_password(
    password_update: schemas.PasswordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """修改密码"""
    # 验证旧密码
    if not services.AuthService.verify_password(
        password_update.old_password, current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password"
        )

    # 更新密码
    await services.AuthService.update_password(
        db, current_user.id, password_update.new_password
    )
    return {"message": "Password updated successfully"}


@router.put("/forgetpwd")
async def forget_password(
    username: str = Query(..., description="用户名"),
    db: AsyncSession = Depends(get_db),
):
    """忘记密码"""
    # 查询用户
    stmt = select(models.User).where(models.User.username == username)
    result = await db.execute(stmt)
    current_user = result.scalar_one_or_none()
    
    if not current_user:
        return {"message": "User not found","code":400,"data":None}


    # 发送新密码到用户邮箱
    await send_text_email(
        to_email=current_user.email,
        subject="忘记密码邮件",
        body=f"您的新密码是{current_user.hashed_password}",
    )
    return {"message": "Password has been sent to your email address","code":200,"data":current_user}
