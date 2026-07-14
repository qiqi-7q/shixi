import uuid as _uuid

from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, ForeignKey, Table, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import BasePG as Base
import enum


def _gen_uuid():
    return _uuid.uuid4()


class UserRole(str, enum.Enum):
    """系统默认角色 code 常量（跨平台通用）"""
    USER = "user"
    ADMIN = "admin"
    SUPERUSER = "superuser"
    MANAGER = "manager"
    TESTER = "tester"
    VIEWER = "viewer"
    VISITOR = "visitor"


class PlatformName(str, enum.Enum):
    """平台 code 常量"""
    PLATFORM_A = "platform_a"
    PLATFORM_B = "platform_b"


# ==================== 角色-权限关联表（多对多，复合主键，无独立 id） ====================
role_permission = Table(
    "role_permissions",
    Base.metadata,
    Column("role_uuid", UUID(as_uuid=True), ForeignKey("roles.uuid", ondelete="CASCADE"),
           primary_key=True, nullable=False),
    Column("permission_uuid", UUID(as_uuid=True), ForeignKey("permissions.uuid", ondelete="CASCADE"),
           primary_key=True, nullable=False),
)


# ==================== 平台表 ====================
class Platform(Base):
    __tablename__ = "platforms"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True, default=_gen_uuid)
    code = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    create_by = Column(String(64), nullable=True)
    create_at = Column(DateTime, server_default=func.now())
    update_by = Column(String(64), nullable=True)
    update_at = Column(DateTime, nullable=True, onupdate=func.now())

    roles = relationship("Role", back_populates="platform_rel", lazy="selectin")
    users = relationship("User", back_populates="platform_rel", lazy="selectin")
    permissions = relationship("Permission", back_populates="platform_rel", lazy="selectin")


# ==================== 权限表 ====================
class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = (
        UniqueConstraint("code", "platform_uuid", name="uq_permission_code_platform"),
    )

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True, default=_gen_uuid)
    code = Column(String(128), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    platform_uuid = Column(UUID(as_uuid=True), ForeignKey("platforms.uuid", ondelete="RESTRICT"),
                           nullable=False, index=True)
    create_by = Column(String(64), nullable=True)
    create_at = Column(DateTime, server_default=func.now())
    update_by = Column(String(64), nullable=True)
    update_at = Column(DateTime, nullable=True, onupdate=func.now())

    platform_rel = relationship("Platform", back_populates="permissions", lazy="selectin")
    roles = relationship("Role", secondary=role_permission, back_populates="permissions", lazy="selectin")


# ==================== 角色表 ====================
class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("code", "platform_uuid", name="uq_roles_code_platform"),
    )

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True, default=_gen_uuid)
    code = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    level = Column(Integer, nullable=False, default=0)
    platform_uuid = Column(UUID(as_uuid=True), ForeignKey("platforms.uuid", ondelete="RESTRICT"),
                           nullable=False, index=True)
    create_by = Column(String(64), nullable=True)
    create_at = Column(DateTime, server_default=func.now())
    update_by = Column(String(64), nullable=True)
    update_at = Column(DateTime, nullable=True, onupdate=func.now())

    platform_rel = relationship("Platform", back_populates="roles", lazy="selectin")
    permissions = relationship(
        "Permission",
        secondary=role_permission,
        primaryjoin=lambda: Role.uuid == role_permission.c.role_uuid,
        secondaryjoin=lambda: Permission.uuid == role_permission.c.permission_uuid,
        lazy="selectin",
    )
    users = relationship("User", back_populates="role_rel", lazy="selectin")


# ==================== 用户表 ====================
class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True, default=_gen_uuid)
    username = Column(String(64), unique=True, nullable=False, index=True)
    full_name = Column(String(128), nullable=False)
    email = Column(String(256), nullable=True, index=True)
    password = Column(String(256), nullable=True)
    role_uuid = Column(UUID(as_uuid=True), ForeignKey("roles.uuid", ondelete="RESTRICT"),
                       nullable=False, index=True)
    is_oa_account = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    platform_uuid = Column(UUID(as_uuid=True), ForeignKey("platforms.uuid", ondelete="RESTRICT"),
                           nullable=False, index=True)
    create_by = Column(String(64), nullable=True)
    create_at = Column(DateTime, server_default=func.now())
    update_by = Column(String(64), nullable=True)
    update_at = Column(DateTime, nullable=True, onupdate=func.now())

    role_rel = relationship("Role", back_populates="users", lazy="selectin", foreign_keys=[role_uuid])
    platform_rel = relationship("Platform", back_populates="users", lazy="selectin")