from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.plugins.auth_plugin.models import UserRole


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

class UserAdminCreate(BaseModel):
    """管理员创建用户"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Optional[UserRole] = None

class UserUpdate(BaseModel):
    """更新用户信息"""
    hashed_password:Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None



USER_WHITELIST = ["id","created_at","updated_at","role","username","is_active"
                  ,"email","full_name"]