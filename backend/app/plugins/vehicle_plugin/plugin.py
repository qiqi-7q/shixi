from fastapi import FastAPI
from app.plugins.base_plugin import BasePlugin
from app.plugins.vehicle_plugin import models
from app.core.database import engine
from app.plugins.vehicle_plugin.router import router, borrow_router


class VehiclePlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "vehicle"

    @property
    def version(self) -> str:
        return "1.0.0"

    def register(self, app: FastAPI):
        # 创建数据库表
        models.Base.metadata.create_all(bind=engine)
        # 注册路由
        app.include_router(router, prefix="/api/vehicle", tags=["车辆管理"])
        app.include_router(borrow_router, prefix="/api/borrow", tags=["借用管理"])
