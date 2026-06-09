from fastapi import FastAPI

from app.core.database import engine
from app.plugins.base_plugin import BasePlugin
from app.plugins.vehicle_plugin import models
from app.plugins.vehicle_plugin.router import borrow_router, router


class VehiclePlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "vehicle"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def register(self, app: FastAPI):
        async with engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
        app.include_router(router, prefix="/api/vehicle", tags=["车辆管理"])
        app.include_router(borrow_router, prefix="/api/borrow", tags=["借用管理"])
