import logging
from logging.handlers import RotatingFileHandler

from app.core.config import settings
from app.core.database import SessionLocal
from app.plugins.test_record_plugin import services
from app.utils.logger import get_logger

logger = get_logger(__name__, log_filename="test_record_scheduler.log")


async def refresh_data_links_job():
    async with SessionLocal() as db:
        try:
            logger.info("开始执行定时任务：刷新数据链接")
            result = await services.refresh_link(db)
            # 检查刷新结果是否为字典且包含success键
            # 如果包含success键且success为True，则刷新成功
            if isinstance(result, dict) and result.get("success"):
                # 记录成功日志，包含总数、成功数、失败数、未匹配数
                logger.info(
                    f"定时任务执行成功: 总数={result.get('total_records')}, "
                    f"成功={result.get('success_count')}, "
                    f"失败={result.get('fail_count')}, "
                    f"未匹配={result.get('no_match_count')}"
                )
            else:
                logger.error(f"定时任务执行失败: {result}")
        except Exception as e:
            logger.exception(f"定时任务执行异常: {str(e)}")
