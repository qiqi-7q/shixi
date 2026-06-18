import logging
import os
from app.core.database import SessionLocal
from app.plugins.test_record_plugin import services
from apscheduler.triggers.interval import IntervalTrigger


logger = logging.getLogger("test_record_scheduler")
logger.setLevel(logging.INFO)
if not logger.handlers:
    log_file = os.path.join(os.path.dirname(__file__), "scheduler.log")
    if os.path.exists(log_file):
        os.remove(log_file)  # 每次重启时清空日志
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


async def refresh_data_links_job():
    async with SessionLocal() as db:
        try:
            logger.info("开始执行定时任务：刷新数据链接")
            result = await services.refresh_link(db)
            if isinstance(result, dict) and result.get("success"):
                logger.info(f"定时任务执行成功: 总数={result.get('total_records')}, "
                      f"成功={result.get('success_count')}, "
                      f"失败={result.get('fail_count')}, "
                      f"未匹配={result.get('no_match_count')}")
            else:
                logger.error(f"定时任务执行失败: {result}")
        except Exception as e:
            logger.exception(f"定时任务执行异常: {str(e)}")


def setup_refresh_link_scheduler(scheduler, interval_minutes: int = 1):
    scheduler.add_job(
        refresh_data_links_job,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id="refresh_data_links",
        name="定时刷新数据链接",
        replace_existing=True
    )
    logger.info(f"定时任务已配置：每{interval_minutes}分钟刷新一次数据链接")