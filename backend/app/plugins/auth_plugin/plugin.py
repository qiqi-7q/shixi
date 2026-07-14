from fastapi import FastAPI

from app.core.database import engine
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
        # 在 MySQL 中创建权限管理相关表
        try:
            async with engine.connect() as conn:
                await conn.run_sync(models.Base.metadata.create_all, checkfirst=True)
        except Exception as e:
            print(f"[AuthPlugin] MySQL 建表失败: {e}")

        # 注册路由（无论建表是否成功都要注册）
        app.include_router(router, prefix="/api/auth", tags=["认证"])