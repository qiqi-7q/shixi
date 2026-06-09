from fastapi import FastAPI

from app.core.database import engine
from app.plugins.base_plugin import BasePlugin
from app.plugins.test_route_plugin import models
from app.plugins.test_route_plugin.router import router


class TestRoutePlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "test_route"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def register(self, app: FastAPI):
        # 创建表
        async with engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
        # 注册路由
        app.include_router(router, prefix="/api/test_route", tags=["测试路线"])
