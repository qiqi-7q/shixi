from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, ForeignKey, Table, Text, true
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    """系统默认角色 code 常量"""
    SUPERUSER = "superuser"
    ADMIN = "admin"
    USER = "user"
    VISITOR = "visitor"


# ==================== 角色-权限关联表（多对多，复合主键） ====================
role_permission = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", BigInteger, ForeignKey("roles.id", ondelete="CASCADE"),
           primary_key=True, nullable=False),
    Column("permission_id", BigInteger, ForeignKey("permissions.id", ondelete="CASCADE"),
           primary_key=True, nullable=False),
)


# ==================== 权限表 ====================
class Permission(Base):
    __tablename__ = "permissions"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    code = Column(String(128), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    create_by = Column(String(64), nullable=True)
    create_at = Column(DateTime, server_default=func.now())
    update_by = Column(String(64), nullable=True)
    update_at = Column(DateTime, nullable=True, onupdate=func.now())

    roles = relationship("Role", secondary=role_permission, back_populates="permissions", lazy="selectin")


# ==================== 角色表 ====================
class Role(Base):
    __tablename__ = "roles"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    code = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    level = Column(Integer, nullable=False, default=0)
    create_by = Column(String(64), nullable=True)
    create_at = Column(DateTime, server_default=func.now())
    update_by = Column(String(64), nullable=True)
    update_at = Column(DateTime, nullable=True, onupdate=func.now())

    permissions = relationship(
        "Permission",
        secondary=role_permission,
        primaryjoin=lambda: Role.id == role_permission.c.role_id,
        secondaryjoin=lambda: Permission.id == role_permission.c.permission_id,
        lazy="selectin",
    )
    users = relationship("User", back_populates="role_rel", lazy="selectin")


# ==================== 用户表 ====================
class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    full_name = Column(String(128), nullable=False)
    email = Column(String(256), nullable=True, index=True)
    password = Column(String(256), nullable=True)
    role_id = Column(BigInteger, ForeignKey("roles.id", ondelete="RESTRICT"),
                     nullable=False, index=True)
    is_active = Column(Boolean, nullable=False, server_default=true(), default=True)
    create_by = Column(String(64), nullable=True)
    create_at = Column(DateTime, server_default=func.now())
    update_by = Column(String(64), nullable=True)
    update_at = Column(DateTime, nullable=True, onupdate=func.now())

    role_rel = relationship("Role", back_populates="users", lazy="selectin", foreign_keys=[role_id])