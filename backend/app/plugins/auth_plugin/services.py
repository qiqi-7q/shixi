from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from jose import jwt
from fastapi import HTTPException, status

from app.core.config import settings
from app.plugins.auth_plugin import models, schemas
from app.utils.all_orderby import universal_sort


async def get_user_permissions(user: models.User) -> list[str]:
    """获取用户的所有权限码"""
    if not user.role_rel:
        return []
    return [p.code for p in user.role_rel.permissions]


class PermissionService:

    @staticmethod
    async def get_all_permissions(db: AsyncSession) -> List[models.Permission]:
        """获取所有权限"""
        stmt = select(models.Permission).order_by(models.Permission.id)
        result = await db.execute(stmt)
        return result.scalars().all()


class RoleService:

    @staticmethod
    async def get_roles(db: AsyncSession, skip: int = 0, limit: int = 100, sort_by: str = "level", sort_order: str = "desc", search: str = None, current_role_code: Optional[str] = None):
        from sqlalchemy import func, or_
        allowed_sort = {"id", "level", "code", "name", "create_at"}
        if sort_by not in allowed_sort:
            sort_by = "level"
        sort_col = getattr(models.Role, sort_by)
        if sort_order == "asc":
            sort_col = sort_col.asc()
        else:
            sort_col = sort_col.desc()

        stmt = (
            select(models.Role)
            .options(selectinload(models.Role.permissions))
        )
        if current_role_code is not None:
            current_permission = AuthService._get_role_permission_level(current_role_code)
            allowed_codes = [code for code, level in AuthService.ROLE_PERMISSION_ORDER.items() if (level >= current_permission if current_role_code == "superuser" else level > current_permission)]
            default_codes = list(AuthService.ROLE_PERMISSION_ORDER.keys())
            if allowed_codes:
                stmt = stmt.where(
                    or_(
                        models.Role.code.in_(allowed_codes),
                        ~models.Role.code.in_(default_codes)
                    )
                )
            else:
                stmt = stmt.where(~models.Role.code.in_(default_codes))
        if search:
            stmt = stmt.where(
                or_(
                    models.Role.name.ilike(f"%{search}%"),
                    models.Role.code.ilike(f"%{search}%"),
                )
            )
        stmt = stmt.order_by(sort_col, models.Role.id).offset(skip).limit(limit)

        count_stmt = select(func.count(models.Role.id))
        if current_role_code is not None:
            current_permission = AuthService._get_role_permission_level(current_role_code)
            allowed_codes = [code for code, level in AuthService.ROLE_PERMISSION_ORDER.items() if (level >= current_permission if current_role_code == "superuser" else level > current_permission)]
            default_codes = list(AuthService.ROLE_PERMISSION_ORDER.keys())
            if allowed_codes:
                count_stmt = count_stmt.where(
                    or_(
                        models.Role.code.in_(allowed_codes),
                        ~models.Role.code.in_(default_codes)
                    )
                )
            else:
                count_stmt = count_stmt.where(~models.Role.code.in_(default_codes))
        if search:
            count_stmt = count_stmt.where(
                or_(
                    models.Role.name.ilike(f"%{search}%"),
                    models.Role.code.ilike(f"%{search}%"),
                )
            )
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()
        result = await db.execute(stmt)
        roles = result.scalars().all()
        return {
            "items": [schemas.RoleResponse.model_validate(r).model_dump(mode="json") for r in roles],
            "total": total, "skip": skip, "limit": limit,
        }

    @staticmethod
    async def get_roles_all(db: AsyncSession, sort_by: str = "level", sort_order: str = "desc", search: str = None, current_role_code: Optional[str] = None):
        from sqlalchemy import or_
        allowed_sort = {"id", "level", "code", "name", "create_at"}
        if sort_by not in allowed_sort:
            sort_by = "level"
        sort_col = getattr(models.Role, sort_by)
        if sort_order == "asc":
            sort_col = sort_col.asc()
        else:
            sort_col = sort_col.desc()

        stmt = (
            select(models.Role)
            .options(selectinload(models.Role.permissions))
        )
        if current_role_code is not None:
            current_permission = AuthService._get_role_permission_level(current_role_code)
            allowed_codes = [code for code, level in AuthService.ROLE_PERMISSION_ORDER.items() if (level >= current_permission if current_role_code == "superuser" else level > current_permission)]
            default_codes = list(AuthService.ROLE_PERMISSION_ORDER.keys())
            if allowed_codes:
                stmt = stmt.where(
                    or_(
                        models.Role.code.in_(allowed_codes),
                        ~models.Role.code.in_(default_codes)
                    )
                )
            else:
                stmt = stmt.where(~models.Role.code.in_(default_codes))
        if search:
            stmt = stmt.where(
                or_(
                    models.Role.name.ilike(f"%{search}%"),
                    models.Role.code.ilike(f"%{search}%"),
                )
            )
        stmt = stmt.order_by(sort_col, models.Role.id)
        result = await db.execute(stmt)
        roles = result.scalars().all()
        return [schemas.RoleResponse.model_validate(r).model_dump(mode="json") for r in roles]

    @staticmethod
    async def get_role(db: AsyncSession, role_id: int):
        stmt = (
            select(models.Role)
            .options(selectinload(models.Role.permissions))
            .where(models.Role.id == role_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_role(db: AsyncSession, role_data: schemas.RoleCreate, current_user: models.User = None):
        exist = await db.execute(
            select(models.Role).where(models.Role.code == role_data.code)
        )
        if exist.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="角色 code 已存在")

        if current_user and current_user.role_rel:
            if role_data.level <= current_user.role_rel.level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权创建同级或更高级别的角色",
                )

        role = models.Role(
            code=role_data.code, name=role_data.name, description=role_data.description,
            level=role_data.level, create_by=current_user.username if current_user else None,
        )
        if role_data.permission_ids:
            perm_result = await db.execute(
                select(models.Permission).where(models.Permission.id.in_(role_data.permission_ids))
            )
            role.permissions = perm_result.scalars().all()
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role

    @staticmethod
    async def update_role(db: AsyncSession, role_id: int, role_data: schemas.RoleUpdate, current_user: models.User = None):
        stmt = (
            select(models.Role)
            .options(selectinload(models.Role.permissions))
            .where(models.Role.id == role_id)
        )
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")

        if current_user and current_user.role_rel:
            if role.level <= current_user.role_rel.level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权修改同级或更高级别的角色",
                )
            if role_data.level is not None and role_data.level <= current_user.role_rel.level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权将角色设置为同级或更高级别",
                )

        if role_data.code is not None and role_data.code != role.code:
            if role.code in ("superuser", "admin", "user", "visitor"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"系统默认角色 '{role.code}' 不可修改 code",
                )
            exist = await db.execute(
                select(models.Role).where(models.Role.code == role_data.code)
            )
            if exist.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"角色 code '{role_data.code}' 已存在",
                )
            role.code = role_data.code
        if role_data.name is not None:
            role.name = role_data.name
        if role_data.description is not None:
            role.description = role_data.description
        if role_data.level is not None:
            role.level = role_data.level
        if current_user:
            role.update_by = current_user.username
        if role_data.permission_ids is not None:
            perm_result = await db.execute(
                select(models.Permission).where(models.Permission.id.in_(role_data.permission_ids))
            )
            role.permissions = perm_result.scalars().all()
        await db.commit()
        await db.refresh(role)
        return role

    @staticmethod
    async def delete_role(db: AsyncSession, role_id: int, current_user: models.User = None):
        role = await db.get(models.Role, role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
        if role.code in ("superuser", "admin", "user", "visitor"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"系统默认角色 '{role.code}' 不可删除",
            )

        if current_user and current_user.role_rel:
            if role.level <= current_user.role_rel.level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权删除同级或更高级别的角色",
                )

        await db.delete(role)
        await db.commit()
        return role


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
        stmt = (
            select(models.User)
            .options(selectinload(models.User.role_rel).selectinload(models.Role.permissions))
            .where(models.User.username == username)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return False
        if not user.password or not AuthService.verify_password(password, user.password):
            return False
        return user

    @staticmethod
    async def create_user(db: AsyncSession, user: schemas.UserCreate):
        stmt = select(models.User).where(models.User.username == user.username)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="账号已存在")

        default_role_result = await db.execute(
            select(models.Role).where(models.Role.code == models.UserRole.USER.value)
        )
        default_role = default_role_result.scalar_one_or_none()

        try:
            db_user = models.User(
                username=user.username,
                password=AuthService.get_password_hash(user.password),
                full_name=user.full_name,
                email=user.email,
                role_id=default_role.id if default_role else None,
            )
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            return db_user
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create user: {str(e)}")

    @staticmethod
    async def get_users(
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100,
            role_name: Optional[str] = None,
            current_role_code: Optional[str] = None,
    ):
        from sqlalchemy import func, or_

        stmt = select(models.User).options(
            selectinload(models.User.role_rel).selectinload(models.Role.permissions)
        )
        count_stmt = select(func.count(models.User.id))

        if role_name:
            stmt = stmt.join(models.User.role_rel).where(models.Role.code == role_name)
            count_stmt = count_stmt.join(models.User.role_rel).where(models.Role.code == role_name)

        if current_role_code is not None:
            current_permission = AuthService._get_role_permission_level(current_role_code)
            operator = "__ge__" if current_role_code == "superuser" else "__gt__"
            allowed_codes = [code for code, level in AuthService.ROLE_PERMISSION_ORDER.items() if getattr(level, operator)(current_permission)]
            default_codes = list(AuthService.ROLE_PERMISSION_ORDER.keys())
            if role_name and role_name not in allowed_codes:
                if role_name in AuthService.ROLE_PERMISSION_ORDER:
                    stmt = stmt.where(models.User.id == -1)
                    count_stmt = count_stmt.where(models.User.id == -1)
            elif not role_name and allowed_codes:
                allowed_ids_subq = select(models.Role.id).where(
                    or_(
                        models.Role.code.in_(allowed_codes),
                        ~models.Role.code.in_(default_codes)
                    )
                )
                stmt = stmt.where(models.User.role_id.in_(allowed_ids_subq))
                count_stmt = count_stmt.where(models.User.role_id.in_(allowed_ids_subq))
            elif not role_name and not allowed_codes:
                allowed_ids_subq = select(models.Role.id).where(~models.Role.code.in_(default_codes))
                stmt = stmt.where(models.User.role_id.in_(allowed_ids_subq))
                count_stmt = count_stmt.where(models.User.role_id.in_(allowed_ids_subq))

        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.offset(skip).limit(limit).order_by(models.User.id.asc())
        result = await db.execute(stmt)
        items = [AuthService._user_to_response(u).model_dump(mode="json") for u in result.scalars().all()]
        return {"items": items, "total": total, "skip": skip, "limit": limit}

    @staticmethod
    async def get_users_simple(
            db: AsyncSession,
            skip: int = 0,
            limit: int = 10,
            username: Optional[str] = None,
            role_name: Optional[str] = None,
            sort_by: Optional[str] = None,
            sort_order: Optional[str] = None,
            current_role_code: Optional[str] = None,
    ):
        from sqlalchemy import func, or_

        stmt = select(models.User).options(
            selectinload(models.User.role_rel).selectinload(models.Role.permissions)
        )
        count_stmt = select(func.count(models.User.id))

        if username:
            stmt = stmt.where(models.User.username.icontains(username))
            count_stmt = count_stmt.where(models.User.username.icontains(username))
        if role_name:
            stmt = stmt.join(models.User.role_rel).where(models.Role.code == role_name)
            count_stmt = count_stmt.join(models.User.role_rel).where(models.Role.code == role_name)

        if current_role_code is not None:
            current_permission = AuthService._get_role_permission_level(current_role_code)
            operator = "__ge__" if current_role_code == "superuser" else "__gt__"
            allowed_codes = [code for code, level in AuthService.ROLE_PERMISSION_ORDER.items() if getattr(level, operator)(current_permission)]
            default_codes = list(AuthService.ROLE_PERMISSION_ORDER.keys())
            if role_name and role_name not in allowed_codes:
                if role_name in AuthService.ROLE_PERMISSION_ORDER:
                    stmt = stmt.where(models.User.id == -1)
                    count_stmt = count_stmt.where(models.User.id == -1)
            elif not role_name and allowed_codes:
                allowed_ids_subq = select(models.Role.id).where(
                    or_(
                        models.Role.code.in_(allowed_codes),
                        ~models.Role.code.in_(default_codes)
                    )
                )
                stmt = stmt.where(models.User.role_id.in_(allowed_ids_subq))
                count_stmt = count_stmt.where(models.User.role_id.in_(allowed_ids_subq))
            elif not role_name and not allowed_codes:
                allowed_ids_subq = select(models.Role.id).where(~models.Role.code.in_(default_codes))
                stmt = stmt.where(models.User.role_id.in_(allowed_ids_subq))
                count_stmt = count_stmt.where(models.User.role_id.in_(allowed_ids_subq))

        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        default_sort = "id"
        default_desc = True
        sort_expr = None

        if not sort_by:
            sort_by = default_sort
            is_desc = default_desc
        else:
            if sort_by not in schemas.USER_WHITELIST:
                sort_by = "username"
            valid_order = sort_order.lower() if sort_order else "asc"
            is_desc = valid_order == "desc" if valid_order in ("asc", "desc") else False

        sort_expr = getattr(models.User, sort_by)

        order_clause = sort_expr.desc() if is_desc else sort_expr.asc()
        stmt = stmt.order_by(order_clause).offset(skip).limit(limit)

        result = await db.execute(stmt)
        data_list = [AuthService._user_to_response(u).model_dump(mode="json") for u in result.scalars().all()]

        return {"items": data_list, "total": total, "skip": skip, "limit": limit}

    @staticmethod
    def _user_to_response(user: models.User) -> schemas.UserResponse:
        permissions = []
        role_name = None
        role_code = None
        role_id = None
        if user.role_rel:
            role_name = user.role_rel.name
            role_id = user.role_rel.id
            role_code = user.role_rel.code
            permissions = [p.code for p in user.role_rel.permissions]
        return schemas.UserResponse(
            id=user.id,
            username=user.username,
            email=user.email, full_name=user.full_name,
            is_active=user.is_active,
            role_id=role_id,
            role_name=role_name, role=role_code, permissions=permissions,
            create_at=user.create_at, update_at=user.update_at,
            create_by=user.create_by, update_by=user.update_by,
        )

    ROLE_PERMISSION_ORDER = {
        "superuser": 0,
        "admin": 1,
        "user": 2,
        "visitor": 3,
    }

    @staticmethod
    def _get_role_permission_level(role_code: str) -> int:
        """获取角色的权限等级，数字越小权限越高"""
        return AuthService.ROLE_PERMISSION_ORDER.get(role_code, 999)

    @staticmethod
    def _check_role_hierarchy(current_user: models.User, target_user: models.User, action: str = "操作"):
        """校验角色层级（基于 code），防止越级操作"""
        if not current_user.role_rel or not target_user.role_rel:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="角色信息缺失")

        current_level = AuthService._get_role_permission_level(current_user.role_rel.code)
        target_level = AuthService._get_role_permission_level(target_user.role_rel.code)

        if current_level >= target_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"无权{action}同级或更高级别的用户",
            )

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, update_data: schemas.UserUpdate, current_user: Optional[models.User] = None):
        stmt = (
            select(models.User)
            .options(selectinload(models.User.role_rel).selectinload(models.Role.permissions))
            .where(models.User.id == user_id)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

        if current_user:
            if current_user.id != user.id:
                AuthService._check_role_hierarchy(current_user, user, "修改")

            if (
                current_user.role_rel
                and current_user.role_rel.code == "superuser"
                and user.role_rel
                and user.role_rel.code == "superuser"
                and current_user.id != user.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="超级管理员不能修改其他超级管理员",
                )

        update_dict = update_data.model_dump(exclude_unset=True)

        if "role" in update_dict:
            role_code = update_dict.pop("role")
            if role_code:
                role_result = await db.execute(
                    select(models.Role).where(models.Role.code == role_code)
                )
                role_obj = role_result.scalar_one_or_none()
                if not role_obj:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"角色 '{role_code}' 不存在",
                    )
                update_dict["role_id"] = role_obj.id
            else:
                update_dict["role_id"] = None

        if "role_id" in update_dict:
            new_role_id = update_dict["role_id"]
            if new_role_id != user.role_id:
                if not current_user or not current_user.role_rel or current_user.role_rel.code != "superuser":
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="仅超级管理员可修改用户角色",
                    )
                new_role = await db.get(models.Role, new_role_id)
                if new_role and current_user.role_rel and new_role.level <= current_user.role_rel.level:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="无权将用户设置为同级或更高级别角色",
                    )

        if current_user:
            user.update_by = current_user.username

        for field, value in update_dict.items():
            setattr(user, field, value)
        await db.commit()
        await db.refresh(user)
        return AuthService._user_to_response(user)

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int, current_user: Optional[models.User] = None):
        stmt = (
            select(models.User)
            .options(selectinload(models.User.role_rel))
            .where(models.User.id == user_id)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

        if current_user:
            AuthService._check_role_hierarchy(current_user, user, "删除")
        await db.delete(user)
        await db.commit()
        return user

    @staticmethod
    async def create_user_by_admin(db: AsyncSession, user: schemas.UserAdminCreate, current_user: Optional[models.User] = None):
        stmt = select(models.User).where(models.User.username == user.username)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="账号已存在")

        role_id = user.role_id

        if user.role is not None:
            role_result = await db.execute(
                select(models.Role).where(models.Role.code == user.role)
            )
            found_role = role_result.scalar_one_or_none()
            if found_role:
                role_id = found_role.id

        if role_id is None:
            default_role_result = await db.execute(
                select(models.Role).where(models.Role.code == models.UserRole.USER.value)
            )
            default_role = default_role_result.scalar_one_or_none()
            if default_role:
                role_id = default_role.id

        if current_user and current_user.role_rel and role_id is not None:
            target_role = await db.get(models.Role, role_id)
            if target_role and target_role.level <= current_user.role_rel.level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权创建同级或更高级别角色的用户",
                )

        try:
            db_user = models.User(
                username=user.username,
                full_name=user.full_name if user.full_name else user.username,
                email=user.email,
                password=AuthService.get_password_hash(user.password) if user.password else None,
                role_id=role_id,
            )
            if current_user:
                db_user.create_by = current_user.username
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            return AuthService._user_to_response(db_user)
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"创建用户失败: {str(e)}")

    @staticmethod
    async def get_user(db: AsyncSession, user_id: int, current_user: Optional[models.User] = None):
        stmt = (
            select(models.User)
            .options(selectinload(models.User.role_rel).selectinload(models.Role.permissions))
            .where(models.User.id == user_id)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user and current_user:
            AuthService._check_role_hierarchy(current_user, user, "查看")
        return user

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str):
        stmt = (
            select(models.User)
            .options(selectinload(models.User.role_rel).selectinload(models.Role.permissions))
            .where(models.User.username == username)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_visitor_user(db: AsyncSession):
        """获取游客共享账号（仅返回启用状态的）"""
        stmt = (
            select(models.User)
            .options(selectinload(models.User.role_rel).selectinload(models.Role.permissions))
            .join(models.User.role_rel)
            .where(models.Role.code == "visitor", models.User.is_active == True)
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

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