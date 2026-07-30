from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
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
    """获取当前用户（含角色和权限），验证失败抛异常"""
    if await redisserve.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await services.AuthService.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_admin(
    current_user: models.User = Depends(get_current_user),
):
    """要求管理员及以上角色（superuser / admin）"""
    admin_roles = {"superuser", "admin"}
    if current_user.role_rel is None or current_user.role_rel.code not in admin_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return current_user


class PermissionChecker:
    """权限检查器：基于权限码的依赖注入"""

    def __init__(self, permission_code: str):
        self.permission_code = permission_code

    async def __call__(self, current_user: models.User = Depends(get_current_user)):
        permissions = await services.get_user_permissions(current_user)
        if self.permission_code not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要权限: {self.permission_code}",
            )
        return current_user


# 预定义权限检查依赖
# ─── 用户管理 ───
require_user_read = PermissionChecker("user:read")
require_user_add = PermissionChecker("user:add")
require_user_update = PermissionChecker("user:update")
require_user_delete = PermissionChecker("user:delete")
# ─── 人员管理 ───
require_employer_read = PermissionChecker("employer:read")
require_employer_add = PermissionChecker("employer:add")
require_employer_update = PermissionChecker("employer:update")
require_employer_delete = PermissionChecker("employer:delete")
# ─── 路线管理 ───
require_route_read = PermissionChecker("route:read")
require_route_add = PermissionChecker("route:add")
require_route_update = PermissionChecker("route:update")
require_route_delete = PermissionChecker("route:delete")
# ─── 权限管理（角色）───
require_role_read = PermissionChecker("role:read")
require_role_add = PermissionChecker("role:add")
require_role_update = PermissionChecker("role:update")
require_role_delete = PermissionChecker("role:delete")
# ─── 车辆管理 ───
require_vehicle_read = PermissionChecker("vehicle:read")
require_vehicle_add = PermissionChecker("vehicle:add")
require_vehicle_update = PermissionChecker("vehicle:update")
require_vehicle_delete = PermissionChecker("vehicle:delete")
require_vehicle_export = PermissionChecker("vehicle:export")
# ─── 借用管理 ───
require_borrow_read = PermissionChecker("borrow:read")
require_borrow_add = PermissionChecker("borrow:add")
require_borrow_update = PermissionChecker("borrow:update")
require_borrow_approve = PermissionChecker("borrow:approve")
require_borrow_delete = PermissionChecker("borrow:delete")
# ─── 测试记录 ───
require_test_record_read = PermissionChecker("test_record:read")
require_test_record_add = PermissionChecker("test_record:add")
require_test_record_update = PermissionChecker("test_record:update")
require_test_record_delete = PermissionChecker("test_record:delete")
require_test_record_import = PermissionChecker("test_record:import")
require_test_record_export = PermissionChecker("test_record:export")
# ─── 统计分析 ───
require_statistics_view = PermissionChecker("statistics:view")
require_statistics_export = PermissionChecker("statistics:export")
require_statistics_add = PermissionChecker("statistics:add")
require_statistics_update = PermissionChecker("statistics:update")
require_statistics_delete = PermissionChecker("statistics:delete")


@router.get("/users")
async def get_all_users(
    role_name: str = Query(None, description="按角色 code 过滤"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_user_read),
):
    """获取用户列表（需 user:read 权限）"""
    current_role_code = current_user.role_rel.code if current_user.role_rel else None
    users = await services.AuthService.get_users(
        db, skip=skip, limit=limit, role_name=role_name,
        current_role_code=current_role_code,
    )
    return {"code": 200, "message": "获取成功", "data": users}


@router.get("/users/fixsearch")
async def get_users_simple(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=500),
    username: Optional[str] = None,
    role: Optional[str] = Query(None, description="按角色名过滤"),
    sort_by: Optional[str] = Query(None, description="排序字段名"),
    sort_order: Optional[str] = Query("asc", description="排序方向"),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_user_read),
):
    """获取用户列表（需 user:read 权限）"""
    current_role_code = current_user.role_rel.code if current_user.role_rel else None
    users = await services.AuthService.get_users_simple(
        db, skip=skip, limit=limit, username=username,
        role_name=role, sort_by=sort_by, sort_order=sort_order,
        current_role_code=current_role_code,
    )
    return {"code": 200, "message": "获取成功", "data": users}


@router.post("/users")
async def create_user_by_admin(
    user: schemas.UserAdminCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_user_add),
):
    """管理员创建用户（需 user:add 权限）"""
    result = await services.AuthService.create_user_by_admin(db=db, user=user, current_user=current_user)
    return {"code": 201, "message": "创建成功", "data": result.model_dump(mode="json")}


@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_user_read),
):
    """获取用户详情（需 user:read 权限）"""
    target = await services.AuthService.get_user(db, user_id, current_user=current_user)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return {"code": 200, "message": "获取成功", "data": services.AuthService._user_to_response(target).model_dump(mode="json")}


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_user_update),
):
    """更新用户信息（需 user:update 权限）"""
    result = await services.AuthService.update_user(db, user_id, user_update, current_user=current_user)
    return {"code": 200, "message": "更新成功", "data": result.model_dump(mode="json")}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_user_delete),
):
    """删除用户（需 user:delete 权限）"""
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能删除自己")
    result = await services.AuthService.delete_user(db, user_id, current_user=current_user)
    return {"code": 200, "message": "删除成功", "data": result.username}

@router.post("/register")
async def register(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """用户注册，默认分配 user 角色"""
    result = await services.AuthService.create_user(db=db, user=user)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = services.AuthService.create_access_token(
        data={"sub": result.username}, expires_delta=access_token_expires
    )

    return {
        "code": 201,
        "message": "注册成功",
        "data": {
            "user": services.AuthService._user_to_response(result).model_dump(mode="json"),
            "access_token": access_token,
            "token_type": "bearer"
        },
    }


@router.post("/login")
async def login(
    username: str = Form(...),
    password: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """用户登录"""
    user = await services.AuthService.authenticate_user(db, username, password or "")
    if not user:
        return {"code": 401, "message": "用户名或密码错误", "data": None}
    if user.is_active == 0:
        return {"code": 403, "message": "该用户已被禁用，请联系管理员", "data": None}

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = services.AuthService.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    permissions = await services.get_user_permissions(user)

    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "userid": user.id,
            "username": user.username,
            "role": user.role_rel.name if user.role_rel else None,
            "permissions": permissions,
            "access_token": access_token,
            "token_type": "bearer",
        },
    }


@router.post("/visitor_login")
async def visitor_login(
    db: AsyncSession = Depends(get_db),
):
    """游客登录，无需注册账号，仅可查看数据，不能编辑、新增、删除、导入、导出"""
    user = await services.AuthService.get_visitor_user(db)
    if not user:
        return {"code": 500, "message": "游客账号尚未初始化", "data": None}

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = services.AuthService.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    permissions = await services.get_user_permissions(user)

    return {
        "code": 200,
        "message": "游客登录成功",
        "data": {
            "userid": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role_rel.name if user.role_rel else None,
            "permissions": permissions,
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

    await redisserve.blacklist_token(token)
    await redisserve.delete_token(current_user.id)
    return {"code": 200, "message": "登出成功", "data": current_user.full_name}


@router.get("/me")
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """获取当前用户信息"""

    if not current_user:
        return {"code": 401, "message": "Could not validate credentials", "data": None}
    permissions = await services.get_user_permissions(current_user)
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            **services.AuthService._user_to_response(current_user).model_dump(mode="json"),
            "permissions": permissions,
        },
    }


@router.put("/password")
async def update_password(
    password_update: schemas.PasswordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """修改密码"""
    if not current_user:
        return {"code": 401, "message": "Could not validate credentials", "data": None}

    if not services.AuthService.verify_password(
        password_update.old_password, current_user.password
    ):
        return {"code": 400, "message": "原密码输入错误", "data": None}

    await services.AuthService.update_password(
        db, current_user.id, password_update.new_password
    )
    return {
        "code": 200,
        "message": "密码修改成功",
        "data": services.AuthService._user_to_response(current_user).model_dump(mode="json"),
    }


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

    if not current_user.email:
        return {"code": 400, "message": "该用户未绑定邮箱，无法发送邮件", "data": None}

    try:
        await send_text_email(
            to_email=current_user.email,
            subject="忘记密码邮件",
            body=f"您的新密码是{current_user.password}",
        )
    except Exception as e:
        return {"code": 500, "message": f"邮件发送失败: {str(e)}", "data": None}

    return {
        "message": "Password has been sent to your email address",
        "code": 200,
        "data": services.AuthService._user_to_response(current_user).model_dump(mode="json"),
    }


# ==================== 角色管理 CRUD ====================

@router.get("/roles/all")
async def get_roles_all(
    sort_by: str = Query("level", description="排序字段：id/level/code/name/create_at"),
    sort_order: str = Query("desc", description="排序方向：asc/desc"),
    search: Optional[str] = Query(None, description="模糊搜索角色名/编码"),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role_read),
):
    """获取所有角色（不分页，需 role:read 权限）"""
    current_role_code = current_user.role_rel.code if current_user.role_rel else None
    result = await services.RoleService.get_roles_all(
        db, sort_by=sort_by, sort_order=sort_order, search=search,
        current_role_code=current_role_code,
    )
    return {"code": 200, "message": "获取成功", "data": result}


@router.get("/roles")
async def get_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    sort_by: str = Query("level", description="排序字段：id/level/code/name/create_at"),
    sort_order: str = Query("desc", description="排序方向：asc/desc"),
    search: Optional[str] = Query(None, description="模糊搜索角色名/编码"),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role_read),
):
    """获取角色列表（需 role:read 权限）"""
    current_role_code = current_user.role_rel.code if current_user.role_rel else None
    result = await services.RoleService.get_roles(
        db, skip=skip, limit=limit, sort_by=sort_by, sort_order=sort_order,
        search=search, current_role_code=current_role_code,
    )
    return {"code": 200, "message": "获取成功", "data": result}


@router.get("/roles/{role_id}")
async def get_role_detail(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role_read),
):
    """获取角色详情（需 role:read 权限）"""
    role = await services.RoleService.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")

    if current_user.role_rel and role.level <= current_user.role_rel.level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看同级或更高级别的角色",
        )

    return {"code": 200, "message": "获取成功", "data": schemas.RoleResponse.model_validate(role).model_dump(mode="json")}


@router.post("/roles")
async def create_role(
    role_data: schemas.RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role_add),
):
    """创建角色（需 role:add 权限）"""
    role = await services.RoleService.create_role(db, role_data, current_user)
    return {"code": 201, "message": "创建成功", "data": schemas.RoleResponse.model_validate(role).model_dump(mode="json")}


@router.put("/roles/{role_id}")
async def update_role(
    role_id: int,
    role_data: schemas.RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role_update),
):
    """更新角色（需 role:update 权限）"""
    role = await services.RoleService.update_role(db, role_id, role_data, current_user)
    return {"code": 200, "message": "更新成功", "data": schemas.RoleResponse.model_validate(role).model_dump(mode="json")}


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role_delete),
):
    """删除角色（需 role:delete 权限）"""
    role = await services.RoleService.delete_role(db, role_id, current_user)
    return {"code": 200, "message": "删除成功", "data": role.name}


# ==================== 权限查询 ====================

@router.get("/permissions")
async def get_permissions(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role_read),
):
    """获取权限列表（需 role:read 权限）"""
    permissions = await services.PermissionService.get_all_permissions(db)
    items = [schemas.PermissionResponse.model_validate(p).model_dump(mode="json") for p in permissions]

    grouped = {}
    for p in items:
        module = p["code"].split(":")[0] if ":" in p["code"] else "other"
        grouped.setdefault(module, []).append(p)

    return {"code": 200, "message": "获取成功", "data": grouped}