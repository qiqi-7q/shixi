from fastapi import FastAPI
from app.plugins.base_plugin import BasePlugin
from app.plugins.auth_plugin import models
from app.core.database import engine
from app.plugins.auth_plugin.router import router


class AuthPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "auth"

    @property
    def version(self) -> str:
        return "1.0.0"

    def register(self, app: FastAPI):
        # 创建数据库表
        models.Base.metadata.create_all(bind=engine)
        # 注册路由
        app.include_router(router)