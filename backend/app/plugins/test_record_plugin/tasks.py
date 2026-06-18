import logging
import os
from app.core.database import SessionLocal
from app.plugins.test_record_plugin import services
from apscheduler.triggers.interval import IntervalTrigger


logger = logging.getLogger("test_record_scheduler") #创建一个名为###的日志记录器
logger.setLevel(logging.INFO)   # 设置日志级别为INFO，只记录INFO及以上级别的日志
# 配置日志记录器，将日志写入scheduler.log文件
if not logger.handlers:
    log_file = os.path.join(os.path.dirname(__file__), "scheduler.log")
    if os.path.exists(log_file):
        os.remove(log_file)  # 每次重启时清空日志
    handler = logging.FileHandler(log_file, encoding="utf-8") # 创建一个文件处理器，将日志写入scheduler.log文件
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")) # 设置日志格式
    logger.addHandler(handler) # 将文件处理器添加到日志记录器中


async def refresh_data_links_job():
    async with SessionLocal() as db:
        try:
            logger.info("开始执行定时任务：刷新数据链接")
            result = await services.refresh_link(db)
            # 检查刷新结果是否为字典且包含success键
            # 如果包含success键且success为True，则刷新成功
            if isinstance(result, dict) and result.get("success"):
                # 记录成功日志，包含总数、成功数、失败数、未匹配数
                logger.info(f"定时任务执行成功: 总数={result.get('total_records')}, "
                      f"成功={result.get('success_count')}, "
                      f"失败={result.get('fail_count')}, "
                      f"未匹配={result.get('no_match_count')}")
            else:
                logger.error(f"定时任务执行失败: {result}")
        except Exception as e:
            logger.exception(f"定时任务执行异常: {str(e)}")


def setup_refresh_link_scheduler(scheduler, interval_minutes: int = 10):
    scheduler.add_job(
        refresh_data_links_job,
        trigger=IntervalTrigger(minutes=interval_minutes), # 每interval_minutes分钟执行一次
        id="refresh_data_links",  # 任务ID，用于取消任务
        name="定时刷新数据链接",    # 任务名称，用于日志记录
        replace_existing=True  # 如果存在相同ID的任务，则替换为新任务
    )
    logger.info(f"定时任务已配置：每{interval_minutes}分钟刷新一次数据链接")