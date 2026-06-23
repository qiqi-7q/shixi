from fastapi import FastAPI

from app.core.database import engine
from app.core.scheduler import scheduler
from app.plugins.base_plugin import BasePlugin
from app.plugins.test_record_plugin import models
from app.plugins.test_record_plugin.router import router
from app.plugins.test_record_plugin.tasks import setup_refresh_link_scheduler, logger


class TestRecordPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "test_record"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def register(self, app: FastAPI):
        async with engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
        app.include_router(router, prefix="/api/test_record", tags=["测试记录"])
        
        
        # 启动定时任务调度器，刷新数据链接任务每10分钟执行一次
        # 日志文件为scheduler.log，每次重启时清空日志，开启执行一次
        if not scheduler.running:
            scheduler.start()
            logger.info("定时任务调度器已启动")

        setup_refresh_link_scheduler(scheduler, interval_minutes=30)
