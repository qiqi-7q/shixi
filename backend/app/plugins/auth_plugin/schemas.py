from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ==================== 权限相关 ====================

class PermissionResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    create_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== 角色相关 ====================

class RoleBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_ids: Optional[List[int]] = None
    level: int = 3


class RoleUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None
    level: Optional[int] = None


class RoleResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    level: int = 1
    permissions: List[PermissionResponse] = []
    create_by: Optional[str] = None
    create_at: Optional[datetime] = None
    update_by: Optional[str] = None
    update_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== 用户相关 ====================

class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    username: str
    password: str
    full_name: str
    email: str


class UserLogin(BaseModel):
    username: str
    password: Optional[str] = None


class OAuth2PasswordOptionalForm:
    """自定义 OAuth2 表单，password 可选"""

    def __init__(
        self,
        grant_type: str = "password",
        username: str = "",
        password: Optional[str] = None,
        scope: str = "",
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool
    role: Optional[str] = None
    role_id: Optional[int] = None
    role_name: Optional[str] = None
    create_at: Optional[datetime] = None
    update_at: Optional[datetime] = None
    create_by: Optional[str] = None
    update_by: Optional[str] = None

    class Config:
        from_attributes = True


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str


class UserAdminCreate(BaseModel):
    """管理员创建用户"""
    username: str
    password: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role_id: Optional[int] = None
    role: Optional[str] = None


class UserUpdate(BaseModel):
    """更新用户信息"""
    password: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role_id: Optional[int] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


USER_WHITELIST = ["id", "username", "email", "full_name", "is_active", "role_id", "role_name", "create_at", "update_at", "create_by", "update_by"]