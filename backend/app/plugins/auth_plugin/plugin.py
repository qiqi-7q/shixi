from fastapi import FastAPI

from app.core.database import engine_pg
from app.plugins.auth_plugin import models
from app.plugins.auth_plugin.router import router
from app.plugins.base_plugin import BasePlugin


class AuthPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "auth"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def register(self, app: FastAPI):
        # 在 PostgreSQL 中创建权限管理相关表
        # 用 connect() 非事务连接，每个 DDL 自动提交，避免一个表失败导致全部回滚
        try:
            async with engine_pg.connect() as conn:
                await conn.run_sync(models.Base.metadata.create_all, checkfirst=True)
        except Exception:
            pass

        # 注册路由（无论建表是否成功都要注册）
        app.include_router(router, prefix="/api/auth", tags=["认证"])