from fastapi import FastAPI
from app.plugins.base_plugin import BasePlugin
from app.plugins.test_task_plugin import models
from app.core.database import async_engine
from app.plugins.test_task_plugin.router import router


class TestTaskPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "test_task"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def register(self, app: FastAPI):
        async with async_engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
        app.include_router(router, prefix="/api/test_task", tags=["测试任务"])
