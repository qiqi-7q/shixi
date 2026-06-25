from datetime import date
import logging
from sqlalchemy import exists, select, update
from app.core.config import settings
from app.core.database import SessionLocal
from app.plugins.vehicle_plugin import models

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# 使用 settings.BASE_DIR 获取项目根目录
# 配置日志记录器，将日志写入vehicle_scheduler.log文件,路径为logs/vehicle_scheduler.log
if not logger.handlers:
    log_file = settings.LOG_DIR / "vehicle_scheduler.log"
    try:
        if log_file.exists():
            log_file.unlink()  # 每次重启时清空日志
    except Exception as e:
        logger.warning(f"无法清空日志文件 {log_file}: {e}")

    try:
        handler = logging.FileHandler(
            log_file, encoding="utf-8"
        )  # 创建一个文件处理器，将日志写入vehicle_scheduler.log文件
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(funcName)s - %(levelname)s - %(message)s"
            )
        )  # 设置日志格式，包含时间、接口名称(如，refresh_vehicle_status_task)、级别和信息
        logger.addHandler(handler)  # 将文件处理器添加到日志记录器中
    except Exception as e:
        logger.error(f"无法创建vehicle_scheduler.log日志文件，错误信息为: {e}")


async def re_vs_task():
    """定时任务：每日凌晨0点30分刷新全部车辆使用状态(vehicle_status)，从车辆借用表中获取车辆id对应的借用记录，
    根据借用时间判断是否存在有今日借用记录，若存在则更新车辆状态为Borrowed;不存在今日借用则判断是否有未来预约，
    若存在则更新车辆状态为Reserved;不存在今日借用和未来预约则更新车辆状态为Available。最后批量写入数据库。
    """
    try:
        logger.info("开始执行车辆状态定时刷新任务")

        current_date = date.today()
        borrowed_ids = []
        reserved_ids = []
        available_ids = []

        async with SessionLocal() as db:
            # 查询所有非维护中车辆
            vehicle_list = (
                (
                    await db.execute(
                        select(models.Vehicle).filter(
                            models.Vehicle.vehicle_status
                            != models.VehicleStatus.MAINTENANCE
                        )
                    )
                )
                .scalars()
                .all()
            )
            logger.info(f"查询到{len(vehicle_list)}辆非维护中车辆")
            for vehicle in vehicle_list:
                # 第一步：判断是否有今日借用
                has_today = await db.scalar(
                    select(
                        exists().where(
                            models.BorrowRecord.vehicle_id == vehicle.id,
                            models.BorrowRecord.borrow_time == current_date,
                        )
                    )
                )
                if has_today:
                    borrowed_ids.append(vehicle.id)
                    continue

                # 第二步：无今日借用，判断是否有未来预约
                has_future = await db.scalar(
                    select(
                        exists().where(
                            models.BorrowRecord.vehicle_id == vehicle.id,
                            models.BorrowRecord.borrow_time > current_date,
                        )
                    )
                )
                if has_future:
                    reserved_ids.append(vehicle.id)
                else:
                    # 第三步：无今日借用和未来预约，更新状态为Available
                    available_ids.append(vehicle.id)
            logger.info(
                f"今日有{len(borrowed_ids)}辆车辆被借用，{len(reserved_ids)}辆车辆被预约，{len(available_ids)}辆车辆可用"
            )
            # 批量写入：按分组一次性 UPDATE
            if borrowed_ids:
                await db.execute(
                    update(models.Vehicle)
                    .where(models.Vehicle.id.in_(borrowed_ids))
                    .values(vehicle_status=models.VehicleStatus.BORROWED)
                )
            if reserved_ids:
                await db.execute(
                    update(models.Vehicle)
                    .where(models.Vehicle.id.in_(reserved_ids))
                    .values(vehicle_status=models.VehicleStatus.RESERVED)
                )
            if available_ids:
                await db.execute(
                    update(models.Vehicle)
                    .where(models.Vehicle.id.in_(available_ids))
                    .values(vehicle_status=models.VehicleStatus.AVAILABLE)
                )

            await db.commit()
        logger.info("车辆状态定时刷新完成")
    except Exception as ex:
        logger.exception(f"车辆状态定时刷新任务执行失败：{ex}")


async def re_bs_task():
    """定时任务：每日凌晨0点30分刷新全部车辆借用记录的状态（borrow_status），
    从BorrowRecord表中获取所有borrow_status为borrowing或为reserved的借用记录，
    根据借用时间（borrow_time）判断是否存在有今日借用记录，若存在则更新借用记录状态为borrowing;不存在今日借用则判断是否有未来预约，
    若存在则更新借用记录状态为reserved;不存在今日借用和未来预约则更新借用记录状态为returned。最后批量写入数据库。
    """
    try:
        logger.info("开始执行借用记录状态定时刷新任务")

        current_date = date.today()
        borrowing_ids = []
        reserved_ids = []
        returned_ids = []

        async with SessionLocal() as db:
            records = (
                (
                    await db.execute(
                        select(models.BorrowRecord).filter(
                            models.BorrowRecord.borrow_status.in_(
                                ["borrowing", "reserved"]
                            )
                        )
                    )
                )
                .scalars()
                .all()
            )
            logger.info(f"查询到 {len(records)} 条待刷新状态的借用记录")

            for record in records:
                if record.borrow_time == current_date:
                    borrowing_ids.append(record.id)
                elif record.borrow_time > current_date:
                    reserved_ids.append(record.id)
                else:
                    returned_ids.append(record.id)

            logger.info(
                f"今日有 {len(borrowing_ids)} 条借用中，{len(reserved_ids)} 条预约中，{len(returned_ids)} 条已归还"
            )

            if borrowing_ids:
                await db.execute(
                    update(models.BorrowRecord)
                    .where(models.BorrowRecord.id.in_(borrowing_ids))
                    .values(borrow_status="borrowing")
                )
            if reserved_ids:
                await db.execute(
                    update(models.BorrowRecord)
                    .where(models.BorrowRecord.id.in_(reserved_ids))
                    .values(borrow_status="reserved")
                )
            if returned_ids:
                await db.execute(
                    update(models.BorrowRecord)
                    .where(models.BorrowRecord.id.in_(returned_ids))
                    .values(borrow_status="returned")
                )

            await db.commit()
        logger.info("借用记录状态定时刷新完成")
    except Exception as ex:
        logger.exception(f"借用记录状态定时刷新任务执行失败：{ex}")
