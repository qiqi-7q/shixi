from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from jose import jwt
from fastapi import HTTPException, status

from app.core.config import settings
from app.plugins.auth_plugin import models, schemas


async def get_user_permissions(user: models.User) -> list[str]:
    """获取用户的所有权限码"""
    if not user.role_rel:
        return []
    return [p.code for p in user.role_rel.permissions]


class PermissionService:

    @staticmethod
    async def get_all_permissions(
        db: AsyncSession,
        platform_uuid: Optional[str] = None,
    ) -> List[models.Permission]:
        """获取权限列表
        - platform_uuid 为 None：返回所有权限
        - platform_uuid 指定值：返回该平台的所有权限
        """
        from sqlalchemy import or_
        stmt = select(models.Permission)
        if platform_uuid:
            stmt = stmt.where(
                or_(
                    models.Permission.platform_uuid == platform_uuid,
                    models.Permission.platform_uuid.is_(None),
                )
            )
        stmt = stmt.order_by(models.Permission.id)
        result = await db.execute(stmt)
        return result.scalars().all()


class PlatformService:

    @staticmethod
    async def get_platforms(db: AsyncSession) -> List[models.Platform]:
        stmt = select(models.Platform).order_by(models.Platform.id)
        result = await db.execute(stmt)
        return result.scalars().all()


class RoleService:

    @staticmethod
    async def get_roles(db: AsyncSession, skip: int = 0, limit: int = 100, sort_by: str = "level", sort_order: str = "desc", search: str = None, platform_uuid: str = None, current_role_code: Optional[str] = None):
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
        if platform_uuid:
            stmt = stmt.where(models.Role.platform_uuid == platform_uuid)
        if current_role_code is not None:
            current_permission = AuthService._get_role_permission_level(current_role_code)
            allowed_codes = [code for code, level in AuthService.ROLE_PERMISSION_ORDER.items() if (level >= current_permission if current_role_code == "superuser" else level > current_permission)]
            if allowed_codes:
                stmt = stmt.where(models.Role.code.in_(allowed_codes))
            else:
                stmt = stmt.where(models.Role.id == -1)
        if search:
            stmt = stmt.where(
                or_(
                    models.Role.name.ilike(f"%{search}%"),
                    models.Role.code.ilike(f"%{search}%"),
                )
            )
        stmt = stmt.order_by(sort_col, models.Role.id).offset(skip).limit(limit)

        count_stmt = select(func.count(models.Role.id))
        if platform_uuid:
            count_stmt = count_stmt.where(models.Role.platform_uuid == platform_uuid)
        if current_role_code is not None:
            current_permission = AuthService._get_role_permission_level(current_role_code)
            allowed_codes = [code for code, level in AuthService.ROLE_PERMISSION_ORDER.items() if (level >= current_permission if current_role_code == "superuser" else level > current_permission)]
            if allowed_codes:
                count_stmt = count_stmt.where(models.Role.code.in_(allowed_codes))
            else:
                count_stmt = count_stmt.where(models.Role.id == -1)
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
    async def get_roles_all(db: AsyncSession, sort_by: str = "level", sort_order: str = "desc", search: str = None, platform_uuid: str = None, current_role_code: Optional[str] = None):
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
        if platform_uuid:
            stmt = stmt.where(models.Role.platform_uuid == platform_uuid)
        if current_role_code is not None:
            current_permission = AuthService._get_role_permission_level(current_role_code)
            allowed_codes = [code for code, level in AuthService.ROLE_PERMISSION_ORDER.items() if (level >= current_permission if current_role_code == "superuser" else level > current_permission)]
            if allowed_codes:
                stmt = stmt.where(models.Role.code.in_(allowed_codes))
            else:
                stmt = stmt.where(models.Role.id == -1)
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
    async def get_role_by_uuid(db: AsyncSession, role_uuid: str):
        stmt = (
            select(models.Role)
            .options(selectinload(models.Role.permissions))
            .where(models.Role.uuid == role_uuid)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_role(db: AsyncSession, role_data: schemas.RoleCreate, create_by: str = None):
        # 同平台下角色 code 唯一
        exist = await db.execute(
            select(models.Role).where(
                models.Role.code == role_data.code,
                models.Role.platform_uuid == role_data.platform_uuid,
            )
        )
        if exist.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该平台下角色 code 已存在")
        role = models.Role(
            code=role_data.code, name=role_data.name, description=role_data.description,
            platform_uuid=role_data.platform_uuid, level=role_data.level,
            create_by=create_by,
        )
        if role_data.permission_ids:
            perm_result = await db.execute(
                select(models.Permission).where(models.Permission.id.in_(role_data.permission_ids))
            )
            permissions = perm_result.scalars().all()
            RoleService._validate_permission_platform(permissions, role_data.platform_uuid)
            role.permissions = permissions
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role

    @staticmethod
    async def update_role(db: AsyncSession, role_id: int, role_data: schemas.RoleUpdate, update_by: str = None):
        stmt = (
            select(models.Role)
            .options(selectinload(models.Role.permissions))
            .where(models.Role.id == role_id)
        )
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
        if role_data.code is not None:
            role.code = role_data.code
        if role_data.name is not None:
            role.name = role_data.name
        if role_data.description is not None:
            role.description = role_data.description
        if role_data.platform_uuid is not None:
            role.platform_uuid = role_data.platform_uuid
        if role_data.level is not None:
            role.level = role_data.level
        if update_by:
            role.update_by = update_by
        if role_data.permission_ids is not None:
            perm_result = await db.execute(
                select(models.Permission).where(models.Permission.id.in_(role_data.permission_ids))
            )
            permissions = perm_result.scalars().all()
            RoleService._validate_permission_platform(permissions, role.platform_uuid)
            role.permissions = permissions
        await db.commit()
        await db.refresh(role)
        return role

    @staticmethod
    def _validate_permission_platform(permissions, platform_uuid: str):
        """校验权限是否属于当前平台"""
        invalid = [
            p for p in permissions
            if p.platform_uuid is not None and p.platform_uuid != platform_uuid
        ]
        if invalid:
            codes = [p.code for p in invalid]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"以下权限不属于该平台：{', '.join(codes)}",
            )

    # 不可删除的系统默认角色 code
    PROTECTED_ROLE_CODES = {
        models.UserRole.SUPERUSER.value,
        models.UserRole.ADMIN.value,
        models.UserRole.USER.value,
        models.UserRole.VISITOR.value,
    }

    @staticmethod
    async def delete_role(db: AsyncSession, role_id: int, platform_uuid: str = None):
        role = await db.get(models.Role, role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
        if platform_uuid and str(role.platform_uuid) != platform_uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能删除本平台下的角色",
            )
        if role.code in ("superuser", "admin", "user", "visitor"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"系统默认角色 '{role.code}' 不可删除",
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
    async def authenticate_user(db: AsyncSession, username: str, password: str, platform_uuid: str = None):
        stmt = (
            select(models.User)
            .options(selectinload(models.User.role_rel).selectinload(models.Role.permissions))
            .where(models.User.username == username)
        )
        if platform_uuid:
            stmt = stmt.where(models.User.platform_uuid == platform_uuid)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return False
        if user.is_oa_account:
            return user
        if not user.password or not AuthService.verify_password(password, user.password):
            return False
        return user

    @staticmethod
    async def create_user(db: AsyncSession, user: schemas.UserCreate, platform_uuid: str = None):
        stmt = select(models.User).where(models.User.username == user.username)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="账号已存在")

        default_role_result = await db.execute(
            select(models.Role).where(
                models.Role.code == models.UserRole.USER.value,
                models.Role.platform_uuid == platform_uuid,
            )
        )
        default_role = default_role_result.scalar_one_or_none()

        try:
            db_user = models.User(
                username=user.username,
                password=AuthService.get_password_hash(user.password),
                full_name=user.username,
                platform_uuid=platform_uuid,
                role_uuid=default_role.uuid if default_role else None,
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
            platform_uuid: Optional[str] = None,
            current_role_code: Optional[str] = None,
    ):
        from sqlalchemy import func

        stmt = select(models.User).options(
            selectinload(models.User.role_rel).selectinload(models.Role.permissions)
        )
        count_stmt = select(func.count(models.User.id))

        if role_name:
            stmt = stmt.join(models.User.role_rel).where(models.Role.code == role_name)
            count_stmt = count_stmt.join(models.User.role_rel).where(models.Role.code == role_name)
        
        if platform_uuid:
            stmt = stmt.where(models.User.platform_uuid == platform_uuid)
            count_stmt = count_stmt.where(models.User.platform_uuid == platform_uuid)

        if current_role_code is not None:
            current_permission = AuthService._get_role_permission_level(current_role_code)
            operator = "__ge__" if current_role_code == "superuser" else "__gt__"
            allowed_codes = [code for code, level in AuthService.ROLE_PERMISSION_ORDER.items() if getattr(level, operator)(current_permission)]
            if role_name and role_name not in allowed_codes:
                stmt = stmt.where(models.User.id == -1)
                count_stmt = count_stmt.where(models.User.id == -1)
            elif not role_name and allowed_codes:
                allowed_uuids_subq = select(models.Role.uuid).where(models.Role.code.in_(allowed_codes))
                stmt = stmt.where(models.User.role_uuid.in_(allowed_uuids_subq))
                count_stmt = count_stmt.where(models.User.role_uuid.in_(allowed_uuids_subq))
            elif not role_name and not allowed_codes:
                stmt = stmt.where(models.User.id == -1)
                count_stmt = count_stmt.where(models.User.id == -1)

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
            platform_uuid: Optional[str] = None,
            sort_by: Optional[str] = None,
            sort_order: Optional[str] = None,
            current_role_code: Optional[str] = None,
    ):
        from sqlalchemy import func

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
        if platform_uuid:
            stmt = stmt.where(models.User.platform_uuid == platform_uuid)
            count_stmt = count_stmt.where(models.User.platform_uuid == platform_uuid)

        if current_role_code is not None:
            current_permission = AuthService._get_role_permission_level(current_role_code)
            operator = "__ge__" if current_role_code == "superuser" else "__gt__"
            allowed_codes = [code for code, level in AuthService.ROLE_PERMISSION_ORDER.items() if getattr(level, operator)(current_permission)]
            if role_name and role_name not in allowed_codes:
                stmt = stmt.where(models.User.id == -1)
                count_stmt = count_stmt.where(models.User.id == -1)
            elif not role_name and allowed_codes:
                allowed_uuids_subq = select(models.Role.uuid).where(models.Role.code.in_(allowed_codes))
                stmt = stmt.where(models.User.role_uuid.in_(allowed_uuids_subq))
                count_stmt = count_stmt.where(models.User.role_uuid.in_(allowed_uuids_subq))
            elif not role_name and not allowed_codes:
                stmt = stmt.where(models.User.id == -1)
                count_stmt = count_stmt.where(models.User.id == -1)

        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        # 1. 前置统一处理排序参数，消除分支差异逻辑
        # 默认排序字段、升降序
        default_sort = "id"
        default_desc = True
        sort_expr = None

        # 处理空排序场景
        if not sort_by:
            sort_by = default_sort
            is_desc = default_desc
        else:
            # 字段白名单校验
            if sort_by not in schemas.USER_WHITELIST:
                sort_by = "username"
            # 校验排序方向
            valid_order = sort_order.lower() if sort_order else "asc"
            is_desc = valid_order == "desc" if valid_order in ("asc", "desc") else False

        # 普通字段原生排序
        sort_expr = getattr(models.User, sort_by)

        # 升降序统一处理
        order_clause = sort_expr.desc() if is_desc else sort_expr.asc()
        stmt = stmt.order_by(order_clause).offset(skip).limit(limit)

        # 3. 查询逻辑全局只写一次，无重复
        result = await db.execute(stmt)
        data_list = [AuthService._user_to_response(u).model_dump(mode="json") for u in result.scalars().all()]

        return {"items": data_list, "total": total, "skip": skip, "limit": limit}

    @staticmethod
    def _user_to_response(user: models.User) -> schemas.UserResponse:
        permissions = []
        role_name = None
        role_code = None
        if user.role_rel:
            role_name = user.role_rel.name
            role_code = user.role_rel.code
            permissions = [p.code for p in user.role_rel.permissions]
        return schemas.UserResponse(
            id=user.id, uuid=str(user.uuid),
            username=user.username,
            email=user.email, full_name=user.full_name,
            is_active=user.is_active, is_oa_account=user.is_oa_account,
            platform_uuid=str(user.platform_uuid),
            role_uuid=str(user.role_uuid) if user.role_uuid else None,
            role_name=role_name, role=role_code, permissions=permissions,
            create_at=user.create_at, update_at=user.update_at,
            create_by=user.create_by, update_by=user.update_by,
        )

    # 角色权限排序（基于 code 字段），数字越小权限越高
    ROLE_PERMISSION_ORDER = {
        "superuser": 0,
        "admin": 1,
        "user": 2,
        "visitor": 3,
        "manager": 4,
        "tester": 5,
        "viewer": 6,
    }

    @staticmethod
    def _get_role_permission_level(role_code: str) -> int:
        """获取角色的权限等级，数字越小权限越高"""
        return AuthService.ROLE_PERMISSION_ORDER.get(role_code, 999)

    @staticmethod
    def _check_role_hierarchy(current_user: models.User, target_user: models.User, action: str = "操作"):
        """校验角色层级（基于 code + 平台隔离），防止越级/跨平台操作"""
        if not current_user.role_rel or not target_user.role_rel:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="角色信息缺失")

        if current_user.platform_uuid != target_user.platform_uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"无权跨平台{action}其他平台用户",
            )

        current_level = AuthService._get_role_permission_level(current_user.role_rel.code)
        target_level = AuthService._get_role_permission_level(target_user.role_rel.code)

        # 只能操作等级比自己低的用户（严格小于），同级之间不可互操作
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
            AuthService._check_role_hierarchy(current_user, user, "修改")

            # 超管不能修改其他超管
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

        if "role_uuid" in update_dict:
            new_role_uuid = str(update_dict["role_uuid"]) if update_dict["role_uuid"] else None
            current_role_uuid = str(user.role_uuid) if user.role_uuid else None
            if new_role_uuid != current_role_uuid:
                if not current_user or not current_user.role_rel or current_user.role_rel.code != "superuser":
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="仅超级管理员可修改用户角色",
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

        role_uuid = user.role_uuid

        if user.role is not None:
            role_result = await db.execute(
                select(models.Role).where(
                    models.Role.code == user.role,
                    models.Role.platform_uuid == user.platform_uuid,
                )
            )
            found_role = role_result.scalar_one_or_none()
            if found_role:
                role_uuid = found_role.uuid

        if role_uuid is None:
            default_role_result = await db.execute(
                select(models.Role).where(
                    models.Role.code == models.UserRole.USER.value,
                    models.Role.platform_uuid == user.platform_uuid,
                )
            )
            default_role = default_role_result.scalar_one_or_none()
            if default_role:
                role_uuid = default_role.uuid

        if current_user and current_user.role_rel and role_uuid is not None:
            target_role_result = await db.execute(
                select(models.Role).where(models.Role.uuid == role_uuid)
            )
            target_role = target_role_result.scalar_one_or_none()
            if target_role and target_role.level >= current_user.role_rel.level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权创建同级或更高级别角色的用户",
                )

        try:
            db_user = models.User(
                username=user.username, platform_uuid=user.platform_uuid,
                full_name=user.full_name if user.full_name else user.username,
                password=AuthService.get_password_hash(user.password) if user.password else None,
                is_oa_account=user.is_oa_account,
                role_uuid=role_uuid,
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
    async def get_visitor_user(db: AsyncSession, platform_uuid: str):
        """获取指定平台的游客共享账号（支持 visitor/viewer 角色，A平台用visitor，B平台用viewer）"""
        stmt = (
            select(models.User)
            .options(selectinload(models.User.role_rel).selectinload(models.Role.permissions))
            .join(models.User.role_rel)
            .where(
                models.User.platform_uuid == platform_uuid,
                models.Role.code.in_(["visitor", "viewer"]),
            )
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