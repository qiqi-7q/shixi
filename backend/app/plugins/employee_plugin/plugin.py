from fastapi import FastAPI
from app.plugins.base_plugin import BasePlugin
from app.plugins.employee_plugin import models
from app.core.database import engine
from app.plugins.employee_plugin.router import router


class EmployeePlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "employee"

    @property
    def version(self) -> str:
        return "1.0.0"

    def register(self, app: FastAPI):
        models.Base.metadata.create_all(bind=engine)
        app.include_router(router, prefix="/api/employee", tags=["员工管理"])
