import logging

from app.core.config import settings
from app.core.database import SessionLocal
from app.plugins.test_record_plugin import services

logger = logging.getLogger("test_record_scheduler")  # 创建一个名为###的日志记录器
logger.setLevel(logging.INFO)  # 设置日志级别为INFO，只记录INFO及以上级别的日志
# 配置日志记录器，将日志写入test_record_scheduler.log文件,路径为logs/test_record_scheduler.log，日志文件不存在则创建，每次重启时清空日志
if not logger.handlers:
    log_file = settings.LOG_DIR / "test_record_scheduler.log"
    # 尝试清空日志文件，如果失败则继续执行
    try:
        if log_file.exists():
            log_file.unlink()  # 每次重启时清空日志
    except Exception as e:
        logger.warning(f"无法清空日志文件 {log_file}: {e}")

    try:
        handler = logging.FileHandler(
            log_file, encoding="utf-8"
        )  # 创建一个文件处理器，将日志写入scheduler.log文件
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )  # 设置日志格式，包含时间、级别和信息
        logger.addHandler(handler)  # 将文件处理器添加到日志记录器中
    except Exception as e:
        logger.error(f"无法创建日志文件处理器: {e}")


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
