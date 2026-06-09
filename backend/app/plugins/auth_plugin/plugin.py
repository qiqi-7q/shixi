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
        # 创建数据库表
        async with engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
        # 注册路由
        app.include_router(router, prefix="/api/auth", tags=["认证"])
