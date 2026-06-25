from fastapi import FastAPI
from app.plugins.base_plugin import BasePlugin
from app.plugins.employee_plugin import models
from app.core.database import async_engine
from app.plugins.employee_plugin.router import router


class EmployeePlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "employee"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def register(self, app: FastAPI):
        async with async_engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
        app.include_router(router, prefix="/api/employee", tags=["员工管理"])
        print("员工管理插件注册成功，接口已加载！")
