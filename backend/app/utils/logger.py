import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from app.core.config import settings


def get_logger(name: str, log_filename: str = "app.log") -> logging.Logger:
    """
    获取统一配置的日志实例
    :param name: 模块名，传入 __name__
    :param log_filename: 日志文件名，不同业务传不同名称
    :return: Logger对象
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 避免重复添加handler
    if logger.handlers:
        return logger

    # 创建日志目录
    settings.LOG_DIR.mkdir(exist_ok=True, parents=True)
    log_file: Path = settings.LOG_DIR / log_filename

    try:
        # 按天切割日志，保留7天
        file_handler = TimedRotatingFileHandler(
            log_file, when="midnight", interval=1, backupCount=7, encoding="utf-8"
        )
        # 统一日志格式
        log_formatter = logging.Formatter(
            "%(asctime)s - %(funcName)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)

    except Exception as e:
        print(f"日志文件初始化失败: {e}")
        logger.error(f"日志文件初始化失败: {e}")

    return logger
